#!/bin/bash
# ╔══════════════════════════════════════════════════════════════╗
# ║     JGAutomações.AI — Deploy PDV SaaS Template NASA        ║
# ║     Novo cliente em ~5 minutos                             ║
# ╚══════════════════════════════════════════════════════════════╝
set -e
VERDE="\033[0;32m"; AMARELO="\033[1;33m"; VERMELHO="\033[0;31m"; AZUL="\033[0;34m"; RESET="\033[0m"; NEGRITO="\033[1m"
echo ""
echo -e "${AZUL}${NEGRITO}╔══════════════════════════════════════════════════╗${RESET}"
echo -e "${AZUL}${NEGRITO}║   🛍️  PDV SaaS Deploy — JGAutomações.AI NASA   ║${RESET}"
echo -e "${AZUL}${NEGRITO}╚══════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${AMARELO}📋 Dados do novo cliente:${RESET}"
read -p "  Nome da loja (ex: Boutique Sofia): " LOJA_NOME
read -p "  Apelido/slug (ex: sofia): " LOJA_APELIDO
read -p "  Subtítulo (ex: Moda Feminina): " LOJA_SUBTITULO
read -p "  Ícone emoji (padrão 🛍️): " PAGE_ICON; PAGE_ICON=${PAGE_ICON:-"🛍️"}
read -p "  Arquivo de logo (ex: logo-sofia.png): " LOGO_FILE
read -p "  Nome no cupom (ex: BOUTIQUE SOFIA): " LOGO_CUPOM_NOME
echo ""
echo -e "${AMARELO}🎨 Paleta de cores (hex, ex: #8B5CF6):${RESET}"
read -p "  Cor principal (navbar/bordas): " COR_PRINCIPAL; COR_PRINCIPAL=${COR_PRINCIPAL:-"#1A2035"}
read -p "  Cor principal clara (hover): " COR_PRINCIPAL_LT; COR_PRINCIPAL_LT=${COR_PRINCIPAL_LT:-"#2A3558"}
read -p "  Cor principal fundo: " COR_PRINCIPAL_BG; COR_PRINCIPAL_BG=${COR_PRINCIPAL_BG:-"#F0EAD6"}
read -p "  Cor destaque (botões/métricas): " COR_DESTAQUE; COR_DESTAQUE=${COR_DESTAQUE:-"#C9A84C"}
read -p "  Cor destaque clara: " COR_DESTAQUE_LT; COR_DESTAQUE_LT=${COR_DESTAQUE_LT:-"#E8C97A"}
read -p "  Cor destaque fundo: " COR_DESTAQUE_BG; COR_DESTAQUE_BG=${COR_DESTAQUE_BG:-"#F8F4E8"}
echo ""
echo -e "${AMARELO}🗄️  Banco e aplicação:${RESET}"
read -p "  Nome do banco (ex: sofia_db): " DB_NAME
read -p "  Porta da aplicação (ex: 8511): " APP_PORT
read -p "  WhatsApp da loja (ex: 5537999999999): " WHATSAPP_LOJA; WHATSAPP_LOJA=${WHATSAPP_LOJA:-"5537999999999"}
APP_DIR="/opt/jg-projetos/loja-${LOJA_APELIDO}"
TEMPLATE_DIR="/opt/jg-projetos/pdv-saas-template"
echo ""
echo -e "${AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "  Loja: ${VERDE}${LOJA_NOME}${RESET} | Pasta: ${VERDE}${APP_DIR}${RESET}"
echo -e "  Banco: ${VERDE}${DB_NAME}${RESET} | Porta: ${VERDE}${APP_PORT}${RESET}"
echo -e "${AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
read -p "  Confirmar deploy? (s/N): " CONFIRMA
[[ "$CONFIRMA" != "s" && "$CONFIRMA" != "S" ]] && echo -e "${VERMELHO}  Cancelado.${RESET}" && exit 0
echo ""
echo -e "  ${AMARELO}[1/7]${RESET} Criando pastas..."
mkdir -p "${APP_DIR}/backups" "${APP_DIR}/fotos_produtos" "${APP_DIR}/static"
echo -e "       ${VERDE}✅ OK${RESET}"
echo -e "  ${AMARELO}[2/7]${RESET} Copiando template..."
cp "${TEMPLATE_DIR}/dashboard.py"     "${APP_DIR}/dashboard.py"
cp "${TEMPLATE_DIR}/db_connection.py" "${APP_DIR}/db_connection.py"
cp "${TEMPLATE_DIR}/requirements.txt" "${APP_DIR}/requirements.txt"
echo -e "       ${VERDE}✅ $(wc -l < ${APP_DIR}/dashboard.py) linhas copiadas${RESET}"
echo -e "  ${AMARELO}[3/7]${RESET} Gerando config.py..."
read -s -p "  Senha do banco PostgreSQL (jgadmin): " DB_PASSWORD; echo ""
cat > "${APP_DIR}/config.py" << CONFIGEOF
# JGAutomações.AI — PDV Config — ${LOJA_NOME} — $(date '+%d/%m/%Y %H:%M')
LOJA_NOME        = "${LOJA_NOME}"
LOJA_APELIDO     = "${LOJA_APELIDO}"
LOJA_SUBTITULO   = "${LOJA_SUBTITULO}"
PAGE_TITLE       = "PDV — ${LOJA_NOME}"
PAGE_ICON        = "${PAGE_ICON}"
LOGO_FILE        = "${LOGO_FILE}"
LOGO_CUPOM_NOME  = "${LOGO_CUPOM_NOME}"
COR_PRINCIPAL    = "${COR_PRINCIPAL}"
COR_PRINCIPAL_LT = "${COR_PRINCIPAL_LT}"
COR_PRINCIPAL_BG = "${COR_PRINCIPAL_BG}"
COR_DESTAQUE     = "${COR_DESTAQUE}"
COR_DESTAQUE_LT  = "${COR_DESTAQUE_LT}"
COR_DESTAQUE_BG  = "${COR_DESTAQUE_BG}"
COR_TEXTO_DARK   = "#0D1117"
DB_NAME          = "${DB_NAME}"
DB_USER          = "jgadmin"
DB_PASSWORD      = "${DB_PASSWORD}"
DB_HOST          = "127.0.0.1"
DB_PORT          = 5432
APP_PORT         = ${APP_PORT}
APP_DIR          = "${APP_DIR}"
WHATSAPP_LOJA    = "${WHATSAPP_LOJA}"
USUARIO_GERENTE  = "admin"
SENHA_GERENTE    = "admin"
USUARIO_CAIXA    = "admin"
SENHA_CAIXA      = "vendas"
USUARIO_MASTER   = "master"
SENHA_MASTER     = "jardel2026"
CONFIGEOF
echo -e "       ${VERDE}✅ config.py gerado${RESET}"
echo -e "  ${AMARELO}[4/7]${RESET} Criando start.sh..."
cat > "${APP_DIR}/start.sh" << STARTEOF
#!/bin/bash
source ${APP_DIR}/venv/bin/activate
echo "🛍️ Iniciando ${LOJA_NOME} PDV..."
nohup streamlit run ${APP_DIR}/dashboard.py \\
  --server.port ${APP_PORT} \\
  --server.address 127.0.0.1 \\
  --server.headless true \\
  >> ${APP_DIR}/streamlit.log 2>&1 &
