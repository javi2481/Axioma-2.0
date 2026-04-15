# Informe Completo: Axioma 2.0

> Proyecto RAG empresarial basado en OpenRAG (langflow-ai/openrag)
> **Descubrimiento clave: El 90% ya está resuelto. Solo 10% requiere código.**
> Última actualización: 2026-04-15

---

## TL;DR: Lo que SÍ hay que hacer

```
┌─────────────────────────────────────────────────────────────────┐
│                     AXIOMA 2.0                                  │
├─────────────────────────────────────────────────────────────────┤
│  ✅ HECHO (código + configuración)                            │
│  ─────────────────────────────────────────────────────────   │
│  • Rate Limiting ← COMPLETADO 2026-04-14                     │
│  • Migración Redis → Valkey 9.x ← COMPLETADO 2026-04-14     │
│  • Valkey I/O threading + OpenSearch RRF ← 2026-04-15       │
│  • Ragas batch eval nocturno ← 2026-04-15                   │
│  • LLMRouter + Granite 4.0 H-Tiny ← 2026-04-15             │
│  • Granite Guardian 3.3 async guardrail ← 2026-04-15        │
│  • HybridChunker + Context Expansion ← 2026-04-15           │
│  • SSO/SAML (OpenSearch — configuración)                     │
│  • DLS/FLS (OpenSearch — configuración)                      │
│  • Audit Logs (OpenSearch — configuración)                   │
│  • Multi-language (.env)                                     │
│                                                               │
│  💻 CÓDIGO PENDIENTE                                          │
│  ─────────────────                                            │
│  • White-label (frontend)                                    │
│  • APIs, Conectores, Auth, etc   │                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Qué es Axioma 2.0

**Axioma 2.0** es una plataforma de **Retrieval-Augmented Generation (RAG)** self-hosted de nivel empresarial. 

En términos simples: **Es un motor de búsqueda inteligente con IA que permite a las empresas:**

- Subir documentos (PDFs, Word, etc) y hacer que la IA los entienda
- Buscar información usando lenguaje natural ("¿Qué dice el contrato sobre la garantía?")
- Chatear con los documentos ("Explicame este informe en 3 puntos")
- Crear agentes especializados (Legal, Financiero, Soporte)

**Básicamente:** Es como tener un empleado virtual que leyó TODOS los documentos de la empresa y puede responder cualquier pregunta.

---

## 2. Lo que hace (Funcionalidades)

### 2.1 Ingestión de Documentos
- **Qué hace:** Procesa documentos de múltiples fuentes
- **Fuentes:** PDFs, texto, URLs, SharePoint, OneDrive, S3, IBM Cloud Object Storage
- **Cómo:** Usa Docling para OCR y extracción inteligente de contenido
- **Resultado:** Documentos chunkeados y listos para búsqueda

### 2.2 Búsqueda Semántica Híbrida
- **Qué hace:** Busca en los documentos usando lenguaje natural
- **Cómo funciona:**
  - Búsqueda vectorial (semántica) — entiende el significado
  - Búsqueda por palabras clave — coincidencia exacta
  - RRF (Reciprocal Rank Fusion) — combina ambos para mejores resultados
- **Resultado:** Encuentra lo que buscas aunque uses sinónimos o preguntas vagas

### 2.3 Chat con Contexto (RAG)
- **Qué hace:** Respon preguntas sobre tus documentos
- **Cómo:**
  1. Tu pregunta → búsqueda en documentos
  2. Recupera contexto relevante
  3. Envía pregunta + contexto al LLM
  4. El LLM responde usando solo tus documentos
- **Resultado:** Respuestas precisas basadas en TU información

### 2.4 Agentes Especializados
- **Qué hace:** Crea agentes con conocimientos específicos
- **Cómo:** Langflow (interfaz visual drag-and-drop)
- **Ejemplos:**
  - Agente Legal → sabe de contratos, cláusulas
  - Agente Financiero → sabe de estados financieros
  - Agente Soporte → sabe de FAQs y troubleshooting

### 2.5 Conectores Empresariales
- **Qué hace:** Se conecta a servicios externos para traer documentos
- **Disponibles:**
  - Microsoft OneDrive
  - SharePoint
  - Amazon S3
  - IBM COS

---

## 3. Lo que tiene (Stack Tecnológico)

### Backend
| Tecnología | Para qué |
|------------|-----------|
| Python 3.13+ | Lenguaje principal |
| FastAPI | API REST |
| uvicorn | Servidor |
| structlog | Logging |

### Base de Datos
| Tecnología | Para qué |
|------------|-----------|
| OpenSearch 3.x | Búsqueda + Vector Store |

### AI/ML
| Tecnología | Para qué |
|------------|-----------|
| Langflow | Orquestación de agentes |
| Docling | Procesamiento de documentos |
| OpenAI | LLM (GPT-4) |
| Anthropic | LLM (Claude) |
| IBM Watsonx | LLM empresarial |
| Ollama | LLM local |

### Frontend
| Tecnología | Para qué |
|------------|-----------|
| Next.js | Interfaz web |
| TypeScript | Tipado |
| React | Componentes UI |

### Infra
| Tecnología | Para qué |
|------------|-----------|
| Docker Compose | Contenedores |
| OAuth/OIDC | Autenticación |
| JWT | Sesiones |

---

## 4. Lo que ya está resuelto (90%)

**Del código base de OpenRAG, ya viene listo:**

| Feature | Estado | Descripción |
|---------|--------|-------------|
| Docling | ✅ | OCR, chunking automático |
| OpenSearch | ✅ | Búsqueda híbrida con RRF |
| Langflow | ✅ | Agentes visuales |
| APIs FastAPI | ✅ | /v1/chat, /v1/search, /v1/documents |
| MCP Server | ✅ | Conexión con Cursor/Claude Desktop |
| OAuth | ✅ | Google, Microsoft |
| API Keys | ✅ | Autenticación API pública |
| Conectores | ✅ | OneDrive, SharePoint, S3 |
| Langfuse | ✅ | Observabilidad y evaluación — variables configuradas |

---

## 5. Lo que falta (CORREGIDO)

> ⚠️ IMPORTANTE: Revisando el análisis original, varias features marcadas como "faltante" en realidad YA ESTÁN RESUELTAS por el ecosistema subyacente (OpenSearch, Granite). No necesitas código — solo configuración.

### Lo que SÍ hay que codificar (Tus verdaderos gaps)

| Feature | Estado | Cómo resolverlo |
|---------|--------|-----------------|
| **Rate Limiting** | ✅ Implementado | `src/rate_limit_middleware.py` + Valkey |
| **White-label** | 🔴 Por implementar | Frontend: Vercel v0 + Next.js |

### Lo que parece "faltar" pero ya está resuelto (solo configuración)

| Feature | Estado | Cómo resolverlo |
|---------|--------|-----------------|
| **SSO/SAML Enterprise** | ⚠️ Config | OpenSearch Security: SAML, OIDC, AD, LDAP nativos |
| **Permisos Granulares (DLS/FLS)** | ⚠️ Config | OpenSearch DLS/FLS nativos — sin Python |
| **Audit Logs** | ⚠️ Config | OpenSearch Audit Logs nativos — activar en config |
| **Multi-language** | ⚠️ Config | granite-embedding-278m-multilingual (12 idiomas) |

---

## 6. Lo que puede hacer (Casos de Uso)

### B2B (Empresas)
1. **Knowledge Base Interno**
   - Wiki corporativo, políticas, procedimientos
   - Empleados preguntan y la IA responde

2. **Soporte al Cliente**
   - Base de conocimiento para equipo de soporte
   - Respuestas rápidas y consistentes

3. **Gestión Documental**
   - Búsqueda en contratos, documentos legales
   - Encontrar cláusulas específicas

4. **Asistente de Ventas**
   - Documentación de productos
   - Competitor analysis

### B2C (Consumidores)
1. **Customer Support Chatbot**
   - FAQ automático
   - Troubleshooting 24/7

2. **Product Documentation**
   - Manuales interactivos
   - Chat con el manual

3. **Chat de Ventas**
   - Información de productos
   - Pre-sales

---

## 7. Lo que SÍ hay que codificar

> Resumen corregido: Solo 2 cosas necesitan código. El resto es configuración.

### Código (Desarrollo)

| Feature | Estado | Descripción |
|---------|--------|-------------|
| **Rate Limiting** | ✅ Implementado | Valkey 9.x + Starlette middleware + fallback en memoria |
| **White-label** | 🔴 Por implementar | Frontend con Vercel v0 |

### Configuración (No requiere código)

| Feature | Estado | Descripción |
|---------|--------|-------------|
| SSO/SAML | ⚠️ Config | OpenSearch native (SAML, OIDC, AD, LDAP) |
| DLS/FLS | ⚠️ Config | OpenSearch Document/Field Level Security |
| Audit Logs | ⚠️ Config | OpenSearch Audit Logs (activar) |
| Multi-language | ⚠️ Config | granite-embedding-278m-multilingual |

---

## 8. El Futuro ( Roadmap 2026)

### Fase 0 + Fase 1 ✅ COMPLETADAS (2026-04-14/15)
- [x] Migración Redis → Valkey 9.x (BSD-3-Clause) ← **2026-04-14**
- [x] Rate Limiting ← **2026-04-14**
- [x] Documentar MCP para clientes ← **2026-04-14**
- [x] Valkey I/O threading (4 threads, lazyfree) ← **2026-04-15**
- [x] OpenSearch hybrid + RRF normalization pipeline ← **2026-04-15**
- [x] Ragas batch eval nocturno con Langfuse ← **2026-04-15**

### Fase 2 ✅ COMPLETA (2026-04-15)
- [x] LLMRouter + Granite 4.0 H-Tiny (Ollama, toggle SGLang) ← **2026-04-15**
- [x] Granite Guardian 3.3 async guardrail ← **2026-04-15**
- [x] HybridChunker + Context Expansion ← **2026-04-15**

### Fase 3: Diferenciación Enterprise (Q2-Q3 2026)
- [ ] SGLang backend (`GRANITE_BACKEND=sglang`) — RadixAttention MoE
- [ ] Self-RAG / CRAG patterns en Langflow
- [ ] Valkey HEXPIRE per-field TTL (sesiones multi-agente)
- [ ] Multi-agent Langflow + MCP externo (Slack, SQL, Jira)
- [ ] Grafana AIOps dashboards

### Q2: Enterprise B2B (Configuración)
- [ ] SSO/SAML ← Config OpenSearch
- [ ] Audit Logs ← Config OpenSearch
- [ ] DLS/FLS ← Config OpenSearch
- [ ] White-label ← Código Vercel v0

### Q3: Scale B2C
- [ ] Valkey Cache (opcional)
- [ ] Rate Plans
- [x] Analytics Dashboard (Langfuse — configurado)
- [ ] Multi-language (config Granite)

### Q4: Launch
- [ ] Performance
- [ ] Security audit
- [ ] Beta program
- [ ] Public launch

---

## 12. Métricas Objetivo 2026

| Métrica | Target |
|---------|--------|
| Uptime | 99.9% |
| Latencia búsqueda | <200ms |
| Latencia chat | <3s |
| API Keys activas | 100+ |
| Clientes enterprise | 5+ |

---

## 13. Cómo empezar

### Para desarrollo
```bash
# Clonar el repo
git clone https://github.com/javi2481/Axioma-2.0.git

