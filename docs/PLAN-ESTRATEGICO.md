# Plan: Mejoras Estratégicas Axioma 2.0 — Fase 2 (actualizado 2026-04-15)

## Fuentes

Todo verificado desde repositorios oficiales:
- github.com/DS4SD/docling + huggingface.co/ibm-granite/granite-docling-258M
- github.com/ibm-granite/granite-4.0-language-models + HuggingFace model cards
- github.com/ibm-granite/granite-guardian
- github.com/opensearch-project/neural-search (CHANGELOG + commits)
- github.com/explodinggradients/ragas

---

## Análisis por componente (verificado)

### 1. Docling + Granite-Docling-258M ✅ GA

- **Status**: GA desde Sep 17, 2025. MIT license.
- **VLM CLI**: `docling --pipeline vlm --vlm-model granite_docling [doc]`
- **Bounding boxes**: CONFIRMADO. El modelo emite coordinate tokens: `<loc_155><loc_233><loc_206><loc_237>`. Se pueden usar para OCR en regiones específicas e identificar elementos por coordenadas.
- **DocTags**: XML estructurado exportable a `DoclingDocument`, luego a Markdown/HTML/JSON lossless.
- **XBRL**: Introducido en v2.79.0 con fact metadata y linkbase relationships.
- **Benchmarks**: Tables TEDS 0.82→0.97, Code F1 0.915→0.988 vs SmolDocling.
- **Caveat real**: "Visually Grounded RAG" con highlights en PDF requiere pasar coordenadas a través de todo el pipeline RAG (ingestión → OpenSearch → API response → frontend con PDF.js overlay). No es trivial.

### 2. Granite 4.0 H-Tiny ✅ GA (corregido — NO es preview)

- **Status**: GA desde Oct 2, 2025. Apache 2.0.
- **Arquitectura confirmada**: 4 attention layers + 36 Mamba2 layers + MoE (64 expertos totales, 6 activos).
- **Parámetros**: 7B totales / **1B activos** (sparse MoE — esto es la clave de eficiencia).
- **Contexto**: **128K tokens** CONFIRMADO.
- **Variantes disponibles**: micro, h-micro, h-tiny, h-small, 8b (base + instruct).
- **Benchmarks**: MMLU 68.65%, HumanEval 83%, GSM8K 84.69%, BFCL v3 57.65%.
- **Instalación**: `transformers` estándar desde pip (ya no requiere source install).

### 3. RRF en OpenSearch ✅ DISPONIBLE (corregido — el blog era viejo)

- **Commit**: `f6d8a12` (Jan 14, 2025) — "Adding Reciprocal Rank Fusion (RRF) in hybrid query (#1086)"
- **Custom weights**: PR #1322 (May 15, 2025)
- **Stats integration**: Jun 5, 2025
- **Plugin**: `neural-search` (se instala con OpenSearch 3.x como plugin incluido).
- **Combinación disponible**: RRF como normalization processor + arithmetic/harmonic/geometric mean.

### 4. Granite Guardian 3.3 ✅ GA

- **Status**: GA. Última versión: 3.3-8B (Sep 2025). Apache 2.0.
- **Variantes**: 2B a 8B parámetros para distintos trade-offs de latencia/costo.
- **Evalúa**: Groundedness, Context Relevance, Answer Relevance, Jailbreak, Hallucinations, Harm.
- **Output**: Yes/No + confidence score. Soporta "thinking mode" para trazas de razonamiento.
- **Latencia**: El modelo 3B es "moderate latency" — NO va en el path síncrono de cada request.

### 5. Ragas ✅ GA — integración Langfuse CONFIRMADA

- **Version**: v0.4.3 (Jan 2026). Apache 2.0. 13.4k stars.
- **Integración Langfuse**: CONFIRMADA. Dos modos: per-trace scoring y batch sampling periódico.
- **Métricas RAG confirmadas**: Faithfulness, Answer Relevancy, Context Precision, Aspect Critique.
- **TestsetGenerator**: Disponible. Genera datasets sintéticos desde documentos Docling.
- **Estrategia correcta**: batch sampling nocturno, NO evaluación síncrona en cada request.

