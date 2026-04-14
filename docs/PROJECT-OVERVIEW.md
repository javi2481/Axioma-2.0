# Exploración Completa: Axioma-2.0 (OpenRAG)

## 1. Propósito del Proyecto

**OpenRAG** es una plataforma completa de **Retrieval-Augmented Generation (RAG)** que permite:

- **Ingestión de documentos**: PDF, texto, desde URLs, SharePoint, OneDrive, S3, IBM COS
- **Búsqueda semántica**: OpenSearch con embeddings dinámicos (soporta múltiples providers)
- **Chat con contexto**: Un agente conversacional que recupera contexto relevante y responde
- **Flows configurables**: Langflow para pipelines de AI customizables
- **Autenticación robusta**: OAuth/OIDC (Google, Microsoft) + JWT

### ¿Quién es el usuario objetivo?
- Equipos que necesitan un RAG privado y self-hosted
- Empresas que quieren controlar sus datos
- Desarrolladores que necesitan una plataforma extensible

---

## 2. Stack Técnico Detallado

### Backend
| Componente | Tecnología |
|------------|-------------|
| Lenguaje | Python 3.13+ |
| Framework | FastAPI |
| Server | uvicorn |
| Package Manager | uv |
| Logging | structlog |
| Metrics | Prometheus |

### Frontend
| Componente | Tecnología |
|------------|-------------|
| Framework | Next.js |
| Lenguaje | TypeScript |
| UI | React |

### Infraestructura
| Servicio | Tecnología |
|----------|-------------|
| Database | OpenSearch 3.x |
| Vector Store | OpenSearch (index con embeddings) |
| AI Pipeline | Langflow |
| Containers | Docker + Compose |

### AI/LLM Providers
- OpenAI (GPT-4, embeddings)
- Anthropic (Claude)
- IBM Watsonx
- Ollama (local)
- Modelos de embedding configurables

### Autenticación
- OAuth 2.0 (Google, Microsoft Graph)
- OIDC
- JWT (RSA signed)
- Modo "no-auth" para desarrollo

---

## 3. Estructura del Proyecto

```
axioma-2.0/
├── src/                          # Backend Python
│   ├── main.py                   # Entry point, startup, initialization
│   ├── api/                      # FastAPI endpoints
│   │   ├── auth.py               # /auth/* endpoints
│   │   ├── chat.py               # /chat/* - RAG conversation
│   │   ├── documents.py          # /documents/* - CRUD documentos
│   │   ├── search.py             # /search/* - búsqueda semántica
│   │   ├── flows.py              # /flows/* - Langflow management
│   │   ├── connectors.py         # /connectors/* - external integrations
│   │   ├── settings.py           # /settings/* - configuración
│   │   ├── tasks.py              # /tasks/* - background tasks
│   │   ├── docling.py            # /docling/* - document processing
│   │   ├── models.py             # /models/* - LLM config
│   │   ├── keys.py               # /keys/* - API keys
│   │   ├── knowledge_filter.py   # /knowledge_filter/*
│   │   ├── nudges.py             # /nudges/*
│   │   ├── router.py             # Router principal
│   │   └── v1/                   # API v1
│   │
│   ├── services/                 # Lógica de negocio
│   │   ├── document_service.py   # Ingestión, procesamiento
│   │   ├── search_service.py     # Búsqueda semántica
│   │   ├── chat_service.py       # RAG conversation
│   │   ├── task_service.py       # Background tasks
│   │   ├── flows_service.py      # Langflow management
│   │   ├── auth_service.py       # Autenticación
│   │   ├── models_service.py     # LLM configuration
│   │   ├── monitor_service.py    # Health monitoring
│   │   ├── langflow_mcp_service.py   # MCP server
│   │   ├── langflow_file_service.py  # File upload via Langflow
│   │   ├── knowledge_filter_service.py
│   │   ├── api_key_service.py    # API keys management
│   │   └── rate_limiter.py       # Rate limiting (Redis + fallback en memoria)
│   │
│   ├── auth/                     # Autenticación
│   │   └── ibm_auth.py           # IBM auth mode
│   │
│   ├── connectors/              # Conectores externos
│   │   ├── service.py            # Connector service
│   │   ├── base.py               # Base connector
│   │   ├── sharepoint/            # SharePoint connector
│   │   ├── onedrive/             # OneDrive connector
│   │   ├── connection_manager.py # Manage connections
│   │   └── langflow_connector_service.py
│   │
│   ├── models/                   # Pydantic models
│   │   ├── tasks.py
│   │   ├── processors.py
│   │   └── url.py
│   │
│   ├── utils/                    # Utilidades
│   │   ├── embeddings.py          # Embedding utilities
│   │   ├── opensearch_utils.py    # OpenSearch helpers
│   │   ├── encryption.py          # Encryption utilities
│   │   ├── docling_client.py      # Docling integration
│   │   ├── langflow_utils.py      # Langflow helpers
│   │   └── telemetry/            # Telemetry client
│   │
│   ├── tui/                      # Textual TUI
│   │   ├── main.py
│   │   ├── screens/
│   │   └── widgets/
│   │
│   ├── rate_limit_middleware.py  # Starlette middleware — rate limiting /v1/*
│   ├── session_manager.py        # JWT + user management
│   ├── agent.py                  # Agent logic
│   └── dependencies.py          # FastAPI dependencies
│
├── frontend/                     # Next.js app
├── sdks/                         # SDKs
│   ├── python/                  # Python SDK
│   └── typescript/               # TypeScript SDK
├── tests/
│   ├── unit/                    # Unit tests
│   └── integration/              # Integration tests
│       ├── core/
│       └── sdk/
├── flows/                       # Langflow JSON configs
├── config/                      # Runtime config
├── keys/                        # JWT keys
├── data/                        # Runtime data
├── openrag-documents/           # Default documents
└── docker-compose.yml           # Full stack
```

