# Conectar AI tools a Axioma via MCP

[Model Context Protocol](https://modelcontextprotocol.io/) (MCP) es la forma en que Cursor, Claude Desktop y otros IDEs con IA se conectan a tu instancia de Axioma para usar sus capacidades RAG directamente desde el editor.

---

## Qué es MCP en Axioma

Axioma expone un servidor MCP como subproceso (`openrag-mcp`) que el IDE levanta automáticamente desde su archivo de configuración. El servidor se comunica con la API pública de Axioma (`/v1/*`) usando tu API key — no hay ningún servicio extra que desplegar.

```
IDE (Cursor / Claude Desktop)
    └── subprocess: openrag-mcp
            └── HTTP → Axioma /v1/* (X-API-Key: orag_...)
```

> **Nota sobre los nombres de variables:** Las variables de entorno usan el prefijo `OPENRAG_` por compatibilidad histórica. El nombre del producto es Axioma, pero los nombres de las variables no cambian.

---

## Prerequisitos

- Python 3.10+
- Una instancia de Axioma corriendo (anota la URL base, ej: `http://localhost:3000`)
- Un API key de Axioma (formato `orag_...`) — crealo en **Settings → API Keys**
- `uv` instalado ([instrucciones](https://docs.astral.sh/uv/))

---

## Herramientas disponibles

Una vez conectado, tu IDE puede usar estas herramientas directamente:

| Herramienta | Descripción |
|:------------|:------------|
| `openrag_chat` | Envía un mensaje y recibe una respuesta grounded en tu knowledge base. Soporta `chat_id`, `filter_id`, `limit`, `score_threshold`. |
| `openrag_search` | Búsqueda semántica sobre la knowledge base. Soporta `limit`, `score_threshold`, `filter_id`, `data_sources`, `document_types`. |
| `openrag_get_settings` | Lee la configuración actual de Axioma (LLM, embeddings, chunk settings, system prompt). |
| `openrag_update_settings` | Actualiza la configuración de Axioma (modelo LLM, embedding, chunk size/overlap, system prompt, OCR, etc.). |
| `openrag_list_models` | Lista los modelos disponibles para un provider (`openai`, `anthropic`, `ollama`, `watsonx`). |

> Las herramientas de gestión de documentos (`openrag_ingest_file`, `openrag_delete_document`, etc.) están implementadas pero aún no habilitadas — se activarán en una versión futura.

---

## Conectar Cursor

**Archivo de config:** `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "axioma": {
      "command": "uvx",
      "args": ["openrag-mcp"],
      "env": {
        "OPENRAG_URL": "https://tu-instancia-axioma.com",
        "OPENRAG_API_KEY": "orag_tu_api_key"
      }
    }
  }
}
```

Reiniciá Cursor después de guardar el archivo.

---

## Conectar Claude Desktop

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "axioma": {
      "command": "uvx",
      "args": ["openrag-mcp"],
      "env": {
        "OPENRAG_URL": "https://tu-instancia-axioma.com",
        "OPENRAG_API_KEY": "orag_tu_api_key"
      }
    }
  }
}
```

Reiniciá Claude Desktop después de editar el archivo.

---

## Variables de entorno

### Requeridas

| Variable | Descripción |
|:---------|:------------|
| `OPENRAG_API_KEY` | Tu API key de Axioma (`orag_...`) |
| `OPENRAG_URL` | URL base de tu instancia (default: `http://localhost:3000`) |

### Opcionales (cliente HTTP)

| Variable | Descripción | Default |
|:---------|:------------|:--------|
| `OPENRAG_MCP_TIMEOUT` | Timeout de requests en segundos | `60.0` |
| `OPENRAG_MCP_MAX_CONNECTIONS` | Máximo de conexiones simultáneas | `100` |
| `OPENRAG_MCP_MAX_KEEPALIVE_CONNECTIONS` | Máximo de conexiones keepalive | `20` |
| `OPENRAG_MCP_MAX_RETRIES` | Máximo de reintentos ante fallo | `3` |
| `OPENRAG_MCP_FOLLOW_REDIRECTS` | Seguir redirects HTTP | `true` |

Estas variables se pasan en el bloque `env` del config del cliente MCP.

---

## Ejecutar desde el código fuente (desarrollo)

Para usar la versión más reciente del código MCP del repo en lugar del paquete publicado en PyPI:

### Pasos

| Paso | Qué hacer | Comando |
|------|-----------|---------|
| 1 | Levantar Axioma | Correr el backend normalmente |
| 2 | Sincronizar dependencias MCP | `cd sdks/mcp && uv sync` |
| 3 | (Opcional) SDK desde repo | `cd sdks/python && uv pip install -e .` |

### Correr el MCP desde el repo

```bash
cd sdks/mcp
uv sync
export OPENRAG_URL="http://localhost:3000"
export OPENRAG_API_KEY="orag_tu_api_key"
uv run openrag-mcp
```

### Config de Cursor apuntando al repo

En `~/.cursor/mcp.json`, usá `--directory` para que Cursor ejecute el código del repo:

```json
{
  "mcpServers": {
    "axioma": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/ruta/a/axioma-2.0/sdks/mcp",
        "openrag-mcp"
      ],
      "env": {
        "OPENRAG_URL": "https://tu-instancia-axioma.com",
        "OPENRAG_API_KEY": "orag_tu_api_key"
      }
    }
  }
}
```

Reemplazá `/ruta/a/axioma-2.0` con el path real del repo. Si previamente instalaste el paquete via pip, desinstalalo:

```bash
uv pip uninstall openrag-mcp
```

Luego reiniciá Cursor.

---

## Prompts de ejemplo

Una vez configurado, podés pedirle a tu AI:

- *"Buscá en mi knowledge base las mejores prácticas de autenticación"*
- *"Chateá con Axioma sobre el roadmap de Q3"*
- *"¿Cuál es la configuración actual de Axioma?"*
- *"Listá los modelos disponibles para el provider openai"*
- *"Actualizá Axioma para usar chunk size 512"*

---

## Troubleshooting

### "OPENRAG_API_KEY environment variable is required"

Falta la variable en el bloque `env` del config del cliente. El servidor la lee al arrancar.

### "Connection refused" o errores de red

1. Confirmá que tu instancia de Axioma está corriendo y es accesible.
2. Revisá `OPENRAG_URL` (sin trailing slash; incluí `https://` si corresponde).
3. Verificá que no hay firewall o proxy bloqueando la conexión.

### Las herramientas no aparecen en el IDE

1. Reiniciá el IDE después de cambiar el config MCP.
2. Revisá la consola MCP del IDE para ver errores (`command`/`args` incorrectos, `uv`/`uvx` no instalado).
3. Si usás "run from source", confirmá que `args` incluye `--directory` con el path correcto a `sdks/mcp`.

---

## Links

- [Axioma API Reference](http://localhost:3000/docs) — Swagger interactivo (requiere instancia corriendo)
- [Model Context Protocol](https://modelcontextprotocol.io/) — Spec oficial del protocolo
- [SDK MCP source](../sdks/mcp/) — Código fuente del servidor MCP
