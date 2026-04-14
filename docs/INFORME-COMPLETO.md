# Informe Completo: Axioma 2.0

> Proyecto RAG empresarial basado en OpenRAG (langflow-ai/openrag)
> Última actualización: 2026-04-13

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
| Langfuse | ✅ | Analíticas (solo configurar .env) |

---

## 5. Lo que falta (10%)

### Prioridad Alta
| Feature | Estado | Descripción |
|---------|--------|-------------|
| **Rate Limiting** | 🔄 En Progreso | Control de requests por API key |

**Por qué es importante:** Sin Rate Limiting, un cliente puede:
- Gastar todos tus tokens de LLM
- Saturar tu OpenSearch
- Generarte facturas enormes

### Prioridad Media
| Feature | Estado |
|---------|--------|
| SSO/SAML Enterprise | ❌ |
| Audit Logs | ⚠️ |
| DLS/FLS permisos | ⚠️ |
| White-label | ❌ |

### Prioridad Baja
| Feature | Estado |
|---------|--------|
| Redis Cache | ❌ |
| Multi-language | ⚠️ |
| Rate Plans | ❌ |

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

## 7. El Futuro ( Roadmap 2026)

### Q1: Foundations (Ahora)
- [x] Review técnico
- [~] Rate Limiting ← **En proceso**
- [ ] Documentar MCP para clientes
- [ ] Pulir Swagger

### Q2: Enterprise B2B
- [ ] SSO/SAML
- [ ] Audit Logs
- [ ] Permisos granulares
- [ ] White-label

### Q3: Scale B2C
- [ ] Redis Cache
- [ ] Rate Plans (Free/Pro/Enterprise)
- [ ] Analytics Dashboard
- [ ] Multi-language

### Q4: Launch
- [ ] Performance
- [ ] Security audit
- [ ] Beta program
- [ ] Public launch

---

## 8. Métricas Objetivo 2026

| Métrica | Target |
|---------|--------|
| Uptime | 99.9% |
| Latencia búsqueda | <200ms |
| Latencia chat | <3s |
| API Keys activas | 100+ |
| Clientes enterprise | 5+ |

---

## 9. Cómo empezar

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
4. Implementar Rate Limiting
5. Desplegar

---

## 10. Diferenciadores

| Aspecto | Axioma 2.0 |
|---------|------------|
| **Self-hosted** | ✅ Tus datos nunca salen de tu infrastructure |
| **Multi-provider** | OpenAI, Anthropic, IBM, Ollama |
| **Conectores** | OneDrive, SharePoint, S3 |
| **MCP** | Conexión directa con Cursor/Claude |
| **Visual** | Langflow para diseñar agentes sin código |
| **Enterprise ready** | OAuth, OIDC, JWT |

---

## 11. Estado Actual

```
███░░░░░░░░░░░░░░░░░░░░░░░░░  85% B2C Listo
███████░░░░░░░░░░░░░░░░░░░░░  60% B2B Listo
```

**Falta:**
- Rate Limiting (código por implementar)
- SSO/SAML (para enterprise)
- White-label (para comercializar)

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
