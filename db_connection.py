"""
db_connection.py — Módulo único de conexão PostgreSQL
Loja Manu Itaúna | JGAutomações.AI

Problema resolvido: @st.cache_resource cacheava uma única conexão psycopg2
que expirava silenciosamente, fazendo run_query() retornar DataFrame vazio.

Solução: ThreadedConnectionPool com reconnect automático.
"""
import os
import psycopg2
import psycopg2.pool
import psycopg2.extensions
import pandas as pd
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# ── Parâmetros de conexão lidos do ambiente (carregado pelo systemd via EnvironmentFile)
def _get_params() -> dict:
    return {
        "host":     os.getenv("DB_HOST", "127.0.0.1"),
        "port":     int(os.getenv("DB_PORT", 5432)),
        "dbname":   os.getenv("DB_NAME", "loja_manu"),
        "user":     os.getenv("DB_USER", "jgadmin"),
        "password": os.getenv("DB_PASS", os.getenv("DB_PASSWORD", "")),
    }

# ── Pool singleton (uma instância por processo Streamlit) ─────────────────────
_pool: psycopg2.pool.ThreadedConnectionPool | None = None

def _get_pool() -> psycopg2.pool.ThreadedConnectionPool:
    global _pool
    if _pool is not None:
        return _pool
    params = _get_params()
    _pool = psycopg2.pool.ThreadedConnectionPool(minconn=1, maxconn=10, **params)
    return _pool

def _reset_pool() -> None:
    """Fecha o pool e força recriação na próxima chamada."""
    global _pool
    if _pool:
        try:
            _pool.closeall()
        except Exception:
            pass
    _pool = None

# ── Gerenciador de contexto para conexão ─────────────────────────────────────
@contextmanager
def get_conn():
    """
    Uso:
        with get_conn() as conn:
            pd.read_sql(query, conn)

    - Obtém conexão do pool
    - Detecta e recupera conexões fechadas/expiradas automaticamente
    - Devolve sempre ao pool no finally
    """
    pool = _get_pool()
    conn = pool.getconn()

    # Verificar se a conexão está viva; reconectar se necessário
    if conn.closed:
        try:
            pool.putconn(conn, close=True)
        except Exception:
            pass
        conn = pool.getconn()

    try:
        # Ping rápido para detectar conexão zumbi
        conn.cursor().execute("SELECT 1")
    except (psycopg2.OperationalError, psycopg2.InterfaceError):
        # Conexão morta — resetar pool e tentar de novo
        logger.warning("db_connection: conexão morta detectada, recriando pool...")
        try:
            pool.putconn(conn, close=True)
        except Exception:
            pass
        _reset_pool()
        pool = _get_pool()
        conn = pool.getconn()

    try:
        yield conn
        conn.commit()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        try:
            pool.putconn(conn)
        except Exception:
            pass

# ── Helpers públicos ──────────────────────────────────────────────────────────
def run_query(sql: str, params=None) -> pd.DataFrame:
    """SELECT → DataFrame. Retorna DataFrame vazio em erro, logando a causa."""
    try:
        with get_conn() as conn:
            return pd.read_sql_query(sql, conn, params=params)
    except Exception as e:
        logger.error("run_query falhou: %s | SQL: %.200s", e, sql)
        return pd.DataFrame()

def run_command(sql: str, params: tuple = ()) -> bool:
    """INSERT/UPDATE/DELETE. Retorna True em sucesso."""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
        return True
    except Exception as e:
        logger.error("run_command falhou: %s | SQL: %.200s", e, sql)
        return False

def testar_conexao() -> tuple[bool, dict | str]:
    """Retorna (ok, info_dict) ou (False, mensagem_erro)."""
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    (SELECT COUNT(*) FROM clientes)                             AS clientes,
                    (SELECT COUNT(*) FROM clientes_legados)                     AS clientes_leg,
                    (SELECT COUNT(*) FROM produtos)                             AS produtos,
                    (SELECT COUNT(*) FROM duplicatas_abertas WHERE status='Pendente') AS parcelas
            """)
            row = cur.fetchone()
        p = _get_params()
        return True, {
            "host": p["host"], "port": p["port"], "banco": p["dbname"],
            "clientes": row[0], "clientes_legados": row[1],
            "produtos": row[2], "parcelas_abertas": row[3],
        }
    except Exception as e:
        return False, str(e)
