# 🛍️ PDV SaaS Template NASA — JGAutomações.AI

Template base white-label para PDVs de moda/varejo.
Toda melhoria é validada aqui primeiro, depois propagada para os clientes ativos.

## ⚡ Deploy novo cliente (5 passos)
1. Copie a pasta do template para `/opt/jg-projetos/loja-CLIENTE/`
2. Edite `config.py` com dados do cliente (nome, cores, banco, logo)
3. Substitua `logo.png` pela logo do cliente
4. Crie o banco PostgreSQL: `createdb nome_db`
5. Execute: `bash start.sh`

## 🔑 Credenciais padrão (alterar no primeiro acesso)
| Perfil    | Usuário | Senha      |
|-----------|---------|------------|
| Gerente   | admin   | admin      |
| Caixa     | admin   | vendas     |
| Master    | master  | jardel2026 |

## 🎨 Customização por cliente
Edite apenas o `config.py` — nunca o `dashboard.py` para visual.

## ✨ Funcionalidades
| Módulo | Descrição |
|--------|-----------|
| 🛍️ Vendas | PDV completo com cupom, parcelamento e crediário |
| 💳 Recebimentos | Duplicatas com juros automáticos 0,1%/dia |
| 📋 Condicional | Consignação com controle de devoluções |
| 📦 Estoque | Variações cor/tamanho, histórico e alertas |
| 👥 Clientes | CRM com RFM, histórico e mala direta |
| 📊 Relatórios | Vendas, recebimentos e comissões em PDF |
| 📱 WhatsApp | Cobrança e comprovantes automáticos |
| 🏦 Financeiro | Contas a pagar/receber e fluxo de caixa |

## 🏪 Clientes ativos JGAutomações.AI
| Loja            | URL                                    | Porta |
|-----------------|----------------------------------------|-------|
| GM Homem Itaúna | lojagmh.jardelguimaraes.com.br        | 8510  |
| Loja Manu       | lojamanu.jardelguimaraes.com.br       | 8506  |
| Loja Lume       | lume.jardelguimaraes.com.br           | 8505  |

## 📋 Fluxo de melhorias
Template → valida → propaga clientes ativos com 1 comando

## 🚀 Instalação (ambiente novo)
```bash
git clone https://github.com/jardelguimaraes/pdv-saas-template.git
cd pdv-saas-template
cp config.py.exemplo config.py
# Edite config.py com os dados do cliente
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
bash start.sh
```

---
JGAutomações.AI · Itaúna/MG · Nível NASA 🚀
