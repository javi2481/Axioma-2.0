#!/bin/bash
set -e

# =============================================================================
# Axioma-2.0 — Setup inicial para Digital Ocean Droplet (Ubuntu 22.04+)
#
# Uso:
#   bash scripts/setup-droplet.sh
#
# Qué hace:
#   1. Instala Docker y Docker Compose
#   2. Clona el repositorio
#   3. Genera los certificados SSL para OpenSearch
#   4. Crea el .env desde .env.example
#   5. Levanta todos los servicios
# =============================================================================

REPO_URL="https://github.com/javi2481/Axioma-2.0.git"
APP_DIR="/opt/axioma"

echo "==> Actualizando paquetes..."
apt-get update -y

echo "==> Instalando dependencias..."
apt-get install -y ca-certificates curl gnupg lsb-release git

# --- Docker ---
if ! command -v docker &> /dev/null; then
    echo "==> Instalando Docker..."
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
      https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    systemctl enable docker
    systemctl start docker
    echo "==> Docker instalado: $(docker --version)"
else
    echo "==> Docker ya instalado: $(docker --version)"
fi

# --- vm.max_map_count para OpenSearch ---
echo "==> Configurando vm.max_map_count para OpenSearch..."
sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" >> /etc/sysctl.conf

# --- Clonar repositorio ---
if [ -d "$APP_DIR" ]; then
    echo "==> Actualizando repositorio existente en $APP_DIR..."
    git -C "$APP_DIR" pull origin main
else
    echo "==> Clonando repositorio en $APP_DIR..."
    git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"

# --- Certificados SSL ---
if [ ! -f "keys/root-ca.pem" ]; then
    echo "==> Generando certificados SSL para OpenSearch..."
    MSYS_NO_PATHCONV=1 bash generate-certs.sh
else
    echo "==> Certificados SSL ya existen, saltando..."
fi

# --- Archivo .env ---
if [ ! -f ".env" ]; then
    echo "==> Creando .env desde .env.example..."
    cp .env.example .env
    echo ""
    echo "  IMPORTANTE: Editá el archivo .env antes de continuar."
    echo "  Como mínimo configurá:"
    echo "    - OPENSEARCH_PASSWORD"
    echo "    - OPENSEARCH_INITIAL_ADMIN_PASSWORD"
    echo "    - ENCRYPTION_KEY"
    echo "    - NEXTAUTH_SECRET"
    echo "    - Credenciales del proveedor LLM (OpenAI, Anthropic, etc.)"
    echo ""
    read -p "  ¿Ya editaste el .env? Presioná Enter para continuar o Ctrl+C para salir y editarlo primero..."
else
    echo "==> .env ya existe, saltando..."
fi

# --- Levantar servicios ---
echo "==> Levantando servicios con Docker Compose..."
docker compose up -d --build

echo ""
echo "==> Deploy completado."
echo ""
echo "  Servicios disponibles:"
echo "    Frontend:             http://$(curl -s ifconfig.me):3000"
echo "    Backend API:          http://$(curl -s ifconfig.me):8000"
echo "    Langflow:             http://$(curl -s ifconfig.me):7860"
echo "    OpenSearch Dashboards: http://$(curl -s ifconfig.me):5601"
echo ""
echo "  Para ver logs:   docker compose logs -f"
echo "  Para detener:    docker compose down"
