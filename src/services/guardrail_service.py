"""
Granite Guardian async guardrail service.

Evaluates LLM responses for safety and faithfulness using Granite Guardian
via Ollama. All evaluation is fire-and-forget — never blocks the hot path.
Results are logged to structlog and uploaded to Langfuse as trace scores.

Architecture
------------
- ``evaluate_response()``  : single call to Guardian, returns ``GuardrailResult``
- ``evaluate_and_log()``   : wraps evaluate + logging; designed for
                             ``asyncio.create_task()`` — never awaited directly
- Respects ``GUARDIAN_SAMPLE_RATE`` (0.0–1.0): only evaluates a fraction of
  responses to control cost and latency on the Ollama side

Usage (from agent.py)
---------------------
    from config.settings import GUARDIAN_ENABLED
    from services.guardrail_service import guardrail_service

    if GUARDIAN_ENABLED:
        asyncio.create_task(
            guardrail_service.evaluate_and_log(
                question=prompt,
                context=prompt,   # enriched context if available
                answer=response_text,
                trace_id=response_id,
            )
        )

Required env vars (when GUARDIAN_ENABLED=true):
    GUARDIAN_MODEL      — Ollama model name (default: granite-guardian-3.3:8b)
    OLLAMA_ENDPOINT     — Ollama server URL

Optional:
    GUARDIAN_SAMPLE_RATE — Fraction of requests to evaluate (default: 1.0)
    LANGFUSE_SECRET_KEY  — Langfuse server-key for score upload
    LANGFUSE_PUBLIC_KEY  — Langfuse public key
    LANGFUSE_HOST        — Langfuse host (default: https://cloud.langfuse.com)
"""

import asyncio
import os
import random
import time
from dataclasses import dataclass, field
from typing import Optional

import httpx

from config.settings import (
    GUARDIAN_ENABLED,
    GUARDIAN_MODEL,
    GUARDIAN_SAMPLE_RATE,
    LANGFUSE_HOST,
    LANGFUSE_PUBLIC_KEY,
    LANGFUSE_SECRET_KEY,
)
from utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class GuardrailResult:
    """Result of a single Guardian evaluation."""

    is_safe: bool = True
    is_faithful: bool = True
    risk_type: Optional[str] = None
    confidence: float = 1.0
    raw_response: str = ""
    evaluation_ms: int = 0
    error: Optional[str] = None