### 6. Valkey 9.x — features ya verificadas en sesiones anteriores ✅

- I/O multi-threading: `io-threads` config + `io-threads-do-reads yes`
- HEXPIRE per-field TTL: real en 9.0
- SET IFEQ: real
- valkey/valkey-bundle: JSON + Bloom + Search + LDAP incluidos

---

## Priorización recomendada

### Fase 1 — Alto impacto, bajo riesgo (Q2 2026)

| Feature | Esfuerzo | Valor |
|---|---|---|
| OpenSearch híbrido con RRF | Medio | Alto — diferenciador B2B inmediato |
| Ragas batch nocturno con Langfuse | Bajo | Alto — ya tenemos Langfuse activo |
| Valkey I/O threading (config pura) | Mínimo | Medio — sin código, solo config |

### Fase 2 — Alto impacto, esfuerzo medio (Q2-Q3 2026)

| Feature | Esfuerzo | Valor |
|---|---|---|
| Granite-Docling-258M en pipeline de ingestión | Medio | Alto — tablas TEDS 0.97, fórmulas, XBRL |
| Granite Guardian como guardrail **asíncrono** (sampling) | Medio | Alto — argumento de venta B2B/salud/finanzas |
| Granite 4.0 H-Tiny como motor de razonamiento | Alto | Alto — 128K ctx, 1B activos, costo inferencia |

### Fase 3 — Infraestructura y diferenciación máxima (Q3-Q4 2026)

| Feature | Esfuerzo | Valor |
|---|---|---|
| Multi-agent Langflow + MCP externo (Slack, SQL, Jira) | Alto | Máximo — transforma de buscador a agente |
| Grafana AIOps (mezcla FastAPI + OpenSearch + Valkey) | Medio | Medio — venta enterprise SLA |
| OpenSearch Dashboards UBI + DLS/FLS | Alto | Alto — compliance multi-tenant B2B |

### Fase 4 — Cuando haya demanda explícita del cliente

| Feature | Por qué esperar |
|---|---|
| Bounding boxes en PDF (frontend) | 3 sprints frontend + coordinación pipeline completo |
| Ragas TestsetGenerator por cliente | Necesita documentos reales del cliente para generar el dataset |

---

## Archivos Axioma 2.0 que se tocan por feature

| Feature | Archivos principales |
|---|---|
| RRF OpenSearch | `docker-compose.yml` (neural-search config), nuevo `src/services/search_service.py` |
| Ragas batch | nuevo `scripts/ragas_batch_eval.py`, `pyproject.toml` |
| Valkey I/O threading | `docker-compose.yml` (command flags) |
| Granite-Docling ingestión | `src/services/document_service.py`, `pyproject.toml` |
| Granite Guardian | nuevo `src/services/guardrail_service.py`, `src/services/chat_service.py` |
| Granite 4.0 | config Langflow (modelo de inferencia) + `src/config/settings.py` |

---

## Estado de ejecución

### ✅ Fase 0 — Migración Redis → Valkey (COMPLETA)
### ✅ Fase 1 — commit `db2495f4` (COMPLETA)
- Valkey I/O threading, OpenSearch hybrid + RRF, Ragas batch eval

---

## Fase 2 — Implementación detallada

### Correcciones a sugerencias externas (verificadas)

| Sugerencia | Veredicto | Evidencia |
|---|---|---|
| "Granite Guardian 3.2-5B es la última versión estable" | **INCORRECTO** | 3.3-8B es la última (Aug 1, 2025). 3.2 existe pero es más vieja. |
| SGLang RadixAttention + Zero-Overhead Scheduler | **CONFIRMADO** | v0.4+ docs: 95-98% GPU util, 3.1x vs vLLM en MoE |
| "28% TTFT reduction" de SGLang | **NO VERIFICADO** | No es una métrica documentada de SGLang; posiblemente confundido con FP8 |
| Docling HybridChunker preserva jerarquía | **CONFIRMADO** | docs oficiales + `contextualize()` method |
| Granite Vision 3.3-2B para charts/infografías | **CONFIRMADO** | DocVQA 0.91, InfoVQA 0.68; scope más amplio que declarado |