echo "✅ ${LOJA_NOME} PDV iniciado! PID: \$!"
STARTEOF
chmod +x "${APP_DIR}/start.sh"
echo -e "       ${VERDE}✅ start.sh criado (porta ${APP_PORT})${RESET}"
echo -e "  ${AMARELO}[5/7]${RESET} Criando banco ${DB_NAME}..."
psql -U postgres -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw "${DB_NAME}" \
  && echo -e "       ${AMARELO}⚠️  Banco já existe — pulando${RESET}" \
  || (createdb -U postgres "${DB_NAME}" 2>/dev/null && psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO jgadmin;" 2>/dev/null && echo -e "       ${VERDE}✅ Banco criado${RESET}" || echo -e "       ${AMARELO}⚠️  Criar banco manualmente: createdb ${DB_NAME}${RESET}")
echo -e "  ${AMARELO}[6/7]${RESET} Configurando venv Python..."
[ ! -d "${APP_DIR}/venv" ] \
  && python3 -m venv "${APP_DIR}/venv" \
  && "${APP_DIR}/venv/bin/pip" install -q -r "${APP_DIR}/requirements.txt" \
  && echo -e "       ${VERDE}✅ Venv criado${RESET}" \
  || echo -e "       ${AMARELO}⚠️  Venv já existe — pulando${RESET}"
echo -e "  ${AMARELO}[7/7]${RESET} Validando e iniciando..."
python3 -c "import ast; ast.parse(open('${APP_DIR}/dashboard.py').read()); print('Sintaxe OK')"
bash "${APP_DIR}/start.sh"
echo ""
echo -e "${VERDE}${NEGRITO}╔══════════════════════════════════════════════════╗${RESET}"
echo -e "${VERDE}${NEGRITO}║        ✅  Deploy concluído com sucesso!        ║${RESET}"
echo -e "${VERDE}${NEGRITO}╚══════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "  🏪 ${NEGRITO}${LOJA_NOME}${RESET} — porta ${APP_PORT}"
echo -e "  ${AMARELO}Próximos passos:${RESET}"
echo -e "  1. Adicione ${LOGO_FILE} em ${APP_DIR}/"
echo -e "  2. Configure Cloudflare Tunnel para porta ${APP_PORT}"
echo -e "  3. Rode o schema.sql no banco ${DB_NAME}"
echo -e "  4. Primeiro acesso: master / jardel2026"
echo -e ""
echo -e "  ${AZUL}Pra cima sempre 🚀 · Nível NASA${RESET}"
