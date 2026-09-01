# Viaj.AI — v0.1 ESQUELETO, NÃO TESTADO (ver 00-handoff.md do VIAJAI no vault)
# Gestão de folgas, deslocamento e custo de funcionários em obra — EnerMais.
#
# Reaproveita o padrão validado em produção do TIA.go/RHDADOS:
# - cliente Supabase sempre em st.session_state (nunca st.cache_resource)
# - reanexar token a cada rerun (supabase.postgrest.auth(token))
# - login só Supabase Auth (e-mail/senha)
#
# NAO RODA ainda: precisa (1) schema `viajai` criado no Supabase (ver
# arquivos/schema_v0.1_viajai_base.txt no vault) e (2) .env preenchido
# a partir de .env.example.

import os
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

st.set_page_config(page_title="Viaj.AI", page_icon="🧳", layout="wide")


def get_client() -> Client:
    if "supabase_client" not in st.session_state:
        st.session_state.supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    return st.session_state.supabase_client


def tela_login():
    st.title("🧳 Viaj.AI")
    st.caption("Gestão de folgas, deslocamento e custo — EnerMais")
    with st.form("login"):
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar")
    if entrar:
        supabase = get_client()
        try:
            resp = supabase.auth.sign_in_with_password({"email": email, "password": senha})
            st.session_state.sessao = resp.session
            st.session_state.usuario = email
            st.rerun()
        except Exception as e:
            st.error(f"Login falhou: {e}")


def main():
    if "sessao" not in st.session_state:
        tela_login()
        return

    # Reanexa o token a cada rerun (padrão TIA.go — Streamlit recria o
    # cliente do zero a cada interação, sem isso a consulta vai como anônimo
    # e a RLS devolve vazio sem erro nenhum).
    supabase = get_client()
    supabase.postgrest.auth(st.session_state.sessao.access_token)

    st.sidebar.write(f"Logado como: {st.session_state.usuario}")
    if st.sidebar.button("Sair"):
        supabase.auth.sign_out()
        del st.session_state.sessao
        st.rerun()

    st.title("🧳 Viaj.AI")
    st.info(
        "Esqueleto v0.1 — telas de folga/passagem/gasto e o chat ainda não "
        "existem. Próximo passo: rodar o schema no Supabase e construir as "
        "telas em cima das RPCs de leitura do RHDADOS."
    )


if __name__ == "__main__":
    main()