---

### Orden de implementación recomendado (sin dependencias entre ítems)

**Semana 1 → Item 3** (LLMRouter + Granite 4.0): cero riesgo, nuevo archivo, valida Ollama endpoint.  
**Semana 2 → Item 2** (Guardian): nuevo archivo, hooks mínimos, deploy con `GUARDIAN_ENABLED=false`.  
**Semana 3 → Item 1** (HybridChunker): mayor riesgo, deploy con `HYBRID_CHUNKER_ENABLED=false`.

---

### Item 1: Granite-Docling-258M + HybridChunker + Context Expansion

**Contexto**: Docling ya está integrado vía HTTP a docling-serve. El chunking actual es por página (`extract_relevant()` en `src/utils/document_processing.py`). HybridChunker del Python SDK de docling preserva jerarquía de secciones en metadata — mejora TEDS de tablas 0.82→0.97 y reduce alucinaciones al pasar contexto más rico.

**Archivos a modificar**:
- `pyproject.toml` — agregar `"docling>=2.0.0"` (SDK Python, distinto de docling-serve)
- `src/utils/document_processing.py` — nueva función `extract_with_hybrid_chunker(doc_dict)` junto a `extract_relevant()` (no reemplaza, convive)
- `src/models/processors.py` — dispatch condicional en `process_document_standard()` (líneas 262-263): si `HYBRID_CHUNKER_ENABLED` → `extract_with_hybrid_chunker`, si no → `extract_relevant`
- `src/config/settings.py` — nuevos flags: `HYBRID_CHUNKER_ENABLED`, `CONTEXT_EXPANSION_ENABLED` + nuevos campos en `INDEX_BODY["mappings"]["properties"]`: `section_title`, `parent_section`, `chunk_index`, `prev_chunk_index`, `next_chunk_index`
- `src/main.py` — startup migration: `put_mapping` con los nuevos campos (aditivo, no requiere reindexar)
- `src/services/search_service.py` — nuevo método `_fetch_adjacent_chunks()` + context expansion post-retrieval (solo si ambos flags activos); agregar `"chunk_index"`, `"document_id"`, `"section_title"` al `_source` list

**Función nueva en document_processing.py**:
```python
def extract_with_hybrid_chunker(doc_dict: dict) -> dict:
    from docling.datamodel.document import DoclingDocument
    from docling.chunking import HybridChunker
    doc = DoclingDocument.model_validate(doc_dict)
    chunker = HybridChunker()
    raw_chunks = list(chunker.chunk(doc))
    chunks = []
    for i, chunk in enumerate(raw_chunks):
        ctx = chunker.contextualize(chunk)
        page_no = None
        try:
            prov = chunk.meta.doc_items[0].prov
            page_no = prov[0].page_no if prov else None
        except Exception:
            pass
        chunks.append({
            "page": page_no, "type": "text", "text": ctx.text,
            "section_title": ctx.meta.headings[0] if ctx.meta.headings else None,
            "parent_section": ctx.meta.headings[1] if len(ctx.meta.headings) > 1 else None,
            "chunk_index": i,
            "prev_chunk_index": i - 1 if i > 0 else None,
            "next_chunk_index": i + 1 if i < len(raw_chunks) - 1 else None,
        })
    origin = doc_dict.get("origin", {})
    return {"id": origin.get("binary_hash"), "filename": origin.get("filename"),
            "mimetype": origin.get("mimetype"), "chunks": chunks}
```