# Configurar .env con tus API keys
cp .env.example .env

# Levantar todo
make dev

# Acceder
# http://localhost:3000 (Frontend)
# http://localhost:8000/docs (API)
```

### Para producción
1. Configurar `.env` con tus proveedores
2. Diseñar agentes en Langflow
3. Personalizar frontend con tu marca
4. Desplegar

---

## 14. Diferenciadores

| Aspecto | Axioma 2.0 |
|---------|------------|
| **Self-hosted** | ✅ Tus datos nunca salen de tu infrastructure |
| **Multi-provider** | OpenAI, Anthropic, IBM, Ollama |
| **Conectores** | OneDrive, SharePoint, S3 |
| **MCP** | Conexión directa con Cursor/Claude |
| **Visual** | Langflow para diseñar agentes sin código |
| **Enterprise ready** | OAuth, OIDC, JWT |

---

## 15. Estado Actual (CORREGIDO)

```
████████████░░░░░░░░░░░░░░░  90% Resuelto (configuración)
███░░░░░░░░░░░░░░░░░░░░░░░░░  10% Por hacer (código)
```

### Lo que SÍ requiere código

| Feature | Prioridad | Estado |
|---------|-----------|--------|
| **Rate Limiting** | Alta | ✅ Implementado |
| **White-label** | Alta | 🔴 Por implementar |

### Lo que es configuración (NO código)

| Feature | Estado | Responsable |
|---------|--------|-------------|
| SSO/SAML | ⚠️ Config | OpenSearch |
| DLS/FLS | ⚠️ Config | OpenSearch |
| Audit Logs | ⚠️ Config | OpenSearch |
| Multi-language | ⚠️ Config | .env (Granite) |

---

## 12. Enlaces

- **Repo:** https://github.com/javi2481/Axioma-2.0
- **Base:** https://github.com/langflow-ai/openrag
- **Documentación:**
  - `docs/ROADMAP-2026.md`
  - `docs/PROJECT-COMPLETE.md`
  - `docs/PROJECT-OVERVIEW.md`

---

*Creado: 2026-04-13*
*Proyecto basado en langflow-ai/openrag*
