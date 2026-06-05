#!/bin/bash

# Loja Manu PDV — Script de Inicialização
# Porta fixa: 8506

PROJ_DIR="/opt/jg-projetos/loja-manu"
LOG_FILE="/var/log/lojamanu_streamlit.log"

echo "🛍️  Iniciando Loja Manu PDV..."

if [ ! -d "$PROJ_DIR/venv" ]; then
    echo "❌ Ambiente virtual não encontrado."
    exit 1
fi

# Parar instância anterior se existir
pkill -f "loja-manu.*dashboard.py" 2>/dev/null && sleep 2 || true

cd "$PROJ_DIR"
source venv/bin/activate
[ -f .env ] && export $(grep -v '^#' .env | xargs) 2>/dev/null || true

nohup streamlit run dashboard.py \
    --server.port 8506 \
    --server.address 127.0.0.1 \
    --server.headless true \
    > "$LOG_FILE" 2>&1 &

sleep 3
pgrep -f "loja-manu.*dashboard.py" > /dev/null \
    && echo "✅ Loja Manu PDV iniciada! PID: $(pgrep -f 'loja-manu.*dashboard.py')" \
    || echo "❌ Falha ao iniciar. Verifique: $LOG_FILE"

echo ""
echo "📍 Disponível em: https://lojamanu.jardelguimaraes.com.br"

# ─── Webhook servidor para produtos (N8N) ───────────────────────
killall python3 2>/dev/null || true
sleep 1
nohup /opt/jg-projetos/loja-manu/venv/bin/python3 \
  /opt/jg-projetos/loja-manu/webhook_server.py \
  >> /opt/jg-projetos/loja-manu/webhook.log 2>&1 &
WEBHOOK_PID=$!
sleep 1
[ -n "$WEBHOOK_PID" ] && echo "✅ Webhook server iniciado (PID: $WEBHOOK_PID, porta 5055)" || echo "❌ Erro ao iniciar webhook"