**Riesgos**:
- HybridChunker API puede cambiar entre minor versions — usar `getattr(..., None)` defensivo en todos los accesos a metadata
- `docling` SDK puede traer dependencias pesadas (torch, transformers) — verificar que HybridChunker no descarga modelos al importar; si lo hace, importar lazy dentro de la función
- `document_id` debe agregarse al `_source` en search_service.py (ya está en OpenSearch, solo falta retornarlo)
- Índices existentes: PUT mapping es aditivo, docs viejos tienen `null` en campos nuevos — el context expansion chequea `chunk.get("chunk_index") is not None`

---

### Item 2: Granite Guardian 3.3-8B Async Guardrail

**Contexto**: No existe ningún guardrail en el codebase. `langfuse` ya está en `pyproject.toml`. Guardian corre async (fire-and-forget) — nunca bloquea el path de respuesta al usuario. Se usa `GUARDIAN_SAMPLE_RATE` para evaluar solo un porcentaje de requests (arrancar con 0.1).

**Versión**: `granite-guardian-3.3:8b` (más nueva, GA Aug 2025). Alternativa más liviana: `granite-guardian-3.2:5b` (5B params, más rápida). Configurable vía `GUARDIAN_MODEL`.

**Archivos a modificar**:
- `src/services/guardrail_service.py` (nuevo) — clase `GuardrailService` con `evaluate_response()` + `evaluate_and_log()` + singleton `guardrail_service`
- `src/agent.py` — hook post-response en `async_langflow_chat()` (post línea ~595) y `async_chat()` (post línea ~435): `asyncio.create_task(guardrail_service.evaluate_and_log(...))`
- `src/config/settings.py` — nuevos env vars: `GUARDIAN_ENABLED` (default `false`), `GUARDIAN_MODEL` (default `granite-guardian-3.3:8b`), `GUARDIAN_SAMPLE_RATE` (default `1.0`), + exponer `LANGFUSE_*` vars al service layer
- `src/config/settings.py::AppClients.cleanup()` — agregar `await guardrail_service.cleanup()`

**Scores en Langfuse**: `guardian/safe` (0/1), `guardian/faithful` (0/1), `guardian/evaluation_ms`, `guardian/risk_type` (si aplica).

**Riesgos**:
- Guardian 3.3-8B requiere pull explícito: `docker exec axioma-ollama ollama pull granite-guardian-3.3:8b`
- Cold start del modelo: primeras evaluaciones pueden tardar 30-90s — no bloquea usuarios, pero alertas de `evaluation_ms` deben tener threshold alto
- `asyncio.create_task()` en shutdown: tasks pendientes se cancelan al SIGTERM. Mitigado con `langfuse.flush()` en `cleanup()`
- En el path de Langflow, el contexto recuperado está embebido en el prompt por Langflow — usar `prompt` como aproximación para faithfulness es aceptable en Fase 2

---

### Item 3: Granite 4.0 H-Tiny via Ollama + LLMRouter

**Decisión: Ollama para Fase 2. SGLang queda para Fase 3.**

SGLang es técnicamente superior para MoE (3.1x vs vLLM, RadixAttention) pero requiere: nuevo servicio Docker, nuevo provider en `config_manager.py`, nuevos endpoints de validación, nuevo Langflow component, y lógica de load balancing. La infraestructura Ollama ya existe y es trivial operacionalmente.

**Archivos a modificar**:
- `src/services/llm_router.py` (nuevo) — clase `LLMRouter` con `complete()`, backend seleccionable vía `GRANITE_BACKEND` env var (`"ollama"` default, `"sglang"` reservado para Fase 3). Singleton `llm_router`.
- `src/config/settings.py` — nuevos env vars: `GRANITE_MODEL` (default `granite4.0-htiny:instruct`), `GRANITE_ENDPOINT` (default: usa `OLLAMA_ENDPOINT`), `GRANITE_BACKEND` (default `ollama`)
- Langflow: agregar componente Ollama con `granite4.0-htiny:instruct` en el flow de chat. Enrutar queries complejas (multi-hop, largo contexto) a Granite 4.0 vs queries simples al modelo actual.

