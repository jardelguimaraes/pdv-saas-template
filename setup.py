#!/usr/bin/env python3
"""PDV SaaS Setup Wizard v1.0 — JGAutomacoes.AI"""
import json, re, secrets

def ask(prompt, default=None):
    suf = f" [{default}]" if default else ""
    while True:
        v = input(f"  {prompt}{suf}: ").strip()
        if v: return v
        if default: return default
        print("  Obrigatorio.")

print("\n PDV SaaS — Instalacao — JGAutomacoes.AI\n")
nome  = ask("1. Nome da loja")
cidade= ask("2. Cidade/UF")
insta = ask("3. Instagram", "@suasloja")
cor   = ask("4. Cor principal hex", "#C4697B")
senha = ask("5. Senha do banco")

db = "pdv_" + re.sub(r'[^a-z0-9]','', nome.lower())[:20]

with open("config.json","w") as f:
    json.dump({"loja_nome":nome,"loja_cidade":cidade,"loja_instagram":insta,
               "db_name":db,"db_password":senha,"cor_primaria":cor,
               "webhook_secret":secrets.token_hex(16),"versao":"6.1"},
              f, indent=2, ensure_ascii=False)

with open(".env","w") as f:
    f.write(f"DB_NAME={db}\nDB_USER=jgadmin\nDB_PASSWORD={senha}\nPORTA=8506\n")

print(f"\n Configurado! Banco: {db}\n Proximos passos:\n  1. docker exec -i jg-postgres psql -U postgres -c \"CREATE DATABASE {db};\"\n  2. docker exec -i jg-postgres psql -U postgres -d {db} < schema.sql\n  3. bash start.sh\n")