class GuardrailService:
    """
    Async safety/faithfulness evaluation using Granite Guardian via Ollama.

    Thread-safe: uses a single shared httpx.AsyncClient.
    Langfuse client is lazy-initialised on first use.
    """

    def __init__(self) -> None:
        self._langfuse = None
        self._http_client: Optional[httpx.AsyncClient] = None

    # ─── Internal helpers ────────────────────────────────────────────────────

    def _get_http_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=httpx.Timeout(60.0))
        return self._http_client

    def _get_langfuse(self):
        """Lazy-init Langfuse client. Returns None when credentials are absent."""
        if self._langfuse is not None:
            return self._langfuse
        if not (LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY):
            return None
        try:
            from langfuse import Langfuse

            self._langfuse = Langfuse(
                secret_key=LANGFUSE_SECRET_KEY,
                public_key=LANGFUSE_PUBLIC_KEY,
                host=LANGFUSE_HOST,
            )
        except Exception as exc:
            logger.warning("GuardrailService: Langfuse init failed", error=str(exc))
        return self._langfuse

    def _resolve_ollama_endpoint(self) -> str:
        try:
            from config.settings import config_manager
            from utils.container_utils import transform_localhost_url

            cfg = config_manager.get_config()
            if cfg and cfg.providers.ollama.endpoint:
                return transform_localhost_url(cfg.providers.ollama.endpoint)
        except Exception:
            pass
        from utils.container_utils import transform_localhost_url

        return transform_localhost_url(
            os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
        )

    # ─── Public API ──────────────────────────────────────────────────────────

    async def evaluate_response(
        self,
        question: str,
        context: str,
        answer: str,
    ) -> GuardrailResult:
        """
        Call Granite Guardian via Ollama to evaluate safety/faithfulness.

        Returns a ``GuardrailResult``. Never raises — all errors are captured
        and returned as ``result.error``.

        Guardian output format: "safe" | "unsafe\\n<risk_type>"
        """
        start = time.monotonic()
        try:
            endpoint = self._resolve_ollama_endpoint()

            # IBM-recommended Granite Guardian prompt template
            prompt = (
                f"<|start_of_role|>user<|end_of_role|>"
                f"Question: {question}\n\nContext: {context}\n\nAnswer: {answer}"
                f"<|end_of_text|>"
                f"<|start_of_role|>assistant<|end_of_role|>"
            )

            payload = {
                "model": GUARDIAN_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0, "num_predict": 20},
            }

            client = self._get_http_client()
            response = await client.post(f"{endpoint}/api/generate", json=payload)
            response.raise_for_status()

            data = response.json()
            raw = data.get("response", "").strip().lower()
            elapsed_ms = int((time.monotonic() - start) * 1000)

            is_safe = raw.startswith("safe")
            risk_type: Optional[str] = None
            if not is_safe and "\n" in raw:
                risk_type = raw.split("\n", 1)[1].strip()

            return GuardrailResult(
                is_safe=is_safe,
                is_faithful=is_safe,
                risk_type=risk_type,
                raw_response=raw,
                evaluation_ms=elapsed_ms,
            )

        except Exception as exc:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            logger.warning(
                "GuardrailService: evaluation failed",
                error=str(exc),
                elapsed_ms=elapsed_ms,
            )
            return GuardrailResult(error=str(exc), evaluation_ms=elapsed_ms)

    async def evaluate_and_log(
        self,
        question: str,
        context: str,
        answer: str,
        trace_id: Optional[str] = None,
    ) -> None:
        """
        Evaluate a response and log results to structlog + Langfuse.

        Designed to be dispatched via ``asyncio.create_task()`` — never awaited
        directly from the request path.

        No-op when:
        - ``GUARDIAN_ENABLED=false``
        - The request is not selected by ``GUARDIAN_SAMPLE_RATE``
        """
        if not GUARDIAN_ENABLED:
            return

        if GUARDIAN_SAMPLE_RATE < 1.0 and random.random() > GUARDIAN_SAMPLE_RATE:
            return

        result = await self.evaluate_response(question, context, answer)

        logger.info(
            "GuardrailService: evaluation complete",
            is_safe=result.is_safe,
            is_faithful=result.is_faithful,
            risk_type=result.risk_type,
            evaluation_ms=result.evaluation_ms,
            trace_id=trace_id,
            error=result.error,
        )

        if result.error:
            return

        lf = self._get_langfuse()
        if not lf:
            return

        try:
            trace_kwargs: dict = {"name": "guardian-evaluation"}
            if trace_id:
                trace_kwargs["id"] = trace_id

            trace = lf.trace(**trace_kwargs)
            trace.score(name="guardian/safe", value=1.0 if result.is_safe else 0.0)
            trace.score(name="guardian/faithful", value=1.0 if result.is_faithful else 0.0)
            trace.score(name="guardian/evaluation_ms", value=float(result.evaluation_ms))
            if result.risk_type:
                trace.score(
                    name="guardian/risk_type",
                    value=0.0,
                    comment=result.risk_type,
                )
        except Exception as exc:
            logger.warning(
                "GuardrailService: Langfuse upload failed", error=str(exc)
            )

    async def cleanup(self) -> None:
        """Flush Langfuse buffer and close HTTP client. Call on app shutdown."""
        lf = self._langfuse
        if lf:
            try:
                lf.flush()
            except Exception:
                pass

        if self._http_client is not None:
            try:
                await self._http_client.aclose()
                logger.info("GuardrailService HTTP client closed")
            except Exception as exc:
                logger.warning("GuardrailService cleanup error", error=str(exc))
            finally:
                self._http_client = None


# Module-level singleton — import this directly
guardrail_service = GuardrailService()
