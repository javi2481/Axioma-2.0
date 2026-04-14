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
[ ]    Documentar API MCP para clientes
[ ]    Pulir docstrings + Swagger
```

**Responsable:** Backend Team  
**Entregables:**
- ✅ Middleware de rate limiting (Redis + Starlette + fallback en memoria)
- ✅ Tests unitarios completos (13 tests)
- ✅ Redis en docker-compose con healthcheck
- Documentación técnica para clientes
- OpenAPI spec pulida

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

### Q4 2026: polish & Launch

```
[ ]    Performance optimization
[ ]    Security audit
[ ]    Beta program
[ ]    Public launch
[ ]    Customer onboarding flow
```

**Responsable:** Full Team  
**Entregables:**
- GA release
- Documentación para clientes
- Portal de desarrollador

---

## 6. Estado por Vertical

### B2B (Enterprise)

| Feature | Status |
|---------|--------|
| OAuth/OIDC | ✅ Listo |
| API Keys | ✅ Listo |
| DLS/FLS | ⚠️ Configurar |
| SSO/SAML | ❌ Por implementar |
| Audit Logs | ⚠️ Configurar |
| White-label | ❌ Por implementar |

**Listo para:** 60%

### B2C (Consumer)

| Feature | Status |
|---------|--------|
| API Keys | ✅ Listo |
| API v1 | ✅ Listo |
| MCP | ✅ Listo (falta doc) |
| Rate Limiting | ✅ Implementado |
| Analytics | ✅ Configurar |
| Cache | ❌ Por implementar |

**Listo para:** 100%

---

## 7. Tech Debt & Known Issues

- [ ] No existe tests de integración con todos los conectores
- [ ] Documentación de API dispersa
- [ ] No hay CI/CD pipeline configurado
- [ ] Falta stress testing para B2C

---

## 8. Métricas Objetivo 2026

| Métrica | Target |
|---------|--------|
| Uptime | 99.9% |
| Latencia search | <200ms (p95) |
| Latencia chat | <3s (p95) |
| API Keys activas | 100+ |
| Clientes enterprise | 5+ |

---

## 9. Links Relevantes

- Repositorio: `axioma-2.0`
- Docs: `/docs` (Swagger)
- MCP: via Langflow (`/v1/mcp/...`)
- Analytics: Langfuse dashboard

---

## 10. Changelog

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

---

*Documento vivo — actualizar conforme evoluciona el proyecto*
