#!/bin/bash
PROJ_DIR="/opt/jg-projetos/pdv-saas-template"
LOG_FILE="/var/log/pdv_template_streamlit.log"
echo "🛍️ Iniciando PDV SaaS Template..."
[ ! -d "$PROJ_DIR/venv" ] && echo "❌ venv não encontrado." && exit 1
pkill -f "pdv-saas-template.*dashboard.py" 2>/dev/null && sleep 2 || true
cd "$PROJ_DIR"
source venv/bin/activate
[ -f .env ] && export $(grep -v '^#' .env | xargs) 2>/dev/null || true
nohup streamlit run dashboard.py \
    --server.port 8510 \
    --server.address 127.0.0.1 \
    --server.headless true \
    > "$LOG_FILE" 2>&1 &
sleep 3
pgrep -f "pdv-saas-template.*dashboard.py" > /dev/null \
    && echo "✅ PDV Template iniciado! PID: $(pgrep -f 'pdv-saas-template.*dashboard.py')" \
    || echo "❌ Falha. Verifique: $LOG_FILE"
