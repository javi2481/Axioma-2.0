# Axioma-2.0 (OpenRAG) — Roadmap 2026

> Documento maestro con el estado actual del proyecto y plan a futuro.
> Última actualización: 2026-04-13

---

## 1. Qué es Axioma-2.0 (OpenRAG)

**Axioma** es una plataforma **RAG (Retrieval-Augmented Generation)** self-hosted de nivel empresarial diseñada para ingestion, búsqueda semántica y conversaciones con contexto.

### Propósito
- plataforma de IA documental para empresas
- Alternativa privada y self-hosted a soluciones cloud como ChatGPT Enterprise o Azure AI Search
- Base para producto comercial (B2B y B2C)

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
- [x] Langfuse integration (solo configurar .env)
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
| 1 | **Rate Limiting** | 🔄 En Progreso | Throttling por API key para controlar costos |
| 2 | **MCP Documentation** | ⚠️ | Documentar endpoints MCP para clientes |
| 3 | **Swagger Polish** | ⚠️ | Pulir docstrings y descripciones |

### 🟡 PRIORIDAD MEDIA (Q2-Q3 2026)

| # | Feature | Estado | Descripción |
|---|---------|--------|-------------|
| 4 | SSO/SAML Enterprise | ❌ | Para clientes que requieren IdP corporativo |
| 5 | Audit Logs | ⚠️ | OpenSearch tiene audit, falta dashboard |
| 6 | Permisos Granulares (DLS/FLS) | ⚠️ | Configurar Document/Field Level Security |
| 7 | White-label / Theming | ❌ | Fork + personalización frontend |

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
[~]    Rate Limiting ← PRIORIDAD #1 (Spec creado: api-rate-limiting)
[ ]    Documentar API MCP para clientes
[ ]    Pulir docstrings + Swagger
```

**Responsable:** Backend Team  
**Entregables:**
- Middleware de rate limiting (Redis o slowapi)
- Documentación técnica para clientes
- OpenAPI spec pulida

**Spec creado:** `docs/specs/api-rate-limiting.md`

---

### Q2 2026: Enterprise B2B

```
[ ]    SSO/SAML setup (Auth0/Keycloak bridge)
[ ]    OpenSearch Audit Logs configuration
[ ]    DLS/FLS granular permissions
[ ]    White-label base (theming)
```

**Responsable:** DevOps + Backend  
**Entregables:**
- SSO con IdP corporativos
- Dashboard de auditoría
- Control de acceso granular
- Tema custom para frontend

---

### Q3 2026: Scale B2C

```
[ ]    Redis LangCache
[ ]    Rate plans (Free/Pro/Enterprise)
[ ]    Analytics dashboard (Langfuse)
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
| Rate Limiting | 🔄 Spec creado |
| Analytics | ✅ Configurar |
| Cache | ❌ Por implementar |

**Listo para:** 80% → 85%

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
| 2026-04-13 | Creado spec para api-rate-limiting |
| 2026-04-13 | Propuesta y spec guardados en Engram |
| 2026-04-13 | Spec creado: docs/specs/api-rate-limiting.md |
| 2026-04-13 | Diseño creado: docs/specs/api-rate-limiting-design.md |

---

*Documento vivo — actualizar conforme evoluciona el proyecto*