**SGLang en Fase 3**: El `GRANITE_BACKEND=sglang` env var es el toggle de migración. Al habilitar, `llm_router._ollama_complete()` no se toca — se agrega `_sglang_complete()` y el dispatch ya está en `complete()`.

**Riesgos**:
- Granite 4.0 H-Tiny: `ollama pull granite4.0-htiny:instruct` — verificar que el nombre del modelo en Ollama registry es este exactamente antes de hardcodearlo como default
- 128K context window requiere suficiente RAM/VRAM en el host donde corre Ollama

---

## Fase 3 — Revisada con sugerencias incorporadas

| Feature | Origen | Prioridad |
|---|---|---|
| SGLang como backend de Granite 4.0 H-Tiny | Sugerencia validada | Alta — `GRANITE_BACKEND=sglang` ya está en llm_router |
| Self-RAG / CRAG patterns en Langflow | Sugerencia validada | Alta — requiere nodos de reflexión en el flow |
| Valkey HEXPIRE per-field TTL para memoria de sesión | Sugerencia validada | Media — aplica cuando hay multi-agent concurrente |
| Valkey SET IFEQ para race conditions | Sugerencia validada | Media — junto con HEXPIRE |
| Multi-agent Langflow + MCP externo | Original | Máxima |
| Grafana AIOps | Original | Media |
| **OpenSearch Dashboards — Cuarto de Máquinas** | Nuevo (detallado abajo) | Alta (compliance B2B) |

---

## Fase 3 — OpenSearch Dashboards: Arquitectura y Alcance

### Marco arquitectónico (acordado)

```
┌─────────────────────────────────────────────────────────┐
│  FACHADA          → Frontend Next.js (cliente final)    │
│  FÁBRICA CEREBROS → Langflow (lógica de IA, agentes)   │
│  CUARTO MÁQUINAS  → OpenSearch Dashboards (infra/ops)  │
└─────────────────────────────────────────────────────────┘
```

**Regla de oro**: Toda decisión de IA (prompts, herramientas, razonamiento, trazas) vive en **Langflow** y se audita en **Langfuse**. Dashboards es solo para infraestructura y seguridad.

---

### Lo que SÍ configurar en OpenSearch Dashboards

#### 1. DLS/FLS — Seguridad multi-tenant (verificado, ya en plan)
- **Document Level Security**: filtros por `owner`, `allowed_users`, `allowed_groups`
- **Field Level Security**: ocultar campos sensibles por rol
- **Resultado**: los vectores de la Empresa A nunca son visibles para la Empresa B
- **Archivos**: config OpenSearch Security plugin (sin código Python nuevo)

#### 2. ISM — Index State Management (lifecycle de índices)
- Políticas automatizadas para mover índices vectoriales inactivos a cold storage
- Trigger: últimos accesos > N días → tier `warm` → tier `cold`
- **Resultado**: optimización de costos en índices de clientes inactivos
- **Archivos**: JSON de política ISM vía API o UI de Dashboards

#### 3. ML Commons — Registro de modelos de embeddings
- Registrar y administrar los modelos de embedding (Granite embedding, text-embedding-3-small) directamente en el cluster
- Permite cambiar modelos sin modificar código Python
- **Resultado**: gestión centralizada del modelo de embedding activo
- **Archivos**: config vía Dashboards UI (no requiere código)

#### 4. UBI — User Behavior Insights (verificado: release 3.0.0.0)
- Plugin `opensearch-project/user-behavior-insights`
- Registra qué resultados de búsqueda el usuario leyó vs ignoró
- Datos disponibles para afinar el ranking de RRF y evaluar calidad del RAG
- **Resultado**: feedback loop real para mejorar retrieval sin LLM-as-judge
- **Archivos**: instalación del plugin + event collector en `src/services/search_service.py` (enviar `click_event` post-resultado)