---

## 4. Arquitectura del Backend

### Flujo de Inicialización (src/main.py)

1. **Configuración temprana**:
   - `configure_from_env()` - setup logging
   - `enforce_startup_prerequisites()` - encryption, paths

2. **Generación de claves JWT**:
   - Genera RSA key pair si no existen
   - Permisos: private key 0600, public key 0644

3. **Servicios inicializados**:
   - `SessionManager` - JWT management
   - `AuthService` - OAuth/OIDC
   - `DocumentService` - document handling
   - `SearchService` - semantic search
   - `ChatService` - RAG conversation
   - `FlowsService` - Langflow management
   - `LangflowMCPService` - MCP server

4. **Startup tasks**:
   - Wait for OpenSearch
   - Setup OpenSearch security (roles, mappings)
   - Create indices (documents, knowledge_filters, api_keys)
   - Ingest default documents
   - Ensure Langflow flows exist
   - Check for flow resets

### Capas de la Arquitectura

```
┌─────────────────────────────────────────┐
│           API Layer (FastAPI)            │
│  /auth, /chat, /search, /documents, etc  │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│         Service Layer                    │
│  DocumentService, SearchService, etc    │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│        Connector Layer                  │
│  OpenSearch, Langflow, External APIs    │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│      Infrastructure Layer                │
│   OpenSearch, Docker, Langflow          │
└─────────────────────────────────────────┘
```

---

## 5. Autenticación y Seguridad

### Flujo OAuth/OIDC

1. Usuario inicia login con Google/Microsoft
2. Backend redirecciona al provider
3. Provider retorna authorization code
4. Backend intercambia por tokens
5. Sesión creada con JWT

### JWT

- **Algorithm**: RS256 (RSA)
- **Claims**: user_id, email, name, roles
- **Keys**: stored in `keys/` directory
- **Session**: managed by `SessionManager`

### OpenSearch Security

- Roles configurables
- Role mappings
- JWT authentication domain
- OIDC integration

### Encryption

- `OPENRAG_ENCRYPTION_KEY` para datos sensibles
- AES encryption utilities en `utils/encryption.py`

---

## 6. Flujo de Datos

### Ingestión de Documentos

```
Upload → DocumentService → Processor → 
  → Chunking → Embedding → OpenSearch
```

**Métodos de ingestión**:
1. **Traditional**: DocumentService directo
2. **Langflow**: Via Langflow pipeline (upload → ingest → delete)

### Búsqueda Semántica

```
Query → SearchService → Embedding →
  → OpenSearch k-NN → Results → Rank
```

### Chat RAG

```
User Message → ChatService → 
  → SearchService (retrieve context) →
  → Langflow (generate answer) →
  → Return response
```

---

## 7. Servicios Docker

| Servicio | Container | Puerto | Descripción |
|----------|-----------|--------|-------------|
| opensearch | os | 9200 | Motor de búsqueda + vector store |
| dashboards | osdash | 5601 | OpenSearch Dashboards |
| openrag-backend | openrag-backend | 8000 | API FastAPI |
| openrag-frontend | openrag-frontend | 3000 | Next.js UI |
| langflow | langflow | 7860 | Langflow UI + API |
| redis | axioma_redis | 6379 | Rate limiting + caché |

### Volúmenes

| Path en container | Host path | Descripción |
|-------------------|-----------|-------------|
| /app/openrag-documents | ./openrag-documents | Documentos |
| /app/keys | ./keys | Claves JWT |
| /app/flows | ./flows | Langflow flows |
| /app/config | ./config | Configuración |
| /app/data | ./data | Datos runtime |
| /app/langflow-data | ./langflow-data | Langflow DB |

---

## 8. API Endpoints

