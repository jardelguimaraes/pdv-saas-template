--
-- PostgreSQL database dump
--

\restrict 5zdKIIKRDOBxxqdi76G5mdK2ZGHmZLaFbRkgqPleYRWDf23JtlGk11WPQrhaBGC

-- Dumped from database version 16.13
-- Dumped by pg_dump version 16.13

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: unaccent; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS unaccent WITH SCHEMA public;


--
-- Name: EXTENSION unaccent; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION unaccent IS 'text search dictionary that removes accents';


--
-- Name: fn_nr_documento_cr(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_nr_documento_cr() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.nr_documento IS NULL OR NEW.nr_documento = '' THEN
        NEW.nr_documento := 'CR-' || LPAD(
            (SELECT COUNT(*) + 1 FROM contas_receber)::text, 5, '0');
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_nr_documento_cr() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: chat_ia_tokens; Type: TABLE; Schema: public; Owner: jgadmin
--

CREATE TABLE public.chat_ia_tokens (
    mes text NOT NULL,
    chars bigint DEFAULT 0 NOT NULL,
    atualizado_em timestamp with time zone DEFAULT now()
);


ALTER TABLE public.chat_ia_tokens OWNER TO jgadmin;

--
-- Name: clientes; Type: TABLE; Schema: public; Owner: jgadmin
--

CREATE TABLE public.clientes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    nome text NOT NULL,
    whatsapp text,
    cpf text,
    data_nascimento date,
    tags text[],
    ultima_compra timestamp with time zone,
    ativo boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    email text,
    cep text,
    endereco text,
    numero text,
    bairro text,
    cidade text,
    observacoes text,
    codigo_externo text,
    observacao text
);


ALTER TABLE public.clientes OWNER TO jgadmin;

--
-- Name: clientes_legados; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clientes_legados (
    id integer NOT NULL,
    codigo_legado text NOT NULL,
    nome text NOT NULL,
    cpf text,
    celular text,
    email text,
    limite_credito numeric(10,2) DEFAULT 0,
    dt_nascimento date,
    cidade text,
    bairro text,
    importado_em timestamp without time zone DEFAULT now()
);


ALTER TABLE public.clientes_legados OWNER TO postgres;

--
-- Name: clientes_legados_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.clientes_legados_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.clientes_legados_id_seq OWNER TO postgres;

--
-- Name: clientes_legados_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.clientes_legados_id_seq OWNED BY public.clientes_legados.id;


