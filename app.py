# Viaj.AI — v0.7.1 (tira falsos checkboxes de Previsao/Pendencias, sem RPC de escrita por tras) — ver 00-handoff.md do VIAJAI no vault
# Gestão de folgas, deslocamento e custo de funcionários em obra — EnerMais.
#
# Reaproveita o padrão validado em produção do TIA.go/RHDADOS:
# - cliente Supabase sempre em st.session_state (nunca st.cache_resource)
# - reanexar token a cada rerun (supabase.postgrest.auth(token))
# - login só Supabase Auth (e-mail/senha)
#
# NAO RODA ainda sem: (1) schema `viajai` v0.1 a v0.4 rodados no Supabase
# (ver arquivos/schema_v0.*.txt no vault) e (2) .env preenchido a partir
# de .env.example.
#
# PARSER DO RE090 — NOTA IMPORTANTE (01/09): as 10 planilhas que seguem o
# padrão RE090 NAO tem a mesma ordem de coluna entre si (confirmado lendo
# 4 arquivos reais: uma tem uma coluna extra "CONFERENCIA RH" antes do
# nome, deslocando tudo; duas nao tem as colunas "ultima folga"/"qnt dias"
# de jeito nenhum). Por isso o parser abaixo NUNCA usa indice fixo de
# coluna — ele le a linha de cabecalho (linha 4, confirmado em 4/4 arquivos
# reais) e casa pelo TEXTO do cabecalho. Se um arquivo novo tiver cabecalho
# diferente o suficiente pra nao casar "nome", a tela avisa em vez de
# importar linha errada silenciosamente.

import base64
import os
from datetime import date, datetime

import openpyxl
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

st.set_page_config(page_title="Viaj.AI", page_icon="🧳", layout="wide")

LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo-enermais.png")


