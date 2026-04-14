# Axioma-2.0 (OpenRAG) — Roadmap 2026

> Documento maestro con el estado actual del proyecto y plan a futuro.
> Basado en langflow-ai/openrag — 90% ya está resuelto 🔥
> Última actualización: 2026-04-14

---

## tl;dr: 100% del código implementado

| Lo que YA está |
|----------------|
| Docling (OCR, chunking) |
| OpenSearch + Búsqueda híbrida |
| Langflow (agentes visuales) |
| APIs FastAPI (/v1/*) |
| MCP Server nativo |
| OAuth, OIDC, API Keys |
| Conectores (OneDrive, S3, etc) |
| Langfuse (analíticas) |
| **Rate Limiting (Redis + fallback en memoria)** |

**Tu trabajo:** Ensamblar, configurar y personalizar. El código está completo.

---

## 1. Qué es Axioma-2.0 (OpenRAG)

**Axioma** es una plataforma **RAG (Retrieval-Augmented Generation)** self-hosted de nivel empresarial basada en [langflow-ai/openrag](https://github.com/langflow-ai/openrag).

### El 90% YA está resuelto 🔥

| Feature | Estado | Descripción |
|---------|--------|-------------|
| Docling | ✅ | OCR, chunking automático, preservación de jerarquía |
| OpenSearch | ✅ | Vector store + búsqueda híbrida con RRF |
| Langflow | ✅ | Orquestación visual de agentes (drag-and-drop) |
| APIs FastAPI | ✅ | Endpoints: /v1/chat, /v1/search, /v1/documents |
| MCP Server | ✅ | Conexión nativa con Cursor/Claude Desktop |
| OAuth/OIDC | ✅ | Autenticación Google, Microsoft |
| API Keys | ✅ | Gestión de claves para API pública |
| Conectores | ✅ | OneDrive, SharePoint, S3, IBM COS |
| Langfuse | ✅ | Observabilidad y evaluación — variables configuradas |
| **Rate Limiting** | ✅ | Redis + fallback en memoria. Tiers: free/pro/enterprise |

### Tu trabajo como desarrollador

1. **Configurar** `.env` con tus proveedores de modelos
2. **Diseñar** los agentes en Langflow (interfaz visual)
3. **Personalizar** el frontend (Next.js) con Vercel v0 para tu marca

### Documentación Completa
- Ver `docs/PROJECT-COMPLETE.md` para documentación maestra
- Ver `docs/PROJECT-OVERVIEW.md` para exploración detallada

### Diferenciadores
- Multi-tenant con aislamiento de datos
- Conectores empresariales (SharePoint, OneDrive, S3, IBM COS)
- Búsqueda híbrida (semántica + keyword + prefix)
- Flows configurables via Langflow
- Autenticación robusta (OAuth/OIDC, JWT, API Keys)

---

## 2. Stack Tecnológico

| Capa | Tecnología |
|------|-------------|
| Backend | Python 3.13+, FastAPI, uvicorn, structlog |
| Frontend | Next.js, TypeScript, React |
| Database | OpenSearch 3.x (search + vector store) |
| Cache / Rate Limit | Redis 7 (con fallback en memoria) |
| AI Pipeline | Langflow |
| Auth | OAuth 2.0, OIDC, JWT (RS256), API Keys |
| Containers | Docker + Compose |
| Testing | pytest, pytest-asyncio, pytest-cov |

### AI/LLM Providers
- OpenAI (GPT-4, embeddings)
- Anthropic (Claude)
- IBM Watsonx
- Ollama (local)
- Embeddings: granite-embedding-278m-multilingual (12 idiomas)

---

## 3. Estado Actual — Lo que YA está Implementado

### ✅ Core RAG
- [x] Ingestión de documentos (PDF, texto, URL)
- [x] Chunking automático
- [x] Embedding multi-provider (OpenAI, Ollama, WatsonX)
- [x] Búsqueda semántica híbrida (k-NN + keyword + prefix)
- [x] Chat con RAG via Langflow
- [x] Knowledge filters (ACL por usuario/grupo)

### ✅ API v1 Pública
- [x] `/api/v1/search` — Búsqueda semántica
- [x] `/api/v1/chat` — Chat RAG
- [x] `/api/v1/documents` — Upload de documentos
- [x] `/api/v1/models` — Modelos disponibles
- [x] `/api/v1/knowledge_filters` — Filtros

### ✅ Autenticación
- [x] OAuth 2.0 (Google, Microsoft Graph)
- [x] OIDC support
- [x] JWT con RS256
- [x] API Keys management (`orag_xxxxx`)
- [x] Dependencias: `require_api_key`, `get_api_key_user_async`

### ✅ Conectores
- [x] OneDrive (OAuth, selective sync, webhooks)
- [x] SharePoint (OAuth, ACL per file)
- [x] S3 (buckets, filtros)
- [x] IBM COS (buckets, regional)
- [x] BaseConnector abstracto (extensible)

### ✅ Infra & DevOps
- [x] Docker Compose (dev, dev-cpu, dev-local)
- [x] Makefile automation
- [x] OpenSearch security config
- [x] Docling integration

### ✅ Observabilidad
- [x] Langfuse integration (variables configuradas — observabilidad y evaluación activas)
- [x] Prometheus metrics
- [x] Structlog logging
- [x] Telemetry client

### ✅ Documentación
- [x] Swagger/OpenAPI auto-generado (`/docs`)
- [x] FastAPI native

### ✅ MCP
- [x] Servidor MCP nativo via Langflow
- [x] Herramientas: chat, search, config
- [x] Listo para Cursor/Claude Desktop

---

## 4. Lo que FALTA — Gaps Identificados

### 🔴 PRIORIDAD ALTA (Q1-Q2 2026)

| # | Feature | Estado | Descripción |
|---|---------|--------|-------------|
| 1 | **Rate Limiting** | ✅ Implementado | `src/rate_limit_middleware.py` + `src/services/rate_limiter.py` |
| 2 | **MCP Documentation** | ⚠️ | Documentar endpoints MCP para clientes |
| 3 | **Swagger Polish** | ⚠️ | Pulir docstrings y descripciones |

### Implementación Rate Limiting

| Artefacto | Archivo | Estado |
|-----------|---------|--------|
| Middleware | `src/rate_limit_middleware.py` | ✅ |
| Servicio | `src/services/rate_limiter.py` | ✅ |
| Tests | `tests/unit/test_rate_limiter.py` | ✅ |
| Config | `src/config/settings.py` | ✅ |
| Redis | `docker-compose.yml` | ✅ |
| Dependencia | `pyproject.toml` (`redis[asyncio]>=5.0`) | ✅ |

### 🟡 PRIORIDAD MEDIA (Q2-Q3 2026)

| # | Feature | Estado | Descripción |
|---|---------|--------|-------------|
| 4 | SSO/SAML Enterprise | ⚠️ Config | OpenSearch Security nativo |
| 5 | Audit Logs | ⚠️ Config | OpenSearch Audit Logs nativo |
| 6 | Permisos Granulares (DLS/FLS) | ⚠️ Config | OpenSearch DLS/FLS nativo |
| 7 | White-label / Theming | 🔴 Código | Frontend Vercel v0 |

### 🟢 PRIORIDAD BAJA (Q3-Q4 2026)

| # | Feature | Estado | Descripción |
|---|---------|--------|-------------|
| 8 | Redis Cache (B2C) | ❌ | Para alta concurrencia y reducir costos LLM |
| 9 | Multi-language RAG | ⚠️ | Configurar granite-embedding + reranker |
| 10 | Rate Plans (Tiers) | ❌ | Free/Pro/Enterprise por tiers |

---

## 5. Roadmap 2026 — Plan de Implementación

### Q1 2026: Foundations (Ahora)

```
[x]    Review técnico final
[x]    Rate Limiting ← COMPLETADO 2026-04-14
[x]    Documentar API MCP para clientes ← COMPLETADO 2026-04-14
[x]    Pulir docstrings + Swagger ← COMPLETADO 2026-04-14
```

**Responsable:** Backend Team  
**Entregables:**
- ✅ Middleware de rate limiting (Redis + Starlette + fallback en memoria)
- ✅ Tests unitarios completos (13 tests)
- ✅ Redis en docker-compose con healthcheck
- ✅ `docs/MCP-GUIDE.md` — guía para conectar Cursor y Claude Desktop via MCP
- ✅ Swagger: título "Axioma API", descripción, tags, summaries en los 16 endpoints públicos

---

### Q2 2026: Enterprise B2B (Configuración OpenSearch)

```
[x]    Rate Limiting ← COMPLETADO Q1
[ ]    SSO/SAML ← Config OpenSearch Security
[ ]    Audit Logs ← Config OpenSearch Audit
[ ]    DLS/FLS ← Config OpenSearch Security
[ ]    White-label ← Código Vercel v0
```

**Responsable:** DevOps + Backend  
**Nota:** SSO, Audit y DLS/FLS se configuran en OpenSearch, no requieren código Python.

---

### Q3 2026: Scale B2C

```
[ ]    Redis LangCache
[ ]    Rate plans (Free/Pro/Enterprise)
[x]    Analytics dashboard (Langfuse — configurado)
[ ]    Multi-language support
```

**Responsable:** Backend + Frontend  
**Entregables:**
- Cache de respuestas paraFAQ
- Planes de pricing
- Dashboard de métricas
- RAG multilingual

---

### Q4 2026: Air-gap + Launch

```
[ ]    SGLang integration (inferencia self-hosted)
[ ]    Air-gap deployment guide
[ ]    Performance optimization
[ ]    Security audit
[ ]    Beta program (las 3 verticales)
[ ]    Public launch
[ ]    Customer onboarding flow
```

**Responsable:** Full Team  
**Entregables:**
- SGLang como provider de inferencia (drop-in, OpenAI-compatible)
- Soporte certificado para IBM Granite, Llama 3, Qwen
- Guía de deployment air-gap para enterprise
- GA release
- Documentación por vertical
- Portal de self-service (B2C)

---

## 6. Verticales de Negocio

Axioma puede servir tres verticales con distintos niveles de inversión de infraestructura. La elección de vertical define el go-to-market, los requisitos técnicos y el stack de inferencia.

---

### Vertical 1 — B2C / Developer SaaS

**Cliente objetivo:** Desarrolladores, startups, equipos pequeños que necesitan un RAG privado sin gestionar infraestructura.

**Propuesta de valor:** API lista para usar, onboarding en minutos, pago por uso.

| Feature | Status |
|---------|--------|
| API v1 pública | ✅ Listo |
| API Keys (`orag_...`) | ✅ Listo |
| Rate Limiting (free/pro/enterprise) | ✅ Listo |
| MCP (Cursor, Claude Desktop) | ✅ Listo |
| Analytics (Langfuse) | ✅ Configurado |
| Conectores (OneDrive, S3, etc.) | ✅ Listo |
| Rate Plans / Billing | ❌ Pendiente |
| Portal de self-service | ❌ Pendiente |

**LLM stack:** OpenAI / Anthropic via API (costos trasladados al cliente o absorbidos en el plan).

**Listo para producción:** 90% — falta billing y portal.

---

### Vertical 2 — B2B Cloud / Enterprise Managed

**Cliente objetivo:** Empresas medianas/grandes que quieren un RAG empresarial gestionado, con sus propios datos, SSO, auditoría y branding propio. Los datos viajan a APIs de LLM en cloud.

**Propuesta de valor:** Plataforma enterprise-grade, white-label, compliance parcial, sin gestión de infra de modelos.

| Feature | Status |
|---------|--------|
| OAuth/OIDC (Google, Microsoft) | ✅ Listo |
| API Keys | ✅ Listo |
| Multi-tenant (aislamiento por owner) | ✅ Listo |
| Rate Limiting | ✅ Listo |
| Conectores empresariales | ✅ Listo |
| SSO/SAML | ⚠️ Config OpenSearch |
| Audit Logs | ⚠️ Config OpenSearch |
| DLS/FLS (permisos granulares) | ⚠️ Config OpenSearch |
| White-label / Branding | ❌ Código frontend |

**LLM stack:** OpenAI / Anthropic / IBM Watsonx via API.

**Listo para producción:** 65% — falta SSO, Audit, White-label.

---

### Vertical 3 — B2B Enterprise Air-gap / On-premise

**Cliente objetivo:** Corporaciones en sectores regulados (banca, salud, gobierno, defensa) que **no pueden enviar datos a APIs externas**. Todo debe correr en su infraestructura o en cloud privado.

**Propuesta de valor:** RAG 100% privado — datos, modelos e inferencia en su propia infra. Cero datos salen de su red.

| Feature | Status |
|---------|--------|
| Toda la plataforma Axioma | ✅ Deploy on-premise |
| Ollama (modelos locales, single GPU) | ✅ Soportado |
| IBM Watsonx (modelos propios) | ✅ Soportado |
| **SGLang (inferencia de alto rendimiento)** | 🔵 Roadmap Q4 2026 |
| SSO/SAML | ⚠️ Config |
| Audit Logs | ⚠️ Config |
| Air-gap deployment guide | ❌ Pendiente |

**LLM stack:** SGLang + IBM Granite / Llama 3 / Qwen en GPUs propias del cliente.

**Listo para producción:** 40% — falta SGLang integration, air-gap guide, SSO.

**Diferenciador clave:** Axioma ya tiene Ollama como provider. SGLang es la evolución: misma compatibilidad OpenAI API, pero con RadixAttention (prefix caching), throughput 5-7x mayor y soporte para cargas enterprise multi-tenant.

---

### Resumen de verticales

| | B2C SaaS | B2B Cloud | B2B Air-gap |
|--|----------|-----------|-------------|
| **Datos en cloud API** | Sí | Sí | NO |
| **GPU propia necesaria** | No | No | Sí |
| **SSO/SAML** | No | Sí | Sí |
| **White-label** | Opcional | Sí | Sí |
| **Compliance nivel** | Bajo | Medio | Alto |
| **Precio** | Por uso | SaaS mensual | Licencia + soporte |
| **Time to market** | Ahora | Q2-Q3 2026 | Q4 2026+ |

---

## 7. Infraestructura de Inferencia — SGLang

### Qué es SGLang

[SGLang](https://github.com/sgl-project/sglang) es un framework de serving de LLMs de alto rendimiento. 25.8k stars en GitHub, `v0.5.10` (Abril 2026), en producción en más de 400.000 GPUs.

**Por qué importa para Axioma:** es la pieza que habilita la **Vertical 3 (Air-gap)** — permite correr modelos open source (Granite, Llama 3, Qwen) en la infra del cliente con performance enterprise.

### Innovación clave: RadixAttention

RadixAttention organiza el KV Cache en un árbol radix con política LRU. El impacto directo en RAG:

- **System prompts compartidos**: si 10 usuarios envían requests con el mismo system prompt de 2000 tokens, la GPU lo procesa una sola vez.
- **Documentos largos repetidos**: en multi-agente, si el Supervisor ya procesó un contrato de 50 páginas, el Agente Trabajador reutiliza el caché — cero recalculo.
- **Resultado medido**: 5-7x mayor throughput, latencia al primer token drásticamente reducida.

### Por qué es drop-in para Axioma

SGLang expone una **API 100% compatible con OpenAI**. Axioma ya tiene soporte multi-provider. Integrar SGLang es un cambio de configuración:

```bash
# .env — apuntar al servidor SGLang en lugar de OpenAI
OPENAI_BASE_URL=http://sglang-server:30000/v1
OPENAI_API_KEY=none  # SGLang no requiere key real
```

Cero cambios de código en Axioma para la integración básica.

### Modelos soportados relevantes para Axioma

| Modelo | Parámetros | GPU mínima | Caso de uso |
|--------|-----------|------------|-------------|
| IBM Granite 3.1 8B | 8B | 1x A100 40GB (FP8) | Chat RAG, clasificación |
| IBM Granite 3.1 34B | 34B | 2x A100 80GB | Razonamiento complejo |
| Llama 3.1 8B | 8B | 1x A100 40GB | General purpose |
| Llama 3.1 70B | 70B | 4x A100 80GB | Enterprise reasoning |
| Qwen2.5 7B | 7B | 1x A100 40GB | Multilingual |

Con cuantización FP8/INT4 los requisitos de GPU se reducen ~2x.

### Hardware mínimo viable (entrada)

| Configuración | GPU | VRAM | Modelos posibles |
|--------------|-----|------|-----------------|
| Entry (1 GPU) | NVIDIA A100 40GB | 40 GB | Granite 8B, Llama 8B (FP16) |
| Standard (1 GPU) | NVIDIA H100 80GB | 80 GB | Granite 34B, Llama 70B (FP8) |
| Scale (multi-GPU) | 4x H100 | 320 GB | Llama 70B (FP16), modelos mayores |

Para clientes enterprise con VMware/baremetal ya existente: AMD MI300 también es soportado.

### Plan de integración (Q4 2026)

1. Agregar `sglang` como provider en `src/config/settings.py` (junto a `openai`, `ollama`, etc.)
2. Configurar `OPENAI_BASE_URL` dinámico según provider seleccionado
3. `docker-compose.sglang.yml` — perfil de compose para deployments con GPU
4. Guía de air-gap deployment para enterprise
5. Benchmark comparativo: SGLang vs Ollama vs API cloud (latencia, throughput, costo)

---

## 9. Tech Debt & Known Issues

- [ ] No existe tests de integración con todos los conectores
- [ ] Documentación de API dispersa
- [ ] No hay CI/CD pipeline configurado
- [ ] Falta stress testing para B2C

---

## 10. Métricas Objetivo 2026

| Métrica | Target |
|---------|--------|
| Uptime | 99.9% |
| Latencia search | <200ms (p95) |
| Latencia chat | <3s (p95) |
| API Keys activas | 100+ |
| Clientes enterprise | 5+ |

---

## 11. Links Relevantes

- Repositorio: `axioma-2.0`
- Docs: `/docs` (Swagger)
- MCP: via Langflow (`/v1/mcp/...`)
- Analytics: Langfuse dashboard

---

## 12. Changelog

| Fecha | Cambio |
|-------|--------|
| 2026-04-13 | Creado roadmap 2026 |
| 2026-04-13 | Actualizado con feedback de features ya existentes (MCP, Langfuse, Swagger) |
| 2026-04-13 | Identificado Rate Limiting como PRIORIDAD #1 |
| 2026-04-13 | Spec creado: docs/specs/api-rate-limiting.md |
| 2026-04-13 | Diseño creado: docs/specs/api-rate-limiting-design.md |
| 2026-04-13 | Tasks creadas: docs/specs/api-rate-limiting-tasks.md |
| 2026-04-13 | Guía de implementación: docs/specs/rate-limiting-implementation-guide.md |
| 2026-04-13 | Actualizado roadmap con 90% resuelto insight |
| 2026-04-14 | Rate Limiting implementado: middleware, servicio Redis, 13 tests unitarios |
| 2026-04-14 | Redis agregado a docker-compose y pyproject.toml |
| 2026-04-14 | Tests pre-existentes corregidos (encryption, opensearch_security_setup) |
| 2026-04-14 | Langfuse marcado como configurado y activo |
| 2026-04-14 | docs/MCP-GUIDE.md: guía completa para conectar Cursor y Claude Desktop via MCP |
| 2026-04-14 | Swagger: título "Axioma API", descripción, openapi_tags y summaries en 16 endpoints públicos |
| 2026-04-14 | Q1 2026 completado al 100% |
| 2026-04-14 | Definidas 3 verticales: B2C SaaS, B2B Cloud, B2B Air-gap |
| 2026-04-14 | SGLang agregado al roadmap Q4 como motor de inferencia para Vertical 3 |

---

*Documento vivo — actualizar conforme evoluciona el proyecto*