--
-- Name: condicionais; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.condicionais (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    numero integer NOT NULL,
    cliente_nome text NOT NULL,
    cliente_telefone text,
    vendedora text,
    dt_saida date DEFAULT CURRENT_DATE NOT NULL,
    dt_devolucao date NOT NULL,
    prazo_horas integer DEFAULT 24,
    status text DEFAULT 'aberto'::text,
    observacao text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.condicionais OWNER TO postgres;

--
-- Name: condicionais_numero_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.condicionais_numero_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.condicionais_numero_seq OWNER TO postgres;

--
-- Name: condicionais_numero_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.condicionais_numero_seq OWNED BY public.condicionais.numero;


--
-- Name: config_comissao; Type: TABLE; Schema: public; Owner: jgadmin
--

CREATE TABLE public.config_comissao (
    id bigint NOT NULL,
    codigo_vendedor text NOT NULL,
    nome_vendedor text,
    percentual numeric(5,2) DEFAULT 5.0 NOT NULL,
    ativo boolean DEFAULT true
);


ALTER TABLE public.config_comissao OWNER TO jgadmin;

--
-- Name: config_comissao_id_seq; Type: SEQUENCE; Schema: public; Owner: jgadmin
--

CREATE SEQUENCE public.config_comissao_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.config_comissao_id_seq OWNER TO jgadmin;

--
-- Name: config_comissao_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jgadmin
--

ALTER SEQUENCE public.config_comissao_id_seq OWNED BY public.config_comissao.id;


--
-- Name: config_geral; Type: TABLE; Schema: public; Owner: jgadmin
--

CREATE TABLE public.config_geral (
    chave text NOT NULL,
    valor text,
    atualizado_em timestamp with time zone DEFAULT now()
);


ALTER TABLE public.config_geral OWNER TO jgadmin;

--
-- Name: configuracoes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.configuracoes (
    id integer NOT NULL,
    chave character varying(100) NOT NULL,
    valor text,
    descricao text,
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.configuracoes OWNER TO postgres;

--
-- Name: configuracoes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.configuracoes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.configuracoes_id_seq OWNER TO postgres;

--
-- Name: configuracoes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.configuracoes_id_seq OWNED BY public.configuracoes.id;


--
-- Name: contas_a_pagar; Type: TABLE; Schema: public; Owner: jgadmin
--

CREATE TABLE public.contas_a_pagar (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    descricao text NOT NULL,
    categoria text,
    valor numeric(10,2),
    data_vencimento date,
    status text DEFAULT 'pendente'::text,
    comprovante_url text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.contas_a_pagar OWNER TO jgadmin;

--
-- Name: contas_receber; Type: TABLE; Schema: public; Owner: jgadmin
--

CREATE TABLE public.contas_receber (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    venda_id uuid,
    valor_parcela numeric(10,2),
    data_vencimento date,
    status text DEFAULT 'aberto'::text,
    lembrete_enviado boolean DEFAULT false,
    data_pagamento date,
    valor_pago_final numeric(10,2),
    juros_isento boolean DEFAULT false,
    isento_por text,
    nr_documento text,
    detalhes_venda text,
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.contas_receber OWNER TO jgadmin;

--
-- Name: duplicatas_abertas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.duplicatas_abertas (
    id integer NOT NULL,
    codigo_cliente text NOT NULL,
    nome_cliente text,
    documento text NOT NULL,
    ordem text NOT NULL,
    dt_emissao date,
    dt_vencimento date,
    modalidade text DEFAULT 'Crediario'::text,
    valor_original numeric(10,2) NOT NULL,
    valor_saldo numeric(10,2) NOT NULL,
    valor_pago_total numeric(10,2) DEFAULT 0,
    observacao text,
    pedido text,
    vendedor text,
    status text DEFAULT 'Pendente'::text,
    dt_baixa date,
    forma_recebimento text,
    isentou_encargos boolean DEFAULT false,
    origem text DEFAULT 'legado'::text
);


ALTER TABLE public.duplicatas_abertas OWNER TO postgres;

--
-- Name: duplicatas_abertas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.duplicatas_abertas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.duplicatas_abertas_id_seq OWNER TO postgres;

--
-- Name: duplicatas_abertas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.duplicatas_abertas_id_seq OWNED BY public.duplicatas_abertas.id;


--
-- Name: duplicatas_abertas_itens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.duplicatas_abertas_itens (
    id integer NOT NULL,
    documento text NOT NULL,
    cliente_codigo text NOT NULL,
    cliente_nome text,
    referencia text,
    descricao text,
    cor text,
    quantidade numeric(10,2),
    valor_unitario numeric(10,2),
    valor_total numeric(10,2),
    origem text DEFAULT 'SGA_SCRRR06'::text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.duplicatas_abertas_itens OWNER TO postgres;

--
-- Name: duplicatas_abertas_itens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.duplicatas_abertas_itens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.duplicatas_abertas_itens_id_seq OWNER TO postgres;

--
-- Name: duplicatas_abertas_itens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.duplicatas_abertas_itens_id_seq OWNED BY public.duplicatas_abertas_itens.id;


--
-- Name: duplicatas_bkp_sync_29042026; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.duplicatas_bkp_sync_29042026 (
    id integer,
    codigo_cliente text,
    nome_cliente text,
    documento text,
    ordem text,
    dt_emissao date,
    dt_vencimento date,
    modalidade text,
    valor_original numeric(10,2),
    valor_saldo numeric(10,2),
    valor_pago_total numeric(10,2),
    observacao text,
    pedido text,
    vendedor text,
    status text,
    dt_baixa date,
    forma_recebimento text,
    isentou_encargos boolean,
    origem text,
    bkp_em timestamp with time zone
);


ALTER TABLE public.duplicatas_bkp_sync_29042026 OWNER TO postgres;

--
-- Name: estoque; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.estoque (
    id integer NOT NULL,
    nome text NOT NULL,
    preco_custo numeric(10,2) DEFAULT 0,
    preco_venda numeric(10,2) DEFAULT 0,
    quantidade_atual integer DEFAULT 0,
    categoria text,
    ativo boolean DEFAULT true,
    data_lancamento date DEFAULT CURRENT_DATE
);


ALTER TABLE public.estoque OWNER TO postgres;

--
-- Name: estoque_historico; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.estoque_historico (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    produto_id uuid NOT NULL,
    tipo character varying(20) DEFAULT 'entrada'::character varying NOT NULL,
    quantidade integer NOT NULL,
    preco_custo numeric(10,2),
    preco_venda numeric(10,2),
    origem character varying(50) DEFAULT 'telegram'::character varying,
    observacao text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.estoque_historico OWNER TO postgres;

--
-- Name: estoque_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.estoque_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.estoque_id_seq OWNER TO postgres;

--
-- Name: estoque_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.estoque_id_seq OWNED BY public.estoque.id;


--
-- Name: fornecedores; Type: TABLE; Schema: public; Owner: jgadmin
--

CREATE TABLE public.fornecedores (
    id bigint NOT NULL,
    nome text NOT NULL,
    tipo text,
    ativo boolean DEFAULT true
);


ALTER TABLE public.fornecedores OWNER TO jgadmin;

--
-- Name: fornecedores_id_seq; Type: SEQUENCE; Schema: public; Owner: jgadmin
--

CREATE SEQUENCE public.fornecedores_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fornecedores_id_seq OWNER TO jgadmin;

--
-- Name: fornecedores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jgadmin
--

ALTER SEQUENCE public.fornecedores_id_seq OWNED BY public.fornecedores.id;


--
-- Name: historico_legado; Type: TABLE; Schema: public; Owner: jgadmin
--

CREATE TABLE public.historico_legado (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    cliente_codigo text,
    cliente_id uuid,
    documento text,
    ordem text,
    dt_emissao date,
    dt_vencimento date,
    situacao_original text,
    modalidade text,
    valor_docto numeric(12,2) DEFAULT 0,
    observacao text,
    vendedor text,
    forma_pagto text,
    nro_parcelas text,
    status text DEFAULT 'baixado'::text NOT NULL,
    data_baixa date,
    baixa_por text,
    valor_recebido numeric(12,2),
    raw_data jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    juros_recebido numeric(10,2) DEFAULT 0,
    origem text DEFAULT 'CSV_ORIGINAL'::text
);


ALTER TABLE public.historico_legado OWNER TO jgadmin;

--
-- Name: historico_precos; Type: TABLE; Schema: public; Owner: jgadmin
--

CREATE TABLE public.historico_precos (
    id bigint NOT NULL,
    produto_id uuid NOT NULL,
    tipo_preco text NOT NULL,
    preco_antigo numeric(12,2),
    preco_novo numeric(12,2) NOT NULL,
    data_alteracao timestamp with time zone DEFAULT now() NOT NULL,
    usuario text,
    CONSTRAINT historico_precos_tipo_preco_check CHECK ((tipo_preco = ANY (ARRAY['custo'::text, 'venda'::text])))
);


ALTER TABLE public.historico_precos OWNER TO jgadmin;

--
-- Name: historico_precos_id_seq; Type: SEQUENCE; Schema: public; Owner: jgadmin
--

CREATE SEQUENCE public.historico_precos_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.historico_precos_id_seq OWNER TO jgadmin;

--
-- Name: historico_precos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jgadmin
--

ALTER SEQUENCE public.historico_precos_id_seq OWNED BY public.historico_precos.id;


--
-- Name: historico_quitado; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.historico_quitado (
    id integer NOT NULL,
    codigo_cliente text,
    nome_cliente text,
    documento text,
    ordem text,
    dt_emissao date,
    dt_vencimento date,
    dt_pagamento date,
    modalidade text,
    valor_docto numeric(10,2),
    valor_desconto numeric(10,2) DEFAULT 0,
    valor_juros_pagos numeric(10,2) DEFAULT 0,
    observacao text,
    vendedor text,
    pedido text,
    origem text DEFAULT 'legado'::text
);


ALTER TABLE public.historico_quitado OWNER TO postgres;

--
-- Name: historico_quitado_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.historico_quitado_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.historico_quitado_id_seq OWNER TO postgres;

--
-- Name: historico_quitado_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.historico_quitado_id_seq OWNED BY public.historico_quitado.id;


--
-- Name: itens_condicional; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.itens_condicional (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    condicional_id uuid,
    produto_id uuid,
    nome text NOT NULL,
    referencia text,
    tamanho text,
    quantidade integer DEFAULT 1,
    preco_unit numeric(10,2),
    devolvido boolean DEFAULT false
);


ALTER TABLE public.itens_condicional OWNER TO postgres;

--
-- Name: itens_historico_legado; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.itens_historico_legado (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    cliente_codigo text,
    documento text,
    ordem text,
    referencia text,
    descricao text,
    quantidade numeric(10,2),
    valor_unitario numeric(10,2),
    valor_total numeric(10,2),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.itens_historico_legado OWNER TO postgres;

--
-- Name: itens_venda; Type: TABLE; Schema: public; Owner: jgadmin
--

CREATE TABLE public.itens_venda (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    venda_id uuid NOT NULL,
    produto_id uuid NOT NULL,
    quantidade integer DEFAULT 1 NOT NULL,
    preco_unit numeric(10,2) NOT NULL,
    descricao text,
    preco_unitario numeric(10,2),
    subtotal numeric(10,2)
);


ALTER TABLE public.itens_venda OWNER TO jgadmin;

--
-- Name: vendas; Type: TABLE; Schema: public; Owner: jgadmin
--

CREATE TABLE public.vendas (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    cliente_id uuid,
    valor_total numeric(10,2),
    forma_pagamento text,
    status_pagamento text,
    data_venda timestamp with time zone DEFAULT now(),
    codigo_vendedor text,
    vendedor_nome text,
    observacao text,
    cupom_text text DEFAULT ''::text,
    parcelas integer DEFAULT 1
);


ALTER TABLE public.vendas OWNER TO jgadmin;

--
-- Name: lista_vermelha; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.lista_vermelha AS
 SELECT (c.id)::text AS cliente_id,
    c.nome AS cliente,
    c.whatsapp,
    (count(cr.id))::integer AS parcelas_em_aberto,
    sum(cr.valor_parcela) AS total_em_aberto,
    min(cr.data_vencimento) AS vencimento_mais_antigo,
    max((CURRENT_DATE - cr.data_vencimento)) AS max_dias_atraso
   FROM ((public.contas_receber cr
     JOIN public.vendas v ON ((cr.venda_id = v.id)))
     JOIN public.clientes c ON ((v.cliente_id = c.id)))
  WHERE ((cr.status = 'aberto'::text) AND (cr.data_vencimento < CURRENT_DATE))
  GROUP BY c.id, c.nome, c.whatsapp;


ALTER VIEW public.lista_vermelha OWNER TO postgres;

--
-- Name: manu_ai_sessao; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.manu_ai_sessao (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    chat_id text NOT NULL,
    ultimo_cliente_nome text,
    ultimo_cliente_lista jsonb,
    ultima_intencao text,
    ultima_consulta jsonb,
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.manu_ai_sessao OWNER TO postgres;

--
-- Name: metas_mensais; Type: TABLE; Schema: public; Owner: jgadmin
--

CREATE TABLE public.metas_mensais (
    id bigint NOT NULL,
    ano_mes text NOT NULL,
    meta_valor numeric(12,2) NOT NULL,
    criado_em timestamp with time zone DEFAULT now()
);


ALTER TABLE public.metas_mensais OWNER TO jgadmin;

--
-- Name: metas_mensais_id_seq; Type: SEQUENCE; Schema: public; Owner: jgadmin
--

CREATE SEQUENCE public.metas_mensais_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.metas_mensais_id_seq OWNER TO jgadmin;

--
-- Name: metas_mensais_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jgadmin
--

ALTER SEQUENCE public.metas_mensais_id_seq OWNED BY public.metas_mensais.id;


--
-- Name: movimentos_financeiros; Type: TABLE; Schema: public; Owner: jgadmin
--

CREATE TABLE public.movimentos_financeiros (
    id integer NOT NULL,
    parcela_id text,
    origem text,
    valor_pago numeric(10,2),
    forma_pagamento text,
    isentou_encargos boolean DEFAULT false,
    saldo_anterior numeric(10,2),
    saldo_posterior numeric(10,2),
    operador text,
    observacao text,
    data_movimento timestamp without time zone DEFAULT now()
);


ALTER TABLE public.movimentos_financeiros OWNER TO jgadmin;

--
-- Name: movimentos_financeiros_id_seq; Type: SEQUENCE; Schema: public; Owner: jgadmin
--

CREATE SEQUENCE public.movimentos_financeiros_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.movimentos_financeiros_id_seq OWNER TO jgadmin;

--
-- Name: movimentos_financeiros_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jgadmin
--

ALTER SEQUENCE public.movimentos_financeiros_id_seq OWNED BY public.movimentos_financeiros.id;


--
-- Name: oracle_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.oracle_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    store_id text DEFAULT 'loja_manu'::text NOT NULL,
    chat_id text NOT NULL,
    mensagem_input text,
    tool_chamada text,
    sql_executado text,
    resultado_resumo text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.oracle_log OWNER TO postgres;

--
-- Name: oracle_sessao; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.oracle_sessao (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    chat_id text NOT NULL,
    store_id text DEFAULT 'loja_manu'::text NOT NULL,
    ultimo_cliente_nome text,
    ultima_intencao text,
    historico_mensagens jsonb DEFAULT '[]'::jsonb,
    preferencias jsonb DEFAULT '{}'::jsonb,
    total_interacoes integer DEFAULT 0,
    tokens_consumidos integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.oracle_sessao OWNER TO postgres;

--
-- Name: oracle_stores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.oracle_stores (
    store_id text NOT NULL,
    nome_loja text NOT NULL,
    cidade text,
    nome_ai text DEFAULT 'Oracle AI'::text NOT NULL,
    nome_lojista text,
    telegram_chat_ids jsonb DEFAULT '[]'::jsonb,
    db_name text DEFAULT 'loja_manu'::text NOT NULL,
    cor_identidade text DEFAULT '#c9a84c'::text,
    plano text DEFAULT 'basico'::text,
    ativo boolean DEFAULT true,
    criado_em timestamp with time zone DEFAULT now()
);


ALTER TABLE public.oracle_stores OWNER TO postgres;

--
-- Name: pagamentos_balcao; Type: TABLE; Schema: public; Owner: jgadmin
--

CREATE TABLE public.pagamentos_balcao (
    id bigint NOT NULL,
    cliente_nome text NOT NULL,
    valor_abatido numeric(12,2) NOT NULL,
    operador text,
    observacao text,
    data_hora timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.pagamentos_balcao OWNER TO jgadmin;

--
-- Name: pagamentos_balcao_id_seq; Type: SEQUENCE; Schema: public; Owner: jgadmin
--

CREATE SEQUENCE public.pagamentos_balcao_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pagamentos_balcao_id_seq OWNER TO jgadmin;

--
-- Name: pagamentos_balcao_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jgadmin
--

ALTER SEQUENCE public.pagamentos_balcao_id_seq OWNED BY public.pagamentos_balcao.id;


--
-- Name: produto_variacoes; Type: TABLE; Schema: public; Owner: jgadmin
--

CREATE TABLE public.produto_variacoes (
    id bigint NOT NULL,
    produto_id uuid NOT NULL,
    tamanho text NOT NULL,
    estoque integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.produto_variacoes OWNER TO jgadmin;

--
-- Name: produto_variacoes_id_seq; Type: SEQUENCE; Schema: public; Owner: jgadmin
--

CREATE SEQUENCE public.produto_variacoes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.produto_variacoes_id_seq OWNER TO jgadmin;

--
-- Name: produto_variacoes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jgadmin
--

ALTER SEQUENCE public.produto_variacoes_id_seq OWNED BY public.produto_variacoes.id;


--
-- Name: produtos; Type: TABLE; Schema: public; Owner: jgadmin
--

CREATE TABLE public.produtos (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    codigo_barras text,
    nome text NOT NULL,
    preco_custo numeric(10,2),
    preco_venda numeric(10,2),
    estoque_atual integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    categoria text,
    fornecedor_ref text,
    descricao_detalhada text,
    estoque_minimo integer DEFAULT 0,
    ultima_entrada date,
    foto_url text,
    ativo boolean DEFAULT true NOT NULL,
    data_lancamento date DEFAULT CURRENT_DATE,
    observacao text,
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.produtos OWNER TO jgadmin;

--
-- Name: produtos_legados; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.produtos_legados (
    id integer NOT NULL,
    referencia text,
    descricao text,
    grupo text,
    subgrupo text,
    colecao text,
    preco_venda numeric(10,2) DEFAULT 0,
    preco_custo numeric(10,2) DEFAULT 0,
    unidade text,
    marca text
);


ALTER TABLE public.produtos_legados OWNER TO postgres;

--
-- Name: produtos_legados_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.produtos_legados_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.produtos_legados_id_seq OWNER TO postgres;

--
-- Name: produtos_legados_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.produtos_legados_id_seq OWNED BY public.produtos_legados.id;


--
-- Name: seq_condicional; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.seq_condicional
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.seq_condicional OWNER TO postgres;

--
-- Name: vales_troca; Type: TABLE; Schema: public; Owner: jgadmin
--

CREATE TABLE public.vales_troca (
    id bigint NOT NULL,
    cliente_id uuid NOT NULL,
    venda_id uuid,
    valor numeric(12,2) NOT NULL,
    saldo numeric(12,2) NOT NULL,
    operador text,
    motivo text,
    ativo boolean DEFAULT true,
    criado_em timestamp with time zone DEFAULT now()
);


ALTER TABLE public.vales_troca OWNER TO jgadmin;

--
-- Name: vales_troca_id_seq; Type: SEQUENCE; Schema: public; Owner: jgadmin
--

CREATE SEQUENCE public.vales_troca_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vales_troca_id_seq OWNER TO jgadmin;

--
-- Name: vales_troca_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jgadmin
--

ALTER SEQUENCE public.vales_troca_id_seq OWNED BY public.vales_troca.id;


--
-- Name: vw_clientes_completos; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_clientes_completos AS
 SELECT (c.id)::text AS id,
    c.nome,
    c.cpf,
    c.whatsapp AS celular,
    (c.created_at)::date AS data_cadastro,
    c.cidade,
    'Novo Sistema'::text AS origem,
    ( SELECT (max(v.data_venda))::date AS max
           FROM public.vendas v
          WHERE (v.cliente_id = c.id)) AS ultima_compra,
    ( SELECT COALESCE(sum(v.valor_total), (0)::numeric) AS "coalesce"
           FROM public.vendas v
          WHERE (v.cliente_id = c.id)) AS total_gasto,
    c.codigo_externo AS codigo_legado
   FROM public.clientes c
UNION ALL
 SELECT cl.codigo_legado AS id,
    cl.nome,
    cl.cpf,
    cl.celular,
    (cl.importado_em)::date AS data_cadastro,
    cl.cidade,
    'Sistema Antigo'::text AS origem,
    ( SELECT max(hq.dt_emissao) AS max
           FROM public.historico_legado hq
          WHERE ((hq.cliente_codigo = cl.codigo_legado) AND (hq.status = 'baixado'::text))) AS ultima_compra,
    ( SELECT COALESCE(sum(hq.valor_docto), (0)::numeric) AS "coalesce"
           FROM public.historico_legado hq
          WHERE (hq.cliente_codigo = cl.codigo_legado)) AS total_gasto,
    cl.codigo_legado
   FROM public.clientes_legados cl
  WHERE ((TRIM(BOTH FROM cl.nome) <> 'CONSUMIDOR FINAL'::text) AND (cl.nome IS NOT NULL) AND (NOT (EXISTS ( SELECT 1
           FROM public.clientes c2
          WHERE (c2.codigo_externo = cl.codigo_legado)))));


ALTER VIEW public.vw_clientes_completos OWNER TO postgres;

--
-- Name: vw_estoque_completo; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_estoque_completo AS
 SELECT id,
    nome,
    categoria,
    preco_venda,
    preco_custo,
    estoque_atual AS quantidade_atual,
        CASE
            WHEN (estoque_atual <= 0) THEN 'Sem estoque'::text
            WHEN (estoque_atual <= 3) THEN 'Crítico'::text
            WHEN (estoque_atual <= 10) THEN 'Baixo'::text
            ELSE 'Normal'::text
        END AS status_estoque,
    ativo
   FROM public.produtos p;


ALTER VIEW public.vw_estoque_completo OWNER TO postgres;

--
-- Name: vw_recebiveis; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.vw_recebiveis AS
 SELECT DISTINCT ON (cr.id) (cr.id)::text AS id,
    COALESCE(c.nome, da.nome_cliente, 'Não identificado'::text) AS nome_cliente,
    COALESCE(c.cpf, ''::text) AS cpf,
    COALESCE((c.id)::text, ''::text) AS cliente_id,
    cr.nr_documento AS documento,
    hl.dt_emissao,
    cr.data_vencimento AS dt_vencimento,
    cr.valor_parcela AS valor_saldo,
    cr.status,
    COALESCE(hl.modalidade, da.modalidade, 'Crediario'::text) AS modalidade,
    'banco'::text AS origem,
    COALESCE(hl.observacao, ''::text) AS observacao,
        CASE
            WHEN ((cr.data_vencimento < CURRENT_DATE) AND (cr.status = 'aberto'::text)) THEN (CURRENT_DATE - cr.data_vencimento)
            ELSE 0
        END AS dias_atraso
   FROM (((public.contas_receber cr
     LEFT JOIN public.historico_legado hl ON ((cr.nr_documento = hl.documento)))
     LEFT JOIN public.clientes c ON ((hl.cliente_id = c.id)))
     LEFT JOIN public.duplicatas_abertas da ON ((cr.nr_documento = da.documento)))
  WHERE (cr.status = 'aberto'::text)
UNION ALL
 SELECT (da.id)::text AS id,
    COALESCE(da.nome_cliente, cl.nome, 'Não identificado'::text) AS nome_cliente,
    COALESCE(cl.cpf, ''::text) AS cpf,
    COALESCE((c2.id)::text, ''::text) AS cliente_id,
    da.documento,
    da.dt_emissao,
    da.dt_vencimento,
    da.valor_saldo,
    da.status,
    da.modalidade,
    'legado'::text AS origem,
    COALESCE(da.observacao, ''::text) AS observacao,
        CASE
            WHEN ((da.dt_vencimento < CURRENT_DATE) AND (da.status = 'Pendente'::text)) THEN (CURRENT_DATE - da.dt_vencimento)
            ELSE 0
        END AS dias_atraso
   FROM ((public.duplicatas_abertas da
     LEFT JOIN public.clientes_legados cl ON ((da.codigo_cliente = cl.codigo_legado)))
     LEFT JOIN public.clientes c2 ON ((c2.codigo_externo = da.codigo_cliente)))
  WHERE ((da.status = 'Pendente'::text) AND (NOT (EXISTS ( SELECT 1
           FROM public.contas_receber cr2
          WHERE (cr2.nr_documento = da.documento)))));


ALTER VIEW public.vw_recebiveis OWNER TO postgres;

--
-- Name: clientes_legados id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clientes_legados ALTER COLUMN id SET DEFAULT nextval('public.clientes_legados_id_seq'::regclass);


--
-- Name: condicionais numero; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.condicionais ALTER COLUMN numero SET DEFAULT nextval('public.condicionais_numero_seq'::regclass);


--
-- Name: config_comissao id; Type: DEFAULT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.config_comissao ALTER COLUMN id SET DEFAULT nextval('public.config_comissao_id_seq'::regclass);


--
-- Name: configuracoes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configuracoes ALTER COLUMN id SET DEFAULT nextval('public.configuracoes_id_seq'::regclass);


--
-- Name: duplicatas_abertas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.duplicatas_abertas ALTER COLUMN id SET DEFAULT nextval('public.duplicatas_abertas_id_seq'::regclass);


--
-- Name: duplicatas_abertas_itens id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.duplicatas_abertas_itens ALTER COLUMN id SET DEFAULT nextval('public.duplicatas_abertas_itens_id_seq'::regclass);


--
-- Name: estoque id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estoque ALTER COLUMN id SET DEFAULT nextval('public.estoque_id_seq'::regclass);


--
-- Name: fornecedores id; Type: DEFAULT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.fornecedores ALTER COLUMN id SET DEFAULT nextval('public.fornecedores_id_seq'::regclass);


--
-- Name: historico_precos id; Type: DEFAULT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.historico_precos ALTER COLUMN id SET DEFAULT nextval('public.historico_precos_id_seq'::regclass);


--
-- Name: historico_quitado id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historico_quitado ALTER COLUMN id SET DEFAULT nextval('public.historico_quitado_id_seq'::regclass);


--
-- Name: metas_mensais id; Type: DEFAULT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.metas_mensais ALTER COLUMN id SET DEFAULT nextval('public.metas_mensais_id_seq'::regclass);


--
-- Name: movimentos_financeiros id; Type: DEFAULT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.movimentos_financeiros ALTER COLUMN id SET DEFAULT nextval('public.movimentos_financeiros_id_seq'::regclass);


--
-- Name: pagamentos_balcao id; Type: DEFAULT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.pagamentos_balcao ALTER COLUMN id SET DEFAULT nextval('public.pagamentos_balcao_id_seq'::regclass);


--
-- Name: produto_variacoes id; Type: DEFAULT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.produto_variacoes ALTER COLUMN id SET DEFAULT nextval('public.produto_variacoes_id_seq'::regclass);


--
-- Name: produtos_legados id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.produtos_legados ALTER COLUMN id SET DEFAULT nextval('public.produtos_legados_id_seq'::regclass);


--
-- Name: vales_troca id; Type: DEFAULT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.vales_troca ALTER COLUMN id SET DEFAULT nextval('public.vales_troca_id_seq'::regclass);


--
-- Name: chat_ia_tokens chat_ia_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.chat_ia_tokens
    ADD CONSTRAINT chat_ia_tokens_pkey PRIMARY KEY (mes);


--
-- Name: clientes_legados clientes_legados_codigo_legado_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clientes_legados
    ADD CONSTRAINT clientes_legados_codigo_legado_key UNIQUE (codigo_legado);


--
-- Name: clientes_legados clientes_legados_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clientes_legados
    ADD CONSTRAINT clientes_legados_pkey PRIMARY KEY (id);


--
-- Name: clientes clientes_pkey; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.clientes
    ADD CONSTRAINT clientes_pkey PRIMARY KEY (id);


--
-- Name: condicionais condicionais_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.condicionais
    ADD CONSTRAINT condicionais_pkey PRIMARY KEY (id);


--
-- Name: config_comissao config_comissao_codigo_vendedor_key; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.config_comissao
    ADD CONSTRAINT config_comissao_codigo_vendedor_key UNIQUE (codigo_vendedor);


--
-- Name: config_comissao config_comissao_pkey; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.config_comissao
    ADD CONSTRAINT config_comissao_pkey PRIMARY KEY (id);


--
-- Name: config_geral config_geral_pkey; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.config_geral
    ADD CONSTRAINT config_geral_pkey PRIMARY KEY (chave);


--
-- Name: configuracoes configuracoes_chave_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configuracoes
    ADD CONSTRAINT configuracoes_chave_key UNIQUE (chave);


--
-- Name: configuracoes configuracoes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configuracoes
    ADD CONSTRAINT configuracoes_pkey PRIMARY KEY (id);


--
-- Name: contas_a_pagar contas_a_pagar_pkey; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.contas_a_pagar
    ADD CONSTRAINT contas_a_pagar_pkey PRIMARY KEY (id);


--
-- Name: contas_receber contas_receber_pkey; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.contas_receber
    ADD CONSTRAINT contas_receber_pkey PRIMARY KEY (id);


--
-- Name: duplicatas_abertas_itens duplicatas_abertas_itens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.duplicatas_abertas_itens
    ADD CONSTRAINT duplicatas_abertas_itens_pkey PRIMARY KEY (id);


--
-- Name: duplicatas_abertas duplicatas_abertas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.duplicatas_abertas
    ADD CONSTRAINT duplicatas_abertas_pkey PRIMARY KEY (id);


--
-- Name: estoque_historico estoque_historico_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estoque_historico
    ADD CONSTRAINT estoque_historico_pkey PRIMARY KEY (id);


--
-- Name: estoque estoque_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estoque
    ADD CONSTRAINT estoque_pkey PRIMARY KEY (id);


--
-- Name: fornecedores fornecedores_nome_key; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.fornecedores
    ADD CONSTRAINT fornecedores_nome_key UNIQUE (nome);


--
-- Name: fornecedores fornecedores_pkey; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.fornecedores
    ADD CONSTRAINT fornecedores_pkey PRIMARY KEY (id);


--
-- Name: historico_legado historico_legado_pkey; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.historico_legado
    ADD CONSTRAINT historico_legado_pkey PRIMARY KEY (id);


--
-- Name: historico_precos historico_precos_pkey; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.historico_precos
    ADD CONSTRAINT historico_precos_pkey PRIMARY KEY (id);


--
-- Name: historico_quitado historico_quitado_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historico_quitado
    ADD CONSTRAINT historico_quitado_pkey PRIMARY KEY (id);


--
-- Name: itens_condicional itens_condicional_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.itens_condicional
    ADD CONSTRAINT itens_condicional_pkey PRIMARY KEY (id);


--
-- Name: itens_historico_legado itens_historico_legado_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.itens_historico_legado
    ADD CONSTRAINT itens_historico_legado_pkey PRIMARY KEY (id);


--
-- Name: itens_venda itens_venda_pkey; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.itens_venda
    ADD CONSTRAINT itens_venda_pkey PRIMARY KEY (id);


--
-- Name: manu_ai_sessao manu_ai_sessao_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.manu_ai_sessao
    ADD CONSTRAINT manu_ai_sessao_pkey PRIMARY KEY (id);


--
-- Name: metas_mensais metas_mensais_ano_mes_key; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.metas_mensais
    ADD CONSTRAINT metas_mensais_ano_mes_key UNIQUE (ano_mes);


--
-- Name: metas_mensais metas_mensais_pkey; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.metas_mensais
    ADD CONSTRAINT metas_mensais_pkey PRIMARY KEY (id);


--
-- Name: movimentos_financeiros movimentos_financeiros_pkey; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.movimentos_financeiros
    ADD CONSTRAINT movimentos_financeiros_pkey PRIMARY KEY (id);


--
-- Name: oracle_log oracle_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oracle_log
    ADD CONSTRAINT oracle_log_pkey PRIMARY KEY (id);


--
-- Name: oracle_sessao oracle_sessao_chat_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oracle_sessao
    ADD CONSTRAINT oracle_sessao_chat_id_key UNIQUE (chat_id);


--
-- Name: oracle_sessao oracle_sessao_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oracle_sessao
    ADD CONSTRAINT oracle_sessao_pkey PRIMARY KEY (id);


--
-- Name: oracle_stores oracle_stores_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oracle_stores
    ADD CONSTRAINT oracle_stores_pkey PRIMARY KEY (store_id);


--
-- Name: pagamentos_balcao pagamentos_balcao_pkey; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.pagamentos_balcao
    ADD CONSTRAINT pagamentos_balcao_pkey PRIMARY KEY (id);


--
-- Name: produto_variacoes produto_variacoes_pkey; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.produto_variacoes
    ADD CONSTRAINT produto_variacoes_pkey PRIMARY KEY (id);


--
-- Name: produto_variacoes produto_variacoes_produto_id_tamanho_key; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.produto_variacoes
    ADD CONSTRAINT produto_variacoes_produto_id_tamanho_key UNIQUE (produto_id, tamanho);


--
-- Name: produtos produtos_codigo_barras_key; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.produtos
    ADD CONSTRAINT produtos_codigo_barras_key UNIQUE (codigo_barras);


--
-- Name: produtos_legados produtos_legados_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.produtos_legados
    ADD CONSTRAINT produtos_legados_pkey PRIMARY KEY (id);


--
-- Name: produtos_legados produtos_legados_referencia_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.produtos_legados
    ADD CONSTRAINT produtos_legados_referencia_key UNIQUE (referencia);


--
-- Name: produtos produtos_pkey; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.produtos
    ADD CONSTRAINT produtos_pkey PRIMARY KEY (id);


--
-- Name: vales_troca vales_troca_pkey; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.vales_troca
    ADD CONSTRAINT vales_troca_pkey PRIMARY KEY (id);


--
-- Name: vendas vendas_pkey; Type: CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.vendas
    ADD CONSTRAINT vendas_pkey PRIMARY KEY (id);


--
-- Name: idx_clientes_codigo_externo; Type: INDEX; Schema: public; Owner: jgadmin
--

CREATE UNIQUE INDEX idx_clientes_codigo_externo ON public.clientes USING btree (codigo_externo) WHERE (codigo_externo IS NOT NULL);


--
-- Name: idx_clientes_mes_nasc; Type: INDEX; Schema: public; Owner: jgadmin
--

CREATE INDEX idx_clientes_mes_nasc ON public.clientes USING btree (EXTRACT(month FROM data_nascimento)) WHERE (data_nascimento IS NOT NULL);


--
-- Name: idx_clientes_nome_lower; Type: INDEX; Schema: public; Owner: jgadmin
--

CREATE INDEX idx_clientes_nome_lower ON public.clientes USING btree (lower(nome));


--
-- Name: idx_clientes_whatsapp; Type: INDEX; Schema: public; Owner: jgadmin
--

CREATE INDEX idx_clientes_whatsapp ON public.clientes USING btree (whatsapp) WHERE ((whatsapp IS NOT NULL) AND (whatsapp <> ''::text));


--
-- Name: idx_clileg_cpf; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_clileg_cpf ON public.clientes_legados USING btree (cpf);


--
-- Name: idx_cond_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_cond_status ON public.condicionais USING btree (status);


--
-- Name: idx_cr_status_venda; Type: INDEX; Schema: public; Owner: jgadmin
--

CREATE INDEX idx_cr_status_venda ON public.contas_receber USING btree (venda_id, status) WHERE (status = 'aberto'::text);


--
-- Name: idx_dai_cli; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_dai_cli ON public.duplicatas_abertas_itens USING btree (cliente_codigo);


--
-- Name: idx_dai_doc; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_dai_doc ON public.duplicatas_abertas_itens USING btree (documento);


--
-- Name: idx_dup_cliente; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_dup_cliente ON public.duplicatas_abertas USING btree (codigo_cliente);


--
-- Name: idx_dup_nome; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_dup_nome ON public.duplicatas_abertas USING btree (nome_cliente);


--
-- Name: idx_dup_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_dup_status ON public.duplicatas_abertas USING btree (status);


--
-- Name: idx_dup_vencimento; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_dup_vencimento ON public.duplicatas_abertas USING btree (dt_vencimento);


--
-- Name: idx_eh_data; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eh_data ON public.estoque_historico USING btree (created_at);


--
-- Name: idx_eh_produto; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_eh_produto ON public.estoque_historico USING btree (produto_id);


--
-- Name: idx_hist_precos_produto; Type: INDEX; Schema: public; Owner: jgadmin
--

CREATE INDEX idx_hist_precos_produto ON public.historico_precos USING btree (produto_id, data_alteracao DESC);


--
-- Name: idx_hl_cliente_cod; Type: INDEX; Schema: public; Owner: jgadmin
--

CREATE INDEX idx_hl_cliente_cod ON public.historico_legado USING btree (cliente_codigo);


--
-- Name: idx_hl_cliente_id; Type: INDEX; Schema: public; Owner: jgadmin
--

CREATE INDEX idx_hl_cliente_id ON public.historico_legado USING btree (cliente_id);


--
-- Name: idx_hl_doc; Type: INDEX; Schema: public; Owner: jgadmin
--

CREATE INDEX idx_hl_doc ON public.historico_legado USING btree (documento);


--
-- Name: idx_hl_dt_venc; Type: INDEX; Schema: public; Owner: jgadmin
--

CREATE INDEX idx_hl_dt_venc ON public.historico_legado USING btree (dt_vencimento);


--
-- Name: idx_hl_status; Type: INDEX; Schema: public; Owner: jgadmin
--

CREATE INDEX idx_hl_status ON public.historico_legado USING btree (status);


--
-- Name: idx_ihl_cli; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ihl_cli ON public.itens_historico_legado USING btree (cliente_codigo);


--
-- Name: idx_ihl_doc; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ihl_doc ON public.itens_historico_legado USING btree (documento);


--
-- Name: idx_ihl_ref; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_ihl_ref ON public.itens_historico_legado USING btree (referencia);


--
-- Name: idx_itens_cond_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_itens_cond_id ON public.itens_condicional USING btree (condicional_id);


--
-- Name: idx_itens_venda_produto_id; Type: INDEX; Schema: public; Owner: jgadmin
--

CREATE INDEX idx_itens_venda_produto_id ON public.itens_venda USING btree (produto_id);


--
-- Name: idx_itens_venda_venda_id; Type: INDEX; Schema: public; Owner: jgadmin
--

CREATE INDEX idx_itens_venda_venda_id ON public.itens_venda USING btree (venda_id);


--
-- Name: idx_manu_sessao_chat; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_manu_sessao_chat ON public.manu_ai_sessao USING btree (chat_id);


--
-- Name: idx_oracle_log_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_oracle_log_created_at ON public.oracle_log USING btree (created_at DESC);


--
-- Name: idx_oracle_log_store_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_oracle_log_store_id ON public.oracle_log USING btree (store_id);


--
-- Name: idx_oracle_sessao_chat_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_oracle_sessao_chat_id ON public.oracle_sessao USING btree (chat_id);


--
-- Name: idx_oracle_sessao_store_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_oracle_sessao_store_id ON public.oracle_sessao USING btree (store_id);


--
-- Name: idx_prod_var_produto; Type: INDEX; Schema: public; Owner: jgadmin
--

CREATE INDEX idx_prod_var_produto ON public.produto_variacoes USING btree (produto_id);


--
-- Name: idx_produtos_estoque; Type: INDEX; Schema: public; Owner: jgadmin
--

CREATE INDEX idx_produtos_estoque ON public.produtos USING btree (estoque_atual) WHERE (ativo IS NOT FALSE);


--
-- Name: idx_produtos_nome_lower; Type: INDEX; Schema: public; Owner: jgadmin
--

CREATE INDEX idx_produtos_nome_lower ON public.produtos USING btree (lower(nome)) WHERE (ativo IS NOT FALSE);


--
-- Name: idx_quit_cliente; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_quit_cliente ON public.historico_quitado USING btree (codigo_cliente);


--
-- Name: idx_quit_nome; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_quit_nome ON public.historico_quitado USING btree (nome_cliente);


--
-- Name: idx_quit_pagto; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_quit_pagto ON public.historico_quitado USING btree (dt_pagamento);


--
-- Name: idx_vendas_cliente_data; Type: INDEX; Schema: public; Owner: jgadmin
--

CREATE INDEX idx_vendas_cliente_data ON public.vendas USING btree (cliente_id, data_venda DESC);


--
-- Name: contas_receber trg_nr_documento_cr; Type: TRIGGER; Schema: public; Owner: jgadmin
--

CREATE TRIGGER trg_nr_documento_cr BEFORE INSERT ON public.contas_receber FOR EACH ROW EXECUTE FUNCTION public.fn_nr_documento_cr();


--
-- Name: contas_receber contas_receber_venda_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.contas_receber
    ADD CONSTRAINT contas_receber_venda_id_fkey FOREIGN KEY (venda_id) REFERENCES public.vendas(id);


--
-- Name: estoque_historico estoque_historico_produto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.estoque_historico
    ADD CONSTRAINT estoque_historico_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produtos(id);


--
-- Name: historico_legado historico_legado_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.historico_legado
    ADD CONSTRAINT historico_legado_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.clientes(id);


--
-- Name: historico_precos historico_precos_produto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.historico_precos
    ADD CONSTRAINT historico_precos_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produtos(id) ON DELETE CASCADE;


--
-- Name: itens_condicional itens_condicional_condicional_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.itens_condicional
    ADD CONSTRAINT itens_condicional_condicional_id_fkey FOREIGN KEY (condicional_id) REFERENCES public.condicionais(id) ON DELETE CASCADE;


--
-- Name: itens_venda itens_venda_produto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.itens_venda
    ADD CONSTRAINT itens_venda_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produtos(id);


--
-- Name: itens_venda itens_venda_venda_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.itens_venda
    ADD CONSTRAINT itens_venda_venda_id_fkey FOREIGN KEY (venda_id) REFERENCES public.vendas(id) ON DELETE CASCADE;


--
-- Name: produto_variacoes produto_variacoes_produto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.produto_variacoes
    ADD CONSTRAINT produto_variacoes_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produtos(id) ON DELETE CASCADE;


--
-- Name: vales_troca vales_troca_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.vales_troca
    ADD CONSTRAINT vales_troca_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.clientes(id) ON DELETE CASCADE;


--
-- Name: vales_troca vales_troca_venda_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.vales_troca
    ADD CONSTRAINT vales_troca_venda_id_fkey FOREIGN KEY (venda_id) REFERENCES public.vendas(id) ON DELETE SET NULL;


--
-- Name: vendas vendas_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jgadmin
--

ALTER TABLE ONLY public.vendas
    ADD CONSTRAINT vendas_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.clientes(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO jgadmin;


--
-- Name: FUNCTION fn_nr_documento_cr(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.fn_nr_documento_cr() TO jgadmin;


--
-- Name: FUNCTION unaccent(text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.unaccent(text) TO jgadmin;


--
-- Name: FUNCTION unaccent(regdictionary, text); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.unaccent(regdictionary, text) TO jgadmin;


--
-- Name: FUNCTION unaccent_init(internal); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.unaccent_init(internal) TO jgadmin;


--
-- Name: FUNCTION unaccent_lexize(internal, internal, internal, internal); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.unaccent_lexize(internal, internal, internal, internal) TO jgadmin;


--
-- Name: TABLE clientes_legados; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.clientes_legados TO jgadmin;


--
-- Name: SEQUENCE clientes_legados_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.clientes_legados_id_seq TO jgadmin;


--
-- Name: TABLE condicionais; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.condicionais TO jgadmin;


--
-- Name: SEQUENCE condicionais_numero_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.condicionais_numero_seq TO jgadmin;


--
-- Name: TABLE configuracoes; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.configuracoes TO jgadmin;


--
-- Name: SEQUENCE configuracoes_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.configuracoes_id_seq TO jgadmin;


--
-- Name: TABLE duplicatas_abertas; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.duplicatas_abertas TO jgadmin;


--
-- Name: SEQUENCE duplicatas_abertas_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.duplicatas_abertas_id_seq TO jgadmin;


--
-- Name: TABLE duplicatas_abertas_itens; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.duplicatas_abertas_itens TO jgadmin;


--
-- Name: SEQUENCE duplicatas_abertas_itens_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.duplicatas_abertas_itens_id_seq TO jgadmin;


--
-- Name: TABLE duplicatas_bkp_sync_29042026; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.duplicatas_bkp_sync_29042026 TO jgadmin;


--
-- Name: TABLE estoque; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.estoque TO jgadmin;


--
-- Name: TABLE estoque_historico; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.estoque_historico TO jgadmin;


--
-- Name: SEQUENCE estoque_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.estoque_id_seq TO jgadmin;


--
-- Name: TABLE historico_quitado; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.historico_quitado TO jgadmin;


--
-- Name: SEQUENCE historico_quitado_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.historico_quitado_id_seq TO jgadmin;


--
-- Name: TABLE itens_condicional; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.itens_condicional TO jgadmin;


--
-- Name: TABLE itens_historico_legado; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.itens_historico_legado TO jgadmin;


--
-- Name: TABLE lista_vermelha; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.lista_vermelha TO jgadmin;


--
-- Name: TABLE manu_ai_sessao; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.manu_ai_sessao TO jgadmin;


--
-- Name: TABLE oracle_log; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.oracle_log TO jgadmin;


--
-- Name: TABLE oracle_sessao; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.oracle_sessao TO jgadmin;


--
-- Name: TABLE oracle_stores; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.oracle_stores TO jgadmin;


--
-- Name: COLUMN produtos.ativo; Type: ACL; Schema: public; Owner: jgadmin
--

GRANT UPDATE(ativo) ON TABLE public.produtos TO jgadmin;


--
-- Name: TABLE produtos_legados; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.produtos_legados TO jgadmin;


--
-- Name: SEQUENCE produtos_legados_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.produtos_legados_id_seq TO jgadmin;


--
-- Name: SEQUENCE seq_condicional; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.seq_condicional TO jgadmin;


--
-- Name: TABLE vw_clientes_completos; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vw_clientes_completos TO jgadmin;


--
-- Name: TABLE vw_estoque_completo; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vw_estoque_completo TO jgadmin;


--
-- Name: TABLE vw_recebiveis; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.vw_recebiveis TO jgadmin;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO jgadmin;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON FUNCTIONS TO jgadmin;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO jgadmin;


--
-- PostgreSQL database dump complete
--

\unrestrict 5zdKIIKRDOBxxqdi76G5mdK2ZGHmZLaFbRkgqPleYRWDf23JtlGk11WPQrhaBGC