@st.cache_data
def logo_base64():
    with open(LOGO_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode()


def render_logo(height=56):
    # Mesmo padrão do TIA.go/Radar/RHDADOS: logo oficial (navy+laranja) em
    # silhueta branca via filtro CSS (brightness(0) invert(1)), sem precisar
    # de PNG separado. Tema base agora e' "dark" (.streamlit/config.toml),
    # entao usa o mesmo filtro do TIA.go (fundo escuro -> silhueta branca).
    st.markdown(
        f"""
        <img src="data:image/png;base64,{logo_base64()}" height="{height}"
             style="filter: brightness(0) invert(1); margin-bottom: 12px;">
        """,
        unsafe_allow_html=True,
    )

ABA_FOLGAS = "Controle de Folgas"
LINHA_CABECALHO = 4  # confirmado em 4/4 arquivos RE090 reais analisados

# texto do cabecalho (minusculo, sem acento no essencial) -> chave interna
ALIASES_COLUNA = {
    "centro de custo": "centro_custo",
    "nome do funcion": "nome",  # match parcial: "Nome do Funcionário (completo)"
    "ultima folga": "ultima_folga",
    "última folga": "ultima_folga",
    "inicio da folga": "inicio_folga",
    "início da folga": "inicio_folga",
    "termino da folga": "termino_folga",
    "término da folga": "termino_folga",
}


def get_client() -> Client:
    if "supabase_client" not in st.session_state:
        st.session_state.supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    return st.session_state.supabase_client


def tela_login():
    render_logo(height=64)
    st.caption("Viaj.AI — Gestão de folgas, deslocamento e custo")
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


def _mapear_colunas(ws, linha_cabecalho=LINHA_CABECALHO, max_colunas=25):
    """Le a linha de cabecalho e devolve {chave_interna: indice_coluna(1-based)}.
    Casamento por trecho de texto, nao por posicao — planilhas reais tem
    colunas em ordens diferentes (ver nota no topo do arquivo)."""
    mapa = {}
    for c in range(1, max_colunas + 1):
        valor = ws.cell(row=linha_cabecalho, column=c).value
        if not valor:
            continue
        texto = str(valor).strip().lower()
        for trecho, chave in ALIASES_COLUNA.items():
            if trecho in texto and chave not in mapa:
                mapa[chave] = c
    return mapa


def _valor_data(v):
    if v is None:
        return None
    if isinstance(v, (datetime, date)):
        return v.date() if isinstance(v, datetime) else v
    return None  # texto solto em campo de data: nao adivinha, descarta


def _ler_planilha_re090(arquivo):
    # read_only=True é obrigatório aqui: testado contra os 14 arquivos reais
    # e o modo padrão (carrega tudo na memória, incl. imagem/formatação)
    # trava/mata o processo no arquivo de 19MB (NATANAEL). Com read_only
    # esse mesmo arquivo leu em 0.1s.
    wb = openpyxl.load_workbook(arquivo, data_only=True, read_only=True)
    if ABA_FOLGAS not in wb.sheetnames:
        return None, f"Aba '{ABA_FOLGAS}' não encontrada. Abas nesse arquivo: {wb.sheetnames}"

    ws = wb[ABA_FOLGAS]
    mapa = _mapear_colunas(ws)
    if "nome" not in mapa:
        return None, (
            "Não achei a coluna de nome do funcionário no cabeçalho da linha "
            f"{LINHA_CABECALHO}. Essa planilha pode não seguir o padrão RE090 "
            "esperado — confere manualmente antes de tentar de novo."
        )

    linhas = []
    for row in ws.iter_rows(min_row=LINHA_CABECALHO + 1, values_only=True):
        def pega(chave):
            idx = mapa.get(chave)
            return row[idx - 1] if idx and idx - 1 < len(row) else None

        nome = pega("nome")
        if not nome or not str(nome).strip():
            continue

        linhas.append({
            "nome": str(nome).strip(),
            "centro_custo": pega("centro_custo"),
            "data_ultimo_retorno": _valor_data(pega("ultima_folga")),
            "data_saida_prevista": _valor_data(pega("inicio_folga")),
            "data_retorno_prevista": _valor_data(pega("termino_folga")),
        })
    return linhas, None


def _importar_um_arquivo(supabase, arquivo):
    """Processa 1 arquivo RE090: le, abre um lote (import_batch), roda a RPC
    linha a linha carimbando o lote, fecha o lote com os totais. Devolve
    (nome_arquivo, resultados, erro_leitura)."""
    linhas, erro = _ler_planilha_re090(arquivo)
    if erro:
        return arquivo.name, None, erro

    batch = supabase.rpc("viajai_criar_import_batch", {
        "p_nome_arquivo": arquivo.name,
        "p_total_linhas": len(linhas),
    }).execute()
    batch_id = batch.data

    resultados = []
    for l in linhas:
        try:
            resp = supabase.rpc("viajai_importar_re090_linha", {
                "p_nome_planilha": l["nome"],
                "p_matricula_planilha": None,
                "p_texto_obra_canteiro": l["centro_custo"],
                "p_data_ultimo_retorno": l["data_ultimo_retorno"].isoformat() if l["data_ultimo_retorno"] else None,
                "p_data_saida_prevista": l["data_saida_prevista"].isoformat() if l["data_saida_prevista"] else None,
                "p_data_retorno_prevista": l["data_retorno_prevista"].isoformat() if l["data_retorno_prevista"] else None,
                "p_import_batch_id": batch_id,
            }).execute()
            linha_resultado = resp.data[0] if resp.data else {"resultado": "sem_retorno"}
        except Exception as e:
            linha_resultado = {"resultado": "erro", "colaborador_id": None, "folga_id": None}
            st.warning(f"Erro ao importar '{l['nome']}' ({arquivo.name}): {e}")
        resultados.append({"nome": l["nome"], **linha_resultado})

    criadas = sum(1 for r in resultados if r.get("resultado") == "criada")
    pendentes = sum(1 for r in resultados if r.get("resultado") == "pendencia")
    supabase.rpc("viajai_finalizar_import_batch", {
        "p_batch_id": batch_id,
        "p_total_criadas": criadas,
        "p_total_pendencias": pendentes,
    }).execute()

    return arquivo.name, resultados, None


def pagina_importar_re090(supabase):
    st.subheader("Importar RE090")
    st.caption(
        "Sobe a(s) planilha(s), resolve cada colaborador contra o RH (ao vivo) "
        "e grava a folga já com o canteiro espelho. Sem match único, a linha "
        "vira pendência — nada é perdido, só fica pra você revisar. Pode subir "
        "mais de um arquivo de uma vez — cada arquivo vira 1 lote no histórico, "
        "revertível separadamente."
    )

    arquivos = st.file_uploader(
        "Planilha(s) RE090 (.xlsx)", type=["xlsx"], accept_multiple_files=True
    )
    if arquivos:
        pre_leituras = []
        for arquivo in arquivos:
            linhas, erro = _ler_planilha_re090(arquivo)
            pre_leituras.append((arquivo, linhas, erro))
            if erro:
                st.error(f"{arquivo.name}: {erro}")
            else:
                st.write(f"**{arquivo.name}** — {len(linhas)} linha(s) com nome preenchido.")
                with st.expander(f"Ver linhas antes de importar — {arquivo.name}"):
                    st.dataframe(linhas)

        if st.button("Importar", type="primary"):
            resultado_por_arquivo = {}
            for arquivo, linhas, erro in pre_leituras:
                if erro:
                    continue
                nome, resultados, _ = _importar_um_arquivo(supabase, arquivo)
                resultado_por_arquivo[nome] = resultados
            st.session_state["resultado_import"] = resultado_por_arquivo

    if "resultado_import" in st.session_state:
        for nome_arquivo, resultados in st.session_state["resultado_import"].items():
            criadas = sum(1 for r in resultados if r.get("resultado") == "criada")
            pendentes = sum(1 for r in resultados if r.get("resultado") == "pendencia")
            duplicadas = sum(1 for r in resultados if r.get("resultado") == "duplicada")
            msg = f"**{nome_arquivo}**: {criadas} folga(s) criada(s), {pendentes} em pendência"
            if duplicadas:
                msg += f", {duplicadas} duplicada(s) (já existia folga prevista pra essa pessoa nessa mesma data — ignorada, não criou de novo)"
            st.success(msg + ".")
            st.dataframe(resultados)

    st.divider()
    st.subheader("Histórico de imports")
    st.caption(
        "Cada linha é 1 upload. Reverter apaga as folgas criadas por esse "
        "lote específico — só as que ninguém mexeu ainda (status ainda "
        "'prevista', sem trecho de viagem associado); o resto fica registrado "
        "mas não é apagado, pra não perder trabalho já feito em cima."
    )
    lotes = supabase.rpc("viajai_listar_import_batches", {"p_limite": 20}).execute()
    if lotes.data:
        for lote in lotes.data:
            cols = st.columns([3, 2, 2, 2, 2])
            cols[0].write(f"{lote['nome_arquivo']}")
            cols[1].write(lote["criado_em"][:16].replace("T", " "))
            cols[2].write(f"{lote['total_criadas']} criada(s)")
            cols[3].write(f"{lote['total_pendencias']} pendência(s)")
            if lote["revertido"]:
                cols[4].write("↩️ revertido")
            else:
                if cols[4].button("Reverter", key=f"reverter_{lote['id']}"):
                    rev = supabase.rpc(
                        "viajai_reverter_import_batch", {"p_batch_id": lote["id"]}
                    ).execute()
                    r = rev.data[0] if rev.data else {}
                    st.success(
                        f"Revertido: {r.get('folgas_removidas', 0)} folga(s) removida(s), "
                        f"{r.get('folgas_puladas', 0)} pulada(s) (já tinham sido mexidas), "
                        f"{r.get('pendencias_removidas', 0)} pendência(s) removida(s)."
                    )
                    st.rerun()
    else:
        st.caption("Nenhum import feito ainda.")

    st.divider()
    st.subheader("Pendências abertas")
    pend = supabase.rpc("viajai_listar_pendencias_import", {"p_apenas_nao_resolvidas": True}).execute()
    if pend.data:
        st.caption(
            "Só leitura por enquanto — marcar pendência como resolvida ainda "
            "não tem tela (fica pra depois, ver 00-handoff)."
        )
        df_pend = pd.DataFrame(pend.data)
        # tira "resolvido" (sempre False aqui, a RPC ja filtra nao-resolvidas
        # -- so confundia como um checkbox clicavel que na pratica nao fazia
        # nada, st.dataframe nunca aceita edicao) e "origem" (sempre 're090').
        df_pend = df_pend.drop(columns=[c for c in ["resolvido", "origem"] if c in df_pend.columns])
        st.dataframe(df_pend, use_container_width=True, hide_index=True)
    else:
        st.caption("Nenhuma pendência em aberto.")


_STATUS_OPCOES = ["prevista", "confirmada", "em_andamento", "realizada", "vendida", "cancelada"]


def pagina_confirmar_folgas(supabase):
    st.subheader("Confirmar folgas")
    st.caption(
        "Fecha o ciclo: registre aqui o que realmente aconteceu com cada "
        "folga que caiu como 'prevista' (via import ou manual). Sem isso, "
        "a Previsão de folgas nunca reflete a realidade — só o que foi "
        "planejado. Edita direto na tabela: muda o 'Status novo' de quem "
        "mudou, preenche data real se for o caso, e clica em Salvar no "
        "final — quem ficar em 'prevista' não é tocado."
    )

    previstas = supabase.rpc("viajai_listar_folgas_previstas", {"p_limite": 300}).execute()
    if not previstas.data:
        st.caption("Nenhuma folga 'prevista' aguardando confirmação no momento.")
    else:
        base = pd.DataFrame(previstas.data)
        base["status_novo"] = "prevista"
        base["data_saida_real"] = pd.NaT
        base["data_retorno_real"] = pd.NaT
        base["motivo_venda"] = ""

        editado = st.data_editor(
            base,
            column_order=[
                "nome", "obra_nome", "canteiro_nome",
                "data_saida_prevista", "data_retorno_prevista",
                "status_novo", "data_saida_real", "data_retorno_real", "motivo_venda",
            ],
            column_config={
                "nome": st.column_config.TextColumn("Nome", disabled=True),
                "obra_nome": st.column_config.TextColumn("Obra", disabled=True),
                "canteiro_nome": st.column_config.TextColumn("Canteiro", disabled=True),
                "data_saida_prevista": st.column_config.DateColumn("Saída prevista", disabled=True),
                "data_retorno_prevista": st.column_config.DateColumn("Retorno previsto", disabled=True),
                "status_novo": st.column_config.SelectboxColumn(
                    "Status novo", options=_STATUS_OPCOES, required=True,
                    help="Deixa 'prevista' pra não mexer nessa linha.",
                ),
                "data_saida_real": st.column_config.DateColumn(
                    "Saída real", help="Preenche se marcou 'em_andamento' ou 'realizada'."
                ),
                "data_retorno_real": st.column_config.DateColumn(
                    "Retorno real", help="Preenche se marcou 'realizada'."
                ),
                "motivo_venda": st.column_config.TextColumn(
                    "Motivo (se vendida)", help="Opcional, só faz sentido se marcou 'vendida'."
                ),
            },
            hide_index=True,
            use_container_width=True,
            key="editor_confirmar_folgas",
        )

        if st.button("Salvar alterações", type="primary"):
            mudou = editado[editado["status_novo"] != "prevista"]
            if mudou.empty:
                st.info("Nenhuma linha teve o status alterado — nada pra salvar.")
            else:
                erros = 0
                for _, linha in mudou.iterrows():
                    try:
                        supabase.rpc("viajai_atualizar_folga", {
                            "p_folga_id": int(linha["folga_id"]),
                            "p_status": linha["status_novo"],
                            "p_data_saida_real": (
                                linha["data_saida_real"].isoformat()
                                if pd.notna(linha["data_saida_real"]) else None
                            ),
                            "p_data_retorno_real": (
                                linha["data_retorno_real"].isoformat()
                                if pd.notna(linha["data_retorno_real"]) else None
                            ),
                            "p_motivo_venda": linha["motivo_venda"] or None,
                        }).execute()
                    except Exception as e:
                        erros += 1
                        st.error(f"Erro ao salvar {linha['nome']}: {e}")
                sucesso = len(mudou) - erros
                if sucesso:
                    st.success(f"{sucesso} folga(s) atualizada(s).")
                st.rerun()

        st.caption(f"{len(previstas.data)} folga(s) prevista(s) aguardando confirmação.")

    st.divider()
    st.subheader("Histórico")
    st.caption("Últimas mudanças registradas — quem, quando, o que mudou.")
    hist = supabase.rpc("viajai_listar_historico_folga", {"p_limite": 100}).execute()
    if hist.data:
        st.dataframe(hist.data, use_container_width=True, hide_index=True)
    else:
        st.caption("Nenhuma mudança registrada ainda.")


_ORDEM_URGENCIA = {"critico": 0, "atencao": 1, "normal": 2}


def pagina_previsao(supabase):
    st.subheader("Previsão de folgas")
    st.caption(
        "Calculado ao vivo: colaborador ativo no RH + última folga conhecida "
        "no Viaj.AI. Sem histórico ainda = sem previsão (precisa de ao menos "
        "1 folga registrada, manual ou via import)."
    )
    resp = supabase.rpc("viajai_previsao_folgas").execute()
    if not resp.data:
        st.caption("Sem dados ainda.")
        return

    df = pd.DataFrame(resp.data)

    mostrar_sem_historico = st.checkbox(
        "Mostrar também quem ainda não tem nenhuma folga registrada "
        "(sem previsão calculável ainda)",
        value=False,
    )
    if not mostrar_sem_historico:
        df = df[df["tem_historico"] == True]  # noqa: E712
        if df.empty:
            st.caption(
                "Ninguém com histórico ainda — importe pelo menos 1 RE090 ou "
                "marque a caixa acima pra ver a lista completa sem previsão."
            )
            return

    # mais urgente primeiro: critico > atencao > normal > (sem classificacao)
    # e, dentro do mesmo nivel, quem tem menos dias restantes primeiro
    df["_ordem_urgencia"] = df["nivel_urgencia"].map(_ORDEM_URGENCIA).fillna(9)
    df = df.sort_values(by=["_ordem_urgencia", "dias_restantes"], na_position="last")
    df = df.drop(columns=["_ordem_urgencia"])

    colunas_principais = [
        "nome", "nivel_urgencia", "dias_restantes",
        "data_saida_prevista", "data_retorno_prevista",
        "obra_nome", "canteiro_nome",
    ]
    colunas_principais = [c for c in colunas_principais if c in df.columns]
    # colunas tecnicas (ids, flags internas de ordenacao/filtro) e
    # "urgencia_manual" (falso checkbox - RPC de escrita ja existe mas
    # nenhuma tela chama ainda, ver 00-handoff) ficam de fora da tabela.
    colunas_ocultas = {
        "colaborador_id", "obra_id", "canteiro_id",
        "data_base_retorno", "tem_historico", "urgencia_manual",
    }
    outras = [c for c in df.columns if c not in colunas_principais and c not in colunas_ocultas]
    df = df[colunas_principais + outras]

    st.dataframe(df, use_container_width=True, hide_index=True)


def main():
    if "sessao" not in st.session_state:
        tela_login()
        return

    # Reanexa o token a cada rerun (padrão TIA.go — Streamlit recria o
    # cliente do zero a cada interação, sem isso a consulta vai como anônimo
    # e a RLS devolve vazio sem erro nenhum).
    supabase = get_client()
    supabase.postgrest.auth(st.session_state.sessao.access_token)

    with st.sidebar:
        render_logo(height=56)
        st.write(f"Logado como: {st.session_state.usuario}")
        pagina = st.radio(
            "Navegação",
            ["Importar RE090", "Confirmar folgas", "Previsão de folgas"],
        )
        if st.button("Sair"):
            supabase.auth.sign_out()
            del st.session_state.sessao
            st.rerun()

    if pagina == "Importar RE090":
        pagina_importar_re090(supabase)
    elif pagina == "Confirmar folgas":
        pagina_confirmar_folgas(supabase)
    elif pagina == "Previsão de folgas":
        pagina_previsao(supabase)


if __name__ == "__main__":
    main()