#### 5. Search Relevance Workbench (verificado: `dashboards-search-relevance`)
- Mesa de trabajo visual para comparar BM25 vs KNN vs Hybrid internamente
- A/B testing de pipelines RRF sin tocar producción
- **Resultado**: validación de cambios en search_service.py antes de deploy
- **Archivos**: solo config Dashboards (zero código)

#### 6. Alertas + Monitoreo
- Disparadores automáticos: uso de memoria crítico, nodo caído, pico de latencia
- Notificaciones vía webhook → Slack del equipo
- **Archivos**: config Alerting plugin en Dashboards

#### 7. OpenSearch Assistant Toolkit (verificado: `dashboards-assistant`)
- Habilitar `assistant.chat.enabled: true` en `opensearch_dashboards.yml`
- Capacidades: PPL queries en lenguaje natural, análisis de logs de error, estado de índices, alertas activas
- Uso interno del equipo DevOps para diagnóstico sin necesidad de DSL
- **NO es para usuarios finales ni para lógica de negocio**

---

### El anti-patrón: NO usar agentic features de Dashboards

**Verificado**: `dashboards-assistant` (el plugin de AI) opera sobre consultas de infraestructura (PPL, índices, logs, alertas). OpenSearch 3.x expone capacidades de orquestación de agentes en su UI.

**Por qué NO hacerlo**:
- Si construís flujos de agentes, prompts o herramientas en OpenSearch Dashboards → **fragmentás la arquitectura**
- Langfuse no puede trazar lo que ocurre dentro de Dashboards
- Toda la lógica de razonamiento debe pasar por Langflow para ser auditable
- El debugging de un agente partido entre Dashboards y Langflow es imposible

**Regla**:
```
OpenSearch Dashboards → consultas de datos (PPL, DSL)
Langflow              → lógica de agentes, herramientas, prompts
```

---

### Orden de implementación dentro de Fase 3

| Prioridad | Item | Esfuerzo | Sin código nuevo |
|---|---|---|---|
| 1 | DLS/FLS | Bajo | ✅ Solo config |
| 2 | ISM lifecycle | Bajo | ✅ Solo config |
| 3 | Alertas + Monitoreo | Bajo | ✅ Solo config |
| 4 | Search Relevance Workbench | Mínimo | ✅ Solo config |
| 5 | ML Commons embedding | Medio | ✅ Casi solo config |
| 6 | UBI plugin | Medio | ⚠️ 1 hook en search_service.py |
| 7 | OpenSearch Assistant | Bajo | ✅ 1 config flag |

**Nota**: ítems 1-5 y 7 son configuración pura — se pueden hacer sin tocar Python. Solo UBI requiere agregar un evento en `search_service.py` cuando el usuario hace click en un resultado.

---

## Fase 4 — Revisada con sugerencias incorporadas

| Feature | Origen | Por qué esperar |
|---|---|---|
| Bounding boxes en PDF (PDF.js overlay) | Original | 3 sprints frontend |
| Ragas TestsetGenerator por cliente | Original | Necesita docs reales del cliente |
| Granite Vision 3.3-2B para charts/infografías | Sugerencia validada | Requiere Granite-Docling detecte imágenes de gráficos → pipeline completo |
| Pathway para ingesta en tiempo real | Sugerencia validada | Solo cuando cliente B2B exija datos en streaming vs PDFs estáticos |

---

## Verificación post-implementación Fase 2

1. **HybridChunker**: subir un PDF con tablas complejas → verificar en OpenSearch que el doc tiene `section_title`, `chunk_index` en los campos. Comparar resultados de búsqueda con/sin `CONTEXT_EXPANSION_ENABLED`.
2. **Guardian**: hacer una pregunta con respuesta inventada → verificar en Langfuse que aparecen scores `guardian/safe: 0` y `guardian/risk_type`.
3. **LLMRouter**: `curl -X POST <ollama_endpoint>/api/chat -d '{"model": "granite4.0-htiny:instruct", "messages": [...]}'` → respuesta válida.
4. **Langflow**: configurar componente Granite 4.0 en flow → test de query multi-hop.