### Autenticación
- `GET /auth/login` - Login redirect
- `GET /auth/callback` - OAuth callback
- `POST /auth/logout` - Logout
- `GET /auth/me` - Current user

### Documentos
- `POST /documents/upload` - Upload file
- `GET /documents` - List documents
- `DELETE /documents/{id}` - Delete document

### Búsqueda
- `POST /search` - Semantic search
- `GET /search/filter` - Filter options

### Chat
- `POST /chat` - RAG conversation
- `GET /chat/history` - Conversation history

### Flows
- `GET /flows` - List flows
- `POST /flows/ensure` - Ensure flow exists
- `GET /flows/{id}/settings` - Get flow settings

### Settings
- `GET /settings` - Get config
- `PUT /settings` - Update config
- `POST /settings/reapply` - Reapply settings

---

## 9. Testing

### Framework
- **pytest** 8.x
- **pytest-asyncio** - async tests
- **pytest-mock** - mocking
- **pytest-cov** - coverage

### Estructura de Tests

```
tests/
├── unit/                    # Tests unitarios
│   ├── test_*.py           # 15+ archivos
│   └── conftest.py
├── integration/
│   ├── core/               # Core API tests
│   │   ├── test_api_endpoints.py
│   │   └── test_startup_ingest.py
│   └── sdk/                # SDK tests
│       ├── test_auth.py
│       ├── test_chat.py
│       ├── test_search.py
│       └── test_*.py
└── conftest.py
```

### Comandos

```bash
make test           # Todos los tests
make test-unit     # Solo unitarios
make test-integration  # Solo integración
make test-sdk      # SDK tests
make test-ci       # CI pipeline
```

---

## 10. SDKs

### Python SDK (`sdks/python/`)

```python
from openrag import OpenRAG

client = OpenRAG("http://localhost:3000")
# Chat
response = client.chat.send("How do I configure embedding?")
# Search
results = client.search.query("authentication setup")
# Documents
client.documents.upload("myfile.pdf")
```

### TypeScript SDK (`sdks/typescript/`)

```typescript
import { OpenRAG } from '@openrag/sdk';

const client = new OpenRAG({ baseUrl: 'http://localhost:3000' });
await client.chat.send('How do I configure embedding?');
```

---

## 11. Características Principales

### Document Processing
- PDF via Docling
- Chunking automático
- Metadata extraction
- Embedding dinámico según provider

### Knowledge Filters
- Filtros por owner, users, groups
- Queries customizadas
- Subscriptions

### MCP Server
- Langflow MCP service
- Global vars injection
- Provider credentials management

### Langflow Integration
- Flows management
- Settings reapplication
- Reset detection

### Background Tasks
- TaskService para tracking
- Progress updates
- Retry logic

---

## 12. Configuración

### Environment Variables Principales

| Variable | Descripción |
|----------|-------------|
| OPENSEARCH_HOST | Host de OpenSearch |
| OPENSEARCH_PASSWORD | Password admin |
| OPENAI_API_KEY | OpenAI key |
| OLLAMA_ENDPOINT | Ollama URL |
| LANGFLOW_URL | Langflow URL |
| GOOGLE_OAUTH_CLIENT_ID | Google OAuth |
| MICROSOFT_GRAPH_OAUTH_CLIENT_ID | Microsoft OAuth |
| SESSION_SECRET | JWT secret |
| OPENRAG_ENCRYPTION_KEY | Encryption key |
| REDIS_URL | URL de Redis (default: `redis://localhost:6379/0`) |
| RATE_LIMIT_ENABLED | Activa/desactiva rate limiting (default: `true`) |
| RATE_LIMIT_WINDOW | Ventana de tiempo en segundos (default: `60`) |
| RATE_LIMIT_FREE | Requests por ventana para tier free (default: `100`) |
| RATE_LIMIT_PRO | Requests por ventana para tier pro (default: `1000`) |

### Archivos de Config

- `config/openrag.yaml` - Runtime config
- `.env` - Environment variables
- `keys/private_key.pem` - JWT private key
- `keys/public_key.pem` - JWT public key

---

## 13. Puntos de Extensión

### Conectores Custom
- Heredar de `connectors/base.py`
- Implementar métodos CRUD
- Registrar en `ConnectorService`

### Providers Custom
- Configurar en `config/settings.py`
- Implementar embedding generation
- Añadir a supported providers

### Flows Custom
- Crear en Langflow UI
- Exportar JSON a `flows/`
- Configurar en settings

---

## Conclusión

**Axioma-2.0 (OpenRAG)** es una plataforma RAG enterprise-grade con:
- Arquitectura limpia (API → Services → Connectors)
- Autenticación robusta (OAuth + JWT)
- Múltiples proveedores AI
- SDKs para integración
- Altamente extensible

El proyecto está bien estructurado, con tests exhaustivos y documentación clara.
