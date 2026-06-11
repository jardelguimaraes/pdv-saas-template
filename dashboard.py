# ═══════════════════════════════════════════════════
# GM HOMEM PDV — JGAutomações.AI
# Versão: 1.0.0
# Data: 26/04/2026
# Changelog:
#   v2.0.0 — Recebimentos NASA + GM Homem AI com SQLAlchemy
#            Múltiplos clientes, botões de ação, KPIs
#   v1.0.0 — Lançamento oficial (5912 linhas)
# ═══════════════════════════════════════════════════
__version__ = "1.0.0-gmh"

# ═══════════════════════════════════════════════════
# GM HOMEM PDV — JGAutomações.AI
# Versão: 1.0.0
# Data: 26/04/2026
# Changelog:
#   v2.0.0 — Recebimentos NASA + GM Homem AI com SQLAlchemy
#            Múltiplos clientes, botões de ação, KPIs
#   v1.0.0 — Lançamento oficial (5912 linhas)
# ═══════════════════════════════════════════════════
__version__ = "1.0.0-gmh"

import re
import base64
import hashlib
import calendar
import math
import urllib.parse
from datetime import date, datetime, timedelta
import requests
import streamlit as st
import streamlit.components.v1 as components
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os
from db_connection import (
    get_conn as _db_get_conn,
    run_query as _db_run_query,
    run_command as _db_run_command,
    testar_conexao as _db_testar_conexao,
)

try:
    import anthropic as _anthropic_lib
    _ANTHROPIC_OK = True
except ImportError:
    _ANTHROPIC_OK = False

try:
    import plotly.graph_objects as _go
    _PLOTLY_OK = True
except ImportError:
    _PLOTLY_OK = False

load_dotenv()

st.set_page_config(
    page_title="GM Homem Itaúna",
    page_icon="🛍️",
    layout="wide",
)
# ── Paleta e CSS global ───────────────────────────────────────────────────────
# Paleta GM Homem: Rosa Antigo + Dourado
#   Rosa principal:  #1A2035   Rosa claro: #2A3558   Rosa fundo: #F0EAD6
#   Dourado:         #C9A84C   Dourado claro: #E8C97A  Dourado fundo: #F8F4E8
#   Texto escuro:    #0D1117
st.markdown("""
<style>
/* ── Variáveis de marca GM Homem ─────────────────── */
:root {
  --gm-azul:       #1A2035;   /* Rosa Antigo — principal */
  --gm-azul-lt:    #2A3558;   /* Rosa claro — hover */
  --gm-azul-bg:    #F0EAD6;   /* Rosa pálido — fundo */
  --gm-ouro:       #C9A84C;   /* Dourado — destaque */
  --gm-ouro-lt:    #E8C97A;   /* Dourado claro */
  --gm-ouro-bg:    #F8F4E8;   /* Dourado pálido — fundo */
  --gm-text-dark:  #0D1117;   /* Texto principal */
  /* Aliases legados (não mudar — usados em cards PDV) */
  --gm-navy:      #1A2035;
  --gm-navy-lt:   #2A3558;
  --gm-navy-bg:   #F0EAD6;
  --lm-verde:      #C9A84C;
  --lm-verde-lt:   #E8C97A;
  --lm-verde-bg:   #F8F4E8;
  /* PDV cards */
  --pdv-card-bg:   #F8F6F0;
  --pdv-card-h4:   #0D1117;
  --pdv-label:     #1A2035;
  --pdv-summary:   #fdf0f3;
  --pdv-hr:        #f0cfd6;
  --chat-card-bg:  #fafafa;
  --chat-card-bdr: #e8d0d5;
  --cart-row-alt:  #fef6f8;
  --cart-row-hdr:  #fce8ec;
}

/* ── Modo escuro ──────────────────────────────────── */
@media (prefers-color-scheme: dark) {
  :root {
    --pdv-card-bg:   #2a1520;
    --pdv-card-h4:   #f5e6ea;
    --pdv-label:     #2A3558;
    --pdv-summary:   #351a24;
    --pdv-hr:        #5a2e3a;
    --chat-card-bg:  #1e0f14;
    --chat-card-bdr: #4a2030;
    --cart-row-alt:  #2d1620;
    --cart-row-hdr:  #3a1c28;
  }
}

/* ── Cards PDV ────────────────────────────────────── */
.pdv-card {
  background: var(--pdv-card-bg);
  border: 1.5px solid var(--gm-azul);
  border-radius: 14px;
  padding: 22px 24px 16px;
}
.pdv-card h4 { color: var(--pdv-card-h4); margin: 0 0 16px; }
.pdv-label {
  font-size: .8rem; font-weight: 700;
  color: var(--gm-azul); letter-spacing: .08em;
}
.chat-card {
  background: var(--chat-card-bg);
  border: 1.5px solid var(--chat-card-bdr);
  border-radius: 14px;
  padding: 18px 20px 10px;
  min-height: 540px;
}
.chat-card h4 { color: var(--pdv-card-h4); margin: 0 0 8px; }

/* ── Carrinho ─────────────────────────────────────── */
.cart-row {
  display: flex; align-items: center;
  padding: 5px 10px; border-radius: 7px;
  font-size: .9rem;
  border-bottom: 1px solid var(--pdv-hr);
}
.cart-row:nth-child(even) { background: var(--cart-row-alt); }
.cart-header {
  display: flex; align-items: center;
  padding: 4px 10px 6px;
  background: var(--cart-row-hdr);
  border-radius: 7px 7px 0 0;
  font-size: .78rem; font-weight: 700; color: var(--gm-azul);
  letter-spacing: .06em;
}

/* ── Métricas ─────────────────────────────────────── */
[data-testid="stMetricValue"] {
  color: var(--gm-azul) !important;
  font-weight: 700 !important;
}
[data-testid="stMetricLabel"] { color: var(--gm-ouro) !important; }

/* ── Barra de progresso — dourado ─────────────────── */
[data-testid="stProgress"] > div > div {
  background: var(--gm-ouro) !important;
}

/* ── Sidebar menu radio ───────────────────────────── */
[data-testid="stSidebar"] [data-testid="stRadio"] label {
  border-radius: 8px;
  padding: 2px 6px;
  transition: background 0.15s;
}

/* ── Dataframe headers ────────────────────────────── */
[data-testid="stDataFrame"] th,
[data-testid="stDataFrame"] [role="columnheader"] {
  text-align: center !important;
}

/* RESET TOTAL DE CONTRASTE */
button, [data-baseweb="tab"], .stButton>button, div[data-testid="stExpander"] p,
button[data-baseweb="tab"] p, button[data-baseweb="tab"] span,
.st-emotion-cache-6qob1r, .st-emotion-cache-16idsys p {
    color: #ffffff !important;
    background-color: #1A2035 !important;
    opacity: 1 !important;
    font-weight: bold !important;
    text-transform: none !important;
}
/* Sidebar e Navegação */
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #ffffff !important;
}
</style>

<script>
(function () {
  "use strict";
  function aplicarCoresMenu() {
    var labels = document.querySelectorAll(
      '[data-testid="stSidebar"] [data-testid="stRadio"] label'
    );
    labels.forEach(function (label) {
      var txt = label.innerText ? label.innerText.trim() : "";
      if (txt === "Gerencial") {
        label.style.cssText +=
          "background:#5C1529!important;color:#fff!important;" +
          "display:block;border-radius:6px;padding:4px 10px;margin-bottom:2px;";
      } else if (txt === "🛒 Vendas") {
        label.style.cssText +=
          "background:#26A69A!important;color:#fff!important;" +
          "display:block;border-radius:6px;padding:4px 10px;margin-bottom:2px;";
      } else if (txt === "👤 Equipe") {
        label.style.cssText +=
          "background:#5B4E6F!important;color:#F5E6FF!important;" +
          "display:block;border-radius:6px;padding:4px 10px;margin-bottom:2px;";
      } else if (txt === "⚡ JG Hub") {
        label.style.cssText +=
          "background:#1A2D20!important;color:#50D4AA!important;" +
          "display:block;border-radius:6px;padding:4px 10px;margin-bottom:2px;" +
          "font-weight:800;letter-spacing:.03em;";
      } else if (txt === "🔴 Inadimplentes") {
        label.style.cssText +=
          "background:#3D0000!important;color:#FFB3B3!important;" +
          "display:block;border-radius:6px;padding:4px 10px;margin-bottom:2px;";
      }
    });
  }
  aplicarCoresMenu();
  var obs = new MutationObserver(aplicarCoresMenu);
  obs.observe(document.body, { childList: true, subtree: true });
})();
</script>
""", unsafe_allow_html=True)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME", "gmh_db"),
    "user": os.getenv("DB_USER", "jgadmin"),
    "password": os.getenv("DB_PASS", os.getenv("DB_PASSWORD", "")),
}

# ── Conexão centralizada via db_connection.py (pool com reconnect automático) ─
# get_connection() mantido para retrocompatibilidade com código legado interno
def get_connection():
    """DEPRECATED: usar get_conn() de db_connection. Mantido para compat."""
    return psycopg2.connect(**DB_CONFIG)


def run_query(sql: str, params=None) -> pd.DataFrame:
    """Executa SELECT via pool com reconnect automático."""
    return _db_run_query(sql, params=params)


def run_command(sql: str, params: tuple = ()) -> bool:
    """Executa INSERT/UPDATE/DELETE via pool com reconnect automático."""
    return _db_run_command(sql, params)


# ── Carregamento de API Keys do banco (config_geral) ─────────────────────────
# Executado uma vez por sessão. Garante que OPENROUTER_API_KEY e GROQ_API_KEY
# fiquem disponíveis via os.getenv() mesmo que não estejam no .env local.

def _init_api_keys_from_db() -> None:
    """Lê chaves de IA da tabela config_geral e injeta em os.environ."""
    if st.session_state.get("_api_keys_loaded"):
        return
    try:
        with _db_get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT chave, valor FROM config_geral "
                    "WHERE chave IN ('OPENROUTER_API_KEY','GROQ_API_KEY','ANTHROPIC_API_KEY') "
                    "AND valor IS NOT NULL AND valor <> ''"
                )
                for chave, valor in cur.fetchall():
                    if valor:
                        os.environ[chave] = valor.strip()
    except Exception:
        pass  # banco ainda não acessível — ignorar silenciosamente
    st.session_state["_api_keys_loaded"] = True


def _forcar_carga_api_keys() -> dict:
    """Leitura direta e forçada das chaves de IA via psycopg2 puro.

    Ignora qualquer cache de sessão. Usa conexão nova e independente.
    Faz mapeamento automático de aliases (ex: GEMINI_API_KEY com valor
    sk-or-v1-* é tratada como OPENROUTER_API_KEY).
    Retorna dict com as chaves canônicas encontradas para exibição de status.
    """
    # Chaves canônicas que o sistema espera em os.environ
    _CANONICAS = ("OPENROUTER_API_KEY", "GROQ_API_KEY", "ANTHROPIC_API_KEY")
    # Aliases salvos no JG Hub que mapeiam para as chaves canônicas
    _ALIAS_MAP = {
        "GEMINI_API_KEY":    "OPENROUTER_API_KEY",   # sk-or-v1-* salvo com nome Gemini
        "OPENROUTER_API_KEY": "OPENROUTER_API_KEY",
        "GROQ_API_KEY":       "GROQ_API_KEY",
        "ANTHROPIC_API_KEY":  "ANTHROPIC_API_KEY",
    }
    _encontradas: dict[str, str] = {}
    try:
        with _db_get_conn() as _conn:
            with _conn.cursor() as _cur:
                _cur.execute(
                    "SELECT chave, valor FROM config_geral "
                    "WHERE chave IN ("
                    "  'OPENROUTER_API_KEY','GROQ_API_KEY','ANTHROPIC_API_KEY','GEMINI_API_KEY'"
                    ") AND valor IS NOT NULL AND TRIM(valor) <> '' "
                    "ORDER BY chave"
                )
                for _chave_db, _valor in _cur.fetchall():
                    _v = (_valor or "").strip()
                    if not _v:
                        continue
                    # Mapeamento por nome de chave do banco
                    _canonico = _ALIAS_MAP.get(_chave_db, _chave_db)
                    # Detecção adicional pelo prefixo do valor (sk-or-v1- → OpenRouter)
                    if _v.startswith("sk-or-v1-") and not os.environ.get("OPENROUTER_API_KEY"):
                        _canonico = "OPENROUTER_API_KEY"
                    elif _v.startswith("gsk_") and not os.environ.get("GROQ_API_KEY"):
                        _canonico = "GROQ_API_KEY"
                    elif _v.startswith("sk-ant-") and not os.environ.get("ANTHROPIC_API_KEY"):
                        _canonico = "ANTHROPIC_API_KEY"
                    if _canonico in _CANONICAS:
                        os.environ[_canonico] = _v
                        _encontradas[_canonico] = _v
    except Exception:
        pass  # falha silenciosa — banco pode estar indisponível
    st.session_state["_api_keys_loaded"] = True
    return _encontradas


_init_api_keys_from_db()


# ── Constantes de caminho ─────────────────────────────────────────────────────

_LOGO_PATH     = "/opt/jg-projetos/loja-gmh/logo-gmh.jpg"
_LOGO_STATIC   = "/opt/jg-projetos/loja-gmh/static/logo-gmh.jpg"
_FOTO_DIR_PROD = "/opt/jg-projetos/loja-gmh/fotos_produtos"

# ── Dialog de detalhes do produto (módulo) ────────────────────────────────────

@st.dialog("Detalhes do Produto", width="large")
def _dlg_produto(row, is_adm: bool) -> None:
    """Modal com foto grande, valor e estoque em destaque."""
    foto_nome = str(row.get("foto_url") or "").strip().lstrip("=").strip()
    foto_exibida = False
    if foto_nome and foto_nome not in ("pendente.jpg", "sem-foto.jpg", ""):
        if foto_nome.startswith("http"):
            st.image(foto_nome, width=360)
            foto_exibida = True
        else:
            _fp = os.path.join(_FOTO_DIR_PROD, foto_nome)
            if os.path.exists(_fp):
                st.image(_fp, width=360)
                foto_exibida = True
    if not foto_exibida:
        st.markdown(
            "<div style='width:100%;height:200px;background:#ececec;border-radius:10px;"
            "display:flex;align-items:center;justify-content:center;font-size:4rem'>"
            "📦</div>",
            unsafe_allow_html=True,
        )

    st.markdown(f"### {row['nome']}")

    _col_v, _col_e = st.columns(2)
    with _col_v:
        venda = row["preco_venda"]
        _v_txt = f"R$ {float(venda):,.2f}" if pd.notna(venda) else "—"
        st.markdown(
            f"<div style='font-size:1.85rem;font-weight:800;color:#022c3a;"
            f"background:#e8f8fa;border-radius:8px;padding:10px 16px;"
            f"border-left:5px solid #5bc5d3'>💰 {_v_txt}</div>",
            unsafe_allow_html=True,
        )
    with _col_e:
        est     = row["estoque_atual"]
        est_min = row.get("estoque_minimo")
        est_label = f"{int(est)} un." if pd.notna(est) else "—"
        critico   = (is_adm and pd.notna(est_min) and pd.notna(est)
                     and int(est) < int(est_min))
        _e_cor, _e_bg, _e_bd = (
            ("#8b0000", "#ffd6d6", "#e57373") if critico
            else ("#022c3a", "#e8f8fa", "#5bc5d3")
        )
        st.markdown(
            f"<div style='font-size:1.45rem;font-weight:700;color:{_e_cor};"
            f"background:{_e_bg};border-radius:8px;padding:10px 16px;"
            f"border-left:5px solid {_e_bd}'>"
            f"📦 Estoque: {est_label}{'  ⚠️' if critico else ''}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    _ic1, _ic2 = st.columns(2)
    with _ic1:
        _cod_dlg = str(row.get("id") or "")[:8].upper()
        if _cod_dlg:
            st.markdown(f"**Cód.:** `{_cod_dlg}`")
        st.markdown(f"**Categoria:** {row['categoria'] or '—'}")
        ref = str(row.get("codigo_barras") or "").strip()
        if ref:
            st.markdown(f"**Referência:** `{ref}`")
        _dl_raw = row.get("data_lancamento")
        if _dl_raw is not None and pd.notna(_dl_raw):
            st.markdown(f"**Lançamento:** {_fmt_data(_dl_raw)}")
        if is_adm:
            st.markdown(f"**Fornecedor:** {row.get('fornecedor_ref') or '—'}")
            ultima = row.get("ultima_entrada")
            if ultima and pd.notna(ultima):
                st.markdown(f"**Última entrada:** {_fmt_data(ultima)}")
            else:
                st.markdown("**Última entrada:** —")
    with _ic2:
        if is_adm:
            custo = row.get("preco_custo")
            if pd.notna(custo):
                st.markdown(f"**Custo:** R$ {float(custo):,.2f}")
                if pd.notna(venda) and float(custo) > 0:
                    margem = ((float(venda) - float(custo)) / float(custo)) * 100
                    st.markdown(f"**Margem:** {margem:.1f}%")
        if is_adm and pd.notna(est_min):
            st.markdown(f"**Estoque mínimo:** {int(est_min)} un.")
    _desc = str(row.get("descricao_detalhada") or "").strip()
    if _desc:
        st.markdown("**Descrição:**")
        st.write(_desc)

    if is_adm:
        st.markdown("---")
        st.markdown("**Histórico de Entradas:**")
        produto_id = row.get("id")
        if produto_id:
            hist_df = run_query("""
            SELECT created_at, quantidade, preco_custo, preco_venda, origem, observacao
            FROM estoque_historico
            WHERE produto_id = %s
            ORDER BY created_at DESC
            LIMIT 10
            """, (produto_id,))
            if not hist_df.empty:
                for _, h_row in hist_df.iterrows():
                    h_data = _fmt_data(h_row.get('created_at')) if h_row.get('created_at') else "—"
                    h_qtd = int(h_row.get('quantidade') or 0)
                    h_custo = float(h_row.get('preco_custo') or 0)
                    h_venda = float(h_row.get('preco_venda') or 0)
                    h_orig = str(h_row.get('origem') or "—")
                    st.caption(f"📅 {h_data} | {h_qtd} un. | Custo: R$ {h_custo:,.2f} | Venda: R$ {h_venda:,.2f} | {h_orig}")
            else:
                st.caption("Sem histórico de entradas.")

    st.markdown("")
    if st.button("Fechar", key="btn_dlg_fechar", use_container_width=True):
        st.session_state.est_dlg_row = None
        st.session_state.est_dlg_reset += 1
        st.rerun()


# ── Dialog: Cadastro Rápido de Cliente (PDV) ─────────────────────────────────

def _dlg_buscar_cpf_callback() -> None:
    """on_change: busca cliente por CPF digitado e pré-preenche campos do dialog."""
    cpf_nums = re.sub(r"\D", "", st.session_state.get("dlg_nc_cpf", ""))
    if len(cpf_nums) == 11:
        _df_found = run_query(
            f"SELECT nome, whatsapp FROM clientes "
            f"WHERE REPLACE(REPLACE(REPLACE(cpf,'.',''),'-',''),' ','') = '{cpf_nums}' LIMIT 1"
        )
        if not _df_found.empty:
            st.session_state["dlg_nc_nome"] = str(_df_found["nome"].iloc[0] or "")
            _cel_raw = str(_df_found["whatsapp"].iloc[0] or "")
            st.session_state["dlg_nc_cel"] = formatar_celular(_cel_raw)
            st.session_state["_dlg_cpf_status"] = "found"
        else:
            st.session_state.pop("_dlg_cpf_status", None)
    else:
        st.session_state.pop("_dlg_cpf_status", None)


def _dlg_cel_mask_callback() -> None:
    """on_change: formata o celular em tempo real no dialog."""
    raw = st.session_state.get("dlg_nc_cel", "")
    nums = re.sub(r"\D", "", raw)
    if len(nums) >= 10:
        st.session_state["dlg_nc_cel"] = formatar_celular(nums)


@st.dialog("🪪 Cartão de Visita", width="large")
def _dialog_ver_cartao(nome, foto_bytes, foto_nome):
    st.markdown(f"### {nome}")
    if foto_bytes:
        import base64
        img_b64 = base64.b64encode(foto_bytes).decode()
        ext = (foto_nome or "foto.jpg").split(".")[-1].lower()
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
        st.markdown(
            f'<img src="data:{mime};base64,{img_b64}" '
            f'style="width:100%;border-radius:8px;max-height:600px;object-fit:contain">',
            unsafe_allow_html=True,
        )
    else:
        st.info("Nenhuma foto de cartão cadastrada.")


@st.dialog("➕ Cadastro Rápido de Fornecedor")
def _dialog_novo_fornecedor_rapido():
    st.caption("Cadastro rápido — complete os dados depois em 🏭 Fornecedores")
    _rn = st.text_input("Nome *", placeholder="Ex: Inovar Modas")
    _rw = st.text_input("📱 WhatsApp", placeholder="11 99999-9999")
    _rc1, _rc2 = st.columns(2)
    if _rc1.button("✅ Salvar", use_container_width=True):
        if not _rn.strip():
            st.error("Nome obrigatório.")
        else:
            run_command(
                "INSERT INTO fornecedores (nome, tipo, whatsapp1) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (_rn.strip(), "Fornecedor", _rw.strip() or None)
            )
            st.success(f"✅ {_rn.strip()} salvo!")
            st.rerun()
    if _rc2.button("❌ Cancelar", use_container_width=True):
        st.rerun()

@st.dialog("➕ Cadastro Rápido de Cliente")
def _dlg_cadastro_rapido() -> None:
    """Cadastra Nome, CPF e Celular no banco sem sair do PDV."""
    st.caption("Nome e Celular são obrigatórios. CPF é opcional.")

    _nc_cpf  = st.text_input("CPF", key="dlg_nc_cpf",
                              placeholder="000.000.000-00",
                              max_chars=14,
                              help="Somente números ou formato 000.000.000-00. "
                                   "Se já cadastrado, preenche os campos automaticamente.",
                              on_change=_dlg_buscar_cpf_callback)

    if st.session_state.get("_dlg_cpf_status") == "found":
        st.info("✅ Cliente encontrado — campos preenchidos. Salve para confirmar ou edite.")

    _nc_nome = st.text_input("Nome completo *", key="dlg_nc_nome",
                              placeholder="Ex: Maria das Graças Silva")
    _nc_cel  = st.text_input("Celular (DDD + número) *", key="dlg_nc_cel",
                              placeholder="(37) 99999-0000",
                              max_chars=15,
                              help="Digite apenas os números — formatação automática.",
                              on_change=_dlg_cel_mask_callback)
    _nc_obs  = st.text_input("Observação", key="dlg_nc_obs",
                              placeholder="Ex: filha da Joana, amiga da Ana...",
                              max_chars=200)

    # ── Validações inline ─────────────────────────────────────────────────
    _nc_cpf_nums  = re.sub(r"\D", "", _nc_cpf)
    _nc_cel_nums  = re.sub(r"\D", "", _nc_cel)
    _cpf_valido   = validar_cpf(_nc_cpf_nums) if _nc_cpf_nums else None
    _cel_valido   = len(_nc_cel_nums) in (10, 11) if _nc_cel_nums else None

    if _nc_cpf_nums and _cpf_valido is False:
        st.error("CPF inválido — verifique os dígitos.")
    if _nc_cel_nums and _cel_valido is False:
        st.error("Celular deve ter 10 ou 11 dígitos (com DDD).")
    if _nc_cpf_nums and _cpf_valido:
        st.success(f"CPF válido: {formatar_cpf(_nc_cpf_nums)}")
    if _nc_cel_nums and _cel_valido:
        st.success(f"Celular: {formatar_celular(_nc_cel_nums)}")

    st.markdown("---")
    if st.button("💾 Salvar Cliente", key="dlg_nc_salvar",
                 use_container_width=True, type="primary"):
        _erros_dlg = []
        if not _nc_nome.strip():
            _erros_dlg.append("Nome é obrigatório.")
        if _nc_cpf_nums and not _cpf_valido:
            _erros_dlg.append("CPF inválido — verifique os dígitos.")
        if not _nc_cel_nums:
            _erros_dlg.append("Celular é obrigatório.")
        elif not _cel_valido:
            _erros_dlg.append("Celular deve ter 10 ou 11 dígitos.")

        if _erros_dlg:
            for _e in _erros_dlg:
                st.error(_e)
        else:
            _cpf_fmt = formatar_cpf(_nc_cpf_nums) if _nc_cpf_nums else None
            _ok = run_command(
                "INSERT INTO clientes (nome, cpf, whatsapp, ativo, observacao) "
                "VALUES (%s, %s, %s, true, %s)",
                (_nc_nome.strip(), _cpf_fmt, _nc_cel_nums, _nc_obs.strip() or None),
            )
            if _ok:
                st.session_state.pop("_dlg_cpf_status", None)
                st.success(
                    f"✅ **{_nc_nome.strip()}** cadastrado com sucesso! "
                    "Feche e recarregue a lista de clientes."
                )
                st.rerun()


# ── Extrato CSV (sistema anterior) ───────────────────────────────────────────

_CSV_EXTRATO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "EXTRATO_UNIFICADO_JG.CSV")


@st.cache_data(ttl=3600)
def _carregar_extrato_csv() -> pd.DataFrame:
    """Carrega EXTRATO_UNIFICADO_JG.CSV (cache 1h). Retorna DataFrame vazio se ausente."""
    if not os.path.exists(_CSV_EXTRATO_PATH):
        return pd.DataFrame()
    try:
        df = pd.read_csv(
            _CSV_EXTRATO_PATH,
            sep=";",
            dtype=str,
            encoding="utf-8",
            on_bad_lines="skip",
        )
        df.columns = df.columns.str.strip()
        if "CLIENTE" in df.columns:
            df["CLIENTE"] = df["CLIENTE"].str.strip()
        return df
    except Exception:
        return pd.DataFrame()


def _parse_valor_br(v: str) -> float:
    """Converte '1.234,56' → 1234.56."""
    try:
        return float(str(v).replace(".", "").replace(",", "."))
    except Exception:
        return 0.0


# ── Logo ─────────────────────────────────────────────────────────────────────


@st.cache_data
def _logo_b64() -> str | None:
    if os.path.exists(_LOGO_PATH):
        with open(_LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


# ── Helpers de renderização de Cupom ─────────────────────────────────────────
#
# _cupom_html_display(text) → str  : HTML para st.markdown (300px, logo no topo)
# _cupom_iframe_html(text, id, ...) → str : HTML para components.html (impressão)
#
# Regras visuais (fixas):
#   • Container 300px, overflow-x:hidden, background branco
#   • Logo 40px à esquerda de "LOJA GM HOMEM ITAÚNA" (substitui marca d'água)
#   • SEM div de watermark (falha na impressão em muitas impressoras)
#   • -webkit-print-color-adjust:exact para a logo aparecer na bobina
# ─────────────────────────────────────────────────────────────────────────────

def _cupom_html_display(text: str) -> str:
    """Retorna o bloco HTML do cupom para exibição na tela (300 px, logo no topo)."""
    logo = _logo_b64()
    text_esc = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    logo_row = ""
    if logo:
        logo_row = (
            "<div style='display:flex;align-items:center;gap:8px;"
            "padding-bottom:6px;margin-bottom:4px;"
            "border-bottom:1px solid #e0e0e0;'>"
            f"<img src='data:image/png;base64,{logo}' "
            "style='height:40px;width:auto;object-fit:contain;"
            "-webkit-print-color-adjust:exact !important;"
            "print-color-adjust:exact !important;' alt='logo'>"
            "<strong style='font-family:\"Courier New\",monospace;"
            "font-size:.88rem;color:#0D1117;'>LOJA GM HOMEM ITAÚNA</strong>"
            "</div>"
        )

    return (
        "<div style='width:300px;margin:0 auto;background:#fff !important;color-scheme:light !important;"
        "border:1px solid #ddd;border-radius:6px;padding:1rem;"
        "overflow-x:hidden;"
        "-webkit-print-color-adjust:exact !important;"
        "print-color-adjust:exact !important;'>"
        f"{logo_row}"
        "<pre style='font-family:\"Courier New\",monospace;font-size:.78rem;"
        f"color:#1a1a1a !important;background:#fff !important;margin:0;white-space:pre;overflow-x:hidden;'>{text_esc}</pre>"
        "</div>"
    )


def _cupom_iframe_html(text: str, frame_id: str,
                        btn_label: str = "🖨️ Imprimir",
                        btn_height: int = 52) -> str:
    """Retorna HTML+JS para components.html() — imprime apenas o cupom via iframe.

    O documento de impressão é pré-montado em Python e codificado em base64
    para evitar problemas de escaping de aspas no JavaScript.
    Logo aparece como <img> no topo da folha impressa.
    """
    logo = _logo_b64()
    text_esc = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    logo_print = ""
    if logo:
        logo_print = (
            f"<div style=\"display:flex;align-items:center;gap:8px;"
            f"margin-bottom:6px;padding-bottom:4px;border-bottom:1px solid #ccc;\">"
            f"<img src=\"data:image/png;base64,{logo}\" "
            f"style=\"height:36px;width:auto;"
            f"-webkit-print-color-adjust:exact !important;"
            f"print-color-adjust:exact !important;\" alt=\"logo\">"
            f"<b style=\"font-family:'Courier New',monospace;font-size:10pt;\">"
            f"LOJA GM HOMEM ITAUNA</b></div>"
        )

    print_doc = (
        "<!DOCTYPE html><html><head><meta charset=\"utf-8\"><style>"
        "body{margin:0;padding:4mm;font-family:'Courier New',monospace;"
        "font-size:10pt;color:#000;background:#fff;}"
        ".wrap{width:72mm;margin:auto;"
        "-webkit-print-color-adjust:exact !important;"
        "print-color-adjust:exact !important;}"
        "img{-webkit-print-color-adjust:exact !important;"
        "print-color-adjust:exact !important;}"
        "pre{margin:0;white-space:pre-wrap;}"
        "</style></head><body>"
        f"<div class=\"wrap\">{logo_print}<pre>{text_esc}</pre></div>"
        "</body></html>"
    )
    b64_doc  = base64.b64encode(print_doc.encode("utf-8")).decode("ascii")
    b64_text = base64.b64encode(text.encode("utf-8")).decode("ascii")
    fn       = f"_imp_{frame_id.replace('-', '_').replace('.', '_')}"

    return (
        f'<iframe id="{frame_id}" style="position:absolute;top:-9999px;'
        f'left:-9999px;width:1px;height:1px;border:none;"></iframe>\n'
        f'<button onclick="{fn}()" style="width:100%;'
        f'background:linear-gradient(135deg,#1A2035,#c27a9b);'
        f'color:#fff;border:none;border-radius:8px;padding:10px 16px;'
        f'font-size:1rem;font-weight:600;cursor:pointer;'
        f'letter-spacing:.4px;box-shadow:0 2px 8px rgba(157,92,109,.4)">'
        f'{btn_label}</button>\n'
        f'<script>\nfunction {fn}(){{\n'
        f'  var htmlDoc=atob("{b64_doc}");\n'
        f'  try{{htmlDoc=decodeURIComponent(escape(htmlDoc));}}catch(e){{}}\n'
        f'  var frm=document.getElementById("{frame_id}");\n'
        f'  var doc=frm.contentDocument||frm.contentWindow.document;\n'
        f'  doc.open();doc.write(htmlDoc);doc.close();\n'
        f'  frm.contentWindow.focus();frm.contentWindow.print();'
        f'setTimeout(function(){{try{{frm.contentWindow.close();}}catch(e){{}}}},1000);\n'
        f'}}\n</script>'
    )


# ── Helpers de Venda Assistida ────────────────────────────────────────────────

def _fmt_data(val) -> str:
    """Formata qualquer valor de data para DD/MM/YYYY (padrão Brasil)."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "—"
    try:
        if isinstance(val, str):
            val = pd.to_datetime(val)
        return pd.Timestamp(val).strftime("%d/%m/%Y")
    except Exception:
        return str(val)


def _add_months(dt: date, meses: int) -> date:
    month = dt.month - 1 + meses
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def parse_venda(texto: str) -> dict:
    """Extrai cliente, descrição, valor, parcelas e forma de pagamento do texto livre."""
    resultado = {}

    # Cliente: "para <Nome>"
    m = re.search(r'\bpara\s+([^,]+)', texto, re.IGNORECASE)
    if m:
        resultado["cliente_nome"] = m.group(1).strip()

    # Valor: "R$ 150", "150 reais", "150,00 reais"
    m = re.search(r'R\$\s*([\d.,]+)|([\d]+(?:[.,]\d+)?)\s*reais', texto, re.IGNORECASE)
    if m:
        valor_str = (m.group(1) or m.group(2)).replace(",", ".")
        resultado["valor_total"] = float(valor_str)

    # Parcelas + forma: "2x no cartão", "3x crédito"
    m_cart = re.search(
        r'(\d+)\s*[xX]\s*(?:no\s+|em\s+)?(cartão|cartao|crédito|credito|débito|debito)',
        texto, re.IGNORECASE,
    )
    if m_cart:
        resultado["parcelas"] = int(m_cart.group(1))
        resultado["forma_pagamento"] = "cartão"
    elif re.search(r'\bpix\b', texto, re.IGNORECASE):
        resultado["parcelas"] = 1
        resultado["forma_pagamento"] = "pix"
    elif re.search(r'\bdinheiro\b|\bespécie\b|\bespecie\b|\bà vista\b|\ba vista\b', texto, re.IGNORECASE):
        resultado["parcelas"] = 1
        resultado["forma_pagamento"] = "dinheiro"
    elif re.search(r'\bcartão\b|\bcartao\b', texto, re.IGNORECASE):
        resultado["parcelas"] = 1
        resultado["forma_pagamento"] = "cartão"
    else:
        resultado["parcelas"] = 1
        resultado["forma_pagamento"] = "não informado"

    # Descrição: partes da frase que não são cliente, valor ou pagamento
    partes = re.split(r',\s*', texto)
    desc_partes = []
    for p in partes[1:]:  # ignora primeiro trecho (contém o nome do cliente)
        if not re.search(
            r'reais|R\$|\d+\s*[xX]|pix|dinheiro|cartão|cartao|crédito|credito|espécie|especie|à vista|a vista',
            p, re.IGNORECASE,
        ):
            desc_partes.append(p.strip())
    resultado["descricao"] = ", ".join(desc_partes) if desc_partes else "Produto não especificado"

    return resultado


def buscar_cliente(nome: str) -> list:
    """Busca clientes ativos pelo nome (ILIKE). Retorna lista de dicts {id, nome}."""
    try:
        with _db_get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, nome FROM clientes WHERE nome ILIKE %s AND ativo = true ORDER BY nome LIMIT 5",
                    (f"%{nome}%",),
                )
                return [{"id": str(r[0]), "nome": r[1]} for r in cur.fetchall()]
    except Exception:
        return []


def salvar_venda(dados: dict, itens: list | None = None) -> str:
    """Insere a venda, seus itens e gera parcelas em contas_receber. Retorna o ID da venda.

    itens: lista de dicts com chaves produto_id, qtd, preco_unit.
    Rastreabilidade: tenta gravar 'vendedor_nome' + 'codigo_vendedor' via SAVEPOINT.
    """
    with _db_get_conn() as conn:
        with conn.cursor() as cur:
                forma        = dados["forma_pagamento"]
                parcelas     = dados["parcelas"]
                vendedor     = dados.get("vendedor_nome", "")
                cod_vendedor = dados.get("codigo_vendedor", "")
                status_pag   = "pago" if forma in ("pix", "dinheiro") else "parcelado"

                # ── INSERT vendas (com fallback se colunas não existem) ───────
                cur.execute("SAVEPOINT sp_vnd")
                try:
                    cur.execute(
                        """
                        INSERT INTO vendas
                            (cliente_id, valor_total, forma_pagamento, status_pagamento,
                             vendedor_nome, codigo_vendedor, observacoes, cupom_texto, parcelas)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                        """,
                        (dados["cliente_id"], dados["valor_total"], forma, status_pag,
                         vendedor, cod_vendedor or None, dados.get("observacao"),
                         dados.get("cupom_text", ""), parcelas),
                    )
                except Exception:
                    cur.execute("ROLLBACK TO SAVEPOINT sp_vnd")
                    cur.execute(
                        """
                        INSERT INTO vendas (cliente_id, valor_total, forma_pagamento, status_pagamento)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                        """,
                        (dados["cliente_id"], dados["valor_total"], forma, status_pag),
                    )
                venda_id = str(cur.fetchone()[0])

                # ── INSERT itens_venda ────────────────────────────────────────
                for it in (itens or []):
                    _cor_it  = it.get("cor") or None
                    _tam_it  = it.get("tamanho") or None
                    _base_nm = it.get("nome", it.get("descricao", ""))
                    _desc_item = _base_nm.strip()
                    _sub_item  = round(float(it["qtd"]) * float(it["preco_unit"]), 2)
                    cur.execute(
                        """
                        INSERT INTO itens_venda
                            (venda_id, produto_id, nome_produto, cor, tamanho,
                             quantidade, preco_unit, preco_unitario, subtotal)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (venda_id, it["produto_id"], _desc_item, _cor_it, _tam_it,
                         it["qtd"], it["preco_unit"], it["preco_unit"], _sub_item),
                    )
                    # Decrementa estoque
                    cur.execute(
                        "UPDATE produtos SET estoque_atual = estoque_atual - %s WHERE id = %s",
                        (it["qtd"], it["produto_id"]),
                    )

                # ── INSERT contas_receber (parcelado/crediário) ───────────────
                if forma in ("cartão", "crediário"):
                    valor_parcela = round(dados["valor_total"] / parcelas, 2)
                    hoje = date.today()
                    from datetime import timedelta
                    for i in range(1, parcelas + 1):
                        # Calcular exatamente 30*N dias (não mês a mês)
                        vencimento = hoje + timedelta(days=30 * i)
                        cur.execute(
                            """
                            INSERT INTO contas_receber (venda_id, valor_parcela, dt_vencimento, status)
                            VALUES (%s, %s, %s, 'aberto')
                            """,
                            (venda_id, valor_parcela, vencimento),
                        )
        return venda_id


# ── Cupom Térmico (80 mm ≈ 42 chars) ─────────────────────────────────────────

def gerar_cupom(dados: dict, venda_id: str, num_cupom: int,
                vendedor: str = "", nome_vendedor: str = "") -> str:
    W   = 42
    SEP = "─" * W
    now = datetime.now()
    dt  = now.strftime("%d/%m/%Y")
    hr  = now.strftime("%H:%M")

    parcelas     = dados.get("parcelas", 1) or 1
    valor_orig   = dados.get("valor_original", dados["valor_total"])
    desconto_pct = dados.get("desconto_pct", 0.0)
    valor        = round(valor_orig * (1.0 - desconto_pct / 100.0), 2)
    desconto_real = round(valor_orig - valor, 2)

    forma_pag = (dados["forma_pagamento"] or "").lower().strip()
    # Normalizar forma de pagamento
    if forma_pag in ('crediário', 'crediario'):
        forma_key = 'crediário'
        forma_display = "CREDIÁRIO"
    elif forma_pag in ('cartão', 'cartao'):
        forma_key = 'cartão'
        forma_display = "CARTÃO"
    elif forma_pag == 'pix':
        forma_key = 'pix'
        forma_display = "PIX"
    else:  # dinheiro ou outro
        forma_key = forma_pag
        forma_display = forma_pag.upper()

    # Construir string de pagamento com parcelas
    if parcelas and parcelas > 1:
        pag_str = f"{forma_display} — {parcelas}x R${valor / parcelas:,.2f}"
    else:
        pag_str = f"{forma_display} — À VISTA"

    _itens_c = dados.get('itens_carrinho', [])
    # Vendedora = nome da config_comissao; Operador = usuario logado
    _nome_vnd = (nome_vendedor or dados.get('nome_vendedor', '')).strip() or '—'
    _operador = (vendedor or dados.get('vendedor_nome', '')).strip() or '—'
    def ctr(s: str) -> str:
        return s.center(W)
    # Buscar nr_documento da primeira parcela
    try:
        _df_nr = run_query(f"SELECT nr_documento FROM contas_receber WHERE venda_id='{venda_id}' ORDER BY nr_documento LIMIT 1")
        _nr_doc = _df_nr.iloc[0]["nr_documento"] if not _df_nr.empty and _df_nr.iloc[0]["nr_documento"] else f"PED-{num_cupom:06d}"
    except: _nr_doc = f"PED-{num_cupom:06d}"
    linhas = [
        SEP,
        ctr('LOJA GM HOMEM ITAÚNA'),
        ctr('Moda Masculina — Itaúna/MG'),
        SEP,
        f"Doc: {_nr_doc}".ljust(W // 2) + f"{dt} {hr}".rjust(W - W // 2),
        f"CLIENTE:    {dados['cliente_nome'][:30]}",
        f"VENDEDORA:  {_nome_vnd[:30]}",
        f"OPERADOR:   {_operador[:30]}",
        SEP,
        f"{'ITEM':<24}{'QTD':>4}{'UNIT':>7}{'TOTAL':>7}",
        SEP,
    ]
    if _itens_c:
        for _it in _itens_c:
            _in = str(_it.get('nome','Produto'))[:20]
            _iq = int(_it.get('qtd',1))
            _iu = float(_it.get('preco_unit',0))
            _is = float(_it.get('subtotal', _iu*_iq))
            linhas.append(f"{_in:<20}{_iq:>4} {f'R${_iu:,.2f}':>7} {f'R${_is:,.2f}':>7}")
    else:
        desc = dados.get('descricao','Produto')[:26]
        linhas.append(f"{desc:<26}{f'R${valor_orig:,.2f}':>16}")

    # Melhoria 3: Só mostrar desconto se > 0%
    if desconto_pct > 0.01:
        linhas += [
            f"{'DESCONTO ' + f'{desconto_pct:.1f}%':<26}{f'-R${desconto_real:,.2f}':>16}",
        ]

    # Adicionar observação se existir
    obs = (dados.get("observacao") or "").strip()
    if obs:
        linhas += [
            SEP,
            f"OBS: {obs[:38]}",
            SEP,
        ]

    linhas += [
        SEP,
        ctr(f"★ TOTAL: R${valor:,.2f} ★"),
        f"PAGAMENTO: {pag_str}",
    ]

    # Adicionar datas de vencimento para crediário parcelado
    if forma_key == 'crediário' and parcelas and parcelas > 1:
        try:
            df_parcelas = run_query(f"""
                SELECT valor_parcela, data_vencimento
                FROM contas_receber
                WHERE venda_id = '{venda_id}'
                ORDER BY data_vencimento ASC
            """)
            if not df_parcelas.empty:
                linhas += [SEP, "PARCELAS:"]
                for idx, (_, row) in enumerate(df_parcelas.iterrows(), 1):
                    val_p = float(row.get('valor_parcela', valor / parcelas))
                    data_v = row.get('data_vencimento')
                    data_fmt = _fmt_data(data_v)
                    linhas.append(f"  {idx}ª  R${val_p:,.2f}  venc. {data_fmt}")
        except Exception:
            pass  # Se não conseguir buscar, continua sem as parcelas

    linhas += [
        SEP,
        ctr("✨ Você merece se sentir incrível!"),
        ctr("Até a próxima 🛍️"),
        SEP,
        ctr("📱 Instagram: @gm.homem"),
        ctr("🌐 By JGAutomações.AI"),
        ctr("Tecnologia de Impacto"),
        SEP,
    ]
    return "\n".join(linhas)


# ── Cupom de Recibo de Pagamento (Balcão) ────────────────────────────────────

def gerar_cupom_pagamento(
    cliente_nome: str,
    operador: str,
    valor_total: float,
    detalhes: list,          # list of (vencimento_str, valor_baixado, tipo)
    nome_vendedor: str = "", # nome de exibição da vendedora
) -> str:
    """Gera recibo de pagamento para impressão.
    tipo: 'pago' (parcela quitada) | 'parcial' (abatimento parcial)
    """
    W   = 42
    SEP = "─" * W
    now = datetime.now()
    dt  = now.strftime("%d/%m/%Y")
    hr  = now.strftime("%H:%M")

    def ctr(s: str) -> str:
        return s.center(W)

    linhas = [
        SEP,
        ctr("LOJA GM HOMEM ITAÚNA"),
        ctr("Recibo de Pagamento"),
        SEP,
        f"Data/Hora:  {dt}  {hr}".ljust(W),
        SEP,
        f"Cliente:    {cliente_nome[:30]}",
        f"Vendedora:  {(nome_vendedor or '—')[:30]}",
        f"Operador:   {(operador or '—')[:30]}",
        SEP,
        "Parcelas baixadas:",
    ]
    for venc, valor, tipo in detalhes:
        sufx = "(parcial)" if tipo == "parcial" else ""
        linha = f"  {venc}  R$ {valor:,.2f}  {sufx}".rstrip()
        linhas.append(linha[:W])
    linhas += [
        SEP,
        f"{'TOTAL RECEBIDO:':>26}{f'R$ {valor_total:,.2f}':>16}",
        SEP,
        ctr("✨ Você merece se sentir incrível"),
        ctr("Até a próxima 🛍️"),
        ctr("By JGAutomações.AI"),
        SEP,
    ]
    return "\n".join(linhas)


# ── Helpers de Clientes ───────────────────────────────────────────────────────

_WEBHOOK_RECADASTRO  = "https://webhook.jardelguimaraes.com.br/webhook/loja-gmh-recadastro"
_WEBHOOK_COBRANCA    = "https://webhook.jardelguimaraes.com.br/webhook/loja-gmh-cobranca"
_WEBHOOK_COMPROVANTE = "https://webhook.jardelguimaraes.com.br/webhook/loja-gmh-comprovante"


def validar_cpf(cpf: str) -> bool:
    """Valida CPF brasileiro pelos dígitos verificadores."""
    nums = re.sub(r"\D", "", cpf or "")
    if len(nums) != 11 or len(set(nums)) == 1:
        return False
    soma = sum(int(nums[i]) * (10 - i) for i in range(9))
    d1 = (soma * 10 % 11) % 10
    if d1 != int(nums[9]):
        return False
    soma = sum(int(nums[i]) * (11 - i) for i in range(10))
    d2 = (soma * 10 % 11) % 10
    return d2 == int(nums[10])


def formatar_cpf(cpf: str) -> str:
    """Retorna CPF no formato XXX.XXX.XXX-XX, ou string vazia se inválido."""
    nums = re.sub(r"\D", "", cpf or "")
    if len(nums) == 11:
        return f"{nums[:3]}.{nums[3:6]}.{nums[6:9]}-{nums[9:]}"
    return nums


def formatar_celular(cel: str) -> str:
    """Formata celular para (DDD) 9XXXX-XXXX (11 dígitos) ou (DDD) XXXX-XXXX (10)."""
    nums = re.sub(r"\D", "", cel or "")
    if len(nums) == 11:
        return f"({nums[:2]}) {nums[2:7]}-{nums[7:]}"
    if len(nums) == 10:
        return f"({nums[:2]}) {nums[2:6]}-{nums[6:]}"
    return cel  # devolve como digitado se não reconhecer


def buscar_cep(cep: str) -> dict:
    """Consulta ViaCEP e retorna dict com logradouro/bairro/localidade, ou {} em falha."""
    digits = re.sub(r"\D", "", cep or "")
    if len(digits) != 8:
        return {}
    try:
        _r = requests.get(
            f"https://viacep.com.br/ws/{digits}/json/",
            timeout=5,
        )
        if _r.ok:
            _d = _r.json()
            if "erro" not in _d:
                return _d
    except Exception:
        pass
    return {}


def enviar_webhook_cobranca(cliente_id: str, whatsapp: str, valor: float) -> tuple:
    """Dispara cobrança via n8n. Retorna (sucesso: bool, detalhe: str)."""
    try:
        resp = requests.post(
            _WEBHOOK_COBRANCA,
            json={"cliente_id": cliente_id, "whatsapp": whatsapp, "valor": valor},
            timeout=10,
        )
        if resp.status_code < 400:
            return True, f"HTTP {resp.status_code}"
        return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
    except requests.exceptions.Timeout:
        return False, "Timeout ao conectar com o n8n."
    except Exception as e:
        return False, str(e)


def enviar_comprovante_wpp(cliente_id: str, whatsapp: str,
                           venda_id: str, cupom_texto: str) -> tuple:
    """Dispara o comprovante de venda via n8n → WhatsApp. Retorna (sucesso, detalhe)."""
    try:
        resp = requests.post(
            _WEBHOOK_COMPROVANTE,
            json={
                "cliente_id":  cliente_id,
                "whatsapp":    whatsapp,
                "venda_id":    venda_id,
                "comprovante": cupom_texto,
            },
            timeout=10,
        )
        if resp.status_code < 400:
            return True, f"HTTP {resp.status_code}"
        return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
    except requests.exceptions.Timeout:
        return False, "Timeout ao conectar com o n8n."
    except Exception as e:
        return False, str(e)


def enviar_webhook_recadastro(cliente_id: str, whatsapp: str) -> tuple:
    """Dispara o webhook do n8n. Retorna (sucesso: bool, detalhe: str)."""
    try:
        resp = requests.post(
            _WEBHOOK_RECADASTRO,
            json={"cliente_id": cliente_id, "whatsapp": whatsapp},
            timeout=10,
        )
        if resp.status_code < 400:
            return True, f"HTTP {resp.status_code}"
        return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
    except requests.exceptions.Timeout:
        return False, "Timeout ao conectar com o n8n."
    except Exception as e:
        return False, str(e)


# ── Motor de Juros ────────────────────────────────────────────────────────────
# Política SGA: 0,1% ao dia = 3% ao mês, sem multa separada
_MULTA_PERCENTUAL  = 0.00   # SGA não cobra multa separada
_JUROS_DIA         = 0.001  # 0,1 % ao dia = ~3 % ao mês

def calcular_juros(valor: float, dias_atraso: int) -> tuple[float, float]:
    """Retorna (juros_valor, valor_total_com_juros).
    dias_atraso deve ser > 0 para que juros sejam aplicados.
    """
    if dias_atraso <= 0:
        return 0.0, float(valor)
    juros = float(valor) * _JUROS_DIA * dias_atraso
    return round(juros, 2), round(float(valor) + juros, 2)


# ── Dialog: Detalhamento de Parcelas (Gestão de Baixas) ──────────────────────
@st.dialog("Detalhamento de Parcelas", width="large")
def _dlg_baixa_cliente(cliente_nome: str, cliente_id_filter: str, role: str, username: str) -> None:
    """Modal que lista parcelas de um cliente com Baixa Individual e Quitação Total."""
    hoje = date.today()

    df_parc = run_query(f"""
        SELECT cr.id::text, cr.valor_parcela, cr.data_vencimento,
               cr.status, cr.data_pagamento, cr.valor_pago_final,
               cr.juros_isento, cr.isento_por,
               v.id::text AS venda_id
        FROM contas_receber cr
        JOIN vendas v ON v.id = cr.venda_id
        JOIN clientes c ON c.id = v.cliente_id
        WHERE c.nome = '{cliente_nome.replace("'", "''")}'
        ORDER BY cr.data_vencimento ASC
    """)

    if df_parc.empty:
        st.info("Nenhuma parcela encontrada para este cliente.")
        return

    abertas = df_parc[df_parc["status"] == "aberto"]
    pagas   = df_parc[df_parc["status"] == "pago"]

    st.markdown(f"#### Cliente: **{cliente_nome}**")
    col_a, col_p = st.columns(2)
    col_a.metric("Parcelas em aberto", len(abertas))
    col_p.metric("Parcelas pagas", len(pagas))
    st.markdown("---")

    if abertas.empty:
        st.success("✅ Todas as parcelas estão quitadas!")
    else:
        # ── Cabeçalho ──────────────────────────────────────────────────────
        h = st.columns([1.2, 1.5, 1.5, 1.8, 1.8, 2.2])
        for col_h, label in zip(h, ["Vencimento", "Valor", "Atraso", "Juros", "Total c/ Juros", "Ação"]):
            col_h.markdown(f"**{label}**")
        st.markdown("<hr style='margin:4px 0 8px'>", unsafe_allow_html=True)

        total_original  = 0.0
        total_com_juros = 0.0
        isentar_todos   = False

        # ── Checkbox isenção global (somente admin) ─────────────────────────
        if role == "admin":
            isentar_todos = st.checkbox(
                "🔓 Isentar juros de TODAS as parcelas (Alçada Gerencial)",
                key="dlg_isentar_todos",
                help="Somente administradores podem isentar juros. A isenção é registrada para auditoria.",
            )

        linhas_baixa = []   # [(id, valor_pago, isento)]

        for _, row in abertas.iterrows():
            dias = (hoje - pd.to_datetime(row["data_vencimento"]).date()).days
            juros_val, total_val = calcular_juros(float(row["valor_parcela"]), dias)
            total_original  += float(row["valor_parcela"])
            total_com_juros += total_val

            c_venc, c_val, c_dias, c_juros, c_total, c_btn = st.columns([1.2, 1.5, 1.5, 1.8, 1.8, 2.2])
            c_venc.write(_fmt_data(row["data_vencimento"]))
            c_val.write(f"R$ {float(row['valor_parcela']):,.2f}")

            if dias > 0:
                c_dias.markdown(f"🔴 **{dias}d**")
                # ── isenção individual (admin) ──────────────────────────────
                if role == "admin" and not isentar_todos:
                    isentar_ind = c_juros.checkbox(
                        "Isentar", key=f"dlg_is_{row['id']}", label_visibility="collapsed"
                    )
                else:
                    isentar_ind = False

                efetivo_isento = isentar_todos or (role == "admin" and isentar_ind)

                if efetivo_isento:
                    c_juros.markdown("~~R$ " + f"{juros_val:,.2f}~~")
                    c_total.write(f"R$ {float(row['valor_parcela']):,.2f}")
                    valor_cobrar = float(row["valor_parcela"])
                else:
                    c_juros.write(f"R$ {juros_val:,.2f}")
                    c_total.write(f"R$ {total_val:,.2f}")
                    valor_cobrar = total_val
            else:
                c_dias.write("—")
                c_juros.write("—")
                c_total.write(f"R$ {float(row['valor_parcela']):,.2f}")
                efetivo_isento = False
                valor_cobrar = float(row["valor_parcela"])

            linhas_baixa.append((row["id"], valor_cobrar, efetivo_isento))

            if c_btn.button("✅ Baixa Individual", key=f"dlg_bi_{row['id']}", use_container_width=True):
                isento_reg = "sim" if efetivo_isento else None
                ok = run_command(
                    """UPDATE contas_receber
                       SET status = 'pago',
                           data_pagamento   = %s,
                           valor_pago_final = %s,
                           juros_isento     = %s,
                           isento_por       = %s
                       WHERE id = %s""",
                    (hoje, valor_cobrar,
                     efetivo_isento,
                     username if efetivo_isento else None,
                     row["id"]),
                )
                if ok:
                    st.success(f"Parcela de {str(row['data_vencimento'])} baixada — R$ {valor_cobrar:,.2f}")
                    st.rerun()

        # ── Rodapé ─────────────────────────────────────────────────────────
        st.markdown("---")
        total_cobrar = sum(v for _, v, _ in linhas_baixa)
        st.markdown(
            f"**Total original:** R$ {total_original:,.2f} &nbsp;|&nbsp; "
            f"**Total a cobrar:** R$ {total_cobrar:,.2f}",
            unsafe_allow_html=True,
        )
        col_ap, col_qt = st.columns(2)

        # ── Abatimento Parcial ─────────────────────────────────────────────
        with col_ap:
            st.markdown("**💳 Abatimento Parcial**")
            st.caption("O valor será abatido das parcelas mais antigas primeiro.")
            valor_abat = st.number_input(
                "Valor a Abater (R$)",
                min_value=0.01,
                max_value=float(total_cobrar) if total_cobrar > 0 else 0.01,
                value=min(10.0, float(total_cobrar)) if total_cobrar > 0 else 0.01,
                step=10.0,
                key="dlg_valor_abatimento",
            )
            if st.button("✅ Aplicar Abatimento", key="dlg_abater", use_container_width=True):
                restante = round(float(valor_abat), 2)
                erros    = 0
                for parc_id, valor_parc, efetivo_isento in linhas_baixa:
                    if restante <= 0:
                        break
                    vp = round(float(valor_parc), 2)
                    if restante >= vp:
                        ok = run_command(
                            """UPDATE contas_receber
                               SET status = 'pago',
                                   data_pagamento   = %s,
                                   valor_pago_final = %s,
                                   juros_isento     = %s,
                                   isento_por       = %s
                               WHERE id = %s""",
                            (hoje, vp, efetivo_isento,
                             username if efetivo_isento else None, parc_id),
                        )
                        if ok:
                            restante = round(restante - vp, 2)
                        else:
                            erros += 1
                    else:
                        novo_valor = round(vp - restante, 2)
                        ok = run_command(
                            """UPDATE contas_receber
                               SET valor_parcela = %s
                               WHERE id = %s""",
                            (novo_valor, parc_id),
                        )
                        if ok:
                            restante = 0
                        else:
                            erros += 1
                        break
                if erros == 0:
                    st.success(f"✅ Abatimento de R$ {valor_abat:,.2f} aplicado!")
                    st.rerun()
                else:
                    st.error("Erro ao aplicar abatimento. Tente novamente.")

        # ── Quitação Total ─────────────────────────────────────────────────
        with col_qt:
            st.write("")
            if st.button("💰 Quitação Total", key="dlg_quit_total", use_container_width=True, type="primary"):
                erros = 0
                for parc_id, valor_cobrar, efetivo_isento in linhas_baixa:
                    ok = run_command(
                        """UPDATE contas_receber
                           SET status = 'pago',
                               data_pagamento   = %s,
                               valor_pago_final = %s,
                               juros_isento     = %s,
                               isento_por       = %s
                           WHERE id = %s""",
                        (hoje, valor_cobrar,
                         efetivo_isento,
                         username if efetivo_isento else None,
                         parc_id),
                    )
                    if not ok:
                        erros += 1
                if erros == 0:
                    st.success(f"✅ {len(linhas_baixa)} parcela(s) quitada(s) — Total: R$ {total_cobrar:,.2f}")
                    st.rerun()
                else:
                    st.error(f"{erros} parcela(s) não foram baixadas. Tente novamente.")

    # ── Histórico de parcelas pagas ────────────────────────────────────────────
    if not pagas.empty:
        with st.expander("📋 Histórico de parcelas pagas"):
            st.dataframe(
                pagas[["data_vencimento", "valor_parcela", "data_pagamento",
                        "valor_pago_final", "juros_isento", "isento_por"]].rename(columns={
                    "data_vencimento": "Vencimento",
                    "valor_parcela":   "Valor Original",
                    "data_pagamento":  "Pago em",
                    "valor_pago_final": "Valor Pago",
                    "juros_isento":    "Juros Isento",
                    "isento_por":      "Isento Por",
                }),
                use_container_width=True,
                hide_index=True,
            )


# ══════════════════════════════════════════════════════════════════════════════
# FINANCEIRO ELITE — Legado + Novo Sistema | JGAutomações.AI
# ══════════════════════════════════════════════════════════════════════════════

def calcular_encargos(valor_saldo: float, dt_vencimento) -> dict:
    """
    Encargos legais para varejo — CDC Art.52 §1 + CC Art.406
    Multa: 2% fixo (uma vez) | Juros mora: 1%/mês proporcional
    """
    if not dt_vencimento:
        return {'valor_original': valor_saldo, 'dias_atraso': 0,
                'multa': 0.0, 'juros': 0.0, 'total_encargos': 0.0,
                'valor_total': valor_saldo, 'em_atraso': False}
    hoje = date.today()
    if isinstance(dt_vencimento, str):
        try:
            dt_vencimento = datetime.strptime(dt_vencimento, '%Y-%m-%d').date()
        except Exception:
            return {'valor_original': valor_saldo, 'dias_atraso': 0,
                    'multa': 0.0, 'juros': 0.0, 'total_encargos': 0.0,
                    'valor_total': valor_saldo, 'em_atraso': False}
    if hasattr(dt_vencimento, 'date'):
        dt_vencimento = dt_vencimento.date()
    if dt_vencimento >= hoje:
        return {'valor_original': valor_saldo, 'dias_atraso': 0,
                'multa': 0.0, 'juros': 0.0, 'total_encargos': 0.0,
                'valor_total': valor_saldo, 'em_atraso': False}
    dias = (hoje - dt_vencimento).days
    multa = 0.0  # SGA nao cobra multa separada
    juros = round(valor_saldo * 0.001 * dias, 2)  # 0,1%/dia = 3%/mes (igual SGA)
    total_enc = round(multa + juros, 2)
    return {
        'valor_original': valor_saldo,
        'dias_atraso': dias,
        'multa': multa,
        'juros': juros,
        'total_encargos': total_enc,
        'valor_total': round(valor_saldo + total_enc, 2),
        'em_atraso': True,
    }


def get_recebiveis_manu(filtro='Todos', busca_cliente=''):
    """Retorna DataFrame unificado de recebíveis: banco novo + legado."""
    q = """
    SELECT
        c.nome                      AS nome_cliente,
        COALESCE(c.cpf,'')          AS cpf,
        v.id::text                  AS documento,
        cr.id::text                 AS ref_id,
        NULL::text                  AS codigo_cliente,
        v.data_venda::date          AS dt_emissao,
        cr.data_vencimento          AS dt_vencimento,
        cr.valor_parcela            AS valor_saldo,
        cr.status,
        v.forma_pagamento           AS modalidade,
        'banco'                     AS origem,
        ''                          AS observacao
    FROM contas_receber cr
    JOIN vendas v ON cr.venda_id = v.id
    JOIN clientes c ON v.cliente_id = c.id
    WHERE cr.status != 'Pago'

    UNION ALL

    SELECT
        COALESCE(da.nome_cliente, 'Cliente '||da.codigo_cliente) AS nome_cliente,
        COALESCE(cl.cpf,'')         AS cpf,
        da.documento                AS documento,
        da.id::text                 AS ref_id,
        da.codigo_cliente           AS codigo_cliente,
        da.dt_emissao,
        da.dt_vencimento,
        da.valor_saldo,
        da.status,
        da.modalidade,
        'legado'                    AS origem,
        COALESCE(da.observacao,'')  AS observacao
    FROM duplicatas_abertas da
    LEFT JOIN clientes_legados cl ON da.codigo_cliente = cl.codigo_legado
    WHERE da.status = 'Pendente'

    ORDER BY dt_vencimento
    """
    df = run_query(q)
    hoje = date.today()

    def _status_cor(row):
        vcto = row['dt_vencimento']
        if vcto is None:
            return 'normal'
        if hasattr(vcto, 'date'):
            vcto = vcto.date()
        if isinstance(vcto, str):
            try:
                vcto = datetime.strptime(vcto, '%Y-%m-%d').date()
            except Exception:
                return 'normal'
        if vcto < hoje:
            return 'vencido'
        if vcto == hoje:
            return 'hoje'
        return 'normal'

    df['status_cor'] = df.apply(_status_cor, axis=1)
    df['enc'] = df.apply(lambda r: calcular_encargos(
        float(r['valor_saldo']), r['dt_vencimento']
    ), axis=1)
    df['dias_atraso']        = df['enc'].apply(lambda e: e['dias_atraso'])
    df['multa']              = df['enc'].apply(lambda e: e['multa'])
    df['juros_mora']         = df['enc'].apply(lambda e: e['juros'])
    df['valor_com_encargos'] = df['enc'].apply(lambda e: e['valor_total'])

    if filtro == 'Vencidos':
        df = df[df['status_cor'] == 'vencido']
    elif filtro == 'Vence Hoje':
        df = df[df['status_cor'] == 'hoje']
    elif filtro == 'A Vencer':
        df = df[df['status_cor'] == 'normal']

    if busca_cliente.strip():
        t = busca_cliente.strip().upper()
        mask = (
            df['nome_cliente'].str.upper().str.contains(t, na=False)
            | df['cpf'].str.replace(r'\D', '', regex=True).str.contains(
                busca_cliente.strip().replace(r'\D', ''), na=False)
            | df['documento'].str.upper().str.contains(t, na=False)
        )
        df = df[mask]

    return df.drop(columns=['enc'])


def render_kpis_manu(df):
    """KPIs cockpit: vencidos / vence hoje / a vencer / carteira total."""
    venc    = df[df['status_cor'] == 'vencido']
    hoje_df = df[df['status_cor'] == 'hoje']
    normal  = df[df['status_cor'] == 'normal']

    total_cart = float(df['valor_saldo'].sum())
    total_venc = float(venc['valor_saldo'].sum())
    enc_potencial = float(venc['valor_com_encargos'].sum()) - total_venc
    cli_inad = int(venc['nome_cliente'].nunique())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔴 Vencido", f"R$ {total_venc:,.2f}",
              delta=f"{cli_inad} clientes", delta_color="inverse")
    c2.metric("🟡 Vence Hoje", f"R$ {float(hoje_df['valor_saldo'].sum()):,.2f}")
    c3.metric("🔵 A Vencer",   f"R$ {float(normal['valor_saldo'].sum()):,.2f}")
    c4.metric("💰 Carteira Total", f"R$ {total_cart:,.2f}")

    if total_venc > 0:
        st.caption(
            f"⚠️ Encargos potenciais nos vencidos: R$ {enc_potencial:,.2f} "
            f"(multa 2% + juros 1%/mês — CDC Art.52 + CC Art.406)"
        )


def render_painel_baixa(parcela_row, conn, perfil):
    """Painel completo de baixa de parcela (banco novo ou legado)."""
    saldo  = float(parcela_row['valor_saldo'])
    vcto   = parcela_row['dt_vencimento']
    if hasattr(vcto, 'date'):
        vcto = vcto.date()
    enc    = calcular_encargos(saldo, vcto)
    nome   = parcela_row['nome_cliente']
    origem = parcela_row['origem']

    st.markdown(f"#### 💳 Baixa — {nome}")
    st.caption(
        f"Doc: {parcela_row['documento']} | Venc: {vcto} | "
        f"Origem: {'🏦 Novo Sistema' if origem == 'banco' else '📁 Sistema Antigo'}"
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Valor Original", f"R$ {saldo:,.2f}")
    if enc['em_atraso']:
        c2.metric("Encargos Legais", f"R$ {enc['total_encargos']:,.2f}",
                  delta=f"{enc['dias_atraso']}d de atraso", delta_color="inverse")
        c3.metric("Total a Cobrar", f"R$ {enc['valor_total']:,.2f}")
    else:
        c2.metric("Encargos", "R$ 0,00", delta="No prazo ✅")
        c3.metric("Total a Cobrar", f"R$ {saldo:,.2f}")

    if enc['em_atraso']:
        with st.expander("📋 Ver detalhamento dos encargos (CDC + Código Civil)"):
            td = enc['dias_atraso']
            st.markdown(f"""
| Item | Base Legal | Cálculo | Valor |
|------|-----------|---------|-------|
| Multa de mora | CDC Art.52 §1 — 2% fixo | R$ {saldo:,.2f} × 2% | **R$ {enc['multa']:,.2f}** |
| Juros de mora | CC Art.406 — 1%/mês prop. | R$ {saldo:,.2f} × {td}d × 0,033%/d | **R$ {enc['juros']:,.2f}** |
| **Total encargos** | | | **R$ {enc['total_encargos']:,.2f}** |
| **Total a cobrar** | | | **R$ {enc['valor_total']:,.2f}** |

> Limite legal STJ: 12% ao ano. Multa cobrada uma única vez.
            """)

    _rid          = parcela_row['ref_id']
    _is_gerencial = perfil in ['admin_master', 'gerencial']

    isentar    = False
    valor_base = enc['valor_total']

    if _is_gerencial:
        isentar = st.checkbox("🔓 Isentar Encargos (Alçada Gerencial)",
                              key=f"isen_{_rid}")
        if isentar:
            valor_base = saldo
            st.info(f"Encargos isentados. Cobrar apenas: R$ {saldo:,.2f}")

    valor_input = st.number_input(
        "💡 Valor recebido",
        min_value=0.01,
        max_value=float(valor_base * 3),
        value=float(round(valor_base, 2)),
        step=0.01,
        format="%.2f",
        key=f"valor_rec_{_rid}",
        help="Menor que o saldo = abate parcial; maior = quita e cascata na próxima.",
    )

    forma = st.selectbox(
        "Forma de recebimento",
        ["Dinheiro", "Pix", "Cartão Débito", "Cartão Crédito", "Transferência", "Cheque"],
        key=f"forma_{_rid}",
    )

    obs = ""
    if _is_gerencial:
        obs = st.text_input("Observação (opcional)", key=f"obs_{_rid}", max_chars=200)

    if valor_input < saldo * 0.999:
        resto = round(saldo - valor_input, 2)
        st.warning(f"⚡ Baixa PARCIAL — Saldo restante: R$ {resto:,.2f} (parcela continua em aberto)")
    else:
        excedente = round(valor_input - valor_base, 2)
        if excedente > 0.01:
            st.success(f"✅ Quita esta parcela + R$ {excedente:,.2f} abatido na próxima")
        else:
            st.success("✅ Quitação total desta parcela")

    if st.button("✅ CONFIRMAR RECEBIMENTO", type="primary",
                 use_container_width=True, key=f"conf_{_rid}"):
        _executar_baixa_manu(parcela_row, valor_input, isentar, enc, forma, conn, obs)
        _exibir_cupom_baixa(parcela_row, valor_input, isentar, enc, forma, obs)
        st.session_state.pop('leg_parcela', None)


def _executar_baixa_manu(parcela, valor_pago, isentou, enc, forma, conn, obs=""):
    """Executa baixa total ou parcial na tabela correta (banco ou legado)."""
    cur     = conn.cursor()
    hoje    = date.today()
    saldo   = float(parcela['valor_saldo'])
    origem  = parcela['origem']
    _ref_raw = str(parcela['ref_id']).strip()
    try:
        ref_id = int(_ref_raw)
        _is_uuid = False
    except ValueError:
        ref_id = _ref_raw
        _is_uuid = True
    operador = st.session_state.get('usuario', '')

    if valor_pago >= saldo * 0.999:
        saldo_pos  = 0.0
        excedente  = max(0, round(valor_pago - saldo, 2))
        if _is_uuid:
            cur.execute("""UPDATE contas_receber SET status='Pago',data_pagamento=%s,valor_pago_final=%s WHERE id=%s::uuid""", (hoje, valor_pago, ref_id))
            conn.commit()
            st.success(f"Quitado! R$ {valor_pago:,.2f} recebido via {forma}.")
            return
        if origem == 'legado':
            cur.execute("""
                UPDATE duplicatas_abertas
                SET status='Pago', dt_baixa=%s,
                    valor_pago_total=valor_pago_total+%s,
                    valor_saldo=0, forma_recebimento=%s,
                    isentou_encargos=%s
                WHERE id=%s
            """, (hoje, valor_pago, forma, isentou, ref_id))
            if excedente > 0.01:
                cur.execute("""
                    UPDATE duplicatas_abertas
                    SET valor_saldo = GREATEST(0, valor_saldo - %s)
                    WHERE codigo_cliente = %s
                      AND status = 'Pendente'
                      AND id != %s
                      AND dt_vencimento = (
                          SELECT MIN(dt_vencimento) FROM duplicatas_abertas
                          WHERE codigo_cliente = %s
                            AND status = 'Pendente'
                            AND id != %s)
                """, (excedente, parcela['codigo_cliente'], ref_id,
                      parcela['codigo_cliente'], ref_id))
        else:
            cur.execute("UPDATE contas_receber SET status='Pago' WHERE id=%s", (ref_id,))
        conn.commit()
        st.success(f"✅ Quitado! R$ {valor_pago:,.2f} recebido via {forma}.")
    else:
        saldo_pos  = round(saldo - valor_pago, 2)
        if origem == 'legado':
            cur.execute("""
                UPDATE duplicatas_abertas
                SET valor_saldo=%s,
                    valor_pago_total=valor_pago_total+%s,
                    forma_recebimento=%s
                WHERE id=%s
            """, (saldo_pos, valor_pago, forma, ref_id))
        else:
            cur.execute(
                "UPDATE contas_receber SET valor_parcela=%s WHERE id=%s",
                (saldo_pos, ref_id)
            )
        conn.commit()
        st.warning(f"⚡ Abatido R$ {valor_pago:,.2f}. Saldo restante: R$ {saldo_pos:,.2f}")

    run_command("""
        INSERT INTO movimentos_financeiros
            (parcela_id, origem, valor_pago, forma_pagamento, isentou_encargos,
             saldo_anterior, saldo_posterior, operador, observacao)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (str(ref_id), origem, valor_pago, forma, isentou,
          saldo, saldo_pos, operador, obs))


def _exibir_cupom_baixa(parcela, valor_pago, isentou, enc, forma, obs=""):
    """Exibe cupom de comprovante após baixa total ou parcial via components.html (impressão real)."""
    import streamlit.components.v1 as _comp
    from datetime import datetime as _dt
    saldo      = float(parcela['valor_saldo'])
    is_total   = valor_pago >= saldo * 0.999
    saldo_rest = max(0.0, round(saldo - valor_pago, 2))
    agora      = _dt.now().strftime('%d/%m/%Y %H:%M')
    operador   = st.session_state.get('usuario', '—')

    enc_val  = float(enc.get('total_encargos', 0))
    enc_html = ""
    if enc_val > 0 and not isentou:
        enc_html = f"<tr><td style='padding:3px 0;color:#6B7280'>Encargos</td><td style='text-align:right;color:#DC2626;font-weight:600'>R$ {enc_val:,.2f}</td></tr>"
    elif isentou:
        enc_html = "<tr><td colspan='2' style='padding:3px 0;font-size:11px;color:#9CA3AF'>* Encargos isentados — alçada gerencial</td></tr>"

    obs_html = f"<tr><td style='padding:3px 0;color:#6B7280'>Observação</td><td style='text-align:right'>{obs}</td></tr>" if obs else ""

    if is_total:
        status_html = "<div style='background:#16A34A;color:white;padding:8px;border-radius:6px;text-align:center;font-weight:700;font-size:15px'>✅ PARCELA QUITADA</div>"
        saldo_html  = "<div style='text-align:center;color:#16A34A;font-weight:600;margin-top:4px'>Saldo devedor: R$ 0,00</div>"
    else:
        status_html = "<div style='background:#D97706;color:white;padding:8px;border-radius:6px;text-align:center;font-weight:700;font-size:15px'>⚡ BAIXA PARCIAL</div>"
        saldo_html  = f"<div style='text-align:center;color:#D97706;font-weight:600;margin-top:4px'>Saldo restante: R$ {saldo_rest:,.2f}</div>"

    nome_esc = str(parcela['nome_cliente']).replace("'", "\\'").replace('"', '&quot;')

    html = f"""
<div id="cupom" style="font-family:'Courier New',monospace;max-width:380px;
    margin:0 auto;padding:20px;border:2px solid #374151;border-radius:8px;
    background:#ffffff;color:#111827">

    <div style="text-align:center;border-bottom:1px dashed #9CA3AF;
                padding-bottom:12px;margin-bottom:12px">
        <div style="font-size:20px;font-weight:700">LOJA GM HOMEM ITAÚNA</div>
        <div style="font-size:12px;color:#6B7280">Moda Masculina — JGAutomações.AI</div>
        <div style="font-size:11px;color:#6B7280">{agora}</div>
    </div>

    <table style="width:100%;font-size:13px;border-collapse:collapse;color:#374151">
        <tr><td style="padding:3px 0;color:#6B7280">Cliente</td>
            <td style="text-align:right;font-weight:600">{parcela['nome_cliente']}</td></tr>
        <tr><td style="padding:3px 0;color:#6B7280">Documento</td>
            <td style="text-align:right">{parcela['documento']}</td></tr>
        <tr><td style="padding:3px 0;color:#6B7280">Vencimento</td>
            <td style="text-align:right">{str(parcela['dt_vencimento'])}</td></tr>
        <tr><td colspan="2"><hr style="border:1px dashed #D1D5DB;margin:6px 0"></td></tr>
        <tr><td style="padding:3px 0;color:#6B7280">Valor original</td>
            <td style="text-align:right">R$ {saldo:,.2f}</td></tr>
        {enc_html}
        <tr style="background:#F3F4F6">
            <td style="padding:5px 4px;font-weight:700">VALOR RECEBIDO</td>
            <td style="text-align:right;font-weight:700;font-size:16px;color:#15803D">R$ {valor_pago:,.2f}</td></tr>
        <tr><td style="padding:3px 0;color:#6B7280">Forma pagamento</td>
            <td style="text-align:right">{forma}</td></tr>
        <tr><td style="padding:3px 0;color:#6B7280">Operador</td>
            <td style="text-align:right">{operador}</td></tr>
        {obs_html}
    </table>

    <div style="margin-top:12px">{status_html}</div>
    {saldo_html}

    <div style="text-align:center;font-size:10px;color:#9CA3AF;margin-top:12px;
        border-top:1px dashed #9CA3AF;padding-top:8px">
        Obrigada pela preferência! 💜<br>
        GM Homem Itaúna — Moda Masculina
    </div>
</div>

<button onclick="imprimirCupom_{id(parcela)}()" style="
    width:100%;margin-top:10px;padding:12px;
    background:#1D4ED8;color:white;border:none;
    border-radius:8px;font-size:15px;cursor:pointer;font-weight:600">
    🖨️ Imprimir Cupom
</button>

<script>
function imprimirCupom_{id(parcela)}() {{
    var conteudo = document.getElementById('cupom').outerHTML;
    var janela = window.open('', '_blank', 'width=460,height=650');
    janela.document.write('<html><head><title>Cupom - {nome_esc}</title>');
    janela.document.write('<style>');
    janela.document.write("body{{font-family:'Courier New',monospace;padding:20px;margin:0;background:#fff;color:#000}}");
    janela.document.write('@media print{{button{{display:none!important}}}}');
    janela.document.write('</style></head><body>');
    janela.document.write(conteudo);
    janela.document.write('<br><button onclick="window.print();setTimeout(function(){{try{{window.close();}}catch(e){{}}}},1000)" style="width:100%;padding:10px;background:#111;color:#fff;border:none;font-size:14px;cursor:pointer;border-radius:6px">🖨️ Confirmar Impressão</button>');
    janela.document.write('</body></html>');
    janela.document.close();
    setTimeout(function() {{ janela.print(); }}, 600);
}}
</script>
"""
    st.markdown("---")
    _comp.html(html, height=500, scrolling=False)


def _executar_baixa_pool(parcela, valor_pago, isentou, enc, forma, obs=""):
    """Executa baixa total ou parcial usando pool — sem conn externo."""
    from datetime import date as _date
    hoje     = _date.today()
    saldo    = float(parcela['valor_saldo'])
    origem   = parcela['origem']
    ref_id   = str(parcela['ref_id'])
    operador = st.session_state.get('usuario', '')
    saldo_pos = 0.0

    with _db_get_conn() as conn:
        cur = conn.cursor()
        if valor_pago >= saldo * 0.999:
            excedente = max(0, round(valor_pago - saldo, 2))
            if origem == 'legado':
                cur.execute("""
                    UPDATE duplicatas_abertas
                    SET status='Pago', dt_baixa=%s,
                        valor_pago_total=valor_pago_total+%s,
                        valor_saldo=0, forma_recebimento=%s,
                        isentou_encargos=%s
                    WHERE id=%s
                """, (hoje, valor_pago, forma, isentou, int(ref_id)))
                if excedente > 0.01:
                    cur.execute("""
                        UPDATE duplicatas_abertas
                        SET valor_saldo = GREATEST(0, valor_saldo - %s)
                        WHERE codigo_cliente = %s AND status = 'Pendente'
                          AND id != %s
                          AND dt_vencimento = (
                              SELECT MIN(dt_vencimento) FROM duplicatas_abertas
                              WHERE codigo_cliente = %s
                                AND status = 'Pendente' AND id != %s)
                    """, (excedente, parcela['codigo_cliente'], int(ref_id),
                          parcela['codigo_cliente'], int(ref_id)))
            else:
                cur.execute("UPDATE contas_receber SET status='Pago' WHERE id=%s::uuid", (ref_id,))
            saldo_pos = 0.0
            st.success(f"✅ Quitado! R$ {valor_pago:,.2f} recebido via {forma}.")
        else:
            saldo_pos = round(saldo - valor_pago, 2)
            if origem == 'legado':
                cur.execute("""
                    UPDATE duplicatas_abertas
                    SET valor_saldo=%s, valor_pago_total=valor_pago_total+%s,
                        forma_recebimento=%s
                    WHERE id=%s
                """, (saldo_pos, valor_pago, forma, int(ref_id)))
            else:
                cur.execute(
                    "UPDATE contas_receber SET valor_parcela=%s WHERE id=%s::uuid",
                    (saldo_pos, ref_id))
            st.warning(f"⚡ Abatido R$ {valor_pago:,.2f}. Saldo restante: R$ {saldo_pos:,.2f}")

        cur.execute("""
            INSERT INTO movimentos_financeiros
                (parcela_id, origem, valor_pago, forma_pagamento, isentou_encargos,
                 saldo_anterior, saldo_posterior, operador, observacao)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (ref_id, origem, valor_pago, forma, isentou,
              saldo, saldo_pos, operador, obs))


def render_painel_baixa_nasa(parcela_row, perfil, state_key=None):
    """Painel de baixa inline — usa pool, sem conn externo."""
    saldo  = float(parcela_row['valor_saldo'])
    vcto   = parcela_row['dt_vencimento']
    if hasattr(vcto, 'date'):
        vcto = vcto.date()
    enc    = calcular_encargos(saldo, vcto)
    origem = parcela_row['origem']
    _rid   = str(parcela_row['ref_id'])
    _sk    = _sanitizar_chave(_rid)  # chave segura para widgets

    st.markdown(f"#### 💳 Baixa — {parcela_row['nome_cliente']}")
    st.caption(
        f"Doc: {parcela_row['documento']} | Venc: {vcto} | "
        f"Origem: {'🏦 Banco' if origem == 'banco' else '📁 Legado'}"
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Valor Original", f"R$ {saldo:,.2f}")
    if enc['em_atraso']:
        c2.metric("Encargos Legais", f"R$ {enc['total_encargos']:,.2f}",
                  delta=f"{enc['dias_atraso']}d de atraso", delta_color="inverse")
        c3.metric("Total a Cobrar", f"R$ {enc['valor_total']:,.2f}")
    else:
        c2.metric("Encargos", "R$ 0,00", delta="No prazo ✅")
        c3.metric("Total a Cobrar", f"R$ {saldo:,.2f}")

    if enc['em_atraso']:
        with st.expander("📋 Ver detalhamento dos encargos"):
            td = enc['dias_atraso']
            st.markdown(f"""| Item | Cálculo | Valor |
|------|---------|-------|
| Juros mora (0,1%/dia) | R$ {saldo:,.2f} × 0,1% × {td}d | R$ {enc['juros']:,.2f} |
| **Total encargos** | | **R$ {enc['total_encargos']:,.2f}** |
| **Total a cobrar** | | **R$ {enc['valor_total']:,.2f}** |""")

    _is_gerencial = perfil in ['admin', 'admin_master', 'gerencial']
    isentar              = False
    isentar_parcial_pct  = 0
    encargos_ajustados   = enc['total_encargos'] if enc['em_atraso'] else 0
    valor_base           = enc['valor_total'] if enc['em_atraso'] else saldo

    if _is_gerencial:
        _sk_isent = _sanitizar_chave(str(parcela_row.get('ref_id', _sk)))
        st.markdown("**⚖️ Gestão de Encargos (alçada gerencial):**")
        tipo_isencao = st.radio(
            "",
            ["Cobrar encargos integrais", "Isenção total de encargos", "Isenção parcial (%)"],
            key=f'tipo_isent_{_sk_isent}',
            horizontal=True,
            label_visibility="collapsed",
        )
        if tipo_isencao == "Isenção total de encargos":
            isentar            = True
            encargos_ajustados = 0
            valor_base         = saldo
            st.info(f"✅ Encargos isentados. Cobrar apenas: **R$ {saldo:,.2f}**")
        elif tipo_isencao == "Isenção parcial (%)":
            pct = st.slider(
                "Percentual de desconto nos encargos",
                min_value=10, max_value=90, value=50, step=10,
                key=f'pct_isent_{_sk_isent}',
                format="%d%%",
            )
            isentar_parcial_pct = pct
            encargos_ajustados  = round(enc['total_encargos'] * (1 - pct / 100), 2)
            valor_base          = saldo + encargos_ajustados
            st.info(
                f"🔸 {pct}% de desconto nos encargos. "
                f"Encargos cobrados: **R$ {encargos_ajustados:,.2f}** "
                f"(desconto de R$ {enc['total_encargos'] - encargos_ajustados:,.2f}). "
                f"Total: **R$ {valor_base:,.2f}**"
            )

    val_default = round(valor_base, 2)

    valor_input = st.number_input(
        "💡 Valor recebido (edite para baixa parcial)",
        min_value=0.01, max_value=float(valor_base * 3),
        value=val_default, step=0.01, format="%.2f",
        key=f"nv_{_sk}",
        help="Menor que o saldo = abate parcial; maior = quita e cascata na próxima.",
    )
    forma = st.selectbox("Forma de recebimento",
        ["Dinheiro", "Pix", "Cartão Débito", "Cartão Crédito", "Transferência", "Cheque"],
        key=f"nf_{_sk}")

    obs = ""
    if _is_gerencial:
        obs = st.text_input("Observação (opcional)", key=f"no_{_sk}", max_chars=200)

    if valor_input < saldo * 0.999:
        st.warning(f"⚡ Baixa PARCIAL — Saldo restante: R$ {round(saldo - valor_input, 2):,.2f}")
    else:
        excedente = round(valor_input - valor_base, 2)
        if excedente > 0.01:
            st.success(f"✅ Quita esta parcela + R$ {excedente:,.2f} abatido na próxima")
        else:
            st.success("✅ Quitação total desta parcela")

    if st.button("✅ CONFIRMAR RECEBIMENTO", type="primary",
                 use_container_width=True, key=f"nc_{_sk}"):
        # Enriquecer obs com info de isenção parcial para auditoria
        _obs_final = obs
        if isentar_parcial_pct > 0:
            _obs_parcial = (
                f"Isenção parcial {isentar_parcial_pct}% encargos "
                f"(cobrado R$ {encargos_ajustados:,.2f} de R$ {enc['total_encargos']:,.2f})"
            )
            _obs_final = f"{obs} | {_obs_parcial}".strip(" |") if obs else _obs_parcial
        _isentar_flag = isentar or (isentar_parcial_pct > 0)
        _executar_baixa_pool(parcela_row, valor_input, _isentar_flag, enc, forma, _obs_final)
        _exibir_cupom_baixa(parcela_row, valor_input, _isentar_flag, enc, forma, _obs_final)
        if state_key:
            st.session_state.pop(state_key, None)
        st.rerun()


def ver_itens_venda_legado(documento, pedido, conn):
    """Busca registros do histórico quitado pelo documento ou pedido."""
    cur = conn.cursor()
    cur.execute("""
        SELECT hq.documento, hq.observacao, hq.modalidade,
               hq.valor_docto, hq.dt_pagamento, hq.vendedor
        FROM historico_quitado hq
        WHERE hq.documento = %s OR hq.pedido = %s
        LIMIT 20
    """, (str(documento), str(pedido)))
    rows = cur.fetchall()
    if rows:
        df_i = pd.DataFrame(rows,
                            columns=['Doc', 'Descrição', 'Modalidade',
                                     'Valor', 'Data Pgto', 'Vendedor'])
        st.dataframe(df_i, use_container_width=True, hide_index=True)
    else:
        st.info("📦 Detalhes de itens não disponíveis para este registro.")


def get_historico_cliente_manu(nome, cpf):
    """Histórico unificado de compras: banco novo + sistema antigo."""
    busca = f'%{nome}%'
    q = """
    SELECT
        v.data_venda::date AS data,
        v.valor_total      AS valor,
        v.forma_pagamento  AS forma,
        'Novo Sistema'     AS origem
    FROM vendas v
    JOIN clientes c ON v.cliente_id = c.id
    WHERE UPPER(c.nome) LIKE UPPER(%s) OR c.cpf = %s

    UNION ALL

    SELECT
        hq.dt_pagamento    AS data,
        hq.valor_docto     AS valor,
        hq.modalidade      AS forma,
        'Sistema Antigo'   AS origem
    FROM historico_quitado hq
    WHERE UPPER(hq.nome_cliente) LIKE UPPER(%s)

    ORDER BY data DESC NULLS LAST
    """
    return run_query(q, params=(busca, cpf, busca))



def _calcular_rfm(codigo_cliente: str) -> dict:
    """Calcula RFM Score + métricas do cliente (legado + novo sistema)."""
    from datetime import date as _date
    hoje = _date.today()
    # Dados do legado
    df_l = run_query("""
        SELECT COUNT(*) as tc, SUM(valor_docto) as vt, AVG(valor_docto) as tm,
               MAX(COALESCE(data_baixa, dt_vencimento)) as uc,
               MIN(dt_vencimento) as pc,
               SUM(CASE WHEN status='baixado' THEN 1 ELSE 0 END) as pg,
               SUM(CASE WHEN status='aberto' AND dt_vencimento < CURRENT_DATE THEN 1 ELSE 0 END) as vd
        FROM historico_legado WHERE cliente_codigo = %s
    """, [codigo_cliente])
    # Dados do sistema novo
    df_n = run_query("""
        SELECT COUNT(*) as tc, SUM(valor_original) as vt, AVG(valor_original) as tm,
               MAX(COALESCE(dt_baixa, dt_vencimento)) as uc,
               MIN(dt_vencimento) as pc,
               SUM(CASE WHEN status='Pago' THEN 1 ELSE 0 END) as pg,
               SUM(CASE WHEN status='Pendente' AND dt_vencimento < CURRENT_DATE THEN 1 ELSE 0 END) as vd
        FROM duplicatas_abertas WHERE codigo_cliente = %s
    """, [codigo_cliente])
    tc, vt, uc_dt, pc_dt, pg, vd = 0, 0.0, None, None, 0, 0
    for df in [df_l, df_n]:
        if not df.empty:
            r = df.iloc[0]
            tc += int(r['tc'] or 0); vt += float(r['vt'] or 0)
            pg += int(r['pg'] or 0); vd += int(r['vd'] or 0)
            for campo, var in [('uc', 'uc_dt'), ('pc', 'pc_dt')]:
                val = r[campo]
                if val:
                    try:
                        from datetime import datetime as _dt
                        d = val if hasattr(val, 'year') else _dt.strptime(str(val)[:10], '%Y-%m-%d').date()
                        if campo == 'uc' and (uc_dt is None or d > uc_dt): uc_dt = d
                        if campo == 'pc' and (pc_dt is None or d < pc_dt): pc_dt = d
                    except: pass
    tm = vt / tc if tc > 0 else 0
    dias_r = (hoje - uc_dt).days if uc_dt else 999
    meses = max(1, (hoje - pc_dt).days // 30) if pc_dt else 0
    # Scores 1-5
    r_s = 5 if dias_r<=30 else 4 if dias_r<=60 else 3 if dias_r<=90 else 2 if dias_r<=180 else 1
    f_s = 5 if tc>=20 else 4 if tc>=10 else 3 if tc>=5 else 2 if tc>=2 else 1
    m_s = 5 if tm>=500 else 4 if tm>=200 else 3 if tm>=100 else 2 if tm>=50 else 1
    p_s = 5 if tc==0 else (5 if pg/tc>=0.95 else 4 if pg/tc>=0.80 else 3 if pg/tc>=0.60 else 2 if pg/tc>=0.40 else 1)
    fi_s = 5 if meses>=24 else 4 if meses>=12 else 3 if meses>=6 else 2 if meses>=3 else 1
    rfm = r_s + f_s + m_s
    med = round((r_s+f_s+m_s+p_s+fi_s)/5, 1)
    seg, cor, desc = (
        ("⭐ VIP","#F59E0B","Cliente premium — prioridade máxima") if rfm>=13 else
        ("💚 Fiel","#10B981","Cliente regular com bom histórico") if rfm>=10 else
        ("🔵 Ativo","#3B82F6","Cliente em dia — manter engajamento") if rfm>=7 else
        ("⚠️ Em Risco","#F97316","Pode estar se afastando — agir agora") if rfm>=5 else
        ("🔴 Inativo","#EF4444","Cliente perdido — campanha de reativação")
    )
    return dict(r_s=r_s,f_s=f_s,m_s=m_s,p_s=p_s,fi_s=fi_s,rfm=rfm,med=med,
                seg=seg,cor=cor,desc=desc,tc=tc,vt=round(vt,2),tm=round(tm,2),
                dias_r=dias_r,meses=meses,pg=pg,vd=vd)


def _render_radar_rfm(rfm: dict, nome: str):
    """Renderiza Radar RFM com SVG via components.html."""
    import streamlit.components.v1 as _c
    import math
    dims = [('Recência',rfm['r_s']),('Frequência',rfm['f_s']),('Valor',rfm['m_s']),
            ('Pontualidade',rfm['p_s']),('Fidelidade',rfm['fi_s'])]
    cx, cy, rm = 150, 150, 95
    n = len(dims)
    pts = []
    for i,(l,s) in enumerate(dims):
        a = math.pi/2 + 2*math.pi*i/n
        r = rm*s/5
        pts.append((cx+r*math.cos(a), cy-r*math.sin(a)))
    poly = ' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)
    grid = ''
    for ring in range(1,6):
        rp = []
        for i in range(n):
            a = math.pi/2+2*math.pi*i/n
            rr = rm*ring/5
            rp.append(f'{cx+rr*math.cos(a):.1f},{cy-rr*math.sin(a):.1f}')
        grid += f'<polygon points="{" ".join(rp)}" fill="none" stroke="#374151" stroke-width="0.5" opacity="0.4"/>'
    axes = ''.join(f'<line x1="{cx}" y1="{cy}" x2="{cx+rm*math.cos(math.pi/2+2*math.pi*i/n):.1f}" y2="{cy-rm*math.sin(math.pi/2+2*math.pi*i/n):.1f}" stroke="#4B5563" stroke-width="0.8" opacity="0.5"/>' for i in range(n))
    lbls = ''
    for i,(l,s) in enumerate(dims):
        a = math.pi/2+2*math.pi*i/n
        lx = cx+(rm+24)*math.cos(a); ly = cy-(rm+24)*math.sin(a)
        anc = 'middle' if abs(lx-cx)<10 else ('end' if lx<cx else 'start')
        lbls += f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="{anc}" font-size="10" fill="#9CA3AF" font-family="monospace">{l}</text><text x="{lx:.0f}" y="{ly+13:.0f}" text-anchor="{anc}" font-size="11" fill="{rfm["cor"]}" font-weight="700" font-family="monospace">{s}/5</text>'
    dot = ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{rfm["cor"]}" stroke="white" stroke-width="1.5"/>' for x,y in pts)
    bars = ''
    for l,s in dims[:3]:
        bars += f'<div style="margin-bottom:8px"><div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:3px"><span style="color:#9CA3AF">{l}</span><span style="color:{rfm["cor"]};font-weight:700">{s}/5</span></div><div style="background:#374151;border-radius:4px;height:6px"><div style="background:{rfm["cor"]};border-radius:4px;height:6px;width:{s*20}%"></div></div></div>'
    html = f"""<div style="font-family:monospace;background:#111827;border-radius:16px;padding:20px;color:white">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
  <div><div style="font-size:10px;color:#6B7280;letter-spacing:2px">ANÁLISE RFM</div><div style="font-size:17px;font-weight:700">{nome}</div></div>
  <div style="text-align:right"><div style="background:{rfm["cor"]}22;border:1px solid {rfm["cor"]};border-radius:20px;padding:5px 14px;display:inline-block"><span style="color:{rfm["cor"]};font-weight:700">{rfm["seg"]}</span></div><div style="font-size:11px;color:#6B7280;margin-top:3px">{rfm["desc"]}</div></div>
</div>
<div style="display:flex;gap:16px">
  <div style="flex:1">
    <svg width="300" height="300" viewBox="0 0 300 300">{grid}{axes}
      <polygon points="{poly}" fill="{rfm["cor"]}" fill-opacity="0.2" stroke="{rfm["cor"]}" stroke-width="2"/>
      {dot}{lbls}
      <text x="150" y="145" text-anchor="middle" font-size="28" font-weight="700" fill="{rfm["cor"]}" font-family="monospace">{rfm["med"]}</text>
      <text x="150" y="162" text-anchor="middle" font-size="10" fill="#6B7280" font-family="monospace">score geral</text>
    </svg>
  </div>
  <div style="flex:1;display:flex;flex-direction:column;gap:10px;justify-content:center">
    <div style="background:#1F2937;border-radius:10px;padding:12px">
      <div style="font-size:10px;color:#6B7280;text-transform:uppercase;letter-spacing:1px">Total Compras</div>
      <div style="font-size:24px;font-weight:700">{rfm["tc"]}</div>
      <div style="font-size:11px;color:#6B7280">{rfm["meses"]} meses de relacionamento</div>
    </div>
    <div style="background:#1F2937;border-radius:10px;padding:12px">
      <div style="font-size:10px;color:#6B7280;text-transform:uppercase;letter-spacing:1px">Volume Total</div>
      <div style="font-size:22px;font-weight:700;color:{rfm["cor"]}">R$ {rfm["vt"]:,.2f}</div>
      <div style="font-size:11px;color:#6B7280">Ticket médio: R$ {rfm["tm"]:,.2f}</div>
    </div>
    <div style="background:#1F2937;border-radius:10px;padding:12px">
      <div style="font-size:10px;color:#6B7280;text-transform:uppercase;letter-spacing:1px">Pontualidade</div>
      <div style="display:flex;gap:14px;margin-top:4px">
        <div><div style="font-size:18px;font-weight:700;color:#10B981">{rfm["pg"]}</div><div style="font-size:10px;color:#6B7280">pagas</div></div>
        <div><div style="font-size:18px;font-weight:700;color:#EF4444">{rfm["vd"]}</div><div style="font-size:10px;color:#6B7280">vencidas</div></div>
        <div><div style="font-size:18px;font-weight:700;color:#6B7280">{rfm["dias_r"]}d</div><div style="font-size:10px;color:#6B7280">últ. compra</div></div>
      </div>
    </div>
    <div style="background:#1F2937;border-radius:10px;padding:12px">{bars}</div>
  </div>
</div></div>"""
    _c.html(html, height=520, scrolling=False)

# ── Resumo IA de Perfil de Consumo ────────────────────────────────────────────
def _resumo_ia_perfil(cliente_nome: str, historico_txt: str) -> str:
    """Gera resumo do perfil de consumo usando Claude. Retorna texto formatado."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not _ANTHROPIC_OK or not api_key:
        return (
            "⚠️ **Resumo IA indisponível.**  \n"
            "Configure `ANTHROPIC_API_KEY` no arquivo `.env` para ativar esta função.  \n"
            "Instale: `pip install anthropic`"
        )
    try:
        client = _anthropic_lib.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[{
                "role": "user",
                "content": (
                    f"Você é analista de CRM de uma loja de roupas femininas chamada GM Homem Itaúna. "
                    f"Com base no histórico de compras a seguir do cliente **{cliente_nome}**, "
                    f"escreva um resumo objetivo em 3-5 frases curtas sobre: "
                    f"perfil de consumo, categorias preferidas, ticket médio, frequência de compra, "
                    f"e uma sugestão de abordagem de relacionamento.\n\n"
                    f"Histórico:\n{historico_txt}"
                ),
            }],
        )
        return msg.content[0].text
    except Exception as e:
        return f"❌ Erro ao gerar resumo: {e}"


# ── Gauge de Meta (Velocímetro) ───────────────────────────────────────────────
def _gauge_meta(valor_atual: float, meta: float) -> "go.Figure | None":
    if not _PLOTLY_OK:
        return None
    teto = max(meta * 1.3, valor_atual * 1.1, 1.0)
    pct  = (valor_atual / meta * 100) if meta > 0 else 0
    cor  = "#26A69A" if pct >= 100 else ("#C8922A" if pct >= 60 else "#A63347")
    fig  = _go.Figure(_go.Indicator(
        mode="gauge+number+delta",
        value=valor_atual,
        delta={"reference": meta, "valueformat": ",.2f", "prefix": "R$ "},
        number={"prefix": "R$ ", "valueformat": ",.2f", "font": {"size": 28}},
        gauge={
            "axis": {"range": [0, teto], "tickformat": ",.0f"},
            "bar":  {"color": cor, "thickness": 0.3},
            "steps": [
                {"range": [0,        meta * 0.6],  "color": "#FFECEC"},
                {"range": [meta*0.6, meta * 0.9],  "color": "#FFF3CD"},
                {"range": [meta*0.9, teto],         "color": "#E0F2F1"},
            ],
            "threshold": {
                "line": {"color": "#7B1F2E", "width": 3},
                "thickness": 0.8,
                "value": meta,
            },
        },
        title={"text": f"Meta do Mês  ·  {pct:.1f}%", "font": {"size": 15}},
    ))
    fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


# ── Categorização automática por palavras-chave ───────────────────────────────
_MAPA_CATEGORIAS: list[tuple[str, list[str]]] = [
    ("Calças",      ["calça", "calca", "jeans", "legging", "legins", "jegging",
                     "jogger", "pantacourt", "saruel"]),
    ("Blusas",      ["blusa", "camisa", "camiseta", "regata", "cropped", "top",
                     "body", "moletom", "suéter", "sueter", "tricô", "tricot"]),
    ("Vestidos",    ["vestido", "vestidinho"]),
    ("Saias",       ["saia", "saiote"]),
    ("Shorts",      ["short", "bermuda", "bermudão"]),
    ("Macacões",    ["macacão", "macacao", "jumpsuit"]),
    ("Casacos",     ["casaco", "jaqueta", "blazer", "colete", "sobretudo",
                     "trench", "cardigan"]),
    ("Acessórios",  ["cinto", "bolsa", "carteira", "clutch", "pochete",
                     "colar", "brinco", "pulseira", "anel", "lenço", "boné",
                     "chapéu", "oculos", "óculos", "meia", "meião"]),
    ("Calçados",    ["sandália", "sandalia", "sapato", "tênis", "tenis",
                     "bota", "mule", "chinelo", "sapatilha", "scarpin"]),
    ("Íntimas",     ["calcinha", "sutiã", "sutia", "lingerie", "pijama",
                     "camisola", "robe"]),
    ("Praia",       ["biquíni", "biquini", "maiô", "maio", "saída de praia",
                     "saida de praia", "canoa"]),
    ("Plus Size",   ["plus", "plus size", "especial"]),
]


def _categorizar_produto(nome: str) -> str | None:
    """Retorna a categoria inferida do nome do produto, ou None se não reconhecer."""
    nome_l = nome.lower()
    for categoria, palavras in _MAPA_CATEGORIAS:
        if any(p in nome_l for p in palavras):
            return categoria
    return None


# ── Parser de Entrada Rápida de Estoque (NLP simples) ────────────────────────
def _parse_entrada_rapida(texto: str) -> dict | None:
    """Interpreta frases como '10 blusas seda 20 custo 50 venda'.
    Retorna dict com qtd, nome, custo, venda ou None se não reconhecer.
    """
    import re as _re
    t = texto.strip()
    # Formato: QTD NOME CUSTO_VAL custo VENDA_VAL venda
    m = _re.match(
        r'^(\d+)\s+(.+?)\s+([\d,.]+)\s+custo\s+([\d,.]+)\s+venda',
        t, _re.IGNORECASE
    )
    if m:
        return {
            "qtd":   int(m.group(1)),
            "nome":  m.group(2).strip(),
            "custo": float(m.group(3).replace(",", ".")),
            "venda": float(m.group(4).replace(",", ".")),
        }
    # Formato alternativo: QTD NOME VENDA_VAL (sem custo explícito)
    m2 = _re.match(r'^(\d+)\s+(.+?)\s+([\d,.]+)$', t, _re.IGNORECASE)
    if m2:
        return {
            "qtd":   int(m2.group(1)),
            "nome":  m2.group(2).strip(),
            "custo": 0.0,
            "venda": float(m2.group(3).replace(",", ".")),
        }
    return None


# ── Dialog: Financeiro Simplificado do Balcão ─────────────────────────────────
@st.dialog("Conta do Cliente", width="large")
def _dlg_balcao_financeiro(cliente_nome: str, username: str) -> None:
    """Modal balcão: parcelas por venda, drill-down de itens, baixa, abatimento parcial e cupom."""
    hoje = date.today()
    st.markdown(f"### {cliente_nome}")

    # Info do cliente (id + whatsapp) para disparo
    _df_cli_blc = run_query(
        "SELECT id::text AS cid, COALESCE(whatsapp, '') AS fone "
        f"FROM clientes WHERE nome = '{cliente_nome.replace(chr(39), chr(39)*2)}' LIMIT 1"
    )
    _blc_cli_id  = _df_cli_blc["cid"].iloc[0]  if not _df_cli_blc.empty else ""
    _blc_cli_fone = _df_cli_blc["fone"].iloc[0] if not _df_cli_blc.empty else ""

    # ── Recibo da última operação (pagamento / abatimento) ───────────────────
    _cupom_key = f"blc_cupom_{cliente_nome}"
    if st.session_state.get(_cupom_key):
        with st.expander("🧾 Recibo da operação — clique para ver/imprimir", expanded=True):
            st.markdown(
                _cupom_html_display(st.session_state[_cupom_key]),
                unsafe_allow_html=True,
            )
            _dc1, _dc2, _dc3 = st.columns([2, 2, 1])
            _dc1.download_button(
                "⬇️ Baixar recibo (.txt)",
                data=st.session_state[_cupom_key],
                file_name=f"recibo_{cliente_nome.replace(' ','_')}.txt",
                mime="text/plain",
                key="blc_dl_cupom",
                use_container_width=True,
            )
            with _dc2:
                components.html(
                    _cupom_iframe_html(
                        st.session_state[_cupom_key],
                        "pf_blc",
                        "🖨️ Imprimir Recibo",
                    ),
                    height=46,
                )
            if _dc3.button("✕ Fechar", key="blc_fechar_cupom",
                           use_container_width=True):
                st.session_state[_cupom_key] = None
                st.rerun()
        st.markdown("---")

    # ── Seletor de Vendedora (obrigatório para liberar pagamentos) ───────────
    _df_vnd_blc = run_query(
        "SELECT codigo_vendedor, COALESCE(nome_vendedor, codigo_vendedor) AS label "
        "FROM config_comissao WHERE ativo = true ORDER BY codigo_vendedor"
    )
    _blc_nome_vnd = ""
    _blc_cod_vnd  = ""
    if not _df_vnd_blc.empty:
        _blc_vnd_opts = _df_vnd_blc["codigo_vendedor"].tolist()
        _blc_vnd_lbl  = _df_vnd_blc["label"].tolist()
        _blc_vnd_idx  = st.selectbox(
            "🏷️ Vendedora responsável *",
            range(len(_blc_vnd_opts)),
            format_func=lambda i: f"{_blc_vnd_opts[i]} — {_blc_vnd_lbl[i]}",
            key="blc_vnd_sel",
        )
        _blc_cod_vnd  = _blc_vnd_opts[_blc_vnd_idx]
        _blc_nome_vnd = _blc_vnd_lbl[_blc_vnd_idx]
    else:
        st.warning("⚠️ Nenhuma vendedora cadastrada. Cadastre em Administração → Vendedoras.")
    _blc_vnd_ok = bool(_blc_cod_vnd)
    if not _blc_vnd_ok:
        st.warning("⚠️ Selecione o Vendedor para liberar os pagamentos.")

    # ── Busca parcelas em aberto (mesma estrutura do gerencial _dlg_baixa_cliente) ──
    _blc_nome_esc = cliente_nome.replace("'", "''")
    df_divida = run_query(f"""
        SELECT cr.id::text        AS parc_id,
               cr.valor_parcela,
               cr.data_vencimento,
               cr.status,
               cr.data_pagamento,
               cr.valor_pago_final,
               cr.juros_isento,
               cr.isento_por,
               v.id::text         AS venda_id,
               v.data_venda::date AS data_venda,
               v.forma_pagamento
        FROM contas_receber cr
        JOIN vendas v ON v.id = cr.venda_id
        JOIN clientes c ON c.id = v.cliente_id
        WHERE c.nome = '{_blc_nome_esc}' AND cr.status = 'aberto'
        ORDER BY cr.data_vencimento ASC
    """)

    # ── Legado em aberto para este cliente ───────────────────────────────────
    df_legado_blc = run_query(f"""
        SELECT hl.id::text AS leg_id,
               hl.documento, hl.ordem,
               hl.dt_emissao, hl.dt_vencimento,
               hl.modalidade, hl.valor_docto,
               hl.observacao, hl.status
        FROM historico_legado hl
        JOIN clientes c ON c.id = hl.cliente_id
        WHERE UPPER(c.nome) = UPPER('{_blc_nome_esc}') AND hl.status = 'aberto'
        ORDER BY hl.dt_vencimento ASC NULLS LAST
    """)

    if df_divida.empty and df_legado_blc.empty:
        st.success("✅ Cliente sem parcelas em aberto.")
        return

    _leg_saldo_blc = float(df_legado_blc["valor_docto"].astype(float).sum()) if not df_legado_blc.empty else 0.0
    total_saldo = float(df_divida["valor_parcela"].sum()) if not df_divida.empty else 0.0
    m1, m2 = st.columns(2)
    m1.metric("Parcelas em aberto", len(df_divida) + len(df_legado_blc))
    m2.metric("Saldo Devedor Total", f"R$ {total_saldo + _leg_saldo_blc:,.2f}")
    st.markdown("---")

    # ── Itens de todas as vendas ──────────────────────────────────────────────
    vendas_ids = df_divida["venda_id"].unique().tolist()
    df_itens_all = run_query(f"""
        SELECT iv.venda_id::text, p.nome AS produto,
               iv.quantidade AS qtd, iv.preco_unit AS unit
        FROM itens_venda iv
        JOIN produtos p ON p.id = iv.produto_id
        WHERE iv.venda_id::text = ANY(ARRAY[{",".join(f"'{v}'" for v in vendas_ids)}])
    """) if vendas_ids else pd.DataFrame()

    # linhas_baixa: [(parc_id, valor_com_juros, vencimento_str)]
    linhas_baixa = []

    # ── Agrupa parcelas por venda ─────────────────────────────────────────────
    for venda_id in vendas_ids:
        parc_venda = df_divida[df_divida["venda_id"] == venda_id]
        data_v  = str(parc_venda["data_venda"].iloc[0])
        forma_v = str(parc_venda["forma_pagamento"].iloc[0])

        hd1, hd2 = st.columns([4, 1])
        hd1.markdown(
            f"<div style='background:#e8f8fa;border-left:4px solid #5bc5d3;"
            f"border-radius:8px;padding:8px 14px;margin:8px 0 4px'>"
            f"<span style='font-size:.8rem;color:#5bc5d3;font-weight:700'>"
            f"Compra de {data_v} · {forma_v}</span></div>",
            unsafe_allow_html=True,
        )
        # ── Ver Itens: expander inline — sem st.rerun() para não resetar a página ──
        with hd2:
            _itens_key = f"blc_show_itens_{venda_id}"
            if st.button(
                "🔼 Fechar" if st.session_state.get(_itens_key) else "📦 Ver Itens",
                key=f"blc_btn_itens_{venda_id}",
                use_container_width=True,
            ):
                st.session_state[_itens_key] = not st.session_state.get(_itens_key, False)
                # sem st.rerun() — o rerun do dialog é automático e não reseta o scroll

        if st.session_state.get(_itens_key, False):
            # Busca o cupom original da venda no banco (pagamentos_balcao ou itens)
            _itens_v = (
                df_itens_all[df_itens_all["venda_id"] == venda_id]
                if not df_itens_all.empty else pd.DataFrame()
            )
            with st.container():
                st.markdown(
                    f"<div style='background:#f0f8ff;border-left:3px solid #5bc5d3;"
                    f"border-radius:6px;padding:8px 12px;margin:4px 0 8px;'>"
                    f"<b style='font-size:.8rem;color:#0077aa'>Itens da compra — {data_v}</b>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                if not _itens_v.empty:
                    # Renderiza cupom com itens + botão de impressão
                    _linhas_it = [
                        f"  📦 {it['produto']}  ×{int(it['qtd'])}"
                        f"  — R$ {float(it['unit']):,.2f}/un"
                        for _, it in _itens_v.iterrows()
                    ]
                    _total_it = float((_itens_v["qtd"] * _itens_v["unit"]).sum())
                    _cupom_it_txt = (
                        f"{'─'*42}\n"
                        f"LOJA GM HOMEM ITAÚNA — Itens da Venda\n"
                        f"Data: {data_v}  |  {forma_v}\n"
                        f"{'─'*42}\n"
                        + "\n".join(_linhas_it)
                        + f"\n{'─'*42}\n"
                        f"TOTAL: R$ {_total_it:,.2f}\n"
                        f"{'─'*42}"
                    )
                    _cupom_it_html = (
                        _cupom_it_txt
                        .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    )
                    _b64_wm2 = _logo_b64()
                    _wm2 = (
                        f"<div style='position:absolute;inset:0;"
                        f"background:url(\"data:image/png;base64,{_b64_wm2}\") center/35% no-repeat;"
                        f"opacity:0.05;pointer-events:none;border-radius:6px;z-index:0;'></div>"
                        if _b64_wm2 else ""
                    )
                    st.markdown(
                        f"<div style='position:relative;background:#fff;border:1px solid #ddd;"
                        f"border-radius:6px;padding:.8rem;'>"
                        f"{_wm2}"
                        f"<pre style='font-family:\"Courier New\",monospace;font-size:.78rem;"
                        f"color:#1a1a1a !important;background:#fff !important;margin:0;white-space:pre;position:relative;z-index:1;'>"
                        f"{_cupom_it_html}</pre></div>",
                        unsafe_allow_html=True,
                    )
                    # Botão de impressão via iframe invisível
                    _b64_it_print = base64.b64encode(
                        _cupom_it_txt.encode("utf-8")
                    ).decode("ascii")
                    components.html(
                        f"""<iframe id="pf_it_{venda_id[:8]}"
                            style="position:absolute;top:-9999px;left:-9999px;
                                   width:1px;height:1px;border:none;"></iframe>
                        <button onclick="imprimirIt_{venda_id[:8].replace('-','_')}()"
                          style="background:linear-gradient(135deg,#1A2035,#c27a9b);
                                 color:#fff;border:none;border-radius:8px;
                                 padding:6px 14px;font-size:.85rem;font-weight:600;
                                 cursor:pointer;margin-top:6px">
                          🖨️ Imprimir
                        </button>
                        <script>
                        function imprimirIt_{venda_id[:8].replace('-','_')}() {{
                            var raw = atob('{_b64_it_print}');
                            try {{ raw = decodeURIComponent(escape(raw)); }} catch(e) {{}}
                            var safe = raw.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
                            var frm = document.getElementById('pf_it_{venda_id[:8]}');
                            var doc = frm.contentDocument || frm.contentWindow.document;
                            doc.open();
                            doc.write('<html><head><style>'
                                + 'body{{margin:4mm;font-family:"Courier New",monospace;'
                                + 'font-size:10pt;white-space:pre-wrap;color:#000;background:#fff;}}'
                                + '</style></head><body>' + safe + '</body></html>');
                            doc.close();
                            frm.contentWindow.focus();
                            frm.contentWindow.print();
                        }}
                        </script>""",
                        height=52,
                    )
                else:
                    st.caption("  (itens não registrados nesta venda)")

        # Parcelas desta venda
        for _, row in parc_venda.iterrows():
            dias      = (hoje - pd.to_datetime(row["data_vencimento"]).date()).days
            juros_val, total_val = calcular_juros(float(row["valor_parcela"]), dias)
            venc_str  = _fmt_data(row["data_vencimento"])
            linhas_baixa.append((row["parc_id"], total_val, venc_str))

            pc1, pc2, pc3, pc4 = st.columns([1.8, 1.5, 1.8, 2])
            pc1.write(venc_str)
            if dias > 0:
                pc2.markdown(
                    f"<span style='color:#CC0000;font-weight:700'>"
                    f"R$ {float(row['valor_parcela']):,.2f}</span>",
                    unsafe_allow_html=True,
                )
                pc3.markdown(f"🔴 +{dias}d  R$ {juros_val:,.2f} juros")
            else:
                pc2.write(f"R$ {float(row['valor_parcela']):,.2f}")
                pc3.write("No prazo")
            if pc4.button(
                "✅ Quitar Parcela",
                key=f"blc_bi_{row['parc_id']}",
                use_container_width=True,
                disabled=not _blc_vnd_ok,
            ):
                ok = run_command(
                    """UPDATE contas_receber
                       SET status='pago', data_pagamento=%s, valor_pago_final=%s
                       WHERE id=%s""",
                    (hoje, total_val, row["parc_id"]),
                )
                if ok:
                    run_command(
                        """INSERT INTO pagamentos_balcao
                               (cliente_nome, valor_abatido, operador, observacao)
                           VALUES (%s, %s, %s, %s)""",
                        (cliente_nome, total_val, username,
                         f"Baixa individual — parcela venc. {venc_str} — vnd: {_blc_cod_vnd}"),
                    )
                    _cup = gerar_cupom_pagamento(
                        cliente_nome, username, total_val,
                        [(venc_str, total_val, "pago")],
                        nome_vendedor=_blc_nome_vnd,
                    )
                    st.session_state[_cupom_key] = _cup
                    st.success(f"Parcela de {venc_str} baixada — R$ {total_val:,.2f}")
                    st.rerun()

    # ── Histórico Legado — parcelas do sistema anterior ───────────────────────
    if not df_legado_blc.empty:
        st.markdown("---")
        st.markdown(
            "<div style='background:#1a2a3a;border-left:4px solid #3498db;"
            "padding:8px 12px;border-radius:6px;margin-bottom:8px'>"
            "<b style='color:#3498db'>📜 Legado — Parcelas do Sistema Anterior</b>"
            f"&nbsp;<span style='color:#aaa;font-size:.82em'>"
            f"{len(df_legado_blc)} parcela(s) · R$ {_leg_saldo_blc:,.2f}</span></div>",
            unsafe_allow_html=True,
        )
        for _, _lg_row in df_legado_blc.iterrows():
            _lg_id   = str(_lg_row["leg_id"])
            _lg_val  = float(_lg_row["valor_docto"] or 0)
            _lg_doc  = str(_lg_row["documento"] or "—")
            _lg_vc   = str(_lg_row["dt_vencimento"] or "—")
            _lg_mod  = str(_lg_row["modalidade"] or "—")
            _lg_bk   = f"blc_leg_baixa_{_lg_id}"
            _lga, _lgb, _lgc, _lgd = st.columns([1.6, 1.2, 1.5, 1.5])
            _lga.caption(f"Doc {_lg_doc} · {_lg_mod}")
            _lgb.caption(f"Venc. {_lg_vc}")
            _lgc.markdown(
                f"<span style='color:#e74c3c;font-weight:700'>R$ {_lg_val:,.2f}</span>",
                unsafe_allow_html=True,
            )
            if _lgd.button(
                "🔼 Fechar" if st.session_state.get(_lg_bk) else "💵 Dar Baixa",
                key=f"blc_leg_btn_{_lg_id}",
                use_container_width=True,
                disabled=not _blc_vnd_ok,
            ):
                st.session_state[_lg_bk] = not st.session_state.get(_lg_bk, False)
            if st.session_state.get(_lg_bk):
                _lbf1, _lbf2, _lbf3 = st.columns([2, 1.2, 1])
                _vr_blc = _lbf1.number_input(
                    "Valor recebido (R$)", min_value=0.01, value=round(_lg_val, 2),
                    step=0.01, key=f"blc_leg_vr_{_lg_id}", label_visibility="collapsed",
                )
                if _lbf2.button("✅ Confirmar Baixa", key=f"blc_leg_conf_{_lg_id}",
                                use_container_width=True, type="primary"):
                    _ok_lg = run_command(
                        "UPDATE historico_legado SET status='baixado', data_baixa=%s,"
                        " baixa_por=%s, valor_recebido=%s, updated_at=now() WHERE id=%s::uuid",
                        (hoje, username, _vr_blc, _lg_id),
                    )
                    if _ok_lg:
                        run_command(
                            "INSERT INTO pagamentos_balcao"
                            " (cliente_nome, valor_abatido, operador, observacao)"
                            " VALUES (%s,%s,%s,%s)",
                            (cliente_nome, _vr_blc, username,
                             f"Baixa legado — Doc {_lg_doc} · venc {_lg_vc} — vnd: {_blc_cod_vnd}"),
                        )
                        st.toast("✅ Baixa legado registrada!", icon="✅")
                        st.session_state.pop(_lg_bk, None)
                        st.rerun()
                    else:
                        st.error("Erro ao registrar baixa.")
                if _lbf3.button("✕", key=f"blc_leg_canc_{_lg_id}", use_container_width=True):
                    st.session_state.pop(_lg_bk, None)
                    st.rerun()

    # ── Rodapé ────────────────────────────────────────────────────────────────
    if not linhas_baixa:
        st.markdown("---")
        st.caption("ℹ️ Todas as parcelas do sistema atual foram quitadas. Legado acima.")
        return
    st.markdown("---")
    total_cobrar = sum(v for _, v, _ in linhas_baixa)

    # ── Isentar juros (alçada gerencial) ─────────────────────────────────────
    _blc_isentar = False
    if st.session_state.get("role") in ("admin", "admin_master"):
        _blc_isentar = st.checkbox(
            "🔓 Isentar juros (Alçada Gerencial)",
            key="blc_isentar_juros",
            help="Zera o acréscimo de juros para todas as parcelas desta baixa.",
        )
        if _blc_isentar:
            # Recalcular sem juros
            linhas_baixa = [(pid, float(run_query(
                f"SELECT valor_parcela FROM contas_receber WHERE id='{pid}'"
            )["valor_parcela"].iloc[0]) if not run_query(
                f"SELECT valor_parcela FROM contas_receber WHERE id='{pid}'"
            ).empty else v, vs) for pid, v, vs in linhas_baixa]
            total_cobrar = sum(v for _, v, _ in linhas_baixa)
            st.caption(f"⚡ Com isenção — Total: R$ {total_cobrar:,.2f}")

    col_ap, col_qt = st.columns(2)

    # ── Baixa por Valor (Amortização Inteligente) ─────────────────────────────
    with col_ap:
        st.markdown("**💡 Baixa por Valor — Amortização Inteligente**")
        st.caption("Valor menor abate a parcela mais antiga e a mantém em aberto com o restante. Valor maior quita e cascateia o excedente.")
        valor_abat = st.number_input(
            "Valor a Abater (R$)",
            min_value=0.01,
            max_value=float(total_cobrar) if total_cobrar > 0 else 0.01,
            value=min(10.0, float(total_cobrar)) if total_cobrar > 0 else 0.01,
            step=10.0,
            key="blc_valor_abatimento",
        )
        if st.button("✅ Aplicar Abatimento", key="blc_abater",
                     use_container_width=True, disabled=not _blc_vnd_ok):
            restante        = round(float(valor_abat), 2)
            detalhes_cupom  = []
            erros           = 0

            for parc_id, valor_parc, venc_str in linhas_baixa:
                if restante <= 0:
                    break
                vp = round(float(valor_parc), 2)
                if restante >= vp:
                    ok = run_command(
                        """UPDATE contas_receber
                           SET status='pago', data_pagamento=%s, valor_pago_final=%s
                           WHERE id=%s""",
                        (hoje, vp, parc_id),
                    )
                    if ok:
                        detalhes_cupom.append((venc_str, vp, "pago"))
                        restante = round(restante - vp, 2)
                    else:
                        erros += 1
                else:
                    novo_valor = round(vp - restante, 2)
                    ok = run_command(
                        """UPDATE contas_receber
                           SET valor_parcela=%s
                           WHERE id=%s""",
                        (novo_valor, parc_id),
                    )
                    if ok:
                        detalhes_cupom.append((venc_str, restante, "parcial"))
                        restante = 0
                    else:
                        erros += 1
                    break

            if erros == 0 and detalhes_cupom:
                run_command(
                    """INSERT INTO pagamentos_balcao
                           (cliente_nome, valor_abatido, operador, observacao)
                       VALUES (%s, %s, %s, %s)""",
                    (cliente_nome, valor_abat, username,
                     f"Abatimento parcial — {len(detalhes_cupom)} parcela(s) — vnd: {_blc_cod_vnd}"),
                )
                _cup = gerar_cupom_pagamento(
                    cliente_nome, username, valor_abat, detalhes_cupom,
                    nome_vendedor=_blc_nome_vnd,
                )
                st.session_state[_cupom_key] = _cup
                st.success(f"✅ Abatimento de R$ {valor_abat:,.2f} aplicado!")
                st.rerun()
            else:
                st.error("Erro ao aplicar abatimento. Tente novamente.")

    # ── Quitação Total ────────────────────────────────────────────────────────
    with col_qt:
        st.markdown(f"**Total a cobrar: R$ {total_cobrar:,.2f}**")
        st.write("")
        if st.button("💰 Quitar Tudo", key="blc_quit_total",
                     use_container_width=True, type="primary",
                     disabled=not _blc_vnd_ok):
            erros          = 0
            detalhes_cupom = []
            for pid, val, venc_str in linhas_baixa:
                ok = run_command(
                    """UPDATE contas_receber
                       SET status='pago', data_pagamento=%s, valor_pago_final=%s
                       WHERE id=%s""",
                    (hoje, val, pid),
                )
                if not ok:
                    erros += 1
                else:
                    detalhes_cupom.append((venc_str, val, "pago"))
            if erros == 0:
                run_command(
                    """INSERT INTO pagamentos_balcao
                           (cliente_nome, valor_abatido, operador, observacao)
                       VALUES (%s, %s, %s, %s)""",
                    (cliente_nome, total_cobrar, username,
                     f"Quitação total — {len(linhas_baixa)} parcela(s) — vnd: {_blc_cod_vnd}"),
                )
                _cup = gerar_cupom_pagamento(
                    cliente_nome, username, total_cobrar, detalhes_cupom,
                    nome_vendedor=_blc_nome_vnd,
                )
                st.session_state[_cupom_key] = _cup
                st.success(f"✅ {len(linhas_baixa)} parcela(s) quitada(s)!")
                st.rerun()
            else:
                st.error(f"{erros} erro(s) ao baixar.")

    # ── Disparo WhatsApp ──────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("📱 Enviar mensagem WhatsApp", expanded=False):
        _blc_msg_default = (
            f"Olá {cliente_nome.split()[0]}! Passando para lembrar sobre "
            f"suas parcelas em aberto na GM Homem. Entre em contato conosco. 💛"
        )
        _blc_msg = st.text_area(
            "Mensagem", value=_blc_msg_default, height=90, key="blc_msg_wpp"
        )
        _col_fone, _col_btn = st.columns([2, 1])
        _blc_fone_edit = _col_fone.text_input(
            "WhatsApp", value=_blc_cli_fone, key="blc_fone_wpp",
            placeholder="5531999990000"
        )
        if _col_btn.button("🚀 Disparar", key="blc_btn_wpp", use_container_width=True):
            _ok, _err = _disparar_whatsapp(
                cliente_id=_blc_cli_id,
                telefone=_blc_fone_edit,
                nome=cliente_nome,
                msg_corpo=_blc_msg,
                vendedora=_blc_nome_vnd or username,
            )
            if _ok:
                st.toast("🚀 Comando enviado ao n8n!", icon="✅")
            else:
                st.error(f"Falha no disparo: {_err}")


# ── Dialog: itens da venda original (drill-down Financeiro) ──────────────────
@st.dialog("Itens da Venda", width="large")
def _dlg_itens_venda(venda_id: str, cliente_nome: str, data_venda: str) -> None:
    """Renderiza o cupom completo da venda (itens + totais) com botão de impressão."""
    # ── Busca dados completos da venda ────────────────────────────────────────
    df_vnd = run_query(f"""
        SELECT v.valor_total, v.forma_pagamento,
               COALESCE(v.codigo_vendedor, v.vendedor_nome, '—') AS vendedor
        FROM vendas v
        WHERE v.id = '{venda_id}'
        LIMIT 1
    """)
    df_it = run_query(f"""
        SELECT p.nome AS produto, iv.quantidade AS qtd,
               iv.preco_unit AS unit,
               (iv.quantidade * iv.preco_unit) AS subtotal
        FROM itens_venda iv
        JOIN produtos p ON p.id = iv.produto_id
        WHERE iv.venda_id = '{venda_id}'
        ORDER BY p.nome
    """)

    if df_it.empty:
        st.info("Nenhum item registrado para esta venda.")
        return

    # ── Monta texto do cupom ──────────────────────────────────────────────────
    W   = 42
    SEP = "─" * W
    valor_total = float(df_vnd["valor_total"].iloc[0]) if not df_vnd.empty else float(df_it["subtotal"].sum())
    forma       = str(df_vnd["forma_pagamento"].iloc[0]).upper() if not df_vnd.empty else "—"
    vendedor    = str(df_vnd["vendedor"].iloc[0]) if not df_vnd.empty else "—"

    def _ctr(s: str) -> str:
        return s.center(W)

    _linhas_cupom = [
        SEP,
        _ctr("LOJA GM HOMEM ITAÚNA"),
        _ctr("Moda Masculina — Itaúna/MG"),
        SEP,
        f"Cliente:   {cliente_nome[:30]}",
        f"Data:      {data_venda}",
        f"Vendedor:  {vendedor[:30]}",
        SEP,
        f"{'PRODUTO':<26}{'QTD':>5}{'UNIT':>6}{'TOTAL':>5}",
        SEP,
    ]
    for _, it in df_it.iterrows():
        nome  = str(it["produto"])[:22]
        qtd   = int(it["qtd"])
        unit  = float(it["unit"])
        sub   = float(it["subtotal"])
        _linhas_cupom.append(
            f"{nome:<22}  {qtd:>3}x {unit:>6,.2f}  {sub:>7,.2f}"
        )
    _linhas_cupom += [
        SEP,
        f"{'TOTAL:':>30}{f'R$ {valor_total:,.2f}':>12}",
        f"PAGAMENTO: {forma}",
        SEP,
        _ctr("Obrigada pela preferência!"),
        _ctr("By JGAutomações.AI"),
        SEP,
        _ctr(f"REF: {venda_id[-8:].upper()}"),
        SEP,
    ]
    _cupom_txt = "\n".join(_linhas_cupom)

    # ── Renderiza cupom via helper centralizado (300px, logo, sem watermark) ──
    st.markdown(_cupom_html_display(_cupom_txt), unsafe_allow_html=True)
    st.write("")
    _, _btn_col, _ = st.columns([1, 2, 1])
    with _btn_col:
        components.html(
            _cupom_iframe_html(_cupom_txt, "pf_dlg", "🖨️ Imprimir Cupom"),
            height=52,
        )


# ══════════════════════════════════════════════════════════════════════════════
# GM HOMEM AI — Inteligência Central (OpenRouter / Groq + SQL direto)
# ══════════════════════════════════════════════════════════════════════════════

# ── Tools Seguras (Fase 1) ────────────────────────────────────────────────────

def _safe_json(dados) -> str:
    """Converte dados para JSON de forma segura, tratando DataFrames e dicts."""
    import json
    if dados is None:
        return "{}"
    if isinstance(dados, pd.DataFrame):
        return dados.to_json(orient='records', force_ascii=False, default_handler=str) if not dados.empty else "[]"
    if isinstance(dados, dict):
        safe = {}
        for k, v in dados.items():
            if isinstance(v, pd.DataFrame):
                safe[k] = v.to_dict('records') if not v.empty else []
            else:
                safe[k] = v
        return json.dumps(safe, ensure_ascii=False, default=str)
    return json.dumps(dados, ensure_ascii=False, default=str)

def _tool_buscar_cliente(nome: str) -> pd.DataFrame:
    """Busca clientes por nome parcial. Retorna id, nome, whatsapp, saldo, última compra, vencidas."""
    return run_query("""
    SELECT c.id::text, c.nome, c.whatsapp,
      (COALESCE((SELECT SUM(da.valor_saldo) FROM duplicatas_abertas da
        WHERE da.nome_cliente ILIKE c.nome AND da.status='Pendente'), 0) +
       COALESCE((SELECT SUM(cr.valor_parcela) FROM contas_receber cr
        JOIN vendas v ON cr.venda_id = v.id
        WHERE v.cliente_id = c.id AND cr.status='aberto'), 0))::float as saldo,
      MAX(v.data_venda::date) as ultima_compra,
      COUNT(cr.id) FILTER (WHERE cr.status='aberto' AND cr.data_vencimento < CURRENT_DATE) as vencidas
    FROM clientes c
    LEFT JOIN vendas v ON v.cliente_id = c.id
    LEFT JOIN contas_receber cr ON cr.venda_id = v.id
    WHERE c.nome ILIKE %(nome)s
    GROUP BY c.id, c.nome, c.whatsapp
    ORDER BY saldo DESC NULLS LAST LIMIT 8
    """, {"nome": f"%{nome}%"})

def _tool_notas_em_atraso(limite: int = 20) -> dict:
    """Retorna resumo + lista de inadimplentes (atraso > 0 dias). Consulta novo + legado."""
    resumo = run_query("""
    SELECT COUNT(DISTINCT cliente) as total_clientes,
           COALESCE(SUM(valor),0)::float as total_valor,
           COUNT(*) as total_parcelas
    FROM (
      SELECT DISTINCT v.cliente_id as cliente, cr.valor_parcela as valor
      FROM contas_receber cr JOIN vendas v ON cr.venda_id = v.id
      WHERE cr.status = 'aberto' AND cr.data_vencimento < CURRENT_DATE
      UNION ALL
      SELECT DISTINCT da.cliente_codigo as cliente, da.valor_saldo as valor
      FROM duplicatas_abertas da
      WHERE da.status = 'Pendente' AND da.dt_vencimento < CURRENT_DATE
    ) merged
    """, {})

    lista = run_query("""
    SELECT nome, whatsapp,
           COALESCE(SUM(valor),0)::float as total_devido,
           MIN(vencimento) as vence_mais_antiga,
           COUNT(*) as qtd_parcelas,
           MAX(CURRENT_DATE - vencimento) as dias_atraso
    FROM (
      SELECT c.nome, c.whatsapp, cr.valor_parcela as valor, cr.data_vencimento as vencimento
      FROM contas_receber cr
      JOIN vendas v ON cr.venda_id = v.id
      JOIN clientes c ON v.cliente_id = c.id
      WHERE cr.status = 'aberto' AND cr.data_vencimento < CURRENT_DATE
      UNION ALL
      SELECT cl.nome, da.contato_whatsapp as whatsapp, da.valor_saldo as valor, da.dt_vencimento as vencimento
      FROM duplicatas_abertas da
      LEFT JOIN clientes_legados cl ON da.cliente_codigo = cl.codigo_legado
      WHERE da.status = 'Pendente' AND da.dt_vencimento < CURRENT_DATE
    ) merged
    GROUP BY nome, whatsapp
    ORDER BY total_devido DESC LIMIT %(limite)s
    """, {"limite": limite})
    return {"resumo": resumo, "lista": lista}

def _tool_historico_cliente(cliente_id: str) -> dict:
    """Retorna histórico completo: resumo + parcelas em aberto (2 fontes)."""
    resumo = run_query("""
    SELECT c.nome, c.whatsapp, c.cpf,
           COUNT(DISTINCT v.id) as total_compras,
           COALESCE(SUM(v.valor_total),0)::float as total_gasto,
           MAX(v.data_venda::date) as ultima_compra,
           COALESCE(AVG(v.valor_total),0)::float as ticket_medio,
           (COALESCE((SELECT SUM(da.valor_saldo) FROM duplicatas_abertas da
             WHERE da.nome_cliente ILIKE c.nome AND da.status='Pendente'), 0) +
            COALESCE((SELECT SUM(cr.valor_parcela) FROM contas_receber cr
             JOIN vendas v ON cr.venda_id = v.id
             WHERE v.cliente_id = c.id AND cr.status='aberto'), 0))::float as saldo_total
    FROM clientes c
    LEFT JOIN vendas v ON v.cliente_id = c.id
    WHERE c.id = %(id)s
    GROUP BY c.id, c.nome, c.whatsapp, c.cpf
    """, {"id": cliente_id})
    parcelas = run_query("""
    SELECT cr.id::text, cr.valor_parcela::float, cr.data_vencimento, cr.status,
           v.numero_documento, v.forma_pagamento
    FROM contas_receber cr
    JOIN vendas v ON cr.venda_id = v.id
    WHERE v.cliente_id = %(id)s AND cr.status = 'aberto'
    ORDER BY cr.data_vencimento ASC LIMIT 10
    """, {"id": cliente_id})
    return {"resumo": resumo, "parcelas": parcelas}

def _tool_relatorio_vendas(periodo: str = "mes") -> pd.DataFrame:
    """Relatório de vendas por período e forma de pagamento."""
    filtros = {
        "hoje":   "v.data_venda::date = CURRENT_DATE",
        "semana": "v.data_venda::date >= CURRENT_DATE - INTERVAL '7 days'",
        "mes":    "DATE_TRUNC('month',v.data_venda)=DATE_TRUNC('month',CURRENT_DATE)",
        "ano":    "DATE_TRUNC('year',v.data_venda)=DATE_TRUNC('year',CURRENT_DATE)",
    }
    filtro = filtros.get(periodo, filtros['mes'])
    return run_query(f"""
    SELECT COUNT(DISTINCT v.id)::int as total_vendas,
           COALESCE(SUM(v.valor_total),0)::float as faturamento,
           COALESCE(AVG(v.valor_total),0)::float as ticket_medio,
           v.forma_pagamento, COUNT(*)::int as qtd_por_forma
    FROM vendas v
    WHERE {filtro}
    GROUP BY v.forma_pagamento ORDER BY qtd_por_forma DESC
    """, {})

def _tool_estoque_baixo(minimo: int = 5) -> pd.DataFrame:
    """Produtos com estoque <= minimo e > 0."""
    return run_query("""
    SELECT nome, codigo_barras, preco_venda::float, estoque_atual::int
    FROM produtos
    WHERE estoque_atual <= %(minimo)s AND estoque_atual > 0 AND ativo IS NOT FALSE
    ORDER BY estoque_atual ASC LIMIT 15
    """, {"minimo": minimo})

def _tool_aniversarios(dias: int = 30) -> pd.DataFrame:
    """Clientes que fazem aniversário nos próximos N dias."""
    return run_query("""
    SELECT nome, whatsapp, data_nascimento,
      EXTRACT(DAY FROM data_nascimento)::int as dia,
      EXTRACT(MONTH FROM data_nascimento)::int as mes
    FROM clientes
    WHERE data_nascimento IS NOT NULL
      AND TO_CHAR(data_nascimento,'MM-DD') BETWEEN
          TO_CHAR(CURRENT_DATE,'MM-DD') AND
          TO_CHAR(CURRENT_DATE + INTERVAL '1 day' * %(dias)s,'MM-DD')
    ORDER BY TO_CHAR(data_nascimento,'MM-DD') LIMIT 20
    """, {"dias": dias})

def _tool_dar_baixa(parcela_id: str) -> dict:
    """Registra pagamento de parcela. Requer confirmação prévia."""
    ok = run_command("""
    UPDATE contas_receber
    SET status='pago', data_pagamento=CURRENT_DATE, updated_at=NOW()
    WHERE id=%(id)s AND status='aberto'
    """, {"id": parcela_id})
    return {"sucesso": ok}

def _tool_variacao_precos(limite: int = 10) -> pd.DataFrame:
    """Relatório de produtos com variação de preço desde a primeira entrada."""
    return run_query("""
    SELECT p.nome, p.codigo_barras,
           p.preco_custo as custo_atual,
           p.preco_venda as venda_atual,
           eh_first.preco_custo as custo_inicial,
           eh_first.preco_venda as venda_inicial,
           COUNT(eh.id) as total_entradas,
           MAX(eh.created_at::date) as ultima_entrada
    FROM produtos p
    JOIN estoque_historico eh ON eh.produto_id = p.id
    JOIN LATERAL (
        SELECT preco_custo, preco_venda
        FROM estoque_historico
        WHERE produto_id = p.id
        ORDER BY created_at ASC LIMIT 1
    ) eh_first ON true
    WHERE (eh.preco_custo != p.preco_custo OR eh.preco_venda != p.preco_venda)
    GROUP BY p.id, p.nome, p.codigo_barras,
             p.preco_custo, p.preco_venda,
             eh_first.preco_custo, eh_first.preco_venda
    ORDER BY MAX(eh.created_at) DESC
    LIMIT %(limite)s
    """, {"limite": limite})

# ── Keywords de Intenção ──────────────────────────────────────────────────────

_INT_ATRASO     = {"atrasad","vencid","inadimpl","devend","atraso","vencida","devedor"}
_INT_RELATORIO  = {"faturamento","vendas","quanto vendeu","relatório","relatorio","receita"}
_INT_ESTOQUE    = {"estoque","produto","faltando","acabou","reposicao"}
_INT_ANIVERSARIO = {"aniversário","aniversario","nascimento","niver"}
_INT_BAIXA      = {"dar baixa","recebeu","pagou","registrar pagamento"}
_INT_PRECOS     = {"variação de preço","variacao de preco","histórico de preço","mudança de preço","preço mudou","reajuste"}

import re as _re
_PATTERN_CLIENTE = _re.compile(
    r'(?:notas?\s+(?:d[aoe]s?\s+)?|cliente\s+|buscar?\s+|ver\s+|historico\s+(?:d[aoe]s?\s+)?)([A-Za-zÀ-ú]{3}[A-Za-zÀ-ú\s]*?)(?:\s*$|\?|\.)',
    _re.IGNORECASE
)

def _detectar_intencao(pergunta: str) -> str:
    """Detecta intenção da pergunta baseado em keywords."""
    p = pergunta.lower()
    if any(k in p for k in _INT_BAIXA):       return "baixa"
    if any(k in p for k in _INT_ATRASO):      return "atraso"
    if any(k in p for k in _INT_RELATORIO):   return "relatorio"
    if any(k in p for k in _INT_ESTOQUE):     return "estoque"
    if any(k in p for k in _INT_ANIVERSARIO): return "aniversario"
    if any(k in p for k in _INT_PRECOS):      return "precos"
    return "cliente"

def _manu_ai_responder(pergunta: str, historico: list) -> dict:
    """Motor do agente: detecta intenção, chama tool, retorna JSON estruturado."""
    ctx = st.session_state.setdefault("manu_ctx", {})
    intent = _detectar_intencao(pergunta)
    dados = None
    tipo = "texto"
    acoes = []

    try:
        if intent == "atraso":
            resultado = _tool_notas_em_atraso(20)
            dados = resultado
            tipo = "atraso"
            ctx["ultima_intencao"] = "atraso"

        elif intent == "relatorio":
            periodo = "mes"
            for p in ["hoje","semana","mes","ano"]:
                if p in pergunta.lower():
                    periodo = p
                    break
            dados = _tool_relatorio_vendas(periodo)
            tipo = "relatorio"

        elif intent == "estoque":
            dados = _tool_estoque_baixo(5)
            tipo = "estoque"

        elif intent == "aniversario":
            dados = _tool_aniversarios(30)
            tipo = "aniversario"

        elif intent == "baixa":
            cid = ctx.get("ultimo_cliente_id")
            if not cid:
                return {"tipo":"texto","dados":None,"texto":"Para dar baixa, primeiro me diga o nome do cliente.","acoes":[]}
            hist_data = _tool_historico_cliente(cid)
            dados = hist_data
            tipo = "historico"

        elif intent == "precos":
            dados = _tool_variacao_precos(10)
            tipo = "variacao_precos"

        else:
            nome_busca = ""

            # Tentar extrair nome com padrão regex: "notas da Maria", "cliente Pamela", etc
            match = _PATTERN_CLIENTE.search(pergunta)
            if match:
                nome_busca = match.group(1).strip()
            else:
                # Fallback: extrair palavras candidatas
                palavras = [w for w in pergunta.split() if len(w) >= 3]
                stopwords = {"que","para","com","uma","umas","uns","ela","ele","tem","seu","sua","dos","das","de"}
                candidatos = [w for w in palavras if w.lower() not in stopwords]
                nome_busca = ctx.get("ultimo_cliente_nome","") if not candidatos else " ".join(candidatos[:3])

            p_lower = pergunta.lower()
            if not nome_busca and any(x in p_lower for x in ["ela","ele","cliente","quanto deve","saldo","nota","parcela"]) and ctx.get("ultimo_cliente_id"):
                hist_data = _tool_historico_cliente(ctx["ultimo_cliente_id"])
                dados = hist_data
                tipo = "historico"
            elif nome_busca:
                resultado = _tool_buscar_cliente(nome_busca)
                if resultado is not None and not resultado.empty:
                    if len(resultado) == 1:
                        ctx["ultimo_cliente_id"]   = resultado.iloc[0]["id"]
                        ctx["ultimo_cliente_nome"] = resultado.iloc[0]["nome"]
                        hist_data = _tool_historico_cliente(resultado.iloc[0]["id"])
                        dados = hist_data
                        tipo = "historico"
                    else:
                        dados = resultado
                        tipo = "clientes_encontrados"
                else:
                    tipo = "texto"
                    dados = None

    except Exception as e:
        tipo = "texto"
        dados = None

    if dados is None:
        dados = {}

    dados_json = _safe_json(dados)
    dados_vazio = (isinstance(dados, dict) and len(dados) == 0) or (isinstance(dados, pd.DataFrame) and dados.empty)

    if dados_vazio or len(dados_json) < 50:
        system = (
            f"Você é a GM Homem, assistente da GM Homem Itaúna. "
            f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}. "
            f"Responda em português, direto e amigável (2-3 linhas max). "
            f"Nenhum dado foi encontrado para essa consulta. "
            f"Responda: 'Não encontrei resultados. Pode ser mais específica? Tente perguntar sobre: clientes em atraso, faturamento, estoque baixo ou aniversários.'"
        )
    else:
        system = (
            f"Você é a GM Homem, gerente de operações da GM Homem Itaúna (moda masculina). "
            f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}. "
            f"Responda em português, direto, amigável. Máximo 3 linhas. "
            f"Use SOMENTE os dados abaixo — NUNCA invente dados ou use placeholders tipo '[Insira...]'.\n\n"
            f"DADOS REAIS DO SISTEMA:\n{dados_json}"
        )

    msgs = historico if isinstance(historico, list) else []
    msgs_truncado = [{"role": m.get("role","user"), "content": str(m.get("content",""))[:400]} for m in msgs[-8:]]
    msgs_truncado.append({"role": "user", "content": pergunta})

    texto = _manu_llm(msgs_truncado, system)

    if tipo == "historico" and ctx.get("ultimo_cliente_id"):
        acoes = [
            {"label":"Ver no CRM","acao":"navegar_crm","param": ctx.get("ultimo_cliente_nome","")},
            {"label":"Ver Recebimentos","acao":"navegar_recebimentos","param": ctx.get("ultimo_cliente_nome","")},
        ]
    elif tipo == "atraso":
        acoes = [{"label":"Abrir Recebimentos","acao":"navegar_recebimentos","param":""}]

    return {"tipo": tipo, "dados": dados, "texto": texto, "acoes": acoes}


# ── Código antigo removido na refatoração GM Homem AI v2 ──────────────────────

# Início do código legado deletado para agente v2
def _q_check(nome_fragmento):
    """Verifica se existe cliente com este nome no banco"""
    try:
        from sqlalchemy import create_engine, text
        import pandas as _pd
        _env = {}
        try:
            with open('/opt/jg-projetos/loja-gmh/.env') as _f:
                for _l in _f:
                    _l = _l.strip()
                    if '=' in _l and not _l.startswith('#'):
                        _k, _v = _l.split('=', 1)
                        _env[_k.strip()] = _v.strip().strip('"').strip("'")
        except: pass
        _url = (f"postgresql://{_env.get('DB_USER','jgadmin')}:"
                f"{_env.get('DB_PASS','JGroot2026')}@"
                f"{_env.get('DB_HOST','127.0.0.1')}:"
                f"{_env.get('DB_PORT','5432')}/"
                f"{_env.get('DB_NAME','gmh_db')}")
        _eng = create_engine(_url)
        with _eng.connect() as _con:
            _df = _pd.read_sql_query(
                text(f"SELECT COUNT(*) as n FROM duplicatas_abertas "
                     f"WHERE status='Pendente' AND "
                     f"UPPER(COALESCE(nome_cliente,'')) LIKE UPPER('%{nome_fragmento}%')"),
                _con)
        return int(_df.iloc[0]['n']) > 0 if not _df.empty else False
    except:
        return False


def render_manu_ai(perfil: str) -> None:
    """GM Homem AI v2 — Agente com tools estruturadas e UI limpa."""

    # Header
    col_h, col_clr = st.columns([0.9, 0.1])
    col_h.markdown("### ✨ GM Homem AI — Agente v2")
    if col_clr.button("🗑️", key="manu_clr", help="Limpar conversa"):
        st.session_state['manu_msgs'] = []
        st.rerun()

    if 'manu_msgs' not in st.session_state:
        st.session_state['manu_msgs'] = []

    st.divider()

    # Histórico de chat
    for msg in st.session_state['manu_msgs']:
        if msg['role'] == 'user':
            with st.chat_message("user"):
                st.write(msg['content'])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                dados_msg = msg.get('_dados', {})
                tipo_msg = msg.get('_tipo', 'texto')

                # Renderização por tipo
                if tipo_msg == 'atraso' and isinstance(dados_msg, dict):
                    resumo = dados_msg.get('resumo')
                    if resumo is not None and not resumo.empty:
                        r = resumo.iloc[0]
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Em atraso", int(r.get('total_clientes', 0)))
                        col2.metric("Total devido", f"R$ {float(r.get('total_valor', 0)):,.2f}")
                        col3.metric("Parcelas", int(r.get('total_parcelas', 0)))

                    lista = dados_msg.get('lista')
                    if lista is not None and not lista.empty:
                        st.dataframe(lista[['nome','total_devido','dias_atraso']], use_container_width=True, hide_index=True)

                elif tipo_msg == 'historico' and isinstance(dados_msg, dict):
                    resumo = dados_msg.get('resumo')
                    if resumo is not None and not resumo.empty:
                        r = resumo.iloc[0]
                        st.write(f"**{r.get('nome', 'Cliente')}** — {int(r.get('total_compras', 0))} compras")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Total gasto", f"R$ {float(r.get('total_gasto', 0)):,.2f}")
                        col2.metric("Saldo devido", f"R$ {float(r.get('saldo_total', 0)):,.2f}")
                        ultima = r.get('ultima_compra')
                        col3.metric("Última compra", str(ultima) if ultima else "Sem compras")

                    parcelas = dados_msg.get('parcelas')
                    if parcelas is not None and not parcelas.empty:
                        st.write("**Parcelas em aberto:**")
                        st.dataframe(parcelas[['data_vencimento','valor_parcela','status']], use_container_width=True, hide_index=True)

                elif tipo_msg == 'estoque' and isinstance(dados_msg, pd.DataFrame):
                    if not dados_msg.empty:
                        st.write("**Produtos com estoque baixo:**")
                        st.dataframe(dados_msg[['nome','estoque_atual','preco_venda']], use_container_width=True, hide_index=True)

                elif tipo_msg == 'aniversario' and isinstance(dados_msg, pd.DataFrame):
                    if not dados_msg.empty:
                        st.write("**Aniversariantes:**")
                        st.dataframe(dados_msg[['nome','dia','mes']], use_container_width=True, hide_index=True)

                elif tipo_msg == 'clientes_encontrados' and isinstance(dados_msg, pd.DataFrame):
                    if not dados_msg.empty:
                        st.write("**Clientes encontrados:**")
                        for idx, row in dados_msg.iterrows():
                            col_nome, col_saldo, col_status, col_btn = st.columns([3, 2, 1, 1.5])
                            col_nome.write(f"**{row['nome']}**")
                            col_saldo.write(f"R$ {float(row['saldo'] or 0):,.2f}")
                            tem_atraso = float(row.get('vencidas', 0) or 0) > 0
                            col_status.write('🔴' if tem_atraso else '🟢')
                            if col_btn.button("Ver notas →", key=f"btn_rec_{row['id']}_{idx}"):
                                st.session_state['menu'] = 'Recebimentos'
                                st.session_state['_filtro_rapido_rec'] = row['nome']
                                st.rerun()

                elif tipo_msg == 'relatorio' and isinstance(dados_msg, pd.DataFrame):
                    if not dados_msg.empty:
                        total_fat = float(dados_msg['faturamento'].sum()) if 'faturamento' in dados_msg.columns else 0
                        col1, col2 = st.columns(2)
                        col1.metric("Vendas", int(len(dados_msg)))
                        col2.metric("Faturamento", f"R$ {total_fat:,.2f}")
                        st.dataframe(dados_msg[['forma_pagamento','faturamento','qtd_por_forma']], use_container_width=True, hide_index=True)

                elif tipo_msg == 'variacao_precos' and isinstance(dados_msg, pd.DataFrame):
                    if not dados_msg.empty:
                        st.write("**Variação de preços:**")
                        for _, row in dados_msg.iterrows():
                            prod_nome = row.get('nome', '?')
                            custo_ini = float(row.get('custo_inicial') or 0)
                            custo_atu = float(row.get('custo_atual') or 0)
                            venda_ini = float(row.get('venda_inicial') or 0)
                            venda_atu = float(row.get('venda_atual') or 0)
                            entradas = int(row.get('total_entradas') or 0)
                            ultima = row.get('ultima_entrada')

                            col_p, col_c, col_v = st.columns([2, 2, 2])
                            col_p.write(f"**{prod_nome}**  \n{entradas} entradas")
                            col_c.write(f"Custo: R$ {custo_ini:,.2f} → R$ {custo_atu:,.2f}")
                            col_v.write(f"Venda: R$ {venda_ini:,.2f} → R$ {venda_atu:,.2f}")

                # Resposta textual
                st.write(msg.get('content', ''))

    # Input (Streamlit coloca no rodapé automaticamente)
    prompt = st.chat_input("Pergunte: 'clientes em atraso', 'Maria', 'faturamento'...", key='manu_input')

    if prompt:
        st.session_state['manu_msgs'].append({'role':'user','content':prompt})
        resposta = _manu_ai_responder(prompt, st.session_state['manu_msgs'][:-1])
        msg_assistant = {
            'role':'assistant',
            'content':resposta.get('texto',''),
            '_dados':resposta.get('dados',{}),
            '_tipo':resposta.get('tipo','texto')
        }
        st.session_state['manu_msgs'].append(msg_assistant)
        st.rerun()


_GMH_SYSTEM = """Você é a GM Homem, Gerente de Operações da GM Homem Itaúna.
Fale como uma pessoa experiente — direta, profissional e humana. Nunca como um robô ou sistema.

IDENTIDADE (nunca quebre estas regras):
- NUNCA mostre código SQL, nomes de tabelas, campos do banco ou linguagem técnica nas respostas.
- NUNCA diga "Sou um modelo de IA", "não tenho acesso" ou qualquer variação.
- Se não souber algo, diga: "Não encontrei esse dado. Pode ser mais específica?" e sugira como reformular.
- Se a pergunta for vaga (ex: "como está a loja?"), pergunte o que a pessoa quer: estoque crítico, clientes em atraso, faturamento ou outra coisa.

COMO RESPONDER:
- Máximo 3 parágrafos curtos ou uma lista objetiva. Sem rodeios.
- Comece pela informação mais importante. Nunca repita a pergunta.
- Use linguagem de gestão: "temos X peças", "a inadimplência está em R$...", "o estoque de Y está crítico".
- Para listas grandes, mostre os 10 mais relevantes e informe o total.
- Quando encontrar múltiplos clientes com o mesmo nome, liste-os numerados e peça ao usuário escolher.
- No final da resposta, se houver ação disponível (ver financeiro, ver histórico), INDIQUE que o botão de ação aparecerá logo abaixo.

PROIBIDO nas respostas: SELECT, FROM, WHERE, JOIN, TABLE, NULL, ILIKE, UUID, qualquer código.

FOCO EXCLUSIVO (regra inquebrável):
Você é a Gerente Digital da GM Homem Itaúna. Seu conhecimento é restrito ao banco de dados da loja e ao varejo de moda masculina. Recuse com elegância qualquer assunto fora desse domínio — política, culinária, tecnologia geral, entretenimento, etc. Responda: "Minha especialidade é a GM Homem — posso te ajudar com estoque, clientes, vendas ou financeiro da loja. Tem algo nisso que posso resolver agora?" """

_GMH_TABELAS_CTX = """
Banco PostgreSQL — GM Homem Itaúna (roupas femininas).

VIEWS PRINCIPAIS (use SEMPRE estas — já unem banco novo + sistema legado):

1. vw_clientes_completos — TODOS os clientes (legados + novos)
   Colunas: id, nome, cpf, celular, data_cadastro, cidade, origem,
            ultima_compra, total_gasto, codigo_legado
   USE para: buscar clientes por nome/CPF, histórico, inadimplência

2. vw_recebiveis — TODAS as parcelas em aberto (legado + novo)
   Colunas: id, nome_cliente, cpf, cliente_id, documento, dt_emissao,
            dt_vencimento, valor_saldo, status, modalidade,
            origem (banco|legado), observacao, dias_atraso
   USE para: dívidas, vencidos, cobranças, crediário

3. vw_estoque_completo — Produtos com status de estoque
   Colunas: id, nome, categoria, preco_venda, preco_custo,
            quantidade_atual, status_estoque, ativo
   USE para: consultas de estoque, reposição, produtos em falta

TABELAS DIRETAS (para queries mais detalhadas):

4. clientes(id, nome, cpf, whatsapp, data_nascimento, ativo, codigo_externo)
5. vendas(id, cliente_id, valor_total, forma_pagamento, status_pagamento, data_venda, vendedor_nome)
6. itens_venda(id, venda_id, produto_id, quantidade, preco_unit)
7. produtos(id, nome, categoria, preco_venda, preco_custo, estoque_atual, estoque_minimo)
8. contas_receber(id, venda_id, valor_parcela, data_vencimento, status, nr_documento)
9. historico_legado(cliente_id, documento, dt_emissao, modalidade, valor_docto, status)
10. duplicatas_abertas(codigo_cliente, nome_cliente, documento, dt_vencimento, valor_saldo, status, modalidade)

REGRAS DE CONSULTA:
- SEMPRE buscar clientes em vw_clientes_completos (não em clientes isolado)
- SEMPRE buscar parcelas/dívidas em vw_recebiveis
- Para dívidas de um cliente: WHERE UPPER(nome_cliente) LIKE UPPER('%nome%')
- Valores: formatar como R$ X.XXX,XX
- Máximo 20 linhas por resposta
- NUNCA: DELETE, UPDATE, INSERT, DROP, ALTER
"""


def _manu_llm(messages: list[dict], system: str = _GMH_SYSTEM) -> str:
    """Chama Qwen 2.5-Coder via OpenRouter (fallback: Groq llama3).

    max_tokens=1000  — evita respostas truncadas em análises maiores.
    timeout=45s      — tempo generoso para o modelo raciocinar sem travar.
    try/except robusto — retorna mensagem amigável em qualquer falha.
    """
    _MSG_ERRO = (
        "Tive um problema ao processar esses dados, pode repetir? "
        "Se o erro persistir, tente uma pergunta mais específica."
    )
    or_key = os.getenv("OPENROUTER_API_KEY", "")
    gr_key = os.getenv("GROQ_API_KEY", "")

    if or_key:
        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json={
                    "model": "qwen/qwen-2.5-coder-32b-instruct",
                    "messages": [{"role": "system", "content": system}] + messages,
                    "max_tokens": 1000,
                    "temperature": 0.2,
                },
                headers={
                    "Authorization": f"Bearer {or_key}",
                    "HTTP-Referer": "https://loja-gmh.com",
                    "Content-Type": "application/json",
                },
                timeout=45,
            )
            if r.status_code == 200:
                _registrar_tokens_ia(messages[-1]["content"], "")
                return r.json()["choices"][0]["message"]["content"]
            if r.status_code == 429:
                return "⏳ Limite de requisições atingido. Aguarde alguns segundos e tente novamente."
            if r.status_code in (401, 403):
                return "🔑 Chave OpenRouter inválida ou expirada. Acesse **⚡ JG Hub → IA & API** para atualizar."
            return f"{_MSG_ERRO} (OpenRouter status {r.status_code})"
        except requests.exceptions.Timeout:
            return "⏱️ A resposta demorou demais. Tente uma pergunta mais curta ou mais específica."
        except requests.exceptions.ConnectionError:
            return "📡 Sem conexão com o servidor de IA. Verifique a internet e tente novamente."
        except Exception:
            return _MSG_ERRO

    if gr_key:
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                json={
                    "model": "llama3-8b-8192",
                    "messages": [{"role": "system", "content": system}] + messages,
                    "max_tokens": 1000,
                    "temperature": 0.2,
                },
                headers={
                    "Authorization": f"Bearer {gr_key}",
                    "Content-Type": "application/json",
                },
                timeout=45,
            )
            if r.status_code == 200:
                _registrar_tokens_ia(messages[-1]["content"], "")
                return r.json()["choices"][0]["message"]["content"]
            if r.status_code == 429:
                return "⏳ Limite de requisições Groq atingido. Aguarde e tente novamente."
            return f"{_MSG_ERRO} (Groq status {r.status_code})"
        except requests.exceptions.Timeout:
            return "⏱️ A resposta demorou demais. Tente uma pergunta mais curta ou mais específica."
        except requests.exceptions.ConnectionError:
            return "📡 Sem conexão com o servidor de IA. Verifique a internet e tente novamente."
        except Exception:
            return _MSG_ERRO

    return ("⚠️ Nenhuma API key configurada. "
            "Acesse **⚡ JG Hub → IA & API** e salve sua OpenRouter API Key.")


def _manu_detectar_intent(txt: str) -> str:
    t = txt.lower()
    if re.search(r'\b(parcela|devendo|em aberto|conta de|saldo de|quanto deve|dívida|divida|débito|debito)\b', t):
        return "parcelas"
    if re.search(r'\b(pedido|venda\s*n[oº°]?\.?\s*\d|cupom|nota\s*\d|compra\s*\d)\b', t):
        return "detalhe_venda"
    if re.search(r'\b(em\s+atraso|inadimplente|atrasad[ao]|vencid[ao]|cobran[cç]a)\b', t):
        return "lista_atraso"
    if re.search(r'\b(aniversarian|aniversár|aniversar|faz\s*aniver)\b', t):
        return "lista_aniversariantes"
    if re.search(r'\b(inativ[ao]|sem\s+comprar|sumiram|sumiram|reativar|nao\s+compra|não\s+compra)\b', t):
        return "lista_inativos"
    if re.search(r'\b(compras?\s+sugerid|o\s+que\s+comprar|repor\s+estoque|acabando|giro\s+de\s+estoque|sugestão\s+de\s+compra|sugestao\s+de\s+compra|o\s+que\s+está\s+acabando)\b', t):
        return "sugestao_compras"
    if re.search(r'\b(estoque|tem\s+em|disponível|quantos?\s+tem|restam|sobraram)\b', t):
        return "estoque"
    if re.search(r'\b(faturamento|vendas?\s+(hoje|mês|mes)|receita|resumo\s+do\s+dia)\b', t):
        return "faturamento"
    if re.search(r'\b(listar?\s+clientes?|lista\s+de\s+clientes?|todos\s+os\s+clientes?|quem\s+s[aã]o\s+os\s+clientes?|clientes?\s+cadastrados?|base\s+de\s+clientes?)\b', t):
        return "lista_clientes"
    return "livre"


def _manu_resp_parcelas(nome_cliente: str) -> dict:
    """Retorna dict com df de parcelas e metadados para renderização.

    Regra de busca: se o nome bater em múltiplos clientes distintos,
    retorna lista de opções para o usuário escolher em vez de misturar dados.
    """
    # Verifica quantos clientes distintos correspondem ao nome informado
    _nome_safe = nome_cliente.lower().replace("'", "''")
    df_clientes = run_query(f"""
        SELECT DISTINCT nome, celular AS whatsapp, cliente_id
        FROM vw_recebiveis
        WHERE LOWER(nome_cliente) ILIKE '%{_nome_safe}%'
        ORDER BY nome
        LIMIT 20
    """)

    if df_clientes.empty:
        return {
            "tipo": "texto",
            "content": (
                f"Nenhum cliente encontrado com o nome **\"{nome_cliente}\"**. "
                "Tente um trecho diferente do nome ou verifique o cadastro."
            ),
        }

    if len(df_clientes) > 1:
        # Múltiplos clientes — lista as opções para o usuário escolher
        opcoes = "\n".join(
            f"{i + 1}. **{row['nome']}**"
            for i, (_, row) in enumerate(df_clientes.iterrows())
        )
        return {
            "tipo": "texto",
            "content": (
                f"Encontrei **{len(df_clientes)} clientes** com o nome "
                f"**\"{nome_cliente}\"**. Por favor, informe o nome completo:\n\n"
                f"{opcoes}"
            ),
        }

    # Cliente único — busca parcelas via view unificada
    df = run_query(f"""
        SELECT
            id,
            nome_cliente AS nome,
            '' AS whatsapp,
            cliente_id,
            valor_saldo AS valor_parcela,
            dt_vencimento AS data_vencimento,
            status,
            dias_atraso,
            documento AS venda_id
        FROM vw_recebiveis
        WHERE LOWER(nome_cliente) ILIKE '%{_nome_safe}%'
        ORDER BY dt_vencimento ASC
        LIMIT 50
    """)
    return {"tipo": "parcelas", "df": df, "nome": nome_cliente}


def _manu_resp_detalhe_venda(termo: str) -> dict:
    """Busca itens de uma venda pelo ID parcial ou número sequencial."""
    nums = re.sub(r"\D", "", termo)
    if not nums:
        return {"tipo": "erro", "msg": "Número de pedido não identificado."}
    df_v = run_query(f"""
        SELECT v.id::text AS venda_id,
               c.nome AS cliente,
               v.valor_total,
               v.forma_pagamento,
               v.data_venda,
               v.vendedor_nome
        FROM vendas v
        JOIN clientes c ON c.id = v.cliente_id
        WHERE v.id::text LIKE '%{nums}%'
           OR CAST(ROW_NUMBER() OVER (ORDER BY v.data_venda) AS TEXT) = '{nums}'
        ORDER BY v.data_venda DESC
        LIMIT 1
    """)
    if df_v.empty:
        return {"tipo": "erro", "msg": f"Venda com referência **{nums}** não encontrada."}
    vid = df_v["venda_id"].iloc[0]
    df_it = run_query(f"""
        SELECT p.nome AS produto, iv.quantidade AS qtd,
               iv.preco_unit, (iv.quantidade * iv.preco_unit) AS subtotal
        FROM itens_venda iv
        JOIN produtos p ON p.id = iv.produto_id
        WHERE iv.venda_id = '{vid}'
        ORDER BY p.nome
    """)
    return {"tipo": "detalhe_venda", "venda": df_v.iloc[0].to_dict(), "itens": df_it}


def _manu_resp_lista(tipo: str) -> dict:
    if tipo == "atraso":
        df = run_query("""
            SELECT
                nome_cliente AS nome,
                '' AS whatsapp,
                COALESCE(cliente_id, '') AS cliente_id,
                COUNT(id) AS parcelas,
                COALESCE(SUM(valor_saldo), 0) AS total,
                MAX(dias_atraso) AS max_dias
            FROM vw_recebiveis
            WHERE dias_atraso > 0
            GROUP BY nome_cliente, cliente_id
            ORDER BY total DESC
            LIMIT 50
        """)
        return {"tipo": "lista", "subtipo": "atraso", "df": df,
                "titulo": "🔴 Clientes em Atraso"}
    elif tipo == "aniversariantes":
        df = run_query("""
            SELECT nome, whatsapp, id::text AS cliente_id,
                   TO_CHAR(data_nascimento, 'DD/MM') AS dia_mes,
                   EXTRACT(MONTH FROM data_nascimento)::int AS mes,
                   EXTRACT(DAY FROM data_nascimento)::int AS dia
            FROM clientes
            WHERE ativo = true
              AND data_nascimento IS NOT NULL
              AND EXTRACT(MONTH FROM data_nascimento) = EXTRACT(MONTH FROM CURRENT_DATE)
            ORDER BY EXTRACT(DAY FROM data_nascimento)
            LIMIT 60
        """)
        return {"tipo": "lista", "subtipo": "aniversariantes", "df": df,
                "titulo": "🎂 Aniversariantes do Mês"}
    else:  # inativos
        df = run_query("""
            SELECT c.nome, c.whatsapp, c.id::text AS cliente_id,
                   MAX(v.data_venda)::date AS ultima_compra,
                   (CURRENT_DATE - MAX(v.data_venda)::date) AS dias_sem_comprar
            FROM clientes c
            JOIN vendas v ON v.cliente_id = c.id
            WHERE c.ativo = true
            GROUP BY c.nome, c.whatsapp, c.id
            HAVING MAX(v.data_venda)::date < CURRENT_DATE - INTERVAL '60 days'
            ORDER BY dias_sem_comprar DESC
            LIMIT 50
        """)
        return {"tipo": "lista", "subtipo": "inativos", "df": df,
                "titulo": "😴 Clientes Inativos (+60 dias)"}


def _manu_resp_sugestao_compras() -> dict:
    df = run_query("""
        SELECT p.nome,
               p.categoria,
               p.estoque_atual,
               p.estoque_minimo,
               COALESCE(SUM(iv.quantidade), 0) AS vendidos_30d,
               COALESCE(SUM(iv.quantidade) / 30.0, 0) AS giro_diario,
               CASE
                 WHEN p.estoque_minimo IS NOT NULL AND p.estoque_atual <= p.estoque_minimo THEN '🔴 Crítico'
                 WHEN COALESCE(SUM(iv.quantidade), 0) >= 5 AND p.estoque_atual <= 3 THEN '🟠 Atenção'
                 ELSE '🟢 OK'
               END AS situacao
        FROM produtos p
        LEFT JOIN itens_venda iv ON iv.produto_id = p.id
        LEFT JOIN vendas v ON v.id = iv.venda_id
            AND v.data_venda >= CURRENT_DATE - INTERVAL '30 days'
        WHERE p.ativo IS NOT FALSE
        GROUP BY p.id, p.nome, p.categoria, p.estoque_atual, p.estoque_minimo
        ORDER BY
            CASE WHEN p.estoque_minimo IS NOT NULL AND p.estoque_atual <= p.estoque_minimo THEN 0
                 WHEN COALESCE(SUM(iv.quantidade), 0) >= 5 AND p.estoque_atual <= 3 THEN 1
                 ELSE 2 END,
            vendidos_30d DESC
        LIMIT 30
    """)
    return {"tipo": "sugestao_compras", "df": df}


def _manu_resp_lista_clientes() -> dict:
    """Lista clientes ativos — validação de IA e resposta a 'listar clientes'."""
    df = run_query("""
        SELECT c.nome,
               c.whatsapp,
               c.id::text AS cliente_id,
               COUNT(v.id) AS total_compras,
               COALESCE(SUM(v.valor_total), 0) AS total_gasto,
               MAX(v.data_venda)::date AS ultima_compra
        FROM clientes c
        LEFT JOIN vendas v ON v.cliente_id = c.id
        WHERE c.ativo IS NOT FALSE
        GROUP BY c.nome, c.whatsapp, c.id
        ORDER BY total_gasto DESC
        LIMIT 50
    """)
    return {"tipo": "lista", "subtipo": "clientes", "df": df,
            "titulo": "👥 Clientes Ativos (Top 50 por volume)"}


# ── Reset de Banco para Produção ──────────────────────────────────────────────
# ATENÇÃO: função DESTRUTIVA — use apenas após backup confirmado.
# Limpa transações, vendas e estoque. Mantém estrutura e usuários do sistema.

def reset_banco_para_producao() -> tuple[bool, str]:
    """Limpa todas as transações, vendas e estoque para início de produção.

    SEGURANÇA: só pode ser chamada explicitamente por um admin_master.
    Mantém intactos: clientes, produtos (estrutura/cadastro), config_geral,
    usuários de sistema e metas_mensais.

    Retorna (sucesso: bool, mensagem: str).
    """
    _SQL_RESET = """
    BEGIN;
    -- Limpa registros financeiros e de vendas (ordem respeita FK)
    DELETE FROM contas_receber;
    DELETE FROM contas_a_pagar;
    DELETE FROM itens_venda;
    DELETE FROM trocas_itens;
    DELETE FROM trocas;
    DELETE FROM vendas;
    -- Zera estoque de todos os produtos (mantém cadastro)
    UPDATE produtos SET estoque_atual = 0, ultima_entrada = NULL;
    -- Limpa histórico de preços
    DELETE FROM historico_precos;
    -- Limpa log de tokens de IA
    DELETE FROM log_tokens_ia;
    COMMIT;
    """
    try:
        with _db_get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(_SQL_RESET)
        return True, (
            "✅ Reset concluído. Vendas, contas e estoque foram zerados. "
            "Cadastro de clientes, produtos e configurações foi preservado."
        )
    except Exception as e:
        return False, f"❌ Falha no reset: {e}"


def _manu_processar(prompt: str, role: str, username: str) -> dict:
    """Processa prompt da GM Homem AI e retorna dict com tipo + dados."""
    intent = _manu_detectar_intent(prompt)

    if intent == "parcelas":
        nome = _chat_extrair_nome(prompt) or prompt
        return _manu_resp_parcelas(nome)

    if intent == "detalhe_venda":
        return _manu_resp_detalhe_venda(prompt)

    if intent == "lista_atraso":
        return _manu_resp_lista("atraso")

    if intent == "lista_aniversariantes":
        return _manu_resp_lista("aniversariantes")

    if intent == "lista_inativos":
        return _manu_resp_lista("inativos")

    if intent == "sugestao_compras":
        return _manu_resp_sugestao_compras()

    if intent == "lista_clientes":
        return _manu_resp_lista_clientes()

    if intent == "estoque":
        nome_prod = _chat_extrair_produto(prompt) or prompt
        df = run_query(f"""
            SELECT nome, categoria, estoque_atual, estoque_minimo, preco_venda
            FROM produtos
            WHERE LOWER(nome) ILIKE '%{nome_prod.lower()}%'
              AND ativo IS NOT FALSE
            ORDER BY nome LIMIT 10
        """)
        if df.empty:
            return {"tipo": "texto", "content": f"Nenhum produto encontrado para **{nome_prod}**."}
        rows = "\n".join(
            f"- **{r['nome']}**: {int(r['estoque_atual'])} un. (mín. {int(r['estoque_minimo']) if pd.notna(r['estoque_minimo']) else '—'})"
            for _, r in df.iterrows()
        )
        return {"tipo": "texto", "content": f"📦 **Estoque — {nome_prod}**\n\n{rows}"}

    if intent == "faturamento":
        df = run_query("""
            SELECT COALESCE(SUM(CASE WHEN data_venda::date = CURRENT_DATE THEN valor_total END), 0) AS hoje,
                   COALESCE(SUM(CASE WHEN DATE_TRUNC('month', data_venda) = DATE_TRUNC('month', CURRENT_DATE) THEN valor_total END), 0) AS mes,
                   COUNT(CASE WHEN data_venda::date = CURRENT_DATE THEN 1 END) AS qtd_hoje
            FROM vendas WHERE status_pagamento IN ('pago','parcelado')
        """)
        if not df.empty:
            r = df.iloc[0]
            txt = (
                f"📊 **Faturamento**\n\n"
                f"- Hoje: **R$ {float(r['hoje']):,.2f}** ({int(r['qtd_hoje'])} vendas)\n"
                f"- Mês atual: **R$ {float(r['mes']):,.2f}**"
            )
        else:
            txt = "Nenhum dado de faturamento disponível."
        return {"tipo": "texto", "content": txt}

    # Intent "livre" — resposta via LLM com contexto SQL básico
    ctx_sql = ""
    try:
        df_ctx = run_query("""
            SELECT
              (SELECT COUNT(*) FROM clientes WHERE ativo = true) AS clientes,
              (SELECT COALESCE(SUM(valor_total),0) FROM vendas
               WHERE data_venda::date = CURRENT_DATE
                 AND status_pagamento IN ('pago','parcelado')) AS fat_hoje,
              (SELECT COUNT(*) FROM contas_receber WHERE status='aberto'
               AND data_vencimento < CURRENT_DATE) AS parc_vencidas
        """)
        if not df_ctx.empty:
            r = df_ctx.iloc[0]
            ctx_sql = (
                f"\n\nContexto atual: {int(r['clientes'])} clientes ativos, "
                f"faturamento hoje R$ {float(r['fat_hoje']):,.2f}, "
                f"{int(r['parc_vencidas'])} parcelas vencidas."
            )
    except Exception:
        pass

    resp = _manu_llm(
        [{"role": "user", "content": prompt + ctx_sql}],
        system=_GMH_SYSTEM + "\n" + _GMH_TABELAS_CTX,
    )
    return {"tipo": "texto", "content": resp}


def _manu_render_action_button(
    label: str,
    cliente_nome: str,
    key: str,
    action: str = "financeiro",
) -> None:
    """Botão de ação contextual gerado pela GM Homem AI após exibir dados.

    Navega para a aba correta e pré-aplica o filtro do cliente automaticamente,
    para que o usuário chegue exatamente onde precisa sem digitar nada.

    action="financeiro" → Recebimentos → Auditoria, filtro pré-preenchido.
    action="historico"  → Recebimentos → Histórico de Vendas, filtro pré-preenchido.
    """
    _ACTIONS: dict[str, tuple[str, str]] = {
        "financeiro": ("Recebimentos", "fin_receber_busca"),
        "historico":  ("Recebimentos", "fin_hist_busca"),
    }
    destino, filtro_key = _ACTIONS.get(action, ("Recebimentos", "fin_receber_busca"))

    # Botão inline no contexto de chat — sem quebrar o visual de mensagem
    st.markdown(
        "<div style='margin-top:8px'>",
        unsafe_allow_html=True,
    )
    if st.button(label, key=key, use_container_width=False):
        st.session_state["_nav_target"] = destino
        if cliente_nome:
            st.session_state[filtro_key] = cliente_nome
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _manu_render_resultado(res: dict, chat_key: str, username: str) -> None:
    """Renderiza o resultado estruturado da GM Homem AI."""
    tipo = res.get("tipo", "texto")

    if tipo == "texto":
        st.markdown(res.get("content", ""))
        return

    if tipo == "erro":
        st.markdown(res.get("msg", res.get("content", "Não consegui processar essa consulta.")))
        return

    if tipo == "parcelas":
        df: pd.DataFrame = res["df"]
        nome = res["nome"]
        if df.empty:
            st.markdown(
                f"Não encontrei nenhuma parcela em aberto para **{nome}**. "
                "Pode ser que ela esteja quite ou com nome diferente no cadastro."
            )
        else:
            nome_real = df["nome"].iloc[0]
            wpp       = str(df["whatsapp"].iloc[0] or "")
            cli_id    = str(df["cliente_id"].iloc[0])
            total     = float(df["valor_parcela"].sum())
            _primeiro = nome_real.split()[0]
            st.markdown(
                f"**{nome_real}** tem **{len(df)} parcela(s)** em aberto, "
                f"somando **R$ {total:,.2f}**:"
            )
            df_show = df[["valor_parcela", "data_vencimento", "status", "dias_atraso"]].copy()
            df_show.columns = ["Valor", "Vencimento", "Status", "Dias Atraso"]
            df_show["Valor"] = df_show["Valor"].apply(lambda x: f"R$ {float(x):,.2f}")
            st.dataframe(df_show, hide_index=True, use_container_width=True)
            _c1, _c2 = st.columns(2)
            # Botão de ação: navega ao Financeiro e pré-filtra pelo nome do cliente
            with _c1:
                _primeiro_nome = nome_real.split()[0]
                _manu_render_action_button(
                    f"📂 Acessar Financeiro de {_primeiro_nome}",
                    nome_real,
                    key=f"manu_fin_{chat_key}_{nome[:6]}",
                    action="financeiro",
                )
            if wpp and _c2.button("📲 WhatsApp", key=f"manu_wpp_p_{chat_key}_{nome[:6]}",
                                  use_container_width=True):
                _msg = (f"Olá {nome_real.split()[0]}! Você tem {len(df)} parcela(s) "
                        f"em aberto totalizando R$ {total:,.2f}. "
                        f"Entre em contato conosco. 💛")
                ok, err = _disparar_whatsapp(cli_id, wpp, nome_real, _msg, username)
                if ok:
                    st.success("Mensagem enviada!")
                else:
                    st.error(err)
        return

    if tipo == "detalhe_venda":
        venda = res["venda"]
        df_it: pd.DataFrame = res["itens"]
        total = float(venda.get("valor_total", 0))
        data  = _fmt_data(venda.get("data_venda"))
        cli   = venda.get("cliente", "—")
        forma = venda.get("forma_pagamento", "—")
        vend  = venda.get("vendedor_nome", "—")

        # Intro natural antes do cupom
        _cli_p = cli.split()[0] if cli and cli != "—" else "este cliente"
        st.markdown(
            f"Aqui está o pedido de **{cli}** realizado em **{data}**, "
            f"no valor de **R$ {total:,.2f}** ({forma}):"
        )

        # Renderiza estilo cupom com marca d'água 5%
        itens_html = "".join(
            f"<tr><td style='padding:2px 8px'>{r['produto']}</td>"
            f"<td style='text-align:center'>{int(r['qtd'])}</td>"
            f"<td style='text-align:right'>R$ {float(r['preco_unit']):,.2f}</td>"
            f"<td style='text-align:right'><b>R$ {float(r['subtotal']):,.2f}</b></td></tr>"
            for _, r in df_it.iterrows()
        ) if not df_it.empty else "<tr><td colspan='4'>Sem itens registrados</td></tr>"

        st.markdown(f"""
<div style="position:relative;font-family:monospace;background:#F8F6F0;border:1px solid #C9A84C;
     border-radius:10px;padding:18px 22px;max-width:480px;overflow:hidden">
  <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%) rotate(-30deg);
       font-size:4rem;font-weight:900;color:rgba(158,91,111,0.05);pointer-events:none;
       white-space:nowrap;user-select:none">LOJA GM HOMEM</div>
  <div style="text-align:center;font-weight:800;font-size:1rem;color:#1A2035">
    🛍️ LOJA GM HOMEM ITAÚNA</div>
  <hr style="border-color:#C9A84C;margin:6px 0">
  <div style="font-size:.8rem">
    <b>Cliente:</b> {cli}<br>
    <b>Data:</b> {data} | <b>Pagamento:</b> {forma}<br>
    <b>Vendedor(a):</b> {vend}
  </div>
  <hr style="border-color:#C9A84C;margin:6px 0">
  <table style="width:100%;font-size:.8rem;border-collapse:collapse">
    <thead>
      <tr style="background:#fce8ec">
        <th style="text-align:left;padding:2px 8px">Produto</th>
        <th>Qtd</th>
        <th style="text-align:right">Unit.</th>
        <th style="text-align:right">Total</th>
      </tr>
    </thead>
    <tbody>{itens_html}</tbody>
  </table>
  <hr style="border-color:#C9A84C;margin:6px 0">
  <div style="text-align:right;font-size:1rem;font-weight:800;color:#1A2035">
    TOTAL: R$ {total:,.2f}
  </div>
</div>
""", unsafe_allow_html=True)
        # Botão de ação: abre histórico de vendas do cliente com filtro pré-aplicado
        if cli and cli != "—":
            _cli_slug = re.sub(r"\W", "", cli)[:8]
            _manu_render_action_button(
                f"📊 Ver Histórico de {cli.split()[0]}",
                cli,
                key=f"manu_hist_{chat_key}_{_cli_slug}",
                action="historico",
            )
        return

    if tipo == "lista":
        df: pd.DataFrame = res["df"]
        subtipo = res["subtipo"]
        titulo  = res["titulo"]
        if df.empty:
            _intros_vazios = {
                "atraso":          "Ótimas notícias — nenhum cliente em atraso no momento! ✅",
                "aniversariantes": "Nenhum aniversariante este mês.",
                "inativos":        "Todos os clientes compraram recentemente. Nenhum inativo. ✅",
                "clientes":        "Nenhum cliente encontrado na base.",
            }
            st.markdown(_intros_vazios.get(subtipo, "Nenhum registro encontrado."))
            return
        # ── intros naturais por subtipo ───────────────────────────────────────
        _intros = {
            "atraso":          (
                f"Temos **{len(df)} cliente(s)** com pagamentos em atraso. "
                f"O total em aberto é **R$ {float(df['total'].sum()):,.2f}**. "
                "Veja a lista abaixo:"
            ),
            "aniversariantes": (
                f"**{len(df)} cliente(s)** fazem aniversário este mês! "
                "Que tal mandar uma mensagem especial? 🎂"
            ),
            "inativos":        (
                f"**{len(df)} cliente(s)** não compram há mais de 60 dias. "
                "Uma boa hora para uma campanha de reativação:"
            ),
            "clientes":        (
                f"Temos **{len(df)} cliente(s)** ativos cadastrados. "
                "Listei os de maior volume de compras:"
            ),
        }
        st.markdown(_intros.get(subtipo, f"**{titulo}** — {len(df)} registro(s)"))
        # ── subtipo: clientes ─────────────────────────────────────────────────
        if subtipo == "clientes":
            df_show = df.drop(columns=["cliente_id", "whatsapp"], errors="ignore").copy()
            if "total_gasto" in df_show.columns:
                df_show["total_gasto"] = df_show["total_gasto"].apply(
                    lambda x: f"R$ {float(x):,.2f}"
                )
            df_show.columns = [c.replace("_", " ").title() for c in df_show.columns]
            st.dataframe(df_show, hide_index=True, use_container_width=True)
            return

        # ── subtipo: atraso — renderização por linha com botões de ação ──────
        if subtipo == "atraso":
            wh_url = _get_webhook_url()
            # Cabeçalho da tabela
            _hdr = st.columns([2.8, 1.4, 0.9, 1.3, 1.6, 1.4])
            for _h, _l in zip(_hdr, ["Cliente", "Total Aberto", "Parcelas",
                                      "Max Atraso", "Financeiro", "WhatsApp"]):
                _h.markdown(f"<small><b>{_l}</b></small>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:2px 0 6px'>", unsafe_allow_html=True)

            for _i, (_, _row) in enumerate(df.iterrows()):
                _nm  = str(_row.get("nome", ""))
                _wpp = str(_row.get("whatsapp") or "")
                _cid = str(_row.get("cliente_id", ""))
                _tot = float(_row.get("total", 0))
                _parc = int(_row.get("parcelas", 0))
                _dias = int(_row.get("max_dias", 0))
                _rk = f"_{chat_key[:8]}_{_i}"

                _rc = st.columns([2.8, 1.4, 0.9, 1.3, 1.6, 1.4])
                _rc[0].write(_nm)
                _rc[1].write(f"R$ {_tot:,.2f}")
                _rc[2].write(f"{_parc}")
                _rc[3].markdown(
                    f"<span style='color:#c0392b;font-weight:700'>{_dias}d</span>"
                    if _dias > 30 else f"{_dias}d",
                    unsafe_allow_html=True,
                )
                # Botão de ação: abre Financeiro com filtro pré-aplicado
                with _rc[4]:
                    _manu_render_action_button(
                        f"📂 {_nm.split()[0]}",
                        _nm,
                        key=f"manu_atraso_fin{_rk}",
                        action="financeiro",
                    )
                # WhatsApp individual
                if _wpp and wh_url:
                    if _rc[5].button("📲", key=f"manu_atraso_wpp{_rk}",
                                     use_container_width=True):
                        _msg_c = (f"Olá {_nm.split()[0]}! Você possui parcelas em atraso "
                                  f"na GM Homem. Entre em contato. 💛")
                        ok, err = _disparar_whatsapp(_cid, _wpp, _nm, _msg_c, username)
                        if ok:
                            st.success(f"✅ Mensagem enviada para {_nm.split()[0]}!")
                        else:
                            st.error(err)
                else:
                    _rc[5].write("—")

            # Disparo em massa mantido como expander opcional
            if wh_url:
                _msg_bulk = "Olá {nome}! Você possui parcelas em atraso na GM Homem. Entre em contato. 💛"
                with st.expander("📱 Disparar WhatsApp para toda a lista"):
                    st.text_area("Mensagem (use {nome})", value=_msg_bulk,
                                 key=f"manu_wpp_msg_{subtipo}", height=80)
                    if st.button(f"🚀 Disparar para {len(df)} contatos via n8n",
                                 key=f"manu_wpp_bulk_{subtipo}", type="primary",
                                 use_container_width=True):
                        _msg_t = st.session_state.get(f"manu_wpp_msg_{subtipo}", _msg_bulk)
                        _ok_c = 0
                        for _, _brow in df.iterrows():
                            _bwpp = str(_brow.get("whatsapp") or "")
                            if not _bwpp:
                                continue
                            _bnm  = str(_brow.get("nome", ""))
                            _bcid = str(_brow.get("cliente_id", ""))
                            ok, _ = _disparar_whatsapp(
                                _bcid, _bwpp, _bnm,
                                _msg_t.replace("{nome}", _bnm.split()[0]),
                                username,
                            )
                            if ok:
                                _ok_c += 1
                        st.success(f"✅ {_ok_c}/{len(df)} mensagens disparadas.")
            return

        # ── subtipo: aniversariantes / inativos — tabela + WhatsApp em massa ─
        st.dataframe(df.drop(columns=["cliente_id", "whatsapp"], errors="ignore"),
                     hide_index=True, use_container_width=True)
        wh_url = _get_webhook_url()
        if wh_url and not df.empty:
            if subtipo == "aniversariantes":
                msg_template = "Feliz aniversário, {nome}! 🎂 A GM Homem deseja um dia incrível para você! Sua surpresa especial te espera aqui. 💛"
            else:
                msg_template = "Olá {nome}! Sentimos sua falta na GM Homem Itaúna. Temos novidades esperando por você! 💛"

            with st.expander("📱 Disparar WhatsApp para toda a lista"):
                st.text_area("Mensagem (use {nome})", value=msg_template,
                             key=f"manu_wpp_msg_{subtipo}", height=80)
                if st.button(f"🚀 Disparar para {len(df)} contatos via n8n",
                             key=f"manu_wpp_bulk_{subtipo}", type="primary",
                             use_container_width=True):
                    _msg_t = st.session_state.get(f"manu_wpp_msg_{subtipo}", msg_template)
                    _ok_count = 0
                    for _, row in df.iterrows():
                        _wpp = str(row.get("whatsapp") or "")
                        if not _wpp:
                            continue
                        _nm  = str(row.get("nome", ""))
                        _cid = str(row.get("cliente_id", ""))
                        _msg_final = _msg_t.replace("{nome}", _nm.split()[0])
                        ok, _ = _disparar_whatsapp(_cid, _wpp, _nm, _msg_final, username)
                        if ok:
                            _ok_count += 1
                    st.success(f"✅ {_ok_count}/{len(df)} mensagens disparadas.")
        return

    if tipo == "sugestao_compras":
        df: pd.DataFrame = res["df"]
        if df.empty:
            st.markdown("Não encontrei produtos ativos para analisar o estoque.")
            return
        criticos  = df[df["situacao"] == "🔴 Crítico"]
        atencao   = df[df["situacao"] == "🟠 Atenção"]
        _intro_parts = []
        if not criticos.empty:
            _intro_parts.append(f"**{len(criticos)} item(ns) em situação crítica**")
        if not atencao.empty:
            _intro_parts.append(f"**{len(atencao)} em atenção**")
        _intro_ctx = " e ".join(_intro_parts) if _intro_parts else "estoque dentro do esperado"
        st.markdown(
            f"Analisei o giro dos últimos 30 dias — {_intro_ctx}. "
            "Veja o que precisa de atenção:"
        )
        df_show = df[["nome", "categoria", "estoque_atual", "estoque_minimo",
                      "vendidos_30d", "situacao"]].copy()
        df_show.columns = ["Produto", "Categoria", "📦 Estoque", "Mínimo", "Vendidos 30d", "Situação"]
        st.dataframe(df_show, hide_index=True, use_container_width=True)
        if not criticos.empty:
            nomes = ", ".join(criticos["nome"].tolist()[:5])
            st.error(f"🔴 **Crítico — repor urgente:** {nomes}")
        if not atencao.empty:
            nomes = ", ".join(atencao["nome"].tolist()[:5])
            st.warning(f"🟠 **Atenção — estoque baixo:** {nomes}")
        return


# ── Autenticação ─────────────────────────────────────────────────────────────

def _h(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


# Senhas padrão: admin → "admin123" | vendas → "vendas123"
# Para trocar, substitua o segundo argumento de _h() pela nova senha.
_USERS: dict = {
    "admin":        {"senha_hash": _h("admin123"),   "role": "admin"},
    "admin_master": {"senha_hash": _h("jardel2026"), "role": "admin_master"},
    "master":       {"senha_hash": _h("jardel2026"), "role": "admin_master"},
    "vendas":       {"senha_hash": _h("vendas123"),  "role": "vendas"},
}

# ── Menu Unificado — mesmo menu para Admin e Vendas ──────────────────────────
# Admin e Vendas veem as mesmas abas. O controle de acesso é feito DENTRO
# de cada página (mensagem "Acesso Restrito") — não por ocultação do menu.
# Isso elimina a confusão de "menus diferentes" entre perfis.
# ⚡ JG Hub continua exclusivo de admin_master.
# 🔄 Trocas liberada para todos os perfis.

_ABAS_TODOS  = ["🛒 Vendas", "💳 Recebimentos", "💳 Pagamentos",
                "📦 Estoque", "📒 Cadastros",
                "📋 Condicional", "🔄 Trocas",
                "📊 Relatórios", "🏠 Visão Geral",
                "📣 Mala Direta", "👤 Equipe",
                "📚 Histórico Legado"]
_ABAS_MASTER = _ABAS_TODOS + ["⚡ JG Hub"]

_TABS_POR_ROLE: dict = {
    "admin":        _ABAS_TODOS,
    "admin_master": _ABAS_MASTER,
    "vendas":       _ABAS_TODOS,   # mesmo menu — bloqueio é feito dentro da página
}

# Páginas restritas para perfil 'vendas' (exibe aviso ao entrar)
_RESTRITAS_VENDAS = frozenset([
    "🏠 Visão Geral",
    "👤 Equipe", "📣 Mala Direta", "🏭 Fornecedores", "⚡ JG Hub",
    "💳 Pagamentos",
])


def _verificar_login(usuario: str, senha: str) -> tuple:
    u = _USERS.get(usuario.strip().lower())
    if not u:
        return False, ""
    # Verifica se há hash sobrescrito no banco (via aba Acessos)
    try:
        with _db_get_conn() as _lc:
            with _lc.cursor() as _cur:
                _cur.execute(
                    "SELECT valor FROM config_geral WHERE chave = %s",
                    (f"AUTH_HASH_{usuario.strip().lower()}",)
                )
                _row = _cur.fetchone()
        _hash_efetivo = _row[0] if _row else u["senha_hash"]
    except Exception:
        _hash_efetivo = u["senha_hash"]
    if _h(senha) == _hash_efetivo:
        return True, u["role"]
    return False, ""


def _tela_login() -> None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        try:
            _, _logo_c, _ = st.columns([1, 2, 1])
            with _logo_c:
                st.image('static/logo-gmh.jpg', width=200)
        except Exception:
            pass
        st.subheader("Acesso ao Dashboard")
        with st.form("login_form", clear_on_submit=False):
            usuario = st.text_input("Usuário", key="login_usuario")
            senha   = st.text_input("Senha", type="password", key="login_senha")
            submitted = st.form_submit_button(
                "Entrar", use_container_width=True, type="primary"
            )
        if submitted:
            ok, role = _verificar_login(usuario, senha)
            if ok:
                st.session_state.logged_in = True
                st.session_state.username  = usuario.strip().lower()
                st.session_state.role      = role
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")


# ── Gate de login ─────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    _tela_login()
    st.stop()

# Role disponível antes da injeção de CSS
_role = st.session_state.get("role", "")
_IS_ADMIN  = _role in ("admin", "admin_master")
_IS_MASTER = _role == "admin_master"

# ── Paleta de tema por perfil ─────────────────────────────────────────────────
if _IS_ADMIN:
    _sb_bg       = "#0D1117"   # fundo marrom-escuro GM Homem
    _sb_text     = "#f5e6ea"   # texto rosado claro
    _sb_accent   = "#E8C97A"   # dourado — item ativo
    _sb_btn_bg   = "#1A2035"   # botão rosa antigo
    _sb_btn_fg   = "#fff"
    _sb_hr       = "rgba(184,137,42,0.40)"
    _sb_sel_bg   = "rgba(212,170,80,0.15)"
    _main_bg     = ""           # sem override no conteúdo principal
    _btn_radius  = "8px"
else:                           # vendas — fundo mais claro, identidade feminina
    _sb_bg       = "#F0EAD6"   # rosa pálido
    _sb_text     = "#0D1117"   # texto escuro
    _sb_accent   = "#1A2035"   # rosa antigo — item ativo
    _sb_btn_bg   = "#1A2035"
    _sb_btn_fg   = "#fff"
    _sb_hr       = "rgba(158,91,111,0.25)"
    _sb_sel_bg   = "rgba(158,91,111,0.08)"
    _main_bg     = "#FEFAF9"   # fundo principal levemente rosado
    _btn_radius  = "8px"       # botões modo vendas

# ── CSS Global + Sidebar dinâmica ─────────────────────────────────────────────
_main_bg_css = (
    f"[data-testid='stAppViewContainer'] > .main {{ background-color: {_main_bg} !important; }}"
    if _main_bg else ""
)
st.markdown(f"""
<style>
/* === Fundo de página por perfil ================ */
{_main_bg_css}

/* === Botões (conteúdo principal) ================ */
.stButton > button {{
    background-color: #1A2035 !important;
    border: 2px solid #1A2035 !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: {_btn_radius} !important;
    opacity: 1 !important;
    transition: background-color .2s, color .2s;
}}
.stButton > button:hover,
.stButton > button:active {{
    background-color: #2A3558 !important;
    border-color: #2A3558 !important;
    color: #ffffff !important;
    opacity: 1 !important;
}}
.stFormSubmitButton > button {{
    background-color: #C9A84C !important;
    border: 2px solid #C9A84C !important;
    color: #fff !important;
    font-weight: 700 !important;
    border-radius: {_btn_radius} !important;
    transition: background-color .2s, color .2s;
}}
.stFormSubmitButton > button:hover {{
    background-color: #E8C97A !important;
    border-color: #E8C97A !important;
    color: #fff !important;
}}

/* === Métricas ===================================  */
[data-testid="stMetricValue"] {{
    color: #1A2035 !important;
    font-weight: 800 !important;
}}
[data-testid="stMetricLabel"] {{
    color: #C9A84C !important;
    font-weight: 600 !important;
}}

/* === Tabs ======================================= */
.stTabs [data-baseweb="tab"] {{ font-weight: 600; }}
.stTabs [aria-selected="true"] {{
    color: #1A2035 !important;
    border-bottom: 3px solid #C9A84C !important;
}}

/* === Tabela — alinhar colunas numéricas ========= */
[data-testid="stDataFrame"] th {{ text-align: center !important; }}

/* ================================================
   SIDEBAR — tema por perfil: {_role}
   ================================================ */
[data-testid="stSidebar"] > div:first-child {{
    background-color: {_sb_bg} !important;
}}

/* Texto geral */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{
    color: {_sb_text} !important;
}}

/* Radio — limpa blocos sólidos, oculta bolinha padrão */
[data-testid="stSidebar"] [data-testid="stRadio"] label {{
    background:    transparent !important;
    border-radius: 0 !important;
    border-left:   3px solid transparent !important;
    padding:       5px 0 5px 12px !important;
    margin-bottom: 1px !important;
    display:       flex !important;
    align-items:   center !important;
    transition:    border-color .15s, background .15s !important;
}}
/* Oculta indicador circular — a barra lateral é o indicador */
[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child {{
    display: none !important;
}}
/* Item selecionado */
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {{
    border-left: 3px solid {_sb_accent} !important;
    background:  {_sb_sel_bg} !important;
}}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {{
    color:       {_sb_accent} !important;
    font-weight: 700 !important;
}}
/* Hover em itens não selecionados */
[data-testid="stSidebar"] [data-testid="stRadio"] label:not(:has(input:checked)):hover {{
    border-left: 3px solid {_sb_accent}66 !important;
    background:  {_sb_sel_bg} !important;
    cursor: pointer;
}}

/* Sidebar buttons — todos os tipos e estados com texto branco */
[data-testid="stSidebar"] .stButton > button,
[data-testid="stSidebar"] .stButton > button:hover,
[data-testid="stSidebar"] .stButton > button:focus,
[data-testid="stSidebar"] .stButton > button:active {{
    background-color: {_sb_btn_bg} !important;
    color:            #ffffff !important;
    border-color:     {_sb_btn_bg} !important;
    border-radius:    8px !important;
    font-weight:      700 !important;
    letter-spacing:   .02em !important;
    opacity:          1 !important;
}}

/* Separadores */
[data-testid="stSidebar"] hr {{
    border-color: {_sb_hr} !important;
    margin: 6px 0 !important;
}}
</style>
""", unsafe_allow_html=True)

# ── Sidebar — Logo ───────────────────────────────────────────────────────────
# Tenta static/logo-gmh.jpg (enviada pelo n8n) e faz fallback para logo-gmh.jpg
_sb_logo_b64: str | None = None
for _sb_path in (_LOGO_STATIC, _LOGO_PATH):
    try:
        if os.path.exists(_sb_path):
            with open(_sb_path, "rb") as _f:
                _sb_logo_b64 = base64.b64encode(_f.read()).decode()
            break
    except Exception:
        pass

if _sb_logo_b64:
    st.sidebar.markdown(
        f'<div style="text-align:center;padding:6px 0 2px">'
        f'<img src="data:image/png;base64,{_sb_logo_b64}" width="180" '
        f'style="border-radius:8px;max-width:100%"/></div>',
        unsafe_allow_html=True,
    )
else:
    st.sidebar.title("GM Homem Itaúna")

st.sidebar.markdown("---")

_role     = st.session_state.role
_IS_ADMIN  = _role in ("admin", "admin_master")
_IS_MASTER = _role == "admin_master"
_abas = _TABS_POR_ROLE.get(_role, [])

# Navegação programática (ex: botão "Abrir Financeiro" da GM Homem AI)
_nav_target = st.session_state.pop("_nav_target", None)
_nav_index  = _abas.index(_nav_target) if _nav_target and _nav_target in _abas else None
st.session_state['_abas_cache'] = _abas
# Se navegação programática, forçar o radio resetando seu state
pagina = st.sidebar.radio(
    "Navegação", _abas,
    index=_nav_index if _nav_index is not None else 0,
    key='_sidebar_nav'
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"👤 **{st.session_state.username}** "
    f"<span style='font-size:0.75rem;color:gray'>({_role})</span>",
    unsafe_allow_html=True,
)
st.sidebar.markdown(
    """<a href="https://t.me/GM HomemPDV_bot" target="_blank">
    <button style="width:100%;padding:10px;background:#0088cc;color:white;
    border:none;border-radius:8px;cursor:pointer;font-size:13px;
    font-weight:600;margin-bottom:8px">
    🤖 GM Homem AI Telegram
    </button></a>""",
    unsafe_allow_html=True
)
# Badge condicionais atrasados
_df_cond_alert = run_query("SELECT COUNT(*) as n FROM condicionais WHERE status='aberto' AND dt_devolucao < CURRENT_DATE")
_n_atrasados = int(_df_cond_alert.iloc[0]["n"]) if not _df_cond_alert.empty else 0
if _n_atrasados > 0:
    st.sidebar.markdown(
        f"""<div style='background:#DC2626;color:white;padding:8px 12px;border-radius:8px;
        font-size:13px;font-weight:700;text-align:center;margin-bottom:8px;cursor:pointer'
        onclick="">
        ⚠️ {_n_atrasados} Condicional{'is' if _n_atrasados>1 else ''} Atrasado{'s' if _n_atrasados>1 else ''}!
        </div>""",
        unsafe_allow_html=True
    )
if st.sidebar.button("Sair", key="btn_logout", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.username  = ""
    st.session_state.role      = ""
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='font-size:.78rem;line-height:1.6;color:#C9A84C'>"
    "<b>Desenvolvido por JGAutomacoes.AI</b><br/>"
    "<span style='font-style:italic'>"
    "Tecnologia de impacto para um império em expansão.</span>"
    "</div>",
    unsafe_allow_html=True,
)
# CSS para fixar rodapé na base do sidebar
st.markdown("""
<style>
[data-testid="stSidebar"] > div:first-child {
    display: flex;
    flex-direction: column;
}
[data-testid="stSidebar"] > div:first-child > div:last-child {
    margin-top: auto;
}
</style>
""", unsafe_allow_html=True)

# ── Coloração dos itens do menu lateral via JS ────────────────────────────────
# Vinho/Escuro → "Gerencial"  |  Verde Água/Claro → "🛒 Vendas"
components.html("""
<script>
(function () {
    function _cor(texto) {
        if (texto === "Gerencial")  return { bg: "#5C1A2E", fg: "#F5D5DC" };
        if (texto === "🛒 Vendas") return { bg: "#B2E1E7", fg: "#013A3A" };
        return null;
    }
    function colorirMenu() {
        try {
            var doc = window.parent.document;
            doc.querySelectorAll(
                '[data-testid="stSidebar"] [role="radiogroup"] label'
            ).forEach(function (label) {
                var texto = label.innerText.trim();
                var c = _cor(texto);
                if (!c) { label.style.backgroundColor = ""; label.style.color = ""; return; }
                label.style.backgroundColor = c.bg;
                label.style.color           = c.fg;
                label.style.borderRadius    = "6px";
                label.style.padding         = "3px 10px";
                label.style.marginBottom    = "2px";
                label.style.display         = "block";
                label.style.fontWeight      = "700";
            });
        } catch (_) {}
    }
    setTimeout(colorirMenu, 200);
    setTimeout(colorirMenu, 700);
    setTimeout(colorirMenu, 2000);
    try {
        new MutationObserver(colorirMenu).observe(
            window.parent.document.body, { childList: true, subtree: true }
        );
    } catch (_) {}
})();
</script>
""", height=0)

# ── Conteúdo por página ───────────────────────────────────────────────────────
_b64 = _logo_b64()
if _b64:
    st.markdown(
        f'<div style="display:flex;align-items:center;justify-content:space-between;'
        f'margin-bottom:0.5rem;padding:8px 0">'
        f'<div>'
        f'<span style="font-size:1.8rem;font-weight:800;color:#1A2035;line-height:1.1">'
        f'GM Homem Itaúna</span><br/>'
        f'<span style="font-size:0.8rem;color:#C9A84C;font-weight:600;letter-spacing:.05em">'
        f'PDV & Gestão</span>'
        f'</div>'
        f'<img src="data:image/png;base64,{_b64}" height="64" '
        f'style="border-radius:10px;box-shadow:0 2px 8px rgba(158,91,111,.25)"/>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="height:3px;background:linear-gradient(90deg,#1A2035,#C9A84C,#1A2035);'
        f'border-radius:2px;margin-bottom:1rem"></div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        '<h1 style="color:#1A2035;font-weight:800">GM Homem Itaúna</h1>',
        unsafe_allow_html=True,
    )

# ── Alerta de orçamento de tokens (admin) ────────────────────────────────────
if _IS_ADMIN:
    try:
        _df_orcamento = run_query(
            "SELECT valor FROM config_geral WHERE chave = 'ORCAMENTO_MENSAL_USD'"
        )
        _orcamento_usd = float(
            _df_orcamento["valor"].iloc[0]
        ) if not _df_orcamento.empty and _df_orcamento["valor"].iloc[0] else 0.0

        if _orcamento_usd > 0:
            _mes_alerta  = date.today().strftime("%Y-%m")
            _df_tok_al   = run_query(
                f"SELECT chars FROM chat_ia_tokens WHERE mes = '{_mes_alerta}'"
            )
            _chars_al     = int(_df_tok_al["chars"].iloc[0]) if not _df_tok_al.empty else 0
            _tokens_al    = _chars_al / 4
            # Estimativa: Gemini Flash ≈ $0.0000005/token (gemini-1.5-flash input)
            _custo_est    = round(_tokens_al * 0.0000005, 4)
            _pct_uso      = (_custo_est / _orcamento_usd) * 100

            if _pct_uso >= 100:
                st.error(
                    f"🚨 **Orçamento IA estourado!** Estimativa: **US$ {_custo_est:.4f}** "
                    f"de US$ {_orcamento_usd:.2f} ({_pct_uso:.0f}%). "
                    "Revise o consumo em Administração → ⚙️ Configurações."
                )
            elif _pct_uso >= 80:
                st.warning(
                    f"⚠️ **Orçamento IA em {_pct_uso:.0f}%** — Estimativa: **US$ {_custo_est:.4f}** "
                    f"de US$ {_orcamento_usd:.2f} este mês. "
                    "Monitore em Administração → ⚙️ Configurações."
                )
    except Exception:
        pass  # alerta nunca deve travar o dashboard

# ── Migrações idempotentes globais ────────────────────────────────────────────
run_command("""
    CREATE TABLE IF NOT EXISTS pagamentos_balcao (
        id            BIGSERIAL     PRIMARY KEY,
        cliente_nome  TEXT          NOT NULL,
        valor_abatido NUMERIC(12,2) NOT NULL,
        operador      TEXT,
        observacao    TEXT,
        data_hora     TIMESTAMPTZ   NOT NULL DEFAULT NOW()
    )
""")
run_command("""
    CREATE TABLE IF NOT EXISTS vales_troca (
        id         BIGSERIAL     PRIMARY KEY,
        cliente_id UUID          NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
        venda_id   UUID          REFERENCES vendas(id) ON DELETE SET NULL,
        valor      NUMERIC(12,2) NOT NULL,
        saldo      NUMERIC(12,2) NOT NULL,
        operador   TEXT,
        motivo     TEXT,
        ativo      BOOLEAN       DEFAULT TRUE,
        criado_em  TIMESTAMPTZ   DEFAULT NOW()
    )
""")
run_command("""
    CREATE TABLE IF NOT EXISTS config_geral (
        chave         TEXT PRIMARY KEY,
        valor         TEXT,
        atualizado_em TIMESTAMPTZ DEFAULT NOW()
    )
""")
run_command("""
    CREATE TABLE IF NOT EXISTS chat_ia_tokens (
        mes           TEXT PRIMARY KEY,
        chars         BIGINT NOT NULL DEFAULT 0,
        atualizado_em TIMESTAMPTZ DEFAULT NOW()
    )
""")
run_command("""
    CREATE TABLE IF NOT EXISTS historico_legado (
        id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
        cliente_codigo    TEXT,
        cliente_id        UUID        REFERENCES clientes(id),
        documento         TEXT,
        ordem             TEXT,
        dt_emissao        DATE,
        dt_vencimento     DATE,
        situacao_original TEXT,
        modalidade        TEXT,
        valor_docto       NUMERIC(12,2) DEFAULT 0,
        observacao        TEXT,
        vendedor          TEXT,
        forma_pagto       TEXT,
        nro_parcelas      TEXT,
        status            TEXT        NOT NULL DEFAULT 'baixado',
        data_baixa        DATE,
        baixa_por         TEXT,
        valor_recebido    NUMERIC(12,2),
        raw_data          JSONB,
        created_at        TIMESTAMPTZ DEFAULT now(),
        updated_at        TIMESTAMPTZ DEFAULT now()
    )
""")
run_command("CREATE INDEX IF NOT EXISTS idx_hl_cliente_id ON historico_legado(cliente_id)")
run_command("CREATE INDEX IF NOT EXISTS idx_hl_status     ON historico_legado(status)")
run_command("CREATE INDEX IF NOT EXISTS idx_hl_dt_venc    ON historico_legado(dt_vencimento)")

run_command("""
    CREATE TABLE IF NOT EXISTS movimentos_financeiros (
        id               SERIAL PRIMARY KEY,
        parcela_id       TEXT,
        origem           TEXT,
        valor_pago       NUMERIC(10,2),
        forma_pagamento  TEXT,
        isentou_encargos BOOLEAN DEFAULT FALSE,
        saldo_anterior   NUMERIC(10,2),
        saldo_posterior  NUMERIC(10,2),
        operador         TEXT,
        observacao       TEXT,
        data_movimento   TIMESTAMP DEFAULT NOW()
    )
""")

# ═══════════════════════════════════════════════════════════════════════════════
# CHAT IA — Motor de Consulta e Operação
# ═══════════════════════════════════════════════════════════════════════════════

def _chat_extrair_nome(texto: str) -> str | None:
    """Extrai nome de cliente de frases como 'parcelas de Maria' / 'histórico da Ana'."""
    for pat in [
        r'\bdo\s+cliente\s+([A-ZÀ-Úa-zà-ú][^\?,.\n]{2,40}?)(?:\s*[?,.]|$)',
        r'\bda\s+cliente\s+([A-ZÀ-Úa-zà-ú][^\?,.\n]{2,40}?)(?:\s*[?,.]|$)',
        r'\bde\s+([A-ZÀ-Úa-zà-ú][^\?,.\n]{2,40}?)(?:\s*[?,.]|$)',
        r'\bda\s+([A-ZÀ-Úa-zà-ú][^\?,.\n]{2,40}?)(?:\s*[?,.]|$)',
        r'\bdo\s+([A-ZÀ-Úa-zà-ú][^\?,.\n]{2,40}?)(?:\s*[?,.]|$)',
        r'\bpara\s+([A-ZÀ-Úa-zà-ú][^\?,.\n]{2,40}?)(?:\s*[?,.]|$)',
        r'\bcliente\s+([A-ZÀ-Úa-zà-ú][^\?,.\n]{2,40}?)(?:\s*[?,.]|$)',
    ]:
        m = re.search(pat, texto, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def _chat_extrair_produto(texto: str) -> str | None:
    """Extrai nome de produto de perguntas de estoque."""
    for pat in [
        r'\bestoque\s+(?:de\s+|do\s+|da\s+)?([a-zA-ZÀ-ú\s]{2,40}?)(?:\s*[?,?]|$)',
        r'\btem\s+([a-zA-ZÀ-ú\s]{2,40}?)\s+(?:em estoque|disponível|no estoque)',
        r'\bquantos?\s+([a-zA-ZÀ-ú\s]{2,40}?)\s+(?:tem|temos|restam|sobraram)',
        r'\bquantas?\s+([a-zA-ZÀ-ú\s]{2,40}?)\s+(?:tem|temos|restam|sobraram)',
    ]:
        m = re.search(pat, texto, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


# ── Mapa de complementos por categoria ───────────────────────────────────────
_COMPLEMENTOS_CATEGORIA: dict[str, list[str]] = {
    "calça":   ["cinto", "blusa", "bolsa", "sandália"],
    "calca":   ["cinto", "blusa", "bolsa", "sandália"],
    "jeans":   ["cinto", "blusa", "tênis", "sandália"],
    "legging": ["blusa", "top", "tênis", "jaqueta"],
    "vestido": ["sandália", "bolsa", "colar", "brinco"],
    "blusa":   ["calça", "saia", "short", "cinto"],
    "camisa":  ["calça", "saia", "cinto", "bolsa"],
    "top":     ["calça", "saia", "short", "cinto"],
    "saia":    ["blusa", "sandália", "cinto", "bolsa"],
    "short":   ["blusa", "sandália", "tênis", "top"],
    "casaco":  ["calça", "blusa", "bota", "cinto"],
    "jaqueta": ["calça", "blusa", "bota"],
    "macacão": ["sandália", "colar", "bolsa", "brinco"],
    "macacao": ["sandália", "colar", "bolsa", "brinco"],
}


def _complementos_para(item: str) -> list[str]:
    """Retorna sugestões complementares para um item de roupa."""
    item_l = item.lower()
    for chave, sugestoes in _COMPLEMENTOS_CATEGORIA.items():
        if chave in item_l:
            return sugestoes
    return ["acessórios", "bolsa", "sandália"]


def _abordagem_prospeccao(ultimo_item: str) -> str:
    """Sugere frase de abordagem baseada no último item comprado."""
    item = (ultimo_item or "").lower()
    if any(x in item for x in ["calça", "calca", "jeans", "legging"]):
        return "Diga que chegaram blusas e cintos novos que combinam com aquela calça."
    if any(x in item for x in ["vestido"]):
        return "Mostre as novas sandálias e bolsas que chegaram para compor o look."
    if any(x in item for x in ["blusa", "camisa", "top"]):
        return "Sugira uma saia ou calça nova que combina com a blusa que ela comprou."
    if any(x in item for x in ["saia", "short"]):
        return "Mostre as blusas e tops novos para montar um look completo."
    if any(x in item for x in ["casaco", "jaqueta", "moletom"]):
        return "Avise que chegaram calças e botas novas na mesma vibe."
    if any(x in item for x in ["bolsa", "carteira"]):
        return "Diga que chegaram novos acessórios e peças na mesma linha."
    return "Diga que chegaram muitas novidades e pergunte se ela precisa de algo especial."


def _registrar_tokens_ia(prompt: str, resposta: str) -> None:
    """Acumula estimativa de tokens por mês (1 token ≈ 4 caracteres)."""
    try:
        chars = len(prompt) + len(resposta)
        mes   = date.today().strftime("%Y-%m")
        run_command(
            "INSERT INTO chat_ia_tokens (mes, chars) VALUES (%s, %s) "
            "ON CONFLICT (mes) DO UPDATE SET "
            "chars = chat_ia_tokens.chars + EXCLUDED.chars, "
            "atualizado_em = NOW()",
            (mes, chars),
        )
    except Exception:
        pass  # contador nunca deve quebrar o chat


def _get_webhook_url() -> str:
    """Lê URL_WEBHOOK_N8N da tabela config_geral."""
    try:
        df = run_query("SELECT valor FROM config_geral WHERE chave = 'URL_WEBHOOK_N8N'")
        return df["valor"].iloc[0] if not df.empty and df["valor"].iloc[0] else ""
    except Exception:
        return ""


def _log_erro_n8n(mensagem: str) -> None:
    """Grava o último erro de disparo em config_geral para diagnóstico."""
    import datetime as _dt
    ts  = _dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log = f"[{ts}] {mensagem}"
    try:
        run_command(
            "INSERT INTO config_geral (chave, valor, atualizado_em) "
            "VALUES ('ULTIMO_ERRO_N8N', %s, NOW()) "
            "ON CONFLICT (chave) DO UPDATE SET valor = EXCLUDED.valor, atualizado_em = NOW()",
            (log[:500],),
        )
    except Exception:
        pass  # não deixar o log quebrar o fluxo


def _disparar_whatsapp(
    cliente_id: str,
    telefone: str,
    nome: str,
    msg_corpo: str,
    vendedora: str,
    webhook_url: str = "",
) -> tuple[bool, str]:
    """
    Dispara webhook n8n → Evolution API.
    Retorna (sucesso: bool, mensagem_erro: str).
    """
    url = webhook_url or _get_webhook_url()
    if not url:
        return False, "URL do Webhook não configurada. Acesse Administração → ⚙️ Configurações."
    payload = {
        "cliente_id": cliente_id,
        "telefone":   telefone,
        "nome":       nome,
        "msg_corpo":  msg_corpo,
        "vendedora":  vendedora,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        ok   = resp.status_code < 400
        if ok:
            # Incrementa contador de disparos do mês
            mes = date.today().strftime("%Y-%m")
            chave_disp = f"DISPAROS_{mes}"
            run_command(
                "INSERT INTO config_geral (chave, valor, atualizado_em) "
                "VALUES (%s, '1', NOW()) "
                "ON CONFLICT (chave) DO UPDATE SET "
                "valor = (COALESCE(config_geral.valor::int, 0) + 1)::text, "
                "atualizado_em = NOW()",
                (chave_disp,),
            )
        else:
            _log_erro_n8n(f"HTTP {resp.status_code} — destino: {nome} ({telefone})")
        return ok, ("" if ok else f"HTTP {resp.status_code}")
    except requests.exceptions.Timeout:
        _log_erro_n8n(f"Timeout >10s — destino: {nome} ({telefone}) — URL: {url[:60]}")
        return False, "Timeout ao conectar ao n8n (>10s)."
    except Exception as _e:
        _log_erro_n8n(f"{type(_e).__name__}: {_e} — destino: {nome} ({telefone})")
        return False, str(_e)


# ── Queries cacheadas (estoque e histórico) ───────────────────────────────────
def _qry_estoque_geral() -> "pd.DataFrame":
    return run_query(
        "SELECT nome, estoque_atual, estoque_minimo FROM produtos "
        "WHERE ativo IS NOT FALSE ORDER BY estoque_atual ASC LIMIT 8"
    )


def _qry_estoque_produto(nome_lower: str) -> "pd.DataFrame":
    _np = re.sub(r"['\"]", "", nome_lower)
    return run_query(
        f"SELECT nome, estoque_atual, preco_venda, categoria "
        f"FROM produtos WHERE LOWER(nome) LIKE '%{_np}%' "
        f"AND ativo IS NOT FALSE ORDER BY nome LIMIT 6"
    )


def _qry_historico_cliente(nome_lower: str) -> "pd.DataFrame":
    _n = nome_lower.replace("'", "''")
    return run_query(f"""
        SELECT data, valor_total, forma_pagamento, status_pagamento, cliente_real, itens
        FROM (
            SELECT v.data_venda::date AS data,
                   v.valor_total,
                   v.forma_pagamento,
                   v.status_pagamento,
                   c.nome AS cliente_real,
                   STRING_AGG(
                       COALESCE(p.nome,'—') || ' ×' || COALESCE(iv.quantidade::text,'?'),
                       ', ' ORDER BY p.nome
                   ) AS itens
            FROM vendas v
            JOIN clientes c          ON c.id = v.cliente_id
            LEFT JOIN itens_venda iv ON iv.venda_id = v.id
            LEFT JOIN produtos p     ON p.id = iv.produto_id
            WHERE LOWER(c.nome) LIKE '%{_n}%'
            GROUP BY v.id, v.data_venda, v.valor_total,
                     v.forma_pagamento, v.status_pagamento, c.nome
            UNION ALL
            SELECT hl.dt_emissao AS data,
                   hl.valor_docto AS valor_total,
                   hl.modalidade  AS forma_pagamento,
                   CASE hl.status WHEN 'baixado' THEN 'pago' ELSE 'em aberto' END AS status_pagamento,
                   c.nome AS cliente_real,
                   COALESCE(NULLIF(hl.observacao,''),
                            hl.raw_data->>'LANCTO_DESCRICAO',
                            hl.modalidade) AS itens
            FROM historico_legado hl
            JOIN clientes c ON c.id = hl.cliente_id
            WHERE LOWER(c.nome) LIKE '%{_n}%'
        ) _h
        ORDER BY data DESC NULLS LAST
        LIMIT 5
    """)


def _chat_detectar_intent(texto: str) -> str:
    """Classifica a intenção do usuário."""
    t = texto.lower()
    if re.search(
        r'\b(parcela|devendo|em aberto|conta de|saldo de|quanto deve|'
        r'dívida|divida|crediário em aberto|débito)\b', t
    ):
        return "parcelas"
    if re.search(
        r'\b(prospecção|prospeccao|mala\s*direta|quem\s+não\s+compra|'
        r'clientes?\s+inativos?|sem\s+comprar|sumiu|cadê\s+\w|inativos?|'
        r'tempo\s+sem\s+comprar|não\s+compra\s+há|nao\s+compra\s+ha|'
        r'clientes?\s+sumidos?|reativar\s+clientes?)\b', t
    ):
        return "prospeccao"
    if re.search(
        r'\b(sugestão|sugestao|sugerir|indicar|o\s+que\s+sugerir|'
        r'combina\s+com|complemento|o\s+que\s+indica|produto\s+para|'
        r'indicação|indicacao|o\s+que\s+ela\s+pode)\b', t
    ):
        return "sugestao"
    if re.search(
        r'\b(última[s]?\s*compra[s]?|histórico|comprou|compras\s+de|'
        r'o que comprou|últimas\s+venda[s]?|histórico de compras)\b', t
    ):
        return "historico"
    if re.search(
        r'\b(minha\s+comissão|comissão\s+(hoje|mês|mes|semana|desse|deste)|'
        r'quanto\s+(ganhei|vendi)|meus\s+ganhos|minhas\s+vendas|'
        r'quanto\s+vendí|quanto\s+vendi)\b', t
    ):
        return "comissao"
    if re.search(
        r'\b(estoque|tem\s+em\s+estoque|disponível|quantos?\s+tem|'
        r'restam|sobraram|no\s+estoque|sem\s+estoque|falta\s+de)\b', t
    ):
        return "estoque"
    if re.search(
        r'\b(faturamento|faturou|total\s+de\s+vendas|vendas\s+(hoje|mês|mes|deste|desse)|'
        r'receita|quanto\s+a\s+loja|resumo\s+do\s+dia|vendas\s+do\s+dia)\b', t
    ):
        return "faturamento"
    if re.search(
        r'\b(ajuda|comandos|o\s+que\s+(você|voce)\s+(pode|faz|sabe|consegue|entende)|'
        r'\bhelp\b|exemplos|como\s+uso|como\s+perguntar)\b', t
    ):
        return "ajuda"
    return "venda"



def _processar_chat_ia(prompt: str, role: str, username: str) -> dict:
    """
    Processa o prompt e retorna:
      {"tipo": "resposta", "content": str}
    ou
      {"tipo": "venda",    "content": ""}   → aciona o fluxo PDV existente
    """
    intent = _chat_detectar_intent(prompt)
    hoje   = date.today()

    # ── AJUDA ─────────────────────────────────────────────────────────────────
    if intent == "ajuda":
        _extras_admin = (
            "\n- `faturamento hoje` / `faturamento desse mês`\n"
            "- `vendas do dia` — resumo do dia atual"
        ) if role == "admin" else ""
        return {
            "tipo": "resposta",
            "content": (
                "🤖 **GM Homem AI — GM Homem**\n\n"
                "**📋 Consultas de clientes:**\n"
                "- `parcelas de [Nome]` — saldo devedor e vencimentos\n"
                "- `últimas compras de [Nome]` — histórico das 3 últimas compras\n\n"
                "**📦 Estoque:**\n"
                "- `estoque de vestido` — quantidade disponível de um produto\n"
                "- `estoque` (sem produto) — lista os itens com menos unidades\n\n"
                "**💰 Comissão:**\n"
                "- `minha comissão hoje`\n"
                "- `minha comissão desse mês`\n"
                f"{_extras_admin}\n\n"
                "**📣 Prospecção:**\n"
                "- `quem não compra há tempo` — clientes inativos há +45 dias com sugestão de abordagem\n"
                "- `mala direta` — mesma lista pronta para contato\n\n"
                "**🎯 Sugestão de produto:**\n"
                "- `o que sugerir para [Nome]?` — complementos baseados no histórico\n\n"
                "**🛒 Registrar Venda** _(aba Vendas)_:\n"
                "- `Venda para Maria, Vestido, 150 reais, 2x no cartão`\n\n"
                "_Para baixas e pagamentos use o menu **Financeiro** → selecione o cliente._"
            ),
        }

    # ── PARCELAS ──────────────────────────────────────────────────────────────
    if intent == "parcelas":
        nome = _chat_extrair_nome(prompt)
        if not nome:
            return {
                "tipo": "resposta",
                "content": "Para consultar parcelas, diga:\n*parcelas de [Nome do cliente]*",
            }
        _n = nome.lower().replace("'", "''")
        df = run_query(f"""
            SELECT cr.valor_parcela,
                   cr.data_vencimento,
                   (CURRENT_DATE - cr.data_vencimento)::int AS dias_atraso,
                   v.forma_pagamento,
                   c.nome AS cliente_real
            FROM contas_receber cr
            JOIN vendas v  ON v.id  = cr.venda_id
            JOIN clientes c ON c.id = v.cliente_id
            WHERE LOWER(c.nome) LIKE '%{_n}%'
              AND cr.status = 'aberto'
            ORDER BY cr.data_vencimento
            LIMIT 12
        """)
        if df.empty:
            return {
                "tipo": "resposta",
                "content": f"✅ Nenhuma parcela em aberto para **{nome}**.",
            }
        cliente_real = df["cliente_real"].iloc[0]
        total = float(df["valor_parcela"].sum())
        linhas = [
            f"**Parcelas em aberto — {cliente_real}**",
            f"Saldo total: **R$ {total:,.2f}** ({len(df)} parcela(s))\n",
        ]
        for _, r in df.iterrows():
            dias = int(r["dias_atraso"] or 0)
            atr  = f"🔴 {dias}d atraso" if dias > 0 else "🟢 no prazo"
            linhas.append(
                f"- {_fmt_data(r['data_vencimento'])}  **R$ {float(r['valor_parcela']):,.2f}**  {atr}"
            )
        linhas.append(
            "\n_Para baixar parcelas: **Financeiro** → selecione o cliente._"
        )
        return {"tipo": "resposta", "content": "\n".join(linhas)}

    # ── HISTÓRICO ─────────────────────────────────────────────────────────────
    if intent == "historico":
        nome = _chat_extrair_nome(prompt)
        if not nome:
            return {
                "tipo": "resposta",
                "content": "Para ver o histórico, diga:\n*últimas compras de [Nome]*",
            }
        df = _qry_historico_cliente(nome.lower())
        if df.empty:
            return {
                "tipo": "resposta",
                "content": f"Nenhuma compra registrada para **{nome}**.",
            }
        cliente_real = df["cliente_real"].iloc[0]
        partes = [f"**Últimas compras — {cliente_real}**\n"]
        for _, r in df.iterrows():
            itens_str = str(r["itens"] or "itens não detalhados")
            status_ic = "✅" if r["status_pagamento"] == "pago" else "🔴"
            partes.append(
                f"**{r['data']}** — R$ {float(r['valor_total']):,.2f} "
                f"({r['forma_pagamento']}) {status_ic}\n"
                f"  ↳ {itens_str[:90]}"
            )
        return {"tipo": "resposta", "content": "\n\n".join(partes)}

    # ── COMISSÃO ──────────────────────────────────────────────────────────────
    if intent == "comissao":
        t = prompt.lower()
        if re.search(r'\b(mês|mes|esse\s*mês|desse\s*mês|mensal|este\s*mês)\b', t):
            filtro_data  = (
                f"EXTRACT(YEAR  FROM data_venda) = {hoje.year} "
                f"AND EXTRACT(MONTH FROM data_venda) = {hoje.month}"
            )
            periodo_label = hoje.strftime("%B/%Y")
        else:
            filtro_data   = f"data_venda::date = '{hoje}'"
            periodo_label = f"hoje ({hoje.strftime('%d/%m/%Y')})"

        # Tenta casar username com config_comissao
        _u = username.lower().replace("'", "''")
        df_cfg = run_query(
            f"SELECT codigo_vendedor, percentual FROM config_comissao "
            f"WHERE LOWER(nome_vendedor) LIKE '%{_u}%' "
            f"   OR LOWER(codigo_vendedor) LIKE '%{_u}%' LIMIT 1"
        )
        if not df_cfg.empty:
            cod = df_cfg["codigo_vendedor"].iloc[0]
            pct = float(df_cfg["percentual"].iloc[0])
            df_v = run_query(
                f"SELECT COALESCE(SUM(valor_total),0) AS total, COUNT(*) AS qtd "
                f"FROM vendas WHERE codigo_vendedor = '{cod}' "
                f"AND {filtro_data} AND status_pagamento IN ('pago','parcelado')"
            )
        else:
            pct  = 5.0
            df_v = run_query(
                f"SELECT COALESCE(SUM(valor_total),0) AS total, COUNT(*) AS qtd "
                f"FROM vendas WHERE LOWER(COALESCE(vendedor_nome,'')) = '{_u}' "
                f"AND {filtro_data} AND status_pagamento IN ('pago','parcelado')"
            )

        total    = float(df_v["total"].iloc[0]) if not df_v.empty else 0.0
        qtd      = int(df_v["qtd"].iloc[0])     if not df_v.empty else 0
        comissao = round(total * pct / 100, 2)
        return {
            "tipo": "resposta",
            "content": (
                f"💰 **Sua comissão — {periodo_label}**\n\n"
                f"- Vendas realizadas: **{qtd}**\n"
                f"- Total vendido: **R$ {total:,.2f}**\n"
                f"- % Comissão: **{pct:.1f}%**\n"
                f"- **Comissão: R$ {comissao:,.2f}**"
            ),
        }

    # ── ESTOQUE ───────────────────────────────────────────────────────────────
    if intent == "estoque":
        nome_prod = _chat_extrair_produto(prompt)
        if not nome_prod:
            df = _qry_estoque_geral()
            if df.empty:
                return {"tipo": "resposta", "content": "Nenhum produto cadastrado."}
            linhas = ["**Produtos com menor estoque:**\n"]
            for _, r in df.iterrows():
                est     = int(r["estoque_atual"] or 0)
                critico = (
                    pd.notna(r["estoque_minimo"])
                    and est < int(r["estoque_minimo"] or 0)
                )
                alerta = " ⚠️ crítico" if critico else ""
                linhas.append(f"- {r['nome']}: **{est} un.**{alerta}")
            return {"tipo": "resposta", "content": "\n".join(linhas)}

        df = _qry_estoque_produto(nome_prod.lower())
        if df.empty:
            return {
                "tipo": "resposta",
                "content": f"Nenhum produto encontrado com **'{nome_prod}'**.",
            }
        linhas = [f"**Estoque — '{nome_prod}':**\n"]
        for _, r in df.iterrows():
            est = int(r["estoque_atual"] or 0)
            pv  = f"R$ {float(r['preco_venda']):,.2f}" if pd.notna(r["preco_venda"]) else "—"
            linhas.append(f"- {r['nome']} ({r['categoria'] or '—'}): **{est} un.** · {pv}")
        return {"tipo": "resposta", "content": "\n".join(linhas)}

    # ── FATURAMENTO (admin only) ──────────────────────────────────────────────
    if intent == "faturamento":
        if role != "admin":
            return {
                "tipo": "resposta",
                "content": (
                    "🔒 Consulta de faturamento disponível apenas para o **Gerente/Admin**.\n"
                    "Você pode consultar *minha comissão hoje* ou *parcelas de [cliente]*."
                ),
            }
        t = prompt.lower()
        if re.search(r'\b(mês|mes|mensal|esse\s*mês|desse\s*mês)\b', t):
            filtro        = (
                f"EXTRACT(YEAR  FROM data_venda) = {hoje.year} "
                f"AND EXTRACT(MONTH FROM data_venda) = {hoje.month}"
            )
            periodo_label = hoje.strftime("%B/%Y")
        else:
            filtro        = f"data_venda::date = '{hoje}'"
            periodo_label = f"hoje ({hoje.strftime('%d/%m/%Y')})"

        df = run_query(
            f"SELECT COALESCE(SUM(valor_total),0) AS total, COUNT(*) AS qtd "
            f"FROM vendas WHERE {filtro} AND status_pagamento IN ('pago','parcelado')"
        )
        total = float(df["total"].iloc[0]) if not df.empty else 0.0
        qtd   = int(df["qtd"].iloc[0])     if not df.empty else 0

        df_ab = run_query(
            "SELECT COALESCE(SUM(valor_parcela),0) AS total "
            "FROM contas_receber WHERE status='aberto'"
        )
        em_aberto = float(df_ab["total"].iloc[0]) if not df_ab.empty else 0.0

        # Top 3 vendedoras no período
        df_vnd = run_query(
            f"SELECT COALESCE(codigo_vendedor, vendedor_nome, 'N/I') AS vnd, "
            f"SUM(valor_total) AS total_vnd, COUNT(*) AS qtd_vnd "
            f"FROM vendas WHERE {filtro} AND status_pagamento IN ('pago','parcelado') "
            f"GROUP BY vnd ORDER BY total_vnd DESC LIMIT 3"
        )
        linhas_vnd = ""
        if not df_vnd.empty:
            linhas_vnd = "\n\n**Top vendedoras:**\n" + "\n".join(
                f"- {r['vnd']}: R$ {float(r['total_vnd']):,.2f} ({int(r['qtd_vnd'])} venda(s))"
                for _, r in df_vnd.iterrows()
            )

        return {
            "tipo": "resposta",
            "content": (
                f"📊 **Faturamento — {periodo_label}**\n\n"
                f"- Vendas confirmadas: **{qtd}**\n"
                f"- Total faturado: **R$ {total:,.2f}**\n"
                f"- A receber (geral em aberto): **R$ {em_aberto:,.2f}**"
                f"{linhas_vnd}"
            ),
        }

    # ── PROSPECÇÃO ────────────────────────────────────────────────────────────
    if intent == "prospeccao":
        df_prosp = run_query("""
            SELECT c.nome,
                   COALESCE(c.whatsapp, '') AS telefone,
                   MAX(v.data_venda)::date               AS ultima_compra,
                   EXTRACT(DAY FROM (CURRENT_DATE - MAX(v.data_venda)))::int AS dias_sem_comprar,
                   (
                       SELECT STRING_AGG(p2.nome, ', ')
                       FROM (
                           SELECT p3.nome
                           FROM itens_venda iv2
                           JOIN vendas v2 ON v2.id = iv2.venda_id
                           LEFT JOIN produtos p3 ON p3.id = iv2.produto_id
                           WHERE v2.cliente_id = c.id
                             AND v2.data_venda = MAX(v.data_venda)
                           LIMIT 2
                       ) p2
                   ) AS ultimo_item
            FROM clientes c
            JOIN vendas v ON v.cliente_id = c.id
            WHERE c.ativo = true
            GROUP BY c.id, c.nome, c.whatsapp
            HAVING EXTRACT(DAY FROM (CURRENT_DATE - MAX(v.data_venda)))::int > 45
            ORDER BY dias_sem_comprar DESC
            LIMIT 10
        """)
        if df_prosp.empty:
            resp = (
                "✅ Todos os clientes compraram nos últimos 45 dias.\n"
                "Nenhuma prospecção necessária agora."
            )
        else:
            linhas = [
                f"📋 **{len(df_prosp)} cliente(s) para prospectar** "
                f"(última compra há +45 dias)\n"
            ]
            for _, r in df_prosp.iterrows():
                tel   = str(r["telefone"] or "—")
                item  = str(r["ultimo_item"] or "—")
                dias  = int(r["dias_sem_comprar"] or 0)
                abord = _abordagem_prospeccao(item)
                linhas.append(
                    f"**{r['nome']}** · {tel} — _{dias} dias sem comprar_\n"
                    f"  ↳ Último item: *{item[:60]}*\n"
                    f"  💬 {abord}"
                )
            resp = "\n\n".join(linhas)
        _registrar_tokens_ia(prompt, resp)
        return {"tipo": "resposta", "content": resp}

    # ── SUGESTÃO DE PRODUTO ───────────────────────────────────────────────────
    if intent == "sugestao":
        nome = _chat_extrair_nome(prompt)
        if not nome:
            return {
                "tipo": "resposta",
                "content": (
                    "Para sugerir um produto, diga:\n"
                    "*o que sugerir para [Nome da cliente]?*"
                ),
            }
        df_hist = run_query(
            "SELECT p.nome AS produto, v.data_venda::date AS data, c.nome AS cliente_real "
            "FROM itens_venda iv "
            "JOIN vendas v   ON v.id  = iv.venda_id "
            "JOIN clientes c ON c.id  = v.cliente_id "
            "LEFT JOIN produtos p ON p.id = iv.produto_id "
            f"WHERE LOWER(c.nome) LIKE '%{nome.lower().replace(chr(39), chr(39)*2)}%' "
            "ORDER BY v.data_venda DESC LIMIT 5"
        )
        if df_hist.empty:
            resp = f"Não encontrei histórico de compras para **{nome}**."
        else:
            cliente_real    = df_hist["cliente_real"].iloc[0]
            itens_comprados = df_hist["produto"].dropna().tolist()
            ultimo          = itens_comprados[0] if itens_comprados else "—"
            complementos    = _complementos_para(ultimo)
            linhas = [
                f"🎯 **Sugestão para {cliente_real}**\n",
                f"Compras recentes: *{', '.join(itens_comprados[:3])}*",
                f"\n**Complementos para `{ultimo}`:**",
            ]
            for comp in complementos:
                df_comp = run_query(
                    "SELECT nome, estoque_atual FROM produtos "
                    f"WHERE LOWER(nome) LIKE '%{comp.lower()}%' "
                    "AND ativo IS NOT FALSE AND estoque_atual > 0 "
                    "ORDER BY estoque_atual DESC LIMIT 1"
                )
                if not df_comp.empty:
                    rc = df_comp.iloc[0]
                    linhas.append(
                        f"- **{rc['nome']}** — {int(rc['estoque_atual'])} un. em estoque ✅"
                    )
                else:
                    linhas.append(f"- *{comp}* — sem estoque no momento")
            resp = "\n".join(linhas)
        _registrar_tokens_ia(prompt, resp)
        return {"tipo": "resposta", "content": resp}

    # ── VENDA (fallback → fluxo PDV existente) ────────────────────────────────
    return {"tipo": "venda", "content": ""}


def _render_chat_ia(chat_key: str, role: str, username: str,
                    placeholder: str = "") -> None:
    """
    Renderiza o widget de Chat IA reutilizável.
    chat_key   — chave única de session_state para as mensagens
    role       — perfil do usuário
    username   — nome de login
    placeholder — texto hint do input
    """
    _msgs_key = f"chat_ia_msgs_{chat_key}"
    if _msgs_key not in st.session_state:
        st.session_state[_msgs_key] = []

    _hint = placeholder or (
        "Venda para Ana, 150 reais, pix | parcelas de João | minha comissão hoje"
    )

    # Histórico de mensagens
    for _msg in st.session_state[_msgs_key]:
        with st.chat_message(_msg["role"]):
            st.markdown(_msg["content"])

    if _prompt := st.chat_input(_hint, key=f"chat_input_{chat_key}"):
        st.session_state[_msgs_key].append({"role": "user", "content": _prompt})
        _res = _processar_chat_ia(_prompt, role, username)

        if _res["tipo"] == "venda":
            # Fluxo PDV existente (parse_venda → va_pendente)
            _dados = parse_venda(_prompt)
            if "cliente_nome" not in _dados:
                _reply = (
                    "Não identifiquei o cliente.\n"
                    "Use: *Venda para [Nome], [Produto], R$ [valor], [forma]*\n\n"
                    "Ou pergunte: `parcelas de [Nome]` · `minha comissão hoje` · `estoque de [produto]`"
                )
            elif "valor_total" not in _dados:
                _reply = "Não identifiquei o valor. Inclua *150 reais* ou *R$ 150,00*."
            else:
                try:
                    _clientes = buscar_cliente(_dados["cliente_nome"])
                except Exception:
                    _clientes = []
                    _reply = "Não consegui acessar o cadastro de clientes agora. Tente novamente em instantes."
                    st.session_state[_msgs_key].append({"role": "assistant", "content": _reply})
                    st.rerun()
                    return

                if not _clientes:
                    _reply = (
                        f"Cliente **{_dados['cliente_nome']}** não encontrado.\n"
                        "Cadastre pelo ➕ ou use o nome completo."
                    )
                elif len(_clientes) > 1:
                    _lista = "\n".join(f"- {c['nome']}" for c in _clientes)
                    _reply = (
                        f"Encontrei {len(_clientes)} clientes:\n\n{_lista}\n\n"
                        "Digite o nome completo para identificar corretamente."
                    )
                else:
                    _dados["cliente_id"]    = _clientes[0]["id"]
                    _dados["cliente_nome"]  = _clientes[0]["nome"]
                    _dados["origem"]        = "chat"
                    _dados["vendedor_nome"] = username
                    st.session_state.va_pendente = _dados
                    _reply = (
                        f"✔️ Dados prontos — confirme no painel ao lado.\n\n"
                        f"**Cliente:** {_dados['cliente_nome']}  \n"
                        f"**Valor:** R$ {_dados['valor_total']:,.2f}  \n"
                        f"**Pagamento:** {_dados['forma_pagamento']}\n\n"
                        f"---\n"
                        f"💡 *Dica: verifique o tamanho preferido da cliente no histórico "
                        f"antes de confirmar — pergunte `últimas compras de {_dados['cliente_nome'].split()[0]}` "
                        f"para ver o que ela costuma levar.*"
                    )
        else:
            _reply = _res["content"]
            _registrar_tokens_ia(_prompt, _reply)

        st.session_state[_msgs_key].append({"role": "assistant", "content": _reply})
        st.rerun()

    # ── Disparo rápido WhatsApp (sempre visível abaixo do chat) ──────────────
    with st.expander("📱 Disparar WhatsApp para cliente", expanded=False):
        _wpp_df_cli = run_query(
            "SELECT id::text AS cid, nome, "
            "COALESCE(whatsapp, '') AS fone "
            "FROM clientes WHERE ativo = true ORDER BY nome"
        )
        if _wpp_df_cli.empty:
            st.info("Nenhum cliente cadastrado.")
        else:
            _wpp_idx = st.selectbox(
                "Cliente",
                range(len(_wpp_df_cli)),
                format_func=lambda i: _wpp_df_cli["nome"].iloc[i],
                key=f"wpp_cli_{chat_key}",
            )
            _wpp_nome = _wpp_df_cli["nome"].iloc[_wpp_idx]
            _wpp_fone = st.text_input(
                "WhatsApp",
                value=str(_wpp_df_cli["fone"].iloc[_wpp_idx]),
                key=f"wpp_fone_{chat_key}",
                placeholder="5531999990000",
            )
            _wpp_msg = st.text_area(
                "Mensagem",
                value=f"Olá {_wpp_nome.split()[0]}! Temos novidades na GM Homem esperando por você. 💛",
                height=80,
                key=f"wpp_msg_{chat_key}",
            )
            if st.button("🚀 Enviar via n8n", key=f"wpp_btn_{chat_key}",
                         use_container_width=True):
                _ok, _err = _disparar_whatsapp(
                    cliente_id=str(_wpp_df_cli["cid"].iloc[_wpp_idx]),
                    telefone=_wpp_fone,
                    nome=_wpp_nome,
                    msg_corpo=_wpp_msg,
                    vendedora=username,
                )
                if _ok:
                    st.toast("🚀 Comando enviado ao n8n!", icon="✅")
                else:
                    st.error(f"Falha: {_err}")


# ═══════════════════════════════════════════════════════════════════════════════




def get_dados_nota_completos(documento, codigo_cliente, origem):
    """Retorna dict com todos os dados disponíveis sobre a nota."""
    doc = str(documento).replace("'", "''")
    cli = str(codigo_cliente).replace("'", "''")

    if origem == 'legado':
        df_dup = run_query(f"""
            SELECT da.documento, da.ordem, da.dt_emissao, da.dt_vencimento,
                   da.valor_original, da.valor_saldo, da.modalidade,
                   COALESCE(da.observacao,'') AS observacao,
                   COALESCE(da.vendedor,'') AS vendedor,
                   COALESCE(da.pedido::text,'') AS pedido,
                   COALESCE(cl.nome, da.nome_cliente,'') AS nome_cliente,
                   COALESCE(cl.cpf,'') AS cpf,
                   COALESCE(cl.celular,'') AS telefone
            FROM duplicatas_abertas da
            LEFT JOIN clientes_legados cl ON da.codigo_cliente = cl.codigo_legado
            WHERE da.documento = '{doc}'
              AND da.codigo_cliente = '{cli}'
            LIMIT 1
        """)
        df_hist = run_query(f"""
            SELECT hq.ordem, hq.dt_pagamento, hq.valor_docto, hq.modalidade, hq.observacao
            FROM historico_quitado hq
            WHERE hq.documento = '{doc}'
              AND hq.codigo_cliente = '{cli}'
            ORDER BY hq.dt_pagamento
        """)
        # Parcelas abertas desta nota
        df_abertas = run_query(f"""
            SELECT da.ordem, da.dt_vencimento, da.valor_saldo, da.modalidade, da.status
            FROM duplicatas_abertas da
            WHERE da.documento = '{doc}'
              AND da.codigo_cliente = '{cli}'
            ORDER BY da.dt_vencimento
        """)
        # Dados extras do sistema legado (hora, caixa, nro_parcelas)
        df_raw = run_query(f"""
            SELECT hl.nro_parcelas,
                   hl.raw_data->>'HORA'             AS hora_venda,
                   hl.raw_data->>'CAIXA'            AS caixa,
                   hl.raw_data->>'LANCTO_DESCRICAO' AS tipo_lancto
            FROM historico_legado hl
            WHERE hl.documento = '{doc}'
              AND hl.cliente_codigo = '{cli}'
            ORDER BY hl.ordem
            LIMIT 1
        """)
        return {
            'tipo': 'legado',
            'duplicata': df_dup,
            'historico_parcelas': df_hist,
            'parcelas_abertas': df_abertas,
            'raw_extra': df_raw,
        }
    else:
        # Handle 'CR-xxxxxxxx' documento format (first 8 chars of contas_receber.id)
        if str(documento).startswith('CR-'):
            cr_ref = str(documento)[3:11]  # Extract 8-char reference
            df_venda = run_query(f"""
                SELECT v.id, v.data_venda, v.valor_total AS valor_bruto,
                       0 AS desconto_pct,
                       v.valor_total, v.forma_pagamento,
                       COALESCE(v.vendedor_nome,'') AS vendedor_nome,
                       c.nome AS cliente, COALESCE(c.cpf,'') AS cpf,
                       COALESCE(c.whatsapp,'') AS whatsapp,
                       COALESCE(v.cupom_text,'') AS cupom_text
                FROM vendas v
                JOIN clientes c ON v.cliente_id = c.id
                WHERE v.id IN (
                    SELECT cr.venda_id FROM contas_receber cr
                    WHERE SUBSTRING(cr.id::text, 1, 8) = '{cr_ref}'
                )
                LIMIT 1
            """)
            df_itens = run_query(f"""
                SELECT COALESCE(e.nome, iv.descricao, 'Produto') AS produto,
                       iv.quantidade, iv.preco_unitario, iv.subtotal
                FROM itens_venda iv
                LEFT JOIN estoque e ON iv.produto_id = e.id
                WHERE iv.venda_id IN (
                    SELECT cr.venda_id FROM contas_receber cr
                    WHERE SUBSTRING(cr.id::text, 1, 8) = '{cr_ref}'
                )
            """)
            df_parcelas = run_query(f"""
                SELECT cr.data_vencimento, cr.valor_parcela, cr.status
                FROM contas_receber cr
                WHERE SUBSTRING(cr.id::text, 1, 8) = '{cr_ref}'
                ORDER BY cr.data_vencimento
            """)
        else:
            # Fallback for raw UUID format
            df_venda = run_query(f"""
                SELECT v.id, v.data_venda, v.valor_total AS valor_bruto,
                       0 AS desconto_pct,
                       v.valor_total, v.forma_pagamento,
                       COALESCE(v.vendedor_nome,'') AS vendedor_nome,
                       c.nome AS cliente, COALESCE(c.cpf,'') AS cpf,
                       COALESCE(c.whatsapp,'') AS whatsapp,
                       COALESCE(v.cupom_text,'') AS cupom_text
                FROM vendas v
                JOIN clientes c ON v.cliente_id = c.id
                WHERE v.id::text = '{doc}'
                LIMIT 1
            """)
            df_itens = run_query(f"""
                SELECT COALESCE(e.nome, iv.descricao, 'Produto') AS produto,
                       iv.quantidade, iv.preco_unitario, iv.subtotal
                FROM itens_venda iv
                LEFT JOIN estoque e ON iv.produto_id = e.id
                WHERE iv.venda_id::text = '{doc}'
            """)
            df_parcelas = run_query(f"""
                SELECT cr.data_vencimento, cr.valor_parcela, cr.status
                FROM contas_receber cr
                WHERE cr.venda_id::text = '{doc}'
                ORDER BY cr.data_vencimento
            """)
        return {'tipo': 'banco', 'venda': df_venda, 'itens': df_itens, 'parcelas': df_parcelas}


def render_ver_itens_nota(documento, codigo_cliente, origem):
    """Renderiza painel de detalhes da nota (legado ou banco)."""
    import streamlit.components.v1 as components
    dados = get_dados_nota_completos(documento, codigo_cliente, origem)

    if dados['tipo'] == 'legado':
        df_dup     = dados['duplicata']
        df_hist    = dados['historico_parcelas']
        df_abertas = dados.get('parcelas_abertas', pd.DataFrame())
        df_raw     = dados.get('raw_extra', pd.DataFrame())

        if df_dup.empty:
            st.warning(f"Nota {documento} não encontrada.")
            return

        row = df_dup.iloc[0]
        nome       = str(row.get('nome_cliente', '—') or '—')
        tel        = str(row.get('telefone', '—') or '—')
        vendedor   = str(row.get('vendedor', '—') or '—')
        dt_compra  = str(row.get('dt_emissao', '—') or '—')
        dt_venc    = str(row.get('dt_vencimento', '—') or '—')
        modalidade = str(row.get('modalidade', '—') or '—')
        obs        = str(row.get('observacao', '—') or '—')
        pedido     = str(row.get('pedido', documento) or documento)
        valor_orig  = float(row.get('valor_original') or row.get('valor_saldo') or 0)
        valor_saldo = float(row.get('valor_saldo') or 0)

        # Dados extras do sistema legado (hora, caixa)
        hora_venda = tipo_lancto = caixa = nro_parcelas = "—"
        if not df_raw.empty:
            raw = df_raw.iloc[0]
            _h = str(raw.get('hora_venda') or '')
            if len(_h) >= 4:
                hora_venda = f"{_h[:2]}:{_h[2:4]}"
            elif _h:
                hora_venda = _h
            caixa        = str(raw.get('caixa')       or '—')
            tipo_lancto  = str(raw.get('tipo_lancto') or '—')
            nro_parcelas = str(raw.get('nro_parcelas') or '—')

        # Parcelas pagas
        linhas_hist = ""
        if not df_hist.empty:
            for _, h in df_hist.iterrows():
                linhas_hist += (
                    f"<tr>"
                    f"<td style='padding:3px 6px'>Parcela {h.get('ordem','—')}</td>"
                    f"<td style='text-align:center;padding:3px 6px'>{h.get('dt_pagamento','—')}</td>"
                    f"<td style='text-align:right;padding:3px 6px'>R$ {float(h.get('valor_docto',0) or 0):,.2f}</td>"
                    f"<td style='padding:3px 6px'>{h.get('modalidade','—')}</td>"
                    f"<td style='padding:3px 6px;color:#16a34a;font-weight:600'>✅ Pago</td>"
                    f"</tr>"
                )

        # Parcelas abertas
        linhas_abertas = ""
        if not df_abertas.empty:
            for _, a in df_abertas.iterrows():
                _cor = "#DC2626" if str(a.get('status','')) == 'Pendente' else "#555"
                linhas_abertas += (
                    f"<tr>"
                    f"<td style='padding:3px 6px'>Parcela {a.get('ordem','—')}</td>"
                    f"<td style='text-align:center;padding:3px 6px'>{a.get('dt_vencimento','—')}</td>"
                    f"<td style='text-align:right;padding:3px 6px;color:{_cor};font-weight:600'>"
                    f"R$ {float(a.get('valor_saldo',0) or 0):,.2f}</td>"
                    f"<td style='padding:3px 6px'>{a.get('modalidade','—')}</td>"
                    f"<td style='padding:3px 6px;color:{_cor};font-weight:600'>⏳ Em aberto</td>"
                    f"</tr>"
                )

        _todas_linhas = linhas_hist + linhas_abertas
        if _todas_linhas:
            secao_hist = (
                "<div style='margin-top:12px'>"
                "<div style='font-weight:600;font-size:13px;margin-bottom:6px'>Parcelas desta compra:</div>"
                "<table style='width:100%;font-size:12px;border-collapse:collapse'>"
                "<tr style='background:#f0f0f0'>"
                "<th style='padding:4px 6px;text-align:left'>Parcela</th>"
                "<th style='padding:4px 6px;text-align:center'>Data/Venc.</th>"
                "<th style='padding:4px 6px;text-align:right'>Valor</th>"
                "<th style='padding:4px 6px;text-align:left'>Forma</th>"
                "<th style='padding:4px 6px;text-align:left'>Status</th>"
                "</tr>"
                f"{_todas_linhas}</table></div>"
            )
        else:
            secao_hist = "<div style='font-size:12px;color:#888;margin-top:8px'>Nenhuma parcela encontrada para esta compra.</div>"

        html_cupom = f"""
<div id="cupom-itens" style="font-family:'Courier New',monospace;max-width:420px;
    margin:0 auto;padding:20px;border:2px solid #333;border-radius:8px;
    background:#fff;color:#000;font-size:13px">
  <div style="text-align:center;border-bottom:2px dashed #000;padding-bottom:10px;margin-bottom:10px">
    <div style="font-size:18px;font-weight:700">LOJA GM HOMEM ITAÚNA</div>
    <div style="font-size:11px;color:#555">Comprovante de Compra — Sistema Legado</div>
  </div>
  <div style="background:#fffbf0;border:1px solid #e0c060;border-radius:6px;
      padding:6px 10px;font-size:11px;color:#856404;margin-bottom:10px">
    ℹ️ O sistema anterior não registrava produtos individuais — apenas o valor total da venda.
  </div>
  <table style="width:100%;border-collapse:collapse;margin-bottom:10px">
    <tr><td style="color:#666;padding:2px 0">Cliente</td>
        <td style="font-weight:600;text-align:right">{nome}</td></tr>
    <tr><td style="color:#666;padding:2px 0">Telefone</td>
        <td style="text-align:right">{tel}</td></tr>
    <tr><td style="color:#666;padding:2px 0">Nota / Pedido</td>
        <td style="text-align:right">{pedido}</td></tr>
    <tr><td style="color:#666;padding:2px 0">Data da compra</td>
        <td style="text-align:right">{dt_compra}</td></tr>
    <tr><td style="color:#666;padding:2px 0">Hora</td>
        <td style="text-align:right">{hora_venda}</td></tr>
    <tr><td style="color:#666;padding:2px 0">Vencimento</td>
        <td style="text-align:right">{dt_venc}</td></tr>
    <tr><td style="color:#666;padding:2px 0">Modalidade</td>
        <td style="text-align:right">{modalidade}</td></tr>
    <tr><td style="color:#666;padding:2px 0">Nº Parcelas</td>
        <td style="text-align:right">{nro_parcelas}</td></tr>
    <tr><td style="color:#666;padding:2px 0">Tipo lançamento</td>
        <td style="text-align:right">{tipo_lancto}</td></tr>
    <tr><td style="color:#666;padding:2px 0">Caixa</td>
        <td style="text-align:right">{caixa}</td></tr>
    <tr><td style="color:#666;padding:2px 0">Vendedora cód.</td>
        <td style="text-align:right">{vendedor}</td></tr>
    <tr><td style="color:#666;padding:2px 0">Observação</td>
        <td style="text-align:right">{obs}</td></tr>
  </table>
  <div style="border-top:1px dashed #000;border-bottom:1px dashed #000;padding:8px 0;margin:8px 0">
    <div style="display:flex;justify-content:space-between">
      <span>Valor original</span>
      <span style="font-weight:700">R$ {valor_orig:,.2f}</span>
    </div>
    <div style="display:flex;justify-content:space-between;color:#DC2626">
      <span>Saldo devedor atual</span>
      <span style="font-weight:700">R$ {valor_saldo:,.2f}</span>
    </div>
  </div>
  {secao_hist}
  <div style="text-align:center;font-size:10px;color:#888;margin-top:12px;
      border-top:1px dashed #000;padding-top:8px">
    GM Homem Itaúna — Moda Masculina<br>
    Registro do sistema anterior (ERP legado)
  </div>
</div>
<button onclick="imprimirItens()" style="width:100%;margin-top:10px;padding:10px;
    background:#1D4ED8;color:white;border:none;border-radius:8px;
    font-size:14px;cursor:pointer;font-weight:600">
  Imprimir comprovante
</button>
<script>
function imprimirItens() {{
    var c = document.getElementById('cupom-itens').innerHTML;
    var w = window.open('','_blank','width=460,height=650');
    w.document.write('<html><head><title>Comprovante</title>'
        +'<style>body{{font-family:Courier New,monospace;padding:20px;font-size:13px}}'
        +'@media print{{button{{display:none}}}}</style></head><body>'
        +c+'<br><button onclick="window.print();setTimeout(function(){{try{{window.close();}}catch(e){{}}}},1000)" style="width:100%;padding:8px;'
        +'background:#000;color:#fff;border:none;cursor:pointer">Imprimir</button>'
        +'</body></html>');
    w.document.close();
    setTimeout(function(){{w.print()}}, 600);
}}
</script>"""

        components.html(html_cupom, height=650, scrolling=True)

    else:
        df_venda    = dados['venda']
        df_itens    = dados['itens']
        df_parcelas = dados['parcelas']

        if df_venda.empty:
            st.info("Venda não encontrada.")
            return

        row = df_venda.iloc[0]
        data_fmt = str(row['data_venda'])[:10] if isinstance(row['data_venda'], str) else row['data_venda'].strftime('%d/%m/%Y')
        st.markdown(f"""
<div style="background:#1F2937;border-radius:10px;padding:16px;color:white;margin-bottom:12px">
    <div style="font-size:17px;font-weight:700">
        🛍️ Venda {str(row['id'])[:8]}...
    </div>
    <div style="opacity:0.75;margin-top:4px;font-size:13px">
        {data_fmt} · Vendedora: {row.get('vendedor_nome','—')} · {row['forma_pagamento']}
    </div>
</div>""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Total", f"R$ {float(row['valor_total']):,.2f}")
        c2.metric("🏷️ Desconto", f"{float(row.get('desconto_pct',0)):.1f}%")
        c3.metric("📅 Data", data_fmt)

        if not df_itens.empty:
            st.markdown("**🛍️ Produtos desta venda:**")
            st.dataframe(df_itens, use_container_width=True, hide_index=True)
        else:
            cupom = str(row.get('cupom_text', '')).strip()
            if cupom:
                st.markdown("**📋 Cupom da venda:**")
                st.code(cupom, language="text")
            else:
                st.caption("Nenhum item detalhado ou cupom registrado.")

        if not df_parcelas.empty:
            st.markdown("**📋 Parcelas:**")
            df_parcelas_fmt = df_parcelas.copy()
            if 'data_vencimento' in df_parcelas_fmt.columns:
                df_parcelas_fmt['data_vencimento'] = df_parcelas_fmt['data_vencimento'].apply(_fmt_data)
            st.dataframe(df_parcelas_fmt, use_container_width=True, hide_index=True)


def _sanitizar_chave(texto):
    """Sanitiza texto para uso seguro como chave de widget/session_state."""
    return re.sub(r'[^a-zA-Z0-9_]', '_', str(texto))[:50]


def render_painel_baixa_lote(nome_cli, notas_df, perfil):
    """Painel completo de baixa em lote com encargos, atalhos e preview FIFO."""
    from datetime import date as _dt_type
    _kl = _sanitizar_chave(nome_cli)
    hoje_d = _dt_type.today()

    total_original = 0.0
    total_encargos = 0.0
    linhas = []
    for _, nota in notas_df.sort_values('dt_vencimento').iterrows():
        saldo = float(nota['valor_saldo'])
        vcto  = nota['dt_vencimento']
        if hasattr(vcto, 'date'):
            vcto = vcto.date()
        enc = calcular_encargos(saldo, vcto)
        total_original += saldo
        total_encargos += enc['total_encargos']
        linhas.append({
            'ref_id': str(nota['ref_id']),
            'origem': nota['origem'],
            'documento': nota['documento'],
            'vencimento': str(vcto),
            'saldo': saldo,
            'encargos': enc['total_encargos'],
            'dias_atraso': enc['dias_atraso'],
        })

    total_com_enc = total_original + total_encargos
    qtd = len(linhas)

    st.markdown(f"#### 💳 Baixa em Lote — {nome_cli}")
    c1, c2, c3 = st.columns(3)
    c1.metric("📋 Notas", qtd)
    c2.metric("💰 Total original", f"R$ {total_original:,.2f}")
    if total_encargos > 0:
        c3.metric("⚠️ Encargos", f"R$ {total_encargos:,.2f}")
    else:
        c3.metric("✅ Encargos", "R$ 0,00", delta="No prazo")

    with st.expander(f"📋 {qtd} notas selecionadas — detalhamento por nota", expanded=True):
        # Cabeçalho estilo SGA
        st.markdown(
            "<div style='display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;"
            "background:#1F2937;color:white;padding:6px 10px;border-radius:6px;"
            "font-size:12px;font-weight:700;margin-bottom:4px'>"
            "<span>Documento</span><span style='text-align:center'>Vencimento</span>"
            "<span style='text-align:right'>Saldo</span>"
            "<span style='text-align:right'>Juros(0,1%/d)</span>"
            "<span style='text-align:right'>Total</span></div>",
            unsafe_allow_html=True)
        for ln in linhas:
            cor = "#DC2626" if ln['dias_atraso'] > 0 else "#16A34A"
            _dias_str = f"{ln['dias_atraso']}d" if ln['dias_atraso'] > 0 else "ok"
            _total_nota = ln['saldo'] + ln['encargos']
            st.markdown(
                f"<div style='display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;"
                f"padding:5px 10px;border-left:3px solid {cor};background:#F9FAFB;"
                f"margin:2px 0;border-radius:4px;font-size:12px;align-items:center'>"
                f"<span><b>{ln['documento']}</b> "
                f"<span style='color:{cor};font-size:10px'>({_dias_str} atraso)</span></span>"
                f"<span style='text-align:center;color:#6B7280'>{ln['vencimento']}</span>"
                f"<span style='text-align:right'>R$ {ln['saldo']:,.2f}</span>"
                f"<span style='text-align:right;color:{cor}'>+R$ {ln['encargos']:,.2f}</span>"
                f"<span style='text-align:right;font-weight:700'>R$ {_total_nota:,.2f}</span>"
                f"</div>",
                unsafe_allow_html=True)
        st.markdown(
            f"<div style='display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;"
            f"background:#1F2937;color:white;padding:6px 10px;border-radius:6px;"
            f"font-size:12px;font-weight:700;margin-top:4px'>"
            f"<span>TOTAL ({qtd} notas)</span><span></span>"
            f"<span style='text-align:right'>R$ {total_original:,.2f}</span>"
            f"<span style='text-align:right'>+R$ {total_encargos:,.2f}</span>"
            f"<span style='text-align:right'>R$ {total_com_enc:,.2f}</span>"
            f"</div>",
            unsafe_allow_html=True)

    isentar = False
    isentar_parcial_pct = 0
    valor_base = total_com_enc
    _kv = f'vl_{_kl}'
    if perfil in ['admin_master', 'admin', 'gerencial']:
        _tipo = st.radio(
            "Encargos:",
            ["Cobrar integrais", "Isencao total", "Isencao parcial (%)"],
            key=f'tipo_isent_lote_{_kl}', horizontal=True,
            label_visibility="collapsed")
        if _tipo == "Isencao total":
            isentar = True
            valor_base = total_original
            st.success(f"Encargos isentados. Cobrar apenas: R$ {total_original:,.2f}")
        elif _tipo == "Isencao parcial (%)":
            _pct = st.slider("Desconto %", 10, 90, 50, 10,
                             key=f'pct_isent_lote_{_kl}', format="%d%%")
            isentar_parcial_pct = _pct
            _enc_total = total_com_enc - total_original
            _enc_cobrar = round(_enc_total * (1 - _pct/100), 2)
            valor_base = total_original + _enc_cobrar
            st.info(f"{_pct}% de desconto nos encargos. Total: R$ {valor_base:,.2f}")

        _new_vl = round(valor_base, 2)
        if st.session_state.get(_kv) != _new_vl:
            st.session_state[_kv] = _new_vl
            st.rerun()

    val_lote = st.number_input(
        "💡 Valor total recebido",
        min_value=0.01,
        max_value=float(valor_base * 3),
        value=float(st.session_state.get(_kv, round(valor_base, 2))),
        format="%.2f",
        key=f'vinp_{_kl}',
        help="FIFO — quita notas mais antigas primeiro"
    )
    forma_lote = st.selectbox(
        "Forma de recebimento",
        ["Dinheiro", "Pix", "Cartão Débito", "Cartão Crédito", "Transferência"],
        key=f'fl_{_kl}'
    )

    if val_lote < total_original * 0.999:
        resto = val_lote
        n_quit = sum(1 for ln in linhas if resto >= ln['saldo'] * 0.999 or (resto := resto - ln['saldo']) is not None and False)
        # simples: conta quantas quita FIFO
        resto2 = val_lote
        n_quit2 = 0
        for ln in linhas:
            if resto2 >= ln['saldo'] * 0.999:
                n_quit2 += 1
                resto2 -= ln['saldo']
            else:
                break
        n_aberto = qtd - n_quit2
        st.warning(f"⚡ **Baixa parcial** — quita {n_quit2} nota(s), mantém {n_aberto} em aberto. Saldo: R$ {total_original - val_lote:,.2f}")
    else:
        st.success(f"✅ Quitação total — todas as {qtd} notas serão quitadas")

    col_conf, col_canc = st.columns(2)
    if col_conf.button(f"✅ CONFIRMAR BAIXA — R$ {val_lote:,.2f}", type="primary",
                       use_container_width=True, key=f'conf_lote_{_kl}'):
        _executar_baixa_em_lote_v2(nome_cli, val_lote, forma_lote,
                                    notas_df.sort_values('dt_vencimento'),
                                    isentar, linhas)
    if col_canc.button("✕ Cancelar", use_container_width=True, key=f'canc_lote_{_kl}'):
        for _k in [f'lote_sel_{_kl}', _kv, f'sel_{_kl}']:
            st.session_state.pop(_k, None)
        st.rerun()


def _executar_baixa_em_lote_v2(nome_cli, valor_total, forma, df_notas, isentar, linhas):
    """Executa baixa FIFO e gera cupom consolidado HTML."""
    from datetime import date as _dt_type, datetime as _datetime
    operador = st.session_state.get('usuario', 'sistema')
    hoje = _dt_type.today()
    agora = _datetime.now().strftime("%d/%m/%Y %H:%M")

    saldo_rest = valor_total
    resumo_baixas = []

    with _db_get_conn() as conn:
        cur = conn.cursor()
        for ln in linhas:
            if saldo_rest <= 0:
                break
            saldo_nota = ln['saldo']
            ref_id = ln['ref_id']
            origem = ln['origem']

            if saldo_rest >= saldo_nota * 0.999:
                valor_baixado = saldo_nota
                saldo_novo = 0.0
                tipo_str = '✅ Quitada'
                if origem == 'legado':
                    cur.execute("""UPDATE duplicatas_abertas
                        SET status='Pago', dt_baixa=%s, valor_saldo=0,
                            valor_pago_total=COALESCE(valor_pago_total,0)+%s,
                            forma_recebimento=%s, isentou_encargos=%s
                        WHERE id=%s""",
                        (hoje, valor_baixado, forma, isentar, int(ref_id)))
                else:
                    cur.execute("UPDATE contas_receber SET status='Pago' WHERE id=%s::uuid", (ref_id,))
            else:
                valor_baixado = saldo_rest
                saldo_novo = round(saldo_nota - valor_baixado, 2)
                tipo_str = f'⚡ Parcial — saldo R$ {saldo_novo:,.2f}'
                if origem == 'legado':
                    cur.execute("""UPDATE duplicatas_abertas
                        SET valor_saldo=%s,
                            valor_pago_total=COALESCE(valor_pago_total,0)+%s,
                            forma_recebimento=%s
                        WHERE id=%s""",
                        (saldo_novo, valor_baixado, forma, int(ref_id)))
                else:
                    cur.execute("UPDATE contas_receber SET valor_parcela=%s WHERE id=%s::uuid",
                                (saldo_novo, ref_id))

            cur.execute("""INSERT INTO movimentos_financeiros
                (parcela_id, origem, valor_pago, forma_pagamento, isentou_encargos,
                 saldo_anterior, saldo_posterior, operador, data_movimento)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW())""",
                (ref_id, origem, valor_baixado, forma, isentar,
                 saldo_nota, saldo_novo, operador))

            resumo_baixas.append({
                'documento': ln['documento'],
                'vencimento': ln['vencimento'],
                'valor_baixado': valor_baixado,
                'saldo_novo': saldo_novo,
                'tipo': tipo_str,
            })
            saldo_rest -= valor_baixado

    # Limpar estados
    _kl = _sanitizar_chave(nome_cli)
    for _k in [f'lote_sel_{_kl}', f'vl_{_kl}']:
        st.session_state.pop(_k, None)
    st.session_state[f'sel_{_kl}'] = []

    n_quit = sum(1 for r in resumo_baixas if 'Quitada' in r['tipo'])
    n_parc = len(resumo_baixas) - n_quit

    linhas_html = ""
    for r in resumo_baixas:
        cor = "#16A34A" if "Quitada" in r['tipo'] else "#D97706"
        linhas_html += (
            f"<tr><td style='padding:4px'>{r['documento']}</td>"
            f"<td style='text-align:center;padding:4px'>{r['vencimento']}</td>"
            f"<td style='text-align:right;padding:4px'>R$ {r['valor_baixado']:,.2f}</td>"
            f"<td style='color:{cor};text-align:center;padding:4px'>{r['tipo']}</td></tr>"
        )

    nome_esc = nome_cli.replace("'", "\\'")
    html_cupom = f"""
<div id="cupom-lote" style="font-family:'Courier New',monospace;max-width:500px;
    margin:0 auto;padding:20px;border:2px solid #000;border-radius:8px;background:#fff;color:#000">
    <div style="text-align:center;border-bottom:2px dashed #000;padding-bottom:12px;margin-bottom:12px">
        <div style="font-size:20px;font-weight:700">LOJA GM HOMEM ITAÚNA</div>
        <div style="font-size:12px;color:#555">PDV & Gestão · JGAutomações.AI · {agora}</div>
    </div>
    <div style="margin-bottom:10px;font-size:13px">
        <div><b>Cliente:</b> {nome_cli}</div>
        <div><b>Forma:</b> {forma}</div>
        {"<div style='color:#D97706;font-size:11px'>* Encargos isentados por gerencial</div>" if isentar else ""}
    </div>
    <table style="width:100%;font-size:12px;border-collapse:collapse;margin-bottom:10px">
        <tr style="background:#f0f0f0;font-weight:700">
            <th style="text-align:left;padding:4px">Nota</th>
            <th style="text-align:center;padding:4px">Venc.</th>
            <th style="text-align:right;padding:4px">Pago</th>
            <th style="text-align:center;padding:4px">Status</th>
        </tr>
        {linhas_html}
    </table>
    <div style="border-top:2px dashed #000;padding-top:10px">
        <table style="width:100%;font-size:14px">
            <tr><td><b>TOTAL RECEBIDO</b></td>
                <td style="text-align:right;font-size:18px;font-weight:700">R$ {valor_total:,.2f}</td></tr>
            <tr><td style="font-size:12px">{n_quit} nota(s) quitada(s)</td>
                <td style="text-align:right;font-size:12px">{n_parc} parcial(is)</td></tr>
        </table>
    </div>
    <div style="text-align:center;font-size:11px;color:#888;margin-top:10px;
        border-top:1px dashed #000;padding-top:8px">
        Obrigada pela preferência! 💜<br>GM Homem Itaúna — Moda Masculina
    </div>
</div>
<button onclick="imprimirLote()" style="width:100%;margin-top:12px;padding:12px;
    background:#1D4ED8;color:white;border:none;border-radius:8px;font-size:15px;cursor:pointer;font-weight:600">
    🖨️ Imprimir Cupom Consolidado
</button>
<script>
function imprimirLote() {{
    var c = document.getElementById('cupom-lote').outerHTML;
    var w = window.open('','_blank','width=520,height=700');
    w.document.write('<html><head><title>Cupom Lote - {nome_esc}</title>');
    w.document.write('<style>body{{font-family:"Courier New",monospace;padding:20px}}@media print{{button{{display:none}}}}</style>');
    w.document.write('</head><body>'+c);
    w.document.write('<br><button onclick="window.print();setTimeout(function(){{try{{window.close();}}catch(e){{}}}},1000)" style="width:100%;padding:10px;background:#000;color:#fff;border:none;font-size:14px;cursor:pointer">🖨️ Confirmar Impressão</button>');
    w.document.write('</body></html>');
    w.document.close();
    setTimeout(function(){{w.print()}},600);
}}
</script>
"""
    components.html(html_cupom, height=550, scrolling=True)
    st.rerun()

def render_recebimentos_nasa(perfil):
    # Redirecionamento da GM Homem AI
    if st.session_state.get('_nav_target') == 'Recebimentos':
        del st.session_state['_nav_target']
    # Texto de busca injetado pela GM Homem AI
    _busca_injetada = st.session_state.pop('_busca_rec_texto', None)
    _filtro_rapido = st.session_state.pop('_filtro_rapido_rec', None)
    _filtro_rapido = st.session_state.pop('_filtro_rapido_rec', None)
    
    """Tela única de recebimentos — arquitetura NASA."""
    import streamlit.components.v1 as _cmp
    from datetime import date as _d

    # Força scroll para o topo sempre que a página renderizar
    _cmp.html("""<script>
    window.parent.document.querySelector('section.main').scrollTo({top:0,behavior:'instant'});
    </script>""", height=0)

    # ── KPIs ─────────────────────────────────────────────────────────────────
    kpis  = run_query("""
        SELECT
            COALESCE(SUM(CASE WHEN dt_vencimento < CURRENT_DATE THEN valor_saldo ELSE 0 END),0) AS vencido,
            COALESCE(SUM(CASE WHEN dt_vencimento = CURRENT_DATE THEN valor_saldo ELSE 0 END),0) AS hoje,
            COALESCE(SUM(CASE WHEN dt_vencimento > CURRENT_DATE
                               AND dt_vencimento <= CURRENT_DATE+7 THEN valor_saldo ELSE 0 END),0) AS prox_7d,
            COALESCE(SUM(valor_saldo),0) AS total_carteira,
            COALESCE(SUM(CASE WHEN dt_vencimento > CURRENT_DATE THEN valor_saldo ELSE 0 END),0) AS a_vencer,
            COALESCE(SUM(valor_saldo),0) AS total_carteira2,
            COUNT(DISTINCT codigo_cliente) AS clientes_inadimplentes
        FROM duplicatas_abertas
        WHERE status='Pendente'
    """)
    kpis2 = run_query("""
        SELECT
            COALESCE(SUM(CASE WHEN cr.data_vencimento < CURRENT_DATE THEN cr.valor_parcela ELSE 0 END),0) AS vencido,
            COALESCE(SUM(CASE WHEN cr.data_vencimento = CURRENT_DATE THEN cr.valor_parcela ELSE 0 END),0) AS hoje,
            COALESCE(SUM(cr.valor_parcela),0) AS total_carteira
        FROM contas_receber cr WHERE cr.status='aberto'
    """)
    vencido  = float(kpis['vencido'].iloc[0])  + 0  # contas_receber desativado — dados em duplicatas_abertas
    hoje_val = float(kpis['hoje'].iloc[0])     + 0
    prox_7d  = float(kpis['prox_7d'].iloc[0])
    a_vencer = float(kpis['a_vencer'].iloc[0]) if 'a_vencer' in kpis.columns else prox_7d
    total    = float(kpis['total_carteira'].iloc[0]) + 0  # cr desativado
    n_inad   = int(kpis['clientes_inadimplentes'].iloc[0])

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"""<div style="background:#DC2626;padding:16px;border-radius:12px;color:white">
        <div style="font-size:12px;opacity:0.85">🔴 VENCIDO</div>
        <div style="font-size:24px;font-weight:700">R$ {vencido:,.2f}</div>
        <div style="font-size:11px;opacity:0.75">{n_inad} clientes</div></div>""",
        unsafe_allow_html=True)
    c2.markdown(f"""<div style="background:#D97706;padding:16px;border-radius:12px;color:white">
        <div style="font-size:12px;opacity:0.85">🟡 VENCE HOJE</div>
        <div style="font-size:24px;font-weight:700">R$ {hoje_val:,.2f}</div></div>""",
        unsafe_allow_html=True)
    c3.markdown(f"""<div style="background:#1D4ED8;padding:16px;border-radius:12px;color:white">
        <div style="font-size:12px;opacity:0.85">📅 A VENCER</div>
        <div style="font-size:24px;font-weight:700">R$ {a_vencer:,.2f}</div></div>""",
        unsafe_allow_html=True)
    c4.markdown(f"""<div style="background:#1F2937;padding:16px;border-radius:12px;color:white">
        <div style="font-size:12px;opacity:0.85">💰 CARTEIRA TOTAL</div>
        <div style="font-size:24px;font-weight:700">R$ {total:,.2f}</div></div>""",
        unsafe_allow_html=True)

    st.markdown("""
<style>
.kpi-card{padding:20px;border-radius:16px;color:white;box-shadow:0 4px 6px rgba(0,0,0,.15)}
div[data-testid="stButton"] button{border-radius:8px!important;font-weight:500!important;transition:all .2s!important}
.badge-atraso{display:inline-block;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600}
</style>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Barra de busca ────────────────────────────────────────────────────────
    col_busca, col_pdf = st.columns([5, 1])
    with col_busca:
        # Autocomplete de clientes
        busca = st.text_input(
            "", placeholder="🔍 Digite o nome do cliente...",
            key="busca_rec_txt2", label_visibility="collapsed"
        )
    with col_pdf:
        if perfil in ['admin', 'admin_master']:
            if st.button("📄 PDF", key="btn_pdf_final", use_container_width=True):
                st.session_state['exportar_pdf_rec'] = True
    filtro = "Todos"

    if _filtro_rapido:
        busca = _filtro_rapido
    if _filtro_rapido:
        busca = _filtro_rapido
    busca_ativa = busca.strip() != ""
    # Se buscando por nome, mostrar todos independente do filtro
    if busca_ativa:
        _ws = ""
        _ws2 = ""
    # Se buscando por nome, mostrar todos independente do filtro
    if busca_ativa:
        _ws = ""
        _ws2 = ""

    _ws  = {"Vencidos": "AND da.dt_vencimento < CURRENT_DATE",
            "Vence Hoje": "AND da.dt_vencimento = CURRENT_DATE",
            "A Vencer":  "AND da.dt_vencimento > CURRENT_DATE",
            "Vence este Mês": "AND DATE_TRUNC('month', da.dt_vencimento) = DATE_TRUNC('month', CURRENT_DATE)"}.get(filtro, "")
    _ws2 = {"Vencidos": "AND cr.data_vencimento < CURRENT_DATE",
            "Vence Hoje": "AND cr.data_vencimento = CURRENT_DATE",
            "A Vencer":  "AND cr.data_vencimento > CURRENT_DATE"}.get(filtro, "")

    if busca_ativa:
        _b = busca.strip().replace("'", "''")  # SQL-safe
        _b_norm = _b.replace("/", " ").replace("\\", " ").strip()
        _where_leg = f"""AND (
            UPPER(REPLACE(COALESCE(da.nome_cliente,''), '/', ' ')) LIKE UPPER('%{_b_norm}%')
            OR UPPER(COALESCE(da.nome_cliente,'')) LIKE UPPER('%{_b}%')
            OR da.documento LIKE '%{_b}%'
        )"""
        _where_ban = f"""AND (
            UPPER(REPLACE(c.nome, '/', ' ')) LIKE UPPER('%{_b_norm}%')
            OR UPPER(c.nome) LIKE UPPER('%{_b}%')
        )"""
    else:
        _where_leg = ""
        _where_ban = ""

    # ══════════════════════════════════════════════════════
    # QUERY UNIFICADA: parte dos clientes, mostra TODOS
    # Com busca: filtra por nome em clientes + duplicatas
    # Sem busca: mostra todos com pendências
    # ══════════════════════════════════════════════════════

    if busca_ativa:
        # Com busca: buscar em todas as tabelas
        _b_norm = busca.strip().replace("/", " ").replace("'", "''")
        _b_safe = busca.strip().replace("'", "''")
        q_leg = f"""
            SELECT da.id::text AS ref_id,
                   da.codigo_cliente,
                   COALESCE(da.nome_cliente,'Cliente '||da.codigo_cliente) AS nome_cliente,
                   COALESCE(cl.cpf,'') AS cpf,
                   COALESCE(cl.celular,'') AS whatsapp,
                   da.documento,
                   da.dt_emissao,
                   da.dt_vencimento,
                   da.valor_original,
                   da.valor_saldo,
                   da.modalidade,
                   COALESCE(da.observacao,'') AS observacao,
                   COALESCE(da.vendedor,'') AS vendedor,
                   da.status AS status_parcela,
                   'legado' AS origem,
                   GREATEST(0, CURRENT_DATE - da.dt_vencimento) AS dias_atraso
            FROM duplicatas_abertas da
            LEFT JOIN clientes_legados cl ON da.codigo_cliente = cl.codigo_legado
            WHERE (
                UPPER(REPLACE(COALESCE(da.nome_cliente,''), '/', ' ')) LIKE UPPER('%{_b_norm}%')
                OR UPPER(COALESCE(da.nome_cliente,'')) LIKE UPPER('%{_b_safe}%')
                OR da.documento LIKE '%{_b_safe}%'
                OR da.codigo_cliente LIKE '%{_b_safe}%'
            )
            ORDER BY da.status DESC, da.dt_vencimento
        """
    else:
        # Sem busca: mostrar todos com pendências
        q_leg = f"""
            SELECT da.id::text AS ref_id,
                   da.codigo_cliente,
                   COALESCE(da.nome_cliente,'Cliente '||da.codigo_cliente) AS nome_cliente,
                   COALESCE(cl.cpf,'') AS cpf,
                   COALESCE(cl.celular,'') AS whatsapp,
                   da.documento,
                   da.dt_emissao,
                   da.dt_vencimento,
                   da.valor_original,
                   da.valor_saldo,
                   da.modalidade,
                   COALESCE(da.observacao,'') AS observacao,
                   COALESCE(da.vendedor,'') AS vendedor,
                   da.status AS status_parcela,
                   'legado' AS origem,
                   GREATEST(0, CURRENT_DATE - da.dt_vencimento) AS dias_atraso
            FROM duplicatas_abertas da
            LEFT JOIN clientes_legados cl ON da.codigo_cliente = cl.codigo_legado
            WHERE da.status = 'Pendente' {_ws}
            ORDER BY da.dt_vencimento
        """

    df_leg = run_query(q_leg)

    # contas_receber — só vendas recentes do sistema novo
    if busca_ativa:
        _b_norm = busca.strip().replace("/", " ").replace("'", "''")
        _b_safe = busca.strip().replace("'", "''")
        q_ban = f"""
            SELECT cr.id::text AS ref_id,
                   c.id::text AS codigo_cliente,
                   c.nome AS nome_cliente,
                   COALESCE(c.cpf,'') AS cpf,
                   COALESCE(c.whatsapp,'') AS whatsapp,
                   'CR-'||SUBSTRING(cr.id::text, 1, 8) AS documento,
                   v.data_venda::date AS dt_emissao,
                   cr.data_vencimento AS dt_vencimento,
                   cr.valor_parcela AS valor_original,
                   cr.valor_parcela AS valor_saldo,
                   v.forma_pagamento AS modalidade,
                   '' AS observacao,
                   '' AS vendedor,
                   cr.status AS status_parcela,
                   'banco' AS origem,
                   GREATEST(0, CURRENT_DATE - cr.data_vencimento) AS dias_atraso
            FROM contas_receber cr
            JOIN vendas v ON cr.venda_id = v.id
            JOIN clientes c ON v.cliente_id = c.id
            WHERE (UPPER(REPLACE(c.nome, '/', ' ')) LIKE UPPER('%{_b_norm}%')
                   OR UPPER(c.nome) LIKE UPPER('%{_b_safe}%'))
            ORDER BY cr.data_vencimento
        """
    else:
        q_ban = f"""
            SELECT cr.id::text AS ref_id,
                   c.id::text AS codigo_cliente,
                   c.nome AS nome_cliente,
                   COALESCE(c.cpf,'') AS cpf,
                   COALESCE(c.whatsapp,'') AS whatsapp,
                   'CR-'||SUBSTRING(cr.id::text, 1, 8) AS documento,
                   v.data_venda::date AS dt_emissao,
                   cr.data_vencimento AS dt_vencimento,
                   cr.valor_parcela AS valor_original,
                   cr.valor_parcela AS valor_saldo,
                   v.forma_pagamento AS modalidade,
                   '' AS observacao,
                   '' AS vendedor,
                   cr.status AS status_parcela,
                   'banco' AS origem,
                   GREATEST(0, CURRENT_DATE - cr.data_vencimento) AS dias_atraso
            FROM contas_receber cr
            JOIN vendas v ON cr.venda_id = v.id
            JOIN clientes c ON v.cliente_id = c.id
            WHERE cr.status = 'aberto' {_ws2}
              AND (v.forma_pagamento ILIKE '%credi%' OR v.parcelas > 1)
            ORDER BY cr.data_vencimento
        """

    df_ban = run_query(q_ban)
    df = pd.concat([df_leg, df_ban], ignore_index=True)

    # Remover duplicatas de nome+documento
    if not df.empty:
        df = df.drop_duplicates(subset=['nome_cliente', 'documento'], keep='first')
        df = df.sort_values('dt_vencimento').reset_index(drop=True)

    if df.empty:
        st.success("✅ Nenhum recebível em aberto!" if not busca else f"Nenhum resultado para '{busca}'")
        return

    st.caption(
        f"**{len(df)} parcela(s)** · R$ {float(df['valor_saldo'].sum()):,.2f} em aberto "
        f"· {df['nome_cliente'].nunique()} clientes"
    )

    # ── Ordenação ─────────────────────────────────────────────────────────────
    ordenar_por = st.radio("Ordenar por:", ["Todos", "Maior atraso", "A-Z", "Maior valor", "A Vencer"],
                           horizontal=True, key="ord_clientes_rec",
                           index=None,
                           label_visibility="collapsed")
    if ordenar_por is None:
        ordenar_por = "Maior atraso"

    # ── Cards por cliente ─────────────────────────────────────────────────────
    clientes_df = (df.groupby('nome_cliente', sort=False)
                     .agg(total_saldo=('valor_saldo','sum'),
                          qtd=('ref_id','count'),
                          max_atraso=('dias_atraso','max'),
                          prox_vcto=('dt_vencimento','min'))
                     .reset_index())
    if ordenar_por == "A-Z":
        clientes_df = clientes_df.sort_values('nome_cliente')
    elif ordenar_por == "Maior valor":
        clientes_df = clientes_df.sort_values('total_saldo', ascending=False)
    elif ordenar_por == "Todos":
        clientes_df = clientes_df.sort_values("max_atraso", ascending=False)
    elif ordenar_por == "A Vencer":
        clientes_df = clientes_df.sort_values('prox_vcto')
    else:
        clientes_df = clientes_df.sort_values('max_atraso', ascending=False)

    hoje_d = _d.today()

    for _, cli in clientes_df.iterrows():
        nome     = cli['nome_cliente']
        total_c  = float(cli['total_saldo'])
        qtd      = int(cli['qtd'])
        atraso   = int(cli['max_atraso'])
        prox     = cli['prox_vcto']
        if hasattr(prox, 'date'):
            prox = prox.date()
        _sk_nome = _sanitizar_chave(nome)  # chave segura derivada do nome

        if atraso > 0:
            cor_borda = "#DC2626"; badge = f"🔴 {atraso}d atraso"
            badge_css = "background:#DC2626;color:white"
        elif prox == hoje_d:
            cor_borda = "#D97706"; badge = "🟡 Vence hoje"
            badge_css = "background:#D97706;color:white"
        else:
            cor_borda = "#1D4ED8"; badge = "🔵 A vencer"
            badge_css = "background:#1D4ED8;color:white"

        with st.expander(
            f"**{nome}** — R$ {total_c:,.2f} ({qtd} nota{'s' if qtd > 1 else ''})",
            expanded=(atraso > 0 and bool(busca))
        ):
            st.markdown(
                f"""<div style="display:flex;gap:8px;margin-bottom:10px;flex-wrap:wrap">
                <span style="padding:4px 12px;border-radius:20px;font-size:12px;{badge_css}">{badge}</span>
                <span style="padding:4px 12px;border-radius:20px;font-size:12px;
                      background:#1e293b;color:#94a3b8">{qtd} nota{'s' if qtd>1 else ''} · R$ {total_c:,.2f}</span>
                </div>""", unsafe_allow_html=True)

            notas = df[df['nome_cliente'] == nome].copy()

            # ── Seleção múltipla ──────────────────────────────────────────────
            _k_sel    = f'sel_{_sk_nome}'
            notas_ids = notas['ref_id'].astype(str).tolist()
            if _k_sel not in st.session_state:
                st.session_state[_k_sel] = []

            _n_sel   = len([x for x in notas_ids if x in st.session_state[_k_sel]])
            _n_total = len(notas_ids)
            _todas   = _n_sel == _n_total and _n_total > 0

            col_sel_all, col_sel_count = st.columns([2, 5])
            with col_sel_all:
                if st.checkbox(f"Selecionar todas ({_n_total})",
                               value=_todas, key=f'ca_{_sk_nome}'):
                    if not _todas:
                        st.session_state[_k_sel] = list(notas_ids)
                        st.rerun()
                else:
                    if _todas:
                        st.session_state[_k_sel] = []
                        st.rerun()
            with col_sel_count:
                if _n_sel > 0:
                    _tot_info = notas[notas['ref_id'].astype(str).isin(
                        st.session_state[_k_sel])]['valor_saldo'].sum()
                    st.info(f"**{_n_sel} nota(s) · R$ {float(_tot_info):,.2f}** selecionada(s)")

            # ── Loop de notas ─────────────────────────────────────────────────
            for _, nota in notas.iterrows():
                saldo_n = float(nota['valor_saldo'])
                vcto_n  = nota['dt_vencimento']
                if hasattr(vcto_n, 'date'):
                    vcto_n = vcto_n.date()
                enc_n   = calcular_encargos(saldo_n, vcto_n)
                dias_n  = int(nota['dias_atraso'])
                _rid_n  = str(nota['ref_id']).strip()
                _sk_id  = _sanitizar_chave(_rid_n)
                _k_ver  = f'stv_{_sk_id}_{_sk_nome}'
                _k_bx   = f'stb_{_sk_id}_{_sk_nome}'

                cor_linha   = "#3a1a1a" if dias_n > 0 else "#2d2a1a" if vcto_n == hoje_d else "#1a1a2a"
                cor_borda_n = "#DC2626" if dias_n > 0 else ("#D97706" if vcto_n == hoje_d else "#1D4ED8")
                status_n    = f"🔴 {dias_n}d atraso" if dias_n > 0 else ("🟡 Hoje" if vcto_n == hoje_d else "🔵 A vencer")

                col_chk, col_info, col_acoes = st.columns([0.5, 3.5, 1.5])

                with col_chk:
                    _marcado_atual = _rid_n in st.session_state.get(_k_sel, [])
                    # Inicializar key no session_state para o Streamlit respeitar value=
                    _ck_key = f'ci_{_sk_id}_{_sk_nome}'
                    if _ck_key not in st.session_state:
                        st.session_state[_ck_key] = _marcado_atual
                    else:
                        # Sincronizar: se selecionar todas mudou, atualizar o widget
                        st.session_state[_ck_key] = _marcado_atual
                    _novo = st.checkbox("", key=_ck_key,
                                   label_visibility="collapsed")
                    if _novo != _marcado_atual:
                        _lst = list(st.session_state.get(_k_sel, []))
                        if _novo and _rid_n not in _lst:
                            _lst.append(_rid_n)
                        elif not _novo and _rid_n in _lst:
                            _lst.remove(_rid_n)
                        st.session_state[_k_sel] = _lst
                        st.rerun()

                with col_info:
                    import html as _he
                    _enc = ""
                    if enc_n['em_atraso']:
                        _enc = "<div style='font-size:11px;color:#f87171'>+R$ " + "{:.2f}".format(enc_n['total_encargos']) + " encargos</div>"
                    _obs_r = str(nota.get('observacao') or "")
                    _obs_t = " - " + _he.escape(_obs_r) if _obs_r else ""
                    _doc = str(nota['documento'])
                    _emi = _fmt_data(nota['dt_emissao'])
                    _vcto = _fmt_data(vcto_n)
                    _sal = "{:.2f}".format(saldo_n)
                    _mod = str(nota['modalidade'])
                    _ori = str(nota['origem'])
                    _html = "<div style='background:" + cor_linha + ";padding:10px 14px;border-radius:8px;border-left:3px solid " + cor_borda_n + ";margin-bottom:4px'>"
                    _html += "<div style='display:flex;justify-content:space-between;align-items:center'>"
                    _html += "<div><span style='font-weight:600;color:#f1f5f9'>Nota " + _doc + "</span>"
                    _html += "<span style='font-size:12px;color:#64748b;margin-left:8px'>Emissao: " + _emi + " - Venc: " + _vcto + "</span></div>"
                    _html += "<div style='text-align:right'><div style='font-weight:700;font-size:16px;color:#f1f5f9'>R$ " + _sal + "</div>" + _enc + "</div>"
                    _html += "</div>"
                    _html += "<div style='font-size:11px;color:#64748b;margin-top:4px'>" + status_n + " - " + _mod + " - " + _ori + _obs_t + "</div>"
                    _html += "</div>"
                    st.markdown(_html, unsafe_allow_html=True)
                with col_acoes:
                    _lbl_ver = "✕ Fechar" if st.session_state.get(_k_ver) else "🔍 Ver Itens"
                    if st.button(_lbl_ver, key=f"bv_{_sk_id}_{_sk_nome}",
                                 use_container_width=True):
                        st.session_state[_k_ver] = not st.session_state.get(_k_ver, False)
                        st.rerun()
                    _lbl_bx  = "✕ Cancelar" if st.session_state.get(_k_bx) else "💳 Dar Baixa"
                    _tipo_bx = "secondary" if st.session_state.get(_k_bx) else "primary"
                    if st.button(_lbl_bx, key=f"bb_{_sk_id}_{_sk_nome}",
                                 use_container_width=True, type=_tipo_bx):
                        _novo_bx = not st.session_state.get(_k_bx, False)
                        for _kk in list(st.session_state.keys()):
                            if _kk.startswith('stb_') and _kk != _k_bx:
                                st.session_state[_kk] = False
                        st.session_state[_k_bx] = _novo_bx
                        st.rerun()

                # Ver Itens — expande abaixo
                if st.session_state.get(_k_ver):
                    with st.container(border=True):
                        render_ver_itens_nota(
                            str(nota['documento']),
                            str(nota.get('codigo_cliente', '')),
                            nota.get('origem', 'legado')
                        )
                    if st.button("✕ Fechar detalhes",
                                 key=f"fv_{_sk_id}_{_sk_nome}",
                                 use_container_width=False):
                        st.session_state[_k_ver] = False
                        st.rerun()

                # Dar Baixa — expande abaixo
                if st.session_state.get(_k_bx):
                    with st.container(border=True):
                        render_painel_baixa_nasa(nota.to_dict(), perfil,
                                                 state_key=_k_bx)

            # ── Painel baixa em lote ──────────────────────────────────────────
            _notas_sel_agora = [x for x in st.session_state.get(_k_sel, [])
                                if x in notas_ids]
            if _notas_sel_agora:
                import pandas as _pd_lote
                from datetime import date as _dt_hoje_lote
                _df_sel  = notas[notas['ref_id'].astype(str).isin(_notas_sel_agora)]
                _tot_sel = float(_df_sel['valor_saldo'].sum())
                _qtd_sel = len(_notas_sel_agora)
                # Calcular juros nota por nota (igual SGA)
                _tot_enc_lote = 0.0
                _hoje_lote = _dt_hoje_lote.today()
                for _, _nl in _df_sel.iterrows():
                    _vl = float(_nl['valor_saldo'])
                    _vt = _nl['dt_vencimento']
                    if hasattr(_vt, 'date'): _vt = _vt.date()
                    if isinstance(_vt, str):
                        from datetime import datetime as _dtp
                        try: _vt = _dtp.strptime(str(_vt), '%Y-%m-%d').date()
                        except: pass
                    try:
                        _dias_l = (_hoje_lote - _vt).days if _vt < _hoje_lote else 0
                    except: _dias_l = 0
                    _tot_enc_lote += round(_vl * 0.001 * _dias_l, 2) if _dias_l > 0 else 0.0
                _tot_enc_lote = round(_tot_enc_lote, 2)
                _tot_com_enc  = round(_tot_sel + _tot_enc_lote, 2)
                st.markdown(
                    f"<div style='background:#1E3A5F;padding:12px 16px;"
                    f"border-radius:10px;color:white;margin:8px 0'>"
                    f"<b>{_qtd_sel} nota(s) selecionada(s) "
                    f"· Saldo: R$ {_tot_sel:,.2f} "
                    f"· Juros: +R$ {_tot_enc_lote:,.2f} "
                    f"· Total: R$ {_tot_com_enc:,.2f}</b></div>",
                    unsafe_allow_html=True)
                _col_bx_s, _col_cl_s = st.columns([4, 1])
                with _col_bx_s:
                    if st.button(
                        f"💰 Dar Baixa nas {_qtd_sel} notas — R$ {_tot_com_enc:,.2f}",
                        type="primary", use_container_width=True,
                        key=f'blote_{_sk_nome}'
                    ):
                        st.session_state[f'lote_sel_{_sk_nome}'] = {
                            'ids': _notas_sel_agora, 'total': _tot_sel,
                            'df': _df_sel.to_dict('records')}
                with _col_cl_s:
                    if st.button("✕ Limpar", key=f'clr_{_sk_nome}',
                                 use_container_width=True):
                        st.session_state[_k_sel] = []
                        st.session_state.pop(f'lote_sel_{_sk_nome}', None)
                        st.rerun()
            else:
                st.session_state.pop(f'lote_sel_{_sk_nome}', None)

            _lote_sel_key = f'lote_sel_{_sk_nome}'
            if st.session_state.get(_lote_sel_key):
                _ld = st.session_state[_lote_sel_key]
                with st.container(border=True):
                    import pandas as _pd_lote2
                    render_painel_baixa_lote(
                        nome,
                        _pd_lote2.DataFrame(_ld['df']),
                        perfil
                    )

    if st.session_state.get('exportar_pdf_rec') and not df.empty:
        from datetime import datetime as _dt_now
        _titulo = f"Filtro: {filtro}" if filtro != "Todos" else "Todos os recebíveis"
        _busca_info = f" | Busca: {busca}" if busca.strip() else ""
        _linhas_html = ""
        for _, _row in df.iterrows():
            _dias = int(_row.get('dias_atraso', 0))
            _cor = "#DC2626" if _dias > 0 else "#1D4ED8"
            _dt_venc_fmt = _fmt_data(_row.get('dt_vencimento', None))
            _linhas_html += (
                f"<tr><td style='padding:4px 6px'>{_row['nome_cliente']}</td>"
                f"<td style='text-align:center;padding:4px 6px'>{_row.get('documento','—')}</td>"
                f"<td style='text-align:center;padding:4px 6px'>{_dt_venc_fmt}</td>"
                f"<td style='text-align:right;padding:4px 6px'>R$ {float(_row['valor_saldo']):,.2f}</td>"
                f"<td style='text-align:center;color:{_cor};padding:4px 6px'>"
                f"{''+str(_dias)+'d atraso' if _dias > 0 else 'No prazo'}</td></tr>"
            )
        _html_pdf = f"""
<div style="font-family:Arial,sans-serif;padding:16px;color:#000">
    <div style="text-align:center;border-bottom:2px solid #000;padding-bottom:10px;margin-bottom:14px">
        <h2 style="margin:0">LOJA GM HOMEM ITAÚNA</h2>
        <h3 style="margin:4px 0;color:#555">Relatório de Recebíveis</h3>
        <div style="font-size:12px">{_titulo}{_busca_info} · {_dt_now.now().strftime('%d/%m/%Y %H:%M')}</div>
        <div style="font-size:12px">{len(df)} parcelas · R$ {float(df['valor_saldo'].sum()):,.2f}</div>
    </div>
    <table style="width:100%;border-collapse:collapse;font-size:11px">
        <thead>
            <tr style="background:#1F2937;color:white">
                <th style="padding:6px;text-align:left">Cliente</th>
                <th style="padding:6px;text-align:center">Doc</th>
                <th style="padding:6px;text-align:center">Vencimento</th>
                <th style="padding:6px;text-align:right">Saldo</th>
                <th style="padding:6px;text-align:center">Status</th>
            </tr>
        </thead>
        <tbody>{_linhas_html}</tbody>
    </table>
    <div style="margin-top:14px;font-size:10px;color:#888;text-align:center">
        JGAutomações.AI · GM Homem Itaúna · {_dt_now.now().strftime('%d/%m/%Y')}
    </div>
</div>
<button onclick="window.print()" style="margin-top:10px;width:100%;padding:12px;
    background:#1D4ED8;color:white;border:none;border-radius:8px;
    font-size:15px;cursor:pointer;font-weight:600">
    🖨️ Imprimir / Salvar PDF
</button>
"""
        components.html(_html_pdf, height=700, scrolling=True)
        if st.button("✕ Fechar relatório", key="fechar_pdf_rec"):
            st.session_state.pop('exportar_pdf_rec', None)
            st.rerun()






def render_clientes_unificado(perfil):
    import streamlit.components.v1 as _comp
    from datetime import date as _date, datetime as _datetime
    import pandas as _pd

    st.markdown("""<style>
    .jg-kpi-row{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:16px}
    .jg-kpi{padding:14px 16px;border-radius:12px;color:white}
    .jg-kpi-label{font-size:11px;opacity:0.75;margin-bottom:4px;text-transform:uppercase;letter-spacing:1px}
    .jg-kpi-val{font-size:22px;font-weight:700}
    .jg-kpi-sub{font-size:11px;opacity:0.55;margin-top:2px}
    .jg-empty{text-align:center;padding:48px 20px;color:#9CA3AF;font-size:15px;background:#F9FAFB;border-radius:12px}
    </style>""", unsafe_allow_html=True)

    kpis = run_query("""
        SELECT
            COALESCE(SUM(CASE WHEN dt_vencimento < CURRENT_DATE THEN valor_saldo ELSE 0 END),0) AS vencido,
            COALESCE(SUM(CASE WHEN dt_vencimento > CURRENT_DATE THEN valor_saldo ELSE 0 END),0) AS a_vencer,
            COALESCE(SUM(valor_saldo),0) AS total,
            COUNT(DISTINCT codigo_cliente) AS n_cli
        FROM duplicatas_abertas WHERE status='Pendente'
    """)
    r = kpis.iloc[0] if not kpis.empty else None
    vencido  = float(r['vencido'])  if r is not None else 0
    a_vencer = float(r['a_vencer']) if r is not None else 0
    total    = float(r['total'])    if r is not None else 0
    n_cli    = int(r['n_cli'])      if r is not None else 0

    st.markdown(f"""
    <div class="jg-kpi-row">
      <div class="jg-kpi" style="background:#DC2626">
        <div class="jg-kpi-label">Vencido</div>
        <div class="jg-kpi-val">R$ {vencido:,.2f}</div>
        <div class="jg-kpi-sub">{n_cli} clientes</div>
      </div>
      <div class="jg-kpi" style="background:#1D4ED8">
        <div class="jg-kpi-label">A vencer</div>
        <div class="jg-kpi-val">R$ {a_vencer:,.2f}</div>
        <div class="jg-kpi-sub">proximas parcelas</div>
      </div>
      <div class="jg-kpi" style="background:#1F2937">
        <div class="jg-kpi-label">Carteira total</div>
        <div class="jg-kpi-val">R$ {total:,.2f}</div>
        <div class="jg-kpi-sub">todas as pendencias</div>
      </div>
    </div>""", unsafe_allow_html=True)

    _col_sel, _col_novo = st.columns([5, 1])
    df_nomes = run_query("""
        SELECT DISTINCT nome FROM (
            SELECT COALESCE(nome_cliente,'') AS nome FROM duplicatas_abertas
            WHERE nome_cliente IS NOT NULL AND TRIM(nome_cliente)!=''
            UNION
            SELECT nome FROM clientes WHERE nome IS NOT NULL AND TRIM(nome)!='' AND ativo=true
            UNION
            SELECT cl.nome FROM clientes cl
            INNER JOIN vendas v ON v.cliente_id = cl.id
            WHERE cl.nome IS NOT NULL AND TRIM(cl.nome)!=''
        ) t ORDER BY nome
    """)
    _opcoes = [''] + (df_nomes['nome'].tolist() if not df_nomes.empty else [])
    with _col_sel:
        _cli_sel = st.selectbox("", options=_opcoes,
            format_func=lambda x: "Pesquisar cliente..." if x=='' else x,
            key="cu_sel", label_visibility="collapsed")
    with _col_novo:
        if st.button("+ Novo", key="cu_novo", use_container_width=True):
            st.session_state['_cu_novo_open'] = not st.session_state.get('_cu_novo_open', False)

    if st.session_state.get('_cu_novo_open'):
        with st.container(border=True):
            st.markdown("#### Novo Cliente")
            _a, _b = st.columns(2)
            _nn = _a.text_input("Nome *", key="cu_nn")
            _nw = _b.text_input("WhatsApp", key="cu_nw")
            _c, _d = st.columns(2)
            _nc = _c.text_input("CPF", key="cu_nc")
            _nt = _d.text_input("Tags (ex: VEREADORA, VIP)", key="cu_nt")
            # ── CEP + Buscar ViaCEP ──────────────────────────────────
            _cep_col, _buscar_col, _end_col = st.columns([1.2, 0.7, 3])
            _ncep = _cep_col.text_input("CEP", key="cu_cep", max_chars=9, placeholder="00000-000")
            _buscar_col.markdown("<br>", unsafe_allow_html=True)
            _buscar_cep_click = _buscar_col.button("🔍 Buscar", key="cu_buscar_cep", use_container_width=True)
            _nend = _end_col.text_input("📍 Endereço", key="cu_end",
                value=st.session_state.get("_cep_end_auto", ""))
            if _buscar_cep_click and _ncep:
                _cep_data = buscar_cep(_ncep)
                if _cep_data:
                    st.session_state["_cep_end_auto"] = _cep_data.get("logradouro", "")
                    st.session_state["_cep_bai_auto"] = _cep_data.get("bairro", "")
                    st.session_state["_cep_cid_auto"] = _cep_data.get("localidade", "Itauna")
                    st.session_state["_cep_est_auto"] = _cep_data.get("uf", "")
                    st.rerun()
                else:
                    st.warning("CEP não encontrado.")
            # ── Bairro / Cidade ──────────────────────────────────────────
            _nb, _nci = st.columns(2)
            _nbai = _nb.text_input("Bairro", key="cu_bai",
                value=st.session_state.get("_cep_bai_auto", ""))
            _ncid = _nci.text_input("Cidade", key="cu_cid",
                value=st.session_state.get("_cep_cid_auto", "Itauna"))
            _nobs = st.text_input("Observacao", key="cu_obs")
            _s1, _s2 = st.columns([1,4])
            if _s1.button("Salvar", key="cu_ns", type="primary"):
                if _nn.strip():
                    run_command("INSERT INTO clientes (nome,whatsapp,cpf,tags,cep,endereco,bairro,cidade,observacoes,ativo,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,true,NOW()) ON CONFLICT DO NOTHING",
                        (_nn.strip(), _nw or None, _nc or None, _nt or None,
                         _ncep or None, _nend or None, _nbai or None, _ncid or None, _nobs or None))
                    st.success(f"Cliente {_nn} cadastrado!")
                    st.session_state['_cu_novo_open'] = False
                    st.rerun()
                else:
                    st.warning("Nome obrigatorio.")
            if _s2.button("Cancelar", key="cu_nc2"):
                st.session_state['_cu_novo_open'] = False
                st.rerun()

    _filtro = st.radio("", ["Vencidos", "Maior atraso", "Maior valor", "A-Z"],
        index=None, horizontal=True, key="cu_filtro", label_visibility="collapsed")

    _tem_busca  = bool(_cli_sel and _cli_sel.strip())
    _tem_filtro = _filtro is not None
    if not _tem_busca and not _tem_filtro:
        st.markdown('''<div class="jg-empty">Selecione um cliente pelo nome ou escolha um filtro para comecar</div>''', unsafe_allow_html=True)
        return

    _w_status = "AND da.status='Pendente'"
    _w_busca  = ""
    if _tem_busca:
        _b  = _cli_sel.replace("'","''")
        _bn = _b.replace("/"," ").strip()
        _w_busca  = f"AND (UPPER(REPLACE(COALESCE(da.nome_cliente,''),'/',' ')) LIKE UPPER('%{_bn}%') OR UPPER(COALESCE(da.nome_cliente,'')) LIKE UPPER('%{_b}%'))"
        _w_status = ""
    elif _filtro == "Vencidos":
        _w_status = "AND da.status='Pendente' AND da.dt_vencimento < CURRENT_DATE"

    # Monta filtro de nome para sistema novo
    _w_busca_novo = ""
    if _tem_busca:
        _bn2 = _cli_sel.replace("'","''").replace("/"," ").strip()
        _w_busca_novo = f"AND UPPER(cl2.nome) LIKE UPPER('%{_bn2}%')"
    # sistema novo usa 'aberto' como pendente — sempre filtrar por padrão
    if _tem_busca:
        _w_status_novo = ""  # busca mostra tudo (pago + aberto)
    else:
        _w_status_novo = "AND cr.status = 'aberto'"

    df = run_query(f"""
        SELECT da.id::text AS ref_id, da.codigo_cliente,
               COALESCE(da.nome_cliente,'?') AS nome_cliente,
               COALESCE(cl.celular,'') AS whatsapp,
               da.documento, da.ordem, da.dt_vencimento,
               da.valor_original, da.valor_saldo, da.modalidade,
               da.status AS status_parcela,
               COALESCE(da.observacao,'') AS obs,
               GREATEST(0, CURRENT_DATE - da.dt_vencimento) AS dias_atraso,
               'legado' AS sistema_origem
        FROM duplicatas_abertas da
        LEFT JOIN clientes_legados cl ON da.codigo_cliente = cl.codigo_legado
        WHERE 1=1 {_w_status} {_w_busca}

        UNION ALL

        SELECT cr.id::text AS ref_id, '0' AS codigo_cliente,
               cl2.nome AS nome_cliente,
               COALESCE(cl2.whatsapp,'') AS whatsapp,
               COALESCE(cr.nr_documento, cr.id::text) AS documento,
               'A' AS ordem,
               cr.data_vencimento AS dt_vencimento,
               cr.valor_parcela AS valor_original,
               CASE WHEN cr.status = 'aberto' THEN cr.valor_parcela ELSE 0 END AS valor_saldo,
               'Sistema Novo' AS modalidade,
               CASE WHEN cr.status = 'aberto' THEN 'Pendente' ELSE 'Pago' END AS status_parcela,
               '' AS obs,
               GREATEST(0, CURRENT_DATE - cr.data_vencimento) AS dias_atraso,
               'sistema_novo' AS sistema_origem
        FROM contas_receber cr
        JOIN vendas v ON v.id = cr.venda_id
        JOIN clientes cl2 ON cl2.id = v.cliente_id
        WHERE 1=1 {_w_status_novo} {_w_busca_novo}

        ORDER BY dt_vencimento
    """)

    if df.empty:
        st.info("Nenhum resultado encontrado.")
        return

    grp = (df[df['status_parcela']=='Pendente']
           .groupby('nome_cliente', sort=False)
           .agg(saldo=('valor_saldo','sum'), atraso=('dias_atraso','max'), qtd=('ref_id','count'))
           .reset_index())
    if _filtro == "A-Z":           grp = grp.sort_values('nome_cliente')
    elif _filtro == "Maior valor": grp = grp.sort_values('saldo', ascending=False)
    else:                          grp = grp.sort_values('atraso', ascending=False)
    nomes_ord = df['nome_cliente'].unique().tolist() if _tem_busca else grp['nome_cliente'].tolist()

    _n_pend = int(df[df['status_parcela']=='Pendente']['valor_saldo'].count())
    _v_tot  = float(df[df['status_parcela']=='Pendente']['valor_saldo'].sum())
    st.caption(f"**{len(nomes_ord)} cliente(s)** · {_n_pend} pendencia(s) · R$ {_v_tot:,.2f}")

    for _nome in nomes_ord:
        _dfc  = df[df['nome_cliente']==_nome].copy()
        _dfp  = _dfc[_dfc['status_parcela']=='Pendente']
        _saldo = float(_dfp['valor_saldo'].sum())
        _atr   = int(_dfc['dias_atraso'].max())
        _qtdp  = len(_dfp)
        _ini   = ''.join([p[0] for p in _nome.split()[:2]])
        if _atr > 30:  _badge,_cor = "Vencido","#DC2626"
        elif _atr > 0: _badge,_cor = "Atrasado","#D97706"
        else:           _badge,_cor = "Em dia","#1D4ED8"
        _sk   = "cu_" + str(abs(hash(_nome)) % 999999)
        _open = st.session_state.get(_sk, _tem_busca and len(nomes_ord)==1)
        # Exibir cupom de baixa se existir para este cliente
        if st.session_state.get(f"baixa_ok_{_sk}"):
            import streamlit.components.v1 as _comp_bx
            with st.container(border=True):
                st.success("✅ Baixa confirmada com sucesso!")
                _html_cupom_bx = st.session_state.get(f"cupom_baixa_{_sk}", "")
                if _html_cupom_bx:
                    _comp_bx.html(_html_cupom_bx, height=660, scrolling=True)
                if st.button("✕ Fechar cupom e continuar", key=f"fch_bx_{_sk}", type="primary", use_container_width=True):
                    st.session_state.pop(f"cupom_baixa_{_sk}", None)
                    st.session_state.pop(f"baixa_ok_{_sk}", None)
                    st.rerun()
            continue

        with st.container(border=True):
            _h1,_h2,_h3 = st.columns([0.5,4.5,1.5])
            with _h1:
                st.markdown(f'''<div style="width:36px;height:36px;border-radius:50%;background:#1F2937;color:white;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;margin-top:8px">{_ini}</div>''', unsafe_allow_html=True)
            with _h2:
                st.markdown(f"**{_nome}**")
                _wh = _dfc['whatsapp'].iloc[0] if not _dfc.empty else ''
                # Buscar total pago e ultima compra
                _tot_pago = float(_dfc[_dfc['status_parcela']=='Pago']['valor_saldo'].sum()) if 'status_parcela' in _dfc.columns else 0
                _ult_compra = str(_dfc['dt_vencimento'].min())[:10] if not _dfc.empty else ''
                _ult_br = f"{_ult_compra[8:10]}/{_ult_compra[5:7]}/{_ult_compra[:4]}" if len(_ult_compra)>=10 else ''
                _info_extra = f" · 1ª parc: {_ult_br}" if _ult_br else ""
                st.caption(f"{_qtdp} pendencia(s) · atraso {_atr}d · {_wh or 'sem WhatsApp'} · {_badge}{_info_extra}")
            with _h3:
                st.markdown(f'''<div style="text-align:right;font-size:18px;font-weight:700;color:{_cor};padding-top:8px">R$ {_saldo:,.2f}</div>''', unsafe_allow_html=True)
                if st.button("Ver" if not _open else "Fechar", key=f"bt_{_sk}", use_container_width=True):
                    st.session_state[_sk] = not _open
                    st.rerun()

            if not _open:
                continue

            st.markdown("---")
            _cod = str(_dfc['codigo_cliente'].iloc[0])
            _tp, _tq, _th, _tr, _tc = st.tabs(["📌 Pendências","✅ Quitadas","📋 Histórico","📊 Radar RFM","👤 Cadastro"])

            with _tp:
                if _dfp.empty:
                    st.success("Nenhuma pendencia!")
                else:
                    _k_sel = f'sels_all_{_sk}'
                    if _k_sel not in st.session_state:
                        st.session_state[_k_sel] = []

                    _col_sa, _col_cl = st.columns([3,2])
                    with _col_sa:
                        if st.button(f'Selecionar todas ({len(_dfp)} parcelas — R$ {float(_dfp["valor_saldo"].sum()):,.2f})', key=f'btn_all_{_sk}', use_container_width=True):
                            _ids_todos = [str(r['ref_id']) for _, r in _dfp.iterrows()]
                            st.session_state[_k_sel] = _ids_todos
                            for _rid_t in _ids_todos:
                                st.session_state[f"ck2_{_rid_t}_{_sk}"] = True
                            st.rerun()
                    with _col_cl:
                        if st.button('Limpar selecao', key=f'btn_none_{_sk}', use_container_width=True):
                            st.session_state[_k_sel] = []
                            for _k2 in [k for k in list(st.session_state.keys()) if k.startswith("ck2_") and k.endswith(f"_{_sk}")]:
                                st.session_state[_k2] = False
                            st.rerun()

                    for _, rw in _dfp.iterrows():
                        _rid_str = str(rw['ref_id'])
                        _dv = str(rw['dt_vencimento'])
                        _dvbr = f"{_dv[8:10]}/{_dv[5:7]}/{_dv[:4]}" if len(_dv)>=10 and _dv[4]=='-' else _dv
                        _ds = f"({int(rw['dias_atraso'])}d atraso)" if rw['dias_atraso']>0 else '(a vencer)'
                        _orig_badge = ' 🆕' if str(rw.get('sistema_origem','')) == 'sistema_novo' else ''
                        _da_rw = int(rw.get('dias_atraso',0))
                        _jur_rw = round(float(rw['valor_saldo']) * 0.001 * _da_rw, 2) if _da_rw > 0 else 0.0
                        _jur_str = f" | +R$ {_jur_rw:,.2f} juros" if _jur_rw > 0 else ""
                        _marcado = _rid_str in st.session_state[_k_sel]
                        _ck_col, _rec_col = st.columns([11, 1])
                        with _ck_col:
                            _ck_key = f"ck2_{_rid_str}_{_sk}"
                            if _ck_key not in st.session_state:
                                st.session_state[_ck_key] = _marcado
                            _novo = st.checkbox(
                                f"Doc {rw['documento']}-{rw['ordem']}{_orig_badge} · Venc {_dvbr} {_ds} · R$ {float(rw['valor_saldo']):,.2f}{_jur_str}",
                                key=_ck_key,
                            )
                        with _rec_col:
                            if st.button("🧾", key=f"brec_{_rid_str}_{_sk}", help="Ver detalhes da compra"):
                                _mk = f"mcupom_{_rid_str}_{_sk}"
                                st.session_state[_mk] = not st.session_state.get(_mk, False)
                        if st.session_state.get(f"mcupom_{_rid_str}_{_sk}", False):
                            with st.container(border=True):
                                st.markdown(f"**🧾 Detalhes — Doc {rw['documento']}-{rw['ordem']}**")
                                _mc1, _mc2, _mc3 = st.columns(3)
                                _mc1.markdown(f"**Vencimento:** {_dvbr}")
                                _mc2.markdown(f"**Valor:** R$ {float(rw['valor_saldo']):,.2f}")
                                _mc3.markdown(f"**Sistema:** {'PDV Novo' if str(rw.get('sistema_origem','')) == 'sistema_novo' else 'Legado SGA'}")
                                if str(rw.get('sistema_origem','')) == 'sistema_novo':
                                    _itens_m = run_query("""
                                        SELECT p.nome, pv.tamanho, iv.quantidade,
                                               iv.valor_unitario,
                                               iv.quantidade * iv.valor_unitario AS subtotal,
                                               v.data_venda, v.forma_pagamento
                                        FROM contas_receber cr
                                        JOIN vendas v ON v.id = cr.venda_id
                                        JOIN itens_venda iv ON iv.venda_id = v.id
                                        JOIN produtos p ON p.id = iv.produto_id
                                        LEFT JOIN produto_variacoes pv ON pv.id = iv.variacao_id
                                        WHERE cr.id = %s::uuid
                                        ORDER BY iv.id
                                    """, [str(rw['ref_id'])])
                                    if not _itens_m.empty:
                                        _vd0 = _itens_m.iloc[0]
                                        _dv0 = str(_vd0['data_venda'])[:10]
                                        _dv0br = f"{_dv0[8:10]}/{_dv0[5:7]}/{_dv0[:4]}" if len(_dv0)==10 else _dv0
                                        st.markdown(f"📅 **Data da compra:** {_dv0br} &nbsp;|&nbsp; **Forma:** {_vd0['forma_pagamento']}")
                                        st.markdown("**🛍 Itens:**")
                                        for _, _it in _itens_m.iterrows():
                                            _tam = f" ({_it['tamanho']})" if _it.get('tamanho') else ""
                                            st.markdown(f"&nbsp;&nbsp;• {_it['nome']}{_tam} &mdash; {int(_it['quantidade'])}x R$ {float(_it['valor_unitario']):,.2f} = **R$ {float(_it['subtotal']):,.2f}**")
                                    else:
                                        st.info("Itens detalhados nao disponiveis para esta parcela.")
                                else:
                                    _cod_b = str(rw.get('codigo_cliente',''))
                                    _doc_raw = str(rw['documento'])
                                    _ord_raw = str(rw.get('ordem','A'))
                                    # Montar no formato da tabela: '016864-A' (6 digitos com zero + letra)
                                    _doc_pad = _doc_raw.zfill(6) + '-' + _ord_raw if _ord_raw and len(_ord_raw)==1 and _ord_raw.isalpha() else _doc_raw.zfill(6)
                                    _its = run_query(
                                        "SELECT referencia,descricao,cor,quantidade,valor_unitario,valor_total FROM duplicatas_abertas_itens WHERE documento=%s AND cliente_codigo=%s ORDER BY id",
                                        [_doc_pad, _cod_b]
                                    )
                                    if _its.empty:
                                        # Tentar com zero padded
                                        _its = run_query(
                                            "SELECT referencia,descricao,cor,quantidade,valor_unitario,valor_total FROM duplicatas_abertas_itens WHERE documento LIKE %s ORDER BY id",
                                            [_doc_raw.zfill(6) + '%']
                                        )
                                    if _its.empty:
                                        # Tentar sem zero
                                        _its = run_query(
                                            "SELECT referencia,descricao,cor,quantidade,valor_unitario,valor_total FROM duplicatas_abertas_itens WHERE documento LIKE %s ORDER BY id",
                                            [str(int(_doc_raw)) + '%'] if _doc_raw.isdigit() else [_doc_raw + '%']
                                        )
                                    if not _its.empty:
                                        _tot_it = float(_its['valor_total'].sum())
                                        _dt_emissao_q = run_query(
                                            "SELECT dt_emissao FROM duplicatas_abertas WHERE (documento=%s OR documento=%s) AND codigo_cliente=%s AND dt_emissao IS NOT NULL LIMIT 1",
                                            [_doc_raw, _doc_raw.lstrip('0'), _cod_b]
                                        )
                                        _dt_em_str = ''
                                        if not _dt_emissao_q.empty and _dt_emissao_q.iloc[0]['dt_emissao']:
                                            _de = str(_dt_emissao_q.iloc[0]['dt_emissao'])[:10]
                                            _dt_em_str = f" &nbsp;|&nbsp; **Data compra:** {_de[8:10]}/{_de[5:7]}/{_de[:4]}"
                                        st.markdown(f"**Total da compra:** R$ {_tot_it:,.2f}{_dt_em_str} &nbsp;|&nbsp; **Sistema:** Legado SGA")
                                        st.markdown("**Itens:**")
                                        for _, _it in _its.iterrows():
                                            _cor_it = f" (cor {_it['cor']})" if _it.get('cor') and str(_it['cor']) not in ('001','002') else ""
                                            st.markdown(f"&nbsp;&nbsp;**{_it['descricao']}**{_cor_it} — {int(_it['quantidade'])}x R$ {float(_it['valor_unitario']):,.2f} = **R$ {float(_it['valor_total']):,.2f}**")
                                        st.caption(f"Refs: {', '.join(_its['referencia'].astype(str).tolist())}")
                                    else:
                                        st.info("Sistema legado SGA. Itens desta parcela nao disponiveis no arquivo SCRRR06.")
                        if _novo != _marcado:
                            _lst = list(st.session_state[_k_sel])
                            if _novo and _rid_str not in _lst:
                                _lst.append(_rid_str)
                            elif not _novo and _rid_str in _lst:
                                _lst.remove(_rid_str)
                            st.session_state[_k_sel] = _lst
                            st.rerun()

                    # Reconstruir _sels do session_state
                    _sels_ids = st.session_state.get(_k_sel, [])
                    _sels = [rw.to_dict() for _, rw in _dfp.iterrows() if str(rw['ref_id']) in _sels_ids]

                    _wh2 = _dfc['whatsapp'].iloc[0] if not _dfc.empty else ''
                    if _wh2:
                        _wn = ''.join(filter(str.isdigit, str(_wh2)))
                        _wmsg = f"Ola {_nome.split()[0]}! Passando para lembrar das suas parcelas em aberto na GM Homem"
                        st.markdown(f'''<a href="https://wa.me/55{_wn}?text={_wmsg.replace(' ','%20')}" target="_blank"><button style="padding:6px 14px;background:#0F6E56;color:white;border:none;border-radius:8px;cursor:pointer;font-size:12px;margin-top:6px">WhatsApp cobranca</button></a>''', unsafe_allow_html=True)
                    if not _sels:
                        st.info("Selecione parcelas para dar baixa.")
                    else:
                        _tot_sel = sum(float(r['valor_saldo']) for r in _sels)
                        with st.container(border=True):
                            st.markdown("##### Dar Baixa")
                            _bf1,_bf2 = st.columns(2)
                            _forma = _bf1.selectbox("Forma", ["Dinheiro","Pix","Cartao Debito","Cartao Credito","Transferencia","Cheque"], key=f"frm_{_sk}")
                            _vrec  = _bf2.number_input("Valor recebido", min_value=0.01, value=float(round(_tot_sel,2)), step=0.01, format="%.2f", key=f"vrec_{_sk}")
                            _jop = st.radio("Encargos", ["Cobrar encargos legais","Isentar total","Isentar parcialmente"], horizontal=True, key=f"jop_{_sk}")
                            _jval = 0.0
                            if _jop == "Cobrar encargos legais":
                                for _r in _sels:
                                    _da2 = int(_r.get('dias_atraso',0))
                                    if _da2 > 0:
                                        _sv = float(_r['valor_saldo'])
                                        _jval += round(_sv * 0.001 * _da2, 2)
                                _jval = round(_jval,2)
                                if _jval > 0:
                                    _qtd_sels = len(_sels)
                                    _total_com_j = round(_tot_sel + _jval, 2)
                                    st.markdown(f"""
                                        <div style="background:linear-gradient(135deg,#1E3A5F,#1D4ED8);border-radius:12px;padding:16px 20px;margin:10px 0;color:white">
                                            <div style="font-size:11px;font-weight:700;letter-spacing:.1em;opacity:.8;margin-bottom:10px">📊 RESUMO DA BAIXA</div>
                                            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
                                                <div><div style="font-size:11px;opacity:.75">Notas selecionadas</div><div style="font-size:16px;font-weight:700">{_qtd_sels} nota(s)</div></div>
                                                <div><div style="font-size:11px;opacity:.75">Saldo devedor</div><div style="font-size:16px;font-weight:700">R$ {_tot_sel:,.2f}</div></div>
                                                <div><div style="font-size:11px;opacity:.75">Juros (0,1%/dia)</div><div style="font-size:16px;font-weight:700;color:#FCD34D">+ R$ {_jval:,.2f}</div></div>
                                                <div style="background:rgba(255,255,255,.15);border-radius:8px;padding:6px 10px"><div style="font-size:11px;opacity:.75">Total a receber</div><div style="font-size:20px;font-weight:800;color:#6EE7B7">R$ {_total_com_j:,.2f}</div></div>
                                            </div>
                                        </div>""", unsafe_allow_html=True)
                            elif _jop == "Isentar parcialmente":
                                _jval = st.number_input("Encargos a cobrar", min_value=0.0, value=0.0, step=1.0, key=f"jp_{_sk}")
                            _total_cobrar = round(_tot_sel + _jval, 2)
                            _isentou = (_jop != "Cobrar encargos legais")
                            st.markdown(f'''<div style="display:flex;justify-content:space-between;padding:10px;background:#F0FDF4;border-radius:8px;margin:8px 0"><span style="color:#166534">Total a receber</span><span style="color:#166534;font-size:20px;font-weight:700">R$ {_total_cobrar:,.2f}</span></div><div style="font-size:12px;color:#6B7280">Cupom gerado automaticamente</div>''', unsafe_allow_html=True)
                            _obs_b = st.text_input("Observacao", key=f"obs_{_sk}", max_chars=200)
                            if st.button(f"Confirmar e gerar cupom  R$ {_total_cobrar:,.2f}", type="primary", use_container_width=True, key=f"conf_{_sk}"):
                                _hoje = _date.today()
                                _sels_fifo = sorted(_sels, key=lambda x: str(x.get('dt_vencimento','')))
                                _saldo_rest = round(float(_vrec), 2)
                                for _r in _sels_fifo:
                                    if _saldo_rest <= 0:
                                        break
                                    _rid_raw = str(_r['ref_id']).strip()
                                    _orig_r  = str(_r.get('sistema_origem','legado'))
                                    _sp = float(_r['valor_saldo'])
                                    _pp = min(_saldo_rest, _sp)
                                    if _orig_r == 'sistema_novo':
                                        if _saldo_rest >= _sp * 0.999:
                                            run_command("UPDATE contas_receber SET status='Pago',data_pagamento=%s,valor_pago_final=%s WHERE id=%s::uuid",
                                                (_hoje, _pp, _rid_raw))
                                        else:
                                            run_command("UPDATE contas_receber SET valor_parcela=%s WHERE id=%s::uuid",
                                                (round(_sp - _pp, 2), _rid_raw))
                                    else:
                                        try: _rid_int = int(_rid_raw)
                                        except: _rid_int = _rid_raw
                                        if _saldo_rest >= _sp * 0.999:
                                            run_command("UPDATE duplicatas_abertas SET status='Pago',dt_baixa=%s,valor_saldo=0,valor_pago_total=COALESCE(valor_pago_total,0)+%s,forma_recebimento=%s,isentou_encargos=%s,observacao=COALESCE(observacao||' | ','')||%s WHERE id=%s",
                                                (_hoje,_pp,_forma,_isentou,f"Baixa {_hoje.strftime('%d/%m/%Y')} {_obs_b}",_rid_int))
                                        else:
                                            run_command("UPDATE duplicatas_abertas SET valor_saldo=%s,valor_pago_total=COALESCE(valor_pago_total,0)+%s,forma_recebimento=%s WHERE id=%s",
                                                (round(_sp-_pp,2),_pp,_forma,_rid_int))
                                    _saldo_rest = round(_saldo_rest - _pp, 2)
                                try:
                                    run_command("INSERT INTO movimentos_financeiros (parcela_id,origem,valor_pago,forma_pagamento,isentou_encargos,saldo_anterior,saldo_posterior,operador,observacao) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                        (str(_sels[0]['ref_id']),'legado',_total_cobrar,_forma,_isentou,_tot_sel,0,st.session_state.get('usuario',''),_obs_b))
                                except: pass
                                _nome_q = _nome.replace("'","''")
                                _rest_leg = run_query("SELECT documento,ordem,dt_vencimento,valor_saldo FROM duplicatas_abertas WHERE codigo_cliente=%s AND status='Pendente' ORDER BY dt_vencimento LIMIT 8", [_cod])
                                _rest_new = run_query(f"SELECT COALESCE(cr.nr_documento, 'CR-'||SUBSTRING(cr.id::text,1,8)) AS documento,'A' AS ordem,cr.data_vencimento AS dt_vencimento,cr.valor_parcela AS valor_saldo FROM contas_receber cr JOIN vendas v ON v.id=cr.venda_id JOIN clientes cl2 ON cl2.id=v.cliente_id WHERE cl2.nome ILIKE '%{_nome_q}%' AND cr.status='aberto' ORDER BY cr.data_vencimento LIMIT 8")
                                import pandas as _pd2
                                _rest = _pd2.concat([_rest_leg, _rest_new], ignore_index=True).sort_values('dt_vencimento') if not _rest_new.empty else _rest_leg
                                _agora = _datetime.now().strftime('%d/%m/%Y %H:%M')
                                def _ref_c(doc, ord):
                                    d=str(doc); return f"{d[:8]}..." if len(d)>15 else f"{d}-{ord}"
                                _lp = ''.join([f"<tr><td style='font-size:11px;color:#166534'>{_ref_c(r['documento'],r['ordem'])}</td><td style='text-align:right;color:#166534'>R$ {float(r['valor_saldo']):,.2f}</td></tr>" for r in _sels])
                                _lr = ''
                                if not _rest.empty:
                                    for _, _pr in _rest.iterrows():
                                        _dv2=str(_pr['dt_vencimento']); _db=f"{_dv2[8:10]}/{_dv2[5:7]}/{_dv2[:4]}" if len(_dv2)>=10 else _dv2
                                        _ref2=_ref_c(_pr['documento'],_pr['ordem'])
                                        _lr += f"<tr style='color:#555'><td style='font-size:11px'>{_ref2} &middot; Venc {_db}</td><td style='text-align:right;font-size:11px'>R$ {float(_pr['valor_saldo']):,.2f}</td></tr>"
                                _ne = _nome.replace("'","\\\'").replace('"','&quot;')
                                _qs = 'QUITACAO TOTAL' if len(_sels)==_qtdp else 'PAGAMENTO PARCIAL'
                                _sep = '<tr><td colspan="2"><hr style="border:1px dashed #D1D5DB;margin:6px 0"></td></tr>'
                                _html_c = f"""<div id="cpjg" style="font-family:'Courier New',monospace;max-width:380px;margin:0 auto;padding:20px;border:2px solid #374151;border-radius:8px;background:#fff;color:#111"><div style="text-align:center;border-bottom:1px dashed #9CA3AF;padding-bottom:12px;margin-bottom:12px"><div style="font-size:20px;font-weight:700">LOJA GM HOMEM ITAUNA</div><div style="font-size:11px;color:#6B7280">Moda Masculina · {_agora}</div></div><table style="width:100%;font-size:13px;border-collapse:collapse"><tr><td style="color:#6B7280">Cliente</td><td style="text-align:right;font-weight:700">{_nome}</td></tr>{_sep}<tr><td colspan="2" style="font-size:11px;font-weight:700;padding:4px 0">PAGO</td></tr>{_lp}{'<tr><td colspan="2" style="font-size:11px;font-weight:700;padding:4px 0">A VENCER</td></tr>' if _lr else ''}{_lr}{_sep}<tr style="background:#F3F4F6"><td style="padding:5px 4px;font-weight:700">TOTAL</td><td style="text-align:right;font-weight:700;font-size:16px;color:#15803D">R$ {float(_vrec):,.2f}</td></tr><tr><td style="color:#6B7280">Forma</td><td style="text-align:right">{_forma}</td></tr></table><div style="text-align:center;font-size:11px;color:#16A34A;margin-top:12px;padding:8px;border:1px solid #16A34A;border-radius:6px;font-weight:700">{_qs}</div><div style="text-align:center;font-size:10px;color:#9CA3AF;margin-top:12px;border-top:1px dashed #9CA3AF;padding-top:8px">Obrigado pela preferência! GM Homem Itaúna</div></div><button onclick="(function(){{var c=document.getElementById('cpjg').outerHTML;var w=window.open('','_blank','width=460,height=700');w.document.write('<html><head><title>Cupom</title><style>body{{font-family:Courier New,monospace;padding:20px}}@media print{{button{{display:none}}}}</style></head><body>'+c+'<br><button onclick=window.print() style=width:100%;padding:10px;background:#111;color:#fff;border:none;font-size:14px;cursor:pointer;border-radius:6px>Imprimir</button></body></html>');w.document.close();setTimeout(function(){{w.print()}},600)}})()" style="width:100%;margin-top:12px;padding:12px;background:#1D4ED8;color:white;border:none;border-radius:8px;font-size:15px;cursor:pointer;font-weight:600">Imprimir Cupom</button>"""
                                # Salvar cupom no session_state para exibir ANTES do rerun
                                st.session_state[f"cupom_baixa_{_sk}"] = _html_c
                                st.session_state[f"baixa_ok_{_sk}"] = True
                                # Limpar selecao
                                st.session_state[_k_sel] = []
                                for _k2 in [k for k in list(st.session_state.keys()) if k.startswith("ck2_") and k.endswith(f"_{_sk}")]:
                                    del st.session_state[_k2]
                                st.rerun()
            with _tq:
                _nome_q2 = _nome.replace("'","''")
                # _cod ja vem da linha 6977 com o codigo correto (ex: '481' para Carla)
                # Se for '0' ou vazio e legado, buscar na duplicatas_abertas
                if str(_cod) not in ('0','','None','nan'):
                    _cod_leg2 = str(_cod)
                else:
                    _df_cod_leg2 = run_query(
                        "SELECT DISTINCT codigo_cliente FROM duplicatas_abertas WHERE nome_cliente=%s LIMIT 1",
                        [_nome]
                    )
                    _cod_leg2 = str(_df_cod_leg2.iloc[0]['codigo_cliente']) if not _df_cod_leg2.empty else _cod
                _df_quit = run_query(f"""
                    SELECT da.documento, da.ordem,
                           da.dt_vencimento, da.dt_baixa AS dt_pagamento,
                           da.valor_original AS valor_original,
                           da.valor_pago_total AS valor_pago,
                           da.forma_recebimento AS forma, 'Legado SGA' AS sistema
                    FROM duplicatas_abertas da
                    WHERE da.codigo_cliente = '{_cod_leg2}' AND da.status = 'Pago'
                    UNION ALL
                    SELECT cr.nr_documento, 'A',
                           cr.data_vencimento, cr.data_pagamento,
                           cr.valor_parcela,
                           COALESCE(cr.valor_pago_final, cr.valor_parcela),
                           NULL, 'PDV Novo'
                    FROM contas_receber cr
                    JOIN vendas v ON v.id = cr.venda_id
                    JOIN clientes cl2 ON cl2.id = v.cliente_id
                    WHERE cl2.nome ILIKE '%{_nome_q2}%' AND cr.status = 'Pago'
                    UNION ALL
                    SELECT hl.documento, COALESCE(hl.ordem,'-'),
                           hl.dt_vencimento, hl.data_baixa,
                           hl.valor_docto, hl.valor_recebido,
                           hl.forma_pagto, 'Hist.Legado'
                    FROM historico_legado hl
                    JOIN clientes_legados cl3 ON cl3.codigo_legado = hl.cliente_codigo
                    WHERE cl3.nome ILIKE '%{_nome_q2}%' AND hl.status = 'Pago'
                    ORDER BY dt_pagamento DESC NULLS LAST LIMIT 200
                """)
                if _df_quit.empty:
                    st.info("Nenhum pagamento quitado encontrado.")
                else:
                    _cq1, _cq2 = st.columns(2)
                    _cq1.metric("Total quitado", f"R$ {float(_df_quit['valor_pago'].sum()):,.2f}")
                    _cq2.metric("Parcelas pagas", len(_df_quit))
                    def _fmt_d(v):
                        s = str(v)[:10]
                        if len(s)==10 and s[4]=='-': return f"{s[8:10]}/{s[5:7]}/{s[:4]}"
                        return '—' if s in ('None','NaT','') else s
                    _dq = _df_quit.copy()
                    for _c in ['dt_vencimento','dt_pagamento']:
                        if _c in _dq.columns: _dq[_c] = _dq[_c].apply(_fmt_d)
                    _dq = _dq.rename(columns={
                        'documento':'Documento','ordem':'Parc',
                        'dt_vencimento':'Vencimento','dt_pagamento':'Pago em',
                        'valor_original':'Valor','valor_pago':'Recebido',
                        'forma':'Forma','sistema':'Sistema'
                    })
                    st.dataframe(_dq[[c for c in ['Documento','Parc','Vencimento','Pago em','Valor','Recebido','Forma','Sistema'] if c in _dq.columns]],
                        use_container_width=True, hide_index=True)

            with _th:
                import streamlit.components.v1 as _comp2
                from datetime import datetime as _dt2
                _hn = _nome.replace("'","''")
                _hn2 = _nome.replace('/','').replace("'","''")
                dh = run_query(f"""
                    SELECT hl.documento, COALESCE(hl.ordem,'-') as ordem,
                           hl.dt_vencimento, hl.valor_docto,
                           hl.status, 'Hist.Legado' AS origem, hl.data_baixa AS dt_pagamento
                    FROM historico_legado hl
                    JOIN clientes_legados cl_h ON cl_h.codigo_legado = hl.cliente_codigo
                    WHERE cl_h.nome ILIKE '%{_hn}%'
                    UNION ALL
                    SELECT da.documento, da.ordem, da.dt_vencimento, da.valor_original,
                           da.status, 'Sistema' AS origem, da.dt_baixa AS dt_pagamento
                    FROM duplicatas_abertas da
                    WHERE UPPER(REPLACE(da.nome_cliente,'/','')) LIKE UPPER('%{_hn2}%')
                    UNION ALL
                    SELECT SUBSTRING(cr.id::text,1,8), 'A', cr.data_vencimento,
                           cr.valor_parcela,
                           CASE WHEN cr.status='aberto' THEN 'Pendente' ELSE 'Pago' END,
                           'PDV Novo', cr.data_pagamento
                    FROM contas_receber cr JOIN vendas v ON v.id=cr.venda_id
                    JOIN clientes cl2 ON cl2.id=v.cliente_id
                    WHERE cl2.nome ILIKE '%{_hn}%'
                    ORDER BY dt_vencimento DESC LIMIT 100
                """)
                _agora_h = _dt2.now().strftime('%d/%m/%Y %H:%M')
                if dh.empty:
                    st.info('Sem historico.')
                else:
                    _hc1,_hc2,_hc3 = st.columns(3)
                    _tv = float(dh['valor_docto'].sum())
                    _tp = len(dh[dh['status'].isin(['Pago','baixado'])])
                    _hc1.metric('Registros', len(dh))
                    _hc2.metric('Volume', f'R$ {_tv:,.2f}')
                    _hc3.metric('Pagos', _tp)
                    # Montar HTML do extrato
                    _rows_h = ''
                    for _ix, (_, _hr) in enumerate(dh.iterrows()):
                        _st_h = str(_hr.get('status','')).lower()
                        _pago_h = _st_h in ['pago','baixado']
                        _cor_h = '#166534' if _pago_h else '#92400E'
                        _ico_h = 'Pago' if _pago_h else 'Pendente'
                        _dv_h_r = str(_hr.get('dt_vencimento',''))[:10]
                        _dp_h_r = str(_hr.get('dt_pagamento','') or '')[:10]
                        _dv_h = f"{_dv_h_r[8:10]}/{_dv_h_r[5:7]}/{_dv_h_r[:4]}" if len(_dv_h_r)==10 and _dv_h_r[4]=='-' else _dv_h_r
                        _dp_h = f"{_dp_h_r[8:10]}/{_dp_h_r[5:7]}/{_dp_h_r[:4]}" if len(_dp_h_r)==10 and _dp_h_r[4]=='-' else ('--' if not _dp_h_r.strip() or _dp_h_r in ('None','NaT') else _dp_h_r)
                        _doc_h = str(_hr.get('documento',''))
                        _doc_f = f'{_doc_h[:10]}' if len(_doc_h)>12 else f"{_doc_h}-{_hr.get('ordem','')}"
                        _bg_h = '#F0FDF4' if _pago_h else ('#FFF9E6' if _ix%2==0 else '#FFFBF0')
                        _rows_h += f"<tr style='background:{_bg_h}'><td style='padding:4px 8px;font-size:11px'>{_doc_f}</td><td style='padding:4px 8px;font-size:11px'>{_dv_h}</td><td style='padding:4px 8px;font-size:11px;color:{_cor_h}'>{_ico_h}</td><td style='padding:4px 8px;font-size:11px'>{_dp_h}</td><td style='padding:4px 8px;font-size:11px;text-align:right'>R$ {float(_hr.get('valor_docto',0)):,.2f}</td><td style='padding:4px 8px;font-size:11px'>{_hr.get('origem','')}</td></tr>"
                    _ne_h = _nome.replace("'","\'").replace('"','&quot;')
                    _tot_pend_h = float(dh[dh['status'].str.lower().isin(['pendente','aberto'])]['valor_docto'].sum()) if not dh.empty else 0
                    _tot_pago_h2 = float(dh[dh['status'].str.lower().isin(['pago','baixado'])]['valor_docto'].sum()) if not dh.empty else 0
                    _pct_pg = round(_tp/len(dh)*100) if len(dh)>0 else 0
                    _saude_cor = '#16A34A' if _pct_pg>=80 else '#D97706' if _pct_pg>=50 else '#DC2626'
                    _saude_txt = 'Excelente' if _pct_pg>=80 else 'Regular' if _pct_pg>=50 else 'Atencao'
                    _anos = {}
                    for _, _hr_a in dh.iterrows():
                        _ano = str(_hr_a.get('dt_vencimento',''))[:4]
                        if _ano.isdigit() and int(_ano) >= 2020:
                            _anos[_ano] = _anos.get(_ano, 0) + float(_hr_a.get('valor_docto',0))
                    _anos_html = ''.join([
                        "<span style='display:inline-block;margin:3px;padding:3px 10px;background:#F3F4F6;border-radius:12px;font-size:11px'><b>" + a + "</b>: R$ " + f"{v:,.2f}" + "</span>"
                        for a, v in sorted(_anos.items())
                    ])
                    _kpis_html = (
                        "<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:12px'>"
                        "<div style='background:#F0FDF4;border:1px solid #BBF7D0;border-radius:8px;padding:10px;text-align:center'>"
                        "<div style='font-size:16px;font-weight:700;color:#166534'>R$ " + f"{_tot_pago_h2:,.2f}" + "</div>"
                        "<div style='font-size:10px;color:#166534'>Total pago</div></div>"
                        "<div style='background:#FEF3C7;border:1px solid #FDE68A;border-radius:8px;padding:10px;text-align:center'>"
                        "<div style='font-size:16px;font-weight:700;color:#92400E'>R$ " + f"{_tot_pend_h:,.2f}" + "</div>"
                        "<div style='font-size:10px;color:#92400E'>Em aberto</div></div>"
                        "<div style='background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;padding:10px;text-align:center'>"
                        "<div style='font-size:16px;font-weight:700;color:#1E40AF'>R$ " + f"{_tv:,.2f}" + "</div>"
                        "<div style='font-size:10px;color:#1E40AF'>Volume total</div></div>"
                        "<div style='background:#F9FAFB;border:1px solid #E5E7EB;border-radius:8px;padding:10px;text-align:center'>"
                        "<div style='font-size:16px;font-weight:700;color:" + _saude_cor + "'>" + str(_pct_pg) + "%</div>"
                        "<div style='font-size:10px;color:" + _saude_cor + "'>Pontualidade</div></div>"
                        "</div>"
                        "<div style='margin-bottom:10px;padding:8px;background:#F9FAFB;border-radius:8px;border:1px solid #E5E7EB'>"
                        "<span style='font-size:11px;color:#6B7280;margin-right:8px'>Volume por ano:</span>" + _anos_html +
                        "</div>"
                    )
                    _html_e = f"""<div id='extjg' style='font-family:Arial,sans-serif;padding:16px;background:#fff;color:#111'>{_kpis_html}<div style='border-bottom:2px solid #374151;padding-bottom:10px;margin-bottom:14px'><div style='font-size:17px;font-weight:700'>LOJA GM HOMEM ITAUNA — EXTRATO</div><div style='font-size:12px;color:#6B7280'>Cliente: <b>{_ne_h}</b> | Gerado: {_agora_h} | {len(dh)} registros | R$ {_tv:,.2f} | {_tp} pagos</div></div><table style='width:100%;border-collapse:collapse'><thead><tr style='background:#374151;color:white'><th style='padding:5px 8px;text-align:left;font-size:11px'>Documento</th><th style='padding:5px 8px;text-align:left;font-size:11px'>Vencimento</th><th style='padding:5px 8px;text-align:left;font-size:11px'>Status</th><th style='padding:5px 8px;text-align:left;font-size:11px'>Dt Pagto</th><th style='padding:5px 8px;text-align:right;font-size:11px'>Valor</th><th style='padding:5px 8px;text-align:left;font-size:11px'>Origem</th></tr></thead><tbody>{_rows_h}</tbody></table><div style='margin-top:12px;font-size:10px;color:#9CA3AF;border-top:1px solid #e5e7eb;padding-top:6px'>Obrigado pela preferência! GM Homem Itaúna</div></div><button onclick="(function(){{var c=document.getElementById('extjg').outerHTML;var w=window.open('','_blank','width=800,height=900');w.document.write('<html><head><title>Extrato</title><style>body{{padding:20px;font-family:Arial}}@media print{{button{{display:none}}}}</style></head><body>'+c+'<br><button onclick=window.print() style=width:100%;padding:10px;background:#111;color:#fff;border:none;cursor:pointer;border-radius:6px>Imprimir / Salvar PDF</button></body></html>');w.document.close();setTimeout(function(){{w.print()}},500)}})()" style='width:100%;padding:10px;background:#1D4ED8;color:white;border:none;border-radius:8px;font-size:14px;cursor:pointer;font-weight:600;margin-top:10px'>📄 Imprimir / Salvar PDF</button>"""
                    _comp2.html(_html_e, height=520, scrolling=True)
                    st.markdown('---')
                    for _, hr in dh.iterrows():
                        _dv3=str(hr.get('dt_vencimento',''))[:10]
                        _dvbr3=f"{_dv3[8:10]}/{_dv3[5:7]}/{_dv3[:4]}" if len(_dv3)>=10 else _dv3
                        _dp3=str(hr.get('dt_pagamento','') or '')[:10]
                        _dpbr3=f"{_dp3[8:10]}/{_dp3[5:7]}/{_dp3[:4]}" if len(_dp3)>=10 else ''
                        _st3=str(hr.get('status','')).lower()
                        _ico='✅' if _st3 in ['pago','baixado'] else '⏳'
                        _cor='#166534' if _st3 in ['pago','baixado'] else '#92400E'
                        _doc=str(hr.get('documento','')); _doc_fmt=f"{_doc[:10]}" if len(_doc)>12 else f"{_doc}-{hr.get('ordem','')}"
                        _orig=str(hr.get('origem','')); _badge={'Legado':'🗂️','Sistema':'📋','PDV Novo':'🆕'}.get(_orig,_orig)
                        _pago_info=f" · Pago {_dpbr3}" if _dpbr3 else ''
                        st.markdown(f"<div style='padding:5px 0;border-bottom:1px solid #f0f0f0'>{_ico} <b>{_doc_fmt}</b> · {_dvbr3}{_pago_info} · <span style='color:{_cor};font-weight:700'>R$ {float(hr.get('valor_docto',0)):,.2f}</span> · {_badge}</div>", unsafe_allow_html=True)
            with _tr:
                try:
                    _rfm = _calcular_rfm(_cod)
                    _render_radar_rfm(_rfm, _nome)
                except Exception as _er:
                    st.error(f"Erro RFM: {_er}")

            with _tc:
                _dn = _nome.replace("'","''")
                dcad = run_query(f"SELECT id::text,nome,whatsapp,cpf,tags,ativo FROM clientes WHERE nome ILIKE '%{_dn}%' LIMIT 1")
                _cid_leg = f"legado_{_nome[:20].replace(' ','_').replace('/','')}"
                if dcad.empty:
                    st.info("Este cliente é do sistema legado. Preencha abaixo para migrar o cadastro (sem duplicar).")
                    _ea2,_eb2 = st.columns(2)
                    _wh_leg = str(_dfc['whatsapp'].iloc[0]) if not _dfc.empty and _dfc['whatsapp'].iloc[0] else ''
                    _en2 = _ea2.text_input("Nome", value=_nome, key=f"en2_{_cid_leg}")
                    _ew2 = _eb2.text_input("WhatsApp", value=_wh_leg, key=f"ew2_{_cid_leg}")
                    _ec3,_ed2 = st.columns(2)
                    _ec4 = _ec3.text_input('CPF', key=f'ec4_{_cid_leg}')
                    _et2 = _ed2.text_input('Tags (ex: VEREADORA)', key=f'et2_{_cid_leg}')
                    _eobs = st.text_input('Observacao', key=f'eobs_{_cid_leg}')
                    _cod_ext = _cod
                    if st.button('Migrar para sistema novo', key=f'es2_{_cid_leg}', type='primary'):
                        _nome_check = _en2.strip().upper()
                        _existe_ext = run_query('SELECT id,nome FROM clientes WHERE codigo_externo=%s LIMIT 1', [str(_cod_ext)])
                        _existe_nome_df = run_query(f"SELECT id,nome FROM clientes WHERE UPPER(nome)='{_nome_check}' LIMIT 1")
                        if not _existe_ext.empty:
                            st.warning(f"Ja migrado: {_existe_ext.iloc[0]['nome']}")
                        elif not _existe_nome_df.empty:
                            st.warning(f"Nome exato ja existe: {_existe_nome_df.iloc[0]['nome']}")
                            _ok_ins = run_command(
                                'INSERT INTO clientes (nome,whatsapp,cpf,tags,observacao,ativo,codigo_externo,created_at) VALUES (%s,%s,%s,%s,%s,true,%s,NOW())',
                                (_en2.strip(), _ew2 or None, _ec4 or None, _et2 or None, _eobs or None, str(_cod_ext)))
                            if _ok_ins:
                                # Atualiza nome nas duplicatas antigas para o novo nome
                                run_command('UPDATE duplicatas_abertas SET nome_cliente=%s WHERE codigo_cliente=%s',
                                    (_en2.strip(), str(_cod_ext)))
                                st.success(f'Cliente {_en2} migrado! Parcelas antigas atualizadas.')
                                st.rerun()
                            else:
                                st.error('Erro ao migrar.')
                else:
                    rc2 = dcad.iloc[0]; cid2 = str(rc2['id'])
                    _ea2,_eb2 = st.columns(2)
                    _en2 = _ea2.text_input('Nome', value=str(rc2['nome'] or ''), key=f'en2_{cid2}')
                    _ew2 = _eb2.text_input("WhatsApp", value=str(rc2['whatsapp'] or ''), key=f"ew2_{cid2}")
                    _ec3,_ed2 = st.columns(2)
                    _ec4 = _ec3.text_input("CPF", value=str(rc2['cpf'] or ''), key=f"ec4_{cid2}")
                    _et2 = _ed2.text_input("Tags", value=str(rc2['tags'] or ''), key=f"et2_{cid2}")
                    _eav2 = st.checkbox("Ativo", value=bool(rc2['ativo']), key=f"eav2_{cid2}")
                    if st.button("Salvar alteracoes", key=f"es2_{cid2}", type="primary"):
                        _ok_upd = run_command(
                            "UPDATE clientes SET nome=%s,whatsapp=%s,cpf=%s,ativo=%s WHERE id=%s",
                            (_en2.strip(), _ew2 or None, _ec4 or None, _eav2, cid2))
                        if _ok_upd:
                            st.success("Cadastro atualizado com sucesso!")
                            st.rerun()
                        else:
                            st.error("Erro ao salvar. Tente novamente.")

    return  # fim render_clientes_unificado

# ── DDL Fornecedores (escopo global — garante tabela ao iniciar) ─────────────
def _ensure_fornecedores_table():
    run_command("""
        CREATE TABLE IF NOT EXISTS fornecedores (
            id    BIGSERIAL PRIMARY KEY,
            nome  TEXT UNIQUE NOT NULL,
            tipo  TEXT,
            ativo BOOLEAN DEFAULT TRUE
        )
    """)
    run_command("ALTER TABLE fornecedores ADD COLUMN IF NOT EXISTS cnpj_cpf TEXT")
    run_command("ALTER TABLE fornecedores ADD COLUMN IF NOT EXISTS whatsapp1 TEXT")
    run_command("ALTER TABLE fornecedores ADD COLUMN IF NOT EXISTS whatsapp2 TEXT")
    run_command("ALTER TABLE fornecedores ADD COLUMN IF NOT EXISTS instagram1 TEXT")
    run_command("ALTER TABLE fornecedores ADD COLUMN IF NOT EXISTS instagram2 TEXT")
    run_command("ALTER TABLE fornecedores ADD COLUMN IF NOT EXISTS email TEXT")
    run_command("ALTER TABLE fornecedores ADD COLUMN IF NOT EXISTS endereco TEXT")
    run_command("ALTER TABLE fornecedores ADD COLUMN IF NOT EXISTS referencia TEXT")
    run_command("ALTER TABLE fornecedores ADD COLUMN IF NOT EXISTS observacoes TEXT")
    run_command("ALTER TABLE fornecedores ADD COLUMN IF NOT EXISTS foto_cartao BYTEA")
    run_command("ALTER TABLE fornecedores ADD COLUMN IF NOT EXISTS foto_cartao_nome TEXT")

_ensure_fornecedores_table()


def _render_forn(tipo, tk):
    import base64 as _b64fc
    df_fl = run_query("SELECT id, nome, cnpj_cpf, whatsapp1, whatsapp2, instagram1, instagram2, email, endereco, referencia, observacoes, ativo, foto_cartao, foto_cartao_nome FROM fornecedores WHERE tipo=%s ORDER BY nome", params=(tipo,))
    _b = st.text_input("🔍 Buscar", key=f"pfb_{tk}", placeholder="Nome, referência...")
    if not df_fl.empty:
        if _b.strip():
            _q = _b.strip().lower()
            df_fl = df_fl[df_fl["nome"].str.lower().str.contains(_q, na=False) | df_fl["referencia"].fillna("").str.lower().str.contains(_q, na=False)]
        st.caption(f"{len(df_fl)} registro(s)")
    _records = [] if df_fl.empty else list(df_fl.iterrows())
    _all_items = _records + [None]
    for _ri in range(0, len(_all_items), 3):
        _row_items = _all_items[_ri:_ri + 3]
        _cols = st.columns(3)
        for _ci, _item in enumerate(_row_items):
            with _cols[_ci]:
                if _item is None:
                    st.markdown('<div style="background:#1A2035;border:2px dashed #C9A227;border-radius:10px;display:flex;align-items:center;justify-content:center;height:120px;"><span style="font-size:40px;color:#C9A227;">＋</span></div>', unsafe_allow_html=True)
                    if st.button("➕ Novo cadastro", key=f"add_{tk}_{_ri}", use_container_width=True):
                        st.session_state[f"sf_{tk}"] = True
                        st.rerun()
                    continue
                _, fr = _item
                _fid = int(fr["id"])
                _fc_raw = fr.get("foto_cartao")
                _has_foto = _fc_raw is not None and len(bytes(_fc_raw)) > 0
                _fc_b64 = _b64fc.b64encode(bytes(_fc_raw)).decode() if _has_foto else ""
                _badge = '<span style="position:absolute;top:8px;right:8px;background:#C9A227;color:#000;padding:2px 7px;border-radius:10px;font-size:10px;font-weight:700;">Cartão</span>' if _has_foto else ""
                _hdr = f'<img src="data:image/jpeg;base64,{_fc_b64}" style="width:100%;height:120px;object-fit:cover;">' if _has_foto else '<div style="display:flex;align-items:center;justify-content:center;height:120px;font-size:44px;color:#C9A227;">👕</div>'
                _n = str(fr["nome"] or "—").replace("<", "&lt;").replace(">", "&gt;")
                _r = str(fr["referencia"] or fr.get("endereco") or "—").replace("<", "&lt;").replace(">", "&gt;")
                _w = str(fr["whatsapp1"] or "—").replace("<", "&lt;").replace(">", "&gt;")
                _g = str(fr["instagram1"] or "—").replace("<", "&lt;").replace(">", "&gt;")
                _ob = str(fr["observacoes"] or "").strip().replace("<", "&lt;").replace(">", "&gt;")
                _obs_div = f'<div style="background:#1F2937;border-radius:4px;padding:4px 7px;margin-top:5px;font-size:11px;color:#9CA3AF;">{_ob}</div>' if _ob else ""
                st.markdown(f'<div style="position:relative;background:#1A2035;border-radius:10px 10px 0 0;overflow:hidden;height:120px;">{_hdr}{_badge}</div><div style="background:#0E1117;border:1px solid #1F2937;border-top:none;border-radius:0 0 10px 10px;padding:10px 10px 6px;margin-bottom:4px;"><p style="font-weight:700;font-size:14px;margin:0 0 2px 0;color:#FFF;">{_n}</p><p style="color:#9CA3AF;font-size:12px;margin:0 0 4px 0;">{_r}</p><p style="margin:0 0 1px 0;font-size:12px;color:#25D366;">📱 {_w}</p><p style="margin:0 0 1px 0;font-size:12px;color:#C9A227;">📸 {_g}</p>{_obs_div}</div>', unsafe_allow_html=True)
                _ba, _bb = st.columns(2)
                if _ba.button("💬 WhatsApp", key=f"pwa_{tk}_{_fid}", use_container_width=True, disabled=not fr["whatsapp1"]):
                    _wn = str(fr["whatsapp1"]).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
                    st.markdown(f"[↗ Abrir no WhatsApp](https://wa.me/55{_wn})", unsafe_allow_html=True)
                if _bb.button("🪪 Ver Cartão", key=f"pvcbtn_{tk}_{_fid}", use_container_width=True, disabled=not _has_foto):
                    _dialog_ver_cartao(str(fr["nome"] or "—"), bytes(_fc_raw) if _has_foto else None, str(fr.get("foto_cartao_nome") or "foto.jpg"))
                _bc, _bd = st.columns(2)
                if _bc.button("✏️ Editar", key=f"ped_{tk}_{_fid}", use_container_width=True):
                    st.session_state[f"pedit_{tk}_{_fid}"] = not st.session_state.get(f"pedit_{tk}_{_fid}", False)
                if _bd.button("🗑️ Excluir", key=f"pdel_{tk}_{_fid}", use_container_width=True):
                    run_command("DELETE FROM fornecedores WHERE id=%s", (_fid,))
                    st.rerun()
    for _, fr in df_fl.iterrows():
        _fid = int(fr["id"])
        if st.session_state.get(f"pedit_{tk}_{_fid}", False):
            st.markdown(f"---\n#### ✏️ Editar: **{fr['nome']}**")
            with st.form(f"pef_{tk}_{_fid}"):
                _en1, _en2 = st.columns(2)
                _enm = _en1.text_input("Nome *", value=str(fr["nome"] or ""))
                _ecn = _en2.text_input("CNPJ/CPF", value=str(fr["cnpj_cpf"] or ""))
                _ew1, _ew2 = st.columns(2)
                _ewp1 = _ew1.text_input("📱 WhatsApp 1", value=str(fr["whatsapp1"] or ""))
                _ewp2 = _ew2.text_input("📱 WhatsApp 2", value=str(fr["whatsapp2"] or ""))
                _ei1, _ei2 = st.columns(2)
                _eis1 = _ei1.text_input("📸 Instagram 1", value=str(fr["instagram1"] or ""))
                _eis2 = _ei2.text_input("📸 Instagram 2", value=str(fr["instagram2"] or ""))
                _ee1, _ee2 = st.columns(2)
                _eem = _ee1.text_input("📧 Email", value=str(fr["email"] or ""))
                _erf = _ee2.text_input("🔖 Referência", value=str(fr["referencia"] or ""))
                _eend = st.text_input("📍 Endereço", value=str(fr["endereco"] or ""))
                _eobs = st.text_area("💬 Observações", value=str(fr["observacoes"] or ""), height=70)
                _efp = st.file_uploader("📷 Nova foto do cartão", type=["jpg", "jpeg", "png"], key=f"pefoto_{tk}_{_fid}") if tipo == "Fornecedor" else None
                _eat = st.checkbox("Ativo", value=bool(fr["ativo"]))
                _es1, _es2 = st.columns(2)
                _eok = _es1.form_submit_button("✅ Salvar", use_container_width=True)
                _eco = _es2.form_submit_button("❌ Cancelar", use_container_width=True)
                if _eco:
                    st.session_state[f"pedit_{tk}_{_fid}"] = False
                    st.rerun()
                if _eok:
                    if not _enm.strip():
                        st.error("Nome obrigatório.")
                    else:
                        _efb = _efp.read() if _efp else None
                        _efn = _efp.name if _efp else None
                        if _efb:
                            run_command("UPDATE fornecedores SET nome=%s,cnpj_cpf=%s,whatsapp1=%s,whatsapp2=%s,instagram1=%s,instagram2=%s,email=%s,referencia=%s,endereco=%s,observacoes=%s,ativo=%s,foto_cartao=%s,foto_cartao_nome=%s WHERE id=%s",
                                (_enm.strip(), _ecn.strip() or None, _ewp1.strip() or None, _ewp2.strip() or None, _eis1.strip() or None, _eis2.strip() or None, _eem.strip() or None, _erf.strip() or None, _eend.strip() or None, _eobs.strip() or None, _eat, _efb, _efn, _fid))
                        else:
                            run_command("UPDATE fornecedores SET nome=%s,cnpj_cpf=%s,whatsapp1=%s,whatsapp2=%s,instagram1=%s,instagram2=%s,email=%s,referencia=%s,endereco=%s,observacoes=%s,ativo=%s WHERE id=%s",
                                (_enm.strip(), _ecn.strip() or None, _ewp1.strip() or None, _ewp2.strip() or None, _eis1.strip() or None, _eis2.strip() or None, _eem.strip() or None, _erf.strip() or None, _eend.strip() or None, _eobs.strip() or None, _eat, _fid))
                        st.success(f"✅ {_enm.strip()} atualizado!")
                        st.session_state[f"pedit_{tk}_{_fid}"] = False
                        st.rerun()


def _form_forn(tipo, tk):
    st.markdown("---")
    _sk = f"sf_{tk}"
    if not st.session_state.get(_sk):
        if st.button(f"➕ Novo {tipo}",key=f"btn_{tk}",use_container_width=True):
            st.session_state[_sk]=True; st.rerun()
        return
    st.markdown(f"#### ➕ Novo {tipo}")
    with st.form(f"pf_{tk}"):
        n1,n2 = st.columns(2)
        _nm = n1.text_input("Nome *",placeholder="Ex: Inovar Modas")
        _cnpj = n2.text_input("CNPJ/CPF",placeholder="00.000.000/0001-00")
        w1,w2 = st.columns(2)
        _w1 = w1.text_input("📱 WhatsApp 1",placeholder="37 99999-9999")
        _w2 = w2.text_input("📱 WhatsApp 2",placeholder="11 99999-9999")
        i1,i2 = st.columns(2)
        _i1 = i1.text_input("📸 Instagram 1",placeholder="@fornecedor")
        _i2 = i2.text_input("📸 Instagram 2",placeholder="@perfil2")
        e1,e2 = st.columns(2)
        _em = e1.text_input("📧 Email",placeholder="contato@empresa.com")
        _ref = e2.text_input("🔖 Referência",placeholder="Rua da Juta, Brás-SP")
        _end = st.text_input("📍 Endereço",placeholder="Rua X, 000 — Bairro — Cidade/UF")
        _obs = st.text_area("💬 Observações",height=70)
        _foto = st.file_uploader("📷 Foto cartão de visita",type=["jpg","jpeg","png"],key=f"foto_{tk}") if tipo=="Fornecedor" else None
        sb1,sb2 = st.columns(2)
        _ok = sb1.form_submit_button("✅ Salvar",use_container_width=True)
        _no = sb2.form_submit_button("❌ Cancelar",use_container_width=True)
        if _no: st.session_state[_sk]=False; st.rerun()
        if _ok:
            if not _nm.strip(): st.error("Nome obrigatório.")
            else:
                _fb = _foto.read() if _foto else None
                _fn = _foto.name if _foto else None
                run_command("INSERT INTO fornecedores (nome,tipo,cnpj_cpf,whatsapp1,whatsapp2,instagram1,instagram2,email,referencia,endereco,observacoes,foto_cartao,foto_cartao_nome) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                    (_nm.strip(),tipo,_cnpj.strip() or None,_w1.strip() or None,_w2.strip() or None,_i1.strip() or None,_i2.strip() or None,_em.strip() or None,_ref.strip() or None,_end.strip() or None,_obs.strip() or None,_fb,_fn))
                st.success(f"✅ {_nm.strip()} salvo!")
                st.session_state[_sk]=False; st.rerun()

def _render_lista_forn_pag(tipo_filtro):
    _tk = tipo_filtro.split()[0][:4].lower()
    _render_forn(tipo_filtro, _tk)

def _form_novo_forn_pag(tipo):
    _tk = tipo.split()[0][:4].lower()
    _form_forn(tipo, _tk)



if pagina == "🏠 Visão Geral":
    if _role == "vendas":
        st.error("🔒 Área restrita — somente administradores.")
        st.stop()
    st.subheader("🏠 Visão Geral")

    # ── 🎂 Aniversariantes do Dia ─────────────────────────────────────────────
    _df_aniv = run_query("""
        SELECT nome FROM clientes
        WHERE ativo = true AND data_nascimento IS NOT NULL
          AND EXTRACT(MONTH FROM data_nascimento) = EXTRACT(MONTH FROM CURRENT_DATE)
          AND EXTRACT(DAY   FROM data_nascimento) = EXTRACT(DAY   FROM CURRENT_DATE)
        ORDER BY nome
    """)
    if not _df_aniv.empty:
        _nomes_aniv = ", ".join(_df_aniv["nome"].tolist())
        st.info(f"🎂 Aniversariantes hoje: **{_nomes_aniv}**")

    # ── 🚨 Sentinela de Boletos ───────────────────────────────────────────────
    _df_sentinela = run_query("""
        SELECT c.nome                              AS cliente,
               cr.valor_parcela,
               cr.data_vencimento,
               (CURRENT_DATE - cr.data_vencimento)::int AS dias_atraso,
               COALESCE(c.whatsapp, '')            AS fone
        FROM contas_receber cr
        JOIN vendas v   ON v.id  = cr.venda_id
        JOIN clientes c ON c.id  = v.cliente_id
        WHERE cr.status = 'aberto'
          AND cr.data_vencimento <= CURRENT_DATE
        ORDER BY cr.data_vencimento ASC
        LIMIT 20
    """)
    if not _df_sentinela.empty:
        _venc_hoje  = _df_sentinela[_df_sentinela["dias_atraso"] == 0]
        _vencidas   = _df_sentinela[_df_sentinela["dias_atraso"] > 0]
        _total_sent = float(_df_sentinela["valor_parcela"].sum())
        _header_cor = "#8B0000" if not _vencidas.empty else "#7A5200"
        _icone      = "🚨" if not _vencidas.empty else "⚠️"

        st.markdown(
            f"<div style='background:#FFF0F0;border-left:5px solid {_header_cor};"
            f"border-radius:8px;padding:12px 18px;margin-bottom:1rem'>"
            f"<b style='color:{_header_cor};font-size:1rem'>{_icone} Sentinela de Boletos</b>"
            f"<span style='color:#555;font-size:.85rem;margin-left:12px'>"
            f"{len(_df_sentinela)} parcela(s) — R$ {_total_sent:,.2f} a cobrar</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        _sc1, _sc2 = st.columns(2)
        if not _vencidas.empty:
            with _sc1:
                st.markdown(
                    f"<b style='color:#8B0000'>🔴 Vencidas ({len(_vencidas)})</b>",
                    unsafe_allow_html=True,
                )
                for _, _sv in _vencidas.iterrows():
                    st.markdown(
                        f"- **{_sv['cliente']}** — "
                        f"R$ {float(_sv['valor_parcela']):,.2f} "
                        f"· {int(_sv['dias_atraso'])}d atraso "
                        f"· venc. {_fmt_data(_sv['data_vencimento'])}"
                    )
        if not _venc_hoje.empty:
            with _sc2:
                st.markdown(
                    "<b style='color:#7A5200'>🟡 Vencem Hoje</b>",
                    unsafe_allow_html=True,
                )
                for _, _sv in _venc_hoje.iterrows():
                    st.markdown(
                        f"- **{_sv['cliente']}** — "
                        f"R$ {float(_sv['valor_parcela']):,.2f}"
                    )
        st.caption(
            "💡 Este alerta some automaticamente após as parcelas serem baixadas no Financeiro."
        )
        st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        df = run_query("SELECT COUNT(*) AS total FROM produtos")
        total_produtos = int(df["total"].iloc[0]) if not df.empty else "—"
        st.metric("Total de Produtos", total_produtos)

    with col2:
        df = run_query("SELECT COUNT(*) AS total FROM vendas")
        total_vendas = int(df["total"].iloc[0]) if not df.empty else "—"
        st.metric("Total de Vendas", total_vendas)

    with col3:
        df = run_query("SELECT COUNT(*) AS total FROM clientes WHERE ativo = true")
        total_clientes = int(df["total"].iloc[0]) if not df.empty else "—"
        st.metric("Clientes Ativos", total_clientes)

    with col4:
        df = run_query("SELECT COALESCE(SUM(valor_total), 0) AS total FROM vendas")
        total_receita = df["total"].iloc[0] if not df.empty else 0
        st.metric("Receita Total", f"R$ {total_receita:,.2f}")

    if _IS_ADMIN:
        st.markdown("---")
        df_lucro = run_query("""
            SELECT COALESCE(SUM((p.preco_venda - p.preco_custo) * iv.quantidade), 0) AS lucro_real
            FROM itens_venda iv
            JOIN produtos p ON p.id = iv.produto_id
        """)
        lucro_real = df_lucro["lucro_real"].iloc[0] if not df_lucro.empty else 0
        st.metric(
            "Lucro Real",
            f"R$ {lucro_real:,.2f}",
            help="(preco_venda − preco_custo) × quantidade — apenas admin",
        )

    # ── Card de Pendências de CPF ─────────────────────────────────────────────
    _df_cpf_pend = run_query("""
        SELECT COUNT(*) AS total FROM clientes
        WHERE ativo = true AND (cpf IS NULL OR TRIM(cpf::text) = '')
    """)
    _n_cpf_pend = int(_df_cpf_pend["total"].iloc[0]) if not _df_cpf_pend.empty else 0
    if _n_cpf_pend > 0:
        st.markdown(
            f"<div style='background:#FFF8E1;border-left:5px solid #F9A825;"
            f"border-radius:8px;padding:12px 18px;margin:0.5rem 0 0.8rem'>"
            f"<b style='color:#7A5200;font-size:1rem'>⚠️ Atenção: Cadastros Incompletos</b><br>"
            f"<span style='color:#555;font-size:.9rem'>"
            f"<b>{_n_cpf_pend}</b> cliente(s) com cadastro de CPF pendente. "
            f"Regularize para emissão de NF e relatórios fiscais.</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        _pend_col, _ = st.columns([1, 4])
        with _pend_col:
            if st.button("🔍 Ver Pendências", key="btn_cpf_pend_geral", use_container_width=True):
                st.session_state["_show_cpf_pend"] = not st.session_state.get("_show_cpf_pend", False)

        if st.session_state.get("_show_cpf_pend"):
            _df_pend_lista = run_query("""
                SELECT nome,
                       COALESCE(whatsapp, '—') AS celular,
                       created_at::date         AS cadastrado_em
                FROM clientes
                WHERE ativo = true AND (cpf IS NULL OR TRIM(cpf::text) = '')
                ORDER BY nome
            """)
            st.caption(f"Exibindo {len(_df_pend_lista)} cliente(s) sem CPF cadastrado.")
            _df_pend_fmt = _df_pend_lista.copy()
            if 'cadastrado_em' in _df_pend_fmt.columns:
                _df_pend_fmt['cadastrado_em'] = _df_pend_fmt['cadastrado_em'].apply(_fmt_data)
            st.dataframe(_df_pend_fmt.rename(columns={
                "nome": "Nome", "celular": "Celular", "cadastrado_em": "Cadastrado em"
            }), use_container_width=True)

    st.markdown("---")

    # ── Vendas hoje vs ontem ─────────────────────────────────────────────
    _df_hj_on = run_query("""
        SELECT
          COALESCE(SUM(CASE WHEN DATE(created_at)=CURRENT_DATE AND status!='cancelada' THEN valor_total END),0) AS hoje,
          COALESCE(SUM(CASE WHEN DATE(created_at)=CURRENT_DATE-1 AND status!='cancelada' THEN valor_total END),0) AS ontem,
          COUNT(CASE WHEN DATE(created_at)=CURRENT_DATE AND status!='cancelada' THEN 1 END) AS qtd_hoje,
          COUNT(CASE WHEN DATE(created_at)=CURRENT_DATE-1 AND status!='cancelada' THEN 1 END) AS qtd_ontem
        FROM vendas
    """)
    _vhj = float(_df_hj_on["hoje"].iloc[0]) if not _df_hj_on.empty else 0.0
    _von = float(_df_hj_on["ontem"].iloc[0]) if not _df_hj_on.empty else 0.0
    _delta_v = _vhj - _von
    _qhj = int(_df_hj_on["qtd_hoje"].iloc[0]) if not _df_hj_on.empty else 0
    _qon = int(_df_hj_on["qtd_ontem"].iloc[0]) if not _df_hj_on.empty else 0

    _vg_c1, _vg_c2 = st.columns(2)
    _vg_c1.metric("📊 Vendas Hoje", f"R$ {_vhj:,.2f}",
                   delta=f"R$ {_delta_v:+,.2f} vs ontem")
    _vg_c2.metric("🛒 Vendas Hoje (Qtd)", _qhj, delta=f"{_qhj - _qon:+d} vs ontem")

    # ── Meta mensal ───────────────────────────────────────────────────────
    _df_meta_cfg = run_query(
        "SELECT valor FROM config_geral WHERE chave = 'meta_mensal_vendas' LIMIT 1"
    )
    _meta_val = float(_df_meta_cfg["valor"].iloc[0]) if not _df_meta_cfg.empty else 0.0
    if _meta_val > 0:
        import datetime as _dtnow_vg
        _df_mes_vg = run_query("""
            SELECT COALESCE(SUM(valor_total),0) AS total
            FROM vendas
            WHERE DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE)
              AND status != 'cancelada'
        """)
        _realizado_vg = float(_df_mes_vg["total"].iloc[0]) if not _df_mes_vg.empty else 0.0
        _pct_meta = min(_realizado_vg / _meta_val * 100, 100)
        st.markdown(f"**🎯 Meta Mensal: R$ {_meta_val:,.2f}**")
        st.progress(int(_pct_meta), text=f"R$ {_realizado_vg:,.2f} realizado ({_pct_meta:.1f}%)")
    else:
        run_command(
            "INSERT INTO config_geral (chave, valor) VALUES ('meta_mensal_vendas','0') ON CONFLICT DO NOTHING"
        )
        _meta_input = st.number_input("🎯 Definir Meta Mensal (R$)", min_value=0.0, step=500.0, key="vg_meta_input")
        if st.button("Salvar Meta", key="vg_salvar_meta"):
            run_command("UPDATE config_geral SET valor=%s WHERE chave='meta_mensal_vendas'",
                        (str(_meta_input),))
            st.rerun()

    # ── Alertas ───────────────────────────────────────────────────────────
    _alertas = []
    _df_estq_crit = run_query(
        "SELECT COUNT(*) AS n FROM produtos WHERE ativo IS NOT FALSE AND estoque_atual <= 3"
    )
    _n_estq = int(_df_estq_crit["n"].iloc[0]) if not _df_estq_crit.empty else 0
    if _n_estq > 0:
        _alertas.append(f"📦 {_n_estq} produto(s) com estoque crítico (≤ 3 unidades)")

    _df_contas_venc = run_query("""
        SELECT COUNT(*) AS n FROM contas_a_pagar
        WHERE status='pendente' AND data_vencimento <= CURRENT_DATE + 3
    """)
    _n_cv = int(_df_contas_venc["n"].iloc[0]) if not _df_contas_venc.empty else 0
    if _n_cv > 0:
        _alertas.append(f"💳 {_n_cv} conta(s) a pagar vencendo em até 3 dias")

    _df_aniv = run_query("""
        SELECT nome FROM clientes
        WHERE ativo=true AND data_nascimento IS NOT NULL
          AND EXTRACT(MONTH FROM data_nascimento) = EXTRACT(MONTH FROM CURRENT_DATE)
          AND EXTRACT(DAY FROM data_nascimento) = EXTRACT(DAY FROM CURRENT_DATE)
    """)
    if not _df_aniv.empty:
        _nomes_aniv = ", ".join(_df_aniv["nome"].tolist())
        _alertas.append(f"🎂 Aniversariantes hoje: {_nomes_aniv}")

    if _alertas:
        st.markdown("---")
        st.markdown("**🔔 Alertas**")
        for _al in _alertas:
            st.warning(_al)
    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Últimas Vendas")
        df = run_query("""
            SELECT v.data_venda::date AS data, c.nome AS cliente,
                   v.valor_total, v.forma_pagamento, v.status_pagamento
            FROM vendas v
            LEFT JOIN clientes c ON c.id = v.cliente_id
            ORDER BY v.data_venda DESC
            LIMIT 10
        """)
        if not df.empty:
            df_fmt = df.copy()
            if 'data' in df_fmt.columns:
                df_fmt['data'] = df_fmt['data'].apply(_fmt_data)
            st.dataframe(df_fmt, use_container_width=True)
        else:
            st.info("Nenhuma venda registrada.")

    with col_b:
        st.subheader("Contas a Pagar (próximas)")
        df = run_query("""
            SELECT descricao, categoria, valor, data_vencimento, status
            FROM contas_a_pagar
            WHERE status = 'pendente'
            ORDER BY data_vencimento ASC
            LIMIT 10
        """)
        if not df.empty:
            df_fmt = df.copy()
            if 'data_vencimento' in df_fmt.columns:
                df_fmt['data_vencimento'] = df_fmt['data_vencimento'].apply(_fmt_data)
            st.dataframe(df_fmt, use_container_width=True)
        else:
            st.info("Nenhuma conta a pagar pendente.")

elif pagina == "📊 Relatórios":
    if _role == "vendas":
        st.error("🔒 Área restrita.")
        st.stop()
    import datetime as _dt_rel
    st.markdown("## 📊 Relatórios")
    _tipo_rel = st.selectbox("Tipo de Relatório", [
        "Vendas por Período","Recebimentos por Período","Duplicatas a Vencer",
        "Vendas por Cliente","Produtos Mais Vendidos","Margem por Produto",
        "Inadimplência","Fluxo de Caixa Diário",
        "Vendas por Forma de Pagamento","Ranking de Produtos","Ranking de Clientes","Clientes Inativos",
    ], key="rel_tipo")
    _col_d1,_col_d2,_col_gb = st.columns([2,2,1])
    _hoje_r = _dt_rel.date.today()
    _d1 = _col_d1.date_input("De", value=_hoje_r.replace(day=1), key="rel_d1", format="DD/MM/YYYY")
    _d2 = _col_d2.date_input("Até", value=_hoje_r, key="rel_d2", format="DD/MM/YYYY")
    _gerar = _col_gb.button("🔍 Gerar", key="rel_gerar", use_container_width=True, type="primary")
    # Campos de filtro adicionais por tipo
    _cli_busca_vp = ''
    _cli_busca_vc = ''
    _cli_busca_vp = ''
    _cli_busca_vc = ''
    if _tipo_rel in ('Vendas por Período', 'Vendas por Cliente'):
        _df_cli_rel = run_query("SELECT DISTINCT nome FROM clientes WHERE ativo=true ORDER BY nome")
        _cli_opts_rel = [''] + (_df_cli_rel['nome'].tolist() if not _df_cli_rel.empty else [])
        _cli_sel_rel = st.selectbox('Filtrar por cliente (opcional)',
            options=_cli_opts_rel,
            format_func=lambda x: 'Todos os clientes' if x=='' else x,
            key='rel_cli_filtro')
        _cli_busca_vp = _cli_sel_rel
        _cli_busca_vc = _cli_sel_rel
    if _gerar:
        st.session_state["_rel_gerado"] = True
        st.session_state["_rel_tipo_cache"] = _tipo_rel
        st.session_state["_rel_d1"] = str(_d1)
        st.session_state["_rel_d2"] = str(_d2)
    if st.session_state.get("_rel_gerado"):
        _d1s = st.session_state.get("_rel_d1", str(_d1))
        _d2s = st.session_state.get("_rel_d2", str(_d2))
        _tipo = st.session_state.get("_rel_tipo_cache", _tipo_rel)
        if _tipo == "Vendas por Período":
            _w_cli_vp = f"AND c.nome ILIKE '%{_cli_busca_vp.replace(chr(39),chr(39)*2)}%'" if _cli_busca_vp.strip() else ""
            df_r = run_query(f"""
                SELECT TO_CHAR(v.created_at,'DD/MM/YYYY') as Data,
                       c.nome as Cliente, v.valor_total as Total,
                       v.forma_pagamento as Forma, v.parcelas as Parcelas,
                       v.status_pagamento as Status,
                       v.id::text as venda_id,
                       STRING_AGG(COALESCE(iv.nome_produto,p.nome)||' x'||iv.quantidade::text,', ') as Itens
                FROM vendas v
                LEFT JOIN clientes c ON c.id=v.cliente_id
                LEFT JOIN itens_venda iv ON iv.venda_id=v.id
                LEFT JOIN produtos p ON p.id=iv.produto_id
                WHERE v.created_at::date BETWEEN '{_d1s}' AND '{_d2s}'
                  AND v.status != 'cancelada' {_w_cli_vp}
                GROUP BY v.id,v.created_at,c.nome,v.valor_total,v.forma_pagamento,v.parcelas,v.status_pagamento
                ORDER BY v.created_at DESC""")
            if df_r.empty:
                st.info("Nenhuma venda no período.")
            else:
                _t=float(df_r.iloc[:,2].sum()) if len(df_r.columns)>2 else 0
                c1,c2,c3=st.columns(3)
                _t_sum = float(df_r.iloc[:,2].sum()) if len(df_r.columns)>2 else 0
                c1.metric("Vendas",len(df_r)); c2.metric("Total",f"R$ {_t_sum:,.2f}"); c3.metric("Ticket médio",f"R$ {_t_sum/max(len(df_r),1):,.2f}")
                for _,row in df_r.iterrows():
                    with st.expander(f"📦 {row['data']} · {row['cliente']} · R$ {float(row['total']):,.2f} · {row['forma']}"):
                        st.write(f"**Itens:** {row['itens'] or '—'}")
                        st.write(f"**Parcelas:** {row['parcelas']} · **Status:** {row['status']}")
                        _cr=run_query(f"SELECT TO_CHAR(dt_vencimento,'DD/MM/YYYY') as Vencimento, valor_parcela as Valor, status as Status FROM contas_receber WHERE venda_id='{row['venda_id']}' ORDER BY dt_vencimento")
                        if not _cr.empty: st.dataframe(_cr,use_container_width=True,hide_index=True)
        elif _tipo == "Recebimentos por Período":
            df_r=run_query(f"""
                SELECT TO_CHAR(dt_baixa,'DD/MM/YYYY') as Data, nome_cliente as Cliente,
                       documento||'-'||ordem as Duplicata, valor_pago_total as Valor,
                       forma_recebimento as Forma
                FROM duplicatas_abertas
                WHERE status='Pago' AND dt_baixa BETWEEN '{_d1s}' AND '{_d2s}'
                UNION ALL
                SELECT TO_CHAR(cr.data_pagamento,'DD/MM/YYYY'), c.nome,
                       cr.nr_documento, cr.valor_pago_final, 'PDV'
                FROM contas_receber cr JOIN vendas v ON v.id=cr.venda_id
                JOIN clientes c ON c.id=v.cliente_id
                WHERE cr.status='Pago' AND cr.data_pagamento BETWEEN '{_d1s}' AND '{_d2s}'
                ORDER BY Data DESC""")
            if df_r.empty: st.info("Nenhum recebimento.")
            else:
                _t=float(df_r['Valor'].sum())
                c1,c2=st.columns(2); c1.metric("Recebimentos",len(df_r)); c2.metric("Total",f"R$ {_t:,.2f}")
                st.dataframe(df_r,use_container_width=True,hide_index=True)
        elif _tipo == "Duplicatas a Vencer":
            df_r=run_query(f"""
                SELECT nome_cliente as Cliente, documento||'-'||ordem as Duplicata,
                       TO_CHAR(dt_vencimento,'DD/MM/YYYY') as Vencimento,
                       valor_saldo as Saldo, GREATEST(0,CURRENT_DATE-dt_vencimento) as Atraso, modalidade as Modalidade
                FROM duplicatas_abertas
                WHERE status='Pendente' AND dt_vencimento BETWEEN '{_d1s}' AND '{_d2s}'
                ORDER BY dt_vencimento""")
            if df_r.empty: st.info("Nenhuma duplicata.")
            else:
                c1,c2,c3=st.columns(3); c1.metric("Parcelas",len(df_r)); c2.metric("Total",f"R$ {float(df_r['saldo'].sum()):,.2f}"); c3.metric("👥 Clientes",df_r['cliente'].nunique())
                st.dataframe(df_r,use_container_width=True,hide_index=True)
        elif _tipo == "Vendas por Cliente":
            if not _cli_busca_vc.strip():
                st.warning("Selecione um cliente para gerar o extrato.")
            else:
                _esc = _cli_busca_vc.replace(chr(39), chr(39)*2)
                _w_vc = f"AND c.nome ILIKE '%{_esc}%'"
                df_r = run_query(f"""
                    SELECT v.id::text as venda_id,
                           TO_CHAR(v.created_at,'DD/MM/YYYY') as Data,
                           c.nome as Cliente,
                           v.valor_total as Total,
                           v.forma_pagamento as Forma,
                           v.parcelas as Parcelas,
                           v.status_pagamento as Status,
                           STRING_AGG(COALESCE(iv.nome_produto,p.nome)||' x'||iv.quantidade::text, ', ') as Itens
                    FROM vendas v
                    LEFT JOIN clientes c ON c.id=v.cliente_id
                    LEFT JOIN itens_venda iv ON iv.venda_id=v.id
                    LEFT JOIN produtos p ON p.id=iv.produto_id
                    WHERE v.created_at::date BETWEEN '{_d1s}' AND '{_d2s}'
                      AND v.status != 'cancelada' {_w_vc}
                    GROUP BY v.id,v.created_at,c.nome,v.valor_total,v.forma_pagamento,v.parcelas,v.status_pagamento
                    ORDER BY v.created_at DESC
                """)
                if df_r.empty:
                    st.info("Nenhuma venda no periodo para este cliente.")
                else:
                    df_r.columns = [c.lower() for c in df_r.columns]
                    _tot_c = float(df_r["total"].sum())
                    _c1,_c2,_c3 = st.columns(3)
                    _c1.metric("Compras", len(df_r))
                    _c2.metric("Total comprado", f"R$ {_tot_c:,.2f}")
                    _c3.metric("Ticket medio", f"R$ {_tot_c/len(df_r):,.2f}")
                    st.markdown("---")
                    for _, row in df_r.iterrows():
                        _vid = str(row["venda_id"])
                        _cr = run_query(f"SELECT TO_CHAR(dt_vencimento,'DD/MM/YYYY') as Vencimento, valor_parcela as Valor, status as Status, TO_CHAR(dt_pagamento,'DD/MM/YYYY') as Pago_em FROM contas_receber WHERE venda_id='{_vid}' ORDER BY dt_vencimento")
                        _n_p = len(_cr) if not _cr.empty else int(row["parcelas"])
                        _sico = "OK" if str(row["status"]).lower()=="pago" else "ABERTO"
                        with st.expander(f"{_sico} | {row["data"]} | R$ {float(row["total"]):,.2f} | {row["forma"]} {_n_p}x | {row["itens"] or '---'}"):
                            ca, cb = st.columns(2)
                            ca.write(f"**Forma:** {row["forma"]} em {_n_p}x")
                            cb.write(f"**Total:** R$ {float(row["total"]):,.2f} | {row["status"]}")
                            if not _cr.empty:
                                st.markdown("**Parcelas:**")
                                st.dataframe(_cr, use_container_width=True, hide_index=True)
                            if st.button("Ver Cupom", key=f"cup_{_vid}"):
                                _cup = run_query(f"SELECT cupom_texto FROM vendas WHERE id='{_vid}' LIMIT 1")
                                if not _cup.empty and _cup.iloc[0]["cupom_texto"]:
                                    st.code(_cup.iloc[0]["cupom_text"], language=None)
                                else:
                                    st.info("Cupom nao disponivel.")
        elif _tipo == "Produtos Mais Vendidos":
            df_r=run_query(f"""
                SELECT p.nome as Produto, p.codigo_barras as Ref,
                       SUM(iv.quantidade) as QtdVendida,
                       SUM(iv.quantidade*iv.preco_unit) as Faturamento,
                       ROUND(AVG(iv.preco_unit),2) as PrecoMedio
                FROM itens_venda iv JOIN produtos p ON p.id=iv.produto_id
                JOIN vendas v ON v.id=iv.venda_id
                WHERE v.created_at::date BETWEEN '{_d1s}' AND '{_d2s}'
                  AND v.status != 'cancelada'
                GROUP BY p.nome,p.codigo_barras ORDER BY QtdVendida DESC LIMIT 50""")
            if df_r.empty: st.info("Nenhum item vendido.")
            else: st.dataframe(df_r,use_container_width=True,hide_index=True)
        elif _tipo == "Margem por Produto":
            df_r=run_query(f"""
                SELECT p.nome as Produto, SUM(iv.quantidade) as Qtd,
                       ROUND(AVG(iv.preco_unit),2) as PrecoVenda,
                       p.preco_custo as Custo,
                       ROUND(AVG(iv.preco_unit)-p.preco_custo,2) as MargemUnit,
                       ROUND((AVG(iv.preco_unit)-p.preco_custo)/NULLIF(AVG(iv.preco_unit),0)*100,1) as MargemPct
                FROM itens_venda iv JOIN produtos p ON p.id=iv.produto_id
                JOIN vendas v ON v.id=iv.venda_id
                WHERE v.created_at::date BETWEEN '{_d1s}' AND '{_d2s}'
                  AND v.status != 'cancelada'
                GROUP BY p.nome,p.preco_custo ORDER BY MargemPct DESC""")
            if df_r.empty: st.info("Nenhum dado.")
            else: st.dataframe(df_r,use_container_width=True,hide_index=True)
        elif _tipo == "Inadimplência":
            df_r=run_query("""
                SELECT nome_cliente as Cliente, COUNT(*) as Parcelas,
                       SUM(valor_saldo) as TotalDevido,
                       MAX(CURRENT_DATE-dt_vencimento) as MaiorAtraso,
                       MIN(TO_CHAR(dt_vencimento,'DD/MM/YYYY')) as VencMaisAntiga
                FROM duplicatas_abertas
                WHERE status='Pendente' AND dt_vencimento < CURRENT_DATE
                GROUP BY nome_cliente ORDER BY TotalDevido DESC""")
            if df_r.empty: st.success("Nenhum inadimplente!")
            else:
                c1,c2=st.columns(2); c1.metric("👥 Clientes",len(df_r)); c2.metric("Total em atraso",f"R$ {float(df_r['TotalDevido'].sum()):,.2f}")
                st.dataframe(df_r,use_container_width=True,hide_index=True)
        elif _tipo == "Vendas por Forma de Pagamento":
            df_r = run_query(f"""
                SELECT
                  forma_pagamento AS "Forma",
                  COUNT(*) AS "Nº Vendas",
                  COALESCE(SUM(valor_total),0) AS "Total (R$)",
                  ROUND(100.0*SUM(valor_total)/NULLIF(SUM(SUM(valor_total)) OVER(),0),1) AS "% Total"
                FROM vendas
                WHERE created_at::date BETWEEN '{_d1s}' AND '{_d2s}'
                  AND status != 'cancelada'
                GROUP BY forma_pagamento ORDER BY "Total (R$)" DESC
            """)
            if df_r.empty:
                st.info("Nenhuma venda no período.")
            else:
                df_r.columns = [c.lower().replace(" ","_").replace("(r$)","rs").replace("%","pct") for c in df_r.columns]
                try:
                    import plotly.express as _px_fp
                    _fig_fp = _px_fp.pie(df_r, names="forma", values="total_rs",
                                         title="Distribuição por Forma de Pagamento",
                                         hole=0.4, color_discrete_sequence=_px_fp.colors.qualitative.Pastel)
                    st.plotly_chart(_fig_fp, use_container_width=True)
                except Exception:
                    st.bar_chart(df_r.set_index("forma")["total_rs"])
                df_r_show = run_query(f"""
                    SELECT forma_pagamento AS "Forma",COUNT(*) AS "Nº Vendas",
                           COALESCE(SUM(valor_total),0) AS "Total (R$)"
                    FROM vendas WHERE created_at::date BETWEEN '{_d1s}' AND '{_d2s}'
                      AND status != 'cancelada'
                    GROUP BY forma_pagamento ORDER BY "Total (R$)" DESC
                """)
                st.dataframe(df_r_show, use_container_width=True, hide_index=True)
                try:
                    import plotly.express as _px_ev
                    _df_evol = run_query(f"""
                        SELECT TO_CHAR(DATE_TRUNC('month',created_at),'MM/YYYY') AS "Mês",
                               forma_pagamento AS "Forma",
                               SUM(valor_total) AS "Total"
                        FROM vendas WHERE created_at::date BETWEEN '{_d1s}' AND '{_d2s}'
                          AND status != 'cancelada'
                        GROUP BY DATE_TRUNC('month',created_at), forma_pagamento
                        ORDER BY DATE_TRUNC('month',created_at)
                    """)
                    if not _df_evol.empty:
                        _fig_ev = _px_ev.line(_df_evol, x="Mês", y="Total", color="Forma",
                                               title="Evolução Mensal por Forma de Pagamento",
                                               markers=True)
                        st.plotly_chart(_fig_ev, use_container_width=True)
                except Exception:
                    pass
        elif _tipo == "Ranking de Produtos":
            df_r = run_query(f"""
                SELECT p.nome AS "Produto", p.codigo_barras AS "Ref",
                       COALESCE(p.categoria, '—') AS "Categoria",
                       SUM(iv.quantidade) AS "Qtd Vendida",
                       SUM(iv.quantidade*iv.preco_unit) AS "Faturamento (R$)",
                       ROUND(AVG(iv.preco_unit),2) AS "Preço Médio"
                FROM itens_venda iv
                JOIN produtos p ON p.id = iv.produto_id
                JOIN vendas v ON v.id = iv.venda_id
                WHERE v.created_at::date BETWEEN '{_d1s}' AND '{_d2s}'
                  AND v.status != 'cancelada'
                GROUP BY p.nome, p.codigo_barras, p.categoria
                ORDER BY "Qtd Vendida" DESC LIMIT 10
            """)
            if df_r.empty:
                st.info("Nenhum item vendido no período.")
            else:
                st.markdown("**Top 10 Produtos por Quantidade**")
                try:
                    import plotly.express as _px_pr
                    _fig_pr = _px_pr.bar(df_r, x="Produto", y="Qtd Vendida",
                                          color="Faturamento (R$)",
                                          title="Top 10 Produtos Mais Vendidos",
                                          color_continuous_scale="Reds")
                    st.plotly_chart(_fig_pr, use_container_width=True)
                except Exception:
                    pass
                st.dataframe(df_r, use_container_width=True, hide_index=True)
        elif _tipo == "Ranking de Clientes":
            df_r = run_query(f"""
                SELECT c.nome AS "Cliente",
                       COUNT(v.id) AS "Nº Compras",
                       SUM(v.valor_total) AS "Total (R$)",
                       ROUND(AVG(v.valor_total),2) AS "Ticket Médio",
                       MAX(v.created_at::date) AS "Última Compra"
                FROM vendas v JOIN clientes c ON c.id = v.cliente_id
                WHERE v.created_at::date BETWEEN '{_d1s}' AND '{_d2s}'
                  AND v.status != 'cancelada'
                GROUP BY c.nome ORDER BY "Total (R$)" DESC LIMIT 10
            """)
            if df_r.empty:
                st.info("Nenhuma venda no período.")
            else:
                st.markdown("**Top 10 Clientes por Valor**")
                try:
                    import plotly.express as _px_cli
                    _fig_cli = _px_cli.bar(df_r, x="Cliente", y="Total (R$)",
                                            title="Top 10 Clientes", color="Nº Compras",
                                            color_continuous_scale="Purples")
                    st.plotly_chart(_fig_cli, use_container_width=True)
                except Exception:
                    pass
                st.dataframe(df_r, use_container_width=True, hide_index=True)
        elif _tipo == "Clientes Inativos":
            df_r = run_query("""
                SELECT c.nome AS "Cliente",
                       COALESCE(c.whatsapp,'—') AS "WhatsApp",
                       MAX(v.created_at::date) AS "Última Compra",
                       (CURRENT_DATE - MAX(v.created_at::date))::int AS "Dias Inativo",
                       COUNT(v.id) AS "Total Compras"
                FROM clientes c LEFT JOIN vendas v ON v.cliente_id = c.id
                WHERE c.ativo = true
                GROUP BY c.id, c.nome, c.whatsapp
                HAVING MAX(v.created_at::date) < CURRENT_DATE - INTERVAL '60 days'
                   OR MAX(v.created_at::date) IS NULL
                ORDER BY "Dias Inativo" DESC NULLS FIRST
            """)
            if df_r.empty:
                st.success("Nenhum cliente inativo (todos compraram nos últimos 60 dias)!")
            else:
                st.warning(f"⚠️ {len(df_r)} clientes inativos há mais de 60 dias")
                st.dataframe(df_r, use_container_width=True, hide_index=True)
                try:
                    _taxa_ret = run_query("""
                        SELECT ROUND(100.0 * COUNT(DISTINCT cliente_id) /
                               NULLIF((SELECT COUNT(*) FROM clientes WHERE ativo=true),0),1) AS taxa
                        FROM vendas WHERE created_at >= CURRENT_DATE - INTERVAL '60 days'
                    """)
                    if not _taxa_ret.empty:
                        st.metric("Taxa de Retorno (60d)", f"{float(_taxa_ret['taxa'].iloc[0])}%")
                except Exception:
                    pass
        elif _tipo == "Fluxo de Caixa Diário":
            df_leg=run_query(f"SELECT TO_CHAR(dt_baixa,'DD/MM/YYYY') as Data, SUM(valor_pago_total) as Legado FROM duplicatas_abertas WHERE status='Pago' AND dt_baixa BETWEEN '{_d1s}' AND '{_d2s}' GROUP BY dt_baixa ORDER BY dt_baixa")
            df_pdv=run_query(f"SELECT TO_CHAR(data_pagamento,'DD/MM/YYYY') as Data, SUM(valor_pago_final) as PDV FROM contas_receber WHERE status='Pago' AND data_pagamento BETWEEN '{_d1s}' AND '{_d2s}' GROUP BY data_pagamento ORDER BY data_pagamento")
            if df_leg.empty and df_pdv.empty: st.info("Nenhum movimento.")
            else:
                import pandas as _pd_fc
                _dfc=_pd_fc.merge(df_leg,df_pdv,on='Data',how='outer').fillna(0)
                _dfc['Total']=_dfc.get('Legado',0)+_dfc.get('PDV',0)
                st.metric("Total período",f"R$ {float(_dfc['Total'].sum()):,.2f}")
                st.dataframe(_dfc,use_container_width=True,hide_index=True)
        st.markdown("---")
        if st.button("📄 Gerar PDF", key="rel_btn_pdf", type="primary"):
            import streamlit.components.v1 as _comp_r
            from datetime import datetime as _dtnow
            _tipo_l = st.session_state.get("_rel_tipo_cache","Relatorio")
            _d1_l = st.session_state.get("_rel_d1","")
            _d2_l = st.session_state.get("_rel_d2","")
            try:
                _cols_r = list(df_r.columns)
                _th = "".join([f"<th style='padding:6px;background:#374151;color:white;font-size:11px'>{c}</th>" for c in _cols_r])
                _tb = ""
                for _ix2,(_,_rr2) in enumerate(df_r.iterrows()):
                    _bg2 = "#f9fafb" if _ix2%2==0 else "#fff"
                    _tb += "<tr style='background:"+_bg2+"'>" + "".join([f"<td style='padding:5px;font-size:11px;border-bottom:1px solid #e5e7eb'>{v}</td>" for v in _rr2]) + "</tr>"
                _dt_str = _dtnow.now().strftime("%d/%m/%Y %H:%M")
                _h1 = "<div id='reljg' style='font-family:Arial,sans-serif;padding:20px'>"
                _h2 = f"<div style='font-size:17px;font-weight:700'>{_tipo_l}</div>"
                _h3 = f"<div style='font-size:11px;color:#6B7280'>Periodo: {_d1_l} a {_d2_l} | {_dt_str}</div>"
                _h4 = f"<table style='width:100%;border-collapse:collapse'><thead><tr>{_th}</tr></thead><tbody>{_tb}</tbody></table>"
                _h5 = "<div style='font-size:10px;color:#9CA3AF;margin-top:8px'>JGAutomacoes.AI - GM Homem Itauna</div></div>"
                _html_final = _h1 + _h2 + _h3 + _h4 + _h5
                _btn_js = "<button onclick=\"(function(){var c=document.getElementById('reljg').outerHTML;var w=window.open('','_blank','width=900,height=700');w.document.write('<html><head><title>Rel</title><style>body{padding:20px;font-family:Arial}@media print{button{display:none}}</style></head><body>'+c+'<br><button onclick=window.print() style=width:100%;padding:10px;background:#111;color:#fff;border:none;cursor:pointer>Imprimir</button></body></html>');w.document.close();setTimeout(function(){w.print()},500)})()\" style='width:100%;padding:12px;background:#1D4ED8;color:white;border:none;border-radius:8px;cursor:pointer;margin-top:10px'>Imprimir / Salvar PDF</button>"
                _comp_r.html(_html_final + _btn_js, height=600, scrolling=True)
            except Exception as _ep:
                st.error(f"Erro PDF: {_ep}")
elif pagina == "📦 Estoque":
    st.subheader("📦 Estoque de Produtos")
    _is_admin = _IS_ADMIN
    run_command("ALTER TABLE produtos ADD COLUMN IF NOT EXISTS observacao TEXT")
    run_command("ALTER TABLE produtos ADD COLUMN IF NOT EXISTS cor TEXT")

    # Vendas só vê o Catálogo (consulta); abas de cadastro são exclusivas do admin
    if _is_admin:
        _tab_cat, _tab_cad_r, _tab_cad_c = st.tabs(
            ["📦 Catálogo", "➕ Cadastro Rápido", "🎨 Cadastro Completo (Grades)"]
        )
    else:
        [_tab_cat] = st.tabs(["📦 Catálogo"])

    with _tab_cat:

        # ── Estado ───────────────────────────────────────────────────────────────
        for _k0, _v0 in [("est_dlg_row", None), ("est_dlg_reset", 0),
                         ("est_edit_pid", None), ("est_grade_pid", None), ("est_del_pid", None)]:
            if _k0 not in st.session_state:
                st.session_state[_k0] = _v0

        # ── Miniatura de produto ─────────────────────────────────────────────────
        _FOTO_DIR_EST = _FOTO_DIR_PROD
        _ICONE_PADRAO = (
            "data:image/svg+xml;charset=utf-8,"
            "%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E"
            "%3Crect width='200' height='200' fill='%23f0ead6'/%3E"
            "%3Ctext x='50%25' y='54%25' dominant-baseline='middle' "
            "text-anchor='middle' font-size='72' fill='%23C9A84C'%3E%F0%9F%93%A6%3C/text%3E"
            "%3C/svg%3E"
        )

        def _foto_thumb(foto_url_raw):
            import base64 as _b64, io as _io
            from PIL import Image as _Img
            _nome = str(foto_url_raw or "").strip().lstrip("=").strip()
            if not _nome or _nome in ("pendente.jpg", "sem-foto.jpg", ""):
                return _ICONE_PADRAO
            _cam = os.path.join(_FOTO_DIR_EST, _nome)
            if not os.path.exists(_cam):
                return _ICONE_PADRAO
            try:
                with _Img.open(_cam) as _im:
                    _im.thumbnail((300, 300), _Img.LANCZOS)
                    _buf = _io.BytesIO()
                    _im.convert("RGB").save(_buf, format="JPEG", quality=80)
                return "data:image/jpeg;base64," + _b64.b64encode(_buf.getvalue()).decode()
            except Exception:
                return _ICONE_PADRAO

        # ── Carregar produtos ────────────────────────────────────────────────────
        df_est = run_query("""
            SELECT id::text,
                   codigo_barras,
                   nome,
                   categoria,
                   cor,
                   fornecedor_ref,
                   preco_custo,
                   preco_venda,
                   estoque_atual,
                   estoque_minimo,
                   ultima_entrada,
                   descricao_detalhada,
                   foto_url,
                   data_lancamento,
                   created_at::date AS cadastrado_em
            FROM produtos
            WHERE ativo IS NOT FALSE
            ORDER BY nome ASC
            LIMIT 500
        """)
        if not df_est.empty:
            df_est["_codigo"] = df_est["id"].str[:8].str.upper()

        # ── Carregar grades (uma query) ──────────────────────────────────────────
        df_var_all = run_query(
            "SELECT produto_id::text AS pid, tamanho, estoque "
            "FROM produto_variacoes WHERE estoque > 0 ORDER BY tamanho"
        )
        _grades: dict = {}
        if not df_var_all.empty:
            for _, _vr in df_var_all.iterrows():
                _grades.setdefault(str(_vr["pid"]), []).append(
                    (str(_vr["tamanho"]), int(_vr["estoque"]))
                )

        if df_est.empty:
            st.info("Nenhum produto cadastrado.")
        else:
            # ── KPIs ─────────────────────────────────────────────────────────────
            _total_skus  = len(df_est)
            _total_unid  = int(df_est["estoque_atual"].fillna(0).sum())
            _total_custo = float(
                (df_est["preco_custo"].fillna(0) * df_est["estoque_atual"].fillna(0)).sum()
            )
            _total_venda = float(
                (df_est["preco_venda"].fillna(0) * df_est["estoque_atual"].fillna(0)).sum()
            )
            _criticos = int(
                (df_est["estoque_atual"].fillna(0) < df_est["estoque_minimo"].fillna(0)).sum()
            )

            _km1, _km2, _km3, _km4 = st.columns(4)
            _km1.metric("Produtos", _total_skus)
            _km2.metric("Total Unidades", f"{_total_unid}")
            if _is_admin:
                _km3.metric("Custo Total Estoque", f"R$ {_total_custo:,.2f}")
                _km4.metric("Valor Total a Venda", f"R$ {_total_venda:,.2f}")
            else:
                _km3.metric("Valor a Venda", f"R$ {_total_venda:,.2f}")
                _km4.metric("Abaixo do Mínimo", _criticos,
                            delta=f"-{_criticos}" if _criticos else None,
                            delta_color="inverse")

            st.markdown("---")

            # ── Filtros ───────────────────────────────────────────────────────────
            if _is_admin:
                _ff1, _ff2, _ff3, _ff4 = st.columns(4)
            else:
                _ff1, _ff2, _ff3 = st.columns(3)
                _ff4 = None

            with _ff1:
                _est_busca = st.text_input(
                    "🔍 Buscar produto", key="est_busca",
                    placeholder="Nome, referência, cor..."
                ).strip().lower()
            with _ff2:
                _cats_lista = ["Todas"] + sorted(
                    df_est["categoria"].dropna().unique().tolist()
                )
                _cat_sel = st.selectbox("Categoria", _cats_lista, key="est_cat_sel")
            with _ff3:
                _cors_raw = df_est["cor"].dropna()
                _cors_raw = _cors_raw[_cors_raw.str.strip() != ""]
                _cors_lista = ["Todas"] + sorted(_cors_raw.unique().tolist())
                _cor_sel = st.selectbox("Cor", _cors_lista, key="est_cor_sel")
            _forn_sel = "Todos"
            if _is_admin and _ff4 is not None:
                with _ff4:
                    _forn_lista = ["Todos"] + sorted(
                        df_est["fornecedor_ref"].dropna().unique().tolist()
                    )
                    _forn_sel = st.selectbox("Fornecedor", _forn_lista, key="est_forn_sel")

            # ── Aplicar filtros ───────────────────────────────────────────────────
            df_filtrado = df_est.copy()
            if _cat_sel != "Todas":
                df_filtrado = df_filtrado[df_filtrado["categoria"] == _cat_sel]
            if _cor_sel != "Todas":
                df_filtrado = df_filtrado[df_filtrado["cor"] == _cor_sel]
            if _forn_sel != "Todos":
                df_filtrado = df_filtrado[df_filtrado["fornecedor_ref"] == _forn_sel]
            if _est_busca:
                import unicodedata as _ud
                def _sem_acento(s):
                    return ''.join(
                        c for c in _ud.normalize('NFD', str(s).lower())
                        if _ud.category(c) != 'Mn'
                    )
                _bn = _sem_acento(_est_busca)
                _mask_est = (
                    df_filtrado["nome"].apply(_sem_acento).str.contains(_bn, na=False)
                    | df_filtrado["codigo_barras"].fillna("").apply(_sem_acento).str.contains(_bn, na=False)
                    | df_filtrado["cor"].fillna("").apply(_sem_acento).str.contains(_bn, na=False)
                    | df_filtrado["categoria"].fillna("").apply(_sem_acento).str.contains(_bn, na=False)
                )
                df_filtrado = df_filtrado[_mask_est]

            st.caption(f"{len(df_filtrado)} produto(s) encontrado(s)")

            # ── Confirmação de exclusão (admin_master) ────────────────────────────
            _del_pid = st.session_state.get("est_del_pid")
            if _del_pid and _IS_MASTER:
                _del_r = df_est[df_est["id"] == _del_pid]
                _del_nome = _del_r["nome"].iloc[0] if not _del_r.empty else _del_pid
                st.warning(f"⚠️ Confirmar exclusão de **{_del_nome}**? Não pode ser desfeito.")
                _dc1, _dc2, _ = st.columns([1, 1, 4])
                if _dc1.button("🗑️ Confirmar exclusão", type="primary",
                               key="est_del_confirm", use_container_width=True):
                    run_command(
                        "UPDATE produtos SET ativo=FALSE WHERE id::text=%s", (_del_pid,)
                    )
                    st.session_state.est_del_pid = None
                    st.session_state.est_dlg_reset += 1
                    st.rerun()
                if _dc2.button("Cancelar", key="est_del_cancel", use_container_width=True):
                    st.session_state.est_del_pid = None
                    st.rerun()

            # ── Formulário inline: Ajustar Grade ─────────────────────────────────
            _grade_pid = st.session_state.get("est_grade_pid")
            if _grade_pid and _is_admin:
                _gp_r = df_est[df_est["id"] == _grade_pid]
                if not _gp_r.empty:
                    _gp_nome = _gp_r["nome"].iloc[0]
                    with st.expander(f"📏 Ajustar Grade — **{_gp_nome}**", expanded=True):
                        _tamanhos_g = ["PP","P","M","G","GG","XGG",
                                       "34","36","38","40","42","44","46","48","U"]
                        _pv_map_g = dict(_grades.get(_grade_pid, []))
                        with st.form(f"grade_form_{_grade_pid[:8]}"):
                            _gu_c = st.columns(8)
                            _gu_q: dict = {}
                            for _gi_g, _tam_g in enumerate(_tamanhos_g):
                                with _gu_c[_gi_g % 8]:
                                    _gu_q[_tam_g] = st.number_input(
                                        _tam_g, min_value=0,
                                        value=int(_pv_map_g.get(_tam_g, 0)),
                                        step=1, key=f"gf_{_grade_pid[:8]}_{_tam_g}"
                                    )
                            _total_grade_f = sum(_gu_q.values())
                            if _total_grade_f > 0:
                                st.info(f"Total: **{_total_grade_f}** unidades")
                            _gc1, _gc2 = st.columns(2)
                            if _gc1.form_submit_button("💾 Salvar Grade",
                                                        use_container_width=True):
                                try:
                                    with _db_get_conn() as _conn_gf:
                                        with _conn_gf.cursor() as _cur_gf:
                                            for _tam_gf, _qtd_gf in _gu_q.items():
                                                _cur_gf.execute(
                                                    "INSERT INTO produto_variacoes "
                                                    "(produto_id, tamanho, estoque) "
                                                    "VALUES (%s, %s, %s) "
                                                    "ON CONFLICT (produto_id, tamanho) "
                                                    "DO UPDATE SET estoque=EXCLUDED.estoque",
                                                    (_grade_pid, _tam_gf, _qtd_gf),
                                                )
                                            _cur_gf.execute(
                                                "UPDATE produtos SET estoque_atual=%s "
                                                "WHERE id::text=%s",
                                                (_total_grade_f, _grade_pid),
                                            )
                                    st.session_state.est_grade_pid = None
                                    st.session_state.est_dlg_reset += 1
                                    st.success(
                                        f"Grade salva! Estoque total: {_total_grade_f} un."
                                    )
                                    st.rerun()
                                except Exception as _e_gf:
                                    st.error(f"Erro ao salvar grade: {_e_gf}")
                            if _gc2.form_submit_button("Fechar", use_container_width=True):
                                st.session_state.est_grade_pid = None
                                st.rerun()

            # ── Formulário inline: Editar Produto ────────────────────────────────
            _edit_pid = st.session_state.get("est_edit_pid")
            if _edit_pid and _is_admin:
                _ep_r = df_est[df_est["id"] == _edit_pid]
                if not _ep_r.empty:
                    _ep = _ep_r.iloc[0]
                    with st.expander(f"✏️ Editando — **{_ep['nome']}**", expanded=True):
                        with st.form(f"edit_form_{_edit_pid[:8]}"):
                            _ec1, _ec2 = st.columns(2)
                            _ep_nome = _ec1.text_input(
                                "Nome *", value=str(_ep.get("nome") or ""),
                                key=f"ef_nome_{_edit_pid[:8]}"
                            )
                            _ep_cat_opts = ["Camisas","Camisetas","Calças","Moletons",
                                            "Bermudas","Jaquetas","Acessórios","Calçados","Outros"]
                            _ep_cat_val = str(_ep.get("categoria") or "Outros")
                            _ep_cat_idx = (_ep_cat_opts.index(_ep_cat_val)
                                           if _ep_cat_val in _ep_cat_opts else 0)
                            _ep_cat = _ec2.selectbox(
                                "Categoria", _ep_cat_opts, index=_ep_cat_idx,
                                key=f"ef_cat_{_edit_pid[:8]}"
                            )
                            _ec3, _ec4 = st.columns(2)
                            _cores_e = ["","Preto","Branco","Cinza","Cinza Mescla","Marrom",
                                        "Marrom Claro","Bege","Azul Marinho","Azul Claro",
                                        "Vinho","Verde","Verde Militar","Caramelo","Laranja",
                                        "Vermelho","Roxo","Rosa","Amarelo","Estampado","Multicolor"]
                            _ep_cor_val = str(_ep.get("cor") or "")
                            _ep_cor_idx = (_cores_e.index(_ep_cor_val)
                                           if _ep_cor_val in _cores_e else 0)
                            _ep_cor = _ec3.selectbox(
                                "🎨 Cor", _cores_e, index=_ep_cor_idx,
                                key=f"ef_cor_{_edit_pid[:8]}"
                            )
                            _df_fe = run_query("SELECT nome FROM fornecedores WHERE ativo=true ORDER BY nome")
                            _fe_opts = ["— Nenhum —"] + _df_fe["nome"].tolist() if not _df_fe.empty else ["— Nenhum —"]
                            _fe_atual = str(_ep.get("fornecedor_ref") or "")
                            _fe_idx = _fe_opts.index(_fe_atual) if _fe_atual in _fe_opts else 0
                            _ep_forn = _ec4.selectbox("🏭 Fornecedor", _fe_opts, index=_fe_idx, key=f"ef_forn_{_edit_pid[:8]}")
                            _ep_forn = _ep_forn if _ep_forn != "— Nenhum —" else ""
                            _ep1, _ep2, _ep3 = st.columns(3)
                            _ep_custo = _ep1.number_input(
                                "Custo (R$)", min_value=0.0,
                                value=float(_ep.get("preco_custo") or 0),
                                format="%.2f", key=f"ef_custo_{_edit_pid[:8]}"
                            )
                            _ep_venda = _ep2.number_input(
                                "Venda (R$)", min_value=0.0,
                                value=float(_ep.get("preco_venda") or 0),
                                format="%.2f", key=f"ef_venda_{_edit_pid[:8]}"
                            )
                            _ep_min = _ep3.number_input(
                                "Est. mínimo", min_value=0,
                                value=int(_ep.get("estoque_minimo") or 0),
                                key=f"ef_min_{_edit_pid[:8]}"
                            )
                            _ep_desc = st.text_area(
                                "Descrição / Observação",
                                value=str(_ep.get("descricao_detalhada") or ""),
                                key=f"ef_desc_{_edit_pid[:8]}"
                            )
                            _esb1, _esb2 = st.columns(2)
                            if _esb1.form_submit_button("💾 Salvar", use_container_width=True):
                                if not _ep_nome.strip():
                                    st.error("Nome obrigatório.")
                                elif _ep_venda <= 0:
                                    st.error("Preço de venda deve ser maior que zero.")
                                else:
                                    _ok_ep = run_command(
                                        "UPDATE produtos SET nome=%s, categoria=%s, cor=%s, "
                                        "fornecedor_ref=%s, preco_custo=%s, preco_venda=%s, "
                                        "estoque_minimo=%s, descricao_detalhada=%s "
                                        "WHERE id::text=%s",
                                        (_ep_nome.strip(), _ep_cat,
                                         _ep_cor if _ep_cor else None,
                                         _ep_forn.strip() or None,
                                         _ep_custo, _ep_venda, _ep_min,
                                         _ep_desc.strip() or None,
                                         _edit_pid),
                                    )
                                    if _ok_ep:
                                        st.session_state.est_edit_pid = None
                                        st.session_state.est_dlg_reset += 1
                                        st.success("✅ Produto atualizado!")
                                        st.rerun()
                            if _esb2.form_submit_button("Cancelar", use_container_width=True):
                                st.session_state.est_edit_pid = None
                                st.rerun()

                        # Foto fora do form (file_uploader não funciona bem dentro de form)
                        _ef_foto_cur = str(_ep.get("foto_url") or "").strip()
                        if _ef_foto_cur and _ef_foto_cur not in ("pendente.jpg", "sem-foto.jpg"):
                            _ef_foto_path = os.path.join(_FOTO_DIR_PROD, _ef_foto_cur)
                            if os.path.exists(_ef_foto_path):
                                st.image(_ef_foto_path, width=120, caption="Foto atual")
                        _ef_nova_foto = st.file_uploader(
                            "📷 Nova foto do produto",
                            type=["jpg", "jpeg", "png", "webp"],
                            key=f"ef_foto_{_edit_pid[:8]}",
                        )
                        if _ef_nova_foto:
                            st.image(_ef_nova_foto, width=120, caption="Preview nova foto")
                            if st.button("📷 Atualizar Foto", key=f"btn_foto_{_edit_pid[:8]}", use_container_width=True):
                                import io as _io_ef
                                from PIL import Image as _PilEf
                                os.makedirs(_FOTO_DIR_PROD, exist_ok=True)
                                _ef_img = _PilEf.open(_ef_nova_foto)
                                _ef_img.thumbnail((800, 800), _PilEf.LANCZOS)
                                _ef_fname = f"{_edit_pid}.jpg"
                                _ef_img.convert("RGB").save(
                                    os.path.join(_FOTO_DIR_PROD, _ef_fname), "JPEG", quality=85
                                )
                                run_command(
                                    "UPDATE produtos SET foto_url=%s WHERE id::text=%s",
                                    (_ef_fname, _edit_pid),
                                )
                                st.success("✅ Foto atualizada!")
                                st.rerun()

            # ── Cards em grade 4 colunas ──────────────────────────────────────────
            df_filtrado = df_filtrado.reset_index(drop=True)
            _COLS_CARD = 4

            st.markdown("""
<style>
.gm-card{border:1px solid #e0ddd5;border-radius:12px;overflow:hidden;background:#fff;
  margin-bottom:10px;box-shadow:0 2px 6px rgba(0,0,0,.07);}
.gm-card img{width:100%;height:200px;object-fit:contain;display:block;background:#f8f6f0;padding:8px;}
.gm-card-body{padding:10px 10px 6px;}
.gm-badges{display:flex;flex-wrap:wrap;gap:3px;margin-bottom:6px;}
.gm-badge-cat{background:#1A2035;color:#fff;padding:2px 7px;
  border-radius:10px;font-size:10px;font-weight:600;}
.gm-badge-cor{background:#C9A84C;color:#fff;padding:2px 7px;
  border-radius:10px;font-size:10px;font-weight:600;}
.gm-badge-low{background:#ffd6d6;color:#8b0000;padding:2px 7px;
  border-radius:10px;font-size:10px;font-weight:600;}
.gm-nome{font-weight:700;font-size:13px;line-height:1.3;color:#0D1117;
  margin-bottom:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.gm-forn{font-size:11px;color:#888;margin-bottom:5px;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.gm-pricerow{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px;}
.gm-price{font-size:15px;font-weight:800;color:#C9A84C;}
.gm-margem{font-size:11px;font-weight:600;color:#27ae60;}
.gm-grade{font-size:10px;color:#555;background:#f5f3ee;padding:3px 6px;
  border-radius:6px;font-family:monospace;}
</style>""", unsafe_allow_html=True)

            for _ci in range(0, len(df_filtrado), _COLS_CARD):
                _chunk = df_filtrado.iloc[_ci:_ci + _COLS_CARD]
                _gcols = st.columns(_COLS_CARD)
                for _cj, (_, _row) in enumerate(_chunk.iterrows()):
                    with _gcols[_cj]:
                        _pid_c   = str(_row.get("id") or "")
                        _pid_key = _pid_c[:12]

                        # Grade de tamanhos
                        _grade_items = _grades.get(_pid_c, [])
                        if _grade_items:
                            _grade_str = " · ".join(
                                f"{_t}:{_q}" for _t, _q in _grade_items[:5]
                            )
                            if len(_grade_items) > 5:
                                _grade_str += f" +{len(_grade_items)-5}"
                        else:
                            _ea_c = int(_row.get("estoque_atual") or 0)
                            _grade_str = (f"{_ea_c} un."
                                         if _ea_c > 0 else "⚠️ Sem estoque")

                        # Preço e margem
                        _pv_c     = float(_row.get("preco_venda") or 0)
                        _pc_c     = float(_row.get("preco_custo") or 0)
                        _margem_c = (((_pv_c - _pc_c) / _pc_c) * 100) if _pc_c > 0 else 0
                        _margem_s = (f"+{_margem_c:.0f}%"
                                     if _is_admin and _pc_c > 0 else "")
                        _preco_s  = f"R$ {_pv_c:,.2f}" if _pv_c > 0 else "—"

                        # Estoque crítico
                        _ea_c2  = int(_row.get("estoque_atual") or 0)
                        _emin_c = _row.get("estoque_minimo")
                        _baixo  = pd.notna(_emin_c) and _ea_c2 < int(_emin_c or 0)

                        # Campos de texto
                        _cat_b  = str(_row.get("categoria") or "").strip()
                        _cor_b  = str(_row.get("cor") or "").strip()
                        _forn_b = str(_row.get("fornecedor_ref") or "—")
                        _nome_b = str(_row.get("nome") or "Produto")

                        _bh = ""
                        if _cat_b:
                            _bh += f'<span class="gm-badge-cat">{_cat_b}</span>'
                        if _cor_b:
                            _bh += f'<span class="gm-badge-cor">{_cor_b}</span>'
                        if _baixo:
                            _bh += '<span class="gm-badge-low">⚠️ Est. baixo</span>'

                        _furi = _foto_thumb(_row.get("foto_url"))
                        _margem_html = (
                            f'<span class="gm-margem">{_margem_s}</span>'
                            if _margem_s else ""
                        )

                        st.markdown(
                            f'<div class="gm-card">'
                            f'<img src="{_furi}" title="{_nome_b}">'
                            f'<div class="gm-card-body">'
                            f'<div class="gm-badges">{_bh}</div>'
                            f'<div class="gm-nome" title="{_nome_b}">{_nome_b}</div>'
                            f'<div class="gm-forn">{_forn_b}</div>'
                            f'<div class="gm-pricerow">'
                            f'<span class="gm-price">{_preco_s}</span>'
                            f'{_margem_html}'
                            f'</div>'
                            f'<div class="gm-grade">{_grade_str}</div>'
                            f'</div></div>',
                            unsafe_allow_html=True,
                        )

                        # Botões de ação
                        if _is_admin:
                            if _IS_MASTER:
                                _ba1, _ba2, _ba3 = st.columns(3)
                            else:
                                _ba1, _ba2 = st.columns(2)
                                _ba3 = None
                            if _ba1.button("✏️ Editar", key=f"ed_{_pid_key}",
                                           use_container_width=True):
                                st.session_state.est_edit_pid  = _pid_c
                                st.session_state.est_grade_pid = None
                                st.rerun()
                            if _ba2.button("📏 Grade", key=f"gr_{_pid_key}",
                                           use_container_width=True):
                                st.session_state.est_grade_pid = _pid_c
                                st.session_state.est_edit_pid  = None
                                st.rerun()
                            if _ba3 is not None and _ba3.button(
                                "🗑️", key=f"del_{_pid_key}", use_container_width=True
                            ):
                                st.session_state.est_del_pid = _pid_c
                                st.rerun()
                        else:
                            if st.button("🔍 Detalhes", key=f"det_{_pid_key}",
                                         use_container_width=True):
                                st.session_state.est_dlg_row  = _ci + _cj
                                st.session_state.est_edit_pid = None
                                st.rerun()

            # ── Dialog de detalhes (não-admin) ────────────────────────────────────
            if st.session_state.est_dlg_row is not None:
                _dlg_idx = st.session_state.est_dlg_row
                if _dlg_idx < len(df_filtrado):
                    _dlg_produto(
                        df_filtrado.reset_index(drop=True).iloc[_dlg_idx], _is_admin
                    )
                else:
                    st.session_state.est_dlg_row = None


    if _is_admin:
        with _tab_cad_r:
            st.markdown("#### ⚡ Cadastro Rápido de Produto (NLP)")
            st.caption(
                "Digite em linguagem natural.  \n"
                "`10 blusas seda 20 custo 50 venda`  \n"
                "`5 calças jeans 35 custo 80 venda`  \n"
                "Se o produto já existir (busca por nome exato), atualiza estoque e preços."
            )
            _nlp_msg = st.session_state.pop("_nlp_success", None)
            if _nlp_msg:
                st.success(_nlp_msg)
            with st.form("est_nlp_form", clear_on_submit=False):
                _er_txt2 = st.text_input("Entrada Rápida", key="est_entrada_rapida",
                                          placeholder="10 blusas seda 20 custo 50 venda")
                _nlp_submitted = st.form_submit_button("⚡ Processar", use_container_width=True)
            if _nlp_submitted and _er_txt2.strip():
                _parsed2 = _parse_entrada_rapida(_er_txt2.strip())
                if _parsed2 is None:
                    st.error("Não consegui interpretar. Use: QUANTIDADE NOME CUSTO custo VENDA venda")
                else:
                    st.info(
                        f"Interpretado: **{_parsed2['qtd']}×** **{_parsed2['nome']}** — "
                        f"custo R$ {_parsed2['custo']:,.2f} / venda R$ {_parsed2['venda']:,.2f}"
                    )
                    _nome2 = _parsed2["nome"]
                    df_chk2 = run_query(
                        f"SELECT id::text, estoque_atual FROM produtos "
                        f"WHERE LOWER(nome) = LOWER('{_nome2.replace(chr(39), chr(39)*2)}') LIMIT 1"
                    )
                    _cat2 = _categorizar_produto(_nome2)
                    if not df_chk2.empty:
                        _pid2  = df_chk2["id"].iloc[0]
                        _ea2   = int(df_chk2["estoque_atual"].iloc[0] or 0)
                        _ne2   = _ea2 + _parsed2["qtd"]
                        ok2 = run_command(
                            "UPDATE produtos SET estoque_atual=%s, preco_custo=%s, "
                            "preco_venda=%s, categoria=COALESCE(categoria,%s) WHERE id=%s",
                            (_ne2, _parsed2["custo"], _parsed2["venda"], _cat2, _pid2),
                        )
                        if ok2:
                            st.success(f"✅ **{_nome2}** atualizado! Estoque: {_ea2} → **{_ne2}** un.")
                            st.rerun()
                    else:
                        try:
                            with _db_get_conn() as _conn_nlp:
                                with _conn_nlp.cursor() as _cur_nlp:
                                    _cur_nlp.execute(
                                        "INSERT INTO produtos (nome, estoque_atual, preco_custo, preco_venda, categoria) "
                                        "VALUES (%s, %s, %s, %s, %s) RETURNING id::text",
                                        (_nome2, _parsed2["qtd"], _parsed2["custo"], _parsed2["venda"], _cat2),
                                    )
                                    _row_nlp = _cur_nlp.fetchone()
                            if _row_nlp:
                                _nid2 = str(_row_nlp[0])[:8].upper()
                                st.session_state["_nlp_success"] = f"✅ **{_nome2}** cadastrado! Código: `{_nid2}`"
                                st.rerun()
                        except Exception as _e_nlp:
                            st.error("Erro ao cadastrar produto. Tente novamente.")
            st.markdown("---")
            st.markdown("##### Ou preencha o formulário:")
            with st.form("est_form_rapido"):
                _fn1, _fn2 = st.columns(2)
                _pnome  = _fn1.text_input("Nome do produto *", placeholder="Blusa floral M")
                _pcat   = _fn2.selectbox("Categoria", ["Blusas","Calças","Vestidos","Saias","Acessórios","Outros"])
                _fp1, _fp2, _fp3 = st.columns(3)
                _pqtd   = _fp1.number_input("Qtd em estoque", min_value=0, value=1)
                _pcusto = _fp2.number_input("Custo (R$)", min_value=0.0, value=0.0, format="%.2f")
                _pvenda = _fp3.number_input("Venda (R$)", min_value=0.0, value=0.0, format="%.2f")
                import datetime as _dtt_e
                _pdata  = st.date_input("📅 Data de lançamento", value=_dtt_e.date.today(), format="DD/MM/YYYY")
                _pobs   = st.text_input("Observação", placeholder="Ex: coleção verão, fornecedor X...", max_chars=200)
                if st.form_submit_button("💾 Salvar Produto", use_container_width=True):
                    if not _pnome.strip():
                        st.error("Nome obrigatório.")
                    elif _pvenda <= 0:
                        st.error("Preço de venda deve ser maior que zero.")
                    else:
                        ok_r = run_command(
                            "INSERT INTO produtos (nome, categoria, estoque_atual, preco_custo, preco_venda, data_lancamento, observacao) "
                            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (_pnome.strip(), _pcat, int(_pqtd), _pcusto, _pvenda, str(_pdata), _pobs.strip() or None),
                        )
                        if ok_r:
                            st.success(f"✅ **{_pnome.strip()}** cadastrado!")
                            st.rerun()

    if _is_admin:
        with _tab_cad_c:
            st.markdown("#### 🎨 Cadastro Completo com Grades de Tamanho")
            run_command("""
                CREATE TABLE IF NOT EXISTS produto_variacoes (
                    id         BIGSERIAL    PRIMARY KEY,
                    produto_id INTEGER      NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
                    tamanho    TEXT         NOT NULL,
                    estoque    INTEGER      NOT NULL DEFAULT 0,
                    created_at TIMESTAMPTZ  DEFAULT NOW(),
                    UNIQUE (produto_id, tamanho)
                )
            """)
            # ── Fornecedor FORA do form (botão não pode estar dentro) ──
            _df_forn_opts = run_query("SELECT id, nome FROM fornecedores WHERE tipo='Fornecedor' AND ativo=true ORDER BY nome")
            _forn_opcoes = ["— Nenhum —"] + _df_forn_opts["nome"].tolist() if not _df_forn_opts.empty else ["— Nenhum —"]
            _ffc1, _ffc2 = st.columns([5,1])
            with _ffc1:
                _cforn_sel = st.selectbox("🏭 Fornecedor", _forn_opcoes, key="est_forn_sel_completo", label_visibility="visible")
                _cforn = _cforn_sel if _cforn_sel != "— Nenhum —" else ""
            with _ffc2:
                st.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
                if st.button("➕ Novo", key="btn_forn_novo_est", use_container_width=True):
                    _dialog_novo_fornecedor_rapido()
                st.markdown("</div>", unsafe_allow_html=True)

            with st.form("est_form_completo"):
                _cc1, _cc2 = st.columns(2)
                _cnome   = _cc1.text_input("Nome do produto *", placeholder="Ex: Moleton Brooksfield")
                _ccat    = _cc2.selectbox("Categoria", ["Camisas","Camisetas","Calças","Moletons","Bermudas","Jaquetas","Acessórios","Calçados","Outros"])
                _cd1, _cd2, _cd3 = st.columns(3)
                _ccusto  = _cd1.number_input("Custo (R$)", min_value=0.0, value=None, format="%.2f", placeholder="0,00")
                _cvenda  = _cd2.number_input("Venda (R$)", min_value=0.0, value=None, format="%.2f", placeholder="0,00")
                _cmin    = _cd3.number_input("Estoque mínimo", min_value=0, value=1)
                _cores_lista = ["— Sem cor —","Preto","Branco","Cinza","Cinza Mescla","Marrom","Marrom Claro","Bege","Azul Marinho","Azul Claro","Vinho","Verde","Verde Militar","Caramelo","Laranja","Vermelho","Roxo","Rosa","Amarelo","Estampado","Multicolor"]
                _ccor = st.selectbox("🎨 Cor", _cores_lista, key="est_cor_completo")
                _ccor = _ccor if _ccor != "— Sem cor —" else ""
                _cdata   = st.date_input("📅 Data de lançamento", value=__import__("datetime").date.today(), format="DD/MM/YYYY", key="est_data_completo")
                _cobs    = st.text_input("Observação", placeholder="Ex: coleção inverno...", max_chars=200, key="est_obs_completo")
                _cdesc   = st.text_area("Descrição", placeholder="Detalhes do produto...")
                _cfoto   = st.file_uploader("📷 Foto do produto", type=["jpg","jpeg","png","webp"], key="est_foto_completo")
                if _cfoto:
                    st.image(_cfoto, width=120, caption="Preview")
                st.markdown("##### Grade de Tamanhos")
                st.caption("Informe o estoque para cada tamanho que deseja cadastrar. Deixe 0 para não cadastrar.")
                _tam_cols = st.columns(8)
                _tamanhos = ["PP","P","M","G","GG","XGG","34","36","38","40","42","44","46","48","U"]
                _tam_qtds: dict = {}
                for _ti, _tam in enumerate(_tamanhos):
                    with _tam_cols[_ti % 8]:
                        _tam_qtds[_tam] = st.number_input(
                            _tam, min_value=0, value=0, step=1, key=f"ccg_{_tam}"
                        )
                _total_grade = sum(_tam_qtds.values())
                if _total_grade > 0:
                    st.info(f"Total em estoque pela grade: **{_total_grade}** unidades")
                _csub = st.form_submit_button("💾 Salvar Produto com Grade", use_container_width=True)
                if _csub:
                    if not _cnome.strip():
                        st.error("Nome obrigatório.")
                    elif _cvenda <= 0:
                        st.error("Preço de venda deve ser maior que zero.")
                    else:
                        _est_total = max(_total_grade, 0)
                        try:
                            with _db_get_conn() as _conn_c:
                                with _conn_c.cursor() as _cur_c:
                                    _cur_c.execute(
                                        "INSERT INTO produtos (nome,categoria,fornecedor_ref,"
                                        "descricao_detalhada,estoque_atual,estoque_minimo,preco_custo,preco_venda,"
                                        "data_lancamento,observacao,cor) "
                                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                                        (_cnome.strip(), _ccat, _cforn.strip() or None,
                                         _cdesc.strip() or None, _est_total, int(_cmin),
                                         _ccusto, _cvenda, str(_cdata), _cobs.strip() or None,
                                         _ccor or None)
                                    )
                                    _novo_prod_id = _cur_c.fetchone()
                                    if _novo_prod_id:
                                        _novo_prod_id = _novo_prod_id[0]
                                        for _tam, _qtd in _tam_qtds.items():
                                            if _qtd > 0:
                                                _cur_c.execute(
                                                    "INSERT INTO produto_variacoes (produto_id, tamanho, estoque) "
                                                    "VALUES (%s, %s, %s) ON CONFLICT (produto_id, tamanho) "
                                                    "DO UPDATE SET estoque = EXCLUDED.estoque",
                                                    (int(_novo_prod_id), _tam, _qtd),
                                                )
                                        if _cfoto is not None:
                                            import io as _io_ins
                                            from PIL import Image as _PilIns
                                            os.makedirs(_FOTO_DIR_PROD, exist_ok=True)
                                            _img_ins = _PilIns.open(_cfoto)
                                            _img_ins.thumbnail((800, 800), _PilIns.LANCZOS)
                                            _fname_ins = f"{_novo_prod_id}.jpg"
                                            _img_ins.convert("RGB").save(
                                                os.path.join(_FOTO_DIR_PROD, _fname_ins), "JPEG", quality=85
                                            )
                                            _cur_c.execute(
                                                "UPDATE produtos SET foto_url=%s WHERE id=%s",
                                                (_fname_ins, int(_novo_prod_id)),
                                            )
                            # Limpar campos após salvar
                            for _k in list(st.session_state.keys()):
                                if any(x in _k for x in ["est_nome","est_cat","est_forn","est_cor","est_data","est_obs","est_desc","ccg_"]):
                                    del st.session_state[_k]
                            _tam_resumo = ", ".join(
                                f"{t}:{q}" for t, q in _tam_qtds.items() if q > 0
                            )
                            st.success(
                                f"✅ **{_cnome.strip()}** cadastrado com grade!  \n"
                                f"Estoque total: {_est_total} un.  \n"
                                f"Tamanhos: {_tam_resumo or 'nenhum'}"
                            )
                            st.rerun()
                        except Exception as _e_prod:
                            st.error(f"Erro ao salvar produto: {_e_prod}")
            st.markdown("---")
            st.markdown("##### 📊 Grade de Produto Existente")
            st.caption("Selecione um produto para visualizar ou editar sua grade de tamanhos.")
            _df_prod_grade = run_query(
                "SELECT id::text, nome FROM produtos WHERE ativo IS NOT FALSE ORDER BY nome LIMIT 300"
            )
            if not _df_prod_grade.empty:
                _gp_idx = st.selectbox(
                    "Produto", range(len(_df_prod_grade)),
                    format_func=lambda i: _df_prod_grade["nome"].iloc[i],
                    key="est_grade_prod_sel",
                )
                _gp_id = _df_prod_grade["id"].iloc[_gp_idx]
                _df_grade = run_query(
                    f"SELECT tamanho, estoque FROM produto_variacoes "
                    f"WHERE produto_id = {_gp_id} ORDER BY tamanho"
                )
                if _df_grade.empty:
                    st.info("Este produto não possui grade de tamanhos cadastrada.")
                else:
                    st.markdown("**Grade atual:**")
                    _g_cols = st.columns(min(len(_df_grade), 8))
                    for _gi, (_, _gr) in enumerate(_df_grade.iterrows()):
                        with _g_cols[_gi % 8]:
                            st.metric(_gr["tamanho"], _gr["estoque"])
                st.markdown("##### Atualizar Estoque por Tamanho")
                with st.form("est_grade_update"):
                    _tamanhos_u = ["PP","P","M","G","GG","XGG","34","36","38","40","42","44","46","48","U"]
                    _gu_cols = st.columns(8)
                    _gu_qtds: dict = {}
                    _pv_map = {r["tamanho"]: r["estoque"] for _, r in _df_grade.iterrows()} if not _df_grade.empty else {}
                    for _gi2, _tam2 in enumerate(_tamanhos_u):
                        with _gu_cols[_gi2 % 8]:
                            _gu_qtds[_tam2] = st.number_input(
                                _tam2, min_value=0, value=int(_pv_map.get(_tam2, 0)),
                                step=1, key=f"gupd_{_tam2}"
                            )
                    if st.form_submit_button("💾 Salvar Grade", use_container_width=True):
                        import psycopg2 as _pg2u
                        _conn_u = _pg2u.connect(**DB_CONFIG)
                        _cur_u  = _conn_u.cursor()
                        for _tam_u, _qtd_u in _gu_qtds.items():
                            _cur_u.execute(
                                "INSERT INTO produto_variacoes (produto_id, tamanho, estoque) "
                                "VALUES (%s, %s, %s) ON CONFLICT (produto_id, tamanho) "
                                "DO UPDATE SET estoque = EXCLUDED.estoque",
                                (_gp_id, _tam_u, _qtd_u),
                            )
                        _est_sum = sum(_gu_qtds.values())
                        _cur_u.execute(
                            "UPDATE produtos SET estoque_atual=%s WHERE id=%s",
                            (_est_sum, _gp_id),
                        )
                        _conn_u.commit()
                        _conn_u.close()
                        st.success(f"Grade salva! Estoque total atualizado para {_est_sum} un.")
                        st.rerun()


elif pagina == "💳 Pagamentos":
    st.subheader("💳 Pagamentos")

    if not _IS_ADMIN:
        st.error("🔒 Área restrita — somente administradores.")
        st.stop()

    # ── KPIs Pagamentos ───────────────────────────────────────────────────────
    _pk1, _pk2, _pk3 = st.columns(3)
    with _pk1:
        _dp = run_query("""
            SELECT COALESCE(SUM(valor),0) AS v FROM contas_a_pagar
            WHERE status != 'pago' AND data_vencimento < CURRENT_DATE
        """)
        _pkv1 = float(_dp["v"].iloc[0]) if not _dp.empty else 0.0
        st.markdown(
            f"<div style='background:#3a1a1a;border-left:4px solid #e74c3c;"
            f"padding:14px 16px;border-radius:8px;margin-bottom:4px'>"
            f"<div style='color:#e74c3c;font-size:.72rem;font-weight:700;"
            f"text-transform:uppercase;letter-spacing:.06em'>🔴 Vencido</div>"
            f"<div style='color:#fff;font-size:1.45rem;font-weight:700;margin-top:4px'>"
            f"R$ {_pkv1:,.2f}</div></div>",
            unsafe_allow_html=True,
        )
    with _pk2:
        _dp = run_query("""
            SELECT COALESCE(SUM(valor),0) AS v FROM contas_a_pagar
            WHERE status != 'pago' AND data_vencimento >= CURRENT_DATE
              AND data_vencimento < CURRENT_DATE + INTERVAL '30 days'
        """)
        _pkv2 = float(_dp["v"].iloc[0]) if not _dp.empty else 0.0
        st.markdown(
            f"<div style='background:#2a2a1a;border-left:4px solid #f39c12;"
            f"padding:14px 16px;border-radius:8px;margin-bottom:4px'>"
            f"<div style='color:#f39c12;font-size:.72rem;font-weight:700;"
            f"text-transform:uppercase;letter-spacing:.06em'>⏳ Próximos 30 dias</div>"
            f"<div style='color:#fff;font-size:1.45rem;font-weight:700;margin-top:4px'>"
            f"R$ {_pkv2:,.2f}</div></div>",
            unsafe_allow_html=True,
        )
    with _pk3:
        _dp = run_query("""
            SELECT COALESCE(SUM(valor),0) AS v FROM contas_a_pagar
            WHERE status = 'pago'
              AND updated_at::date >= DATE_TRUNC('month', CURRENT_DATE)
        """)
        _pkv3 = float(_dp["v"].iloc[0]) if not _dp.empty else 0.0
        st.markdown(
            f"<div style='background:#1a3a1a;border-left:4px solid #27ae60;"
            f"padding:14px 16px;border-radius:8px;margin-bottom:4px'>"
            f"<div style='color:#27ae60;font-size:.72rem;font-weight:700;"
            f"text-transform:uppercase;letter-spacing:.06em'>✅ Pago (mês)</div>"
            f"<div style='color:#fff;font-size:1.45rem;font-weight:700;margin-top:4px'>"
            f"R$ {_pkv3:,.2f}</div></div>",
            unsafe_allow_html=True,
        )
    st.markdown("---")

    _aba_pg, _aba_forn = st.tabs(["💰 Contas a Pagar", "🏭 Fornecedores"])

    with _aba_pg:
        _busca_pagar = st.text_input(
            "🔍 Buscar (descrição / categoria)", key="fin_pagar_busca",
            placeholder="Ex: aluguel, fornecedor..."
        )
        df_pag = run_query("""
            SELECT descricao, categoria, valor, data_vencimento,
                   status, comprovante_url, created_at::date AS criado_em
            FROM contas_a_pagar
            ORDER BY data_vencimento ASC
            LIMIT 500
        """)
        if not df_pag.empty:
            if _busca_pagar.strip():
                _q = _busca_pagar.strip().lower()
                mask = (
                    df_pag["descricao"].str.lower().str.contains(_q, na=False) |
                    df_pag["categoria"].str.lower().str.contains(_q, na=False)
                )
                df_pag = df_pag[mask]
            _pg_hoje = date.today()
            def _pg_cor(row):
                if str(row.get("status","")) == "pago":
                    return ["color: #27ae60"] * len(row)
                try:
                    dv = pd.to_datetime(row["data_vencimento"]).date()
                    if dv < _pg_hoje:
                        return ["color: #e74c3c; font-weight: bold"] * len(row)
                    if dv == _pg_hoje:
                        return ["color: #f39c12; font-weight: bold"] * len(row)
                except Exception:
                    pass
                return [""] * len(row)
            st.caption(f"{len(df_pag)} registro(s)")
            st.dataframe(df_pag.style.apply(_pg_cor, axis=1),
                         use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma conta a pagar registrada.")

    with _aba_forn:
        st.markdown("#### 🏭 Fornecedores / Prestadores / Utilidades")
        _busca_forn = st.text_input("🔍 Buscar fornecedor", key="fin_forn_busca", placeholder="Nome, tipo...")
        _tipo_filtro = st.selectbox("Filtrar por tipo", ["Todos", "Fornecedor", "Prestador de Serviço", "Utilidade/Conta Fixa"], key="fin_forn_tipo")
        df_forn_pg = run_query("SELECT id, nome, tipo, whatsapp1, instagram1, ativo FROM fornecedores ORDER BY nome")
        if not df_forn_pg.empty:
            if _busca_forn.strip():
                _qf = _busca_forn.strip().lower()
                df_forn_pg = df_forn_pg[df_forn_pg["nome"].str.lower().str.contains(_qf, na=False)]
            if _tipo_filtro != "Todos":
                df_forn_pg = df_forn_pg[df_forn_pg["tipo"] == _tipo_filtro]
            for _, frow in df_forn_pg.iterrows():
                _icone = "🏭" if frow["tipo"] == "Fornecedor" else ("🔧" if frow["tipo"] == "Prestador de Serviço" else "💡")
                with st.expander(f"{_icone} {frow['nome']} — {frow['tipo'] or '—'}"):
                    fc1, fc2 = st.columns(2)
                    fc1.write(f"📱 WhatsApp: {frow['whatsapp1'] or '—'}")
                    fc2.write(f"📸 Instagram: {frow['instagram1'] or '—'}")
                    fc1b, fc2b = st.columns(2)
                    if fc1b.button("✏️ Editar", key=f"fin_forn_ed_{frow['id']}", use_container_width=True):
                        st.session_state[f"edit_forn_{frow['id']}"] = True
                    if fc2b.button("Inativar" if frow["ativo"] else "Ativar", key=f"fin_forn_tog_{frow['id']}", use_container_width=True):
                        run_command("UPDATE fornecedores SET ativo = NOT ativo WHERE id = %s", (int(frow["id"]),))
                        st.rerun()
        else:
            st.info("Nenhum fornecedor cadastrado ainda.")

elif pagina == "💳 Recebimentos":
    render_clientes_unificado(perfil=_role)



elif pagina == "📋 Condicional":
    import datetime as _dt_cond
    st.markdown("## 📋 Condicional")
    st.caption("Peças saem para o cliente experimentar — cupom com prazo de devolução")

    # Session state
    if "cond_carrinho" not in st.session_state:
        st.session_state["cond_carrinho"] = []
    if "cond_cli_id" not in st.session_state:
        st.session_state["cond_cli_id"] = None

    _tab1, _tab2 = st.tabs(["➕ Novo Condicional", "📋 Condicionais Abertos"])

    with _tab1:
        # ── CLIENTE com autocomplete ──────────────────────────────────
        st.markdown("### Cliente")
        _df_cli_c = run_query("""
            SELECT id::text, nome, COALESCE(whatsapp,'') as whatsapp
            FROM clientes WHERE ativo IS NOT FALSE ORDER BY nome
        """)
        _cli_c_opts = ["— Selecione ou digite —"]
        _cli_c_map_nome = {}
        _cli_c_map_tel  = {}
        _cli_c_map_id   = {}
        if not _df_cli_c.empty:
            for _, _r in _df_cli_c.iterrows():
                _lbl = f"{_r['nome']}" + (f" | {_r['whatsapp']}" if _r['whatsapp'] else "")
                _cli_c_opts.append(_lbl)
                _cli_c_map_nome[_lbl] = _r['nome']
                _cli_c_map_tel[_lbl]  = _r['whatsapp']
                _cli_c_map_id[_lbl]   = _r['id']

        _cc1, _cc2, _cc3 = st.columns([5, 3, 1])
        _cond_cli_sel = _cc1.selectbox("Nome do cliente *", _cli_c_opts, key="cond_cli_sel")
        if _cond_cli_sel != "— Selecione ou digite —":
            _cond_cli = _cli_c_map_nome.get(_cond_cli_sel, "")
            _cond_tel_default = _cli_c_map_tel.get(_cond_cli_sel, "")
            st.session_state["cond_cli_id"] = _cli_c_map_id.get(_cond_cli_sel)
        else:
            _cond_cli = ""
            _cond_tel_default = ""
            st.session_state["cond_cli_id"] = None
        _cond_tel = _cc2.text_input("Telefone", value=_cond_tel_default, key="cond_cli_tel", placeholder="(37)99999-9999")
        _cc3.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
        if _cc3.button("➕", key="cond_btn_novo_cli", help="Cadastrar Novo Cliente", use_container_width=True):
            st.session_state["cond_novo_cli_open"] = not st.session_state.get("cond_novo_cli_open", False)
        _cc3.markdown("</div>", unsafe_allow_html=True)

        # Cadastro rápido inline
        if st.session_state.get("cond_novo_cli_open", False):
            with st.container():
                st.markdown("#### ➕ Cadastro Rápido de Cliente")
                _nc1, _nc2, _nc3 = st.columns(3)
                _cnc_nome = _nc1.text_input("Nome *", key="cond_nc_nome", placeholder="Nome completo")
                _cnc_tel  = _nc2.text_input("WhatsApp", key="cond_nc_tel", placeholder="(37)99999-9999")
                _cnc_cpf  = _nc3.text_input("CPF (opcional)", key="cond_nc_cpf", placeholder="000.000.000-00")
                if st.button("💾 Salvar Cliente", key="cond_nc_salvar", type="primary"):
                    if not _cnc_nome.strip():
                        st.warning("Informe o nome do cliente.")
                    else:
                        try:
                            import psycopg2 as _pg2_nc
                            _conn_nc = _pg2_nc.connect(host="localhost", port=5432, dbname="gmh_db", user="jgadmin", password="JGroot2026")
                            _cur_nc  = _conn_nc.cursor()
                            _wpp_nc  = re.sub(r"\D", "", _cnc_tel.strip()) if _cnc_tel.strip() else None
                            _cpf_nc  = re.sub(r"\D", "", _cnc_cpf.strip()) if _cnc_cpf.strip() else None
                            _cur_nc.execute(
                                "INSERT INTO clientes (nome, whatsapp, cpf, ativo) VALUES (%s,%s,%s,true) RETURNING id",
                                (_cnc_nome.strip(), _wpp_nc, _cpf_nc)
                            )
                            _conn_nc.commit()
                            _cur_nc.close(); _conn_nc.close()
                            st.success(f"✅ Cliente **{_cnc_nome.strip()}** cadastrado!")
                            st.session_state["cond_novo_cli_open"] = False
                            st.session_state["cond_cli_sel"] = _cnc_nome.strip()
                            st.rerun()
                        except Exception as _e_nc:
                            st.error(f"Erro ao cadastrar: {_e_nc}")

        # ── VENDEDORA / DATA DEVOLUÇÃO ────────────────────────────────
        _cv1, _cv2 = st.columns(2)
        _df_vnd_c = run_query(
            "SELECT codigo_vendedor, COALESCE(nome_vendedor, codigo_vendedor) AS label "
            "FROM config_comissao WHERE ativo=true ORDER BY nome_vendedor"
        )
        if not _df_vnd_c.empty:
            _vnd_c_opts   = _df_vnd_c["codigo_vendedor"].tolist()
            _vnd_c_labels = [str(r['label']) for _, r in _df_vnd_c.iterrows()]
            _vnd_c_idx = _cv1.selectbox(
                "🏷️ Vendedora",
                range(len(_vnd_c_opts)),
                format_func=lambda i: f"{_vnd_c_opts[i]} — {_vnd_c_labels[i]}",
                key="cond_vnd_idx",
                index=0,
            )
            _cond_vnd = _vnd_c_labels[_vnd_c_idx]
        else:
            _cond_vnd = _cv1.text_input("🏷️ Vendedora", key="cond_vnd")
        _cond_prazo = 24
        _cond_dt_dev = _cv2.date_input(
            "Data devolução",
            value=_dt_cond.date.today() + _dt_cond.timedelta(days=1),
            key="cond_dt_dev", format="DD/MM/YYYY"
        )
        _cond_obs = st.text_input("Observação", key="cond_obs", placeholder="Ex: cliente levou para festa, devolve amanhã...")

        st.markdown("---")
        st.markdown("### Produtos")

        # ── BUSCA PRODUTO ─────────────────────────────────────────────
        _df_prod_c = run_query("SELECT id::text, codigo_barras, nome, preco_venda, estoque_atual FROM produtos WHERE ativo IS NOT FALSE AND estoque_atual > 0 ORDER BY nome")
        if not _df_prod_c.empty:
            _prod_c_opts   = ["— Selecione —"] + [f"{r['nome']} [{r['codigo_barras']}] — R$ {float(r['preco_venda']):,.2f} ({int(r['estoque_atual'] or 0)} un)" for _, r in _df_prod_c.iterrows()]
            _prod_c_map_id    = {f"{r['nome']} [{r['codigo_barras']}] — R$ {float(r['preco_venda']):,.2f} ({int(r['estoque_atual'] or 0)} un)": str(r['id'])               for _, r in _df_prod_c.iterrows()}
            _prod_c_map_nome  = {f"{r['nome']} [{r['codigo_barras']}] — R$ {float(r['preco_venda']):,.2f} ({int(r['estoque_atual'] or 0)} un)": r['nome']                  for _, r in _df_prod_c.iterrows()}
            _prod_c_map_ref   = {f"{r['nome']} [{r['codigo_barras']}] — R$ {float(r['preco_venda']):,.2f} ({int(r['estoque_atual'] or 0)} un)": str(r['codigo_barras'] or '') for _, r in _df_prod_c.iterrows()}
            _prod_c_map_preco = {f"{r['nome']} [{r['codigo_barras']}] — R$ {float(r['preco_venda']):,.2f} ({int(r['estoque_atual'] or 0)} un)": float(r['preco_venda'] or 0) for _, r in _df_prod_c.iterrows()}

            _col_pc, _col_qc = st.columns([5, 1])
            _prod_c_sel = _col_pc.selectbox("Produto", _prod_c_opts, key="cond_prod_sel")
            _qtd_c = _col_qc.number_input("Qtd", min_value=1, value=1, key="cond_qtd")

            _tam_c = None
            if _prod_c_sel != "— Selecione —":
                _pid_c = _prod_c_map_id.get(_prod_c_sel, "")
                if _pid_c:
                    _df_gc = run_query(f"SELECT tamanho FROM produto_variacoes WHERE produto_id={_pid_c} AND estoque>0 ORDER BY tamanho")
                    if not _df_gc.empty:
                        _tam_c = st.selectbox("Tamanho", _df_gc["tamanho"].tolist(), key="cond_tam")

            if st.button("➕ Adicionar ao Condicional", key="cond_add_btn", use_container_width=True, type="primary"):
                if _prod_c_sel != "— Selecione —":
                    _nome_c  = _prod_c_map_nome.get(_prod_c_sel, _prod_c_sel)
                    _ref_c   = _prod_c_map_ref.get(_prod_c_sel, "")
                    _preco_c = _prod_c_map_preco.get(_prod_c_sel, 0.0)
                    _pid_c2  = _prod_c_map_id.get(_prod_c_sel, "")
                    _nome_exib_c = f"{_nome_c} [{_tam_c}]" if _tam_c else _nome_c
                    _existente_c = next((it for it in st.session_state["cond_carrinho"] if it["nome"] == _nome_exib_c), None)
                    if _existente_c:
                        _existente_c["qtd"] += int(_qtd_c)
                    else:
                        st.session_state["cond_carrinho"].append({
                            "produto_id": _pid_c2,
                            "nome": _nome_exib_c,
                            "referencia": _ref_c,
                            "tamanho": _tam_c or "",
                            "qtd": int(_qtd_c),
                            "preco_unit": _preco_c,
                        })
                    st.rerun()
                else:
                    st.warning("Selecione um produto.")

        # ── CARRINHO ──────────────────────────────────────────────────
        if st.session_state["cond_carrinho"]:
            st.markdown("---")
            st.markdown("**Itens do Condicional:**")
            _col_h1, _col_h2, _col_h3, _col_h4 = st.columns([5,1,1,1])
            _col_h1.write("**Produto**"); _col_h2.write("**Qtd**"); _col_h3.write("**R$**"); _col_h4.write("")
            for _ci, _cit in enumerate(st.session_state["cond_carrinho"]):
                _ca, _cb, _cc_col, _cd = st.columns([5,1,1,1])
                _ca.write(_cit["nome"])
                _cb.write(str(_cit["qtd"]))
                _cc_col.write(f"R$ {_cit['preco_unit']:,.2f}")
                if _cd.button("🗑", key=f"cond_del_{_ci}"):
                    st.session_state["cond_carrinho"].pop(_ci)
                    st.rerun()

            st.markdown("---")
            _c_btn1, _c_btn2 = st.columns(2)
            if _c_btn2.button("🗑 Limpar tudo", key="cond_limpar"):
                st.session_state["cond_carrinho"] = []
                st.rerun()

            if _c_btn1.button("🖨️ Gerar Cupom Condicional", key="cond_gerar", type="primary", use_container_width=True):
                if not _cond_cli.strip():
                    st.warning("Selecione o cliente.")
                else:
                    import streamlit.components.v1 as _comp_cond
                    from datetime import datetime as _dtnow_c
                    _dt_saida_str = _dtnow_c.now().strftime("%d/%m/%Y %H:%M")
                    _dt_dev_str   = _cond_dt_dev.strftime("%d/%m/%Y")
                    _num_cond = run_query("SELECT COALESCE(MAX(numero),0)+1 as n FROM condicionais")
                    _num = int(_num_cond.iloc[0]["n"]) if not _num_cond.empty else 1
                    run_command(
                        "INSERT INTO condicionais (numero,cliente_nome,cliente_telefone,vendedora,dt_saida,dt_devolucao,prazo_horas,observacao,status) VALUES (%s,%s,%s,%s,CURRENT_DATE,%s,%s,%s,'aberto')",
                        (_num, _cond_cli.strip(), _cond_tel.strip() or None, str(_cond_vnd) or None, str(_cond_dt_dev), int(_cond_prazo), _cond_obs.strip() or None)
                    )
                    _cond_id_r = run_query(f"SELECT id::text FROM condicionais WHERE numero={_num} ORDER BY created_at DESC LIMIT 1")
                    if not _cond_id_r.empty:
                        _cond_id = _cond_id_r.iloc[0]["id"]
                        for _cit in st.session_state["cond_carrinho"]:
                            run_command(
                                "INSERT INTO itens_condicional (condicional_id,produto_id,nome,referencia,tamanho,quantidade,preco_unit) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                                (_cond_id, _cit["produto_id"] or None, _cit["nome"], _cit["referencia"], _cit["tamanho"], _cit["qtd"], _cit["preco_unit"])
                            )
                    _rows_cond  = "".join([f"<tr><td style='padding:4px 8px;border-bottom:1px solid #e5e7eb'>{it['nome']}</td><td style='padding:4px 8px;border-bottom:1px solid #e5e7eb;text-align:center'>{it['qtd']}</td><td style='padding:4px 8px;border-bottom:1px solid #e5e7eb;text-align:right'>R$ {it['preco_unit']:,.2f}</td></tr>" for it in st.session_state["cond_carrinho"]])
                    _total_cond = sum(it["qtd"] * it["preco_unit"] for it in st.session_state["cond_carrinho"])
                    _obs_html   = f"<p style='font-size:11px;color:#6B7280'><b>Obs:</b> {_cond_obs}</p>" if _cond_obs else ""
                    _html_cond  = f"""<div id='condjg' style='font-family:Arial,sans-serif;max-width:500px;margin:0 auto;padding:20px;border:2px solid #374151;border-radius:8px'>
                        <div style='text-align:center;border-bottom:2px solid #374151;padding-bottom:10px;margin-bottom:12px'>
                            <div style='font-size:18px;font-weight:700'>LOJA GM HOMEM ITAUNA</div>
                            <div style='font-size:13px;color:#6B7280'>Moda Masculina - Itauna/MG</div>
                            <div style='font-size:12px;font-weight:700;color:#DC2626;margin-top:4px'>CONDICIONAL Nº {_num:04d}</div>
                        </div>
                        <table style='width:100%;font-size:12px;margin-bottom:8px'>
                            <tr><td><b>Cliente:</b> {_cond_cli}</td><td><b>Tel:</b> {_cond_tel}</td></tr>
                            <tr><td><b>Saída:</b> {_dt_saida_str}</td><td><b>Vendedora:</b> {_cond_vnd or '-'}</td></tr>
                            <tr><td colspan='2' style='color:#DC2626;font-weight:700'><b>⏰ Devolução até:</b> {_dt_dev_str} ({_cond_prazo}h)</td></tr>
                        </table>
                        {_obs_html}
                        <table style='width:100%;border-collapse:collapse;font-size:12px;margin:8px 0'>
                            <thead><tr style='background:#374151;color:white'>
                                <th style='padding:5px 8px;text-align:left'>Produto</th>
                                <th style='padding:5px 8px;text-align:center'>Qtd</th>
                                <th style='padding:5px 8px;text-align:right'>Valor Ref.</th>
                            </tr></thead><tbody>{_rows_cond}</tbody>
                        </table>
                        <div style='text-align:right;font-size:13px;font-weight:700;border-top:1px solid #374151;padding-top:6px'>Total Ref.: R$ {_total_cond:,.2f}</div>
                        <div style='margin-top:16px;border:1px solid #374151;padding:10px;font-size:11px'>
                            <b>TERMOS:</b> O(a) cliente acima identificado(a) declara ter recebido os itens listados em condicional e compromete-se a devolvê-los ou efetuar o pagamento até {_dt_dev_str}.
                        </div>
                        <div style='margin-top:24px;border-top:1px solid #374151;padding-top:6px;font-size:11px;text-align:center;max-width:220px;margin-left:auto;margin-right:auto'>
                            Assinatura do Cliente
                        </div>
                        <div style='text-align:center;font-size:10px;color:#9CA3AF;margin-top:12px;border-top:1px dashed #e5e7eb;padding-top:6px'>By JGAutomacoes.AI</div>
                    </div>"""
                    _comp_cond.html(
                        _html_cond + f"""<button onclick="(function(){{var c=document.getElementById('condjg').outerHTML;var w=window.open('','_blank','width=600,height=800');w.document.write('<html><head><title>Condicional</title><style>body{{padding:20px;font-family:Arial}}@media print{{button{{display:none}}}}</style></head><body>'+c+'<br><button onclick=window.print() style=width:100%;padding:10px;background:#111;color:#fff;border:none;cursor:pointer;border-radius:6px>Imprimir / Salvar PDF</button></body></html>');w.document.close();setTimeout(function(){{w.print()}},500)}})()" style='width:100%;padding:12px;background:#1D4ED8;color:white;border:none;border-radius:8px;cursor:pointer;margin-top:10px;font-size:14px'>🖨️ Imprimir Cupom Condicional</button>""",
                        height=700, scrolling=True
                    )
                    st.session_state["cond_carrinho"] = []

    with _tab2:
        st.markdown("### Condicionais em Aberto")
        _df_cond_ab = run_query("""
            SELECT c.numero as num, c.cliente_nome as cliente, c.cliente_telefone as tel,
                   TO_CHAR(c.dt_saida,'DD/MM/YYYY') as saida,
                   TO_CHAR(c.dt_devolucao,'DD/MM/YYYY') as devolucao,
                   c.prazo_horas as prazo,
                   CASE WHEN c.dt_devolucao < CURRENT_DATE THEN '⚠️ Atrasado' ELSE '✅ No prazo' END as status_prazo,
                   c.id::text as id
            FROM condicionais c WHERE c.status='aberto'
            ORDER BY c.dt_devolucao ASC
        """)
        if _df_cond_ab.empty:
            st.info("Nenhum condicional em aberto.")
        else:
            st.metric("Condicionais abertos", len(_df_cond_ab))
            for _, _crow in _df_cond_ab.iterrows():
                with st.expander(f"{_crow['status_prazo']} | Nº {int(_crow['num']):04d} — {_crow['cliente']} | Dev: {_crow['devolucao']}"):
                    # Busca itens
                    _itens_c = run_query(f"""
                        SELECT id::text as id, nome as produto, tamanho as tam,
                               quantidade as qtd, preco_unit as valor, devolvido
                        FROM itens_condicional
                        WHERE condicional_id='{_crow['id']}'::uuid
                        ORDER BY nome
                    """)
                    if not _itens_c.empty:
                        _itens_c.columns = [c.lower() for c in _itens_c.columns]

                        # ── BAIXA PARCIAL — checkbox por item ──────────
                        st.markdown("**Marque os itens que serão DEVOLVIDOS:**")
                        _dev_ids = []
                        _vnd_itens = []
                        for _, _ir in _itens_c.iterrows():
                            _ja_dev = bool(_ir.get("devolvido", False))
                            _lbl_item = f"{_ir['produto']} | Tam: {_ir['tam'] or '-'} | Qtd: {_ir['qtd']} | R$ {float(_ir['valor']):,.2f}"
                            _ck_col, _lbl_col = st.columns([1, 9])
                            if _ja_dev:
                                _lbl_col.markdown(f"~~{_lbl_item}~~ ✅ devolvido")
                            else:
                                _checked = _ck_col.checkbox("", key=f"dev_{_crow['id']}_{_ir['id']}", value=False)
                                _lbl_col.write(_lbl_item)
                                if _checked:
                                    _dev_ids.append(_ir["id"])
                                else:
                                    _vnd_itens.append(_ir)

                        st.markdown("---")
                        _pendentes = [r for _, r in _itens_c.iterrows() if not r.get("devolvido", False)]
                        _total_pend = sum(float(r["valor"]) * int(r["qtd"]) for r in _pendentes)
                        _total_dev_sel = sum(float(_itens_c[_itens_c["id"]==did]["valor"].values[0]) * int(_itens_c[_itens_c["id"]==did]["qtd"].values[0]) for did in _dev_ids) if _dev_ids else 0.0

                        st.caption(f"Total pendente: R$ {_total_pend:,.2f} | Selecionados p/ devolução: R$ {_total_dev_sel:,.2f}")

                        _cb1, _cb2, _cb3 = st.columns(3)

                        # Botão: marcar selecionados como devolvidos
                        if _cb1.button("↩️ Confirmar Devoluções", key=f"cond_dev_{_crow['id']}", use_container_width=True):
                            if not _dev_ids:
                                st.warning("Marque ao menos um item para devolver.")
                            else:
                                for _did in _dev_ids:
                                    run_command("UPDATE itens_condicional SET devolvido=true WHERE id=%s::uuid", (_did,))
                                # Se todos devolvidos, encerra condicional
                                _restantes = run_query(f"SELECT COUNT(*) as n FROM itens_condicional WHERE condicional_id='{_crow['id']}'::uuid AND devolvido=false")
                                if not _restantes.empty and int(_restantes.iloc[0]["n"]) == 0:
                                    run_command("UPDATE condicionais SET status='encerrado' WHERE id=%s::uuid", (_crow['id'],))
                                    st.success("✅ Todos os itens devolvidos! Condicional encerrado.")
                                else:
                                    st.success(f"✅ {len(_dev_ids)} item(ns) marcado(s) como devolvido(s).")
                                st.rerun()

                        # Botão: converter não-devolvidos em venda
                        if _cb2.button("💰 Virou Venda", key=f"cond_vnd_{_crow['id']}", use_container_width=True, type="primary"):
                            _nao_dev = [r for _, r in _itens_c.iterrows() if not bool(r.get("devolvido", False)) and r["id"] not in _dev_ids]
                            if not _nao_dev:
                                st.warning("Nenhum item pendente para converter.")
                            else:
                                # Carregar itens no carrinho do PDV
                                st.session_state["pdv_carrinho"] = []
                                for _ni in _nao_dev:
                                    _pu_ni = float(_ni["valor"])
                                    _qt_ni = int(_ni["qtd"])
                                    st.session_state["pdv_carrinho"].append({
                                        "produto_id": str(_ni.get("produto_id", "") or ""),
                                        "nome":        str(_ni["produto"]),
                                        "referencia":  "",
                                        "tamanho":     str(_ni["tam"] or ""),
                                        "qtd":         _qt_ni,
                                        "preco_unit":  _pu_ni,
                                        "unit":        _pu_ni,
                                        "subtotal":    round(_pu_ni * _qt_ni, 2),
                                    })
                                # Pre-selecionar cliente no PDV
                                _cli_pdv_preset = str(_crow["cliente"])
                                st.session_state["pdv_cli_selectbox"] = _cli_pdv_preset
                                # Obs com referência ao condicional
                                st.session_state["pdv_obs_preset"] = f"Condicional Nº {int(_crow['num']):04d}"
                                # Ir direto para checkout (pular etapa de adicionar itens)
                                st.session_state["pdv_checkout"] = False
                                run_command("UPDATE condicionais SET status='convertido' WHERE id=%s::uuid", (_crow['id'],))
                                st.session_state["_nav_target"] = "🛒 Vendas"
                                st.rerun()

                        # Botão: encerrar sem venda (tudo devolvido manualmente)
                        if _cb3.button("🗑 Encerrar", key=f"cond_enc_{_crow['id']}", use_container_width=True):
                            run_command("UPDATE condicionais SET status='encerrado' WHERE id=%s::uuid", (_crow['id'],))
                            st.success("Condicional encerrado.")
                            st.rerun()
                    else:
                        st.info("Sem itens registrados.")
                        if st.button("🗑 Encerrar", key=f"cond_enc_vazio_{_crow['id']}"):
                            run_command("UPDATE condicionais SET status='encerrado' WHERE id=%s::uuid", (_crow['id'],))
                            st.rerun()

elif pagina == "🔄 Trocas":
    st.subheader("🔄 Trocas & Devoluções")

    tab_nova_troca, tab_vales = st.tabs(["📦 Registrar Troca", "🎫 Vales em Aberto"])

    # ════════════════════════════════════════════════════════
    # TAB: Registrar Troca
    # ════════════════════════════════════════════════════════
    with tab_nova_troca:
        st.caption(
            "Selecione o cliente e a compra, escolha os itens a devolver, "
            "confirme para repor o estoque e gerar o Vale-Troca automaticamente."
        )

        df_cli_tr = run_query(
            "SELECT id::text, nome FROM clientes WHERE ativo = true ORDER BY nome"
        )
        if df_cli_tr.empty:
            st.info("Nenhum cliente cadastrado.")
            st.stop()

        _tr_cli_idx = st.selectbox(
            "👤 Cliente",
            range(len(df_cli_tr)),
            format_func=lambda i: df_cli_tr["nome"].iloc[i],
            key="tr_cliente_sel",
        )
        _tr_cli_id   = df_cli_tr["id"].iloc[_tr_cli_idx]
        _tr_cli_nome = df_cli_tr["nome"].iloc[_tr_cli_idx]

        df_vnd_tr = run_query(f"""
            SELECT v.id::text AS venda_id, v.data_venda::date AS data,
                   v.valor_total, v.forma_pagamento
            FROM vendas v
            WHERE v.cliente_id = '{_tr_cli_id}'
            ORDER BY v.data_venda DESC
            LIMIT 50
        """)

        if df_vnd_tr.empty:
            st.info("Este cliente não tem vendas registradas.")
        else:
            _tr_vnd_opts = [
                f"Compra de {row['data']} — R$ {float(row['valor_total']):,.2f} ({row['forma_pagamento']})"
                for _, row in df_vnd_tr.iterrows()
            ]
            _tr_vnd_idx = st.selectbox(
                "🛒 Venda de origem",
                range(len(_tr_vnd_opts)),
                format_func=lambda i: _tr_vnd_opts[i],
                key="tr_venda_sel",
            )
            _tr_venda_id = df_vnd_tr["venda_id"].iloc[_tr_vnd_idx]

            df_itens_tr = run_query(f"""
                SELECT iv.id::text AS item_id, p.id::text AS produto_id,
                       p.nome AS produto, iv.quantidade AS qtd_orig,
                       iv.preco_unit AS unit
                FROM itens_venda iv
                JOIN produtos p ON p.id = iv.produto_id
                WHERE iv.venda_id = '{_tr_venda_id}'
                ORDER BY p.nome
            """)

            if df_itens_tr.empty:
                st.info("Nenhum item registrado para esta venda.")
            else:
                st.markdown("**Informe a quantidade a devolver (0 = não devolve):**")

                _h1, _h2, _h3 = st.columns([3.5, 1.5, 1.5])
                _h1.markdown("**Produto**")
                _h2.markdown("**Preço Unit.**")
                _h3.markdown("**Qtd. Dev.**")
                st.markdown("<hr style='margin:4px 0 8px'>", unsafe_allow_html=True)

                itens_selecionados = []
                for _, it in df_itens_tr.iterrows():
                    _ic1, _ic2, _ic3 = st.columns([3.5, 1.5, 1.5])
                    _ic1.write(f"📦 {it['produto']}")
                    _ic2.write(f"R$ {float(it['unit']):,.2f}")
                    _qtd_dev = _ic3.number_input(
                        "",
                        min_value=0,
                        max_value=int(it["qtd_orig"]),
                        value=0,
                        step=1,
                        key=f"tr_qtd_{it['item_id']}",
                        label_visibility="collapsed",
                    )
                    if _qtd_dev > 0:
                        itens_selecionados.append({
                            "produto_id": it["produto_id"],
                            "produto":    it["produto"],
                            "qtd":        _qtd_dev,
                            "unit":       float(it["unit"]),
                            "subtotal":   round(_qtd_dev * float(it["unit"]), 2),
                        })

                if itens_selecionados:
                    _tr_valor_vale = sum(it["subtotal"] for it in itens_selecionados)
                    _tr_desc_itens = ", ".join(
                        f"{it['produto']} ×{it['qtd']}" for it in itens_selecionados
                    )
                    st.markdown("---")
                    st.markdown(
                        f"<div style='background:#e0f2f1;border-left:4px solid #26A69A;"
                        f"border-radius:8px;padding:12px 16px;margin:8px 0'>"
                        f"<b style='font-size:1.05rem'>Vale-Troca: R$ {_tr_valor_vale:,.2f}</b><br/>"
                        f"<span style='font-size:.85rem;color:#555'>{_tr_desc_itens}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                    _tr_motivo = st.text_input(
                        "Motivo da devolução (opcional)", key="tr_motivo",
                        placeholder="Ex: Tamanho incorreto, defeito..."
                    )
                    if st.button("✅ Confirmar Troca e Gerar Vale", key="tr_confirmar",
                                 type="primary", use_container_width=True):
                        _tr_erros = 0
                        for _it in itens_selecionados:
                            if not run_command(
                                "UPDATE produtos SET estoque_atual = estoque_atual + %s "
                                "WHERE id = %s",
                                (_it["qtd"], _it["produto_id"]),
                            ):
                                _tr_erros += 1

                        if _tr_erros == 0:
                            _ok_vale = run_command(
                                """INSERT INTO vales_troca
                                       (cliente_id, venda_id, valor, saldo, operador, motivo)
                                   VALUES (%s, %s, %s, %s, %s, %s)""",
                                (_tr_cli_id, _tr_venda_id, _tr_valor_vale, _tr_valor_vale,
                                 st.session_state.get("username", ""), _tr_motivo or None),
                            )
                            if _ok_vale:
                                st.success(
                                    f"✅ Troca registrada! **Vale-Troca de R$ {_tr_valor_vale:,.2f}** "
                                    f"gerado para **{_tr_cli_nome}**.  \n"
                                    f"Estoque reposto: {_tr_desc_itens}."
                                )
                                st.rerun()
                            else:
                                st.error(
                                    "Estoque reposto, mas erro ao gerar Vale-Troca. "
                                    "Contate o administrador."
                                )
                        else:
                            st.error("Erro ao repor estoque. Tente novamente.")
                else:
                    st.info("Informe a quantidade > 0 em ao menos um item para continuar.")

    # ════════════════════════════════════════════════════════
    # TAB: Vales em Aberto
    # ════════════════════════════════════════════════════════
    with tab_vales:
        st.caption("Vale-Trocas ativos com saldo disponível para uso no PDV.")

        # ── Estatísticas de Conversão ─────────────────────────────────────────
        df_conv = run_query("""
            SELECT
                COUNT(*)                                        AS total_gerados,
                COALESCE(SUM(valor), 0)                         AS valor_gerado,
                COUNT(*) FILTER (WHERE saldo = 0 OR ativo = false) AS total_usados,
                COALESCE(SUM(valor) FILTER (WHERE saldo = 0 OR ativo = false), 0)
                                                                AS valor_usado,
                COUNT(*) FILTER (WHERE ativo = true AND saldo > 0) AS em_aberto,
                COALESCE(SUM(saldo) FILTER (WHERE ativo = true AND saldo > 0), 0)
                                                                AS saldo_aberto
            FROM vales_troca
        """)
        if not df_conv.empty:
            _r = df_conv.iloc[0]
            _total_g = int(_r["total_gerados"])
            _total_u = int(_r["total_usados"])
            _taxa    = round(_total_u / _total_g * 100, 1) if _total_g > 0 else 0.0
            _cv1, _cv2, _cv3, _cv4 = st.columns(4)
            _cv1.metric("Vales Gerados",   _total_g,
                        f"R$ {float(_r['valor_gerado']):,.2f}")
            _cv2.metric("Vales Utilizados", _total_u,
                        f"R$ {float(_r['valor_usado']):,.2f}")
            _cv3.metric("Em Aberto",        int(_r["em_aberto"]),
                        f"R$ {float(_r['saldo_aberto']):,.2f} em saldo")
            _cv4.metric("Taxa de Conversão", f"{_taxa}%",
                        help="% de vales já utilizados pelos clientes")
            st.markdown(
                f"<div style='background:{'#e8f5e9' if _taxa >= 50 else '#fff8e1'};"
                f"border-left:4px solid {'#4caf50' if _taxa >= 50 else '#ff9800'};"
                f"border-radius:6px;padding:8px 14px;margin:8px 0 12px'>"
                f"{'✅' if _taxa >= 50 else '💡'} "
                f"{'Boa conversão! Mais da metade dos vales já voltou para a loja.' if _taxa >= 50 else 'Menos da metade dos vales foi utilizada. Considere lembrar os clientes via Mala Direta.'}"
                f"</div>",
                unsafe_allow_html=True,
            )
        st.markdown("---")

        df_vales = run_query("""
            SELECT vt.id,
                   c.id::text AS cliente_id,
                   c.nome     AS cliente,
                   COALESCE(c.whatsapp, '') AS fone,
                   vt.valor,
                   vt.saldo,
                   vt.operador,
                   vt.motivo,
                   vt.criado_em::date AS data
            FROM vales_troca vt
            JOIN clientes c ON c.id = vt.cliente_id
            WHERE vt.ativo = true AND vt.saldo > 0
            ORDER BY vt.criado_em DESC
        """)

        if df_vales.empty:
            st.info("Nenhum Vale-Troca ativo com saldo no momento.")
        else:
            st.metric("Vales em Aberto", len(df_vales),
                      help="Total de clientes com saldo de troca disponível")

            # Cabeçalho
            _vh1, _vh2, _vh3, _vh4, _vh5 = st.columns([2.5, 1.3, 1.3, 2.5, 1.2])
            _vh1.markdown("**Cliente**"); _vh2.markdown("**Valor**")
            _vh3.markdown("**Saldo**");   _vh4.markdown("**Motivo**"); _vh5.markdown("")
            st.markdown("<hr style='margin:4px 0 8px'>", unsafe_allow_html=True)

            for _, _vr in df_vales.iterrows():
                _vc1, _vc2, _vc3, _vc4, _vc5 = st.columns([2.5, 1.3, 1.3, 2.5, 1.2])
                _vc1.write(f"{_vr['cliente']}  \n`{_vr['data']}`")
                _vc2.write(f"R$ {float(_vr['valor']):,.2f}")
                _vc3.write(f"R$ {float(_vr['saldo']):,.2f}")
                _vc4.write(str(_vr["motivo"] or "—")[:40])
                if _vc5.button("📱", key=f"tr_wpp_{_vr['id']}",
                               help="Avisar cliente sobre o vale"):
                    _msg_vale = (
                        f"Olá {str(_vr['cliente']).split()[0]}! Você tem um "
                        f"Vale-Troca de R$ {float(_vr['saldo']):,.2f} disponível "
                        f"na GM Homem. Venha nos visitar! 💛"
                    )
                    _ok, _err = _disparar_whatsapp(
                        cliente_id=_vr["cliente_id"],
                        telefone=str(_vr["fone"]),
                        nome=str(_vr["cliente"]),
                        msg_corpo=_msg_vale,
                        vendedora=st.session_state.get("username", ""),
                    )
                    if _ok:
                        st.toast(f"🚀 Comando enviado ao n8n!", icon="✅")
                    else:
                        st.warning(f"Falha: {_err}")

elif pagina == "🛒 Vendas":
    _vtab_pdv, _vtab_dia, _vtab_hist = st.tabs(
        ["🛒 PDV — Nova Venda", "📊 Painel do Dia", "📋 Histórico de Vendas"]
    )

    with _vtab_pdv:
        st.subheader("🛒 Vendas — PDV Híbrido")

        # ── CSS local ─────────────────────────────────────────────────────────────
        st.markdown("""
    <style>
    /* Botão Adicionar ao Carrinho (form submit) — teal */
    [data-testid="stFormSubmitButton"] button {
        background: #5bc5d3 !important;
        border-color: #5bc5d3 !important;
        color: #fff !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        background: #3db5c4 !important;
        border-color: #3db5c4 !important;
    }
    /* Botão Finalizar Venda (override primary → teal) */
    button[data-testid="baseButton-primary"].pdv-finalizar {
        background: #5bc5d3 !important;
        border-color: #5bc5d3 !important;
    }
    </style>
    """, unsafe_allow_html=True)

        # ── Estado de sessão ──────────────────────────────────────────────────────
        for _k, _v in [
            ("va_messages",     []),
            ("va_pendente",     None),
            ("va_ultimo_cupom", None),
            ("pdv_carrinho",    []),
            ("pdv_checkout",    False),
            ("pdv_ultima_venda", None),   # info da última venda p/ botão WhatsApp
            ("pdv_obs_preset",  ""),
        ]:
            if _k not in st.session_state:
                st.session_state[_k] = _v

        # ── Cupom (largura total, acima do layout) ────────────────────────────────
        if st.session_state.va_ultimo_cupom:
            _c = st.session_state.va_ultimo_cupom
            with st.expander(f"🧾 Cupom #{_c['num']:06d} — clique para ver / imprimir",
                             expanded=True):
                st.markdown(_cupom_html_display(_c["text"]), unsafe_allow_html=True)
                _col_dl, _col_fch = st.columns([2, 1])
                with _col_dl:
                    components.html(
                        _cupom_iframe_html(_c["text"], "pf_va", "🖨️ Imprimir Cupom"),
                        height=52,
                    )
                if _col_fch.button("✕ Fechar cupom", key="va_fechar_cupom",
                                    use_container_width=True):
                    st.session_state.va_ultimo_cupom = None
                    st.rerun()

        # ── Painel WhatsApp — última venda confirmada ─────────────────────────────
        if st.session_state.pdv_ultima_venda:
            _uv = st.session_state.pdv_ultima_venda
            _wpp_raw  = re.sub(r"\D", "", _uv.get("wpp", "") or "")
            _wpp_br   = ("55" + _wpp_raw) if _wpp_raw and not _wpp_raw.startswith("55") else _wpp_raw
            _cupom_tx = _uv.get("cupom_text", "")

            # Mensagem pré-formatada para WhatsApp
            _msg_wpp = (
                f"Olá {_uv['cliente_nome']}! 😊\n\n"
                f"Segue o comprovante da sua compra na *GM Homem Itaúna*:\n\n"
                f"```\n{_cupom_tx}\n```\n\n"
                f"Obrigada pela preferência! 🛍️"
            )
            _wpp_url = (
                f"https://wa.me/{_wpp_br}?text={urllib.parse.quote(_msg_wpp)}"
                if _wpp_br else None
            )

            with st.container():
                st.markdown(
                    f"<div style='background:linear-gradient(135deg,#075e54 0%,#128c7e 100%);"
                    f"border-radius:12px;padding:14px 20px;margin-bottom:12px;"
                    f"display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px'>"
                    f"<div style='color:#fff'>"
                    f"<div style='font-size:.73rem;font-weight:800;letter-spacing:.1em;"
                    f"opacity:.8;margin-bottom:3px'>✅ VENDA #{_uv['num']:06d} REGISTRADA</div>"
                    f"<div style='font-size:1rem;font-weight:700'>"
                    f"{_uv['cliente_nome']} &nbsp;·&nbsp; "
                    f"<span style='color:#25d366'>R$ {_uv['valor']:,.2f}</span></div>"
                    f"<div style='font-size:.8rem;opacity:.75;margin-top:2px'>"
                    f"Ref: <code style='color:#fff'>{_uv['venda_id'][-8:].upper()}</code>"
                    f"{'&nbsp;·&nbsp;WhatsApp: ' + _uv['wpp'] if _uv.get('wpp') else '&nbsp;·&nbsp;sem WhatsApp cadastrado'}"
                    f"</div></div></div>",
                    unsafe_allow_html=True,
                )

                _wc1, _wc2, _wc3 = st.columns([2, 2, 1])

                # Botão wa.me (abre WhatsApp com cupom pré-preenchido)
                if _wpp_url:
                    with _wc1:
                        st.link_button(
                            "📲 Enviar Comprovante via WhatsApp",
                            _wpp_url,
                            use_container_width=True,
                        )
                        st.caption("⚠️ Abrirá uma nova aba — limitação do navegador.")
                else:
                    _wc1.warning("Sem WhatsApp cadastrado para este cliente.")

                # Botão webhook n8n (envia pelo número da loja, não do navegador)
                with _wc2:
                    if _uv.get("wpp") and st.button(
                        "🤖 Enviar via n8n (loja)",
                        key="pdv_wpp_n8n",
                        use_container_width=True,
                        help="Dispara o webhook n8n/loja-gmh-comprovante",
                    ):
                        _ok_wpp, _det_wpp = enviar_comprovante_wpp(
                            _uv["cliente_id"], _uv["wpp"],
                            _uv["venda_id"], _cupom_tx,
                        )
                        if _ok_wpp:
                            st.toast("✅ Comprovante enviado via n8n!", icon="✅")
                        else:
                            st.error(f"Falha: {_det_wpp}")

                with _wc3:
                    if st.button("✕ Fechar", key="pdv_wpp_fechar",
                                 use_container_width=True):
                        st.session_state.pdv_ultima_venda = None
                        st.rerun()

        col_pdv = st.container()  # PDV ocupa largura total — IA concentrada em ✨ GM Homem AI

        # ════════════════════════════════════════════════════════════════════════
        # COLUNA ESQUERDA — PDV GM Homem com Carrinho
        # ════════════════════════════════════════════════════════════════════════
        with col_pdv:
            st.markdown(
                "<div class='pdv-card'><h4>🖥️ PDV GM Homem</h4>",
                unsafe_allow_html=True,
            )

            # ── Dados do banco ────────────────────────────────────────────────
            df_cli_pdv = run_query(
                "SELECT id::text, nome FROM clientes WHERE ativo = true ORDER BY nome"
            )
            df_prod_pdv = run_query(
                "SELECT id::text, codigo_barras, nome, cor, preco_venda, estoque_atual "
                "FROM produtos WHERE ativo IS NOT FALSE AND estoque_atual > 0 ORDER BY nome"
            )
            _cli_nomes = df_cli_pdv["nome"].tolist() if not df_cli_pdv.empty else []

            # ── Modo confirmação via Chat IA ──────────────────────────────────
            _pendente = st.session_state.va_pendente
            if _pendente and _pendente.get("origem") == "chat":
                _d       = _pendente
                _df_vnd_opts = run_query(
                    "SELECT codigo_vendedor, COALESCE(nome_vendedor, codigo_vendedor) AS label "
                    "FROM config_comissao WHERE ativo = true ORDER BY codigo_vendedor"
                )
                if not _df_vnd_opts.empty:
                    _vnd_opts_chat = _df_vnd_opts["codigo_vendedor"].tolist()
                    _vnd_lbl_chat  = _df_vnd_opts["label"].tolist()
                    _vnd_idx_chat  = 0
                    if _d.get("codigo_vendedor") in _vnd_opts_chat:
                        _vnd_idx_chat = _vnd_opts_chat.index(_d["codigo_vendedor"])
                    _chat_cod_vnd = st.selectbox(
                        "🏷️ Vendedora *", range(len(_vnd_opts_chat)),
                        format_func=lambda i: f"{_vnd_opts_chat[i]} — {_vnd_lbl_chat[i]}",
                        index=_vnd_idx_chat, key="va_cod_vnd",
                    )
                    _d["codigo_vendedor"] = _vnd_opts_chat[_chat_cod_vnd]
                else:
                    _chat_cod_vnd = st.text_input(
                        "🏷️ Código Vendedor *", key="va_cod_vnd",
                        value=_d.get("codigo_vendedor", ""),
                        placeholder="Cadastre vendedoras em Administração.",
                    )
                    _d["codigo_vendedor"] = _chat_cod_vnd.strip()
                _desc_pct = st.number_input(
                    "Desconto (%)", min_value=0.0, max_value=100.0,
                    value=float(_d.get("desconto_pct", 0.0)),
                    step=1.0, format="%.1f", key="va_desconto_pct",
                )
                _d["desconto_pct"] = _desc_pct
                _v_orig    = _d["valor_total"]
                _desc_real = round(_v_orig * _desc_pct / 100, 2)
                _v_final   = round(_v_orig - _desc_real, 2)
                _parc_val  = _v_final / _d["parcelas"]
                _parc_lbl  = (
                    f"{_d['parcelas']}x de R$ {_parc_val:,.2f}"
                    if _d["parcelas"] > 1 else f"1x de R$ {_v_final:,.2f}"
                )
                _desc_span = (
                    f"&nbsp;<span style='color:#d97706'>(-{_desc_pct:.1f}% = "
                    f"-R$ {_desc_real:,.2f})</span>" if _desc_pct > 0 else ""
                )
                st.markdown(
                    f"<div style='background:#e8f8fa;border-left:4px solid #5bc5d3;"
                    f"border-radius:10px;padding:14px 18px;margin:8px 0 16px'>"
                    f"<div style='font-size:.73rem;color:#5bc5d3;font-weight:800;"
                    f"letter-spacing:.1em;margin-bottom:10px'>📋 PREENCHIDO PELO CHAT IA</div>"
                    f"<table style='width:100%;border-collapse:collapse;font-size:.93rem'>"
                    f"<tr><td style='padding:4px 12px 4px 0;color:#555'><b>👤 Cliente</b></td>"
                    f"<td>{_d['cliente_nome']}</td></tr>"
                    f"<tr><td style='padding:4px 12px 4px 0;color:#555'><b>📦 Itens</b></td>"
                    f"<td>{_d['descricao']}</td></tr>"
                    f"<tr><td style='padding:4px 12px 4px 0;color:#555'><b>💰 Valor</b></td>"
                    f"<td><b>R$ {_v_final:,.2f}</b>{_desc_span}</td></tr>"
                    f"<tr><td style='padding:4px 12px 4px 0;color:#555'><b>💳 Pagamento</b></td>"
                    f"<td>{_d['forma_pagamento']} — {_parc_lbl}</td></tr>"
                    f"</table></div>",
                    unsafe_allow_html=True,
                )
                _cc1, _cc2 = st.columns(2)
                with _cc1:
                    if st.button("✅ Confirmar Venda", key="pdv_confirmar",
                                 use_container_width=True, type="primary"):
                        if not _d.get("codigo_vendedor", "").strip():
                            st.error("Informe o **Código Vendedor** antes de confirmar.")
                        else:
                            try:
                                _d["valor_original"] = _v_orig
                                _d["valor_total"]    = _v_final
                                _d["vendedor_nome"]  = st.session_state.get("username", "")
                                _vid = salvar_venda(_d)
                                _dfn = run_query("SELECT COUNT(*) AS total FROM vendas")
                                _nc  = int(_dfn["total"].iloc[0]) if not _dfn.empty else 1
                                _cupom_txt = gerar_cupom(_d, _vid, _nc,
                                                          vendedor=_d["vendedor_nome"])
                                # Salva o cupom gerado na venda
                                with _db_get_conn() as conn:
                                    with conn.cursor() as cur:
                                        cur.execute(
                                            "UPDATE vendas SET cupom_text = %s WHERE id = %s",
                                            (_cupom_txt, _vid)
                                        )
                                        conn.commit()
                                st.session_state.va_ultimo_cupom = {
                                    "text":     _cupom_txt,
                                    "venda_id": _vid,
                                    "num":      _nc,
                                }
                                _parc_m = (
                                    f"{_d['parcelas']} parcela(s) em *Contas a Receber*."
                                    if _d["forma_pagamento"] in ("cartão", "crediário")
                                    else "Pagamento registrado como recebido."
                                )
                                st.session_state.va_messages.append({
                                    "role": "assistant",
                                    "content": (
                                        f"✅ Venda #{_nc:06d} salva!  \n"
                                        f"**Cliente:** {_d['cliente_nome']}  \n"
                                        f"**Valor:** R$ {_v_final:,.2f}  \n{_parc_m}"
                                    ),
                                })
                                st.session_state.va_pendente = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao salvar: {e}")
                with _cc2:
                    if st.button("❌ Cancelar", key="pdv_cancelar_chat",
                                 use_container_width=True):
                        st.session_state.va_messages.append({
                            "role": "assistant",
                            "content": "Venda cancelada. Digite uma nova quando quiser.",
                        })
                        st.session_state.va_pendente = None
                        st.rerun()

            else:
                # ════════════════════════════════════════════════════════════
                # PDV com Carrinho
                # ════════════════════════════════════════════════════════════

                # ── Seleção de Cliente + Cadastro Express ─────────────────
                _col_cli, _col_clr_cli, _col_btn = st.columns([5, 1, 1])
                with _col_cli:
                    pdv_cli_sel = st.selectbox(
                        "👤 Cliente",
                        ["— Selecione —"] + _cli_nomes,
                        key="pdv_cli_selectbox",
                        index=0,
                    )
                with _col_clr_cli:
                    st.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
                    if st.button("✕", key="pdv_btn_clr_cli", help="Limpar cliente",
                                 use_container_width=True):
                        st.session_state["pdv_cli_selectbox"] = "— Selecione —"
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                with _col_btn:
                    st.markdown(
                        "<div style='margin-top:28px'>",
                        unsafe_allow_html=True,
                    )
                    if st.button("➕", key="pdv_btn_novo_cli",
                                 help="Cadastrar Novo Cliente", use_container_width=True):
                        _dlg_cadastro_rapido()
                    st.markdown("</div>", unsafe_allow_html=True)

                # ── Seleção de Produto — Fluxo em Etapas ─────────────────────────────
                if not st.session_state.pdv_checkout:
                    # Inicializar keys do fluxo de variantes
                    for _vk in ("pdv_nome_sel", "pdv_cor_sel", "pdv_tam_sel", "_pdv_nome_prev"):
                        if _vk not in st.session_state:
                            st.session_state[_vk] = None

                    # ── Botão Novo Produto ────────────────────────────────────────
                    _col_prod, _col_novo_prod = st.columns([6, 1])
                    with _col_novo_prod:
                        st.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
                        if st.button("➕", key="pdv_btn_novo_prod", help="Cadastrar Novo Produto", use_container_width=True):
                            st.session_state['_pdv_novo_prod_open'] = not st.session_state.get('_pdv_novo_prod_open', False)
                        st.markdown("</div>", unsafe_allow_html=True)
                    if st.session_state.get('_pdv_novo_prod_open'):
                        with st.container(border=True):
                            st.markdown("#### Novo Produto")
                            _pa, _pb = st.columns(2)
                            _pnome = _pa.text_input("Nome *", key="pdv_np_nome")
                            _pcod  = _pb.text_input("Cod. Barras / Referencia", key="pdv_np_cod")
                            _pc, _pd, _pe = st.columns(3)
                            _ppreco = _pc.number_input("Preco Venda R$", min_value=0.0, step=0.01, format="%.2f", key="pdv_np_preco")
                            _pcusto = _pd.number_input("Preco Custo R$", min_value=0.0, step=0.01, format="%.2f", key="pdv_np_custo")
                            _pestq  = _pe.number_input("Estoque inicial", min_value=0, step=1, key="pdv_np_estq")
                            _ps1, _ps2 = st.columns([1, 4])
                            if _ps1.button("Salvar produto", key="pdv_np_salvar", type="primary"):
                                if _pnome.strip():
                                    run_command(
                                        "INSERT INTO produtos (nome,codigo_barras,preco_venda,preco_custo,estoque_atual,ativo,created_at) VALUES (%s,%s,%s,%s,%s,true,NOW())",
                                        (_pnome.strip().upper(), _pcod or None, _ppreco or None, _pcusto or None, int(_pestq))
                                    )
                                    st.success(f"Produto {_pnome} cadastrado!")
                                    st.session_state['_pdv_novo_prod_open'] = False
                                    st.session_state["pdv_nome_sel"] = _pnome.strip().upper()
                                    st.session_state["_pdv_nome_prev"] = None
                                    st.session_state.pop("pdv_prod_label_main", None)
                                    st.rerun()
                                else:
                                    st.warning("Nome obrigatorio.")
                            if _ps2.button("Cancelar", key="pdv_np_cancel"):
                                st.session_state['_pdv_novo_prod_open'] = False
                                st.rerun()

                    # ── Construir opções agrupadas por nome ───────────────────────
                    if not df_prod_pdv.empty:
                        _df_pv = df_prod_pdv.copy()
                        _df_pv["estoque_atual"] = pd.to_numeric(_df_pv["estoque_atual"], errors="coerce").fillna(0)
                        _nomes_agg = _df_pv.groupby("nome", as_index=False).agg(
                            total_est=("estoque_atual", "sum"),
                            preco_min=("preco_venda", "min"),
                        )
                        _cores_cnt = (
                            _df_pv[_df_pv["cor"].notna() & (_df_pv["cor"] != "")]
                            .groupby("nome")["cor"].nunique()
                        )
                        _nomes_agg["n_cores"] = _nomes_agg["nome"].map(_cores_cnt).fillna(0).astype(int)
                        def _fmt_np(r):
                            n_c = int(r["n_cores"])
                            n_e = int(r["total_est"])
                            return f"{r['nome']}  ({n_c} cores · {n_e} un.)" if n_c > 1 else f"{r['nome']}  ({n_e} un.)"
                        _nome_opts_pdv  = [_fmt_np(r) for _, r in _nomes_agg.iterrows()]
                        _label_to_nome  = {_fmt_np(r): r["nome"] for _, r in _nomes_agg.iterrows()}
                        _nome_to_label  = {r["nome"]: _fmt_np(r) for _, r in _nomes_agg.iterrows()}
                    else:
                        _nome_opts_pdv = []
                        _label_to_nome = {}
                        _nome_to_label = {}

                    # ── ETAPA 1: Selectbox de nome único ─────────────────────────
                    with _col_prod:
                        if _nome_opts_pdv:
                            _pre_nome = st.session_state.get("pdv_nome_sel")
                            _pre_label = _nome_to_label.get(_pre_nome, "— Selecione —") if _pre_nome else "— Selecione —"
                            _opts_n = ["— Selecione —"] + _nome_opts_pdv
                            _idx_n = _opts_n.index(_pre_label) if _pre_label in _opts_n else 0
                            _nome_label_widget = st.selectbox(
                                "👗 Produto", _opts_n, index=_idx_n,
                                key="pdv_prod_label_main",
                            )
                            _pdv_nome_sel = _label_to_nome.get(_nome_label_widget) if _nome_label_widget != "— Selecione —" else None
                        else:
                            st.warning("Nenhum produto em estoque.")
                            _pdv_nome_sel = None

                    # Detectar troca de nome → resetar cor e tamanho
                    if _pdv_nome_sel != st.session_state.get("_pdv_nome_prev"):
                        st.session_state["pdv_nome_sel"]  = _pdv_nome_sel
                        st.session_state["pdv_cor_sel"]   = None
                        st.session_state["pdv_tam_sel"]   = None
                        st.session_state["_pdv_nome_prev"] = _pdv_nome_sel

                    # ── ETAPA 2: Seleção de Cor ───────────────────────────────────
                    _pdv_cor_sel  = st.session_state.get("pdv_cor_sel")
                    _pdv_prod_id  = None
                    _pdv_prod_row = None
                    _prod_tem_grade = False
                    _grade_pdv_dict: dict = {}

                    if _pdv_nome_sel:
                        _df_vars = df_prod_pdv[
                            (df_prod_pdv["nome"] == _pdv_nome_sel) &
                            (pd.to_numeric(df_prod_pdv["estoque_atual"], errors="coerce").fillna(0) > 0)
                        ].copy()
                        _cores_disp = [
                            str(r["cor"]) for _, r in _df_vars.iterrows()
                            if r["cor"] and str(r["cor"]).strip()
                        ]
                        if len(_cores_disp) == 0:
                            _pdv_cor_sel = ""
                            st.session_state["pdv_cor_sel"] = ""
                            if not _df_vars.empty:
                                _pdv_prod_row = _df_vars.iloc[0]
                                _pdv_prod_id  = str(_pdv_prod_row["id"])
                        elif len(_cores_disp) == 1:
                            if _pdv_cor_sel != _cores_disp[0]:
                                _pdv_cor_sel = _cores_disp[0]
                                st.session_state["pdv_cor_sel"] = _pdv_cor_sel
                            _df_cm = _df_vars[_df_vars["cor"] == _pdv_cor_sel]
                            if not _df_cm.empty:
                                _pdv_prod_row = _df_cm.iloc[0]
                                _pdv_prod_id  = str(_pdv_prod_row["id"])
                            st.caption(f"🎨 Cor: **{_pdv_cor_sel}** (única disponível)")
                        else:
                            _cor_css_map = {
                                "preto":"#1a1a1a","branco":"#e8e8e8","cinza":"#808080","cinza mescla":"#a8a8a8",
                                "marrom":"#8B4513","marrom claro":"#c68a4a","bege":"#d4b896","caramelo":"#c68642",
                                "azul marinho":"#1A2035","azul claro":"#7ab8d4","vinho":"#722F37",
                                "verde":"#2d5a1b","verde militar":"#4a5240","laranja":"#e08c3c",
                                "vermelho":"#dc143c","roxo":"#6B3FA0","rosa":"#e8a0b0",
                                "amarelo":"#e0c830","estampado":"#cc6699","multicolor":"#ff6b6b",
                            }
                            _cores_claras = {"branco","bege","amarelo","cinza mescla","marrom claro","azul claro","rosa"}
                            st.markdown("**🎨 Escolha a Cor:**")
                            _n_cc = min(len(_cores_disp), 5)
                            _cor_cols = st.columns(_n_cc)
                            for _ci2, _cor_nm in enumerate(_cores_disp):
                                _bg   = _cor_css_map.get(_cor_nm.lower(), "#888888")
                                _tc   = "#222" if _cor_nm.lower() in _cores_claras else "#fff"
                                _brd  = "3px solid #B8892A" if _pdv_cor_sel == _cor_nm else "2px solid transparent"
                                with _cor_cols[_ci2 % _n_cc]:
                                    st.markdown(
                                        f"<div style='background:{_bg};color:{_tc};border:{_brd};"
                                        f"border-radius:8px;padding:6px 4px;text-align:center;"
                                        f"font-size:.78rem;font-weight:700;margin-bottom:2px'>{_cor_nm}</div>",
                                        unsafe_allow_html=True,
                                    )
                                    if st.button(_cor_nm, key=f"pdv_cor_btn_{_ci2}", use_container_width=True):
                                        st.session_state["pdv_cor_sel"] = _cor_nm
                                        st.session_state["pdv_tam_sel"] = None
                                        st.rerun()
                            if _pdv_cor_sel and _pdv_cor_sel in _cores_disp:
                                _df_cm = _df_vars[_df_vars["cor"] == _pdv_cor_sel]
                                if not _df_cm.empty:
                                    _pdv_prod_row = _df_cm.iloc[0]
                                    _pdv_prod_id  = str(_pdv_prod_row["id"])

                    # ── ETAPA 3: Seleção de Tamanho ─── produto_id INTEGER no GMH ─
                    _pdv_tam_sel = st.session_state.get("pdv_tam_sel")
                    if _pdv_prod_id and _pdv_cor_sel is not None:
                        _df_gv = run_query(
                            f"SELECT tamanho, estoque FROM produto_variacoes "
                            f"WHERE produto_id = {_pdv_prod_id} ORDER BY tamanho"
                        )
                        if not _df_gv.empty:
                            _prod_tem_grade = True
                            for _, _gvr in _df_gv.iterrows():
                                _grade_pdv_dict[str(_gvr["tamanho"])] = int(_gvr["estoque"])
                            _tams_ok = [t for t, e in _grade_pdv_dict.items() if e > 0]
                            if not _pdv_tam_sel and len(_tams_ok) == 1:
                                _pdv_tam_sel = _tams_ok[0]
                                st.session_state["pdv_tam_sel"] = _pdv_tam_sel
                            if _tams_ok:
                                st.markdown("**📏 Escolha o Tamanho:**")
                                _tam_order = ["PP","P","M","G","GG","XGG","34","36","38","40","42","44","46","48","U"]
                                _tams_ord  = sorted(_grade_pdv_dict.keys(), key=lambda t: _tam_order.index(t) if t in _tam_order else 99)
                                _n_tc = min(len(_tams_ord), 8)
                                _tam_cols = st.columns(_n_tc)
                                for _ti, _tam in enumerate(_tams_ord):
                                    _test  = _grade_pdv_dict[_tam]
                                    _is_st = (_pdv_tam_sel == _tam)
                                    _bg_t  = "#5bc5d3" if _is_st else ("#f0f0f0" if _test > 0 else "#e0e0e0")
                                    _c_t   = "#fff"   if _is_st else ("#333"   if _test > 0 else "#aaa")
                                    _brd_t = "3px solid #3db5c4" if _is_st else "1px solid #ccc"
                                    with _tam_cols[_ti % _n_tc]:
                                        st.markdown(
                                            f"<div style='background:{_bg_t};color:{_c_t};border:{_brd_t};"
                                            f"border-radius:6px;padding:6px 2px;text-align:center;"
                                            f"font-size:.82rem;font-weight:700;margin-bottom:2px'>{_tam}</div>",
                                            unsafe_allow_html=True,
                                        )
                                        if st.button(_tam, key=f"pdv_tam_btn_{_ti}", use_container_width=True, disabled=(_test == 0)):
                                            st.session_state["pdv_tam_sel"] = _tam
                                            st.rerun()
                        else:
                            _prod_tem_grade = False
                            if _pdv_tam_sel is None:
                                _pdv_tam_sel = ""
                                st.session_state["pdv_tam_sel"] = ""

                    # ── Preço de referência ───────────────────────────────────────
                    _pdv_preco_ref = 0.01
                    if _pdv_prod_row is not None and pd.notna(_pdv_prod_row.get("preco_venda")):
                        _pdv_preco_ref = float(_pdv_prod_row["preco_venda"])
                    if st.session_state.get("_pdv_preco_ref") != _pdv_preco_ref:
                        st.session_state["_pdv_preco_ref"] = _pdv_preco_ref
                        st.session_state.pop("pdv_preco_edit", None)

                    # ── Resumo da seleção ──────────────────────────────────────────
                    _pronto = (
                        _pdv_nome_sel is not None and
                        _pdv_cor_sel  is not None and
                        _pdv_tam_sel  is not None and
                        _pdv_prod_id  is not None
                    )
                    if _pronto:
                        _cor_rsum = f" | {_pdv_cor_sel}" if _pdv_cor_sel else ""
                        _tam_rsum = f" | {_pdv_tam_sel}" if _pdv_tam_sel else ""
                        _est_rsum = (
                            _grade_pdv_dict.get(_pdv_tam_sel, 0) if _prod_tem_grade and _pdv_tam_sel
                            else (int(_pdv_prod_row["estoque_atual"]) if _pdv_prod_row is not None else 0)
                        )
                        st.markdown(
                            f"<div style='background:#f0faf0;border-left:4px solid #5bc5d3;"
                            f"border-radius:8px;padding:8px 14px;margin:8px 0;font-size:.9rem'>"
                            f"✅ <b>{_pdv_nome_sel}</b>{_cor_rsum}{_tam_rsum} "
                            f"| R$ {_pdv_preco_ref:,.2f} | {_est_rsum} un. disponíveis</div>",
                            unsafe_allow_html=True,
                        )

                    # ── Observação e Data da Venda ────────────────────────────────
                    _col_obs, _col_dt = st.columns([3, 1])
                    with _col_obs:
                        _obs_preset_val = st.session_state.pop("pdv_obs_preset", "")
                        if _obs_preset_val and not st.session_state.get("pdv_obs_venda"):
                            st.session_state["pdv_obs_venda"] = _obs_preset_val
                        _obs_venda = st.text_input(
                            "📝 Observação da venda",
                            key="pdv_obs_venda",
                            placeholder="Ex: para Mariana filha, presente da Ana...",
                            max_chars=200,
                            label_visibility="visible"
                        )
                    with _col_dt:
                        import datetime as _dt
                        _data_venda = st.date_input(
                            "📅 Data",
                            value=_dt.date.today(),
                            key="pdv_data_venda",
                            format="DD/MM/YYYY"
                        )

                    # ── Formulário: Adicionar ao Carrinho ────────────────────────
                    with st.form("pdv_add_item", clear_on_submit=True):
                        _qtd_sel = st.number_input("Qtd", min_value=1, value=1, step=1)
                        _preco_placeholder = f"Padrao: R$ {st.session_state.get('_pdv_preco_ref', 0):.2f} (deixe vazio para usar este)"
                        _preco_txt = st.text_input("Valor unitario R$ (opcional)", key="pdv_preco_edit", placeholder=_preco_placeholder)
                        try:
                            _preco_venda_edit = float(_preco_txt.replace(',', '.')) if _preco_txt.strip() else st.session_state.get('_pdv_preco_ref', 0.01)
                        except Exception:
                            _preco_venda_edit = st.session_state.get('_pdv_preco_ref', 0.01)
                        _add_btn = st.form_submit_button(
                            "➕ Adicionar ao Carrinho",
                            use_container_width=True,
                            disabled=not _pronto,
                        )
                        if _add_btn:
                            if not _pronto:
                                st.error("Selecione produto, cor e tamanho.")
                            elif _prod_tem_grade and not _pdv_tam_sel:
                                st.error("⚠️ Selecione um tamanho antes de adicionar.")
                            else:
                                _pu = _preco_venda_edit if _preco_venda_edit and _preco_venda_edit > 0 else _pdv_preco_ref
                                _cor_ex = f" {_pdv_cor_sel}" if _pdv_cor_sel else ""
                                _tam_ex = f" {_pdv_tam_sel}" if _pdv_tam_sel else ""
                                _nome_exibir = f"{_pdv_nome_sel}{_cor_ex}{_tam_ex}".strip()
                                _existente = next(
                                    (it for it in st.session_state.pdv_carrinho
                                     if it["nome"] == _nome_exibir), None
                                )
                                if _existente:
                                    _existente["qtd"]     += int(_qtd_sel)
                                    _existente["subtotal"] = round(_existente["preco_unit"] * _existente["qtd"], 2)
                                else:
                                    st.session_state.pdv_carrinho.append({
                                        "nome":       _nome_exibir,
                                        "produto_id": _pdv_prod_id,
                                        "preco_unit": _pu,
                                        "qtd":        int(_qtd_sel),
                                        "subtotal":   round(_pu * int(_qtd_sel), 2),
                                        "tamanho":    _pdv_tam_sel if _pdv_tam_sel else None,
                                        "cor":        _pdv_cor_sel if _pdv_cor_sel else None,
                                    })
                                # Limpar seleção para próximo item
                                st.session_state["pdv_nome_sel"]   = None
                                st.session_state["pdv_cor_sel"]    = None
                                st.session_state["pdv_tam_sel"]    = None
                                st.session_state["_pdv_nome_prev"] = None
                                st.session_state.pop("pdv_prod_label_main", None)
                                st.rerun()

                # ── Exibição do Carrinho ──────────────────────────────────
                _carrinho = st.session_state.pdv_carrinho
                if _carrinho:
                    st.markdown(
                        "<div class='pdv-label' style='margin:14px 0 2px'>"
                        "🛒 CARRINHO</div>",
                        unsafe_allow_html=True,
                    )

                    # Cabeçalho
                    _h1, _h2, _h3, _h4, _h5 = st.columns([3.8, 0.7, 1.3, 1.3, 0.55])
                    _h1.markdown(
                        "<span style='font-size:.76rem;font-weight:700;"
                        "color:var(--pdv-label);letter-spacing:.05em'>PRODUTO</span>",
                        unsafe_allow_html=True,
                    )
                    _h2.markdown(
                        "<span style='font-size:.76rem;font-weight:700;"
                        "color:var(--pdv-label)'>QTD</span>",
                        unsafe_allow_html=True,
                    )
                    _h3.markdown(
                        "<span style='font-size:.76rem;font-weight:700;"
                        "color:var(--pdv-label)'>UNIT.</span>",
                        unsafe_allow_html=True,
                    )
                    _h4.markdown(
                        "<span style='font-size:.76rem;font-weight:700;"
                        "color:var(--pdv-label)'>SUBTOTAL</span>",
                        unsafe_allow_html=True,
                    )
                    _h5.markdown("")
                    st.markdown(
                        "<hr style='border:none;border-top:1.5px solid var(--pdv-hr);"
                        "margin:2px 0 4px'>",
                        unsafe_allow_html=True,
                    )

                    # Linhas de item com 🗑️ inline
                    for _ri, _item in enumerate(_carrinho):
                        _c1, _c2, _c3, _c4, _c5 = st.columns([3.8, 0.7, 1.3, 1.3, 0.55])
                        _c1.markdown(
                            f"<span style='font-size:.88rem'>{_item['nome'][:32]}</span>",
                            unsafe_allow_html=True,
                        )
                        _c2.markdown(
                            f"<span style='font-size:.88rem'>{_item['qtd']}</span>",
                            unsafe_allow_html=True,
                        )
                        _c3.markdown(
                            f"<span style='font-size:.88rem'>R$ {_item['preco_unit']:,.2f}</span>",
                            unsafe_allow_html=True,
                        )
                        _c4.markdown(
                            f"<span style='font-size:.88rem;font-weight:700'>"
                            f"R$ {_item['subtotal']:,.2f}</span>",
                            unsafe_allow_html=True,
                        )
                        if _c5.button(
                            "🗑️",
                            key=f"pdv_rm_{_ri}",
                            help=f"Remover '{_item['nome']}' do carrinho",
                        ):
                            st.session_state.pdv_carrinho.pop(_ri)
                            st.session_state.pdv_checkout = False
                            st.rerun()

                    # Total bruto
                    _total_bruto = sum(it["subtotal"] for it in _carrinho)
                    st.markdown(
                        f"<hr style='border:none;border-top:1px solid var(--pdv-hr);"
                        f"margin:6px 0 4px'>"
                        f"<div style='text-align:right;font-size:1.05rem;"
                        f"font-weight:800;color:var(--pdv-card-h4);padding:2px 0 8px'>"
                        f"Subtotal: R$ {_total_bruto:,.2f}</div>",
                        unsafe_allow_html=True,
                    )

                    # ── CHECKOUT ─────────────────────────────────────────────
                    if not st.session_state.pdv_checkout:
                        # JS: pinta o botão Finalizar Venda de verde vibrante
                        components.html("""
    <script>
    (function() {
        function pintarFinalizar() {
            try {
                var doc = window.parent.document;
                doc.querySelectorAll('button').forEach(function(btn) {
                    if ((btn.innerText || '').trim().includes('Finalizar Venda')) {
                        btn.style.setProperty('background-color','#22c55e','important');
                        btn.style.setProperty('border-color',    '#16a34a','important');
                        btn.style.setProperty('color',           '#fff',   'important');
                        btn.style.setProperty('font-weight',     '700',    'important');
                        btn.style.setProperty('font-size',       '1.05rem','important');
                    }
                });
            } catch(_){}
        }
        setTimeout(pintarFinalizar, 100);
        setTimeout(pintarFinalizar, 500);
        new MutationObserver(pintarFinalizar).observe(
            window.parent.document.body, { childList: true, subtree: true }
        );
    })();
    </script>
    """, height=0)
                        if st.button(
                            "🛒 Finalizar Venda", key="pdv_ir_checkout",
                            use_container_width=True, type="primary",
                        ):
                            st.session_state.pdv_checkout = True
                            st.rerun()
                    else:
                        st.markdown(
                            "<div class='pdv-label' style='margin-bottom:10px'>"
                            "💳 CHECKOUT</div>",
                            unsafe_allow_html=True,
                        )
                        _FORMAS_PAG = [
                            "Dinheiro", "Pix", "Cartão de Débito",
                            "Cartão de Crédito", "Crediário",
                        ]
                        _df_vnd_pdv = run_query(
                            "SELECT codigo_vendedor, COALESCE(nome_vendedor, codigo_vendedor) AS label "
                            "FROM config_comissao WHERE ativo = true ORDER BY codigo_vendedor"
                        )
                        if not _df_vnd_pdv.empty:
                            _vnd_opts = _df_vnd_pdv["codigo_vendedor"].tolist()
                            _vnd_lbl  = _df_vnd_pdv["label"].tolist()
                            _chk_cod_sel = st.selectbox(
                                "🏷️ Vendedora *",
                                range(len(_vnd_opts)),
                                format_func=lambda i: f"{_vnd_opts[i]} — {_vnd_lbl[i]}",
                                key="pdv_chk_cod_vnd_sel",
                                help="Selecione a vendedora responsável pela venda.",
                            )
                            _chk_cod_vnd = _vnd_opts[_chk_cod_sel]
                        else:
                            _chk_cod_vnd = st.text_input(
                                "🏷️ Código Vendedor *", key="pdv_chk_cod_vnd",
                                placeholder="Cadastre vendedoras em Administração.",
                            )
                        _chk_desc  = st.number_input(
                            "Desconto Global (%)", min_value=0.0, max_value=100.0,
                            value=0.0, step=1.0, format="%.1f", key="pdv_chk_desc",
                        )
                        _chk_forma = st.selectbox(
                            "💳 Forma de Pagamento", _FORMAS_PAG, key="pdv_chk_forma"
                        )
                        _chk_parcelas = 1
                        if _chk_forma in ("Cartão de Crédito", "Crediário"):
                            _chk_parcelas = int(st.number_input(
                                "Parcelas", min_value=1, max_value=12,
                                value=1, step=1, key="pdv_chk_parcelas",
                            ))
                        _chk_cupom = st.toggle(
                            "🖨️ Gerar Cupom para Impressão?",
                            value=True, key="pdv_chk_cupom",
                        )

                        # ── Resumo financeiro final ───────────────────────────
                        # Fórmula canônica: uma única operação, sem arredondamento intermediário.
                        # _total_liq é a fonte de verdade → banco, cupom e parcelas derivam dele.
                        _total_liq = round(_total_bruto * (1.0 - _chk_desc / 100.0), 2)
                        _desc_R    = round(_total_bruto - _total_liq, 2)   # apenas para exibir
                        _parc_v   = round(_total_liq / _chk_parcelas, 2)
                        _parc_str = (
                            f"{_chk_parcelas}x de R$ {_parc_v:,.2f}"
                            if _chk_parcelas > 1 else f"R$ {_total_liq:,.2f} à vista"
                        )
                        _desc_line = (
                            f"<br><span style='color:#d97706;font-size:.87rem'>"
                            f"Desconto: -{_chk_desc:.1f}% = -R$ {_desc_R:,.2f}</span>"
                            if _chk_desc > 0 else ""
                        )
                        st.markdown(
                            f"<div style='background:#e8f8fa;border-left:4px solid #5bc5d3;"
                            f"border-radius:8px;padding:12px 16px;margin:8px 0 12px'>"
                            f"<span style='font-size:1.3rem;font-weight:900;color:#022c3a'>"
                            f"Total: R$ {_total_liq:,.2f}</span>{_desc_line}"
                            f"<br><span style='color:#555;font-size:.88rem'>"
                            f"{_chk_forma} · {_parc_str}</span></div>",
                            unsafe_allow_html=True,
                        )

                        # ── Pré-calcula valores do vendedor para trava e cupom ────
                        _cli_atual       = st.session_state.get("pdv_cli_selectbox", "— Selecione —")
                        _chk_cod_vnd_val = (
                            _chk_cod_vnd if isinstance(_chk_cod_vnd, str) else str(_chk_cod_vnd)
                        ).strip()
                        # Nome de exibição da vendedora para o cupom
                        _chk_nome_vnd = ""
                        if not _df_vnd_pdv.empty and _chk_cod_vnd_val:
                            _vnd_match = _df_vnd_pdv[_df_vnd_pdv["codigo_vendedor"] == _chk_cod_vnd_val]
                            if not _vnd_match.empty:
                                _chk_nome_vnd = str(_vnd_match["label"].iloc[0])

                        _trava_cli = _cli_atual == "— Selecione —"
                        _trava_vnd = not bool(_chk_cod_vnd_val)

                        if _trava_vnd:
                            st.warning("⚠️ Selecione o Vendedor para liberar a confirmação.")

                        _btn1, _btn2 = st.columns(2)
                        with _btn1:
                            if st.button(
                                "✅ Confirmar Venda", key="pdv_chk_confirmar",
                                use_container_width=True, type="primary",
                                disabled=(_trava_cli or _trava_vnd or _total_liq <= 0),
                            ):
                                if _trava_cli:
                                    st.error("Selecione um cliente antes de finalizar.")
                                elif _total_liq <= 0:
                                    st.error("Valor final inválido.")
                                else:
                                    try:
                                        _cli_row  = df_cli_pdv[
                                            df_cli_pdv["nome"] == _cli_atual
                                        ]
                                        _cli_id   = str(_cli_row["id"].iloc[0])
                                        _forma_map = {
                                            "Dinheiro":          "dinheiro",
                                            "Pix":               "pix",
                                            "Cartão de Débito":  "cartão",
                                            "Cartão de Crédito": "cartão",
                                            "Crediário":         "crediário",
                                        }
                                        _desc_linhas = "; ".join(
                                            f"{it['nome']} x{it['qtd']}"
                                            for it in _carrinho
                                        )
                                        _operador = st.session_state.get("username", "")
                                        _dados_fin = {
                                            "cliente_id":      _cli_id,
                                            "cliente_nome":    _cli_atual,
                                            "descricao":       _desc_linhas[:120],
                                            "valor_total":     _total_liq,
                                            "valor_original":  _total_bruto,
                                            "desconto_pct":    _chk_desc,
                                            "forma_pagamento": _forma_map[_chk_forma],
                                            "parcelas":        _chk_parcelas,
                                            "vendedor_nome":   _operador,
                                            "nome_vendedor":   _chk_nome_vnd,
                                            "codigo_vendedor": _chk_cod_vnd_val,
                                            "observacao":      st.session_state.get("pdv_obs_venda", "").strip() or None,
                                        }
                                        # Monta lista de itens para itens_venda
                                        _itens_venda = [
                                            {
                                                "produto_id": it.get("produto_id", ""),
                                                "nome":       it.get("nome",""),
                                                "qtd":        it["qtd"],
                                                "preco_unit": it["preco_unit"],
                                                "tamanho":    it.get("tamanho"),
                                                "cor":        it.get("cor"),
                                            }
                                            for it in _carrinho
                                            if it.get("produto_id")  # só salva em itens_venda se tem produto_id
                                        ]
                                        # Garante que todos itens aparecem no cupom
                                        _dados_fin["itens_carrinho"] = list(_carrinho)
                                        _venda_id = salvar_venda(_dados_fin, _itens_venda)
                                        # Dar baixa em produto_variacoes (produto_id INTEGER no GMH)
                                        for _it_gv in _itens_venda:
                                            if _it_gv.get("tamanho") and _it_gv.get("produto_id"):
                                                run_command(
                                                    "UPDATE produto_variacoes SET estoque = GREATEST(estoque - %s, 0) "
                                                    "WHERE produto_id = %s AND tamanho = %s",
                                                    (_it_gv["qtd"], _it_gv["produto_id"], _it_gv["tamanho"]),
                                                )
                                        _df_num   = run_query(
                                            "SELECT COUNT(*) AS total FROM vendas"
                                        )
                                        _num_cup = (
                                            int(_df_num["total"].iloc[0])
                                            if not _df_num.empty else 1
                                        )
                                        # Gera cupom sempre (usado no WhatsApp mesmo sem impressão)
                                        _cupom_gerado = gerar_cupom(
                                            _dados_fin, _venda_id, _num_cup,
                                            vendedor=_operador,
                                            nome_vendedor=_chk_nome_vnd,
                                        )
                                        _obs_cupom = (_dados_fin or {}).get("observacao")
                                        if _obs_cupom:
                                            _sep_cupom = "─" * 42
                                            _obs_cupom_linha = ("Obs: " + str(_obs_cupom))[:42]
                                            _cupom_gerado = _cupom_gerado.replace(
                                                _sep_cupom, _obs_cupom_linha + chr(10) + _sep_cupom, 1)
                                        # Salva o cupom gerado na venda
                                        with _db_get_conn() as conn:
                                            with conn.cursor() as cur:
                                                cur.execute(
                                                    "UPDATE vendas SET cupom_text = %s WHERE id = %s",
                                                    (_cupom_gerado, _venda_id)
                                                )
                                                conn.commit()
                                        if _chk_cupom:
                                            st.session_state.va_ultimo_cupom = {
                                                "text":     _cupom_gerado,
                                                "venda_id": _venda_id,
                                                "num":      _num_cup,
                                            }
                                        # Busca WhatsApp do cliente para o botão pós-venda
                                        _df_wpp_cli = run_query(
                                            "SELECT whatsapp FROM clientes "
                                            f"WHERE id = '{_cli_id}' LIMIT 1"
                                        )
                                        _wpp_cli = (
                                            str(_df_wpp_cli["whatsapp"].iloc[0])
                                            if not _df_wpp_cli.empty
                                               and pd.notna(_df_wpp_cli["whatsapp"].iloc[0])
                                            else ""
                                        )
                                        st.session_state.pdv_ultima_venda = {
                                            "num":          _num_cup,
                                            "cliente_id":   _cli_id,
                                            "cliente_nome": _cli_atual,
                                            "venda_id":     _venda_id,
                                            "valor":        _total_liq,
                                            "wpp":          _wpp_cli,
                                            "cupom_text":   _cupom_gerado,
                                        }
                                        # MELHORIA 5: Limpar todos os campos do PDV
                                        st.session_state.pdv_carrinho = []
                                        st.session_state.pdv_checkout = False
                                        # Usar pop para remover widgets (não atribuir valores após renderização)
                                        st.session_state.pop("pdv_cli_selectbox", None)
                                        st.session_state.pop("pdv_prod_label_main", None)
                                        st.session_state.pop("pdv_obs_venda", None)
                                        st.session_state.pop("pdv_data_venda", None)
                                        st.session_state.pop("pdv_chk_desc", None)
                                        st.session_state.pop("pdv_chk_forma", None)
                                        st.session_state.pop("pdv_chk_parcelas", None)
                                        st.session_state.pop("pdv_chk_cupom", None)
                                        st.session_state.pop("pdv_chk_cod_vnd_sel", None)
                                        st.session_state.pop("pdv_chk_cod_vnd", None)
                                        st.session_state["pdv_nome_sel"]   = None
                                        st.session_state["pdv_cor_sel"]    = None
                                        st.session_state["pdv_tam_sel"]    = None
                                        st.session_state["_pdv_nome_prev"] = None
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro ao salvar venda: {e}")
                        with _btn2:
                            if st.button(
                                "← Voltar ao Carrinho", key="pdv_chk_voltar",
                                use_container_width=True,
                            ):
                                st.session_state.pdv_checkout = False
                                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

        # IA concentrada exclusivamente em ✨ GM Homem AI (menu lateral)

    with _vtab_dia:
        import datetime as _dth_dia
        _hoje_dia = _dth_dia.date.today()
        st.markdown("### 📊 Painel do Dia")

        _df_dia = run_query("""
            SELECT
              COUNT(*) as total_vendas,
              COALESCE(SUM(valor_total),0) as total_geral,
              COALESCE(SUM(CASE WHEN forma_pagamento ILIKE '%pix%' THEN valor_total END),0) as pix,
              COALESCE(SUM(CASE WHEN forma_pagamento ILIKE '%cart%'
                               OR forma_pagamento ILIKE '%cred%'
                               OR forma_pagamento ILIKE '%deb%'
                               THEN valor_total END),0) as cartao,
              COALESCE(SUM(CASE WHEN forma_pagamento ILIKE '%dinheiro%'
                               OR forma_pagamento ILIKE '%espe%'
                               THEN valor_total END),0) as dinheiro,
              COALESCE(SUM(CASE WHEN forma_pagamento ILIKE '%crediario%'
                               OR forma_pagamento ILIKE '%prazo%'
                               THEN valor_total END),0) as crediario,
              COALESCE(MAX(valor_total),0) as maior_venda
            FROM vendas
            WHERE DATE(created_at) = CURRENT_DATE AND status != 'cancelada'
        """)

        _tv_d  = int(_df_dia["total_vendas"].iloc[0]) if not _df_dia.empty else 0
        _tg_d  = float(_df_dia["total_geral"].iloc[0]) if not _df_dia.empty else 0.0
        _pix_d = float(_df_dia["pix"].iloc[0]) if not _df_dia.empty else 0.0
        _car_d = float(_df_dia["cartao"].iloc[0]) if not _df_dia.empty else 0.0
        _din_d = float(_df_dia["dinheiro"].iloc[0]) if not _df_dia.empty else 0.0
        _cre_d = float(_df_dia["crediario"].iloc[0]) if not _df_dia.empty else 0.0
        _max_d = float(_df_dia["maior_venda"].iloc[0]) if not _df_dia.empty else 0.0
        _tck_d = (_tg_d / _tv_d) if _tv_d > 0 else 0.0

        _dm1, _dm2, _dm3, _dm4 = st.columns(4)
        _dm1.metric("💰 Total do Dia",  f"R$ {_tg_d:,.2f}")
        _dm2.metric("🛒 Nº de Vendas",  _tv_d)
        _dm3.metric("🎯 Ticket Médio",  f"R$ {_tck_d:,.2f}")
        _dm4.metric("🏆 Maior Venda",   f"R$ {_max_d:,.2f}")

        _dm5, _dm6, _dm7, _dm8 = st.columns(4)
        _dm5.metric("📱 PIX",       f"R$ {_pix_d:,.2f}")
        _dm6.metric("💳 Cartão",    f"R$ {_car_d:,.2f}")
        _dm7.metric("💵 Dinheiro",  f"R$ {_din_d:,.2f}")
        _dm8.metric("📋 Crediário", f"R$ {_cre_d:,.2f}")

        st.markdown("---")
        _df_hora = run_query("""
            SELECT EXTRACT(HOUR FROM created_at)::int AS hora,
                   COALESCE(SUM(valor_total),0) AS total
            FROM vendas
            WHERE DATE(created_at) = CURRENT_DATE AND status != 'cancelada'
            GROUP BY hora ORDER BY hora
        """)
        if not _df_hora.empty:
            import pandas as _pdh
            _df_hfull = _pdh.DataFrame({"hora": range(7, 22)}).merge(
                _df_hora, on="hora", how="left").fillna(0)
            _df_hfull["Hora"] = _df_hfull["hora"].apply(lambda h: f"{int(h):02d}h")
            _df_hfull = _df_hfull.set_index("Hora")[["total"]]
            _df_hfull.columns = ["Vendas (R$)"]
            st.markdown("**Vendas por Hora do Dia**")
            st.bar_chart(_df_hfull)

        st.markdown("**Últimas 10 Vendas**")
        _df_ult10 = run_query("""
            SELECT c.nome AS "Cliente",
                   STRING_AGG(p.nome||' x'||iv.quantidade::text, ', ') AS "Produtos",
                   v.forma_pagamento AS "Pagamento",
                   v.valor_total AS "Valor (R$)",
                   v.status AS "Status",
                   TO_CHAR(v.created_at, 'HH24:MI') AS "Hora"
            FROM vendas v
            LEFT JOIN clientes c ON c.id = v.cliente_id
            LEFT JOIN itens_venda iv ON iv.venda_id = v.id
            LEFT JOIN produtos p ON p.id = iv.produto_id
            WHERE DATE(v.created_at) = CURRENT_DATE
            GROUP BY v.id, c.nome, v.forma_pagamento, v.valor_total, v.status, v.created_at
            ORDER BY v.created_at DESC LIMIT 10
        """)
        if not _df_ult10.empty:
            st.dataframe(_df_ult10, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma venda hoje ainda.")

    with _vtab_hist:
        import datetime as _dth_hist
        st.markdown("### 📋 Histórico de Vendas")

        _hc1, _hc2, _hc3 = st.columns([2, 2, 2])
        _per_h = _hc1.selectbox(
            "Período", ["Hoje", "Esta Semana", "Este Mês", "Personalizado"],
            key="hist_periodo"
        )
        _forma_h = _hc2.selectbox(
            "Forma de Pagamento",
            ["Todas", "PIX", "Cartão", "Dinheiro", "Crediário"],
            key="hist_forma"
        )
        _busca_h = _hc3.text_input("Buscar Cliente", key="hist_busca",
                                    placeholder="Nome do cliente...")

        _hoje_h2 = _dth_hist.date.today()
        if _per_h == "Hoje":
            _d1h, _d2h = _hoje_h2, _hoje_h2
        elif _per_h == "Esta Semana":
            _d1h = _hoje_h2 - _dth_hist.timedelta(days=_hoje_h2.weekday())
            _d2h = _hoje_h2
        elif _per_h == "Este Mês":
            _d1h = _hoje_h2.replace(day=1)
            _d2h = _hoje_h2
        else:
            _hdc1, _hdc2 = st.columns(2)
            _d1h = _hdc1.date_input("De",  value=_hoje_h2.replace(day=1), key="hist_d1", format="DD/MM/YYYY")
            _d2h = _hdc2.date_input("Até", value=_hoje_h2, key="hist_d2", format="DD/MM/YYYY")

        _wf_h = {
            "PIX":       "AND v.forma_pagamento ILIKE '%pix%'",
            "Cartão":    "AND (v.forma_pagamento ILIKE '%cart%' OR v.forma_pagamento ILIKE '%cred%' OR v.forma_pagamento ILIKE '%deb%')",
            "Dinheiro":  "AND (v.forma_pagamento ILIKE '%dinheiro%' OR v.forma_pagamento ILIKE '%espe%')",
            "Crediário": "AND (v.forma_pagamento ILIKE '%crediario%' OR v.forma_pagamento ILIKE '%prazo%')",
        }.get(_forma_h, "")
        _wc_h = f"AND c.nome ILIKE '%{_busca_h.replace(chr(39), chr(39)*2)}%'" if _busca_h.strip() else ""

        _df_hist = run_query(f"""
            SELECT v.id::text AS venda_id,
                   TO_CHAR(v.created_at, 'DD/MM HH24:MI') AS "Data/Hora",
                   COALESCE(c.nome, 'Consumidor') AS "Cliente",
                   v.forma_pagamento AS "Pagamento",
                   COALESCE(v.parcelas, 1) AS "Parcelas",
                   v.valor_total AS "Valor",
                   v.status AS "Status"
            FROM vendas v
            LEFT JOIN clientes c ON c.id = v.cliente_id
            WHERE v.created_at::date BETWEEN '{_d1h}' AND '{_d2h}'
            {_wf_h} {_wc_h}
            ORDER BY v.created_at DESC
        """)

        if not _df_hist.empty:
            _tot_h  = float(_df_hist["Valor"].sum())
            _qtd_h  = len(_df_hist)
            _tck_h  = _tot_h / _qtd_h if _qtd_h > 0 else 0.0
            _fmais  = _df_hist["Pagamento"].mode().iloc[0] if _qtd_h > 0 else "—"

            _kh1, _kh2, _kh3, _kh4 = st.columns(4)
            _kh1.metric("💰 Total",          f"R$ {_tot_h:,.2f}")
            _kh2.metric("🛒 Vendas",          _qtd_h)
            _kh3.metric("🎯 Ticket Médio",    f"R$ {_tck_h:,.2f}")
            _kh4.metric("🏆 Forma Mais Usada", _fmais)

            st.markdown("---")
            _df_disp = _df_hist.drop(columns=["venda_id"], errors="ignore")
            st.dataframe(_df_disp, use_container_width=True, hide_index=True)

            for _, _hrow in _df_hist.iterrows():
                _hvid = str(_hrow["venda_id"])
                _hparc = int(_hrow.get("Parcelas", 1) or 1)
                _hforma_label = f"{_hparc}x {_hrow['Pagamento']}" if _hparc > 1 else _hrow['Pagamento']
                with st.expander(
                    f"🔍 {_hrow['Data/Hora']} · {_hrow['Cliente']} · "
                    f"R$ {float(_hrow['Valor']):,.2f} · {_hforma_label}"
                ):
                    _df_itens_h = run_query(f"""
                        SELECT COALESCE(iv.nome_produto, p.nome, '—') AS "Produto",
                               CASE WHEN iv.cor IS NOT NULL AND iv.cor != ''
                                    THEN iv.cor ELSE '' END AS "Cor",
                               CASE WHEN iv.tamanho IS NOT NULL AND iv.tamanho != ''
                                    THEN iv.tamanho ELSE '' END AS "Tamanho",
                               iv.quantidade AS "Qtd",
                               COALESCE(iv.preco_unit, iv.preco_unitario) AS "Preço Unit",
                               iv.subtotal AS "Subtotal"
                        FROM itens_venda iv
                        LEFT JOIN produtos p ON p.id = iv.produto_id
                        WHERE iv.venda_id = {int(_hvid) if _hvid.isdigit() else 0}
                    """)
                    if not _df_itens_h.empty:
                        st.dataframe(_df_itens_h, use_container_width=True, hide_index=True)
                    else:
                        st.caption("Sem itens registrados.")

            st.markdown("---")
            st.markdown("**Totais por Forma de Pagamento**")
            _df_tfp = (
                _df_hist.groupby("Pagamento")["Valor"]
                .agg(["sum", "count"])
                .reset_index()
            )
            _df_tfp.columns = ["Forma", "Total (R$)", "Qtd"]
            _df_tfp["Total (R$)"] = _df_tfp["Total (R$)"].apply(lambda x: f"R$ {float(x):,.2f}")
            st.dataframe(_df_tfp, use_container_width=True, hide_index=True)

            import io as _io_h
            _csv_h = _df_disp.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Exportar CSV", _csv_h,
                f"vendas_{_d1h}_{_d2h}.csv", "text/csv",
                key="hist_export"
            )
        else:
            st.info("Nenhuma venda no período selecionado.")

elif pagina == "📚 Histórico Legado":
    if _role == "vendas":
        st.error("🔒 Área restrita — somente administradores.")
        st.stop()
    st.subheader("📚 Histórico Sistema Antigo")
    st.caption("Consulta ao histórico do sistema SGA — 10.005 registros")

    # Carregar clientes para autocomplete
    _df_cli_leg = run_query("""
        SELECT DISTINCT hl.cliente_codigo as cod,
               COALESCE(c.nome, hl.cliente_codigo) as nome,
               COALESCE(c.tags::text, '') as tags
        FROM historico_legado hl
        LEFT JOIN clientes c ON c.id = hl.cliente_id
        ORDER BY nome
    """)
    _opts_leg = ['']
    _map_leg = {}
    if not _df_cli_leg.empty:
        for _, _r in _df_cli_leg.iterrows():
            _tag = str(_r.get('tags','')).strip()
            _label = f"{_r['nome']} [{_tag}]" if _tag and _tag not in ('','None','nan') else str(_r['nome'])
            _opts_leg.append(_label)
            _map_leg[_label] = (str(_r['cod']), str(_r['nome']))
    col1, col2, col3 = st.columns([3, 1.5, 1])
    with col1:
        _sel_leg = st.selectbox(
            '🔍 Buscar cliente (nome, codigo ou tag)',
            options=_opts_leg,
            format_func=lambda x: 'Digite para buscar...' if x == '' else x,
            key='hist_busca_cliente'
        )
        busca_cliente = _map_leg[_sel_leg][1] if _sel_leg and _sel_leg in _map_leg else ''
        _cod_sel_leg = _map_leg[_sel_leg][0] if _sel_leg and _sel_leg in _map_leg else ''
    with col2:
        status_filtro = st.selectbox(
            'Status',
            ['Todos', 'baixado', 'aberto'],
            key='hist_status'
        )
    with col3:
        btn_limpar = st.button('🔄 Limpar', use_container_width=True, key='hist_limpar_btn')
    if btn_limpar:
        for k in ['hist_busca_cliente', 'hist_status']:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    if not busca_cliente:
        try:
            _kpi = run_query("""
                SELECT
                    COUNT(*) as total,
                    COUNT(DISTINCT cliente_codigo) as clientes,
                    SUM(CASE WHEN status='baixado' THEN 1 ELSE 0 END) as baixados,
                    SUM(CASE WHEN status='aberto'  THEN 1 ELSE 0 END) as abertos,
                    SUM(valor_docto) as valor_total
                FROM historico_legado
            """)
            if not _kpi.empty:
                r = _kpi.iloc[0]
                c1,c2,c3,c4,c5 = st.columns(5)
                c1.metric("📋 Registros", f"{int(r.total):,}")
                c2.metric("👤 Clientes", f"{int(r.clientes):,}")
                c3.metric("✅ Baixados", f"{int(r.baixados):,}")
                c4.metric("⏳ Abertos", f"{int(r.abertos):,}")
                c5.metric("💰 Valor Total", f"R$ {float(r.valor_total or 0):,.2f}")
        except Exception as e:
            st.warning(f"Erro ao carregar KPIs: {e}")
        st.info("👆 Digite o nome ou código do cliente para consultar o histórico.")
    else:
        try:
            busca = busca_cliente.strip()
            if _cod_sel_leg and _cod_sel_leg.isdigit(): busca = _cod_sel_leg
            if busca.isdigit():
                _query = """
                    SELECT c.nome as cliente_nome, hl.cliente_codigo as cod,
                        hl.documento, hl.ordem,
                        TO_CHAR(hl.dt_emissao,'DD/MM/YYYY') as emissao,
                        TO_CHAR(hl.dt_vencimento,'DD/MM/YYYY') as vencimento,
                        TO_CHAR(hl.data_baixa,'DD/MM/YYYY') as baixa,
                        hl.valor_docto as valor, hl.valor_recebido as recebido,
                        hl.status, hl.modalidade, hl.vendedor, hl.observacao
                    FROM historico_legado hl
                    LEFT JOIN clientes c ON c.id = hl.cliente_id
                    WHERE hl.cliente_codigo = %s
                """
                _params = [busca]
            else:
                _query = """
                    SELECT c.nome as cliente_nome, hl.cliente_codigo as cod,
                        hl.documento, hl.ordem,
                        TO_CHAR(hl.dt_emissao,'DD/MM/YYYY') as emissao,
                        TO_CHAR(hl.dt_vencimento,'DD/MM/YYYY') as vencimento,
                        TO_CHAR(hl.data_baixa,'DD/MM/YYYY') as baixa,
                        hl.valor_docto as valor, hl.valor_recebido as recebido,
                        hl.status, hl.modalidade, hl.vendedor, hl.observacao
                    FROM historico_legado hl
                    INNER JOIN clientes c ON c.id = hl.cliente_id
                    WHERE (
                        UPPER(c.nome) LIKE UPPER('%' || %(b)s || '%')
                        OR UPPER(COALESCE(hl.observacao,'')) LIKE UPPER('%' || %(b)s || '%')
                        OR UPPER(COALESCE(c.tags::text,'')) LIKE UPPER('%' || %(b)s || '%')
                    )
                """
                _params = {"b": busca}

            if status_filtro != "Todos":
                _params["s"] = status_filtro
                _query += " AND hl.status = %(s)s"
            _query += " ORDER BY hl.dt_vencimento DESC LIMIT 500"

            _df_hist = run_query(_query, _params)

            if _df_hist.empty:
                st.warning(f"❌ Nenhum registro para: **{busca}**")
                if not busca.isdigit():
                    _sug = run_query("""
                        SELECT DISTINCT c.nome, hl.cliente_codigo
                        FROM historico_legado hl
                        INNER JOIN clientes c ON c.id = hl.cliente_id
                        WHERE c.nome ILIKE %s LIMIT 5
                    """, [f"%{busca.split()[0]}%"])
                    if not _sug.empty:
                        st.info("💡 Você quis dizer?")
                        for _, row in _sug.iterrows():
                            st.write(f"• **{row.nome}** (cód. {row.cliente_codigo})")
            else:
                nome_exib = _df_hist["cliente_nome"].iloc[0] if "cliente_nome" in _df_hist.columns else busca
                total_val = float(_df_hist["valor"].sum()) if "valor" in _df_hist.columns else 0
                qtd_bx = len(_df_hist[_df_hist["status"] == "baixado"]) if "status" in _df_hist.columns else 0
                qtd_ab = len(_df_hist[_df_hist["status"] == "aberto"]) if "status" in _df_hist.columns else 0

                st.success(f"**{nome_exib}** — {len(_df_hist)} registros")
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("📋 Total", len(_df_hist))
                c2.metric("✅ Baixados", qtd_bx)
                c3.metric("⏳ Abertos", qtd_ab)
                c4.metric("💰 Valor Total", f"R$ {total_val:,.2f}")
                st.divider()
                st.divider()
                # Toggle modo visualização
                _modo_hist = st.radio('Visualização', ['📋 Tabela', '🔍 Por Duplicata (com produtos)'], horizontal=True, key='hist_modo_view')
                if _modo_hist == '📋 Tabela':
                    st.dataframe(
                        _df_hist,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            'cliente_nome': st.column_config.TextColumn('Cliente', width='medium'),
                            'cod':          st.column_config.TextColumn('Cód', width='small'),
                            'documento':    st.column_config.TextColumn('Doc', width='small'),
                            'ordem':        st.column_config.TextColumn('Ord', width='tiny'),
                            'emissao':      st.column_config.TextColumn('Emissão', width='small'),
                            'vencimento':   st.column_config.TextColumn('Vencimento', width='small'),
                            'baixa':        st.column_config.TextColumn('Baixa', width='small'),
                            'valor':        st.column_config.NumberColumn('Valor', format='R$ %.2f'),
                            'recebido':     st.column_config.NumberColumn('Recebido', format='R$ %.2f'),
                            'status':       st.column_config.TextColumn('Status', width='small'),
                            'modalidade':   st.column_config.TextColumn('Modalidade'),
                            'vendedor':     st.column_config.TextColumn('Vend.', width='tiny'),
                            'observacao':   st.column_config.TextColumn('Obs'),
                        }
                    )
                else:
                    # Agrupar por documento e mostrar com produtos
                    _cod_cli = str(_df_hist['cod'].iloc[0]) if 'cod' in _df_hist.columns else ''
                    _docs_unicos = _df_hist['documento'].unique().tolist() if 'documento' in _df_hist.columns else []
                    for _doc in _docs_unicos:
                        _rows_doc = _df_hist[_df_hist['documento'] == _doc]
                        _ordens = _rows_doc['ordem'].tolist() if 'ordem' in _rows_doc.columns else []
                        _venc_doc = _rows_doc['vencimento'].iloc[0] if 'vencimento' in _rows_doc.columns else ''
                        _val_doc = float(_rows_doc['valor'].sum()) if 'valor' in _rows_doc.columns else 0
                        _st_doc = _rows_doc['status'].iloc[0] if 'status' in _rows_doc.columns else ''
                        _modal = _rows_doc['modalidade'].iloc[0] if 'modalidade' in _rows_doc.columns else ''
                        _stico = '✅' if _st_doc == 'baixado' else '⏳'
                        _ordens_str = '/'.join(str(o) for o in _ordens)
                        with st.expander(f'{_stico} Doc {_doc}-{_ordens_str} | Venc {_venc_doc} | R$ {_val_doc:,.2f} | {_modal}'):
                            # Parcelas
                            if len(_rows_doc) > 1:
                                st.markdown('**Parcelas:**')
                                for _, _pr in _rows_doc.iterrows():
                                    _pst = '✅' if _pr.get('status')=='baixado' else '⏳'
                                    _pbx = f" · pago {_pr['baixa']}" if _pr.get('baixa') else ''
                                    st.write(f"  {_pst} Ordem {_pr['ordem']} | Venc {_pr['vencimento']} | R$ {float(_pr['valor']):,.2f}{_pbx}")
                            else:
                                _pr = _rows_doc.iloc[0]
                                _pst = '✅' if _pr.get('status')=='baixado' else '⏳'
                                _pbx = f" · pago {_pr['baixa']}" if _pr.get('baixa') else ''
                                st.write(f"{_pst} Status: {_pr.get('status','?')} | Venc {_pr['vencimento']}{_pbx}")
                            # Produtos da duplicata
                            _df_itens = run_query(
                                'SELECT referencia as Ref, descricao as Produto, quantidade as Qtd, valor_unitario as VlUnit, valor_total as Total FROM itens_historico_legado WHERE cliente_codigo=%s AND documento=%s ORDER BY referencia',
                                [_cod_cli, _doc]
                            )
                            if not _df_itens.empty:
                                st.markdown('**Produtos:**')
                                st.dataframe(_df_itens, use_container_width=True, hide_index=True,
                                    column_config={
                                        'VlUnit': st.column_config.NumberColumn('Vl.Unit', format='R$ %.2f'),
                                        'Total': st.column_config.NumberColumn('Total', format='R$ %.2f'),
                                    })
                            else:
                                st.caption('Produtos não disponíveis para esta duplicata.')
                            # Observacao
                            _obs_doc = _rows_doc['observacao'].iloc[0] if 'observacao' in _rows_doc.columns and _rows_doc['observacao'].iloc[0] else ''
                            if _obs_doc:
                                st.caption(f'📝 Obs: {_obs_doc}')
        except Exception as e:
            st.error(f"Erro na consulta: {e}")
            import traceback
            st.code(traceback.format_exc())

elif pagina == "📒 Cadastros":
    if _role == "vendas":
        st.error("🔒 Área restrita — somente administradores.")
        st.stop()

    st.markdown("## 📒 Central de Cadastros")

    run_command("""
        CREATE TABLE IF NOT EXISTS clientes (
            id BIGSERIAL PRIMARY KEY, nome TEXT NOT NULL,
            cpf TEXT, whatsapp TEXT, email TEXT,
            endereco TEXT, observacoes TEXT, ativo BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    run_command("ALTER TABLE clientes ADD COLUMN IF NOT EXISTS data_nascimento DATE")
    run_command("ALTER TABLE clientes ADD COLUMN IF NOT EXISTS cep VARCHAR(9)")
    run_command("ALTER TABLE clientes ADD COLUMN IF NOT EXISTS logradouro TEXT")
    run_command("ALTER TABLE clientes ADD COLUMN IF NOT EXISTS bairro TEXT")
    run_command("ALTER TABLE clientes ADD COLUMN IF NOT EXISTS cidade TEXT")
    run_command("ALTER TABLE clientes ADD COLUMN IF NOT EXISTS estado VARCHAR(2)")
    run_command("ALTER TABLE clientes ADD COLUMN IF NOT EXISTS complemento TEXT")

    _cad_t1, _cad_t2, _cad_t3 = st.tabs(
        ["👥 Clientes", "🏭 Fornecedores & Prestadores", "💡 Utilidades"]
    )

    # ── ABA CLIENTES ─────────────────────────────────────────────────────────
    with _cad_t1:
        # KPIs
        _df_cli_kpi = run_query("""
            SELECT
              COUNT(*) FILTER (WHERE ativo = true) AS total_ativos,
              COUNT(*) FILTER (WHERE ativo = true AND created_at >= NOW() - INTERVAL '30 days') AS novos_mes,
              COUNT(*) AS total_geral
            FROM clientes
        """)
        _df_inad_cnt = run_query("""
            SELECT COUNT(DISTINCT nome_cliente) AS inadimplentes
            FROM duplicatas_abertas
            WHERE status = 'Pendente' AND dt_vencimento < CURRENT_DATE
        """)
        _kc1, _kc2, _kc3, _kc4 = st.columns(4)
        _kc1.metric("👥 Total Clientes", int(_df_cli_kpi["total_geral"].iloc[0]) if not _df_cli_kpi.empty else 0)
        _kc2.metric("✅ Ativos",          int(_df_cli_kpi["total_ativos"].iloc[0]) if not _df_cli_kpi.empty else 0)
        _kc3.metric("🆕 Novos (30d)",    int(_df_cli_kpi["novos_mes"].iloc[0]) if not _df_cli_kpi.empty else 0)
        _kc4.metric("⚠️ Inadimplentes",  int(_df_inad_cnt["inadimplentes"].iloc[0]) if not _df_inad_cnt.empty else 0)
        st.markdown("---")

        # Busca
        _busca_cad = st.text_input("🔍 Buscar por nome, CPF ou WhatsApp", key="cad_busca",
                                    placeholder="Digite para filtrar...")

        # Lista de clientes
        _df_clis = run_query("""
            SELECT c.id::text, c.nome,
                   COALESCE(c.cpf,'') AS cpf,
                   COALESCE(c.whatsapp,'') AS whatsapp,
                   c.ativo,
                   c.created_at,
                   COUNT(v.id) AS total_compras,
                   MAX(v.created_at::date) AS ultima_compra,
                   COALESCE(SUM(v.valor_total),0) AS valor_total_compras,
                   (SELECT COALESCE(iv2.nome_produto, p2.nome, '')
                    FROM vendas v2
                    LEFT JOIN itens_venda iv2 ON iv2.venda_id = v2.id
                    LEFT JOIN produtos p2 ON p2.id = iv2.produto_id
                    WHERE v2.cliente_id = c.id
                    ORDER BY v2.created_at DESC, iv2.id DESC
                    LIMIT 1) AS ultimo_produto
            FROM clientes c
            LEFT JOIN vendas v ON v.cliente_id = c.id
            GROUP BY c.id, c.nome, c.cpf, c.whatsapp, c.ativo, c.created_at
            ORDER BY c.nome
        """)
        if not _df_clis.empty and _busca_cad.strip():
            _qb = _busca_cad.strip().lower()
            _df_clis = _df_clis[
                _df_clis["nome"].str.lower().str.contains(_qb, na=False) |
                _df_clis["cpf"].str.lower().str.contains(_qb, na=False) |
                _df_clis["whatsapp"].str.lower().str.contains(_qb, na=False)
            ]

        # Badge helpers
        import hashlib as _hlib
        _BADGE_COLORS = ["#9E5B6F","#B8892A","#5B9E8A","#5B6F9E","#9E7A5B"]
        def _avatar_color(nome):
            return _BADGE_COLORS[int(_hlib.md5(nome.encode()).hexdigest(),16) % len(_BADGE_COLORS)]
        def _iniciais(nome):
            parts = (nome or "?").split()
            return (parts[0][0] + (parts[-1][0] if len(parts)>1 else "")).upper()

        # Inadimplentes set
        _df_inad_nomes = run_query("""
            SELECT DISTINCT nome_cliente FROM duplicatas_abertas
            WHERE status='Pendente' AND dt_vencimento < CURRENT_DATE
        """)
        _inad_set = set(_df_inad_nomes["nome_cliente"].str.strip().str.lower().tolist()) if not _df_inad_nomes.empty else set()

        st.caption(f"{len(_df_clis)} cliente(s)")
        _all_clis = list(_df_clis.iterrows()) + [None]
        for _ri in range(0, len(_all_clis), 3):
            _row_clis = _all_clis[_ri:_ri+3]
            _ccols = st.columns(3)
            for _ci, _item in enumerate(_row_clis):
                with _ccols[_ci]:
                    if _item is None:
                        st.markdown(
                            '<div style="border:2px dashed #9E5B6F;border-radius:10px;'
                            'display:flex;align-items:center;justify-content:center;height:140px;">'
                            '<span style="font-size:40px;color:#9E5B6F;">＋</span></div>',
                            unsafe_allow_html=True
                        )
                        if st.button("➕ Novo Cliente", key=f"btn_new_cli_{_ri}", use_container_width=True):
                            st.session_state["cad_form_novo"] = True
                            st.rerun()
                        continue
                    _, _cr = _item
                    _cid = str(_cr["id"])
                    _cnome = str(_cr["nome"] or "—")
                    _ccpf  = str(_cr["cpf"] or "")
                    _cwpp  = str(_cr["whatsapp"] or "")
                    _ccomp = int(_cr["total_compras"] or 0)
                    _culc  = str(_cr["ultima_compra"] or "—")
                    _ctot  = float(_cr["valor_total_compras"] or 0)
                    _cumprod = str(_cr.get("ultimo_produto") or "")
                    _cdt   = _cr.get("created_at")
                    _cor   = _avatar_color(_cnome)
                    _ini   = _iniciais(_cnome)
                    _is_inad = _cnome.strip().lower() in _inad_set
                    _is_vip  = _ccomp >= 5 or _ctot > 500
                    import datetime as _dtnow_c
                    _is_novo = False
                    if _cdt is not None:
                        try:
                            _dtnow_c2 = _dtnow_c.date.today()
                            _dt_c = _cdt.date() if hasattr(_cdt, "date") else _cdt
                            _is_novo = (_dtnow_c2 - _dt_c).days <= 30
                        except Exception:
                            pass
                    _badges = ""
                    if _is_inad: _badges += '<span style="background:#8B0000;color:#fff;padding:1px 6px;border-radius:8px;font-size:10px;margin-right:3px;">Inadimplente</span>'
                    if _is_vip and not _is_inad: _badges += '<span style="background:#B8892A;color:#fff;padding:1px 6px;border-radius:8px;font-size:10px;margin-right:3px;">⭐ VIP</span>'
                    if _is_novo: _badges += '<span style="background:#2E7D32;color:#fff;padding:1px 6px;border-radius:8px;font-size:10px;">Novo</span>'
                    _cpf_mask = (
                        f"{_ccpf[:3]}.***.***-{_ccpf[-2:]}" if len(re.sub(r"\D","",_ccpf)) == 11
                        else _ccpf[:6]+"***" if _ccpf else "—"
                    )
                    _wpp_raw = re.sub(r"\D","",_cwpp)
                    _wpp_link = f"https://wa.me/55{_wpp_raw}" if _wpp_raw else "#"
                    st.markdown(
                        f'<div style="border:1px solid #E8D5C4;border-radius:10px;padding:12px;margin-bottom:4px;">'
                        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">'
                        f'<div style="background:{_cor};color:#fff;border-radius:50%;width:40px;height:40px;'
                        f'display:flex;align-items:center;justify-content:center;font-weight:800;font-size:15px;">{_ini}</div>'
                        f'<div><b style="font-size:14px;">{_cnome}</b><br>'
                        f'<span style="font-size:11px;color:#888;">{_cpf_mask}</span></div></div>'
                        f'<div style="font-size:12px;color:#555;">'
                        f'📱 <a href="{_wpp_link}" target="_blank" style="color:#25D366;">{_cwpp or "—"}</a><br>'
                        f'🛒 {_ccomp} compra(s) · R$ {_ctot:,.0f}<br>'
                        f'📅 Última: {_culc}'
                        + (f'<br>🏷️ {_cumprod[:30]}' if _cumprod else '')
                        + '</div>'
                        f'<div style="margin-top:5px;">{_badges}</div></div>',
                        unsafe_allow_html=True
                    )
                    _ba, _bb, _bc = st.columns(3)
                    if _ba.button("📋 Histórico", key=f"cli_hist_{_cid}", use_container_width=True):
                        st.session_state[f"cad_hist_{_cid}"] = not st.session_state.get(f"cad_hist_{_cid}", False)
                        st.session_state[f"cad_edit_{_cid}"] = False
                    if _cwpp and _bb.button("💬 WhatsApp", key=f"cli_wpp_{_cid}", use_container_width=True):
                        _wn = re.sub(r"\D","",_cwpp)
                        st.markdown(f"[↗ Abrir no WhatsApp](https://wa.me/55{_wn})", unsafe_allow_html=True)
                    if _bc.button("✏️ Editar", key=f"cli_edit_btn_{_cid}", use_container_width=True):
                        st.session_state[f"cad_edit_{_cid}"] = not st.session_state.get(f"cad_edit_{_cid}", False)
                        st.session_state[f"cad_hist_{_cid}"] = False
                    if st.session_state.get(f"cad_edit_{_cid}", False):
                        _df_cli_ed = run_query(
                            f"SELECT nome,cpf,whatsapp,email,endereco,observacoes,"
                            f"data_nascimento,cep,logradouro,bairro,cidade,estado,complemento "
                            f"FROM clientes WHERE id={int(_cid)}"
                        )
                        if not _df_cli_ed.empty:
                            _ed = _df_cli_ed.iloc[0]
                            _ESTADOS_BR_ED = ["","AC","AL","AP","AM","BA","CE","DF","ES","GO",
                                              "MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ",
                                              "RN","RS","RO","RR","SC","SP","SE","TO"]
                            # ── CEP lookup fora do form ───────────────────────
                            _ed_cep_c1, _ed_cep_c2 = st.columns([3, 1])
                            _ed_cep_key = f"edit_cep_{_cid}_input"
                            _ed_cep_val = _ed_cep_c1.text_input(
                                "CEP", placeholder="00000-000", key=_ed_cep_key,
                                value=st.session_state.get(f"edit_cep_{_cid}",
                                      str(_ed["cep"] or ""))
                            )
                            if _ed_cep_c2.button("🔍 Buscar", key=f"edit_cep_btn_{_cid}",
                                                  use_container_width=True):
                                _ed_limpo = re.sub(r"\D", "", _ed_cep_val)
                                if len(_ed_limpo) == 8:
                                    _ed_data = buscar_cep(_ed_limpo)
                                    if _ed_data:
                                        st.session_state[f"edit_cep_{_cid}"]        = _ed_limpo
                                        st.session_state[f"edit_log_{_cid}"]        = _ed_data.get("logradouro", "")
                                        st.session_state[f"edit_bairro_{_cid}"]     = _ed_data.get("bairro", "")
                                        st.session_state[f"edit_cidade_{_cid}"]     = _ed_data.get("localidade", "")
                                        st.session_state[f"edit_estado_{_cid}"]     = _ed_data.get("uf", "")
                                        st.rerun()
                                    else:
                                        st.warning("CEP não encontrado.")
                                else:
                                    st.warning("CEP inválido.")
                            # ── Form ─────────────────────────────────────────
                            with st.form(f"form_edit_cli_{_cid}"):
                                _e1, _e2 = st.columns(2)
                                _ed_nome = _e1.text_input("Nome *", value=str(_ed["nome"] or ""))
                                _ed_cpf  = _e2.text_input("CPF",  value=str(_ed["cpf"] or ""))
                                _e3, _e4 = st.columns(2)
                                _ed_wpp  = _e3.text_input("📱 WhatsApp", value=str(_ed["whatsapp"] or ""))
                                _ed_email= _e4.text_input("📧 Email",    value=str(_ed["email"] or ""))
                                st.markdown("**📍 Endereço**")
                                _ea1, _ea2 = st.columns([2, 1])
                                _ed_log = _ea1.text_input("Logradouro e Nº",
                                    value=st.session_state.get(f"edit_log_{_cid}", str(_ed["logradouro"] or "")),
                                    placeholder="Rua X, 123")
                                _ed_bairro = _ea2.text_input("Bairro",
                                    value=st.session_state.get(f"edit_bairro_{_cid}", str(_ed["bairro"] or "")),
                                    placeholder="Centro")
                                _eb1, _eb2, _eb3 = st.columns([2, 1, 1])
                                _ed_cidade = _eb1.text_input("Cidade",
                                    value=st.session_state.get(f"edit_cidade_{_cid}", str(_ed["cidade"] or "")),
                                    placeholder="Itaúna")
                                _ed_est_cur = st.session_state.get(f"edit_estado_{_cid}", str(_ed["estado"] or ""))
                                _ed_est_idx = _ESTADOS_BR_ED.index(_ed_est_cur) if _ed_est_cur in _ESTADOS_BR_ED else 0
                                _ed_estado  = _eb2.selectbox("UF", _ESTADOS_BR_ED, index=_ed_est_idx)
                                _ed_compl   = _eb3.text_input("Complemento",
                                    value=str(_ed["complemento"] or ""), placeholder="Apto 101")
                                _ed_nasc = st.date_input("🎂 Nascimento",
                                    value=_ed["data_nascimento"] if _ed["data_nascimento"] is not None else None,
                                    min_value=date(1900, 1, 1), max_value=date.today(),
                                    key=f"ed_nasc_{_cid}", format="DD/MM/YYYY")
                                _ed_obs  = st.text_area("💬 Observações",
                                    value=str(_ed["observacoes"] or ""), height=60)
                                _esv, _ecn = st.columns(2)
                                _ed_save   = _esv.form_submit_button("✅ Salvar", use_container_width=True)
                                _ed_cancel = _ecn.form_submit_button("❌ Cancelar", use_container_width=True)
                                if _ed_cancel:
                                    for _ek in [f"edit_cep_{_cid}", f"edit_log_{_cid}",
                                                f"edit_bairro_{_cid}", f"edit_cidade_{_cid}",
                                                f"edit_estado_{_cid}"]:
                                        st.session_state.pop(_ek, None)
                                    st.session_state[f"cad_edit_{_cid}"] = False
                                    st.rerun()
                                if _ed_save:
                                    if not _ed_nome.strip():
                                        st.error("Nome obrigatório.")
                                    else:
                                        _ed_cep_salvo = re.sub(r"\D", "",
                                            st.session_state.get(f"edit_cep_{_cid}",
                                            str(_ed["cep"] or ""))) or None
                                        _ed_end_legado = ", ".join(filter(None, [
                                            _ed_log.strip(), _ed_bairro.strip(),
                                            _ed_cidade.strip(), _ed_estado
                                        ])) or None
                                        run_command(
                                            "UPDATE clientes SET nome=%s, cpf=%s, whatsapp=%s, "
                                            "email=%s, endereco=%s, cep=%s, logradouro=%s, "
                                            "bairro=%s, cidade=%s, estado=%s, complemento=%s, "
                                            "observacoes=%s, data_nascimento=%s WHERE id=%s",
                                            (_ed_nome.strip(), _ed_cpf.strip() or None,
                                             _ed_wpp.strip() or None, _ed_email.strip() or None,
                                             _ed_end_legado, _ed_cep_salvo,
                                             _ed_log.strip() or None, _ed_bairro.strip() or None,
                                             _ed_cidade.strip() or None, _ed_estado or None,
                                             _ed_compl.strip() or None,
                                             _ed_obs.strip() or None, _ed_nasc, int(_cid))
                                        )
                                        for _ek in [f"edit_cep_{_cid}", f"edit_log_{_cid}",
                                                    f"edit_bairro_{_cid}", f"edit_cidade_{_cid}",
                                                    f"edit_estado_{_cid}"]:
                                            st.session_state.pop(_ek, None)
                                        st.success(f"✅ {_ed_nome.strip()} atualizado!")
                                        st.session_state[f"cad_edit_{_cid}"] = False
                                        st.rerun()
                    if st.session_state.get(f"cad_hist_{_cid}", False):
                        _df_ch = run_query(f"""
                            SELECT TO_CHAR(v.created_at,'DD/MM/YYYY') AS Data,
                                   v.valor_total AS Valor,
                                   v.forma_pagamento AS Pagamento,
                                   v.status AS Status
                            FROM vendas v WHERE v.cliente_id = '{_cid}'::bigint
                            ORDER BY v.created_at DESC LIMIT 10
                        """)
                        if not _df_ch.empty:
                            st.dataframe(_df_ch, use_container_width=True, hide_index=True)
                        else:
                            st.caption("Sem compras registradas.")

        # Form novo cliente
        if st.session_state.get("cad_form_novo", False):
            st.markdown("---")
            st.markdown("#### ➕ Novo Cliente")
            _ESTADOS_BR = ["","AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS",
                           "MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"]
            # ── CEP lookup (fora do form para poder dar rerun) ────────────────
            st.markdown("#### 📍 Endereço")
            _nc_cep_c1, _nc_cep_c2, _nc_cep_spacer = st.columns([1.5, 1, 4])
            _nc_cep_val = _nc_cep_c1.text_input("CEP", placeholder="00000-000",
                                                 key="new_cli_cep_input", max_chars=9,
                                                 value=st.session_state.get("new_cli_cep", ""))
            _nc_cep_c2.markdown("<br>", unsafe_allow_html=True)
            if _nc_cep_c2.button("🔍 Buscar", key="new_cli_cep_btn", use_container_width=True):
                _nc_limpo = re.sub(r"\D", "", _nc_cep_val)
                if len(_nc_limpo) == 8:
                    _nc_data = buscar_cep(_nc_limpo)
                    if _nc_data:
                        st.session_state["new_cli_cep"]        = _nc_limpo
                        st.session_state["new_cli_logradouro"] = _nc_data.get("logradouro", "")
                        st.session_state["new_cli_bairro"]     = _nc_data.get("bairro", "")
                        st.session_state["new_cli_cidade"]     = _nc_data.get("localidade", "")
                        st.session_state["new_cli_estado"]     = _nc_data.get("uf", "")
                        st.rerun()
                    else:
                        st.warning("CEP não encontrado.")
                else:
                    st.warning("Digite um CEP válido com 8 dígitos.")
            # ── Form principal ────────────────────────────────────────────────
            with st.form("form_novo_cliente_cad"):
                _fn1, _fn2 = st.columns(2)
                _fnome = _fn1.text_input("Nome *", placeholder="Nome completo")
                _fcpf  = _fn2.text_input("CPF", placeholder="000.000.000-00")
                _fw1, _fw2 = st.columns(2)
                _fwpp  = _fw1.text_input("📱 WhatsApp *", placeholder="37 99999-9999")
                _femail= _fw2.text_input("📧 Email", placeholder="email@exemplo.com")
                _fa1, _fa2 = st.columns([2, 1])
                _f_log_num = _fa1.text_input("Logradouro e Nº",
                                              value=st.session_state.get("new_cli_logradouro", ""),
                                              placeholder="Rua X, 123")
                _f_bairro  = _fa2.text_input("Bairro",
                                              value=st.session_state.get("new_cli_bairro", ""),
                                              placeholder="Centro")
                _fb1, _fb2, _fb3 = st.columns([2, 1, 1])
                _f_cidade  = _fb1.text_input("Cidade",
                                              value=st.session_state.get("new_cli_cidade", ""),
                                              placeholder="Itaúna")
                _f_est_idx = _ESTADOS_BR.index(st.session_state.get("new_cli_estado", "")) \
                             if st.session_state.get("new_cli_estado", "") in _ESTADOS_BR else 0
                _f_estado  = _fb2.selectbox("UF", _ESTADOS_BR, index=_f_est_idx)
                _f_compl   = _fb3.text_input("Complemento", placeholder="Apto 101")
                _fndt  = st.date_input("🎂 Data de Nascimento", value=None,
                                       min_value=date(1900, 1, 1), max_value=date.today(),
                                       format="DD/MM/YYYY", key="cad_nasc")
                _fobs  = st.text_area("💬 Observações", height=60)
                _fsb1, _fsb2 = st.columns(2)
                _fsave = _fsb1.form_submit_button("✅ Salvar", use_container_width=True)
                _fcan  = _fsb2.form_submit_button("❌ Cancelar", use_container_width=True)
                if _fcan:
                    for _k in ["new_cli_cep","new_cli_logradouro","new_cli_bairro",
                                "new_cli_cidade","new_cli_estado"]:
                        st.session_state.pop(_k, None)
                    st.session_state["cad_form_novo"] = False
                    st.rerun()
                if _fsave:
                    if not _fnome.strip():
                        st.error("Nome obrigatório.")
                    else:
                        _cep_salvo = re.sub(r"\D", "", st.session_state.get("new_cli_cep", "")) or None
                        _end_legado = ", ".join(filter(None, [
                            _f_log_num.strip(), _f_bairro.strip(),
                            _f_cidade.strip(), _f_estado
                        ])) or None
                        run_command(
                            "INSERT INTO clientes (nome, cpf, whatsapp, email, endereco, "
                            "cep, logradouro, bairro, cidade, estado, complemento, "
                            "observacoes, data_nascimento) "
                            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                            (_fnome.strip(), _fcpf.strip() or None,
                             _fwpp.strip() or None, _femail.strip() or None,
                             _end_legado, _cep_salvo,
                             _f_log_num.strip() or None, _f_bairro.strip() or None,
                             _f_cidade.strip() or None, _f_estado or None,
                             _f_compl.strip() or None,
                             _fobs.strip() or None, _fndt)
                        )
                        for _k in ["new_cli_cep","new_cli_logradouro","new_cli_bairro",
                                    "new_cli_cidade","new_cli_estado"]:
                            st.session_state.pop(_k, None)
                        st.success(f"✅ {_fnome.strip()} cadastrado!")
                        st.session_state["cad_form_novo"] = False
                        st.rerun()

    # ── ABA FORNECEDORES & PRESTADORES ──────────────────────────────────────
    with _cad_t2:
        st.markdown("#### 🏭 Fornecedores, Prestadores & Utilidades")
        _fpag_sub1, _fpag_sub2, _fpag_sub3 = st.tabs(
            ["🏭 Fornecedores", "🔧 Prestadores de Serviço", "💡 Utilidades/Contas Fixas"]
        )
        with _fpag_sub1:
            _render_lista_forn_pag("Fornecedor")
            _form_novo_forn_pag("Fornecedor")
        with _fpag_sub2:
            _render_lista_forn_pag("Prestador de Serviço")
            _form_novo_forn_pag("Prestador de Serviço")
        with _fpag_sub3:
            _render_lista_forn_pag("Utilidade/Conta Fixa")
            _form_novo_forn_pag("Utilidade/Conta Fixa")

    # ── ABA UTILIDADES ───────────────────────────────────────────────────────
    with _cad_t3:
        st.markdown("#### 💡 Contas Fixas Mensais")
        run_command("""
            CREATE TABLE IF NOT EXISTS contas_fixas_mensais (
                id BIGSERIAL PRIMARY KEY,
                descricao TEXT NOT NULL,
                categoria TEXT,
                valor NUMERIC(10,2),
                dia_vencimento INT,
                ativo BOOLEAN DEFAULT TRUE
            )
        """)
        _df_cfm = run_query(
            "SELECT id, descricao, categoria, valor, dia_vencimento, ativo "
            "FROM contas_fixas_mensais ORDER BY dia_vencimento"
        )
        if not _df_cfm.empty:
            st.dataframe(_df_cfm, use_container_width=True, hide_index=True)
            _tot_fix = float(_df_cfm[_df_cfm["ativo"] == True]["valor"].sum())
            st.metric("💰 Total Mensal Fixo", f"R$ {_tot_fix:,.2f}")
        else:
            st.info("Nenhuma conta fixa cadastrada.")

        with st.expander("➕ Adicionar Conta Fixa"):
            with st.form("form_conta_fixa"):
                _cf1, _cf2 = st.columns(2)
                _cf_desc = _cf1.text_input("Descrição *", placeholder="Ex: Aluguel, Cemig, Internet")
                _cf_cat  = _cf2.text_input("Categoria",  placeholder="Utilidade, Infraestrutura...")
                _cf3, _cf4 = st.columns(2)
                _cf_val  = _cf3.number_input("Valor (R$)", min_value=0.0, step=10.0)
                _cf_dia  = _cf4.number_input("Dia de Vencimento", min_value=1, max_value=31, value=10)
                if st.form_submit_button("✅ Salvar", use_container_width=True):
                    if _cf_desc.strip():
                        run_command(
                            "INSERT INTO contas_fixas_mensais (descricao, categoria, valor, dia_vencimento) VALUES (%s,%s,%s,%s)",
                            (_cf_desc.strip(), _cf_cat.strip() or None, _cf_val, int(_cf_dia))
                        )
                        st.success("✅ Salvo!")
                        st.rerun()
                    else:
                        st.error("Descrição obrigatória.")

elif pagina == "👤 Equipe":
    if _role == "vendas":
        st.error("🔒 Área restrita — somente administradores.")
        st.stop()

    st.subheader("👥 Equipe — Metas, Comissões e Cadastros")

    # ── Auto-migrations idempotentes ─────────────────────────────────────────
    run_command("""
        CREATE TABLE IF NOT EXISTS metas_mensais (
            id         BIGSERIAL    PRIMARY KEY,
            ano_mes    TEXT         UNIQUE NOT NULL,
            meta_valor NUMERIC(12,2) NOT NULL,
            criado_em  TIMESTAMPTZ  DEFAULT NOW()
        )
    """)
    run_command("""
        CREATE TABLE IF NOT EXISTS config_comissao (
            id              BIGSERIAL PRIMARY KEY,
            codigo_vendedor TEXT      UNIQUE NOT NULL,
            nome_vendedor   TEXT,
            percentual      NUMERIC(5,2) NOT NULL DEFAULT 5.0,
            ativo           BOOLEAN  DEFAULT TRUE
        )
    """)
    run_command("""
        CREATE TABLE IF NOT EXISTS fornecedores (
            id    BIGSERIAL PRIMARY KEY,
            nome  TEXT UNIQUE NOT NULL,
            tipo  TEXT,
            ativo BOOLEAN DEFAULT TRUE
        )
    """)

    _eq_meta, _eq_com, _eq_vend, _eq_forn, _eq_perf, _eq_acc = st.tabs(
        ["🎯 Meta", "💰 Comissões", "👩 Vendedoras", "🏭 Fornecedores", "📈 Performance", "🔑 Acessos"]
    )

    # ════════════════════════════════════════════════════════
    # TAB: Meta Mensal
    # ════════════════════════════════════════════════════════
    with _eq_meta:
        hoje_g = date.today()
        _ano_mes_sel = st.selectbox(
            "Mês de referência",
            [f"{hoje_g.year}-{m:02d}" for m in range(hoje_g.month, 0, -1)],
            key="gestao_ano_mes",
        )
        _ano, _mes = int(_ano_mes_sel[:4]), int(_ano_mes_sel[5:])
        df_meta = run_query(
            f"SELECT meta_valor FROM metas_mensais WHERE ano_mes = '{_ano_mes_sel}'"
        )
        _meta_atual = float(df_meta["meta_valor"].iloc[0]) if not df_meta.empty else 0.0
        col_meta, col_set = st.columns([2, 1])
        with col_set:
            _nova_meta = st.number_input(
                "Definir Meta (R$)", min_value=0.0, value=_meta_atual,
                step=500.0, format="%.2f", key="gestao_meta_input",
            )
            if st.button("💾 Salvar Meta", key="gestao_salvar_meta", use_container_width=True):
                run_command(
                    """INSERT INTO metas_mensais (ano_mes, meta_valor)
                       VALUES (%s, %s)
                       ON CONFLICT (ano_mes) DO UPDATE SET meta_valor = EXCLUDED.meta_valor""",
                    (_ano_mes_sel, _nova_meta),
                )
                st.success(f"Meta de {_ano_mes_sel} definida: R$ {_nova_meta:,.2f}")
                st.rerun()
        df_vnd_mes = run_query(f"""
            SELECT COALESCE(SUM(valor_total), 0) AS total
            FROM vendas
            WHERE EXTRACT(YEAR  FROM data_venda) = {_ano}
              AND EXTRACT(MONTH FROM data_venda) = {_mes}
              AND status_pagamento IN ('pago', 'parcelado')
        """)
        _total_mes = float(df_vnd_mes["total"].iloc[0]) if not df_vnd_mes.empty else 0.0
        _meta_ref  = _nova_meta if _nova_meta > 0 else (_meta_atual if _meta_atual > 0 else 1.0)
        with col_meta:
            if _PLOTLY_OK and _meta_ref > 0:
                fig_gauge = _gauge_meta(_total_mes, _meta_ref)
                if fig_gauge:
                    st.plotly_chart(fig_gauge, use_container_width=True)
            else:
                pct_g = (_total_mes / _meta_ref * 100) if _meta_ref > 0 else 0
                st.metric("Progresso do Mês", f"R$ {_total_mes:,.2f}",
                          delta=f"{pct_g:.1f}% da meta")
        df_diario = run_query(f"""
            SELECT data_venda::date AS dia, SUM(valor_total) AS total_dia
            FROM vendas
            WHERE EXTRACT(YEAR  FROM data_venda) = {_ano}
              AND EXTRACT(MONTH FROM data_venda) = {_mes}
              AND status_pagamento IN ('pago', 'parcelado')
            GROUP BY dia ORDER BY dia
        """)
        if not df_diario.empty and _PLOTLY_OK:
            df_diario["acumulado"] = df_diario["total_dia"].cumsum()
            fig_line = _go.Figure()
            fig_line.add_trace(_go.Scatter(
                x=df_diario["dia"].astype(str), y=df_diario["acumulado"],
                mode="lines+markers", name="Acumulado", line=dict(color="#5bc5d3", width=2),
            ))
            fig_line.add_hline(y=_meta_ref, line_dash="dash",
                               line_color="#7B1F2E", annotation_text="Meta")
            fig_line.update_layout(
                title="Evolução Diária de Vendas",
                height=250, margin=dict(l=10, r=10, t=40, b=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                yaxis_tickprefix="R$ ", yaxis_tickformat=",.0f",
            )
            st.plotly_chart(fig_line, use_container_width=True)

    # ════════════════════════════════════════════════════════
    # TAB: Comissões
    # ════════════════════════════════════════════════════════
    with _eq_com:
        cc1, cc2, cc3 = st.columns(3)
        _dt_ini = cc1.date_input("De", value=date(date.today().year, date.today().month, 1), key="com_dt_ini")
        _dt_fim = cc2.date_input("Até", value=date.today(), key="com_dt_fim")
        _cod_fil = cc3.text_input("Código vendedor (vazio = todos)", key="com_cod_fil", placeholder="V001")
        df_com_raw = run_query(f"""
            SELECT COALESCE(codigo_vendedor, vendedor_nome, 'N/I') AS codigo_vendedor,
                   COUNT(*) AS qtd_vendas,
                   SUM(valor_total) AS total_vendido,
                   AVG(valor_total) AS ticket_medio
            FROM vendas
            WHERE data_venda::date BETWEEN '{_dt_ini}' AND '{_dt_fim}'
              AND status_pagamento IN ('pago', 'parcelado')
            GROUP BY COALESCE(codigo_vendedor, vendedor_nome, 'N/I')
            ORDER BY total_vendido DESC
        """)
        if df_com_raw.empty:
            st.info("Nenhuma venda no período.")
        else:
            if _cod_fil.strip():
                df_com_raw = df_com_raw[
                    df_com_raw["codigo_vendedor"].str.lower().str.contains(_cod_fil.strip().lower(), na=False)
                ]
            df_cfg = run_query("SELECT codigo_vendedor, percentual FROM config_comissao WHERE ativo = true")
            pct_map = {str(r["codigo_vendedor"]): float(r["percentual"]) for _, r in df_cfg.iterrows()} if not df_cfg.empty else {}
            df_com_raw["% comissão"] = df_com_raw["codigo_vendedor"].apply(lambda c: pct_map.get(str(c), 5.0))
            df_com_raw["comissão R$"] = (df_com_raw["total_vendido"] * df_com_raw["% comissão"] / 100).round(2)
            m1, m2, m3 = st.columns(3)
            m1.metric("Total vendido", f"R$ {df_com_raw['total_vendido'].sum():,.2f}")
            m2.metric("Total comissões", f"R$ {df_com_raw['comissão R$'].sum():,.2f}")
            m3.metric("Vendedores", len(df_com_raw))
            st.dataframe(
                df_com_raw.rename(columns={
                    "codigo_vendedor": "Vendedor", "qtd_vendas": "Vendas",
                    "total_vendido": "Total Vendido (R$)", "ticket_medio": "Ticket Médio (R$)",
                }).style.format({
                    "Total Vendido (R$)": "R$ {:,.2f}", "Ticket Médio (R$)": "R$ {:,.2f}",
                    "comissão R$": "R$ {:,.2f}", "% comissão": "{:.1f}%",
                }),
                use_container_width=True, hide_index=True,
            )
            st.markdown("---")
            st.markdown("##### 💸 Pagar Comissão")
            st.markdown("""
<style>
/* Botão Pagar Comissão — padrão Enterprise branco */
[data-testid="stFormSubmitButton"].pagar-com button,
.pagar-com-btn button {
    background: #2e7d32 !important;
    border-color: #2e7d32 !important;
    color: #fff !important;
    font-weight: 800 !important;
    border-radius: 20px !important;
}
.pagar-com-btn button:hover {
    background: #388e3c !important;
    color: #fff !important;
}
</style>
""", unsafe_allow_html=True)
            with st.form("eq_pagar_comissao"):
                _pc1, _pc2, _pc3 = st.columns([2, 2, 2])
                _vend_pag = _pc1.text_input("Código vendedor *", placeholder="V001")
                _valor_pag = _pc2.number_input("Valor a pagar (R$)", min_value=0.0, value=0.0, format="%.2f")
                _obs_pag = _pc3.text_input("Observação", placeholder="Comissão Março/2026")
                st.markdown('<div class="pagar-com-btn">', unsafe_allow_html=True)
                _pag_sub = st.form_submit_button(
                    "💸 Confirmar Pagamento de Comissão", use_container_width=True
                )
                st.markdown("</div>", unsafe_allow_html=True)
                if _pag_sub:
                    if not _vend_pag.strip() or _valor_pag <= 0:
                        st.error("Informe o código do vendedor e um valor maior que zero.")
                    else:
                        run_command(
                            "INSERT INTO config_geral (chave, valor, atualizado_em) "
                            "VALUES (%s, %s, NOW()) ON CONFLICT (chave) "
                            "DO UPDATE SET valor = EXCLUDED.valor, atualizado_em = NOW()",
                            (f"COM_PAGO_{_vend_pag.strip().upper()}_{date.today().strftime('%Y%m')}",
                             f"{_valor_pag:.2f} — {_obs_pag.strip() or 'sem obs'}"),
                        )
                        st.success(
                            f"✅ Comissão de **R$ {_valor_pag:,.2f}** registrada para "
                            f"**{_vend_pag.strip().upper()}**."
                        )
                        st.rerun()

    # ════════════════════════════════════════════════════════
    # TAB: Vendedoras
    # ════════════════════════════════════════════════════════
    with _eq_vend:
        st.caption("Cadastre as vendedoras. O **Código** alimenta o seletor obrigatório no PDV.")
        df_vend_adm = run_query(
            "SELECT id, codigo_vendedor, nome_vendedor, percentual, ativo "
            "FROM config_comissao ORDER BY codigo_vendedor"
        )
        if not df_vend_adm.empty:
            hv1, hv2, hv3, hv4, hv5 = st.columns([1.2, 2.2, 1.2, 1, 1.2])
            hv1.markdown("**Código**"); hv2.markdown("**Nome**")
            hv3.markdown("**Comissão %**"); hv4.markdown("**Ativo**"); hv5.markdown("")
            st.markdown("<hr style='margin:4px 0 8px'>", unsafe_allow_html=True)
            for _, vr in df_vend_adm.iterrows():
                cv1, cv2, cv3, cv4, cv5 = st.columns([1.2, 2.2, 1.2, 1, 1.2])
                cv1.write(vr["codigo_vendedor"])
                cv2.write(vr["nome_vendedor"] or "—")
                cv3.write(f"{float(vr['percentual']):.1f}%")
                cv4.write("✅" if vr["ativo"] else "❌")
                _vat_lbl = "Inativar" if vr["ativo"] else "Ativar"
                if cv5.button(_vat_lbl, key=f"eq_vend_tog_{vr['id']}", use_container_width=True):
                    run_command("UPDATE config_comissao SET ativo = NOT ativo WHERE id = %s", (int(vr["id"]),))
                    st.rerun()
        else:
            st.info("Nenhuma vendedora cadastrada.")
        st.markdown("---")
        with st.form("form_add_vend_eq"):
            va1, va2, va3 = st.columns([1.5, 2, 1.2])
            _vc = va1.text_input("Código *", placeholder="V001")
            _vn = va2.text_input("Nome *", placeholder="Maria Silva")
            _vp = va3.number_input("Comissão (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)
            if st.form_submit_button("💾 Salvar Vendedora", use_container_width=True):
                if not _vc.strip() or not _vn.strip():
                    st.error("Código e Nome são obrigatórios.")
                else:
                    run_command(
                        "INSERT INTO config_comissao (codigo_vendedor, nome_vendedor, percentual) "
                        "VALUES (%s, %s, %s) ON CONFLICT (codigo_vendedor) "
                        "DO UPDATE SET nome_vendedor = EXCLUDED.nome_vendedor, "
                        "percentual = EXCLUDED.percentual",
                        (_vc.strip(), _vn.strip(), _vp),
                    )
                    st.success(f"Vendedora **{_vn.strip()}** ({_vc.strip()}) salva!")
                    st.rerun()

    # ════════════════════════════════════════════════════════
    # TAB: Fornecedores / Prestadores / Utilidades
    # ════════════════════════════════════════════════════════
    with _eq_forn:
        st.markdown("### 🏭 Fornecedores, Prestadores & Utilidades")
        _tf1, _tf2, _tf3 = st.tabs(["🏭 Fornecedores", "🔧 Prestadores de Serviço", "💡 Utilidades/Contas Fixas"])

        def _render_lista_forn(tipo_filtro):
            import base64 as _b64fc
            df_fl = run_query("SELECT id, nome, tipo, cnpj_cpf, whatsapp1, whatsapp2, instagram1, instagram2, email, endereco, referencia, observacoes, ativo, foto_cartao, foto_cartao_nome FROM fornecedores WHERE tipo = %s ORDER BY nome", params=(tipo_filtro,))
            _busca = st.text_input("🔍 Buscar", key=f"busca_{tipo_filtro}", placeholder="Nome, referência...")
            if not df_fl.empty:
                if _busca.strip():
                    _qb = _busca.strip().lower()
                    df_fl = df_fl[df_fl["nome"].str.lower().str.contains(_qb, na=False) | df_fl["referencia"].fillna("").str.lower().str.contains(_qb, na=False)]
                st.caption(f"{len(df_fl)} registro(s)")
            _sf_key = f"sf_{tipo_filtro.replace(' ','_').replace('/','_')}"
            _records = [] if df_fl.empty else list(df_fl.iterrows())
            _all_items = _records + [None]
            for _ri in range(0, len(_all_items), 3):
                _row_items = _all_items[_ri:_ri + 3]
                _cols = st.columns(3)
                for _ci, _item in enumerate(_row_items):
                    with _cols[_ci]:
                        if _item is None:
                            st.markdown('<div style="background:#1A2035;border:2px dashed #C9A227;border-radius:10px;display:flex;align-items:center;justify-content:center;height:120px;"><span style="font-size:40px;color:#C9A227;">＋</span></div>', unsafe_allow_html=True)
                            if st.button("➕ Novo cadastro", key=f"add_{tipo_filtro}_{_ri}", use_container_width=True):
                                st.session_state[_sf_key] = True
                                st.rerun()
                            continue
                        _, fr = _item
                        _fid = int(fr["id"])
                        _fc_raw = fr.get("foto_cartao")
                        _has_foto = _fc_raw is not None and len(bytes(_fc_raw)) > 0
                        _fc_b64 = _b64fc.b64encode(bytes(_fc_raw)).decode() if _has_foto else ""
                        _badge = '<span style="position:absolute;top:8px;right:8px;background:#C9A227;color:#000;padding:2px 7px;border-radius:10px;font-size:10px;font-weight:700;">Cartão</span>' if _has_foto else ""
                        _hdr = f'<img src="data:image/jpeg;base64,{_fc_b64}" style="width:100%;height:120px;object-fit:cover;">' if _has_foto else '<div style="display:flex;align-items:center;justify-content:center;height:120px;font-size:44px;color:#C9A227;">👕</div>'
                        _n = str(fr["nome"] or "—").replace("<", "&lt;").replace(">", "&gt;")
                        _r = str(fr["referencia"] or fr.get("endereco") or "—").replace("<", "&lt;").replace(">", "&gt;")
                        _w = str(fr["whatsapp1"] or "—").replace("<", "&lt;").replace(">", "&gt;")
                        _g = str(fr["instagram1"] or "—").replace("<", "&lt;").replace(">", "&gt;")
                        _ob = str(fr["observacoes"] or "").strip().replace("<", "&lt;").replace(">", "&gt;")
                        _obs_div = f'<div style="background:#1F2937;border-radius:4px;padding:4px 7px;margin-top:5px;font-size:11px;color:#9CA3AF;">{_ob}</div>' if _ob else ""
                        st.markdown(f'<div style="position:relative;background:#1A2035;border-radius:10px 10px 0 0;overflow:hidden;height:120px;">{_hdr}{_badge}</div><div style="background:#0E1117;border:1px solid #1F2937;border-top:none;border-radius:0 0 10px 10px;padding:10px 10px 6px;margin-bottom:4px;"><p style="font-weight:700;font-size:14px;margin:0 0 2px 0;color:#FFF;">{_n}</p><p style="color:#9CA3AF;font-size:12px;margin:0 0 4px 0;">{_r}</p><p style="margin:0 0 1px 0;font-size:12px;color:#25D366;">📱 {_w}</p><p style="margin:0 0 1px 0;font-size:12px;color:#C9A227;">📸 {_g}</p>{_obs_div}</div>', unsafe_allow_html=True)
                        _ba, _bb = st.columns(2)
                        if _ba.button("💬 WhatsApp", key=f"wa_{tipo_filtro}_{_fid}", use_container_width=True, disabled=not fr["whatsapp1"]):
                            _wn = str(fr["whatsapp1"]).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
                            st.markdown(f"[↗ Abrir no WhatsApp](https://wa.me/55{_wn})", unsafe_allow_html=True)
                        if _bb.button("🪪 Ver Cartão", key=f"vcbtn_{tipo_filtro}_{_fid}", use_container_width=True, disabled=not _has_foto):
                            _dialog_ver_cartao(str(fr["nome"] or "—"), bytes(_fc_raw) if _has_foto else None, str(fr.get("foto_cartao_nome") or "foto.jpg"))
                        _bc, _bd = st.columns(2)
                        if _bc.button("✏️ Editar", key=f"ed_{tipo_filtro}_{_fid}", use_container_width=True):
                            st.session_state[f"edit_{tipo_filtro}_{_fid}"] = not st.session_state.get(f"edit_{tipo_filtro}_{_fid}", False)
                        if _bd.button("🗑️ Excluir", key=f"del_{tipo_filtro}_{_fid}", use_container_width=True):
                            run_command("DELETE FROM fornecedores WHERE id = %s", (_fid,))
                            st.rerun()
            for _, fr in df_fl.iterrows():
                _fid = int(fr["id"])
                if st.session_state.get(f"edit_{tipo_filtro}_{_fid}", False):
                    st.markdown(f"---\n#### ✏️ Editar: **{fr['nome']}**")
                    with st.form(f"ef_{tipo_filtro}_{_fid}"):
                        _en1, _en2 = st.columns(2)
                        _enm = _en1.text_input("Nome *", value=str(fr["nome"] or ""))
                        _ecn = _en2.text_input("CNPJ/CPF", value=str(fr["cnpj_cpf"] or ""))
                        _ew1, _ew2 = st.columns(2)
                        _ewp1 = _ew1.text_input("📱 WhatsApp 1", value=str(fr["whatsapp1"] or ""))
                        _ewp2 = _ew2.text_input("📱 WhatsApp 2", value=str(fr["whatsapp2"] or ""))
                        _ei1, _ei2 = st.columns(2)
                        _eis1 = _ei1.text_input("📸 Instagram 1", value=str(fr["instagram1"] or ""))
                        _eis2 = _ei2.text_input("📸 Instagram 2", value=str(fr["instagram2"] or ""))
                        _ee1, _ee2 = st.columns(2)
                        _eem = _ee1.text_input("📧 Email", value=str(fr["email"] or ""))
                        _erf = _ee2.text_input("🔖 Referência", value=str(fr["referencia"] or ""))
                        _eend = st.text_input("📍 Endereço", value=str(fr["endereco"] or ""))
                        _eobs = st.text_area("💬 Observações", value=str(fr["observacoes"] or ""), height=70)
                        _efp = st.file_uploader("📷 Nova foto do cartão", type=["jpg", "jpeg", "png"], key=f"efoto_{tipo_filtro}_{_fid}") if tipo_filtro == "Fornecedor" else None
                        _eat = st.checkbox("Ativo", value=bool(fr["ativo"]))
                        _es1, _es2 = st.columns(2)
                        _eok = _es1.form_submit_button("✅ Salvar", use_container_width=True)
                        _eco = _es2.form_submit_button("❌ Cancelar", use_container_width=True)
                        if _eco:
                            st.session_state[f"edit_{tipo_filtro}_{_fid}"] = False
                            st.rerun()
                        if _eok:
                            if not _enm.strip():
                                st.error("Nome obrigatório.")
                            else:
                                _efb = _efp.read() if _efp else None
                                _efn = _efp.name if _efp else None
                                if _efb:
                                    run_command("UPDATE fornecedores SET nome=%s,cnpj_cpf=%s,whatsapp1=%s,whatsapp2=%s,instagram1=%s,instagram2=%s,email=%s,referencia=%s,endereco=%s,observacoes=%s,ativo=%s,foto_cartao=%s,foto_cartao_nome=%s WHERE id=%s",
                                        (_enm.strip(), _ecn.strip() or None, _ewp1.strip() or None, _ewp2.strip() or None, _eis1.strip() or None, _eis2.strip() or None, _eem.strip() or None, _erf.strip() or None, _eend.strip() or None, _eobs.strip() or None, _eat, _efb, _efn, _fid))
                                else:
                                    run_command("UPDATE fornecedores SET nome=%s,cnpj_cpf=%s,whatsapp1=%s,whatsapp2=%s,instagram1=%s,instagram2=%s,email=%s,referencia=%s,endereco=%s,observacoes=%s,ativo=%s WHERE id=%s",
                                        (_enm.strip(), _ecn.strip() or None, _ewp1.strip() or None, _ewp2.strip() or None, _eis1.strip() or None, _eis2.strip() or None, _eem.strip() or None, _erf.strip() or None, _eend.strip() or None, _eobs.strip() or None, _eat, _fid))
                                st.success(f"✅ {_enm.strip()} atualizado!")
                                st.session_state[f"edit_{tipo_filtro}_{_fid}"] = False
                                st.rerun()

        def _form_novo_forn(tipo):
            _sf_key = f"sf_{tipo.replace(' ','_').replace('/','_')}"
            if not st.session_state.get(_sf_key, False):
                return
            st.markdown(f"---\n#### ➕ Novo {tipo}")
            with st.form(f"form_{tipo.replace(' ','_').replace('/','_')}"):
                _fn1, _fn2 = st.columns(2)
                _fnome = _fn1.text_input("Nome *", placeholder="Ex: Inovar Modas")
                _fcnpj = _fn2.text_input("CNPJ / CPF", placeholder="00.000.000/0001-00")
                _fw1, _fw2 = st.columns(2)
                _fwpp1 = _fw1.text_input("📱 WhatsApp 1", placeholder="37 99999-9999")
                _fwpp2 = _fw2.text_input("📱 WhatsApp 2", placeholder="11 99999-9999")
                _fi1, _fi2 = st.columns(2)
                _finst1 = _fi1.text_input("📸 Instagram 1", placeholder="@fornecedor")
                _finst2 = _fi2.text_input("📸 Instagram 2", placeholder="@perfil2")
                _fe1, _fe2 = st.columns(2)
                _femail = _fe1.text_input("📧 Email", placeholder="contato@empresa.com")
                _fref = _fe2.text_input("🔖 Referência", placeholder="Rua da Juta, Brás-SP")
                _fend = st.text_input("📍 Endereço", placeholder="Rua X, 000 — Bairro — Cidade/UF")
                _fobs = st.text_area("💬 Observações", placeholder="Prazo, condições especiais...", height=70)
                _ffoto = st.file_uploader("📷 Foto do cartão de visita", type=["jpg","jpeg","png"], key=f"foto_{tipo.replace(' ','_')}") if tipo == "Fornecedor" else None
                _fsb1, _fsb2 = st.columns(2)
                _fsave = _fsb1.form_submit_button(f"✅ Salvar {tipo}", use_container_width=True)
                _fcancel = _fsb2.form_submit_button("❌ Cancelar", use_container_width=True)
                if _fcancel:
                    st.session_state[_sf_key] = False
                    st.rerun()
                if _fsave:
                    if not _fnome.strip():
                        st.error("Nome obrigatório.")
                    else:
                        _foto_bytes = _ffoto.read() if _ffoto else None
                        _foto_nome = _ffoto.name if _ffoto else None
                        run_command("INSERT INTO fornecedores (nome, tipo, cnpj_cpf, whatsapp1, whatsapp2, instagram1, instagram2, email, referencia, endereco, observacoes, foto_cartao, foto_cartao_nome) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
                            (_fnome.strip(), tipo, _fcnpj.strip() or None, _fwpp1.strip() or None, _fwpp2.strip() or None, _finst1.strip() or None, _finst2.strip() or None, _femail.strip() or None, _fref.strip() or None, _fend.strip() or None, _fobs.strip() or None, _foto_bytes, _foto_nome))
                        st.success(f"✅ {_fnome.strip()} salvo!")
                        st.session_state[_sf_key] = False
                        st.rerun()

        with _tf1:
            _render_lista_forn("Fornecedor")
            _form_novo_forn("Fornecedor")
        with _tf2:
            _render_lista_forn("Prestador de Serviço")
            _form_novo_forn("Prestador de Serviço")
        with _tf3:
            st.info("💡 Em breve: lançamento automático em Contas a Pagar.")
            _render_lista_forn("Utilidade/Conta Fixa")
            _form_novo_forn("Utilidade/Conta Fixa")

    # ════════════════════════════════════════════════════════
    # TAB: Performance
    # ════════════════════════════════════════════════════════
    with _eq_perf:
        st.markdown("#### 📈 Relatório de Performance da Equipe")
        _perf_period = st.selectbox(
            "Período", ["Este mês", "Mês anterior", "Últimos 30 dias", "Últimos 90 dias"],
            key="eq_perf_period"
        )
        _hoje_p = date.today()
        if _perf_period == "Este mês":
            _p_ini = date(_hoje_p.year, _hoje_p.month, 1)
            _p_fim = _hoje_p
        elif _perf_period == "Mês anterior":
            _primeiro = date(_hoje_p.year, _hoje_p.month, 1)
            _p_fim = _primeiro - __import__("datetime").timedelta(days=1)
            _p_ini = date(_p_fim.year, _p_fim.month, 1)
        elif _perf_period == "Últimos 30 dias":
            _p_ini = _hoje_p - __import__("datetime").timedelta(days=30)
            _p_fim = _hoje_p
        else:
            _p_ini = _hoje_p - __import__("datetime").timedelta(days=90)
            _p_fim = _hoje_p
        df_perf = run_query(f"""
            SELECT COALESCE(codigo_vendedor, vendedor_nome, 'N/I') AS vendedor,
                   COUNT(*)              AS vendas,
                   SUM(valor_total)      AS total,
                   AVG(valor_total)      AS ticket,
                   MAX(valor_total)      AS maior_venda,
                   MIN(data_venda::date) AS primeira,
                   MAX(data_venda::date) AS ultima
            FROM vendas
            WHERE data_venda::date BETWEEN '{_p_ini}' AND '{_p_fim}'
              AND status_pagamento IN ('pago', 'parcelado')
            GROUP BY COALESCE(codigo_vendedor, vendedor_nome, 'N/I')
            ORDER BY total DESC
        """)
        if df_perf.empty:
            st.info("Nenhuma venda no período selecionado.")
        else:
            _pm1, _pm2, _pm3 = st.columns(3)
            _pm1.metric("Vendedores ativos", len(df_perf))
            _pm2.metric("Total do período", f"R$ {df_perf['total'].sum():,.2f}")
            _pm3.metric("Ticket médio geral", f"R$ {df_perf['total'].sum()/max(df_perf['vendas'].sum(),1):,.2f}")
            st.markdown("**Ranking de Vendedoras:**")
            for _ri, (_, _pr) in enumerate(df_perf.iterrows(), 1):
                _medal = "🥇" if _ri == 1 else ("🥈" if _ri == 2 else ("🥉" if _ri == 3 else f"{_ri}º"))
                _pc1, _pc2, _pc3, _pc4 = st.columns([0.5, 2, 2, 2])
                _pc1.markdown(f"**{_medal}**")
                _pc2.markdown(f"**{_pr['vendedor']}**")
                _pc3.metric("Total", f"R$ {float(_pr['total']):,.2f}", label_visibility="collapsed")
                _pc4.metric("Vendas", int(_pr["vendas"]), label_visibility="collapsed")

    # ════════════════════════════════════════════════════════
    # TAB: Acessos — troca de senhas
    # ════════════════════════════════════════════════════════
    with _eq_acc:
        st.markdown("#### 🔑 Gerenciar Acessos")
        st.caption(
            "Os **logins são fixos**. Aqui você pode trocar a senha de cada perfil. "
            "A nova senha vale imediatamente no próximo login."
        )

        # Tabela de contas disponíveis para alteração
        _ACC_INFO = {
            "admin":        "Administrador (Raquel)",
            "vendas":       "Vendedoras (conta compartilhada)",
            "admin_master": "Master — acesso total",
        }
        # admin_master pode trocar qualquer senha; admin pode trocar admin e vendas
        _can_change = list(_ACC_INFO.keys()) if _IS_MASTER else ["admin", "vendas"]

        # Mostra status de cada conta
        st.markdown("**Contas do sistema:**")
        for _acc_usr, _acc_label in _ACC_INFO.items():
            _df_hash = run_query(
                f"SELECT valor FROM config_geral "
                f"WHERE chave = 'AUTH_HASH_{_acc_usr}'"
            )
            _personalizada = not _df_hash.empty
            _status_txt = "🔒 senha personalizada" if _personalizada else "🔓 senha padrão"
            _c1, _c2 = st.columns([3, 1])
            _c1.markdown(f"**{_acc_label}** — login: `{_acc_usr}`")
            _c2.caption(_status_txt)

        st.markdown("---")
        st.markdown("**Alterar senha:**")

        with st.form("eq_form_trocar_senha", clear_on_submit=True):
            _ta1, _ta2 = st.columns(2)
            _acc_sel = _ta1.selectbox(
                "Conta",
                _can_change,
                format_func=lambda u: _ACC_INFO.get(u, u),
                key="acc_sel_usr",
            )
            _nova_senha = _ta2.text_input("Nova senha *", type="password", placeholder="mínimo 6 caracteres")
            _conf_senha = st.text_input("Confirmar nova senha *", type="password")
            _sub_acc = st.form_submit_button("🔑 Salvar nova senha", use_container_width=True)
            if _sub_acc:
                if not _nova_senha or len(_nova_senha) < 6:
                    st.error("A senha deve ter pelo menos 6 caracteres.")
                elif _nova_senha != _conf_senha:
                    st.error("As senhas não coincidem.")
                else:
                    _novo_hash = _h(_nova_senha)
                    _ok_acc = run_command(
                        "INSERT INTO config_geral (chave, valor, atualizado_em) "
                        "VALUES (%s, %s, NOW()) "
                        "ON CONFLICT (chave) DO UPDATE SET valor = EXCLUDED.valor, atualizado_em = NOW()",
                        (f"AUTH_HASH_{_acc_sel}", _novo_hash),
                    )
                    if _ok_acc:
                        st.success(
                            f"✅ Senha de **{_ACC_INFO.get(_acc_sel, _acc_sel)}** atualizada com sucesso!"
                        )
                    else:
                        st.error("Não foi possível salvar. Tente novamente.")

elif pagina == "⚡ JG Hub":
    if not _IS_MASTER:
        st.error("🔒 Acesso restrito ao usuário **admin_master**.")
        st.stop()

    st.subheader("⚡ JG Automations Hub")
    st.caption("Central de automação e configuração master. Acesso exclusivo Jardel.")

    _hub_logo, _hub_ia, _hub_nasa, _hub_carga = st.tabs(["🖼️ Logo", "🔑 IA & API", "🚀 NASA", "🚀 Carga Inicial"])

    # ════════════════════════════════════════════════════════
    # TAB: Logo
    # ════════════════════════════════════════════════════════
    with _hub_logo:
        st.markdown("#### 🖼️ Identidade Visual — Substituir Logo")
        st.caption("Envie um arquivo PNG ou JPG. Ele substituirá a logo na sidebar e tela de login.")
        _logo_up = st.file_uploader("Selecione a nova logo", type=["png","jpg","jpeg"], key="hub_logo_upload")
        if _logo_up is not None:
            _lb = _logo_up.read()
            try:
                os.makedirs(os.path.dirname(_LOGO_STATIC), exist_ok=True)
                for _ld in (_LOGO_PATH, _LOGO_STATIC):
                    with open(_ld, "wb") as _lf:
                        _lf.write(_lb)
                    os.chmod(_ld, 0o777)
                st.success("✅ Logo atualizada em ambos os caminhos. Atualize (F5) para ver.")
                st.session_state.pop("_logo_cache", None)
            except Exception as _le:
                st.error(f"Erro: {_le}")
        if os.path.exists(_LOGO_STATIC):
            _ls = os.path.getsize(_LOGO_STATIC)
            st.caption(f"Arquivo atual: `{_LOGO_STATIC}` — {_ls:,} bytes")
            st.image(_LOGO_STATIC, width=200)

    # ════════════════════════════════════════════════════════
    # TAB: IA & API
    # ════════════════════════════════════════════════════════
    with _hub_ia:
        st.markdown("#### 🔑 Configurações de IA & Integrações")

        # ── OpenRouter API Key (GM Homem AI / Qwen 2.5-Coder) ────────────────────
        st.markdown("##### 🤖 OpenRouter API Key (GM Homem AI — Qwen 2.5-Coder)")
        _df_or_key = run_query("SELECT valor FROM config_geral WHERE chave = 'OPENROUTER_API_KEY'")
        _or_key_db = _df_or_key["valor"].iloc[0] if not _df_or_key.empty else ""
        _or_env    = os.getenv("OPENROUTER_API_KEY", "")
        _or_ativo  = bool(_or_key_db or _or_env)
        if _or_ativo:
            _or_src = "banco de dados" if _or_key_db else ".env"
            _or_mask = (_or_key_db or _or_env)
            _or_mask = _or_mask[:6] + "•"*20 + _or_mask[-4:] if len(_or_mask) > 12 else _or_mask
            st.success(f"✅ Chave ativa (fonte: {_or_src}): `{_or_mask}`")
        else:
            st.warning("⚠️ Chave não configurada — GM Homem AI funcionará sem LLM.")
        with st.form("hub_openrouter_key"):
            _nork = st.text_input("Nova OpenRouter API Key", type="password",
                                  placeholder="sk-or-v1-...")
            if st.form_submit_button("💾 Salvar Chave OpenRouter", use_container_width=True):
                if not _nork.strip():
                    st.error("Digite a chave.")
                else:
                    run_command(
                        "INSERT INTO config_geral (chave,valor,atualizado_em) VALUES('OPENROUTER_API_KEY',%s,NOW()) "
                        "ON CONFLICT (chave) DO UPDATE SET valor=EXCLUDED.valor, atualizado_em=NOW()",
                        (_nork.strip(),),
                    )
                    os.environ["OPENROUTER_API_KEY"] = _nork.strip()
                    st.session_state["_api_keys_loaded"] = False  # forçar reload
                    st.success("✅ Chave OpenRouter salva! GM Homem AI ativada.")
                    st.rerun()
        st.markdown("---")

        # ── Gemini/Claude API Key (legado) ────────────────────────────────────
        st.markdown("##### API Key legado (Claude/Gemini)")
        _df_cfg_key = run_query("SELECT valor FROM config_geral WHERE chave = 'GEMINI_API_KEY'")
        _key_atual = _df_cfg_key["valor"].iloc[0] if not _df_cfg_key.empty else ""
        _key_mask = (_key_atual[:6] + "•"*20 + _key_atual[-4:] if len(_key_atual) > 12 else ("(não configurada)" if not _key_atual else _key_atual))
        st.caption(f"Chave atual: `{_key_mask}`")
        with st.form("hub_gemini_key"):
            _nk = st.text_input("Nova API Key", type="password", placeholder="AIza...")
            if st.form_submit_button("💾 Salvar Chave", use_container_width=True):
                if not _nk.strip():
                    st.error("Digite a chave.")
                else:
                    run_command(
                        "INSERT INTO config_geral (chave,valor,atualizado_em) VALUES('GEMINI_API_KEY',%s,NOW()) "
                        "ON CONFLICT (chave) DO UPDATE SET valor=EXCLUDED.valor, atualizado_em=NOW()",
                        (_nk.strip(),),
                    )
                    st.success("Chave salva!")
                    st.rerun()
        st.markdown("---")
        # Consumo Tokens
        st.markdown("##### 📊 Consumo do Chat IA")
        _df_tok = run_query("SELECT mes, chars, atualizado_em FROM chat_ia_tokens ORDER BY mes DESC LIMIT 6")
        if not _df_tok.empty:
            _mes_a = date.today().strftime("%Y-%m")
            _chars_a = int(_df_tok[_df_tok["mes"]==_mes_a]["chars"].iloc[0]) if not _df_tok[_df_tok["mes"]==_mes_a].empty else 0
            _tc1, _tc2 = st.columns(2)
            _tc1.metric("Caracteres este mês", f"{_chars_a:,}")
            _tc2.metric("Tokens estimados", f"~{_chars_a//4:,}")
            for _, _tr in _df_tok.iterrows():
                st.caption(f"`{_tr['mes']}` — {int(_tr['chars']):,} chars · ~{int(_tr['chars'])//4:,} tokens")
        else:
            st.info("Nenhuma interação registrada ainda.")
        st.markdown("---")
        # Orçamento Mensal
        st.markdown("##### 💰 Orçamento Mensal IA (USD)")
        _df_orc = run_query("SELECT valor FROM config_geral WHERE chave = 'ORCAMENTO_MENSAL_USD'")
        _orc_a = float(_df_orc["valor"].iloc[0]) if not _df_orc.empty and _df_orc["valor"].iloc[0] else 0.0
        with st.form("hub_orcamento"):
            _no = st.number_input("Orçamento (US$)", min_value=0.0, max_value=1000.0, value=_orc_a, step=1.0, format="%.2f")
            if st.form_submit_button("💾 Salvar Orçamento", use_container_width=True):
                run_command(
                    "INSERT INTO config_geral (chave,valor,atualizado_em) VALUES('ORCAMENTO_MENSAL_USD',%s,NOW()) "
                    "ON CONFLICT (chave) DO UPDATE SET valor=EXCLUDED.valor, atualizado_em=NOW()",
                    (str(_no),),
                )
                st.success(f"Orçamento US$ {_no:.2f} salvo!")
                st.rerun()
        st.markdown("---")
        # Webhook n8n
        st.markdown("##### 🔗 Webhook n8n — WhatsApp")
        _df_wh = run_query("SELECT valor FROM config_geral WHERE chave = 'URL_WEBHOOK_N8N'")
        _wh_a = _df_wh["valor"].iloc[0] if not _df_wh.empty else ""
        st.caption(f"URL atual: `{_wh_a[:40]}…`" if len(_wh_a) > 40 else f"URL atual: `{_wh_a or '(não configurada)'}`")
        with st.form("hub_webhook"):
            _nurl = st.text_input("URL do Webhook n8n", placeholder="https://n8n.seudominio.com/webhook/loja-gmh")
            if st.form_submit_button("💾 Salvar URL", use_container_width=True):
                if not _nurl.strip().startswith("http"):
                    st.error("URL inválida.")
                else:
                    run_command(
                        "INSERT INTO config_geral (chave,valor,atualizado_em) VALUES('URL_WEBHOOK_N8N',%s,NOW()) "
                        "ON CONFLICT (chave) DO UPDATE SET valor=EXCLUDED.valor, atualizado_em=NOW()",
                        (_nurl.strip(),),
                    )
                    st.success("URL salva!")
                    st.rerun()
        # Log erros
        _df_err = run_query("SELECT valor, atualizado_em FROM config_geral WHERE chave = 'ULTIMO_ERRO_N8N'")
        if not _df_err.empty and _df_err["valor"].iloc[0]:
            st.error(f"**Último erro:** `{_df_err['valor'].iloc[0]}`")
            if st.button("🗑️ Limpar log de erro", key="hub_limpar_erro"):
                run_command("UPDATE config_geral SET valor='',atualizado_em=NOW() WHERE chave='ULTIMO_ERRO_N8N'")
                st.rerun()

    # ════════════════════════════════════════════════════════
    # TAB: NASA — Limpeza Irreversível
    # ════════════════════════════════════════════════════════
    with _hub_nasa:
        st.markdown(
            "<div style='background:#3D0000;border-radius:10px;padding:12px 18px;"
            "border-left:5px solid #FF4444;margin-bottom:1rem'>"
            "<span style='color:#FF8888;font-size:.85rem;font-weight:700'>🚀 LIMPEZA NASA</span><br/>"
            "<span style='color:#FFB3B3;font-size:.8rem'>"
            "⚠️ Esta ação é <b>irreversível</b> e exige autorização do Jardel. "
            "Não pode ser desfeita. Use somente para limpar dados de teste.</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        _df_nasa_pw = run_query("SELECT valor FROM config_geral WHERE chave = 'SENHA_MASTER_NASA'")
        _nasa_pw_salva = _df_nasa_pw["valor"].iloc[0] if not _df_nasa_pw.empty else ""
        with st.expander("🔐 Definir Senha Master NASA", expanded=not bool(_nasa_pw_salva)):
            with st.form("hub_nasa_senha"):
                _npw = st.text_input("Nova Senha Master", type="password", placeholder="Min. 8 caracteres")
                if st.form_submit_button("💾 Salvar Senha"):
                    if len(_npw) < 8:
                        st.error("Mínimo 8 caracteres.")
                    else:
                        import hashlib as _hl
                        run_command(
                            "INSERT INTO config_geral (chave,valor,atualizado_em) VALUES('SENHA_MASTER_NASA',%s,NOW()) "
                            "ON CONFLICT (chave) DO UPDATE SET valor=EXCLUDED.valor, atualizado_em=NOW()",
                            (_hl.sha256(_npw.encode()).hexdigest(),),
                        )
                        st.success("Senha master definida.")
                        st.rerun()
        st.markdown("---")
        _nasa_input = st.text_input("🔑 Senha Master", type="password", key="hub_nasa_pw")
        import hashlib as _hl2
        _nasa_hash = _hl2.sha256(_nasa_input.encode()).hexdigest() if _nasa_input else ""
        _nasa_ok = bool(_nasa_pw_salva) and (_nasa_hash == _nasa_pw_salva)
        if _nasa_input and not _nasa_ok:
            st.error("❌ Senha incorreta.")
        if _nasa_ok:
            st.success("✅ Acesso NASA liberado.")
            st.markdown("---")
            # Excluir Produto
            st.markdown("##### 🗑️ Excluir Produto")
            df_prod_nasa = run_query("SELECT id::text AS pid, nome FROM produtos ORDER BY nome")
            if not df_prod_nasa.empty:
                _np_idx = st.selectbox("Produto", range(len(df_prod_nasa)),
                                        format_func=lambda i: df_prod_nasa["nome"].iloc[i], key="hub_nasa_prod")
                _np_id   = df_prod_nasa["pid"].iloc[_np_idx]
                _np_nome = df_prod_nasa["nome"].iloc[_np_idx]
                st.warning(f"Produto: **{_np_nome}**")
                if st.button(f"🗑️ EXCLUIR '{_np_nome}' permanentemente", key="hub_del_prod", type="primary"):
                    if run_command("DELETE FROM produtos WHERE id = %s", (_np_id,)):
                        st.toast(f"Produto '{_np_nome}' excluído.", icon="🗑️")
                        st.rerun()
            st.markdown("---")
            # Excluir Venda
            st.markdown("##### 🗑️ Excluir Venda")
            df_vnd_nasa = run_query("""
                SELECT v.id::text AS vid, c.nome AS cliente, v.data_venda::date AS data, v.valor_total
                FROM vendas v JOIN clientes c ON c.id = v.cliente_id
                ORDER BY v.data_venda DESC LIMIT 100
            """)
            if not df_vnd_nasa.empty:
                _nv_opts = [f"{_fmt_data(r['data'])} — {r['cliente']} — R$ {float(r['valor_total']):,.2f}" for _, r in df_vnd_nasa.iterrows()]
                _nv_idx  = st.selectbox("Venda", range(len(_nv_opts)), format_func=lambda i: _nv_opts[i], key="hub_nasa_vnd")
                _nv_id   = df_vnd_nasa["vid"].iloc[_nv_idx]
                if st.button("🗑️ EXCLUIR esta venda permanentemente", key="hub_del_vnd", type="primary"):
                    run_command("DELETE FROM itens_venda WHERE venda_id = %s", (_nv_id,))
                    run_command("DELETE FROM contas_receber WHERE venda_id = %s", (_nv_id,))
                    if run_command("DELETE FROM vendas WHERE id = %s", (_nv_id,)):
                        st.toast("Venda excluída.", icon="🗑️")
                        st.rerun()
            st.markdown("---")
            # Excluir Cliente
            st.markdown("##### 👤 Excluir Cliente")
            df_cli_nasa = run_query("SELECT id::text AS cid, nome FROM clientes ORDER BY nome")
            if not df_cli_nasa.empty:
                _ncl_idx  = st.selectbox("Cliente", range(len(df_cli_nasa)),
                                          format_func=lambda i: df_cli_nasa["nome"].iloc[i], key="hub_nasa_cli")
                _ncl_id   = df_cli_nasa["cid"].iloc[_ncl_idx]
                _ncl_nome = df_cli_nasa["nome"].iloc[_ncl_idx]
                st.warning(f"Cliente: **{_ncl_nome}**")
                _df_div = run_query(f"SELECT COUNT(*) AS qtd FROM contas_receber cr "
                                    f"JOIN vendas v ON v.id = cr.venda_id "
                                    f"WHERE v.cliente_id = '{_ncl_id}' AND cr.status = 'aberto'")
                if int(_df_div["qtd"].iloc[0]) > 0 if not _df_div.empty else False:
                    st.error("❌ Cliente com parcelas em aberto. Quite antes de excluir.")
                else:
                    if st.button(f"🗑️ EXCLUIR '{_ncl_nome}' permanentemente", key="hub_del_cli", type="primary"):
                        _df_vc = run_query(f"SELECT id::text AS vid FROM vendas WHERE cliente_id = '{_ncl_id}'")
                        for _, _vc in _df_vc.iterrows():
                            run_command("DELETE FROM itens_venda WHERE venda_id = %s", (_vc["vid"],))
                            run_command("DELETE FROM contas_receber WHERE venda_id = %s", (_vc["vid"],))
                        run_command("DELETE FROM vendas WHERE cliente_id = %s", (_ncl_id,))
                        if run_command("DELETE FROM clientes WHERE id = %s", (_ncl_id,)):
                            st.toast(f"Cliente '{_ncl_nome}' excluído.", icon="🗑️")
                            st.rerun()
            st.markdown("---")
            # Limpeza Histórico
            st.markdown("##### ☢️ Limpar Histórico de Testes")
            st.caption("Exclui pagamentos do balcão e tokens de IA. Vendas e parcelas NÃO são afetadas.")
            if st.button("☢️ LIMPAR histórico de pagamentos e tokens", key="hub_nasa_hist", type="primary"):
                run_command("DELETE FROM pagamentos_balcao")
                run_command("DELETE FROM chat_ia_tokens")
                run_command("UPDATE config_geral SET valor = '0' WHERE chave LIKE 'DISPAROS_%'")
                st.toast("Histórico limpo.", icon="☢️")
                st.rerun()
        else:
            st.info("🔐 Digite a senha master acima para liberar as operações irreversíveis.")

    # ════════════════════════════════════════════════════════
    # TAB: 🚀 Carga Inicial — Importação de CSV (somente admin_master)
    # ════════════════════════════════════════════════════════
    with _hub_carga:
        import io as _io
        import pandas as _pd_carga

        _CSV_ENC = "latin1"

        st.markdown("#### 🚀 Carga Inicial — Migração de Dados")
        st.caption(
            "Importe dados legados para o sistema. "
            "Use apenas em ambiente limpo ou de primeiro uso. "
            "Registros com chave duplicada são ignorados (não sobrescrevem). "
            "Delimitador detectado automaticamente (`;` ou `,`) · Encoding: **`latin1`**"
        )

        # ── helpers internos ────────────────────────────────────────────────
        def _carga_conn():
            """Conexão dedicada para importações longas (fora do pool)."""
            return psycopg2.connect(**DB_CONFIG)

        def _read_csv(uploaded, enc=_CSV_ENC):
            raw = uploaded.read()
            # sep=None + engine='python' → detecta automaticamente ; ou ,
            # quoting=3 (QUOTE_NONE) → ignora aspas problemáticas
            # on_bad_lines='skip' → pula linhas malformadas sem travar
            return _pd_carga.read_csv(
                _io.BytesIO(raw),
                sep=None,
                engine="python",
                encoding=enc,
                quoting=3,
                on_bad_lines="skip",
                dtype=str,
                keep_default_na=False,
            )

        def _norm_col(col: str) -> str:
            return col.strip().upper()

        def _to_float_br(series):
            """Converte valores monetários BR ou decimais para float.
            Detecta formato por linha: vírgula+ponto → BR (1.234,56);
            só vírgula → BR decimal (12,50); só ponto → decimal US (12.50)."""
            s = series.astype(str).str.strip()
            # Remove tudo que não é dígito, vírgula, ponto ou sinal negativo
            s = s.str.replace(r"[^\d,.\-]", "", regex=True)
            _has_comma = s.str.contains(",", regex=False)
            _has_dot   = s.str.contains(".", regex=False)
            # BR com milhar: tem vírgula E ponto → remove ponto (milhar), vírgula→ponto
            _br_milhar = _has_comma & _has_dot
            _s_br = s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            # BR só decimal: só vírgula → vírgula vira ponto
            _br_dec = _has_comma & ~_has_dot
            _s_dec = s.str.replace(",", ".", regex=False)
            # Aplica transformação correta por linha; só ponto → mantém (decimal US/padrão)
            result = s.copy()
            result = result.where(~_br_milhar, _s_br)
            result = result.where(~_br_dec, _s_dec)
            result = result.replace("", "0")
            return _pd_carga.to_numeric(result, errors="coerce").fillna(0.0)

        def _show_col_map(**cols):
            """Exibe mapeamento de colunas detectado automaticamente."""
            with st.expander("🔍 Mapeamento de colunas detectado", expanded=False):
                for _campo, _coluna in cols.items():
                    _icon = "✅" if _coluna else "❌"
                    _txt  = f"`{_coluna}`" if _coluna else "_não encontrada_"
                    st.markdown(f"- {_icon} **{_campo}** → {_txt}")

        # auto-migrate: garante coluna nr_documento em contas_receber
        try:
            with _carga_conn() as _mc:
                with _mc.cursor() as _mcur:
                    _mcur.execute(
                        "ALTER TABLE contas_receber "
                        "ADD COLUMN IF NOT EXISTS nr_documento TEXT;"
                    )
        except Exception:
            pass

        # ── 1. Importar Clientes ─────────────────────────────────────────────
        st.markdown("---")
        st.markdown("##### 👤 1. Importar Clientes")
        st.caption(
            "Arquivo: **EXPORT-CLIENTE.CSV** · Campos detectados automaticamente: "
            "`NOME` (obrigatório), `CPF`, `FONE`/`WHATSAPP`/`CELULAR`, "
            "`NASCIMENTO`/`DATA_NASC`, `EMAIL`, `CEP`, `ENDERECO`, "
            "`NUMERO`, `BAIRRO`, `CIDADE`, `OBS`/`OBSERVACAO`"
        )
        _cli_file = st.file_uploader(
            "Selecione EXPORT-CLIENTE.CSV", type=["csv", "CSV"], key="hub_carga_cli"
        )
        if _cli_file is not None:
            try:
                _df_cli = _read_csv(_cli_file)
                _df_cli.columns = [_norm_col(c) for c in _df_cli.columns]

                _col_nome  = next((c for c in _df_cli.columns if "NOME"   in c), None)
                _col_cpf   = next((c for c in _df_cli.columns if "CPF"    in c), None)
                _col_fone  = next((c for c in _df_cli.columns
                                   if any(x in c for x in ("FONE", "WHATSAPP", "CELULAR"))), None)
                _col_nasc  = next((c for c in _df_cli.columns
                                   if any(x in c for x in ("NASC", "DT_NASC", "DATA_NASC"))), None)
                _col_email = next((c for c in _df_cli.columns if "EMAIL"  in c), None)
                _col_cep   = next((c for c in _df_cli.columns if "CEP"    in c), None)
                _col_end   = next((c for c in _df_cli.columns
                                   if any(x in c for x in ("ENDERECO", "ENDEREÇO", "RUA", "LOGRADOURO"))), None)
                _col_num   = next((c for c in _df_cli.columns
                                   if any(x in c for x in ("NUMERO", "NÚMERO", "NR_END"))), None)
                _col_bairro = next((c for c in _df_cli.columns if "BAIRRO" in c), None)
                _col_cidade = next((c for c in _df_cli.columns
                                    if any(x in c for x in ("CIDADE", "MUNICIPIO", "MUNICÍPIO"))), None)
                _col_obs   = next((c for c in _df_cli.columns
                                   if any(x in c for x in ("OBS", "OBSERV"))), None)
                _col_cod   = next((c for c in _df_cli.columns
                                   if any(x in c for x in ("CODIGO", "CODCLI", "COD_CLI", "CODCLIENTE", "COD"))), None)

                _show_col_map(
                    NOME=_col_nome, CPF=_col_cpf, WHATSAPP=_col_fone, NASCIMENTO=_col_nasc,
                    EMAIL=_col_email, CEP=_col_cep, ENDERECO=_col_end,
                    BAIRRO=_col_bairro, CIDADE=_col_cidade, CODIGO=_col_cod,
                )

                if not _col_nome:
                    st.error("❌ Coluna NOME não encontrada no CSV.")
                else:
                    # ── limpeza com pandas ──────────────────────────────────
                    _dc = _df_cli.copy()
                    _dc["xnome"] = _dc[_col_nome].str.strip()
                    _dc = _dc[_dc["xnome"] != ""]

                    def _col_val(col):
                        if col and col in _dc.columns:
                            return _dc[col].str.strip().replace("", None)
                        return _pd_carga.Series([None] * len(_dc), dtype=object)

                    _dc["xcpf"]    = _col_val(_col_cpf)
                    _dc["xfone"]   = _col_val(_col_fone)
                    _dc["xemail"]  = _col_val(_col_email)
                    _dc["xcep"]    = _col_val(_col_cep)
                    _dc["xend"]    = _col_val(_col_end)
                    _dc["xnum"]    = _col_val(_col_num)
                    _dc["xbairro"] = _col_val(_col_bairro)
                    _dc["xcidade"] = _col_val(_col_cidade)
                    _dc["xobs"]    = _col_val(_col_obs)
                    _dc["xcod"]    = _col_val(_col_cod)

                    # strip explícito + vazio → None (evita Duplicate Key em campos livres)
                    _dc["xcpf"]  = _dc["xcpf"].str.strip().replace("", None)
                    _dc["xfone"] = _dc["xfone"].str.strip().replace("", None)

                    if _col_nasc:
                        _nasc_dt     = _pd_carga.to_datetime(_dc[_col_nasc], dayfirst=True, errors="coerce")
                        _dc["xnasc"] = _nasc_dt.dt.strftime("%Y-%m-%d").where(_nasc_dt.notna(), other=None)
                    else:
                        _dc["xnasc"] = None

                    _preview_cols = [c for c in [_col_nome, _col_cpf, _col_fone, _col_email] if c]
                    st.dataframe(_dc[_preview_cols].head(8), use_container_width=True)
                    st.caption(f"**{len(_dc)}** registros válidos prontos para importar.")

                    if st.button("✅ Importar Clientes agora", key="hub_btn_cli",
                                 use_container_width=True, type="primary"):
                        from psycopg2.extras import execute_batch as _exec_batch
                        # fillna('') → NaN vira '' → '' or None = None no psycopg2
                        _dc_f = _dc.fillna("")
                        _rows_cli = [
                            (
                                r.xnome   or None,
                                r.xcpf    or None,
                                r.xfone   or None,
                                r.xnasc   or None,
                                r.xemail  or None,
                                r.xcep    or None,
                                r.xend    or None,
                                r.xnum    or None,
                                r.xbairro or None,
                                r.xcidade or None,
                                r.xobs    or None,
                                r.xcod    or None,
                            )
                            for r in _dc_f.itertuples(index=False)
                        ]
                        _total_cli = len(_rows_cli)
                        _ph_cli = st.empty()
                        _ph_cli.progress(0.0, text=f"Preparando {_total_cli} registros…")

                        _SQL_CLI = """
                            INSERT INTO clientes
                                (nome, cpf, whatsapp, data_nascimento, ativo,
                                 email, cep, endereco, numero, bairro, cidade, observacoes,
                                 codigo_externo)
                            VALUES (%s,%s,%s,%s,true,%s,%s,%s,%s,%s,%s,%s,%s)
                            ON CONFLICT (codigo_externo) WHERE codigo_externo IS NOT NULL
                            DO UPDATE SET
                                nome            = EXCLUDED.nome,
                                cpf             = EXCLUDED.cpf,
                                whatsapp        = EXCLUDED.whatsapp,
                                data_nascimento = EXCLUDED.data_nascimento,
                                email           = EXCLUDED.email,
                                cep             = EXCLUDED.cep,
                                endereco        = EXCLUDED.endereco,
                                numero          = EXCLUDED.numero,
                                bairro          = EXCLUDED.bairro,
                                cidade          = EXCLUDED.cidade,
                                observacoes     = EXCLUDED.observacoes
                        """
                        _BATCH = 500
                        _err_cli = 0
                        _conn_cli = _carga_conn()
                        try:
                            with _conn_cli.cursor() as _cur_cli:
                                _cur_cli.execute("SELECT COUNT(*) FROM clientes")
                                _cnt_antes = _cur_cli.fetchone()[0]

                            _batches_cli = [
                                _rows_cli[i:i+_BATCH]
                                for i in range(0, _total_cli, _BATCH)
                            ]
                            _n_bat = len(_batches_cli)

                            with _conn_cli.cursor() as _cur_cli:
                                for _bi, _bat in enumerate(_batches_cli):
                                    _ph_cli.progress(
                                        (_bi + 1) / _n_bat,
                                        text=f"Lote {_bi+1}/{_n_bat} "
                                             f"({min((_bi+1)*_BATCH, _total_cli)}/{_total_cli} registros)…"
                                    )
                                    _cur_cli.execute("SAVEPOINT sp_bat")
                                    try:
                                        _exec_batch(_cur_cli, _SQL_CLI, _bat, page_size=_BATCH)
                                        _cur_cli.execute("RELEASE SAVEPOINT sp_bat")
                                    except Exception as _e_bat:
                                        _cur_cli.execute("ROLLBACK TO SAVEPOINT sp_bat")
                                        _cur_cli.execute("RELEASE SAVEPOINT sp_bat")
                                        st.warning(
                                            f"⚠️ Falha no lote {_bi+1}: {_e_bat} "
                                            f"— tentando linha a linha…"
                                        )
                                        for _row_f in _bat:
                                            _cur_cli.execute("SAVEPOINT sp_row")
                                            try:
                                                _cur_cli.execute(_SQL_CLI, _row_f)
                                                _cur_cli.execute("RELEASE SAVEPOINT sp_row")
                                            except Exception as _e_row:
                                                _cur_cli.execute("ROLLBACK TO SAVEPOINT sp_row")
                                                _cur_cli.execute("RELEASE SAVEPOINT sp_row")
                                                _err_cli += 1

                            _ph_cli.progress(1.0, text="Aguardando COMMIT do banco…")
                            _conn_cli.commit()

                            with _conn_cli.cursor() as _cur_cli:
                                _cur_cli.execute("SELECT COUNT(*) FROM clientes")
                                _cnt_depois = _cur_cli.fetchone()[0]

                            _ok_cli      = _cnt_depois - _cnt_antes
                            _updated_cli = max(_total_cli - _ok_cli - _err_cli, 0)
                            _ph_cli.empty()
                            st.success(
                                f"✅ **{_ok_cli}** clientes novos inseridos · "
                                f"**{_updated_cli}** atualizados (codigo_externo já existia) · "
                                f"**{_err_cli}** erros."
                            )
                        except Exception as _e_bulk:
                            _conn_cli.rollback()
                            _ph_cli.empty()
                            st.error(f"Falha na importação em lote: {_e_bulk}")
                        finally:
                            _conn_cli.close()
                        st.rerun()
            except Exception as _e_cli:
                st.error(f"Erro ao ler CSV: {_e_cli}")

        # ── 2. Importar Produtos & Estoque ───────────────────────────────────
        st.markdown("---")
        st.markdown("##### 📦 2. Importar Produtos & Estoque")
        st.caption(
            "Arquivos: **EXPORT-PRODUTO.CSV** + **EXPORT-ESTOQUE.CSV** — "
            "cruzamento automático por `CODBAR` / `REFERENCIA` via `pandas.merge`. "
            "Campos produto: `DESCRICAO`/`NOME`, `CODBAR`, `PRECO_VENDA`, `PRECO_CUSTO`, `CATEGORIA`; "
            "campos estoque: `CODBAR`/`REFERENCIA`, `SALDO`/`QTDE`/`ESTOQUE`"
        )
        _col_p1, _col_p2 = st.columns(2)
        with _col_p1:
            _prod_file = st.file_uploader("EXPORT-PRODUTO.CSV",  type=["csv", "CSV"], key="hub_carga_prod")
        with _col_p2:
            _est_file  = st.file_uploader("EXPORT-ESTOQUE.CSV", type=["csv", "CSV"], key="hub_carga_est")

        if _prod_file is not None:
            try:
                _df_prod = _read_csv(_prod_file)
                _df_prod.columns = [_norm_col(c) for c in _df_prod.columns]

                _df_est = None
                if _est_file is not None:
                    _df_est = _read_csv(_est_file)
                    _df_est.columns = [_norm_col(c) for c in _df_est.columns]

                # mapeamento produtos
                _p_nome  = next((c for c in _df_prod.columns if "DESCRI" in c or c == "NOME"), None)
                _p_cod   = next((c for c in _df_prod.columns if "CODBAR" in c or "REFERENCIA" in c), None)
                _p_venda = next((c for c in _df_prod.columns
                                 if ("PRECO" in c and "VENDA" in c)
                                 or any(c == x for x in ("VENDA", "VLR_VENDA", "VALOR_VENDA",
                                                          "PRECO_UNIT", "VALOR_UNIT"))), None)
                _p_custo = next((c for c in _df_prod.columns
                                 if ("PRECO" in c and "CUSTO" in c)
                                 or any(c == x for x in ("CUSTO", "VALOR_CUSTO",
                                                          "CUSTO_UNIT", "COMPRA"))), None)
                _p_cat   = next((c for c in _df_prod.columns if "CATEG" in c or "GRUPO" in c), None)
                _p_emin  = next((c for c in _df_prod.columns if "ESTOQUE_MIN" in c or "QTD_MIN" in c), None)
                # estoque inicial pode vir na própria planilha de produtos
                _p_saldo = next((c for c in _df_prod.columns
                                 if any(x in c for x in ("ESTOQUE", "SALDO", "QTD"))
                                 and "MIN" not in c), None)

                _e_cod   = None
                _e_sald  = None
                if _df_est is not None:
                    _e_cod  = next((c for c in _df_est.columns if "CODBAR" in c or "REFERENCIA" in c), None)
                    _e_sald = next((c for c in _df_est.columns
                                    if any(x in c for x in ("SALDO", "QTDE", "ESTOQUE", "QTD"))), None)

                _show_col_map(**{
                    "NOME/DESC":    _p_nome,
                    "CODBAR":       _p_cod,
                    "PRECO_VENDA":  _p_venda,
                    "PRECO_CUSTO":  _p_custo,
                    "CATEGORIA":    _p_cat,
                    "ESTOQUE_INI":  _p_saldo or _e_sald,
                    "EST.CODBAR":   _e_cod,
                })

                if not _p_nome:
                    st.error("❌ Coluna de nome/descrição não encontrada em EXPORT-PRODUTO.CSV.")
                else:
                    # ── seleção manual de colunas de preço ──────────────────
                    _all_prod_cols = ["— não usar —"] + list(_df_prod.columns)
                    _col_sv, _col_sc = st.columns(2)
                    with _col_sv:
                        _sv_idx = _all_prod_cols.index(_p_venda) if _p_venda in _all_prod_cols else 0
                        _sel_venda = st.selectbox(
                            "💲 Coluna → Preço de Venda",
                            _all_prod_cols,
                            index=_sv_idx,
                            key="hub_sel_venda",
                            help="Detectado automaticamente. Altere se necessário.",
                        )
                        _p_venda = None if _sel_venda == "— não usar —" else _sel_venda
                    with _col_sc:
                        _sc_idx = _all_prod_cols.index(_p_custo) if _p_custo in _all_prod_cols else 0
                        _sel_custo = st.selectbox(
                            "💰 Coluna → Preço de Custo",
                            _all_prod_cols,
                            index=_sc_idx,
                            key="hub_sel_custo",
                            help="Detectado automaticamente. Altere se necessário.",
                        )
                        _p_custo = None if _sel_custo == "— não usar —" else _sel_custo

                    # ── limpeza e cruzamento com pandas merge ───────────────
                    _dp = _df_prod.copy()
                    _dp["xnome"]  = _dp[_p_nome].str.strip()
                    _dp["xcod"]   = _dp[_p_cod].str.strip()   if _p_cod   else ""
                    _dp["xvenda"] = _to_float_br(_dp[_p_venda]) if _p_venda else 0.0
                    _dp["xcusto"] = _to_float_br(_dp[_p_custo]) if _p_custo else 0.0
                    _dp["xcat"]   = _dp[_p_cat].str.strip().fillna("Importado") if _p_cat else "Importado"
                    _dp["xemin"]  = _to_float_br(_dp[_p_emin])  if _p_emin  else 0.0
                    _dp = _dp[_dp["xnome"] != ""]

                    # merge com estoque via CODBAR (pd.merge → sem iteração manual)
                    if _df_est is not None and _e_cod and _e_sald:
                        _de = _df_est[[_e_cod, _e_sald]].copy()
                        _de.columns = ["xcod", "xsaldo_raw"]
                        _de["xcod"]    = _de["xcod"].str.strip()
                        _de["xsaldo"]  = _to_float_br(_de["xsaldo_raw"])
                        _dp = _dp.merge(_de[["xcod", "xsaldo"]], on="xcod", how="left")
                        _dp["xsaldo"]  = _dp["xsaldo"].fillna(0.0)
                    elif _p_saldo:
                        # estoque inicial vem da própria planilha de produtos
                        _dp["xsaldo"] = _to_float_br(_dp[_p_saldo])
                    else:
                        _dp["xsaldo"] = 0.0

                    st.dataframe(
                        _dp[["xnome", "xcod", "xvenda", "xcusto", "xsaldo"]].rename(columns={
                            "xnome": "Nome", "xcod": "Código", "xvenda": "Preço Venda",
                            "xcusto": "Preço Custo", "xsaldo": "Estoque Inicial"
                        }).head(8),
                        use_container_width=True
                    )

                    # ── DEBUG: valores convertidos antes do envio ao banco ──
                    with st.expander("🔬 Debug — valores convertidos (5 primeiros)", expanded=True):
                        st.write(
                            _dp[["xnome", "xvenda", "xcusto", "xsaldo"]]
                            .rename(columns={"xnome": "Nome", "xvenda": "Venda",
                                             "xcusto": "Custo", "xsaldo": "📦 Estoque"})
                            .head(5)
                        )

                    st.caption(
                        f"**{len(_dp)}** produtos encontrados."
                        + (f" · **{len(_df_est)}** registros de estoque cruzados." if _df_est is not None else "")
                    )

                    if st.button("✅ Importar Produtos & Estoque agora", key="hub_btn_prod",
                                 use_container_width=True, type="primary"):
                        _rows_prod = [
                            (
                                str(r.xnome),
                                str(r.xcat) or "Importado",
                                float(r.xvenda),
                                float(r.xcusto),
                                float(r.xsaldo),
                                float(r.xemin),
                                str(r.xcod) if r.xcod else None,
                            )
                            for r in _dp.itertuples(index=False)
                        ]
                        _prog_prod  = st.progress(0, text="Importando produtos…")
                        _total_prod = len(_rows_prod)
                        _conn_prod  = _carga_conn()
                        _ok_prod = _upd_prod = _err_prod = 0

                        # SQL 1: produtos COM codigo_barras → upsert por código
                        _SQL_COD = """
                            INSERT INTO produtos
                                (nome, categoria, preco_venda, preco_custo,
                                 estoque_atual, estoque_minimo, codigo_barras)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (codigo_barras) DO UPDATE SET
                                preco_venda   = EXCLUDED.preco_venda,
                                preco_custo   = EXCLUDED.preco_custo,
                                estoque_atual = COALESCE(produtos.estoque_atual, 0)
                                                + EXCLUDED.estoque_atual,
                                categoria     = COALESCE(EXCLUDED.categoria, produtos.categoria),
                                nome          = EXCLUDED.nome
                        """
                        # SQL 2a: produtos SEM codigo_barras → tenta UPDATE por nome
                        _SQL_UPD_NOME = """
                            UPDATE produtos
                            SET preco_venda   = %s,
                                preco_custo   = %s,
                                estoque_atual = COALESCE(estoque_atual, 0) + %s,
                                categoria     = COALESCE(%s, categoria)
                            WHERE LOWER(nome) = LOWER(%s)
                        """
                        # SQL 2b: fallback INSERT se nome não existe
                        _SQL_INS = """
                            INSERT INTO produtos
                                (nome, categoria, preco_venda, preco_custo,
                                 estoque_atual, estoque_minimo)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                        """
                        with _conn_prod:
                            with _conn_prod.cursor() as _cur_prod:
                                for _i_prod, _rp in enumerate(_rows_prod):
                                    _rp_nome, _rp_cat, _rp_venda, _rp_custo, \
                                        _rp_saldo, _rp_emin, _rp_cod = _rp
                                    try:
                                        if _rp_cod:
                                            _cur_prod.execute(_SQL_COD, _rp)
                                            _ok_prod += 1
                                        else:
                                            _cur_prod.execute(
                                                _SQL_UPD_NOME,
                                                (_rp_venda, _rp_custo, _rp_saldo,
                                                 _rp_cat, _rp_nome),
                                            )
                                            if _cur_prod.rowcount > 0:
                                                _upd_prod += 1
                                            else:
                                                _cur_prod.execute(
                                                    _SQL_INS,
                                                    (_rp_nome, _rp_cat, _rp_venda,
                                                     _rp_custo, _rp_saldo, _rp_emin),
                                                )
                                                _ok_prod += 1
                                    except Exception:
                                        _err_prod += 1
                                    if _i_prod % 50 == 0:
                                        _prog_prod.progress(
                                            (_i_prod + 1) / _total_prod,
                                            text=f"Importando… {_i_prod + 1}/{_total_prod}"
                                        )
                        _conn_prod.close()
                        _prog_prod.progress(1.0, text="Concluído!")
                        st.success(
                            f"✅ **{_ok_prod}** inseridos · "
                            f"**{_upd_prod}** atualizados por nome · "
                            f"**{_err_prod}** erros."
                        )
                        st.rerun()
            except Exception as _e_prod:
                st.error(f"Erro ao ler CSV: {_e_prod}")

        # ── 3. Importar Financeiro ───────────────────────────────────────────
        st.markdown("---")
        st.markdown("##### 💰 3. Importar Financeiro — Contas a Receber")
        st.caption(
            "Arquivo: **EXPORT-DUPLIC.CSV** · Campos: "
            "`REFERENCIA` (nº doc, salvo em `nr_documento`), "
            "`VALOR_DOCTO`/`VALOR`, `DT_VENCIMENTO`/`VENCIMENTO`, "
            "`NOME`/`CLIENTE`. Todas as parcelas são inseridas com **status = 'aberto'**."
        )
        _fin_file = st.file_uploader(
            "Selecione EXPORT-DUPLIC.CSV", type=["csv", "CSV"], key="hub_carga_fin"
        )
        if _fin_file is not None:
            try:
                _df_fin = _read_csv(_fin_file)
                _df_fin.columns = [_norm_col(c) for c in _df_fin.columns]

                _f_ref  = next((c for c in _df_fin.columns
                                if any(x in c for x in ("REFERENCIA", "REFER", "NR_DOC", "DOCUMENTO"))), None)
                _f_val  = next((c for c in _df_fin.columns
                                if any(x in c for x in ("VALOR_DOCTO", "VALOR", "VLR"))), None)
                _f_venc = next((c for c in _df_fin.columns
                                if any(x in c for x in ("VENCIMENTO", "DT_VENC", "DATA_VENC"))), None)
                _f_cli  = next((c for c in _df_fin.columns
                                if any(x in c for x in ("NOME", "CLIENTE"))), None)

                _show_col_map(REFERENCIA=_f_ref, VALOR=_f_val, VENCIMENTO=_f_venc, CLIENTE=_f_cli)

                if not _f_val or not _f_venc:
                    st.error("❌ Colunas VALOR e VENCIMENTO são obrigatórias no CSV financeiro.")
                else:
                    # ── limpeza com pandas ──────────────────────────────────
                    _df = _df_fin.copy()
                    _df["xvalor"] = _to_float_br(_df[_f_val])

                    _venc_dt      = _pd_carga.to_datetime(_df[_f_venc], dayfirst=True, errors="coerce")
                    _df["xvenc"]  = _venc_dt.dt.strftime("%Y-%m-%d").where(_venc_dt.notna(), other=None)
                    _df["xref"]   = _df[_f_ref].str.strip().replace("", None) if _f_ref  else None
                    _df["xcli"]   = _df[_f_cli].str.strip()                   if _f_cli  else ""

                    # remove linhas sem valor válido ou sem data de vencimento
                    _df = _df[_df["xvalor"] > 0]
                    _df = _df[_venc_dt.notna()]

                    _prev_cols = [c for c in [_f_venc, _f_val, _f_ref, _f_cli] if c]
                    st.dataframe(_df[_prev_cols].head(8), use_container_width=True)
                    st.caption(f"**{len(_df)}** duplicatas válidas encontradas.")

                    if st.button("✅ Importar Financeiro agora", key="hub_btn_fin",
                                 use_container_width=True, type="primary"):
                        _prog_fin  = st.progress(0, text="Importando financeiro…")
                        _total_fin = len(_df)
                        _conn_fin  = _carga_conn()
                        _ok_fin = _err_fin = 0
                        with _conn_fin:
                            with _conn_fin.cursor() as _cur_fin:
                                for _i_fin, _rf in enumerate(_df.itertuples(index=False)):
                                    # associa venda_id pelo nome do cliente (melhor esforço)
                                    _vid_fin = None
                                    _cli_fin = str(getattr(_rf, "xcli", "")).strip()
                                    if _cli_fin:
                                        _cur_fin.execute(
                                            """
                                            SELECT v.id FROM vendas v
                                            JOIN clientes c ON c.id = v.cliente_id
                                            WHERE c.nome ILIKE %s
                                            ORDER BY v.data_venda DESC LIMIT 1
                                            """,
                                            (f"%{_cli_fin}%",),
                                        )
                                        _vr_fin = _cur_fin.fetchone()
                                        _vid_fin = _vr_fin[0] if _vr_fin else None
                                    try:
                                        _cur_fin.execute(
                                            """
                                            INSERT INTO contas_receber
                                                (venda_id, valor_parcela, dt_vencimento,
                                                 status, nr_documento)
                                            VALUES (%s, %s, %s, 'aberto', %s)
                                            """,
                                            (
                                                _vid_fin,
                                                float(getattr(_rf, "xvalor")),
                                                str(getattr(_rf,  "xvenc")),
                                                getattr(_rf, "xref", None),
                                            ),
                                        )
                                        _ok_fin += 1
                                    except Exception:
                                        _err_fin += 1
                                    if _i_fin % 50 == 0:
                                        _prog_fin.progress(
                                            (_i_fin + 1) / _total_fin,
                                            text=f"Importando… {_i_fin + 1}/{_total_fin}"
                                        )
                        _conn_fin.close()
                        _prog_fin.progress(1.0, text="Concluído!")
                        st.success(
                            f"✅ **{_ok_fin}** parcelas importadas como **aberto**. "
                            f"{_err_fin} erros."
                        )
                        st.rerun()
            except Exception as _e_fin:
                st.error(f"Erro ao ler CSV: {_e_fin}")

elif pagina == "📣 Mala Direta":
    if _role == "vendas":
        st.error("🔒 Área restrita — somente administradores.")
        st.stop()

    st.subheader("📣 Mala Direta — Disparos em Massa")
    st.caption(
        "Identifique clientes inativos e aniversariantes e dispare mensagens "
        "WhatsApp via n8n + Evolution API com um clique."
    )

    _wh_url_md = _get_webhook_url()
    if not _wh_url_md:
        st.warning(
            "⚠️ Webhook n8n não configurado. "
            "Acesse **Administração → ⚙️ Configurações** para salvar a URL."
        )

    _vnd_md = st.session_state.get("username", "admin")
    tab_inat, tab_aniv = st.tabs(["😴 Inativos +60 dias", "🎂 Aniversariantes do Mês"])

    # ════════════════════════════════════════════════════════
    # TAB: Inativos > 60 dias
    # ════════════════════════════════════════════════════════
    with tab_inat:
        st.caption("Clientes com última compra há mais de 60 dias.")

        df_inat = run_query("""
            SELECT c.id::text AS cliente_id,
                   c.nome,
                   COALESCE(c.whatsapp, '') AS fone,
                   MAX(v.data_venda)::date               AS ultima_compra,
                   EXTRACT(DAY FROM (CURRENT_DATE - MAX(v.data_venda)))::int AS dias_sem_comprar,
                   (
                       SELECT p2.nome
                       FROM itens_venda iv2
                       JOIN vendas v2 ON v2.id = iv2.venda_id
                       LEFT JOIN produtos p2 ON p2.id = iv2.produto_id
                       WHERE v2.cliente_id = c.id
                       ORDER BY v2.data_venda DESC
                       LIMIT 1
                   ) AS ultimo_item
            FROM clientes c
            JOIN vendas v ON v.cliente_id = c.id
            WHERE c.ativo = true
            GROUP BY c.id, c.nome, c.whatsapp
            HAVING EXTRACT(DAY FROM (CURRENT_DATE - MAX(v.data_venda)))::int > 60
            ORDER BY dias_sem_comprar DESC
        """)

        if df_inat.empty:
            st.success("✅ Nenhum cliente inativo há mais de 60 dias.")
        else:
            st.metric("Clientes inativos", len(df_inat))

            # Cabeçalho
            _ih1, _ih2, _ih3, _ih4, _ih5 = st.columns([2.5, 1.5, 1.2, 2, 1])
            _ih1.markdown("**Cliente**"); _ih2.markdown("**Último item**")
            _ih3.markdown("**Dias**");    _ih4.markdown("**WhatsApp**"); _ih5.markdown("")
            st.markdown("<hr style='margin:4px 0 8px'>", unsafe_allow_html=True)

            for _, _ri in df_inat.iterrows():
                _ic1, _ic2, _ic3, _ic4, _ic5 = st.columns([2.5, 1.5, 1.2, 2, 1])
                _ic1.write(str(_ri["nome"]))
                _ic2.write(str(_ri["ultimo_item"] or "—")[:22])
                _ic3.write(f"{int(_ri['dias_sem_comprar'])}d")
                _ic4.write(str(_ri["fone"]) or "—")
                if _ic5.button("📱", key=f"inat_wpp_{_ri['cliente_id']}",
                               help="Disparar mensagem"):
                    _abord = _abordagem_prospeccao(str(_ri["ultimo_item"] or ""))
                    _msg_i = (
                        f"Olá {str(_ri['nome']).split()[0]}! Sentimos sua falta na "
                        f"GM Homem Itaúna. {_abord} Te esperamos! 💛"
                    )
                    _ok, _err = _disparar_whatsapp(
                        cliente_id=_ri["cliente_id"],
                        telefone=str(_ri["fone"]),
                        nome=str(_ri["nome"]),
                        msg_corpo=_msg_i,
                        vendedora=_vnd_md,
                    )
                    st.toast("🚀 Comando enviado ao n8n!" if _ok else f"❌ {_err}")

            st.markdown("---")
            _msg_massa_i = st.text_area(
                "Mensagem padrão (usada no 'Enviar para Todos')",
                value=(
                    "Olá {nome}! Sentimos sua falta na GM Homem Itaúna. "
                    "Temos novidades incríveis esperando por você. Venha nos visitar! 💛"
                ),
                height=90,
                key="inat_msg_massa",
            )
            if st.button(
                f"📤 Enviar para Todos os {len(df_inat)} inativos",
                key="inat_enviar_todos",
                type="primary",
                disabled=not bool(_wh_url_md),
            ):
                _erros_i = 0
                _prog_i  = st.progress(0)
                for _idx_i, (_, _ri) in enumerate(df_inat.iterrows()):
                    _msg_sub = _msg_massa_i.replace("{nome}", str(_ri["nome"]).split()[0])
                    _ok, _ = _disparar_whatsapp(
                        cliente_id=_ri["cliente_id"],
                        telefone=str(_ri["fone"]),
                        nome=str(_ri["nome"]),
                        msg_corpo=_msg_sub,
                        vendedora=_vnd_md,
                        webhook_url=_wh_url_md,
                    )
                    if not _ok:
                        _erros_i += 1
                    _prog_i.progress((_idx_i + 1) / len(df_inat))
                    import time as _time; _time.sleep(0.5)  # delay anti-flood
                if _erros_i == 0:
                    st.toast(f"🚀 {len(df_inat)} mensagens enviadas ao n8n!", icon="✅")
                else:
                    st.warning(f"{len(df_inat) - _erros_i} enviadas, {_erros_i} com erro.")

    # ════════════════════════════════════════════════════════
    # TAB: Aniversariantes do Mês
    # ════════════════════════════════════════════════════════
    with tab_aniv:
        st.caption("Clientes que fazem aniversário neste mês (campo Nascimento preenchido).")

        _mes_atual_num = date.today().month
        df_aniv = run_query(f"""
            SELECT c.id::text AS cliente_id,
                   c.nome,
                   COALESCE(c.whatsapp, '') AS fone,
                   c.data_nascimento,
                   EXTRACT(DAY FROM c.data_nascimento)::int AS dia_aniv
            FROM clientes c
            WHERE c.ativo = true
              AND EXTRACT(MONTH FROM c.data_nascimento) = {_mes_atual_num}
            ORDER BY dia_aniv
        """)

        if df_aniv.empty:
            st.info("Nenhum aniversariante cadastrado para este mês.")
        else:
            st.metric("Aniversariantes este mês", len(df_aniv))

            _ah1, _ah2, _ah3, _ah4 = st.columns([2.5, 1.2, 2, 1])
            _ah1.markdown("**Cliente**"); _ah2.markdown("**Dia**")
            _ah3.markdown("**WhatsApp**"); _ah4.markdown("")
            st.markdown("<hr style='margin:4px 0 8px'>", unsafe_allow_html=True)

            for _, _ra in df_aniv.iterrows():
                _ac1, _ac2, _ac3, _ac4 = st.columns([2.5, 1.2, 2, 1])
                _ac1.write(str(_ra["nome"]))
                _ac2.write(f"dia {int(_ra['dia_aniv'])}")
                _ac3.write(str(_ra["fone"]) or "—")
                if _ac4.button("🎂", key=f"aniv_wpp_{_ra['cliente_id']}",
                               help="Enviar parabéns"):
                    _msg_a = (
                        f"Feliz Aniversário, {str(_ra['nome']).split()[0]}! 🎉🎂 "
                        f"A GM Homem Itaúna deseja um dia incrível para você! "
                        f"Temos uma surpresa especial esperando. Venha nos visitar! 💛"
                    )
                    _ok, _err = _disparar_whatsapp(
                        cliente_id=_ra["cliente_id"],
                        telefone=str(_ra["fone"]),
                        nome=str(_ra["nome"]),
                        msg_corpo=_msg_a,
                        vendedora=_vnd_md,
                    )
                    st.toast("🎉 Parabéns enviado via n8n!" if _ok else f"❌ {_err}")

            st.markdown("---")
            if st.button(
                f"🎂 Enviar Parabéns para Todos os {len(df_aniv)} aniversariantes",
                key="aniv_enviar_todos",
                type="primary",
                disabled=not bool(_wh_url_md),
            ):
                _erros_a = 0
                _prog_a  = st.progress(0)
                for _idx_a, (_, _ra) in enumerate(df_aniv.iterrows()):
                    _msg_sub_a = (
                        f"Feliz Aniversário, {str(_ra['nome']).split()[0]}! 🎉🎂 "
                        f"A GM Homem Itaúna deseja um dia incrível para você! "
                        f"Temos uma surpresa especial esperando. Venha nos visitar! 💛"
                    )
                    _ok, _ = _disparar_whatsapp(
                        cliente_id=_ra["cliente_id"],
                        telefone=str(_ra["fone"]),
                        nome=str(_ra["nome"]),
                        msg_corpo=_msg_sub_a,
                        vendedora=_vnd_md,
                        webhook_url=_wh_url_md,
                    )
                    if not _ok:
                        _erros_a += 1
                    _prog_a.progress((_idx_a + 1) / len(df_aniv))
                    import time as _time; _time.sleep(0.5)
                if _erros_a == 0:
                    st.toast(f"🎉 {len(df_aniv)} parabéns enviados!", icon="✅")
                else:
                    st.warning(f"{len(df_aniv)-_erros_a} enviados, {_erros_a} com erro.")

elif pagina == "🔴 Inadimplentes":
    if _role == "vendas":
        st.error("🔒 Área restrita — somente administradores.")
        st.stop()

    st.subheader("🔴 Inadimplentes — Clientes em Atraso")
    st.caption(
        "Clientes com parcelas vencidas. "
        "Juros calculados automaticamente: **multa 2% + 0,1% ao dia**."
    )

    df_lv = run_query("SELECT * FROM lista_vermelha ORDER BY total_em_aberto DESC")

    if df_lv.empty:
        st.success("Nenhum inadimplente no momento.")
    else:
        hoje_lv = date.today()

        # Calcular juros projetados para cada cliente
        juros_projetados = []
        totais_com_juros = []
        for _, row_lv in df_lv.iterrows():
            dias = int(row_lv.get("max_dias_atraso") or 0)
            tot  = float(row_lv.get("total_em_aberto") or 0)
            j, t = calcular_juros(tot, dias)
            juros_projetados.append(j)
            totais_com_juros.append(t)
        df_lv = df_lv.copy()
        df_lv["juros_projetado"]  = juros_projetados
        df_lv["total_com_juros"]  = totais_com_juros

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Inadimplentes", len(df_lv))
        col_m2.metric("Total em Aberto", f"R$ {df_lv['total_em_aberto'].sum():,.2f}")
        col_m3.metric("Total c/ Juros",  f"R$ {df_lv['total_com_juros'].sum():,.2f}")

        st.markdown("---")

        # Cabeçalho
        h_lv = st.columns([2.2, 1.3, 1.4, 1.4, 1.3, 1.5, 2])
        for col_h, lbl in zip(h_lv, ["Cliente", "Parcelas", "Em Aberto", "Juros", "Total c/J", "Dias Atr.", ""]):
            col_h.markdown(f"**{lbl}**")
        st.markdown("<hr style='margin:4px 0 8px'>", unsafe_allow_html=True)

        for _, row in df_lv.iterrows():
            c_nome, c_parc, c_ab, c_j, c_t, c_dias, c_btn = st.columns([2.2, 1.3, 1.4, 1.4, 1.3, 1.5, 2])
            c_nome.markdown(f"**{row['cliente']}**")
            c_parc.write(str(row.get("parcelas_em_aberto", "—")))
            c_ab.write(f"R$ {float(row['total_em_aberto']):,.2f}")
            c_j.markdown(f"🔺 R$ {float(row['juros_projetado']):,.2f}")
            c_t.markdown(f"**R$ {float(row['total_com_juros']):,.2f}**")
            dias_lv = int(row.get("max_dias_atraso") or 0)
            c_dias.markdown(f"🔴 {dias_lv}d")

            cli_id = str(row.get("cliente_id", ""))
            wpp    = str(row["whatsapp"]) if pd.notna(row.get("whatsapp")) else ""
            valor  = float(row["total_com_juros"])

            c1_btn, c2_btn = c_btn.columns(2)
            if wpp:
                if c1_btn.button("📲", key=f"cobr_{cli_id}", help="Enviar cobrança WhatsApp",
                                  use_container_width=True):
                    ok, detalhe = enviar_webhook_cobranca(cli_id, wpp, valor)
                    if ok:
                        st.success(f"Cobrança enviada para **{row['cliente']}**.")
                    else:
                        st.error(f"Falha: {detalhe}")
            else:
                c1_btn.caption("—")
            if c2_btn.button("📋", key=f"lv_parc_{cli_id}", help="Ver / baixar parcelas",
                              use_container_width=True):
                _dlg_baixa_cliente(
                    str(row["cliente"]),
                    cli_id,
                    _role,
                    st.session_state.get("username", ""),
                )

# ════════════════════════════════════════════════════════════════════════════
# GM HOMEM AI — Página Central de Inteligência
# ════════════════════════════════════════════════════════════════════════════
elif pagina == "✨ GM Homem AI":
    if st.session_state.get("_nav_target") == "✨ GM Homem AI":
        st.session_state.pop("_nav_target", None)
    render_manu_ai(_role)
