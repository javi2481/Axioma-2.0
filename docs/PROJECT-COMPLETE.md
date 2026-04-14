# Axioma-2.0 (OpenRAG) — Proyecto Completo

> Documento maestro con toda la información del proyecto.
> Última actualización: 2026-04-13

---

## Tabla de Contenidos

1. [Resumen del Proyecto](#1-resumen-del-proyecto)
2. [Stack Tecnológico](#2-stack-tecnológico)
3. [Arquitectura](#3-arquitectura)
4. [Características Implementadas](#4-características-implementadas)
5. [API Pública](#5-api-pública)
6. [Verticales de Negocio (B2B/B2C)](#6-verticales-de-negocio-b2bb2c)
7. [Gaps y Soluciones](#7-gaps-y-soluciones)
8. [Roadmap 2026](#8-roadmap-2026)
9. [SDD - Rate Limiting](#9-sdd---rate-limiting)
10. [Enlaces](#10-enlaces)

---

## 1. Resumen del Proyecto

**Axioma** (anteriormente **OpenRAG**) es una plataforma **RAG (Retrieval-Augmented Generation)** self-hosted de nivel empresarial diseñada para:

- **Ingestión de documentos**: PDF, texto, SharePoint, OneDrive, S3, IBM COS
- **Búsqueda semántica híbrida**: k-NN + keyword + prefix matching
- **Chat con contexto**: RAG conversacional via Langflow
- **Flows configurables**: Langflow para pipelines de AI customizables
- **Autenticación robusta**: OAuth/OIDC, JWT, API Keys

### Propósito
- Plataforma de IA documental para empresas
- Alternativa privada y self-hosted a soluciones cloud como ChatGPT Enterprise
- Base para producto comercial (B2B y B2C)

### Diferenciadores
- Multi-tenant con aislamiento de datos
- Conectores empresariales (SharePoint, OneDrive, S3, IBM COS)
- Búsqueda híbrida avanzada
- Autenticación robusta

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

### AI/LLM Providers Soportados
- OpenAI (GPT-4, embeddings)
- Anthropic (Claude)
- IBM Watsonx
- Ollama (local)
- Embeddings: granite-embedding-278m-multilingual (12 idiomas)

---

## 3. Arquitectura

### Estructura del Proyecto

```
axioma-2.0/
├── src/                          # Backend Python
│   ├── main.py                   # Entry point
│   ├── api/                      # FastAPI endpoints
│   │   ├── auth.py, chat.py, documents.py, search.py
│   │   ├── flows.py, connectors.py, keys.py
│   │   └── v1/                   # API v1 pública
│   ├── services/                 # Lógica de negocio
│   │   ├── search_service.py     # Búsqueda semántica
│   │   ├── chat_service.py       # Chat RAG
│   │   ├── document_service.py   # Ingestión
│   │   ├── api_key_service.py    # API Keys
│   │   └── langflow_mcp_service.py
│   ├── connectors/               # Conectores externos
│   │   ├── base.py              # BaseConnector abstract
│   │   ├── onedrive/, sharepoint/
│   │   └── connection_manager.py
│   ├── session_manager.py        # JWT management
│   └── dependencies.py           # FastAPI dependencies
├── frontend/                     # Next.js app
├── sdks/                         # Python + TypeScript SDKs
├── tests/                        # Unit + Integration tests
├── flows/                        # Langflow configs
├── docker-compose.yml           # Full stack
└── Makefile                     # Automation
```

### Capas de la Arquitectura

```
┌─────────────────────────────────────────┐
│        API Layer (FastAPI)              │
│  /auth, /chat, /search, /documents      │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│          Service Layer                  │
│  DocumentService, SearchService, etc    │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│         Connector Layer                 │
│  OpenSearch, Langflow, APIs Externas    │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│        Infrastructure Layer             │
│   OpenSearch, Docker, Langflow          │
└─────────────────────────────────────────┘
```

### Flujo de Datos

**Ingestión:**
```
Upload → DocumentService → Processor → Chunking → Embedding → OpenSearch
```

**Búsqueda:**
```
Query → Embedding → OpenSearch k-NN → Results → Rank
```

**Chat RAG:**
```
User → ChatService → SearchService (context) → Langflow → Response
```

---

## 4. Características Implementadas

### ✅ Core RAG
- [x] Ingestión de documentos (PDF, texto, URL)
- [x] Chunking automático
- [x] Embedding multi-provider (OpenAI, Ollama, WatsonX)
- [x] Búsqueda semántica híbrida
- [x] Chat con RAG via Langflow
- [x] Knowledge filters (ACL)

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

### ✅ Conectores
- [x] OneDrive (OAuth, selective sync, webhooks)
- [x] SharePoint (OAuth, ACL per file)
- [x] S3 (buckets, filtros)
- [x] IBM COS (buckets, regional)
- [x] BaseConnector abstracto (extensible)

### ✅ Infra & DevOps
- [x] Docker Compose
- [x] Makefile automation
- [x] OpenSearch security
- [x] Docling integration

### ✅ Observabilidad
- [x] Langfuse integration (configurar .env)
- [x] Prometheus metrics
- [x] Structlog logging
- [x] Telemetry client

### ✅ Documentación
- [x] Swagger/OpenAPI (`/docs`)
- [x] FastAPI native

### ✅ MCP
- [x] Servidor MCP nativo via Langflow
- [x] Herramientas: chat, search, config

---

## 5. API Pública

### Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/search` | POST | Búsqueda semántica |
| `/api/v1/chat` | POST | Chat RAG |
| `/api/v1/documents` | POST | Upload documento |
| `/api/v1/models` | GET | Modelos disponibles |
| `/api/v1/knowledge_filters` | GET | Filtros |
| `/v1/mcp/...` | GET | Servidor MCP |

### API Keys

- **Formato**: `orag_{random_32_chars}`
- **Hash**: SHA-256 para storage
- **Prefix display**: `orag_{first_8_chars}`

### Autenticación

```bash
Authorization: Bearer orag_xxxxxxxxxxxx
```

### Rate Limiting (EN PROGRESO)

| Tier | Límite |
|------|--------|
| Free | 100 req/min |
| Pro | 1000 req/min |
| Enterprise | Ilimitado |

---

## 6. Verticales de Negocio (B2B/B2C)

### B2B — Casos de Uso

| # | Caso de Uso | Descripción |
|---|-------------|-------------|
| 1 | Knowledge Base Interno | Wiki corporativo, políticas |
| 2 | Soporte al Cliente B2B | Base conocimiento soporte |
| 3 | Asistente de Ventas | Documentación productos |
| 4 | Gestión Documental | Búsqueda contratos |
| 5 | Compliance/Regulatorio | Docs regulatorios |
| 6 | Help Desk IT | Knowledge base tickets |

### B2C — Casos de Uso

| # | Caso de Uso | Descripción |
|---|-------------|-------------|
| 1 | Customer Support Chatbot | FAQ, troubleshooting |
| 2 | Product Documentation | Manuales, guías |
| 3 | Chat de Ventas | Pre-sales |
| 4 | Community Q&A | Foro interno |
| 5 | User Guide/Manual | Docs interactivos |

### Estado por Vertical

| Vertical | Listo | Faltante |
|----------|-------|----------|
| **B2B** | 60% | SSO, Audit, White-label |
| **B2C** | 85% | Rate Limiting (casi listo) |

---

## 7. Gaps y Soluciones

### B2B

| Gap | Solución |
|-----|----------|
| SSO/SAML | IdP (Auth0/Keycloak) + OpenSearch SAML |
| Audit Logs | OpenSearch Audit Logs nativo |
| Permisos granulares | DLS + FLS |
| White-label | Fork + Vercel v0 en /frontend |

### B2C

| Gap | Solución |
|-----|----------|
| Caching | Redis LangCache (futuro) |
| Analytics | Langfuse (ya integrado, configurar .env) |
| Rate Limiting | **EN IMPLEMENTACIÓN** |
| Multi-language | granite-embedding + reranker |

---

## 8. Roadmap 2026

### Q1: Foundations (Ahora)

```
[x]    Review técnico final
[~]    Rate Limiting (Spec + Design + Tasks listos)
[ ]    Documentar API MCP para clientes
[ ]    Pulir docstrings + Swagger
```

### Q2: Enterprise B2B

```
[ ]    SSO/SAML setup
[ ]    OpenSearch Audit Logs
[ ]    DLS/FLS granular permissions
[ ]    White-label base
```

### Q3: Scale B2C

```
[ ]    Redis LangCache
[ ]    Rate plans (Free/Pro/Enterprise)
[ ]    Analytics dashboard
[ ]    Multi-language support
```

### Q4: Polish & Launch

```
[ ]    Performance optimization
[ ]    Security audit
[ ]    Beta program
[ ]    Public launch
```

---

## 9. SDD - Rate Limiting

### Estado de Fases SDD

| Fase | Status | Artefacto |
|------|--------|-----------|
| sdd-init | ✅ | sdd-init/axioma-2.0 |
| sdd-explore | ✅ | 6 exploraciones |
| sdd-propose | ✅ | sdd/rate-limiting/proposal |
| sdd-spec | ✅ | sdd/rate-limiting/spec |
| sdd-design | ✅ | sdd/rate-limiting/design |
| sdd-tasks | ✅ | sdd/rate-limiting/tasks |

### Tareas (18 total)

**Phase 1: Foundation (3)**
- [ ] 1.1 Add RATE_LIMITS config
- [ ] 1.2 Add Redis config
- [ ] 1.3 Add Redis client in main.py

**Phase 2: Core (4)**
- [ ] 2.1 Create rate_limiter.py
- [ ] 2.2 check_limit() method
- [ ] 2.3 increment() method
- [ ] 2.4 get_tier() method

**Phase 3: Integration (6)**
- [ ] 3.1 get_rate_limiter dependency
- [ ] 3.2-3.6 Add to 6 endpoints

**Phase 4: Testing (5)**
- [ ] 4.1-4.5 Unit + Integration tests

**Phase 5: Cleanup (3)**
- [ ] 5.1-5.3 Docstrings, logs, docs

---

## 10. Enlaces

### Repositorio
- GitHub: `javi2481/Axioma-2.0`

### Documentación del Proyecto
- `/docs/ROADMAP-2026.md` — Roadmap maestro
- `/docs/specs/api-rate-limiting.md` — Spec
- `/docs/specs/api-rate-limiting-design.md` — Design
- `/docs/specs/api-rate-limiting-tasks.md` — Tasks

### API
- Swagger: `/docs` (cuando el servidor corre)

### Métricas Objetivo 2026

| Métrica | Target |
|---------|--------|
| Uptime | 99.9% |
| Latencia search | <200ms (p95) |
| Latencia chat | <3s (p95) |
| API Keys activas | 100+ |
| Clientes enterprise | 5+ |

---

*Documento vivo — actualizar conforme evoluciona el proyecto*
*Creado: 2026-04-13*
*SDD Phases: Init → Explore → Propose → Spec → Design → Tasks*
