# Viaj.AI — v20.0 (evolucao estrutural: "Passagem pra revisar" alcancavel
# de verdade - vincular lancamento/trecho a folga, via chat, tela e
# retroativo - schema_v0.32)
# ACHADO testando o v19.0 ao vivo (08/09): "Passagem pra revisar" (v0.29)
# so' listava folga vendida/cancelada com lancamento_custo_rapido.folga_id
# preenchido, mas NENHUM caminho do app (tela "Lançamento rápido" nem chat)
# jamais preenchia esse campo (0 linhas no banco, sempre) - e passagem
# lancada na aba "Por folga" (viagem/trecho) nunca era considerada de jeito
# nenhum. A tela sempre mostrava "nenhuma pendente".
# Pedido do Rafael (08/09), verbatim: "acho q tem q ser via chat e via
# pagina de passagem pra revisar tb ne, da p implementar os 2?" -
# confirmado (pergunta de esclarecimento respondida: as 3 frentes).
# Mudancas: viajai_registrar_lancamento_rapido ganha p_folga_id opcional
# (tela "Lançamento rápido" E chat, via card de confirmacao, com validacao
# de colaborador<->folga no backend); viajai_folga_passagem_para_revisar
# passa a UNIR os 2 sistemas de passagem (lancamento_custo_rapido E
# viagem/trecho); nova RPC viajai_vincular_lancamento_folga pro vinculo
# retroativo (novo expander em Urgências, pra quem ja lancou sem apontar a
# folga); viajai.revisao_passagem (historico PERMANENTE, nunca dropada)
# ganhou trecho_id como fonte alternativa a lancamento_id via ALTER TABLE
# (tinha 0 linhas, conferido antes - ALTER seguro). Achado secundario sem
# risco: existiam 2 overloads orfas de viajai_registrar_lancamento_rapido
# no banco (uma bem antiga, nunca usada desde o schema_v0.27) - limpas
# nesta mesma migracao. NAO RODA sem rodar schema_v0.32_viajai_vincular_
# passagem_folga.txt no Supabase ANTES do deploy (varias RPCs mudam de
# assinatura).
#
# Viaj.AI — v19.0 (evolucao estrutural: "Confirmar folgas" + chat cobrem
# folga ja 'confirmada'/'em_andamento', nao so' 'prevista' - schema_v0.31)
# Pedido do Rafael (08/09), em resposta ao achado de que nao existia
# NENHUM caminho (nem tela, nem chat) pra marcar uma folga ja 'confirmada'/
# 'em_andamento' como 'vendida'/'cancelada' - so' dava pra fazer essa
# transicao enquanto a folga ainda estava 'prevista'. Isso contradizia a
# propria "Passagem pra revisar" (v0.29), que documenta o cenario "folga
# vendida/cancelada DEPOIS DE JA COMPRADA" (ou seja, ja 'confirmada').
# Decisao do Rafael, verbatim: "deixa coberto, pode ser editavel e
# ajustavel dps, se nao cobrir nao tem saida ne? deixa tudo o fluxo fluido".
# Classificado como EVOLUCAO (bump inteiro, nao decimal) porque muda
# logica/estrutura central, nao so' corrige um valor: alarga o WHERE e o
# RETURNS TABLE (coluna `status` nova) da RPC viajai_listar_folgas_
# previstas() (mesmo nome mantido de proposito - continua sendo "folgas em
# aberto pra agir"), muda o default do dropdown "Status novo" (antes fixo
# em 'prevista', agora = status real da linha) e a logica de diff no botao
# Salvar (compara contra o status original, nao contra 'prevista' fixo), e
# muda a regra de negocio da tool de chat propor_atualizar_folga (aceita
# 'prevista'/'confirmada'/'em_andamento' como ponto de partida, nao so'
# 'prevista'). NAO RODA sem rodar schema_v0.31_viajai_confirmar_folgas_
# abertas.txt no Supabase ANTES do deploy (a RPC muda de assinatura).
#
# Viaj.AI — v18.5 (fix pragmatico: "Salvar ajustes de urgencia" continuava
# mudo mesmo apos a v18.4 - mensagem trocada de fila (_flash+rerun) pra
# direta, sem rerun. Achado testando ao vivo 08/09: depois do fix da v18.4
# (que corrigiu o st.error engolido em 3 telas), 2 das 3 telas passaram a
# funcionar certo (Importar RE090 > resolver pendencias, Confirmar folgas >
# salvar alteracoes - confirmado ao vivo), MAS "Previsao de folgas > Salvar
# ajustes de urgencia" continuou sem mostrar NADA (nem sucesso nem erro),
# apesar do dado gravar certo no banco toda vez (confirmado navegando fora
# e voltando). Investigacao a fundo (nao aceito como "so' aparencia"):
# confirmado que o botao registra o clique normal (o caminho SEM rerun -
# "Nenhum ajuste mudou - nada pra salvar" - sempre apareceu certinho, na
# hora); confirmado que a excecao nao e' o problema (a v18.4 ja cobria
# isso, sem efeito aqui); confirmado que nao e' problema de indice/
# comparacao do pandas (a gravacao no banco prova que "mudou" bateu certo).
# Ou seja: SO' a combinacao especifica desse botao com _flash()+st.rerun()
# falha, mesmo sendo codigo estruturalmente identico ao de Confirmar folgas
# (que funciona). Causa exata dentro do Streamlit/data_editor nao
# identificada com certeza - documentado no proprio código como mistério
# nao resolvido. Fix pragmatico aplicado: esse botao especifico agora usa
# st.success()/st.warning() DIRETO (sem fila, sem rerun) - mesmo padrao
# comprovado do "Nenhum ajuste mudou" que sempre funcionou nessa mesma tela.
# Troca aceita: a tabela/KPIs so' refletem o ajuste na proxima interacao
# natural (trocar de aba e voltar, F5) em vez de na hora - mensagem de
# confirmacao sempre aparece, que e' o que importa. Nenhuma mudanca de
# logica de gravacao/dado. Ver 00-handoff.md do VIAJAI no vault
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
import io
import os
import re
import time
import unicodedata
import uuid
from datetime import date, datetime

import requests

import anthropic
import openpyxl
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
# Google Maps (Directions/Distance Matrix) - chave obtida pelo Rafael em
# 02/09, guardada sem uso ate agora (bloco "chat+Maps+Duffel" ficou em
# standby quando o pivo pra "historico real" aconteceu). Retomado 03/09:
# so a parte de CARRO (distancia/tempo, sem busca de preco - mesma regra
# do projeto inteiro de nao inventar preco) - ver _consultar_distancia_carro.
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# TODO (03/09): confirmado contra a doc oficial da Anthropic em 02/09/2026
# que "claude-sonnet-5" e' o identificador de modelo atual - MAS confirma
# de novo aqui se isso mudar (mesmo erro que o TIA.go deixou marcado: nunca
# hardcoded sem checar contra a conta/doc na hora).
MODEL_ID = "claude-sonnet-5"

# Versao/contato exibidos no rodape da sidebar (pedido do Rafael 03/09:
# "anotar a versao e contato pra manter atualizando conforme evolucao") -
# atualizar VERSAO_APP a cada bump de versao (mesmo numero do comentario
# no topo do arquivo), pra sempre bater com o que esta rodando de fato.
# VERSAO_APP = controle INTERNO de build, usado no git/vault/versoes.md -
# nao muda de significado. VERSAO_EXIBIDA = o que aparece pro usuario
# final (Amanda etc) - pedido do Rafael 04/09: "ainda nao entreguei,
# melhor deixar como a versao 1 do projeto" ate o lancamento de verdade.
# CORRIGIDO 10/09 (achado pelo Rafael: rodape ainda mostrava "v1.0" preso,
# nunca tinha acompanhado os bumps de VERSAO_APP - ficou defasado desde que
# foi escrito em 04/09): em vez de string fixa separada, deriva direto de
# VERSAO_APP (troca só o "v" pelo "v1." na frente) - fica sempre em dia
# sozinho a cada bump, sem precisar lembrar de editar as 2 linhas. Quando
# o Rafael decidir acompanhar a versao real (pos-lancamento), e' so trocar
# essa linha pra VERSAO_EXIBIDA = VERSAO_APP.
VERSAO_APP = "v23.0"
VERSAO_EXIBIDA = f"v1.{VERSAO_APP.lstrip('v')} (pré-lançamento)"
CONTATO_SUPORTE = "rafael.nakahara@enermais.com.br"

# Cores EnerMais (mesmo padrao do TIA.go, codigo real conferido antes de
# portar - amostradas do logo-enermais.png) - usadas no relatorio HTML
# exportavel do chat (ver gerar_relatorio_html_viajai).
NAVY = "#171D62"
LARANJA = "#FA9C20"

# Quantas mensagens do chat entram no contexto enviado pra API a cada
# pergunta (janela deslizante) - achado 03/09 debugando o bug do R$640:
# sem limite, toda a conversa (persistida por usuario desde schema_v0.11)
# crescia sem fim dentro da sessao e ia inteira em toda chamada, custando
# mais token a cada pergunta E aumentando o risco do modelo reaproveitar
# resposta velha em vez de consultar de novo. O HISTORICO COMPLETO continua
# salvo pra sempre no banco (viajai_salvar_mensagem_chat) - esse numero so
# limita o que e' REENVIADO como contexto ativo pra API.
JANELA_HISTORICO_CHAT = 24

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

# Codigo IATA por cidade (fato estavel de aviacao, nao preco/horario - sem
# risco de ficar desatualizado do jeito que preco fica). So' as capitais/
# hubs mais comuns; se a cidade digitada nao estiver aqui, usuario digita
# o codigo direto (ex.: "FOR") que a funcao abaixo aceita igual.
_IATA_CIDADES = {
    "fortaleza": "FOR", "sao paulo": "GRU", "são paulo": "GRU",
    "rio de janeiro": "GIG", "salvador": "SSA", "recife": "REC",
    "brasilia": "BSB", "brasília": "BSB", "belo horizonte": "CNF",
    "curitiba": "CWB", "porto alegre": "POA", "manaus": "MAO",
    "belem": "BEL", "belém": "BEL", "vitoria": "VIX", "vitória": "VIX",
    "natal": "NAT", "joao pessoa": "JPA", "joão pessoa": "JPA",
    "maceio": "MCZ", "maceió": "MCZ", "aracaju": "AJU", "teresina": "THE",
    "sao luis": "SLZ", "são luís": "SLZ", "cuiaba": "CGB", "cuiabá": "CGB",
    "campo grande": "CGR", "goiania": "GYN", "goiânia": "GYN",
    "florianopolis": "FLN", "florianópolis": "FLN",
    "maringa": "MGF", "maringá": "MGF",
}


def _resolver_iata(texto):
    """Aceita nome de cidade (casa pelo dicionario acima) ou codigo IATA
    direto (3 letras) - devolve o codigo em maiusculo, ou string vazia se
    nao reconhecer nem uma coisa nem outra (usuario ve e corrige)."""
    if not texto:
        return ""
    limpo = texto.strip()
    if len(limpo) == 3 and limpo.isalpha():
        return limpo.upper()
    return _IATA_CIDADES.get(limpo.lower(), "")


def _link_skyscanner(origem_txt, destino_txt, data_ida_str):
    """Monta o MESMO link oficial de busca do Skyscanner que ja existia
    como botao manual na tela Custo & Passagens (deep-link documentado,
    sem API key - developers.skyscanner.net/docs/referrals/examples) -
    agora tambem disponivel pro Assistente montar em conversa. So' abre
    a pagina real deles com o resultado ja filtrado (origem/destino/data);
    NUNCA devolve preco aqui dentro - quem ve o preco real e' o proprio
    site do Skyscanner quando a pessoa clica."""
    origem_iata = _resolver_iata(origem_txt)
    destino_iata = _resolver_iata(destino_txt)
    if not origem_iata or not destino_iata:
        faltando = []
        if not origem_iata:
            faltando.append(f"origem '{origem_txt}'")
        if not destino_iata:
            faltando.append(f"destino '{destino_txt}'")
        return {
            "erro": (
                f"Nao reconheci {' e '.join(faltando)} - peca pro usuario o codigo "
                "do aeroporto direto (ex.: FOR, GRU) ou o nome da cidade certinho."
            )
        }
    try:
        data_ida = (
            datetime.strptime(data_ida_str, "%Y-%m-%d").date() if data_ida_str else date.today()
        )
    except ValueError:
        data_ida = date.today()
    url = (
        "https://www.skyscanner.net/g/referrals/v1/flights/day-view/"
        f"?origin={origem_iata}&destination={destino_iata}"
        f"&outboundDate={data_ida.isoformat()}&market=BR&currency=BRL&locale=pt-BR"
    )
    return {
        "origem": origem_iata,
        "destino": destino_iata,
        "data_ida": data_ida.isoformat(),
        "link_skyscanner": url,
    }


def _slug_cidade_clickbus(cidade, uf):
    """Gera o slug de cidade+UF no formato que o ClickBus usa nas paginas
    de rota - confirmado lendo os links REAIS publicados na propria home
    de clickbus.com.br em 03/09 (ex.: 'sao-paulo-sp-todos',
    'belo-horizonte-mg-todos'), nao documentado oficialmente como o
    deep-link do Skyscanner (ClickBus so' tem programa de afiliado via
    rede externa, sem link direto por parametro), entao isso e' best-
    effort por observacao, nao garantido pra toda cidade - por isso o
    link sempre volta pro usuario conferir antes de confiar, mesma
    logica do link do Skyscanner."""
    if not cidade or not uf:
        return None
    texto = unicodedata.normalize("NFKD", cidade.strip()).encode("ascii", "ignore").decode("ascii")
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9]+", "-", texto).strip("-")
    if not texto:
        return None
    return f"{texto}-{uf.strip().lower()}-todos"


def _link_clickbus(origem_cidade, origem_uf, destino_cidade, destino_uf):
    """Monta o link de busca de rota de onibus no ClickBus - MESMO
    principio do _link_skyscanner: nunca preco, so' abre a pagina real
    pra conferir manualmente. NAO suporta data especifica (nao achei
    parametro de data confirmado nos links reais observados, e o projeto
    nao chuta formato nao verificado - ver nota em _slug_cidade_clickbus)
    - quem escolhe a data e' o usuario, direto na pagina do ClickBus."""
    slug_origem = _slug_cidade_clickbus(origem_cidade, origem_uf)
    slug_destino = _slug_cidade_clickbus(destino_cidade, destino_uf)
    if not slug_origem or not slug_destino:
        faltando = []
        if not slug_origem:
            faltando.append("origem (cidade + UF)")
        if not slug_destino:
            faltando.append("destino (cidade + UF)")
        return {
            "erro": (
                f"Faltou informar {' e '.join(faltando)} - peca cidade e UF completos "
                "(ex.: cidade='Fortaleza', uf='CE')."
            )
        }
    url = f"https://www.clickbus.com.br/onibus/{slug_origem}/{slug_destino}"
    return {
        "origem": f"{origem_cidade.strip()} - {origem_uf.strip().upper()}",
        "destino": f"{destino_cidade.strip()} - {destino_uf.strip().upper()}",
        "link_clickbus": url,
        "aviso": "Link nao inclui data - escolha a data direto na pagina do ClickBus.",
    }


def _filtrar_dash_multi_viajai(itens):
    """Limpa a lista de chamadas de ferramenta acumuladas numa mesma
    pergunta antes de virar 'Analise do assistente' (dash_multi_viajai):
    quando a IA tenta de novo a MESMA ferramenta com a MESMA entrada,
    fica so' a ultima tentativa; quando ela erra e depois acerta a MESMA
    ferramenta com entrada DIFERENTE (ex.: tentou origem='Maringa' por
    extenso, deu erro, tentou nome='MGF' e acertou), o erro que ela
    mesma corrigiu sai da lista - sem apagar chamadas de ferramentas
    DIFERENTES que deram certo (isso e' o cenario real de comparacao que
    o quadro existe pra guardar, ex.: rota A x rota B, mes X x mes Y -
    ai' os 2 ficam, porque sao 2 fontes de dado diferentes, nao um erro
    corrigido)."""
    vistos, ordem = {}, []
    for item in itens:
        chave = (item.get("tool"), str(item.get("input")))
        if chave not in vistos:
            ordem.append(chave)
        vistos[chave] = item
    dedup = [vistos[chave] for chave in ordem]

    tem_sucesso_por_tool = set()
    for item in dedup:
        resultado = item.get("resultado")
        eh_erro = isinstance(resultado, dict) and "erro" in resultado
        if not eh_erro:
            tem_sucesso_por_tool.add(item.get("tool"))

    filtrados = []
    for item in dedup:
        resultado = item.get("resultado")
        eh_erro = isinstance(resultado, dict) and "erro" in resultado
        if eh_erro and item.get("tool") in tem_sucesso_por_tool:
            continue  # erro que a propria IA corrigiu na mesma pergunta
        filtrados.append(item)
    return filtrados


def _consultar_distancia_carro(origem, destino):
    """Distancia/duracao de carro entre 2 pontos via Google Distance
    Matrix API - chave ja obtida pelo Rafael, retomada 03/09 depois do
    pivo pra "historico real" (ver 00-handoff). So' geografia (distancia
    e tempo reais do Google), NUNCA preco - preco continua vindo so' do
    historico proprio do Viaj.AI, mesma regra do projeto inteiro.
    Devolve dict com distancia_km/duracao_min ou {"erro": ...}."""
    if not GOOGLE_MAPS_API_KEY:
        return {"erro": "Google Maps API key nao configurada (Secrets do Streamlit: GOOGLE_MAPS_API_KEY)"}
    if not origem or not destino:
        return {"erro": "faltou origem ou destino"}
    try:
        resp = requests.get(
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            params={
                "origins": origem,
                "destinations": destino,
                "units": "metric",
                "language": "pt-BR",
                "key": GOOGLE_MAPS_API_KEY,
            },
            timeout=10,
        )
        dado = resp.json()
        if dado.get("status") == "REQUEST_DENIED":
            return {"erro": "Estimativa por carro temporariamente indisponível (configuração de faturamento do Google Maps pendente) — use o Skyscanner/ClickBus normalmente enquanto isso."}
        if dado.get("status") != "OK":
            return {"erro": f"Google Maps recusou a consulta ({dado.get('status')}): {dado.get('error_message', '')}"}
        linha = dado.get("rows", [{}])[0]
        elemento = linha.get("elements", [{}])[0]
        if elemento.get("status") != "OK":
            return {"erro": f"Nao encontrei rota de carro entre esses 2 pontos ({elemento.get('status')}) - confere os nomes."}
        return {
            "origem": dado.get("origin_addresses", [origem])[0],
            "destino": dado.get("destination_addresses", [destino])[0],
            "distancia_km": round(elemento["distance"]["value"] / 1000, 1),
            "duracao_min": round(elemento["duration"]["value"] / 60),
            "distancia_texto": elemento["distance"]["text"],
            "duracao_texto": elemento["duration"]["text"],
        }
    except requests.exceptions.RequestException as e:
        return {"erro": f"Falha de rede consultando o Google Maps: {e}"}
    except Exception as e:
        return {"erro": str(e)}


def _botao_exportar_excel(df, nome_arquivo, label="Exportar Excel"):
    """Exporta o df atual (como esta na tela, ja filtrado/ordenado) pra .xlsx.
    Pedido do Rafael (02/09): dar pra levar a tabela pra fora do app, ex.
    compartilhar com gestor de obra que nao usa o Viaj.AI."""
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    st.download_button(
        label,
        data=buffer.getvalue(),
        file_name=nome_arquivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"export_{nome_arquivo}",
    )


def _obter_cidades_usadas(supabase):
    """Lista de cidades ja usadas em origem/destino, dedup e normalizada
    (schema_v0.37/v0.38) - usada pra sugerir preenchimento nos formularios
    de trecho/lancamento rapido. Pedido do Rafael (10/09): 'da pra deixar
    sugerido o preenchimento correto? tem muitos erros (eu que fiz) e vai
    dar numeros falsos futuramente' - ataca a causa raiz da duplicidade no
    Resumo por rota (schema_v0.36/v0.37 so corrigiam o relatorio com o
    que ja tinha sido digitado; isso aqui evita variacao NOVA). Buscada 1x
    por carregamento de pagina - lista pequena, nao precisa de cache."""
    try:
        r = supabase.rpc("viajai_listar_cidades_usadas").execute()
        return [row["cidade"] for row in (r.data or []) if row.get("cidade")]
    except Exception:
        return []


_SENTINELA_NOVA_CIDADE = "✏️ Digitar outra (não está na lista)"


def _input_cidade_com_sugestao(coluna, label, key, cidades_existentes, valor_atual=None):
    """Campo de Origem/Destino com sugestao das cidades ja usadas antes,
    mais opcao de digitar uma nova - sem travar quem precisa de cidade
    que ainda nao existe na lista. Fica FORA do st.form (respostas de
    selectbox dentro de um form so atualizam a tela no submit - aqui
    precisa reagir na hora pra mostrar/esconder o campo de texto livre),
    por isso recebe a coluna (st ou st.columns(...)[i]) como parametro em
    vez de ser chamado direto dentro do form."""
    opcoes = [_SENTINELA_NOVA_CIDADE] + cidades_existentes
    indice_padrao = 0
    if valor_atual and valor_atual in cidades_existentes:
        indice_padrao = opcoes.index(valor_atual)
    escolha = coluna.selectbox(label, opcoes, index=indice_padrao, key=f"{key}_select")
    if escolha == _SENTINELA_NOVA_CIDADE:
        return coluna.text_input(f"{label} (nova)", value=(valor_atual or ""), key=f"{key}_novo")
    return escolha


TITULOS_RELATORIO_VIAJAI = {
    "consultar_previsao_folgas": "Previsão de folgas",
    "consultar_folgas_aguardando_vinculo": "Folgas aguardando vínculo com RH",
    "consultar_pendencias_import": "Pendências de import (legado)",
    "consultar_historico_folga": "Histórico de folgas",
    "consultar_desvio_planejamento": "Desvio de planejamento",
    "consultar_previsao_gasto_colaborador": "Previsão de gasto por colaborador",
    "consultar_comparativo_custo_folga": "Comparativo de custo x desvio",
    "consultar_sugestao_fornecedor_rota": "Sugestão de fornecedor por rota",
    "consultar_comparar_modais_rota": "Comparativo de modais por rota",
    "consultar_resumo_custo_por_rota": "Resumo de custo por rota",
    "consultar_gasto_por_periodo": "Gasto por período",
    "consultar_lancamentos_rapidos": "Lançamentos rápidos recentes",
    "consultar_historico_imports": "Histórico de imports",
    "consultar_localizacoes_canteiro": "Localizações de canteiro",
    "consultar_distancia_carro": "Distância de carro (Google Maps)",
    "consultar_link_skyscanner": "Link de busca (Skyscanner)",
    "consultar_link_clickbus": "Link de busca (ClickBus)",
    "calcular_diaria_deslocamento": "Cálculo de diária de deslocamento",
}

# Atalhos de relatorio rapido (pedido do Rafael 03/09: "botaozinho que pede
# um relatorio ou tabela especifica") - chamam a MESMA RPC que a ferramenta
# do chat chamaria, so' que direto (sem passar pela IA/Anthropic) - zero
# custo de token, resposta instantanea, determinístico. O chat em
# linguagem natural continua funcionando igual pra tudo que nao tiver
# atalho ou pra pergunta mais especifica/combinada.
def _renderizar_calculo_diaria(resultado):
    """Cartao bonito pro resultado (dict unico, nao lista) de
    calcular_diaria_deslocamento - pedido do Rafael 04/09: 'JSON cru parece
    que deu falha'."""
    valor = resultado.get("valor_total")
    st.metric(
        "Diária de deslocamento",
        f"R$ {float(valor):.2f}" if valor is not None else "—",
    )
    if resultado.get("resumo"):
        st.caption(resultado["resumo"])


def _renderizar_urgencias_dash(resultado):
    """Painel do chat pra consultar_urgencias - resultado e' um dict com
    3 LISTAS (nao 1 lista de linhas, nao 1 dict escalar), caso que o
    renderizador padrao do painel nao cobria e caia no fallback st.write()
    (mostra JSON cru) - achado pelo Rafael 08/09 ('parece erro de
    principiante'). 3 sub-tabelas rotuladas, cada uma com contagem."""
    for _titulo, _chave in (
        ("⏳ Folgas sem vínculo com RH (+60 dias)", "folgas_sem_vinculo_rh"),
        ("🚨 Folgas sem passagem", "folgas_sem_passagem"),
        ("💸 Preços fora do padrão", "precos_fora_padrao"),
        ("↩️ Passagens pra revisar", "passagens_para_revisar"),
    ):
        _linhas = resultado.get(_chave) or []
        st.write(f"**{_titulo}** ({len(_linhas)})")
        if _linhas:
            st.dataframe(pd.DataFrame(_linhas), use_container_width=True, hide_index=True, placeholder="")
        else:
            st.caption("Nenhum registro.")


def _renderizar_tabela_resultado_viajai(tool, df_dash):
    """Tabela padrao do painel/analise do chat - por padrao so' joga todas
    as colunas cruas da RPC (generico, serve pra qualquer ferramenta), mas
    pra ferramentas especificas com colunas dificeis de ler cru, aplica
    column_order/column_config dedicado (pedido do Rafael 10/09:
    'consultar_previsao_folgas' escondia 'dias_restantes' no meio de 13
    colunas tecnicas - mesma info que ja aparece com rotulo bonito na
    pagina 'Previsao de folgas', so' faltava aqui). Extraido pra funcao
    unica porque o painel de baixo (1 consulta) e o quadro de analise
    (varias consultas da mesma pergunta) usam exatamente a mesma logica -
    sem essa funcao, ia duplicar o mesmo column_config nos 2 lugares."""
    if tool == "consultar_previsao_folgas" and "dias_restantes" in df_dash.columns:
        _ordem = [
            "nome", "dias_restantes", "nivel_urgencia",
            "data_saida_prevista", "data_retorno_prevista",
            "obra_nome", "canteiro_nome",
        ]
        _ordem = [c for c in _ordem if c in df_dash.columns]
        _outras = [c for c in df_dash.columns if c not in _ordem]
        st.dataframe(
            df_dash[_ordem + _outras],
            column_config={
                "nome": "Nome",
                "dias_restantes": st.column_config.NumberColumn(
                    "Dias restantes (estim.)",
                    help="Positivo = faltam N dias pra sair de folga. Negativo = já passou N dias do previsto.",
                    format="%d",
                ),
                "nivel_urgencia": "Urgência",
                "data_saida_prevista": "Saída prevista",
                "data_retorno_prevista": "Retorno previsto",
                "obra_nome": "Obra",
                "canteiro_nome": "Canteiro",
            },
            use_container_width=True, hide_index=True, placeholder="",
        )
    else:
        st.dataframe(df_dash, use_container_width=True, hide_index=True, placeholder="")


REPORTS_RAPIDOS_VIAJAI = [
    {"label": "📊 Previsão de folgas", "tool": "consultar_previsao_folgas", "input": {}},
    {"label": "💰 Previsão de gasto", "tool": "consultar_previsao_gasto_colaborador", "input": {}},
    {"label": "🚩 Desvio de planejamento", "tool": "consultar_desvio_planejamento", "input": {"limite": 200}},
    {"label": "🗺️ Resumo por rota", "tool": "consultar_resumo_custo_por_rota", "input": {"limite": 100}},
    {"label": "📅 Gasto por período", "tool": "consultar_gasto_por_periodo", "input": {"meses": 12}},
]


def _corpo_item_relatorio_viajai(tool, resultado):
    """Renderiza o corpo HTML de 1 item de consulta (tabela, dict ou
    grafico de barras em CSS) - extraido de gerar_relatorio_html_viajai
    pra ser reaproveitado tanto pelo relatorio de 1 consulta so' quanto
    pelo relatorio combinado (varias consultas + texto da IA, ver
    gerar_relatorio_analise_html_viajai)."""
    if not resultado:
        return "<p>Nenhum dado encontrado para essa consulta.</p>"
    if tool == "consultar_urgencias" and isinstance(resultado, dict):
        _blocos = []
        for _titulo, _chave in (
            ("Folgas sem vínculo com RH (+60 dias)", "folgas_sem_vinculo_rh"),
            ("Folgas sem passagem", "folgas_sem_passagem"),
            ("Preços fora do padrão", "precos_fora_padrao"),
            ("Passagens pra revisar", "passagens_para_revisar"),
        ):
            _linhas = resultado.get(_chave) or []
            _blocos.append(f"<p><strong>{_titulo} ({len(_linhas)})</strong></p>")
            if _linhas:
                _blocos.append(pd.DataFrame(_linhas).to_html(index=False, border=0, classes="tabela"))
            else:
                _blocos.append("<p>Nenhum registro.</p>")
        return "".join(_blocos)
    if isinstance(resultado, dict):
        if resultado.get("erro"):
            return f"<p>{resultado['erro']}</p>"
        linhas = "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in resultado.items())
        return f"<table class='tabela'>{linhas}</table>"
    df = pd.DataFrame(resultado)
    if tool == "consultar_gasto_por_periodo" and {"periodo", "valor_total"}.issubset(df.columns):
        maximo = df["valor_total"].max() or 1
        barras = "".join(
            f"<div class='barra-linha'><span class='barra-rotulo'>{r['periodo']}</span>"
            f"<div class='barra-fundo'><div class='barra-cheia' "
            f"style='width:{(r['valor_total'] / maximo) * 100:.1f}%'></div></div>"
            f"<span class='barra-valor'>R$ {r['valor_total']:.2f}</span></div>"
            for _, r in df.iterrows()
        )
        return f"<div class='grafico-barras'>{barras}</div>" + df.to_html(index=False, border=0, classes="tabela")
    return df.to_html(index=False, border=0, classes="tabela")


def _estilo_relatorio_viajai():
    """CSS compartilhado pelos 2 geradores de relatorio (1 consulta e
    combinado) - separado pra nao duplicar a folha de estilo inteira."""
    return f"""
  body {{ font-family: Arial, Helvetica, sans-serif; background: #fff; color: #1a1a1a; margin: 32px; }}
  header {{ border-bottom: 4px solid {LARANJA}; padding-bottom: 12px; margin-bottom: 24px; }}
  h1 {{ color: {NAVY}; margin: 0 0 4px 0; font-size: 22px; }}
  h2 {{ color: {NAVY}; font-size: 16px; margin: 28px 0 8px 0; border-left: 4px solid {LARANJA}; padding-left: 8px; }}
  .meta {{ color: #666; font-size: 13px; }}
  .narrativa {{ background: #f7f7f9; border-radius: 6px; padding: 14px 16px; margin: 16px 0; font-size: 14px; line-height: 1.5; }}
  table.tabela {{ border-collapse: collapse; width: 100%; margin-top: 12px; }}
  table.tabela th {{ background: {NAVY}; color: #fff; text-align: left; padding: 8px 10px; font-size: 13px; }}
  table.tabela td {{ padding: 7px 10px; border-bottom: 1px solid #e5e5e5; font-size: 13px; }}
  table.tabela tr:nth-child(even) td {{ background: #f7f7f9; }}
  .grafico-barras {{ margin: 16px 0; }}
  .barra-linha {{ display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }}
  .barra-rotulo {{ width: 90px; font-size: 12px; color: #444; }}
  .barra-fundo {{ flex: 1; background: #eee; border-radius: 3px; overflow: hidden; height: 16px; }}
  .barra-cheia {{ background: {LARANJA}; height: 100%; }}
  .barra-valor {{ width: 110px; font-size: 12px; text-align: right; color: #444; }}
  footer {{ margin-top: 32px; font-size: 11px; color: #999; }}
"""


def gerar_relatorio_html_viajai(extra):
    """Empacota o que esta no painel lateral (dash_extra_viajai) num HTML
    autocontido pra baixar, abrir em qualquer navegador, imprimir em PDF
    (Ctrl+P > Salvar como PDF) ou mandar por e-mail/Teams. Mesmo padrao do
    TIA.go (gerar_relatorio_html, codigo real conferido antes de portar) -
    adaptado porque o Viaj.AI nao usa plotly (so' st.bar_chart nativo): o
    unico grafico (gasto por periodo) vira um mini bar chart em CSS puro
    em vez de fig.to_html() do plotly - zero dependencia nova, mesmo
    espirito de "nao antecipar complexidade que nao precisa ainda".
    Pedido do Rafael 03/09: "o chat pode adiantar geracao de relatorios" -
    funciona tanto pra resultado que veio de atalho (REPORTS_RAPIDOS_VIAJAI)
    quanto de pergunta em linguagem natural, e' o mesmo dash_extra_viajai
    dos dois jeitos.
    """
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    usuario = st.session_state.get("usuario", "")
    tool = extra.get("tool", "")
    titulo = TITULOS_RELATORIO_VIAJAI.get(tool, "Relatório Viaj.AI")
    corpo = _corpo_item_relatorio_viajai(tool, extra.get("resultado"))

    html = f"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>{titulo} — Viaj.AI</title>
<style>{_estilo_relatorio_viajai()}</style>
</head>
<body>
<header>
  <h1>{titulo}</h1>
  <div class="meta">Gerado em {agora} por {usuario} — Viaj.AI {VERSAO_EXIBIDA}</div>
</header>
{corpo}
<footer>Viaj.AI — EnerMais. Dado extraído do sistema no momento da geração, nunca busca preço externo.</footer>
</body>
</html>"""
    return html.encode("utf-8")


def gerar_relatorio_analise_html_viajai(analise):
    """Relatorio COMBINADO: o texto que a propria IA escreveu (a analise/
    comparacao) + TODAS as tabelas que ela consultou pra chegar nessa
    resposta (nao so' a ultima) - pedido do Rafael 03/09: "peço uma
    comparacao especifica, a ia gera um dash... decido gerar o relatorio
    mostrando esses dados estudados e trabalhados... pra nao correr o
    risco de perder alguma informacao trabalhada". Guardado em
    st.session_state.analise_ia_viajai, resetado a cada pergunta nova
    (ver o loop de tool-use em pagina_chat) - reflete sempre a ULTIMA
    troca da conversa, exportavel antes de perguntar outra coisa."""
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    usuario = st.session_state.get("usuario", "")
    texto = (analise.get("texto") or "").strip()
    itens = analise.get("itens") or []

    # texto da IA e' texto puro (nao HTML) - so escapa os caracteres
    # perigosos e quebra paragrafo por linha em branco, sem tentar
    # renderizar markdown (** negrito ** etc fica literal mesmo, nao
    # antecipando complexidade que ninguem pediu ainda).
    import html as _html_stdlib
    paragrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    narrativa = "".join(f"<p>{_html_stdlib.escape(p)}</p>" for p in paragrafos) or "<p>(sem texto)</p>"

    secoes = ""
    for item in itens:
        titulo_item = TITULOS_RELATORIO_VIAJAI.get(item.get("tool", ""), item.get("tool", "Consulta"))
        secoes += f"<h2>{titulo_item}</h2>" + _corpo_item_relatorio_viajai(item.get("tool", ""), item.get("resultado"))

    if not secoes:
        secoes = "<p>Nenhuma consulta associada a essa análise.</p>"

    html = f"""<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>Análise do Assistente — Viaj.AI</title>
<style>{_estilo_relatorio_viajai()}</style>
</head>
<body>
<header>
  <h1>Análise do Assistente Viaj.AI</h1>
  <div class="meta">Gerado em {agora} por {usuario} — Viaj.AI {VERSAO_EXIBIDA}</div>
</header>
<div class="narrativa">{narrativa}</div>
{secoes}
<footer>Viaj.AI — EnerMais. Dado extraído do sistema no momento da geração, nunca busca preço externo. Texto de análise gerado pelo assistente a partir desses dados — revise antes de usar como decisão final.</footer>
</body>
</html>"""
    return html.encode("utf-8")


def _botao_baixar_relatorio_html(extra, key):
    """Botao de download do relatorio empacotado (ver gerar_relatorio_html_viajai)."""
    tool = extra.get("tool", "relatorio")
    nome_arquivo = f"viajai_{tool}.html"
    st.download_button(
        "📄 Baixar relatório desta consulta",
        data=gerar_relatorio_html_viajai(extra),
        file_name=nome_arquivo,
        mime="text/html",
        key=key,
    )


def _botao_baixar_relatorio_analise_html(analise, key):
    """Botao de download do relatorio COMBINADO (ver gerar_relatorio_analise_html_viajai)."""
    st.download_button(
        "📄 Gerar relatório desta análise",
        data=gerar_relatorio_analise_html_viajai(analise),
        file_name="viajai_analise_assistente.html",
        mime="text/html",
        key=key,
    )


def _flash(tipo, texto):
    """Guarda uma mensagem de feedback pra mostrar DEPOIS do st.rerun().

    Achado em teste ao vivo 08/09 (Claude, autorizado pelo Rafael a
    corrigir): varios botoes chamavam st.success(...)/st.info(...) e, na
    linha seguinte, st.rerun() - o rerun reinicia o script ANTES do
    navegador chegar a desenhar aquele frame, entao a mensagem nunca
    aparecia (a acao funcionava e gravava certo no banco, so' o feedback
    visual sumia). Padrao corrigido: guarda a mensagem na sessao antes do
    rerun, _renderizar_flash() (chamada 1x no topo do main(), antes de
    despachar pra pagina) mostra e limpa na leva seguinte.
    """
    st.session_state.setdefault("_flash_queue", []).append((tipo, texto))


def _renderizar_flash():
    fila = st.session_state.pop("_flash_queue", None)
    if not fila:
        return
    for tipo, texto in fila:
        getattr(st, tipo)(texto)


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
    # NOVO schema_v0.40 (Caminho A): linha sem match 1:1 no RH nao vira mais
    # pendencia_import - vira folga provisoria na hora (colaborador_id NULL,
    # nome_provisorio preenchido). "pendentes" aqui conta esse resultado novo
    # ('criada_provisoria') soh pra manter o total do lote coerente com o
    # nome do parametro da RPC de fechamento (p_total_pendencias) - nao
    # significa que foi criada pendencia_import nenhuma.
    pendentes = sum(1 for r in resultados if r.get("resultado") == "criada_provisoria")
    supabase.rpc("viajai_finalizar_import_batch", {
        "p_batch_id": batch_id,
        "p_total_criadas": criadas,
        "p_total_pendencias": pendentes,
    }).execute()

    return arquivo.name, resultados, None


def pagina_importar_re090(supabase):
    st.subheader("Importar RE090")
    # ATUALIZADO 10/09 (schema_v0.40, pedido do Rafael: "a amanda conseguir
    # setar e trabalhar todos os colaboradores... posteriormente a RH subir
    # e o match der ok, reune as informacoes") - sem match unico, a folga
    # e' criada MESMO ASSIM (nao trava mais Amanda esperando o RH), soh fica
    # marcada com o selo "aguardando vinculo com RH" ate alguem vincular
    # (manual, aqui/em Confirmar folgas) ou o sistema achar sozinho
    # ("Tentar vincular automaticamente" abaixo). Ninguem fica esquecido:
    # passado +60 dias sem vincular, aparece um alerta em Urgencias.
    st.caption(
        "Sobe a(s) planilha(s), resolve cada colaborador contra o RH (ao vivo) "
        "e grava a folga já com o canteiro espelho. Sem match único, a folga "
        "entra do mesmo jeito, com o selo ⏳ 'aguardando vínculo com RH' — "
        "nada trava. Quando o RH cadastrar/ativar a pessoa (ou você vincular "
        "na mão), o dado já lançado (custo, trecho, status) fica "
        "automaticamente com ela, sem precisar reunir nada depois. Pode "
        "subir mais de um arquivo de uma vez — cada arquivo vira 1 lote no "
        "histórico, revertível separadamente."
    )

    # CORRIGIDO 10/09 (achado pelo Rafael testando: reimportava o mesmo
    # arquivo sozinho a cada clique em "Importar", e o preview às vezes
    # mostrava gente que já tinha sido apagada da planilha original) -
    # CAUSA RAIZ: st.file_uploader com key fixa nunca esvazia sozinho -
    # ele guarda os bytes exatos de quando o arquivo foi solto na tela, e
    # devolve os MESMOS arquivos (com os MESMOS bytes antigos, mesmo que o
    # arquivo já tenha sido editado/salvo de novo no disco) em toda
    # rerun/clique seguinte, até alguém clicar no "x" de cada arquivo na
    # tela. Resultado: "Importar" de novo sem tirar o arquivo da lista
    # reimporta o mesmo lote (e, se a planilha em disco mudou depois do
    # primeiro upload, reimporta a versão VELHA, congelada no navegador -
    # não busca o arquivo atual). Fix: key dinâmica que muda a cada
    # import bem-sucedido, forçando o widget a esvaziar sozinho - assim
    # cada arquivo só é processado 1 vez, e pra importar nesse mesmo nome
    # de novo precisa soltar ele de novo (bytes atuais, garantido).
    if "import_uploader_geracao" not in st.session_state:
        st.session_state["import_uploader_geracao"] = 0

    arquivos = st.file_uploader(
        "Planilha(s) RE090 (.xlsx)", type=["xlsx"], accept_multiple_files=True,
        key=f"import_uploader_{st.session_state['import_uploader_geracao']}",
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
                    st.dataframe(linhas, placeholder="")

        if st.button("Importar", type="primary"):
            resultado_por_arquivo = {}
            for arquivo, linhas, erro in pre_leituras:
                if erro:
                    continue
                nome, resultados, _ = _importar_um_arquivo(supabase, arquivo)
                resultado_por_arquivo[nome] = resultados
            st.session_state["resultado_import"] = resultado_por_arquivo
            # esvazia o uploader (ver comentário acima) - sem isso o próximo
            # clique em "Importar" reprocessaria os mesmos arquivos nesta lista.
            st.session_state["import_uploader_geracao"] += 1
            st.rerun()

    if "resultado_import" in st.session_state:
        for nome_arquivo, resultados in st.session_state["resultado_import"].items():
            criadas = sum(1 for r in resultados if r.get("resultado") == "criada")
            # ATUALIZADO schema_v0.40: sem match 1:1 no RH nao vira mais
            # pendencia_import - vira folga provisoria na hora ("aguardando
            # vinculo com RH"). O dedup (reimportou a mesma pessoa/data por
            # engano) tambem se aplica a esse caso agora - mesmo resultado
            # 'duplicada' de sempre, so' que comparando nome_provisorio.
            provisorias = sum(1 for r in resultados if r.get("resultado") == "criada_provisoria")
            duplicadas = sum(1 for r in resultados if r.get("resultado") == "duplicada")
            msg = f"**{nome_arquivo}**: {criadas} folga(s) criada(s)"
            if provisorias:
                msg += f", {provisorias} criada(s) aguardando vínculo com RH (⏳ nome não bateu 1:1 agora — nada travado, vincula manual ou automático depois)"
            if duplicadas:
                msg += f", {duplicadas} duplicada(s) (já existia folga prevista pra essa pessoa nessa mesma data — ignorada, não criou de novo)"
            st.success(msg + ".")
            st.dataframe(resultados, placeholder="")
            if criadas:
                st.info(
                    "➡️ Próximo passo: as folgas criadas já aparecem em **Previsão de folgas** "
                    "(quando cada uma vai chegar) e, mais perto da data, em **Confirmar folgas** "
                    "(pra registrar saída/retorno real)."
                )
            if provisorias:
                st.info(
                    "🔗 Tem folga aguardando vínculo com RH nesse lote — use "
                    "'Tentar vincular automaticamente' embaixo (tenta casar sozinho contra "
                    "o RH atual) ou vá em **Confirmar folgas** pra vincular manualmente."
                )

    st.divider()
    st.subheader("Histórico de imports")
    st.caption(
        "Cada linha é 1 upload. Reverter apaga as folgas criadas por esse "
        "lote específico — só as que ninguém mexeu ainda (status ainda "
        "'prevista', sem trecho de viagem associado); o resto fica registrado "
        "mas não é apagado, pra não perder trabalho já feito em cima."
    )
    lotes = supabase.rpc("viajai_listar_import_batches", {"p_limite": 200}).execute()
    if lotes.data:
        for lote in lotes.data[:20]:
            cols = st.columns([3, 2, 2, 2, 2])
            cols[0].write(f"{lote['nome_arquivo']}")
            cols[1].write(lote["criado_em"][:16].replace("T", " "))
            cols[2].write(f"{lote['total_criadas']} criada(s)")
            cols[3].write(f"{lote['total_pendencias']} aguardando vínculo")
            if lote["revertido"]:
                cols[4].write("↩️ revertido")
            else:
                if cols[4].button("Reverter", key=f"reverter_{lote['id']}"):
                    rev = supabase.rpc(
                        "viajai_reverter_import_batch", {"p_batch_id": lote["id"]}
                    ).execute()
                    r = rev.data[0] if rev.data else {}
                    _flash("success",
                        f"Revertido: {r.get('folgas_removidas', 0)} folga(s) removida(s), "
                        f"{r.get('folgas_puladas', 0)} pulada(s) (já tinham sido mexidas), "
                        f"{r.get('pendencias_removidas', 0)} pendência(s) removida(s)."
                    )
                    st.rerun()

        with st.expander(f"📋 Consultar histórico completo ({len(lotes.data)} lote(s))"):
            df_lotes = pd.DataFrame(lotes.data)
            colunas_consulta = [c for c in [
                "nome_arquivo", "criado_em", "criado_por", "total_linhas",
                "total_criadas", "total_pendencias", "revertido",
                "revertido_por", "revertido_em",
            ] if c in df_lotes.columns]
            df_lotes = df_lotes[colunas_consulta]
            st.dataframe(df_lotes, hide_index=True, use_container_width=True, placeholder="")
            _botao_exportar_excel(df_lotes, "viajai_historico_imports.xlsx")
    else:
        st.caption("Nenhum import feito ainda.")

    st.divider()
    # NOVO schema_v0.40 (Caminho A - confirmado pelo Rafael 10/09: "1. sim
    # caminho A"): substitui o antigo fluxo de pendencia_import pra RE090.
    # Sem match 1:1, a folga ja e' criada com colaborador_id NULL - essa
    # secao concentra as 3 acoes possiveis sobre ela: vincular na mao,
    # tentar vincular sozinho (todas de uma vez), ou so' revisar/deixar pro
    # alerta de +60 dias em Urgencias.
    st.subheader("⏳ Folgas aguardando vínculo com RH")
    st.caption(
        "Folga criada (via import ou manual) sem achar 1:1 no RH no momento — "
        "não trava nada, a Amanda já pode lançar custo/trecho/status normalmente "
        "usando o nome provisório. Some dessa lista sozinha assim que vincular "
        "(manual abaixo, ou automático). Sem vincular há mais de 60 dias, "
        "aparece um alerta separado em **Urgências**."
    )
    try:
        # Junta viajai_listar_folgas_previstas (prevista/confirmada/em_andamento)
        # + viajai_listar_folgas_desvio (status <> 'prevista', cobre tambem
        # realizada/vendida/cancelada) - mesmo padrao de "Confirmar folgas"
        # (mostrar_fechadas) - senao uma folga provisoria que ja foi marcada
        # vendida/cancelada/realizada sem nunca ter sido vinculada ficaria
        # visivel so' no alerta de +60 dias, sem nenhuma tela pra resolver.
        _provisorias_resp = supabase.rpc(
            "viajai_listar_folgas_previstas", {"p_limite": 1000}
        ).execute()
        _folgas_provisorias = [
            f for f in (_provisorias_resp.data or []) if f.get("aguardando_vinculo_rh")
        ]
        _ids_prov_ja_presentes = {int(f["folga_id"]) for f in _folgas_provisorias}
        _fechadas_prov_resp = supabase.rpc(
            "viajai_listar_folgas_desvio", {"p_limite": 1000}
        ).execute()
        for _f in (_fechadas_prov_resp.data or []):
            if _f.get("aguardando_vinculo_rh") and int(_f["folga_id"]) not in _ids_prov_ja_presentes:
                _folgas_provisorias.append({
                    "folga_id": _f["folga_id"], "nome": _f["nome"], "obra_nome": _f.get("obra_nome"),
                    "status": _f["status"], "data_saida_prevista": _f.get("data_saida_prevista"),
                })
    except Exception as e:
        _folgas_provisorias = []
        st.error(f"Não consegui consultar (rodou o schema_v0.40 no Supabase?) — {e}")

    c_auto, c_info = st.columns([1, 3])
    if c_auto.button("🔄 Tentar vincular automaticamente"):
        r_auto = supabase.rpc("viajai_tentar_vincular_automatico", {}).execute()
        resumo_auto = r_auto.data[0] if r_auto.data else {}
        vinculadas_auto = resumo_auto.get("vinculadas", 0)
        ainda_auto = resumo_auto.get("ainda_sem_vinculo", 0)
        if vinculadas_auto:
            _flash("success", f"{vinculadas_auto} folga(s) vinculada(s) agora. {ainda_auto} continuam sem vínculo (sem match único no RH atual).")
        else:
            _flash("info", f"Nenhuma vinculou ainda ({ainda_auto} continuam sem match único no RH).")
        st.rerun()
    c_info.caption(
        "Tenta casar cada nome provisório contra o RH ATUAL — útil quando o RH "
        "cadastrou/ativou a pessoa depois do import. Só vincula quando dá match "
        "único (mesma regra do import); ambíguo (2+ pessoas com nome parecido) "
        "fica pra vínculo manual abaixo."
    )

    if not _folgas_provisorias:
        st.caption("Nenhuma folga aguardando vínculo com RH no momento.")
    else:
        df_prov = pd.DataFrame(_folgas_provisorias)
        st.dataframe(
            df_prov[["folga_id", "nome", "obra_nome", "status", "data_saida_prevista"]],
            column_config={
                "folga_id": st.column_config.NumberColumn("Nº", format="%d"),
                "nome": "Nome (provisório)",
                "obra_nome": "Obra/canteiro (texto da planilha ou manual)",
                "status": "Status",
                "data_saida_prevista": st.column_config.DateColumn("Saída prevista"),
            },
            hide_index=True, use_container_width=True, placeholder="",
        )
        st.write("**🔗 Vincular ao RH manualmente**")
        try:
            _ativos_resp = supabase.rpc("viajai_colaboradores_ativos").execute()
            _ativos_data = _ativos_resp.data or []
        except Exception as e:
            _ativos_data = []
            st.error(f"Não consegui consultar colaboradores ativos — {e}")
        if not _ativos_data:
            st.caption("Nenhum colaborador ativo encontrado no RH pra vincular.")
        else:
            _opcoes_folga_prov = {
                f"#{f['folga_id']} — {f['nome']} — {f.get('status') or '—'} — "
                f"saída {f.get('data_saida_prevista') or '—'}": f["folga_id"]
                for f in _folgas_provisorias
            }
            _opcoes_colab = {
                f"{c['nome']} — {c.get('obra_nome') or '—'} ({c['colaborador_id']})": c["colaborador_id"]
                for c in _ativos_data
            }
            with st.form("form_vincular_folga_rh"):
                folga_prov_sel = st.selectbox("Folga aguardando vínculo", list(_opcoes_folga_prov.keys()), key="vinc_rh_folga")
                colab_sel = st.selectbox("Colaborador (RH)", list(_opcoes_colab.keys()), key="vinc_rh_colab")
                enviar_vinc_rh = st.form_submit_button("Vincular")
            if enviar_vinc_rh:
                try:
                    supabase.rpc("viajai_vincular_colaborador_folga", {
                        "p_folga_id": _opcoes_folga_prov[folga_prov_sel],
                        "p_colaborador_id": _opcoes_colab[colab_sel],
                    }).execute()
                    _flash("success", "Folga vinculada ao colaborador do RH.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao vincular: {e}")

    st.divider()
    with st.expander("➕ Adicionar folga manualmente (sem planilha)"):
        st.caption(
            "Pra demanda emergencial (ex.: comprar passagem urgente) sem esperar "
            "o próximo RE090 — pedido do Rafael 10/09. Resolve contra o RH na "
            "hora igual ao import; sem match, cria como 'aguardando vínculo com "
            "RH' (aparece na lista acima) do mesmo jeito."
        )
        with st.form("form_criar_folga_manual"):
            nome_manual = st.text_input("Nome do colaborador", key="manual_nome")
            matricula_manual = st.text_input("Matrícula (opcional, ajuda a desambiguar nome repetido)", key="manual_matricula")
            obra_texto_manual = st.text_input("Obra/canteiro (texto livre, opcional)", key="manual_obra_texto")
            c_m1, c_m2, c_m3 = st.columns(3)
            data_saida_manual = c_m1.date_input("Saída prevista", value=None, key="manual_data_saida")
            data_retorno_manual = c_m2.date_input("Retorno previsto", value=None, key="manual_data_retorno")
            data_ultimo_retorno_manual = c_m3.date_input("Último retorno (base do ciclo, opcional)", value=None, key="manual_data_ultimo_retorno")
            enviar_manual = st.form_submit_button("Criar folga", type="primary")
        if enviar_manual:
            if not nome_manual or not nome_manual.strip():
                st.error("Nome é obrigatório.")
            else:
                try:
                    r_manual = supabase.rpc("viajai_criar_folga_manual", {
                        "p_nome": nome_manual.strip(),
                        "p_matricula": matricula_manual.strip() or None,
                        "p_texto_obra_canteiro": obra_texto_manual.strip() or None,
                        "p_data_saida_prevista": data_saida_manual.isoformat() if data_saida_manual else None,
                        "p_data_retorno_prevista": data_retorno_manual.isoformat() if data_retorno_manual else None,
                        "p_data_ultimo_retorno": data_ultimo_retorno_manual.isoformat() if data_ultimo_retorno_manual else None,
                    }).execute()
                    r_manual_linha = r_manual.data[0] if r_manual.data else {}
                    if r_manual_linha.get("resultado") == "criada":
                        _flash("success", f"Folga criada e já vinculada a {nome_manual.strip()} (achou 1:1 no RH).")
                    else:
                        _flash("success", f"Folga criada aguardando vínculo com RH ({nome_manual.strip()}) — sem match único agora, aparece na lista acima.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao criar folga manual: {e}")

    st.divider()
    pend = supabase.rpc("viajai_listar_pendencias_import", {"p_apenas_nao_resolvidas": True}).execute()
    # NOVO 10/09 (pedido do Rafael): contador ao lado do título, pra ver de
    # relance se a fila tá crescendo ou diminuindo sem precisar contar linha.
    st.subheader(f"Pendências abertas — legado ({len(pend.data or [])})")
    st.caption(
        "⚠️ Desde o schema_v0.40, o import RE090 não gera mais pendência nova "
        "aqui — nome sem match vira folga 'aguardando vínculo com RH' (seção "
        "acima). Esta lista só mostra pendência criada ANTES dessa mudança "
        "(deve ficar vazia depois da limpeza de base de teste). Mantida só "
        "pra não perder o que já estava registrado."
    )
    st.caption(
        "Marca 'Resolvida' pra tirar da lista (revisou manualmente e não "
        "precisa mais aparecer aqui — não cria folga nenhuma, só limpa a fila; "
        "a pendência continua salva no banco, só sai da lista de abertas). "
        "⚠️ ATENÇÃO (dúvida do Rafael 10/09, confirmada no código): marcar "
        "resolvida é **definitivo pro 'Reprocessar pendências'** — essa "
        "pendência nunca mais entra na tentativa automática de casar com o "
        "RH, nem se a pessoa for cadastrada/ativada lá depois. Só marque se "
        "já resolveu esse caso por fora (ex.: criou a folga manualmente, ou "
        "confirmou que a pessoa não vai mais trabalhar aqui). Se ainda pode "
        "ser só questão de tempo do RH cadastrar, deixe sem marcar — "
        "'Reprocessar pendências' vai pegar sozinho quando der match. Marcou "
        "sem querer? Dá pra reabrir no expander embaixo."
    )
    if pend.data:
        df_pend = pd.DataFrame(pend.data)
        df_pend = df_pend.drop(columns=[c for c in ["origem"] if c in df_pend.columns])
        df_pend["resolvido"] = False
        editado_pend = st.data_editor(
            df_pend,
            column_config={
                "resolvido": st.column_config.CheckboxColumn(
                    "✏️ Resolvida",
                    help=(
                        "Definitivo pro reprocessamento automático (ver aviso "
                        "acima) — marca e clica em Salvar embaixo."
                    ),
                ),
            },
            disabled=[c for c in df_pend.columns if c not in ("resolvido",)],
            hide_index=True,
            use_container_width=True,
            key="editor_pendencias", placeholder="",
        )
        _botao_exportar_excel(df_pend.drop(columns=["resolvido"]), "viajai_pendencias.xlsx")
        if st.button(
            "🔄 Reprocessar pendências (legado)",
            help=(
                "Só afeta pendência antiga (de antes do schema_v0.40) — pra "
                "folga 'aguardando vínculo com RH' (fluxo atual), use "
                "'Tentar vincular automaticamente' na seção acima. Tenta casar "
                "de novo cada pendência contra o cadastro ATUAL do RH — sem "
                "precisar reupload do arquivo."
            ),
        ):
            r_reproc = supabase.rpc("viajai_reprocessar_pendencias_import", {}).execute()
            resumo_reproc = r_reproc.data[0] if r_reproc.data else {}
            reprocessadas = resumo_reproc.get("reprocessadas", 0)
            ainda_pendentes = resumo_reproc.get("ainda_pendentes", 0)
            if reprocessadas:
                _flash("success",
                    f"{reprocessadas} pendência(s) casaram agora e viraram folga "
                    f"(ou já existiam e só limparam a fila). "
                    f"{ainda_pendentes} continuam sem match no RH."
                )
            else:
                _flash("info", f"Nenhuma pendência casou ainda ({ainda_pendentes} continuam sem match no RH).")
            st.rerun()
        if st.button("Salvar pendências resolvidas"):
            marcadas = editado_pend[editado_pend["resolvido"] == True]  # noqa: E712
            if marcadas.empty:
                st.info("Nenhuma pendência marcada — nada pra salvar.")
            else:
                erros = 0
                for _, linha in marcadas.iterrows():
                    try:
                        supabase.rpc("viajai_marcar_pendencia_resolvida", {
                            "p_pendencia_id": int(linha["id"]),
                            "p_resolvido": True,
                        }).execute()
                    except Exception as e:
                        erros += 1
                        _flash("error", f"Erro ao resolver pendência {linha['id']}: {e}")
                sucesso = len(marcadas) - erros
                if sucesso:
                    _flash("success", f"{sucesso} pendência(s) marcada(s) como resolvida(s).")
                st.rerun()
    else:
        st.caption("Nenhuma pendência em aberto.")

    # NOVO 10/09 (dúvida do Rafael: "pra onde vai" quando marca resolvida) -
    # a linha nunca é apagada, só some da lista acima (resolvido=true) - RPC
    # já suportava listar as resolvidas também (schema_v0.4, parâmetro
    # p_apenas_nao_resolvidas), só a tela nunca tinha chamado com False.
    with st.expander("Ver pendências já marcadas como resolvidas"):
        pend_todas = supabase.rpc("viajai_listar_pendencias_import", {"p_apenas_nao_resolvidas": False}).execute()
        df_pend_resolvidas = pd.DataFrame(pend_todas.data or [])
        if not df_pend_resolvidas.empty:
            df_pend_resolvidas = df_pend_resolvidas[df_pend_resolvidas["resolvido"] == True]  # noqa: E712
        if df_pend_resolvidas.empty:
            st.caption("Nenhuma pendência resolvida ainda.")
        else:
            st.caption(
                "Marcou sem querer, ou o caso na verdade ainda pode casar com "
                "o RH mais tarde? Reabre aqui — ela volta pra lista de abertas "
                "e volta a entrar em 'Reprocessar pendências'."
            )
            st.dataframe(
                df_pend_resolvidas.drop(columns=[c for c in ["origem"] if c in df_pend_resolvidas.columns]),
                hide_index=True, use_container_width=True, placeholder="",
            )
            _reabrir_rotulo = df_pend_resolvidas.apply(
                lambda r: f"#{r['id']} — {r.get('nome_planilha') or '—'} — {r.get('motivo') or '—'}",
                axis=1,
            )
            _escolha_reabrir = st.selectbox("Qual reabrir?", _reabrir_rotulo, key="pend_reabrir_select")
            _id_reabrir = int(df_pend_resolvidas.loc[_reabrir_rotulo == _escolha_reabrir, "id"].iloc[0])
            if st.button("↩️ Reabrir esta pendência", key="pend_reabrir_btn"):
                supabase.rpc("viajai_marcar_pendencia_resolvida", {
                    "p_pendencia_id": _id_reabrir,
                    "p_resolvido": False,
                }).execute()
                _flash("success", "Pendência reaberta — volta a aparecer em 'Pendências abertas'.")
                st.rerun()


_STATUS_OPCOES = ["prevista", "confirmada", "em_andamento", "realizada", "vendida", "cancelada"]


def pagina_confirmar_folgas(supabase):
    st.subheader("Confirmar folgas")
    st.caption(
        "Fecha o ciclo: registre aqui o que realmente aconteceu com cada "
        "folga em aberto (status 'prevista', 'confirmada' ou 'em_andamento' "
        "— via import ou manual). Sem isso, a Previsão de folgas nunca "
        "reflete a realidade — só o que foi planejado. Edita direto na "
        "tabela: muda o 'Status novo' de quem mudou, preenche data real se "
        "for o caso, e clica em Salvar no final — quem não mudar o status "
        "não é tocado."
    )
    st.info(
        "✏️ Só as colunas com lápis são editáveis: **Status novo**, "
        "**Saída real**, **Retorno real** e **Motivo**. O resto (Situação, "
        "Urgência, Nome, Obra, Canteiro, datas previstas) é só pra consulta. "
        "Depois de salvar aqui, se a folga precisava de passagem, ela some "
        "de 'Confirmar folgas' mas pode continuar aparecendo em **Urgências** "
        "até você lançar a compra em **Custo & Passagens**.\n\n"
        "O que cada status significa: **confirmada** = já tem data marcada/"
        "passagem definida, mas a pessoa ainda não saiu; **em_andamento** = "
        "já saiu, ainda não voltou (preenche Saída real); **realizada** = "
        "já voltou (preenche Saída real e Retorno real); **vendida** = não "
        "saiu, converteu os dias em pagamento e continua trabalhando; "
        "**cancelada** = a folga não vai mais acontecer."
    )
    st.caption(
        "Por padrão só aparece quem ainda está em aberto. Marque a caixa abaixo "
        "pra também poder corrigir uma folga que já saiu daqui (realizada, "
        "vendida ou cancelada) — o salvar funciona igual."
    )
    # NOVO schema_v0.40: folga sem match 1:1 no RH aparece aqui do mesmo
    # jeito, com "⏳ aguardando vínculo com RH" na Situação — nao trava,
    # da' pra editar Status/datas normalmente com o nome provisorio. Vincular
    # ao RH (manual ou automatico) fica centralizado em "Importar RE090" pra
    # nao duplicar a mesma acao de escrita em 2 telas.
    st.caption(
        "⏳ Viu 'aguardando vínculo com RH' na Situação? É folga com nome "
        "provisório (import ou lançamento manual) que ainda não achou 1:1 no "
        "RH — pode editar normalmente aqui, o vínculo (manual ou automático) "
        "fica na página **Importar RE090**."
    )

    # v21.3 (pedido do Rafael 09/09: "se eu quiser atualizar uma folga
    # passada, na qual o funcionario ja ate retornou, ou q nao esteja em
    # confirmar folgas, nao tem como? / conseguimos deixar editavel?").
    # ACHADO antes de mexer (regra-mae): viajai_atualizar_folga (RPC de
    # escrita) NUNCA teve trava de status atual - aceita qualquer folga_id
    # e status novo, sempre gravou certo. O gargalo era so' a LISTAGEM -
    # viajai_listar_folgas_previstas so' traz prevista/confirmada/em_andamento
    # de proposito (schema_v0.31). Fix: quando marcado, tambem busca em
    # viajai_listar_folgas_desvio (ja existe desde schema_v0.9, cobre TODO
    # status <> 'prevista' incluindo realizada/vendida/cancelada, mesmas
    # colunas essenciais que essa tela ja usa) e mistura na mesma tabela -
    # zero RPC nova, zero schema novo, mesmo botao Salvar/mesma RPC de escrita.
    mostrar_fechadas = st.checkbox(
        "Mostrar também folgas já concluídas (realizada/vendida/cancelada)",
        key="cf_mostrar_fechadas",
        help=(
            "Pra corrigir uma folga que já passou (data errada, status errado, "
            "esqueceu de marcar) mesmo depois dela sair desta lista. Salvar "
            "funciona igual — o sistema nunca travou por status atual, só "
            "não aparecia aqui por padrão."
        ),
    )

    previstas = supabase.rpc("viajai_listar_folgas_previstas", {"p_limite": 300}).execute()
    linhas = list(previstas.data or [])
    _STATUS_ABERTOS = {"prevista", "confirmada", "em_andamento"}
    if mostrar_fechadas:
        try:
            fechadas_resp = supabase.rpc("viajai_listar_folgas_desvio", {"p_limite": 500}).execute()
        except Exception as e:
            fechadas_resp = None
            st.error(f"Não consegui buscar as folgas concluídas (rodou o schema_v0.9 no Supabase?) — {e}")
        if fechadas_resp and fechadas_resp.data:
            _ids_ja_presentes = {int(l["folga_id"]) for l in linhas}
            _colunas_comuns = [
                "folga_id", "colaborador_id", "nome", "obra_nome", "canteiro_nome",
                "status", "data_saida_prevista", "data_retorno_prevista",
                "aguardando_vinculo_rh",
            ]
            for l in fechadas_resp.data:
                if l["status"] not in _STATUS_ABERTOS and int(l["folga_id"]) not in _ids_ja_presentes:
                    linhas.append({k: l.get(k) for k in _colunas_comuns})

    if not linhas:
        if mostrar_fechadas:
            st.caption("Nenhuma folga encontrada — nem em aberto, nem concluída/vendida/cancelada.")
        else:
            st.caption("Nenhuma folga em aberto (prevista/confirmada/em_andamento) aguardando ação no momento.")
    else:
        base = pd.DataFrame(linhas)
        # "atrasada" so' faz sentido pra quem ainda esta em aberto - uma
        # folga ja realizada/vendida/cancelada nao e' um problema pendente,
        # mesmo com data prevista no passado (e' o caso normal dela).
        _hoje = date.today()
        base["data_saida_prevista"] = pd.to_datetime(base["data_saida_prevista"]).dt.date

        # NOVO schema_v0.40: folga provisoria (colaborador_id NULL, aguardando
        # RH cadastrar/vincular) ganha um selo somado a situacao normal - nao
        # substitui "atrasada"/"concluida", so' avisa que falta o vinculo.
        def _situacao(row):
            if row["status"] not in _STATUS_ABERTOS:
                situacao_base = "🔒 concluída/fechada"
            else:
                d = row["data_saida_prevista"]
                situacao_base = "⚠️ atrasada" if pd.notna(d) and d < _hoje else "no prazo"
            if row.get("aguardando_vinculo_rh"):
                return f"⏳ aguardando vínculo com RH + {situacao_base}"
            return situacao_base

        base["situacao"] = base.apply(_situacao, axis=1)

        # urgencia (mesmo calculo da tela Previsao de folgas) trazida por
        # colaborador_id - pedido do Rafael: ajuda a Amanda a priorizar
        # quem confirmar primeiro sem precisar trocar de tela.
        prev_resp = supabase.rpc("viajai_previsao_folgas").execute()
        if prev_resp.data:
            df_urg = pd.DataFrame(prev_resp.data)[["colaborador_id", "nivel_urgencia"]]
            df_urg = df_urg.rename(columns={"nivel_urgencia": "urgencia"})
            base = base.merge(df_urg, on="colaborador_id", how="left")
        else:
            base["urgencia"] = None
        base["urgencia"] = base["urgencia"].fillna("—")

        # origem do import (schema_v0.33, pedido do Rafael 09/09: "lastro"
        # por funcionario - de qual arquivo/planilha RE090 e quando veio
        # essa folga). So' leitura, join simples por folga_id -> nao mexe
        # em nenhuma RPC/tela existente, nao afeta performance.
        try:
            origem_resp = supabase.rpc(
                "viajai_origem_folgas", {"p_folga_ids": base["folga_id"].astype(int).tolist()}
            ).execute()
        except Exception:
            origem_resp = None
        if origem_resp and origem_resp.data:
            df_origem = pd.DataFrame(origem_resp.data)
            base = base.merge(df_origem, on="folga_id", how="left")
        else:
            base["nome_planilha_origem"] = None
            base["nome_arquivo"] = None
            base["import_criado_em"] = None

        def _fmt_origem(row):
            if pd.isna(row.get("nome_arquivo")):
                return "— (sem import registrado)"
            data_txt = ""
            if pd.notna(row.get("import_criado_em")):
                try:
                    data_txt = f" em {str(row['import_criado_em'])[:10]}"
                except Exception:
                    data_txt = ""
            nome_txt = ""
            if pd.notna(row.get("nome_planilha_origem")) and row["nome_planilha_origem"]:
                nome_txt = f" (\"{row['nome_planilha_origem']}\" na planilha)"
            return f"{row['nome_arquivo']}{data_txt}{nome_txt}"

        base["origem_import"] = base.apply(_fmt_origem, axis=1)

        base = base.sort_values(by=["situacao", "data_saida_prevista"], ascending=[True, True])
        # v18.6 (pedido do Rafael 08/09, "deixa coberto, fluxo fluido"): antes
        # essa lista so' trazia folga 'prevista' e o default do dropdown era
        # sempre "prevista" fixo. Agora tambem traz 'confirmada'/'em_andamento'
        # (schema_v0.31), entao o ponto de partida de cada linha tem que ser
        # o status REAL dela, senao toda linha ja confirmada apareceria como
        # se estivesse "prevista" (errado) e qualquer status escolhido pareceria
        # uma "mudanca" mesmo sem ser.
        base["status_novo"] = base["status"]
        base["data_saida_real"] = pd.NaT
        base["data_retorno_real"] = pd.NaT
        base["motivo_venda"] = ""

        editado = st.data_editor(
            base,
            column_order=[
                "status", "situacao", "urgencia", "nome", "obra_nome", "canteiro_nome",
                "data_saida_prevista", "data_retorno_prevista", "origem_import",
                "status_novo", "data_saida_real", "data_retorno_real", "motivo_venda",
            ],
            column_config={
                "status": st.column_config.TextColumn(
                    "🔒 Status atual", disabled=True,
                    help="Status real da folga agora — inclui realizada/vendida/cancelada quando "
                         "'Mostrar também folgas já concluídas' está marcado.",
                ),
                "situacao": st.column_config.TextColumn("🔒 Situação", disabled=True),
                "urgencia": st.column_config.TextColumn(
                    "🔒 Urgência", disabled=True,
                    help="Calculado automaticamente. Pra forçar um nível diferente pra 1 pessoa, use a tela 'Previsão de folgas'.",
                ),
                "nome": st.column_config.TextColumn("🔒 Nome", disabled=True),
                "obra_nome": st.column_config.TextColumn("🔒 Obra", disabled=True),
                "canteiro_nome": st.column_config.TextColumn("🔒 Canteiro", disabled=True),
                "data_saida_prevista": st.column_config.DateColumn("🔒 Saída prevista", disabled=True),
                "data_retorno_prevista": st.column_config.DateColumn("🔒 Retorno previsto", disabled=True),
                "origem_import": st.column_config.TextColumn(
                    "🔒 Origem do import", disabled=True,
                    help="De qual import RE090 (arquivo + data) essa folga veio, e o nome exatamente como veio na planilha. '—' = folga anterior a essa rastreabilidade (schema_v0.33) ou criada sem import associado.",
                ),
                "status_novo": st.column_config.SelectboxColumn(
                    "✏️ Status novo", options=_STATUS_OPCOES, required=True,
                    help="Deixa igual ao 'Status atual' pra não mexer nessa linha.",
                ),
                "data_saida_real": st.column_config.DateColumn(
                    "✏️ Saída real", help="Preenche se marcou 'em_andamento' ou 'realizada'."
                ),
                "data_retorno_real": st.column_config.DateColumn(
                    "✏️ Retorno real", help="Preenche se marcou 'realizada'."
                ),
                "motivo_venda": st.column_config.TextColumn(
                    "✏️ Motivo (se vendida)", help="Opcional, só faz sentido se marcou 'vendida'."
                ),
            },
            hide_index=True,
            use_container_width=True,
            key="editor_confirmar_folgas", placeholder="",
        )
        _botao_exportar_excel(
            base.drop(columns=["status_novo", "data_saida_real", "data_retorno_real", "motivo_venda"]),
            "viajai_confirmar_folgas.xlsx",
        )

        if st.button("Salvar alterações", type="primary"):
            # v18.6: compara contra o status ORIGINAL de cada linha (base,
            # antes da edicao) - nao mais contra "prevista" fixo, ja que
            # agora uma linha pode comecar em 'confirmada'/'em_andamento'.
            mudou = editado[editado["status_novo"] != base["status"]]
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
                        _flash("error", f"Erro ao salvar {linha['nome']}: {e}")
                sucesso = len(mudou) - erros
                if sucesso:
                    _flash("success", f"{sucesso} folga(s) atualizada(s).")
                st.rerun()

        st.caption(f"{len(previstas.data or [])} folga(s) em aberto aguardando confirmação.")

    st.divider()
    st.subheader("Histórico")
    st.caption("Últimas mudanças registradas — quem, quando, o que mudou.")
    hist = supabase.rpc("viajai_listar_historico_folga", {"p_limite": 100}).execute()
    if hist.data:
        st.dataframe(hist.data, use_container_width=True, hide_index=True, placeholder="")
    else:
        st.caption("Nenhuma mudança registrada ainda.")


_ORDEM_URGENCIA = {"atrasado": -1, "critico": 0, "atencao": 1, "normal": 2}


def pagina_previsao(supabase):
    st.subheader("Previsão de folgas")
    st.caption(
        "Calculado ao vivo: colaborador ativo no RH + última folga conhecida "
        "no Viaj.AI. Sem histórico ainda = sem previsão (precisa de ao menos "
        "1 folga registrada, manual ou via import)."
    )
    st.caption(
        "➡️ Pra que serve: só olhar/planejar (não edita a folga aqui). Quando "
        "a data se aproxima, vá em **Confirmar folgas** pra registrar saída/"
        "retorno real. Os mesmos alertas de urgência aparecem resumidos na "
        "aba **Urgências**."
    )
    resp = supabase.rpc("viajai_previsao_folgas").execute()
    if not resp.data:
        st.caption("Sem dados ainda.")
        return

    df = pd.DataFrame(resp.data)

    # NOVO schema_v0.40: viajai_previsao_folgas() parte de
    # viajai_colaboradores_ativos() (RH), entao uma folga provisoria
    # (colaborador_id NULL, ainda sem match) nao tem como aparecer aqui por
    # natureza - essa tela e' centrada em quem JA esta identificado no RH.
    # Avisa quantas existem e onde ver/agir, pra nao parecer que sumiram.
    _folgas_abertas_panorama = supabase.rpc("viajai_listar_folgas_previstas", {"p_limite": 1000}).execute()
    _qtd_aguardando_vinculo = sum(
        1 for f in (_folgas_abertas_panorama.data or []) if f.get("aguardando_vinculo_rh")
    )
    if _qtd_aguardando_vinculo:
        st.info(
            f"⏳ {_qtd_aguardando_vinculo} folga(s) aguardando vínculo com RH não "
            "aparecem nesta tela (ela é centrada em quem já está identificado no "
            "RH) — veja em **Confirmar folgas** ou **Urgências**, e vincule em "
            "**Importar RE090**."
        )

    # previsao de gasto por colaborador (schema_v0.15): media do proprio
    # historico, cai pra media do canteiro, depois da obra, se nao tiver -
    # pedido do Rafael (02/09) pra dar valor em R$ nessa tabela tambem.
    gasto_resp = supabase.rpc("viajai_previsao_gasto_colaborador").execute()
    if gasto_resp.data:
        df_gasto = pd.DataFrame(gasto_resp.data)
        # so' as colunas novas (previsao_gasto/base_previsao) - "nome"/
        # "canteiro_nome"/"obra_nome" essa tela JA TEM vindo de
        # viajai_previsao_folgas; se merge trouxesse de novo, o pandas
        # criaria nome_x/nome_y e quebraria as referencias abaixo
        # (schema_v0.18, achado 03/09 revisando antes de aplicar).
        df = df.merge(
            df_gasto[["colaborador_id", "previsao_gasto", "base_previsao"]],
            on="colaborador_id", how="left",
        )
    else:
        df["previsao_gasto"] = None
        df["base_previsao"] = "sem_dado"

    # ===== Panorama geral (pedido do Rafael 09/09: "ver de forma facil e
    # macroscopicamente todos os funcionarios... total, quantos de folga,
    # quantos previsao, quantos ativos, etc") - so' consulta, nao edita
    # aqui (edicao continua so' em "Confirmar folgas", pra nao duplicar
    # aquela logica de salvar status/data em 2 lugares - decisao consciente
    # de manter 1 caminho de escrita so'). Usa dado que o app ja busca
    # nessa mesma tela (df, de viajai_previsao_folgas - cobre TODO ativo,
    # nao so' quem tem folga em aberto) + viajai_listar_folgas_previstas
    # (status de quem esta com folga aberta agora).
    st.subheader("📊 Panorama geral — todos os colaboradores ativos")

    # _folgas_abertas_panorama ja foi buscado acima (schema_v0.40, pra
    # contar quem esta aguardando vinculo com RH) - reaproveita, nao busca
    # de novo.
    _status_por_colab = {}
    if _folgas_abertas_panorama.data:
        for _f in _folgas_abertas_panorama.data:
            _status_por_colab[_f["colaborador_id"]] = _f["status"]

    _total_ativos = len(df)
    _qtd_em_andamento = sum(1 for s in _status_por_colab.values() if s == "em_andamento")
    _qtd_aguardando = sum(1 for s in _status_por_colab.values() if s in ("prevista", "confirmada"))
    _qtd_sem_historico = int((df["tem_historico"] == False).sum())  # noqa: E712

    kpi_p1, kpi_p2, kpi_p3, kpi_p4 = st.columns(4)
    kpi_p1.metric("Total de colaboradores ativos", _total_ativos)
    kpi_p2.metric("De folga agora (em andamento)", _qtd_em_andamento)
    kpi_p3.metric("Com folga prevista/confirmada", _qtd_aguardando)
    kpi_p4.metric("Sem folga registrada ainda", _qtd_sem_historico)

    def _situacao_panorama(row):
        _status = _status_por_colab.get(row["colaborador_id"])
        if _status == "em_andamento":
            return "🚌 De folga agora"
        if _status in ("prevista", "confirmada"):
            return f"📅 Previsão ({_status})"
        if not row["tem_historico"]:
            return "— sem folga registrada"
        return "✅ Ativo (última folga já encerrada)"

    df_panorama = df.copy()
    df_panorama["situação"] = df_panorama.apply(_situacao_panorama, axis=1)
    df_panorama = df_panorama.sort_values(by=["situação", "nome"])

    st.dataframe(
        df_panorama[[
            "nome", "situação", "obra_nome", "canteiro_nome",
            "dias_restantes", "nivel_urgencia",
        ]],
        column_config={
            "nome": "Nome",
            "situação": "Situação",
            "obra_nome": "Obra",
            "canteiro_nome": "Canteiro",
            "dias_restantes": "Dias restantes (estim.)",
            "nivel_urgencia": "Urgência",
        },
        hide_index=True,
        use_container_width=True,
    )
    st.caption(
        "Essa tabela é só consulta. Pra confirmar saída/retorno ou mudar "
        "status de alguém, use a página **Confirmar folgas**."
    )
    st.divider()

    # painel resumido (pedido do Rafael: "dimensionar quantos funcionarios
    # precisarao de passagem nos proximos 30 dias" + gasto previsto) - usa
    # o df ANTES do filtro de "mostrar sem historico" (precisa de
    # dias_restantes calculado, que so existe pra quem tem historico).
    _janela_30d = df[
        df["dias_restantes"].notna()
        & (df["dias_restantes"] >= 0)
        & (df["dias_restantes"] <= 30)
    ]
    _qtd_30d = len(_janela_30d)
    _com_previsao = _janela_30d["previsao_gasto"].notna().sum() if _qtd_30d else 0
    _gasto_30d = _janela_30d["previsao_gasto"].sum(skipna=True) if _qtd_30d else 0
    kpi1, kpi2 = st.columns(2)
    kpi1.metric("Precisando de passagem (próx. 30 dias)", _qtd_30d)
    if _com_previsao:
        kpi2.metric(
            "Gasto previsto pra esse período",
            f"R$ {_gasto_30d:,.2f}",
            help=f"Baseado em {_com_previsao} de {_qtd_30d} pessoa(s) com histórico de custo — o resto ainda não tem base pra estimar.",
        )
    else:
        kpi2.metric("Gasto previsto pra esse período", "sem dado ainda")
    st.divider()

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

    # "atrasado" = dias_restantes negativo (a data prevista de saida ja
    # passou e ninguem registrou nada ainda) - risco real, pedido do Rafael.
    # So' compara com o que ja vem calculado, nao precisa de RPC nova.
    df["situacao"] = df.apply(
        lambda r: "atrasado" if pd.notna(r["dias_restantes"]) and r["dias_restantes"] < 0 else r["nivel_urgencia"],
        axis=1,
    )

    # mais urgente primeiro: atrasado > critico > atencao > normal > (sem classificacao)
    # e, dentro do mesmo nivel, quem tem menos dias restantes primeiro
    df["_ordem_urgencia"] = df["situacao"].map(_ORDEM_URGENCIA).fillna(9)
    df = df.sort_values(by=["_ordem_urgencia", "dias_restantes"], na_position="last")
    df = df.drop(columns=["_ordem_urgencia"])

    # override manual de urgencia: nivel_urgencia ja vem calculado com o
    # override aplicado (COALESCE no RPC) e urgencia_manual diz se existe
    # override pra aquela pessoa - entao da pra reconstruir o valor bruto
    # do override sem precisar de outra RPC.
    _UO_AUTOMATICO = "(automático)"
    df["override_manual"] = df.apply(
        lambda r: r["nivel_urgencia"] if r.get("urgencia_manual") else _UO_AUTOMATICO,
        axis=1,
    )

    colunas_principais = [
        "nome", "situacao", "dias_restantes",
        "data_saida_prevista", "data_retorno_prevista",
        "obra_nome", "canteiro_nome", "previsao_gasto", "base_previsao", "override_manual",
    ]
    colunas_principais = [c for c in colunas_principais if c in df.columns]
    # colunas tecnicas (ids, flags internas de ordenacao/filtro) ficam de
    # fora da visualizacao, mas continuam no df (usadas ao salvar).
    colunas_ocultas = {
        "obra_id", "canteiro_id", "data_base_retorno",
        "tem_historico", "urgencia_manual", "nivel_urgencia",
    }
    outras = [c for c in df.columns if c not in colunas_principais and c not in colunas_ocultas]
    df = df[colunas_principais + outras]

    st.info(
        "✏️ Só a coluna **Forçar nível (manual)** é editável aqui — o resto "
        "é só consulta. 'Urgência'/'Situação' mudam sozinhas conforme os dias "
        "passam; pra travar manualmente pra 1 pessoa (ex.: sabe que ela vai "
        "atrasar por outro motivo), escolha um nível em 'Forçar nível (manual)' "
        "e clique Salvar embaixo — '(automático)' devolve o controle pro cálculo."
    )
    editado = st.data_editor(
        df,
        column_config={
            "override_manual": st.column_config.SelectboxColumn(
                "✏️ Forçar nível (manual)",
                options=[_UO_AUTOMATICO, "critico", "atencao", "normal"],
                required=True,
                help="'(automático)' deixa o cálculo decidir sozinho. Escolher um nível trava esse nível pra essa pessoa até você voltar pra '(automático)'.",
            ),
            "previsao_gasto": st.column_config.NumberColumn(
                "🔒 Previsão de gasto",
                format="R$ %.2f",
                help="Média do custo histórico (da própria pessoa; sem isso, do canteiro; sem isso, da obra) — ver coluna 'Base'.",
            ),
            "base_previsao": st.column_config.TextColumn(
                "🔒 Base", help="De onde veio a previsão: colaborador, canteiro, obra ou sem_dado (nunca registrado nada ainda)."
            ),
        },
        disabled=[c for c in df.columns if c != "override_manual"],
        column_order=colunas_principais,
        hide_index=True,
        use_container_width=True,
        key="editor_previsao", placeholder="",
    )
    _botao_exportar_excel(df.drop(columns=["override_manual"]), "viajai_previsao_folgas.xlsx")

    if st.button("Salvar ajustes de urgência"):
        mudou = editado[editado["override_manual"] != df["override_manual"]]
        if mudou.empty:
            st.info("Nenhum ajuste mudou — nada pra salvar.")
        else:
            erros = 0
            for _, linha in mudou.iterrows():
                try:
                    if linha["override_manual"] == _UO_AUTOMATICO:
                        supabase.rpc("viajai_remover_urgencia_override", {
                            "p_colaborador_id": linha["colaborador_id"],
                        }).execute()
                    else:
                        supabase.rpc("viajai_definir_urgencia_override", {
                            "p_colaborador_id": linha["colaborador_id"],
                            "p_nivel": linha["override_manual"],
                        }).execute()
                except Exception as e:
                    erros += 1
                    st.error(f"Erro ao salvar ajuste de urgência de {linha['nome']}: {e}")
            sucesso = len(mudou) - erros
            # NAO usa _flash()/st.rerun() aqui de proposito (achado 08/09,
            # v18.5): mesmo com o mecanismo _flash comprovadamente funcionando
            # em Confirmar folgas/Reprocessar pendencias (codigo identico),
            # SO' nesse botao especifico a mensagem nunca aparecia - gravava
            # certo no banco (confirmado navegando fora e voltando, varias
            # vezes) mas nem sucesso nem erro renderizava, mesmo depois do fix
            # de erro-engolido da v18.4. Causa exata nao identificada (nao e'
            # excecao silenciosa - ja descartado; nao e' problema de indice/
            # comparacao - a gravacao prova que "mudou" bate certo; testado
            # com espera de 5s pra descartar race de rerun do proprio
            # data_editor, mesmo assim falhou) - fica registrado como mistério
            # nao resolvido do Streamlit especifico dessa combinacao de
            # data_editor+SelectboxColumn+rerun nessa tela. Solucao pragmatica:
            # mensagem direta (sem fila, sem rerun) - comprovadamente funciona
            # aqui (mesmo padrao do "Nenhum ajuste mudou" logo acima, que
            # sempre apareceu certo). Troca: a tabela/KPIs so' refletem o
            # ajuste novo na proxima interacao natural (trocar de aba e
            # voltar, ou F5) em vez de na hora - mas o feedback de "salvou"
            # aparece sempre, o que é mais importante pro usuario do que o
            # reordenamento automatico da tabela.
            if erros:
                st.warning(
                    f"{sucesso} ajuste(s) salvo(s), {erros} com erro (ver acima). "
                    "Troque de aba e volte (ou F5) pra ver a tabela atualizada."
                )
            elif sucesso:
                st.success(
                    f"{sucesso} ajuste(s) de urgência salvo(s). "
                    "Troque de aba e volte (ou F5) pra ver a tabela reordenada com o novo nível."
                )



def pagina_custo_passagens(supabase):
    st.subheader("Custo & Passagens")
    st.caption(
        "Registra o preço REAL pago (passagem/ônibus/carro) e gastos extras "
        "por folga, ou um lançamento rápido solto quando não dá pra apontar "
        "folga específica na hora. Sem busca de preço ao vivo (decisão "
        "02/09 — ver 00-handoff): a inteligência aqui é o histórico que a "
        "própria Amanda for alimentando, cresce com o uso."
    )
    cidades_usadas = _obter_cidades_usadas(supabase)

    with st.expander("🔎 Consultar histórico da rota (antes de comprar)"):
        st.caption(
            "Usa o que já foi registrado no Viaj.AI — escreva origem/destino "
            "igual a como costuma registrar (mesmo texto), senão não casa."
        )
        c1, c2 = st.columns(2)
        origem_c = c1.text_input("Origem", key="consulta_origem")
        destino_c = c2.text_input("Destino", key="consulta_destino")
        if st.button("Consultar histórico", key="btn_consulta_hist"):
            if origem_c and destino_c:
                sug = supabase.rpc("viajai_sugestao_fornecedor_rota", {
                    "p_origem": origem_c, "p_destino": destino_c,
                }).execute()
                if sug.data:
                    st.write("**Fornecedor mais usado nessa rota:**")
                    st.dataframe(sug.data, hide_index=True, use_container_width=True, placeholder="")
                else:
                    st.caption("Sem fornecedor registrado ainda pra essa rota.")

                comp_modal = supabase.rpc("viajai_comparar_modais_rota", {
                    "p_origem": origem_c, "p_destino": destino_c,
                }).execute()
                if comp_modal.data:
                    st.write("**Comparativo por modal (preço médio e duração média):**")
                    st.dataframe(comp_modal.data, hide_index=True, use_container_width=True, placeholder="")
                else:
                    st.caption("Sem dado suficiente ainda pra comparar modal nessa rota.")
            else:
                st.info("Preenche origem e destino.")

        st.divider()
        st.caption(
            "Atalho pra abrir busca já preenchida no Skyscanner (link oficial "
            "deles, sem API key) — digita nome da cidade (ex.: Fortaleza) ou "
            "já o código do aeroporto (ex.: FOR), os dois funcionam:"
        )
        c3, c4, c5 = st.columns(3)
        origem_txt = c3.text_input("Origem", key="sky_origem")
        destino_txt = c4.text_input("Destino", key="sky_destino")
        data_ida_sky = c5.date_input("Data de ida", value=date.today(), key="sky_data")
        origem_iata = _resolver_iata(origem_txt)
        destino_iata = _resolver_iata(destino_txt)
        if origem_txt and not origem_iata:
            st.caption(f"Não reconheci '{origem_txt}' — digita o código do aeroporto direto (ex.: FOR).")
        if destino_txt and not destino_iata:
            st.caption(f"Não reconheci '{destino_txt}' — digita o código do aeroporto direto (ex.: FOR).")
        if origem_iata and destino_iata:
            url_sky = (
                "https://www.skyscanner.net/g/referrals/v1/flights/day-view/"
                f"?origin={origem_iata}&destination={destino_iata}"
                f"&outboundDate={data_ida_sky.isoformat()}&market=BR&currency=BRL&locale=pt-BR"
            )
            st.link_button(f"🔗 Ver no Skyscanner ({origem_iata} → {destino_iata})", url_sky)
        else:
            st.caption("Preenche origem e destino (cidade ou código) pra habilitar o link.")

    with st.expander("🚗 Estimar por carro (Google Maps) *"):
        st.caption(
            "* Depende de uma configuração de faturamento no Google Cloud — "
            "pode ficar temporariamente indisponível. Use Skyscanner/ClickBus "
            "normalmente enquanto isso."
        )
        if not GOOGLE_MAPS_API_KEY:
            st.caption(
                "Chave do Google Maps ainda não configurada (Secrets do Streamlit Cloud: "
                "GOOGLE_MAPS_API_KEY) — essa parte não funciona sem ela."
            )
        else:
            st.caption(
                "Distância e tempo reais (Google Directions), sem depender de histórico "
                "próprio — só pra carro. Preço NÃO vem da internet (mesma regra do "
                "resto do app): você informa consumo e preço do combustível, o app só "
                "faz a conta."
            )
            c1, c2 = st.columns(2)
            origem_carro = c1.text_input("Origem", key="carro_origem")
            destino_carro = c2.text_input("Destino", key="carro_destino")
            if st.button("Calcular distância", key="btn_calcular_carro"):
                if origem_carro and destino_carro:
                    st.session_state.dist_carro_resultado = _consultar_distancia_carro(origem_carro, destino_carro)
                else:
                    st.info("Preenche origem e destino.")

            _dist = st.session_state.get("dist_carro_resultado")
            if _dist:
                if _dist.get("erro"):
                    st.error(_dist["erro"])
                else:
                    st.write(
                        f"**{_dist['distancia_texto']}** — cerca de **{_dist['duracao_texto']}** de carro "
                        f"({_dist['origem']} → {_dist['destino']})"
                    )
                    c3, c4 = st.columns(2)
                    consumo = c3.number_input(
                        "Consumo do veículo (km/l)", min_value=0.1, value=10.0, step=0.5, key="carro_consumo",
                    )
                    preco_combustivel = c4.number_input(
                        "Preço do combustível (R$/l)", min_value=0.0, value=6.00, step=0.10, key="carro_preco",
                    )
                    if consumo:
                        custo_estimado = (_dist["distancia_km"] / consumo) * preco_combustivel
                        st.metric("Custo estimado (combustível, só ida)", f"R$ {custo_estimado:.2f}")
                        st.caption("Não inclui pedágio, desgaste do veículo ou diária de motorista — só combustível.")

    aba_folga, aba_rapido = st.tabs(["Por folga", "Lançamento rápido"])

    with aba_folga:
        st.caption(
            "Essa aba é pra quem JÁ tem folga confirmada/realizada/vendida/"
            "cancelada (feito em 'Confirmar folgas') — é só pra anexar "
            "trechos e gastos extras a essa folga, não dá pra editar a folga "
            "em si aqui. Folga ainda 'prevista' não aparece na lista abaixo."
        )
        folgas_resp = supabase.rpc("viajai_listar_folgas_desvio", {"p_limite": 500}).execute()
        if not folgas_resp.data:
            st.caption(
                "Nenhuma folga confirmada/realizada ainda — confirme pelo "
                "menos 1 na tela 'Confirmar folgas' antes de registrar custo."
            )
        else:
            df_folgas = pd.DataFrame(folgas_resp.data)
            # NOVO 10/09 (pedido do Rafael: lista cresce e "nome - obra -
            # status" sozinho não basta pra achar a folga certa rolando a
            # lista) - rótulo ganha a data de saída prevista, e a lista
            # ordena pela mesma data (mais recente primeiro) em vez da
            # ordem crua que a RPC devolveu.
            df_folgas = df_folgas.sort_values("data_saida_prevista", ascending=False, na_position="last")
            # NOVO schema_v0.40: folga provisoria (aguardando_vinculo_rh)
            # ganha o selo ⏳ no rotulo tambem, pra Amanda saber que aquele
            # nome ainda nao foi vinculado ao RH (mas ja pode lancar custo
            # normalmente - o vinculo posterior nao muda o folga_id).
            df_folgas["rotulo"] = df_folgas.apply(
                lambda r: (
                    f"#{r['folga_id']} — "
                    f"{'⏳ ' if r.get('aguardando_vinculo_rh') else ''}{r['nome']} — "
                    f"{r.get('canteiro_nome') or '—'} — "
                    f"{r['status']} — saída {r['data_saida_prevista'] or '—'}"
                ),
                axis=1,
            )
            escolha = st.selectbox("Folga", df_folgas["rotulo"], key="folga_custo_select")
            folga_id_sel = int(df_folgas.loc[df_folgas["rotulo"] == escolha, "folga_id"].iloc[0])

            viagens_resp = supabase.rpc("viajai_listar_viagens_folga", {"p_folga_id": folga_id_sel}).execute()
            st.write("**Trechos já registrados:**")
            if viagens_resp.data:
                df_viagens = pd.DataFrame(viagens_resp.data)
                st.caption(
                    "Agrupado por viagem — 'ida' e 'volta' são 2 viagens "
                    "separadas; cada uma pode ter vários trechos (paradas) "
                    "na mesma viagem, um embaixo do outro na ordem que foram "
                    "adicionados."
                )
                for (_sent, _vid), _grupo in df_viagens.groupby(["sentido", "viagem_id"], sort=False):
                    _n_trechos = int(_grupo["trecho_id"].notna().sum())
                    st.write(f"Viagem de **{_sent}** — {_n_trechos} trecho(s)")
                    st.dataframe(
                        _grupo.drop(columns=["sentido", "viagem_id"]),
                        hide_index=True, use_container_width=True, placeholder="",
                    )
            else:
                st.caption("Nenhum trecho registrado ainda pra essa folga.")

            gastos_resp = supabase.rpc("viajai_listar_gastos_folga", {"p_folga_id": folga_id_sel}).execute()
            st.write("**Gastos extras já registrados:**")
            if gastos_resp.data:
                st.dataframe(pd.DataFrame(gastos_resp.data), hide_index=True, use_container_width=True, placeholder="")
            else:
                st.caption("Nenhum gasto extra registrado ainda.")

            st.write("**Adicionar trecho (passagem/perna da viagem)**")
            sentido = st.selectbox("Sentido", ["ida", "volta"], key="trecho_sentido_select")
            _trechos_do_sentido = [
                v for v in (viagens_resp.data or [])
                if v["sentido"] == sentido and v.get("trecho_id") is not None
            ]
            if _trechos_do_sentido:
                st.info(
                    f"➡️ Já existe uma viagem de '{sentido}' com "
                    f"{len(_trechos_do_sentido)} trecho(s) (veja acima). O que "
                    f"você preencher abaixo vira o trecho {len(_trechos_do_sentido) + 1} "
                    f"dessa MESMA viagem — não cria uma viagem nova. Pra "
                    f"registrar como outra viagem, muda o 'Sentido' acima."
                )
            else:
                st.caption(f"➡️ Ainda não existe viagem de '{sentido}' pra essa folga — isso vai criar a primeira.")
            # Origem/Destino ficam FORA do form de propósito (selectbox
            # dentro de form so' reage no submit - ver _input_cidade_com_sugestao).
            c3, c4 = st.columns(2)
            origem_t = _input_cidade_com_sugestao(c3, "Origem", "trecho_origem", cidades_usadas)
            destino_t = _input_cidade_com_sugestao(c4, "Destino", "trecho_destino", cidades_usadas)
            with st.form("form_add_trecho"):
                st.caption("Só o essencial aqui — o resto é opcional, fica em 'Mais detalhes'.")
                c1, c2 = st.columns(2)
                modal = c1.selectbox("Modal", ["aviao", "onibus", "carro", "taxi", "outro"])
                data_t = c2.date_input("Data da viagem", value=date.today(), key="trecho_data")
                preco_t = st.number_input("Preço (R$)", min_value=0.0, step=0.01, format="%.2f")

                with st.expander("Mais detalhes (opcional)"):
                    c7, c8 = st.columns(2)
                    fornecedor_t = c7.text_input("Fornecedor/companhia", key="trecho_fornecedor")
                    duracao_t = c8.number_input("Duração (horas)", min_value=0.0, step=0.5, format="%.1f")
                    c9, c10 = st.columns(2)
                    km_t = c9.number_input("Km (útil pra carro)", min_value=0.0, step=1.0)
                    data_compra_t = c10.date_input(
                        "Data da compra (se diferente de hoje)", value=None, key="trecho_data_compra",
                    )
                    obs_t = st.text_input("Observação", key="trecho_obs")

                enviar_trecho = st.form_submit_button("Adicionar trecho")

            if enviar_trecho:
                if not origem_t or not destino_t:
                    st.error("Preenche origem e destino.")
                else:
                    viagem_id = None
                    maior_ordem = 0
                    for v in (viagens_resp.data or []):
                        if v["sentido"] == sentido:
                            viagem_id = v["viagem_id"]
                            if v.get("ordem") and v["ordem"] > maior_ordem:
                                maior_ordem = v["ordem"]
                    try:
                        if viagem_id is None:
                            nova_viagem = supabase.rpc("viajai_criar_viagem", {
                                "p_folga_id": folga_id_sel, "p_sentido": sentido,
                            }).execute()
                            viagem_id = nova_viagem.data
                        supabase.rpc("viajai_adicionar_trecho", {
                            "p_viagem_id": viagem_id,
                            "p_ordem": maior_ordem + 1,
                            "p_origem": origem_t,
                            "p_destino": destino_t,
                            "p_modal": modal,
                            "p_km": km_t or None,
                            "p_data": data_t.isoformat() if data_t else None,
                            "p_preco": preco_t or None,
                            "p_fornecedor": fornecedor_t or None,
                            "p_observacao": obs_t or None,
                            "p_duracao_horas": duracao_t or None,
                            "p_data_compra": data_compra_t.isoformat() if data_compra_t else None,
                        }).execute()
                        _flash("success", "Trecho adicionado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao adicionar trecho: {e}")

            # Reembolso (schema_v0.30) - pedido do Rafael 08/09: passagem
            # comprada mas depois reembolsada pela companhia, precisava de
            # um jeito de registrar isso sem virar "gasto com passagem" de
            # verdade (o dinheiro voltou, nao foi gasto liquido).
            _trechos_p_reembolso = [
                v for v in (viagens_resp.data or []) if v.get("trecho_id") is not None
            ]
            if _trechos_p_reembolso:
                with st.expander("💰 Marcar/desfazer reembolso de um trecho"):
                    st.caption(
                        "Passagem comprada, mas a companhia devolveu o valor "
                        "(total ou parcial)? Marca aqui — o valor reembolsado "
                        "sai do cálculo de gasto real (Previsão de gasto, "
                        "Comparativo de custo), mas o preço original da "
                        "passagem continua registrado normalmente."
                    )
                    _df_reemb = pd.DataFrame(_trechos_p_reembolso)
                    _df_reemb["_rotulo"] = _df_reemb.apply(
                        lambda r: (
                            f"#{int(r['trecho_id'])} — {r['sentido']} — {r['origem']} -> {r['destino']} — "
                            f"R$ {r['preco']:.2f}"
                            + (f" (já reembolsado: R$ {r['valor_reembolsado']:.2f})" if r.get("reembolsado") else "")
                        ),
                        axis=1,
                    )
                    _rotulo_reemb = st.selectbox("Qual trecho?", _df_reemb["_rotulo"], key="reemb_select")
                    _linha_reemb = _df_reemb.loc[_df_reemb["_rotulo"] == _rotulo_reemb].iloc[0]
                    if _linha_reemb.get("reembolsado"):
                        st.write(
                            f"Reembolsado em {_linha_reemb.get('data_reembolso') or '—'}: "
                            f"R$ {_linha_reemb['valor_reembolsado']:.2f}"
                            + (f" — {_linha_reemb['observacao_reembolso']}" if _linha_reemb.get("observacao_reembolso") else "")
                        )
                        if st.button("Desfazer reembolso", key="btn_desfazer_reembolso"):
                            try:
                                supabase.rpc("viajai_marcar_trecho_reembolsado", {
                                    "p_trecho_id": int(_linha_reemb["trecho_id"]),
                                    "p_reembolsado": False,
                                }).execute()
                                _flash("success", "Reembolso desfeito.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao desfazer reembolso: {e}")
                    else:
                        with st.form("form_marcar_reembolso"):
                            valor_reemb = st.number_input(
                                "Valor reembolsado (R$)", min_value=0.0, step=0.01, format="%.2f",
                                value=float(_linha_reemb["preco"] or 0),
                                help="Já vem preenchido com o preço cheio — ajusta se foi reembolso parcial.",
                            )
                            data_reemb = st.date_input("Data do reembolso", value=date.today(), key="reemb_data")
                            obs_reemb = st.text_input("Observação (opcional)", key="reemb_obs")
                            enviar_reemb = st.form_submit_button("Marcar como reembolsado")
                        if enviar_reemb:
                            try:
                                supabase.rpc("viajai_marcar_trecho_reembolsado", {
                                    "p_trecho_id": int(_linha_reemb["trecho_id"]),
                                    "p_reembolsado": True,
                                    "p_valor_reembolsado": valor_reemb,
                                    "p_data_reembolso": data_reemb.isoformat() if data_reemb else None,
                                    "p_observacao": obs_reemb or None,
                                }).execute()
                                _flash("success", "Marcado como reembolsado.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao marcar reembolso: {e}")

            with st.form("form_add_gasto"):
                st.write("Adicionar gasto extra (hospedagem, alimentação, transporte local...)")
                c1, c2 = st.columns(2)
                tipo_g = c1.selectbox("Tipo", ["hospedagem", "transporte_local", "alimentacao", "outro"])
                valor_g = c2.number_input("Valor (R$)", min_value=0.0, step=0.01, format="%.2f", key="gasto_valor")
                data_g = st.date_input("Data", value=date.today(), key="gasto_data")
                obs_g = st.text_input("Observação (opcional)", key="gasto_obs")
                enviar_gasto = st.form_submit_button("Adicionar gasto")

            if enviar_gasto:
                if not valor_g:
                    st.error("Preenche o valor.")
                else:
                    try:
                        supabase.rpc("viajai_registrar_gasto", {
                            "p_folga_id": folga_id_sel,
                            "p_tipo": tipo_g,
                            "p_valor": valor_g,
                            "p_data": data_g.isoformat() if data_g else None,
                            "p_observacao": obs_g or None,
                        }).execute()
                        _flash("success", "Gasto registrado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao registrar gasto: {e}")

    with aba_rapido:
        st.caption(
            "Pra quando não dá pra apontar folga específica na hora "
            "(ex.: \"comprei 10 passagens do Ceará pra SP\") — serve pra "
            "somar gasto por rota/período e ajudar a prever. Se a compra "
            "FOR de uma folga específica, dá pra vincular abaixo (opcional) "
            "— assim, se essa folga depois for vendida/cancelada, ela "
            "aparece em Urgências > \"Passagem pra revisar\"."
        )
        _colabs_resp_lr = supabase.rpc("viajai_colaboradores_ativos").execute()
        _colabs_opcoes_lr = ["— Lote / sem definir —"] + [c["nome"] for c in (_colabs_resp_lr.data or [])]
        _colabs_por_nome_lr = {c["nome"]: c["colaborador_id"] for c in (_colabs_resp_lr.data or [])}
        # v20.0 (pedido do Rafael 08/09, "via chat e via pagina de passagem
        # pra revisar tb"): lista de folgas em aberto (mesma RPC widened na
        # v19.0) pra oferecer vinculo opcional aqui - o backend confere se
        # o colaborador escolhido acima bate com o dono da folga escolhida
        # aqui, entao nao precisa filtrar client-side pra ficar seguro.
        _folgas_abertas_lr_resp = supabase.rpc("viajai_listar_folgas_previstas", {"p_limite": 300}).execute()
        _opcoes_folga_lr = ["— Nenhuma —"] + [
            f"#{f['folga_id']} — {f['nome']} — {f.get('canteiro_nome') or '—'} — {f['status']}"
            for f in (_folgas_abertas_lr_resp.data or [])
        ]
        _folga_id_por_rotulo_lr = {
            f"#{f['folga_id']} — {f['nome']} — {f.get('canteiro_nome') or '—'} — {f['status']}": f["folga_id"]
            for f in (_folgas_abertas_lr_resp.data or [])
        }
        # Origem/Destino ficam FORA do form de propósito (selectbox
        # dentro de form so' reage no submit - ver _input_cidade_com_sugestao).
        c1, c2 = st.columns(2)
        origem_lr = _input_cidade_com_sugestao(c1, "Origem", "lr_origem", cidades_usadas)
        destino_lr = _input_cidade_com_sugestao(c2, "Destino", "lr_destino", cidades_usadas)
        with st.form("form_lancamento_rapido"):
            c3, c4, c5 = st.columns(3)
            modal_lr = c3.selectbox("Modal", ["aviao", "onibus", "carro", "taxi", "outro"], key="lr_modal")
            qtd_lr = c4.number_input("Quantidade de passagens", min_value=1, value=1, step=1, key="lr_qtd")
            valor_lr = c5.number_input("Valor total (R$)", min_value=0.0, step=0.01, format="%.2f", key="lr_valor")
            data_lr = st.date_input("Data da compra", value=date.today(), key="lr_data")
            obs_lr = st.text_input("Observação (opcional)", key="lr_obs")
            colab_lr = st.selectbox("Colaborador (opcional)", _colabs_opcoes_lr, key="lr_colab")
            nome_prov_lr = st.text_input(
                "Nome (se a pessoa ainda não aparece no RH)",
                key="lr_nome_provisorio",
                help=(
                    "Só pra organizar/identificar depois — NÃO cria colaborador "
                    "nenhum, é rótulo solto. Ignorado se você já escolheu um "
                    "colaborador real acima."
                ),
            )
            folga_lr = st.selectbox(
                "Folga vinculada (opcional)", _opcoes_folga_lr, key="lr_folga",
                help=(
                    "Só se essa passagem for de uma folga específica — precisa "
                    "ter escolhido o colaborador real acima (não dá com nome "
                    "provisório) e ser a folga daquela mesma pessoa."
                ),
            )
            enviar_lr = st.form_submit_button("Registrar")

        if enviar_lr:
            if not origem_lr or not destino_lr or not valor_lr:
                st.error("Preenche origem, destino e valor.")
            else:
                try:
                    supabase.rpc("viajai_registrar_lancamento_rapido", {
                        "p_origem": origem_lr,
                        "p_destino": destino_lr,
                        "p_valor_total": valor_lr,
                        "p_quantidade": int(qtd_lr),
                        "p_modal": modal_lr,
                        "p_data": data_lr.isoformat() if data_lr else None,
                        "p_observacao": obs_lr or None,
                        "p_colaborador_id": _colabs_por_nome_lr.get(colab_lr),
                        "p_colaborador_nome_provisorio": nome_prov_lr or None,
                        "p_folga_id": _folga_id_por_rotulo_lr.get(folga_lr),
                    }).execute()
                    _flash("success", "Lançamento registrado.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao registrar lançamento: {e}")

        st.divider()
        st.write("**Lançamentos recentes**")
        lancs = supabase.rpc("viajai_listar_lancamentos_rapidos", {"p_limite": 200}).execute()
        if lancs.data:
            df_lanc = pd.DataFrame(lancs.data)
            st.dataframe(df_lanc, hide_index=True, use_container_width=True, placeholder="")
            _botao_exportar_excel(df_lanc, "viajai_lancamentos_rapidos.xlsx")

            # Atribuir colaborador retroativamente (RH subiu/ativou a pessoa
            # depois do lançamento "solto") - pedido do Rafael 04/09, RPC
            # nova em schema_v0.27 (viajai_atribuir_colaborador_lancamento_rapido).
            _sem_colab = df_lanc[df_lanc["colaborador_nome"].isna()] if "colaborador_nome" in df_lanc.columns else df_lanc.iloc[0:0]
            if not _sem_colab.empty:
                with st.expander("👤 Atribuir colaborador a um lançamento (RH subiu depois)"):
                    st.caption(
                        "Pra lançamento registrado sem colaborador porque a pessoa "
                        "ainda não estava ativa no RH na hora — anexa agora que já está."
                    )
                    _sem_colab = _sem_colab.copy()
                    _sem_colab["_rotulo"] = _sem_colab.apply(
                        lambda r: (
                            f"#{r['id']} — {r['origem']} -> {r['destino']} — R$ {r['valor_total']:.2f}"
                            + (f" — (provisório: {r['colaborador_nome_provisorio']})" if r.get("colaborador_nome_provisorio") else " — sem nome")
                            + f" — {r.get('observacao') or ''}"
                        ),
                        axis=1,
                    )
                    rotulo_atribuir = st.selectbox("Qual lançamento?", _sem_colab["_rotulo"], key="lr_atribuir_select")
                    _linha_atribuir = _sem_colab.loc[_sem_colab["_rotulo"] == rotulo_atribuir].iloc[0]
                    id_atribuir = int(_linha_atribuir["id"])
                    # sugestao automatica: casa o nome provisorio (se tiver) contra
                    # os nomes ativos no RH, sem acento/maiuscula - pedido do Rafael
                    # 04/09 (nao travar E nao perder controle com varios "sem nome")
                    _opcoes_atribuir = ["— selecione —"] + list(_colabs_por_nome_lr.keys())
                    _nome_prov_atual = (_linha_atribuir.get("colaborador_nome_provisorio") or "").strip()
                    _indice_sugerido = 0
                    if _nome_prov_atual:
                        _alvo = unicodedata.normalize("NFKD", _nome_prov_atual.upper()).encode("ascii", "ignore").decode()
                        for _i, _opt in enumerate(_opcoes_atribuir):
                            if _opt == "— selecione —":
                                continue
                            _opt_norm = unicodedata.normalize("NFKD", _opt.upper()).encode("ascii", "ignore").decode()
                            if _opt_norm == _alvo:
                                _indice_sugerido = _i
                                break
                    if _indice_sugerido:
                        st.caption(f"💡 Sugestão pelo nome provisório: **{_opcoes_atribuir[_indice_sugerido]}**")
                    colab_atribuir = st.selectbox(
                        "Colaborador", _opcoes_atribuir, index=_indice_sugerido, key="lr_atribuir_colab"
                    )
                    if st.button("Atribuir", key="lr_atribuir_btn"):
                        if colab_atribuir == "— selecione —":
                            st.info("Escolhe um colaborador.")
                        else:
                            try:
                                supabase.rpc("viajai_atribuir_colaborador_lancamento_rapido", {
                                    "p_id": id_atribuir,
                                    "p_colaborador_id": _colabs_por_nome_lr[colab_atribuir],
                                }).execute()
                                _flash("success", "Colaborador atribuído.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Não consegui atribuir (rodou o schema_v0.27 no Supabase?): {e}")

            # Apagar (teste ou registro errado) - pedido do Rafael 03/09,
            # RPC nova em schema_v0.16 (viajai_apagar_lancamento_rapido).
            with st.expander("Apagar um lançamento (teste ou erro de digitação)"):
                df_lanc["_rotulo"] = df_lanc.apply(
                    lambda r: (
                        f"#{r['id']} — {r['origem']} -> {r['destino']} — R$ {r['valor_total']:.2f}"
                        + (f" — {r['colaborador_nome']}" if r.get("colaborador_nome") else "")
                        + (f" — (provisório: {r['colaborador_nome_provisorio']})" if r.get("colaborador_nome_provisorio") else "")
                        + f" — {r.get('observacao') or ''}"
                    ),
                    axis=1,
                )
                rotulo_apagar = st.selectbox("Qual?", df_lanc["_rotulo"], key="lr_apagar_select")
                id_apagar = int(df_lanc.loc[df_lanc["_rotulo"] == rotulo_apagar, "id"].iloc[0])
                if st.button("🗑️ Apagar este lançamento", key="lr_apagar_btn"):
                    try:
                        supabase.rpc("viajai_apagar_lancamento_rapido", {"p_id": id_apagar}).execute()
                        _flash("success", "Apagado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Não consegui apagar (rodou o schema_v0.16 no Supabase?): {e}")
        else:
            st.caption("Nenhum lançamento rápido ainda.")

        st.divider()
        st.write("**Resumo de custo por rota**")
        resumo = supabase.rpc("viajai_resumo_custo_por_rota", {"p_limite": 100}).execute()
        if resumo.data:
            df_resumo = pd.DataFrame(resumo.data)
            st.dataframe(df_resumo, hide_index=True, use_container_width=True, placeholder="")
            _botao_exportar_excel(df_resumo, "viajai_resumo_custo_rota.xlsx")
        else:
            st.caption("Nenhum custo registrado ainda (nem lançamento rápido nem trecho com preço).")

    st.divider()
    st.write("**Gasto por período**")
    st.caption("Soma tudo que tem data (trecho + gasto extra + lançamento rápido), mês a mês.")
    meses_janela = st.slider("Últimos quantos meses?", min_value=1, max_value=24, value=12, key="periodo_meses")
    periodo_resp = supabase.rpc("viajai_gasto_por_periodo", {"p_meses": meses_janela}).execute()
    if periodo_resp.data:
        df_periodo = pd.DataFrame(periodo_resp.data)
        st.bar_chart(df_periodo.set_index("periodo")["valor_total"])
        st.dataframe(df_periodo, hide_index=True, use_container_width=True, placeholder="")
        _botao_exportar_excel(df_periodo, "viajai_gasto_por_periodo.xlsx")
    else:
        st.caption("Nenhum custo com data registrada ainda nesse período.")



# ---------- Assistente (chat) — mesmo padrao validado do TIA.go/app_tiago.py ----------
# (lido direto do arquivo real antes de desenhar isso, nao suposicao):
# loop de tool-use da Anthropic, 2 fases (grava pergunta + rerun, so' entao
# chama a API) pra evitar bug de ordem de mensagem, dolar escapado no
# markdown. DIFERENCA proposital do TIA.go: aqui o historico e' PERSISTIDO
# por usuario (schema_v0.11), o TIA.go so' guarda em session_state (some ao
# dar F5) - pedido explicito do Rafael (02/09): "gostaria que a memoria do
# chat fosse preservada pra ajudar nas decisoes".
#
# ESCOPO v1 (decisao 02/09, ver 00-handoff): SO CONSULTA. Nenhuma ferramenta
# de escrita ainda - registrar lancamento/trecho por chat fica pra depois,
# so' depois de validar que a parte de leitura funciona bem de verdade.

TOOLS_VIAJAI = [
    {
        "name": "consultar_previsao_folgas",
        "description": "Previsao de folga por colaborador ativo: urgencia, dias restantes, datas previstas, previsao de gasto. Use para 'quem esta de folga', 'quem precisa viajar', 'urgencia'.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "consultar_pendencias_import",
        "description": "LEGADO (schema_v0.40): pendencia de import criada ANTES do schema_v0.40 - hoje o import RE090 nao gera mais pendencia nova (linha sem match 1:1 vira folga 'aguardando vinculo com RH' - use consultar_folgas_aguardando_vinculo pra isso). So' use esta ferramenta se o usuario perguntar especificamente por 'pendencia antiga/legado'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "apenas_nao_resolvidas": {"type": "boolean", "description": "So' as ainda nao marcadas como resolvidas (padrao true)"}
            },
        },
    },
    {
        "name": "consultar_folgas_aguardando_vinculo",
        "description": "Folgas criadas (import RE090 ou manual) que ainda nao acharam match 1:1 no RH - colaborador_id em aberto, nome/obra provisorios (schema_v0.40). Nao trava nada, mas precisa vincular em algum momento (manual em 'Importar RE090' ou automatico). Use para 'quem esta sem vinculo com o RH', 'folga provisoria', 'nome que nao bateu no import'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "dias_minimo": {"type": "integer", "description": "So' quem esta ha pelo menos X dias sem vinculo (padrao 0 = todas, sem filtro de tempo)"}
            },
        },
    },
    {
        "name": "consultar_historico_folga",
        "description": "Historico de mudancas de status de folga (quem mudou, quando, de qual valor pra qual).",
        "input_schema": {
            "type": "object",
            "properties": {"limite": {"type": "integer", "description": "Quantos registros (padrao 200)"}},
        },
    },
    {
        "name": "consultar_desvio_planejamento",
        "description": "Folgas ja confirmadas/realizadas comparando data prevista x real (quantos dias atrasou/antecipou na saida e no retorno).",
        "input_schema": {
            "type": "object",
            "properties": {"limite": {"type": "integer", "description": "Quantos registros (padrao 200)"}},
        },
    },
    {
        "name": "consultar_previsao_gasto_colaborador",
        "description": "Previsao de gasto por colaborador: media do historico REAL (nunca inventado) da propria pessoa; se nao tiver, cai pro canteiro dela; se nao tiver, pra obra; se nem a obra tiver nada, cai pra media de TODA a empresa (todo lancamento real ja registrado, base_previsao= 'empresa') como ultimo recurso antes de 'sem_dado'. Devolve tambem 'base_previsao' ""(colaborador/canteiro/obra/empresa/sem_dado) - sempre informe essa base na resposta, e deixe claro pro usuario quando for 'empresa' que e' uma media geral, nao especifica dessa pessoa.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "consultar_comparativo_custo_folga",
        "description": "Folgas com custo real ja registrado (passagem + gasto extra), cruzado com o desvio de planejamento em dias.",
        "input_schema": {
            "type": "object",
            "properties": {"limite": {"type": "integer", "description": "Quantos registros (padrao 200)"}},
        },
    },
    {
        "name": "consultar_sugestao_fornecedor_rota",
        "description": "Fornecedor/companhia mais usado historicamente numa rota especifica (origem/destino precisam bater com o texto ja registrado).",
        "input_schema": {
            "type": "object",
            "properties": {
                "origem": {"type": "string"},
                "destino": {"type": "string"},
            },
            "required": ["origem", "destino"],
        },
    },
    {
        "name": "consultar_comparar_modais_rota",
        "description": "Compara preco medio e duracao media entre modais (aviao/onibus/carro/etc) numa rota especifica, baseado no que ja foi registrado.",
        "input_schema": {
            "type": "object",
            "properties": {
                "origem": {"type": "string"},
                "destino": {"type": "string"},
            },
            "required": ["origem", "destino"],
        },
    },
    {
        "name": "consultar_resumo_custo_por_rota",
        "description": "Soma de gasto e quantidade de passagens por rota (origem/destino), juntando lancamento rapido e trecho registrado.",
        "input_schema": {
            "type": "object",
            "properties": {"limite": {"type": "integer", "description": "Quantas rotas (padrao 100)"}},
        },
    },
    {
        "name": "consultar_gasto_por_periodo",
        "description": "Soma de todo gasto registrado (trecho + gasto extra + lancamento rapido), agrupado por mes.",
        "input_schema": {
            "type": "object",
            "properties": {"meses": {"type": "integer", "description": "Quantos meses pra tras (padrao 12)"}},
        },
    },
    {
        "name": "consultar_lancamentos_rapidos",
        "description": "Lancamentos rapidos de compra registrados sem apontar folga especifica (ex.: 'comprei 10 passagens do Ceara pra SP').",
        "input_schema": {
            "type": "object",
            "properties": {"limite": {"type": "integer", "description": "Quantos registros (padrao 200)"}},
        },
    },
    {
        "name": "consultar_historico_imports",
        "description": "Historico de uploads da planilha RE090 (1 linha por upload): quando, quantas folgas criou, quantas pendencia, se foi revertido. Use para 'quantos imports fizemos', 'qual foi o ultimo import', 'historico de upload'.",
        "input_schema": {
            "type": "object",
            "properties": {"limite": {"type": "integer", "description": "Quantos lotes (padrao 200)"}},
        },
    },
    {
        "name": "consultar_localizacoes_canteiro",
        "description": "Localizacao (cidade/UF/endereco/aeroporto mais proximo) dos canteiros que ja tem esse cadastro feito - nem todos tem ainda, e' alimentado aos poucos.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "propor_lancamento_rapido",
        "description": (
            "Prepara um lancamento rapido de compra de passagem (ex.: 'comprei 10 passagens do "
            "Ceara pra SP por 3500') pra o usuario CONFIRMAR na tela antes de gravar. NUNCA grava "
            "direto no banco - so' monta a proposta, que aparece no painel lateral com um botao "
            "de confirmar. So' chame com origem, destino e valor_total certos (extraidos do que "
            "o usuario disse); se faltar algum desses 3, pergunte antes de chamar a ferramenta."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "origem": {"type": "string", "description": "Cidade/local de origem"},
                "destino": {"type": "string", "description": "Cidade/local de destino"},
                "valor_total": {"type": "number", "description": "Valor total pago (soma de todas as passagens desse lote)"},
                "quantidade": {"type": "integer", "description": "Quantas passagens (padrao 1)"},
                "modal": {"type": "string", "enum": ["aviao", "onibus", "carro", "taxi", "outro"], "description": "Padrao aviao"},
                "data": {"type": "string", "description": "Data da compra, formato YYYY-MM-DD (padrao hoje)"},
                "observacao": {"type": "string", "description": "Detalhe extra opcional (ex.: nome do fornecedor, se foi dito)"},
                "colaborador_nome": {
                    "type": "string",
                    "description": (
                        "Nome do colaborador, SO' se o usuario disse que e' pra uma pessoa "
                        "especifica (ex.: 'passagem do Joao'). Deixe vazio se for lote/compra "
                        "em massa sem pessoa definida ainda - nao pergunte isso sempre, so' "
                        "quando a frase do usuario ficar ambigua sobre isso."
                    ),
                },
            },
            "required": ["origem", "destino", "valor_total"],
        },
    },
    {
        "name": "consultar_distancia_carro",
        "description": (
            "Distancia e tempo REAIS de carro entre 2 pontos (Google Maps) - so' geografia, "
            "NUNCA preco. Use quando o usuario perguntar km/tempo de carro entre 2 lugares "
            "(ex.: 'quantos km de carro do canteiro X ate' Y'). O preco/custo estimado de "
            "combustivel so' e' calculado na tela (usuario informa consumo e preco do "
            "litro), essa ferramenta nao devolve preco nenhum - se o usuario quiser custo, "
            "diga pra usar o expansor 'Estimar por carro' na pagina de Custo/Passagens."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "origem": {"type": "string", "description": "Cidade/local de origem"},
                "destino": {"type": "string", "description": "Cidade/local de destino"},
            },
            "required": ["origem", "destino"],
        },
    },
    {
        "name": "consultar_link_skyscanner",
        "description": (
            "Monta um link pronto pra abrir a busca de passagem no Skyscanner (site real "
            "deles, deep-link oficial, sem API key) - use quando o usuario pedir pra "
            "'buscar passagem', 'ver preco de voo', 'cotar passagem' etc em conversa. "
            "Aceita nome de cidade OU codigo IATA pra origem/destino. NUNCA devolve preco "
            "nenhum - so' o link; quem ve o preco de verdade e' o proprio site quando a "
            "pessoa clica. Se a data nao for informada, usa hoje."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "origem": {"type": "string", "description": "Cidade ou codigo IATA de origem"},
                "destino": {"type": "string", "description": "Cidade ou codigo IATA de destino"},
                "data_ida": {
                    "type": "string",
                    "description": "Data de ida no formato AAAA-MM-DD. Deixe vazio se o usuario nao disse.",
                },
            },
            "required": ["origem", "destino"],
        },
    },
    {
        "name": "consultar_link_clickbus",
        "description": (
            "Monta um link pronto pra abrir a busca de passagem de ONIBUS no ClickBus (site "
            "real deles) - use quando o usuario pedir pra 'buscar passagem de onibus', 'ver "
            "rota de onibus' etc. Precisa de cidade E UF pra origem e destino (ex.: cidade "
            "'Fortaleza', uf 'CE') - sem UF nao da' pra montar o link direito. NAO suporta data "
            "especifica (o usuario escolhe a data na propria pagina do ClickBus depois de "
            "abrir). NUNCA devolve preco nenhum - so' o link."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "origem_cidade": {"type": "string", "description": "Cidade de origem"},
                "origem_uf": {"type": "string", "description": "UF (sigla, 2 letras) da origem"},
                "destino_cidade": {"type": "string", "description": "Cidade de destino"},
                "destino_uf": {"type": "string", "description": "UF (sigla, 2 letras) do destino"},
            },
            "required": ["origem_cidade", "origem_uf", "destino_cidade", "destino_uf"],
        },
    },
    {
        "name": "propor_atualizar_folga",
        "description": (
            "Propoe atualizar o status de UMA folga especifica (confirmar saida/retorno, marcar "
            "vendida, cancelada etc) - MESMA logica da tela 'Confirmar folgas', so' que pelo chat. "
            "NUNCA grava sozinho, so' resolve qual folga em aberto (status 'prevista', 'confirmada' "
            "ou 'em_andamento') bate com o nome dito e monta a proposta pro usuario confirmar no "
            "painel (igual propor_lancamento_rapido) - desde a v18.6 cobre inclusive folga que ja "
            "tinha passagem comprada ('confirmada') e depois foi vendida/cancelada, nao so' folga "
            "ainda 'prevista'. Use quando o usuario disser algo tipo 'confirma que o Fulano saiu "
            "ontem', 'marca a folga do Ciclano como vendida', 'o Fulano ja voltou, retornou dia X'. "
            "Se a ferramenta devolver erro (nome nao achado ou mais de 1 folga em aberto pra esse "
            "nome), oriente o usuario a usar a tela 'Confirmar folgas' direto pra escolher a linha "
            "certa."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "colaborador_nome": {
                    "type": "string",
                    "description": "Nome do colaborador, como o usuario disse.",
                },
                "status_novo": {
                    "type": "string",
                    "enum": ["confirmada", "em_andamento", "realizada", "vendida", "cancelada"],
                    "description": "Novo status da folga - nunca 'prevista' (isso seria nao mudar nada).",
                },
                "data_saida_real": {
                    "type": "string",
                    "description": "Data de saida real, formato AAAA-MM-DD, so' se o usuario disse. Deixe vazio se nao.",
                },
                "data_retorno_real": {
                    "type": "string",
                    "description": "Data de retorno real, formato AAAA-MM-DD, so' se o usuario disse. Deixe vazio se nao.",
                },
                "motivo_venda": {
                    "type": "string",
                    "description": "So' preencha se status_novo='vendida' e o usuario disse o motivo.",
                },
            },
            "required": ["colaborador_nome", "status_novo"],
        },
    },
    {
        "name": "calcular_diaria_deslocamento",
        "description": (
            "Calcula o valor total de diaria de deslocamento: dias informados x valor fixo "
            "por tipo (formula simples, decisao do Rafael 04/09/2026 - SEM regra de pernoite "
            "ou arredondamento ainda, isso fica pra depois se precisar). Use quando o usuario "
            "pedir pra 'calcular a diaria', 'quanto custa o deslocamento de X dias' etc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "tipo": {
                    "type": "string",
                    "enum": ["folga", "admissao_demissao_deslocamento"],
                    "description": "'folga' = deslocamento do ciclo normal (ida/volta de folga); 'admissao_demissao_deslocamento' = deslocamento de admissao/demissao.",
                },
                "dias": {
                    "type": "integer",
                    "description": "Total de dias de deslocamento (soma ida + volta, se for o caso).",
                },
            },
            "required": ["tipo", "dias"],
        },
    },
    {
        "name": "consultar_urgencias",
        "description": (
            "Resumo das urgencias atuais do Viaj.AI: (1) folga sem vinculo com RH ha mais de "
            "60 dias (schema_v0.40), (2) folgas chegando nos proximos dias SEM passagem "
            "lancada ainda, (3) lancamentos recentes com preco fora do padrao historico da "
            "rota, (4) passagem ja comprada vinculada a uma folga que depois virou vendida/"
            "cancelada (candidata a revisar estorno). Use quando o usuario perguntar 'tem "
            "alguma urgencia', 'o que precisa de atencao hoje', 'tem algo "
            "pendente' etc. Mesma logica da aba 'Urgencias' do app."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
]


def _resolver_colaborador_por_nome(supabase, nome_busca):
    """Tenta achar 1 colaborador ativo cujo nome contenha o texto dito no
    chat (case-insensitive). So' resolve se achar exatamente 1 - se achar
    0 ou mais de 1 (nome ambiguo), devolve (None, None) e deixa a pessoa
    escolher direto no seletor do painel de confirmacao (rede de seguranca,
    pedido do Rafael 03/09: "direcionar pra quem ficara esse custo antes
    de pensar em gravar")."""
    nome_busca = (nome_busca or "").strip().lower()
    if not nome_busca:
        return None, None
    try:
        r = supabase.rpc("viajai_colaboradores_ativos").execute()
    except Exception:
        return None, None
    candidatos = [c for c in (r.data or []) if nome_busca in (c.get("nome") or "").lower()]
    if len(candidatos) == 1:
        return candidatos[0]["colaborador_id"], candidatos[0]["nome"]
    return None, None


def _executar_ferramenta_viajai(supabase, nome, entrada):
    try:
        if nome == "consultar_previsao_folgas":
            r = supabase.rpc("viajai_previsao_folgas").execute()
        elif nome == "consultar_pendencias_import":
            r = supabase.rpc("viajai_listar_pendencias_import", {
                "p_apenas_nao_resolvidas": entrada.get("apenas_nao_resolvidas", True),
            }).execute()
        elif nome == "consultar_folgas_aguardando_vinculo":
            r = supabase.rpc("viajai_folgas_sem_vinculo_rh", {
                "p_dias": entrada.get("dias_minimo", 0),
            }).execute()
        elif nome == "consultar_historico_folga":
            r = supabase.rpc("viajai_listar_historico_folga", {"p_limite": entrada.get("limite", 200)}).execute()
        elif nome == "consultar_desvio_planejamento":
            r = supabase.rpc("viajai_listar_folgas_desvio", {"p_limite": entrada.get("limite", 200)}).execute()
        elif nome == "consultar_previsao_gasto_colaborador":
            r = supabase.rpc("viajai_previsao_gasto_colaborador").execute()
        elif nome == "consultar_comparativo_custo_folga":
            r = supabase.rpc("viajai_comparativo_custo_folga", {"p_limite": entrada.get("limite", 200)}).execute()
        elif nome == "consultar_sugestao_fornecedor_rota":
            r = supabase.rpc("viajai_sugestao_fornecedor_rota", {
                "p_origem": entrada.get("origem", ""), "p_destino": entrada.get("destino", ""),
            }).execute()
        elif nome == "consultar_comparar_modais_rota":
            r = supabase.rpc("viajai_comparar_modais_rota", {
                "p_origem": entrada.get("origem", ""), "p_destino": entrada.get("destino", ""),
            }).execute()
        elif nome == "consultar_resumo_custo_por_rota":
            r = supabase.rpc("viajai_resumo_custo_por_rota", {"p_limite": entrada.get("limite", 100)}).execute()
        elif nome == "consultar_gasto_por_periodo":
            r = supabase.rpc("viajai_gasto_por_periodo", {"p_meses": entrada.get("meses", 12)}).execute()
        elif nome == "consultar_lancamentos_rapidos":
            r = supabase.rpc("viajai_listar_lancamentos_rapidos", {"p_limite": entrada.get("limite", 200)}).execute()
        elif nome == "consultar_historico_imports":
            r = supabase.rpc("viajai_listar_import_batches", {"p_limite": entrada.get("limite", 200)}).execute()
        elif nome == "consultar_localizacoes_canteiro":
            r = supabase.rpc("viajai_listar_localizacoes_canteiro").execute()
        elif nome == "consultar_distancia_carro":
            # nao passa pelo padrao supabase.rpc(...).execute() - chama a
            # API do Google direto (funcao ja devolve o dict pronto, com
            # "erro" quando da' errado) - so' geografia, nunca preco.
            return _consultar_distancia_carro(entrada.get("origem", ""), entrada.get("destino", ""))
        elif nome == "consultar_link_skyscanner":
            # tambem nao passa pelo supabase - so' monta URL local (mesma
            # logica do botao manual na tela Custo & Passagens); nunca
            # busca/mostra preco, so' devolve o link pronto.
            return _link_skyscanner(
                entrada.get("origem", ""), entrada.get("destino", ""), entrada.get("data_ida", "")
            )
        elif nome == "consultar_link_clickbus":
            # mesma logica do skyscanner: nao passa pelo supabase, so' monta
            # URL local, nunca mostra preco.
            return _link_clickbus(
                entrada.get("origem_cidade", ""), entrada.get("origem_uf", ""),
                entrada.get("destino_cidade", ""), entrada.get("destino_uf", ""),
            )
        elif nome == "propor_lancamento_rapido":
            # NUNCA grava aqui - so' monta a proposta pro usuario confirmar
            # na tela (col_dash em pagina_chat). O INSERT de verdade so'
            # acontece quando a pessoa clica "Confirmar e registrar", que
            # chama viajai_registrar_lancamento_rapido direto (sem passar
            # pela IA de novo) - pedido do Rafael 03/09: IA pode propor
            # acao, mas quem executa e' sempre o humano clicando.
            origem = (entrada.get("origem") or "").strip()
            destino = (entrada.get("destino") or "").strip()
            valor_total = entrada.get("valor_total")
            if not origem or not destino or not valor_total:
                return {"erro": "faltou origem, destino ou valor_total - pergunte pro usuario antes de propor de novo"}
            colaborador_nome_dito = (entrada.get("colaborador_nome") or "").strip()
            colaborador_id_resolvido, colaborador_nome_resolvido = _resolver_colaborador_por_nome(
                supabase, colaborador_nome_dito
            )
            if "propostas_pendentes_viajai" not in st.session_state:
                st.session_state.propostas_pendentes_viajai = []
            st.session_state.propostas_pendentes_viajai.append({
                "id": uuid.uuid4().hex[:8],
                "tipo": "lancamento_rapido",
                "origem": origem,
                "destino": destino,
                "valor_total": float(valor_total),
                "quantidade": int(entrada.get("quantidade") or 1),
                "modal": entrada.get("modal") or "aviao",
                "data": entrada.get("data") or date.today().isoformat(),
                "observacao": entrada.get("observacao") or "",
                "colaborador_id": colaborador_id_resolvido,
                "colaborador_nome": colaborador_nome_resolvido,
            })
            resumo = f"{entrada.get('quantidade') or 1}x {origem} -> {destino}, R$ {float(valor_total):.2f}"
            aviso_colaborador = ""
            if colaborador_nome_dito and not colaborador_id_resolvido:
                aviso_colaborador = (
                    f" (nao encontrei '{colaborador_nome_dito}' com certeza entre os "
                    "colaboradores ativos - avise o usuario pra escolher direto no painel)"
                )
            elif colaborador_nome_resolvido:
                resumo += f" — {colaborador_nome_resolvido}"
            total_pendentes = len(st.session_state.propostas_pendentes_viajai)
            return {
                "status": (
                    f"proposta adicionada ao painel lateral (agora sao {total_pendentes} "
                    "pendente(s) aguardando confirmacao, nenhuma foi gravada ainda)"
                ) + aviso_colaborador,
                "resumo": resumo,
            }
        elif nome == "propor_atualizar_folga":
            # MESMA regra de seguranca: NUNCA grava aqui. So' resolve QUAL
            # folga (tem que achar exatamente 1 folga em aberto - prevista,
            # confirmada ou em_andamento, schema_v0.31 - com o nome dito -
            # 0 ou mais de 1 e' erro, pra nao arriscar atualizar a pessoa
            # errada) e monta a proposta - quem executa de verdade e' o
            # clique humano no painel, chamando viajai_atualizar_folga
            # direto (MESMA RPC ja usada pela tela "Confirmar folgas",
            # nenhum schema novo precisou ser escrito pra isso).
            colaborador_nome_dito = (entrada.get("colaborador_nome") or "").strip()
            status_novo = (entrada.get("status_novo") or "").strip()
            if not colaborador_nome_dito or not status_novo:
                return {"erro": "faltou colaborador_nome ou status_novo"}
            if status_novo not in ("confirmada", "em_andamento", "realizada", "vendida", "cancelada"):
                return {"erro": f"status_novo invalido: '{status_novo}'"}
            r_prev = supabase.rpc("viajai_listar_folgas_previstas", {"p_limite": 300}).execute()
            candidatos = [
                fl for fl in (r_prev.data or [])
                if colaborador_nome_dito.lower() in (fl.get("nome") or "").lower()
            ]
            if len(candidatos) == 0:
                return {
                    "erro": (
                        f"Nao achei nenhuma folga em aberto (prevista/confirmada/em_andamento) pra "
                        f"'{colaborador_nome_dito}' - confere o nome ou oriente a usar a tela "
                        "'Confirmar folgas' direto."
                    )
                }
            if len(candidatos) > 1:
                return {
                    "erro": (
                        f"Achei {len(candidatos)} folgas em aberto pra '{colaborador_nome_dito}' - "
                        "nome ambiguo, preciso de um nome mais especifico ou oriente a usar a tela "
                        "'Confirmar folgas' direto pra escolher a linha certa."
                    )
                }
            folga_alvo = candidatos[0]
            if "propostas_pendentes_viajai" not in st.session_state:
                st.session_state.propostas_pendentes_viajai = []
            st.session_state.propostas_pendentes_viajai.append({
                "id": uuid.uuid4().hex[:8],
                "tipo": "atualizar_folga",
                "folga_id": folga_alvo["folga_id"],
                "colaborador_nome": folga_alvo.get("nome"),
                "status_novo": status_novo,
                "data_saida_real": entrada.get("data_saida_real") or None,
                "data_retorno_real": entrada.get("data_retorno_real") or None,
                "motivo_venda": entrada.get("motivo_venda") or None,
            })
            total_pendentes = len(st.session_state.propostas_pendentes_viajai)
            return {
                "status": (
                    f"proposta de atualizacao de folga adicionada ao painel lateral (agora sao "
                    f"{total_pendentes} pendente(s) aguardando confirmacao, nada foi gravado ainda)"
                ),
                "resumo": f"{folga_alvo.get('nome')}: {folga_alvo.get('status')} -> {status_novo}",
            }
        elif nome == "calcular_diaria_deslocamento":
            tipo = (entrada.get("tipo") or "").strip()
            dias = entrada.get("dias")
            if tipo not in ("folga", "admissao_demissao_deslocamento") or not dias:
                return {"erro": "faltou tipo (folga ou admissao_demissao_deslocamento) ou dias"}
            r_diaria = supabase.rpc(
                "viajai_calcular_diaria_simples",
                {"p_tipo": tipo, "p_dias": int(dias)},
            ).execute()
            valor_total = r_diaria.data
            if valor_total is None:
                return {"erro": f"tipo '{tipo}' nao encontrado na config de diaria"}
            return {
                "tipo": tipo,
                "dias": int(dias),
                "valor_total": float(valor_total),
                "resumo": f"{int(dias)} dia(s) x valor fixo ({tipo}) = R$ {float(valor_total):.2f} (formula simples, sem pernoite ainda)",
            }
        elif nome == "consultar_urgencias":
            r_sem_vinculo = supabase.rpc("viajai_folgas_sem_vinculo_rh", {"p_dias": 60}).execute()
            r_sem_passagem = supabase.rpc("viajai_folgas_sem_passagem", {"p_dias_janela": 10}).execute()
            r_preco = supabase.rpc(
                "viajai_alerta_preco_fora_padrao", {"p_dias_janela": 30, "p_desvio_pct": 0.4}
            ).execute()
            r_revisar = supabase.rpc("viajai_folga_passagem_para_revisar").execute()
            return {
                "folgas_sem_vinculo_rh": r_sem_vinculo.data or [],
                "folgas_sem_passagem": r_sem_passagem.data or [],
                "precos_fora_padrao": r_preco.data or [],
                "passagens_para_revisar": r_revisar.data or [],
            }
        else:
            return {"erro": "ferramenta desconhecida"}
        return r.data if r.data else []
    except Exception as e:
        try:
            supabase.rpc("viajai_registrar_log_erro", {
                "p_contexto": "chat_tool",
                "p_ferramenta": nome,
                "p_entrada": entrada,
                "p_mensagem_erro": str(e),
            }).execute()
        except Exception:
            pass  # log e' best-effort - nunca pode quebrar a resposta pro usuario
        return {"erro": str(e)}


def _montar_system_prompt_viajai(usuario_email):
    return (
        "Voce e o assistente do Viaj.AI, sistema de gestao de folgas/viagens/custo de "
        "colaboradores em obra da EnerMais. Ajuda a Amanda (compradora/logistica) e outras "
        f"pessoas autorizadas. A pessoa logada agora e {usuario_email}.\n\n"
        f"A data de HOJE e {date.today().isoformat()} — use esse fato pra resolver qualquer "
        "expressao de data relativa ('proximos 30 dias', 'esse mes', 'mes passado'), nunca "
        "calcule data de cabeca.\n\n"
        "Responda so com dado que veio de verdade das ferramentas — nunca invente numero, "
        "preco, rota ou nome de fornecedor. Se a ferramenta nao trouxer dado suficiente, "
        "diga isso claramente em vez de estimar ou supor.\n\n"
        "Se o resultado de uma ferramenta trouxer MUITOS registros (mais de uns 15), "
        "RESUMA com numero/agregado em vez de listar todo mundo pelo nome - isso evita "
        "resposta gigante e cortada pela metade. So liste nomes um por um se forem poucos "
        "(ate uns 15) ou se a pessoa pedir a lista completa explicitamente. A tabela "
        "completa sempre aparece no painel lateral de qualquer forma.\n\n"
        "IMPORTANTE sobre preco de passagem: voce NAO tem acesso a busca de preco em tempo "
        "real (decisao de projeto, 02/09) — toda 'previsao' ou 'estimativa' de custo vem do "
        "HISTORICO ja registrado no proprio Viaj.AI, nunca do seu conhecimento geral sobre "
        "preco de passagem. Sem historico suficiente pra uma rota ou colaborador, diga isso "
        "em vez de chutar um valor plausivel.\n\n"
        "IMPORTANTE sobre pergunta repetida: se o usuario perguntar de novo algo que voce "
        "ja respondeu antes NESSA MESMA conversa (ex.: previsao de gasto, previsao de folga, "
        "qualquer numero que pode ter mudado), CHAME A FERRAMENTA DE NOVO, nunca repita o "
        "valor que voce mesmo disse antes so' porque ele ja esta na conversa - o dado no "
        "banco pode ter mudado entre uma pergunta e outra (ex.: a pessoa acabou de "
        "confirmar um lancamento novo). Sua propria resposta anterior NAO e' fonte "
        "confiavel pra responder de novo, so' a ferramenta e'.\n\n"
        "Voce PODE propor o registro de uma compra de passagem via "
        "propor_lancamento_rapido quando o usuario contar que comprou (ex.: 'comprei 10 "
        "passagens do Ceara pra SP por 3500') — mas isso NUNCA grava direto: so' monta uma "
        "proposta que aparece pro usuario confirmar na tela antes de qualquer coisa ir pro "
        "banco. So' chame essa ferramenta com origem, destino e valor_total certos; se "
        "faltar algum, pergunte antes (nunca invente valor pra completar). Se o usuario "
        "citar o nome de uma pessoa especifica pra quem e' a passagem, passe em "
        "colaborador_nome. Se parecer lote/compra em massa sem pessoa definida ainda (ex.: "
        "'comprei 10 passagens do Ceara pra SP'), NAO pergunte de quem e' - isso e' normal e "
        "fica sem colaborador definido, a pessoa pode atribuir depois na tela. So' pergunte "
        "'e' pra alguem especifico ou lote sem definir ainda?' quando a frase ficar realmente "
        "ambigua sobre isso.\n\n"
        "Se o usuario descrever VARIAS compras numa mensagem so' (ex.: varios "
        "colaboradores, varios trechos de uma mesma viagem, ou uma lista de lancamentos "
        "diferentes), chame propor_lancamento_rapido UMA VEZ PRA CADA lancamento "
        "separado (1 pessoa + 1 trecho = 1 chamada) — cada chamada vira uma proposta "
        "INDEPENDENTE no painel lateral, empilhada junto com as outras, nunca substitui a "
        "anterior. Quando terminar de propor todas, informe corretamente quantas ficaram "
        "pendentes (o campo 'status' de cada chamada já te diz o total acumulado até "
        "aquele momento) e diga que da' pra confirmar uma por uma OU todas de uma vez com "
        "o botao 'Confirmar todas' que aparece quando ha' mais de 1 pendente. Se o usuario "
        "der um valor TOTAL (ex.: 'gastei 6mil no total, dividido em 3 trechos') e nao "
        "estiver claro quanto cada trecho custou, pergunte o valor de cada um antes de "
        "propor — nunca reparta um valor total automaticamente (dividir errado seria "
        "inventar numero).\n\n"
        "Voce tambem pode PROPOR atualizar o status de uma folga (confirmar saida/retorno, "
        "vendida, cancelada) via propor_atualizar_folga - MESMA regra: nunca grava sozinho, so' "
        "propoe pro usuario confirmar no painel. Fora essas 2 propostas, voce ainda so' CONSULTA "
        "— outra acao (registrar trecho/gasto de uma folga especifica) nao tem ferramenta ainda, "
        "oriente a usar a tela correspondente. Varias acoes existem SO na tela, sem ferramenta "
        "de chat pra executar (voce pode explicar que existem e orientar onde estao, mas nao "
        "tem como fazer por voce): 'vincular ao RH' uma folga aguardando vinculo, manual ou "
        "'tentar vincular automaticamente' (secao 'Folgas aguardando vinculo com RH', dentro de "
        "'Importar RE090'), 'adicionar folga manualmente' sem planilha, pra demanda emergencial "
        "(expander na mesma tela 'Importar RE090'), 'reprocessar pendencias de import' - so' "
        "afeta pendencia ANTIGA, de antes do schema_v0.40 (botao na mesma tela, tenta casar de "
        "novo contra o RH atual sem precisar reupload), 'atribuir colaborador' a um lancamento "
        "rapido que ficou sem pessoa/so com nome provisorio (expander na aba 'Lancamento "
        "rapido', dentro de 'Custo & Passagens'), 'marcar passagem como revisada' (formulario "
        "na aba 'Urgencias', secao 'Passagem vinculada a folga vendida/cancelada' - fica "
        "registrado pra sempre no historico dali) e 'marcar/desfazer reembolso de um trecho' "
        "(expander na aba 'Por folga', dentro de 'Custo & Passagens' - desconta do calculo de "
        "gasto real, sem mexer no preco original da passagem).\n\n"
        "Se o usuario perguntar 'como funciona', 'o que voce consegue fazer', 'pra que serve "
        "essa tela/funcao' ou demonstrar duvida sobre o fluxo do Viaj.AI, EXPLIQUE em texto "
        "claro em vez de tentar chamar uma ferramenta - use como referencia o conteudo da aba "
        "'Central de Ajuda' do proprio app (fluxo geral, o que cada tela faz, o que voce pode/"
        "nao pode fazer, frases-modelo, mensagens comuns que nao sao erro).\n\n"
        "Guia de qual ferramenta usar:\n"
        "- quem esta de folga / precisa viajar / urgencia -> consultar_previsao_folgas.\n"
        "- folga sem match no RH / nome provisorio / aguardando vinculo -> "
        "consultar_folgas_aguardando_vinculo (schema_v0.40 - e' o caso normal hoje pra quem nao "
        "bateu no import).\n"
        "- pendencia de import ANTIGA/legado (de antes do schema_v0.40) -> "
        "consultar_pendencias_import (so' use se o usuario pedir especificamente por isso).\n"
        "- historico de mudanca de status de folga -> consultar_historico_folga.\n"
        "- quem atrasou / desvio do planejado -> consultar_desvio_planejamento.\n"
        "- previsao de gasto por colaborador -> consultar_previsao_gasto_colaborador "
        "(sempre informe o 'base_previsao' que vier na resposta - se vier 'empresa', deixe "
        "claro que e' media geral da empresa toda, nao dado especifico dessa pessoa).\n"
        "- custo real x desvio de uma folga -> consultar_comparativo_custo_folga.\n"
        "- qual companhia mais usamos numa rota -> consultar_sugestao_fornecedor_rota "
        "(precisa origem e destino).\n"
        "- aviao x onibus x carro numa rota -> consultar_comparar_modais_rota (precisa "
        "origem e destino).\n"
        "- gasto total por rota -> consultar_resumo_custo_por_rota.\n"
        "- gasto por mes/periodo -> consultar_gasto_por_periodo.\n"
        "- lancamentos rapidos recentes -> consultar_lancamentos_rapidos.\n"
        "- onde fica um canteiro / aeroporto mais proximo -> consultar_localizacoes_canteiro "
        "(nem todo canteiro tem cadastro ainda, avise se nao achar).\n"
        "- usuario disse que COMPROU passagem(ns) -> propor_lancamento_rapido (so' com "
        "origem/destino/valor certos; nunca grava sozinho, so' propoe pro usuario confirmar).\n"
        "- quantos km / quanto tempo de carro entre 2 lugares -> consultar_distancia_carro "
        "(Google Maps - devolve so' distancia/tempo REAIS, NUNCA preco/custo; se o usuario "
        "quiser custo estimado de combustivel, explique que precisa usar o expansor 'Estimar "
        "por carro' na pagina de Custo/Passagens, la' ele informa consumo e preco do litro).\n"
        "- usuario pede pra buscar/cotar passagem/voo -> consultar_link_skyscanner (devolve "
        "so' um link pronto pro site real deles, NUNCA um preco - se der erro de origem/"
        "destino nao reconhecido, peca o codigo do aeroporto direto).\n"
        "- usuario disse que uma folga MUDOU (confirmou saida/retorno, vendeu, cancelou) -> "
        "- usuario pede pra buscar/cotar passagem de ONIBUS -> consultar_link_clickbus (precisa "
        "cidade + UF de origem e destino; devolve so' link, NUNCA preco; nao suporta data "
        "especifica, avise que a data e' escolhida na pagina do ClickBus).\n"
        "propor_atualizar_folga (so' propoe, nunca grava sozinho; se der erro de nome nao "
        "achado ou ambiguo, oriente a usar a tela 'Confirmar folgas' direto).\n"
        "- calcular quanto e' de diaria de deslocamento (dias x valor fixo) -> "
        "calcular_diaria_deslocamento (formula simples por decisao do Rafael 04/09/2026, "
        "sem regra de pernoite/arredondamento ainda).\n"
        "- tem urgencia / precisa de atencao / algo pendente -> consultar_urgencias "
        "(folga sem passagem, preco fora do padrao, passagem pra revisar apos folga "
        "vendida/cancelada - mesma logica da aba 'Urgencias')."
    )


FERRAMENTAS_VISUAIS_VIAJAI = {
    tool["name"] for tool in TOOLS_VIAJAI
    if tool["name"] not in ("propor_lancamento_rapido", "propor_atualizar_folga")
}
# Toda ferramenta de consulta pode virar tabela no painel lateral do chat;
# a de localizacao de canteiro tambem tenta virar mapa (se tiver lat/lon
# cadastrada) — pedido do Rafael 02/09: "gerar um dash interativo ao lado,
# mostrando tabela, mapa". Mesmo padrao do TIA.go (col_dash / dash_extra),
# adaptado pras ferramentas do Viaj.AI.


def pagina_chat(supabase):
    st.subheader("Viaj.AI")
    st.caption(
        "Converse em português sobre folgas, urgência, custo e histórico — só responde com "
        "dado real do Viaj.AI (nunca busca preço na internet nem inventa número). Já entende "
        "'comprei N passagens de X pra Y' e prepara o lançamento, mas só grava depois que "
        "você confirmar no painel ao lado — nunca escreve sozinho."
    )
    st.caption(
        f"Obs.: o assistente lembra só das últimas {JANELA_HISTORICO_CHAT} mensagens desta "
        "conversa (fica mais rápido e evita confundir com resposta antiga) — o histórico "
        "completo continua salvo. Pra números que mudam (previsão, gasto), pergunte de novo "
        "em vez de confiar numa resposta antiga."
    )

    cidades_usadas = _obter_cidades_usadas(supabase)

    # atalhos de relatorio (pedido do Rafael 03/09) ficam ANTES do check da
    # chave Anthropic de proposito: chamam a RPC direto, nunca passam pela IA,
    # entao nao dependem de ANTHROPIC_API_KEY pra funcionar.
    st.caption("Atalhos de relatório (instantâneo, não passa pela IA):")
    _cols_atalho = st.columns(len(REPORTS_RAPIDOS_VIAJAI))
    for _col, _rep in zip(_cols_atalho, REPORTS_RAPIDOS_VIAJAI):
        if _col.button(_rep["label"], key=f"atalho_{_rep['tool']}", use_container_width=True):
            _resultado_atalho = _executar_ferramenta_viajai(supabase, _rep["tool"], _rep["input"])
            st.session_state.dash_extra_viajai = {
                "tool": _rep["tool"], "input": _rep["input"], "resultado": _resultado_atalho,
            }
            st.rerun()

    if not ANTHROPIC_API_KEY:
        # limitacao aceita: sem essa chave a funcao para aqui, entao o painel
        # com a tabela/download do atalho clicado acima nao chega a aparecer
        # nesse caso especifico (na pratica nao acontece - a chave ja esta
        # configurada em producao; se um dia sumir, so mover o bloco de
        # col_dash pra fora desse return resolve, nao fiz agora pra nao mexer
        # numa pagina que ja funciona por uma situacao que nao ocorre hoje).
        st.warning(
            "Chave da Anthropic ainda não configurada (Secrets do Streamlit Cloud: "
            "ANTHROPIC_API_KEY) — o chat em linguagem natural não funciona sem ela "
            "(mas os atalhos de relatório acima funcionam sem essa chave)."
        )
        return

    if "mensagens_chat" not in st.session_state:
        # carrega so as ultimas JANELA_HISTORICO_CHAT (o log completo continua
        # no banco pra sempre, isso e' so o que entra no contexto ativo)
        hist = supabase.rpc(
            "viajai_listar_historico_chat", {"p_limite": JANELA_HISTORICO_CHAT}
        ).execute()
        st.session_state.mensagens_chat = [
            {"role": m["papel"], "content": m["conteudo"]} for m in (hist.data or [])
        ]

    def _escapar_dolar(texto):
        return texto.replace("$", "\\$")

    col_chat, col_dash = st.columns([3, 2])

    with col_chat:
        # Container de altura fixa - pedido do Rafael 03/09: o campo de
        # digitar ia descendo junto com a conversa em vez de ficar fixo
        # embaixo. Achado (doc oficial do Streamlit, checado antes de
        # mexer): st.chat_input SO fixa sozinho no rodape quando chamado
        # no corpo principal da pagina - dentro de st.columns ele vira um
        # campo comum, sem fixar. Por isso o chat_input foi movido pra
        # fora das colunas (ve mais abaixo) e aqui a lista de mensagens
        # ganhou altura fixa com rolagem propria, pra nao esticar a pagina.
        historico_box = st.container(height=900)
        with historico_box:
            for m in st.session_state.mensagens_chat:
                with st.chat_message(m["role"]):
                    conteudo = m["content"] if isinstance(m["content"], str) else "(ferramenta)"
                    st.markdown(_escapar_dolar(conteudo))

    with col_dash:
        # BUG CORRIGIDO 03/09 (achado pelo Rafael testando compra
        # multi-pessoa/multi-trecho, "so' gravou 1?"): acao_pendente_viajai
        # era um dict UNICO no session_state - quando a IA chamava
        # propor_lancamento_rapido varias vezes na mesma resposta (1 por
        # pessoa/trecho), cada chamada SOBRESCREVIA a anterior, so' a
        # ultima sobrevivia ate a tela, mesmo a IA descrevendo em texto
        # "9 propostas prontas". Virou lista (propostas_pendentes_viajai),
        # cada proposta com id proprio - confirma/cancela 1 por 1, ou em
        # lote com "Confirmar todas".
        propostas = st.session_state.get("propostas_pendentes_viajai", [])
        # v11.0: 2 tipos de proposta agora (lancamento_rapido e atualizar_folga,
        # ver propor_atualizar_folga) - separados aqui pra cada bloco renderizar
        # so' o que sabe tratar; a lista guardada continua unica no session_state.
        propostas_lanc = [p for p in propostas if p.get("tipo", "lancamento_rapido") == "lancamento_rapido"]
        propostas_folga = [p for p in propostas if p.get("tipo") == "atualizar_folga"]
        if propostas:
            st.warning(
                f"{len(propostas)} proposta(s) aguardando confirmação — extraído da "
                "conversa, revise cada uma antes de gravar"
            )
        if propostas_lanc:
            _colabs_resp = supabase.rpc("viajai_colaboradores_ativos").execute()
            _colabs_lista = _colabs_resp.data or []
            _colabs_opcoes = ["— Lote / sem definir —"] + [c["nome"] for c in _colabs_lista]
            _colabs_por_nome = {c["nome"]: c["colaborador_id"] for c in _colabs_lista}
            # v20.0: mesmo vinculo opcional de folga que existe na tela
            # "Lançamento rápido" (Custo & Passagens), agora tambem no card
            # de confirmacao do chat - pedido do Rafael 08/09 ("via chat e
            # via pagina de passagem pra revisar tb"). O humano escolhe no
            # dropdown, a IA nunca resolve folga_id sozinha.
            _folgas_abertas_chat_resp = supabase.rpc("viajai_listar_folgas_previstas", {"p_limite": 300}).execute()
            _opcoes_folga_chat = ["— Nenhuma —"] + [
                f"#{f['folga_id']} — {f['nome']} — {f.get('canteiro_nome') or '—'} — {f['status']}"
                for f in (_folgas_abertas_chat_resp.data or [])
            ]
            _folga_id_por_rotulo_chat = {
                f"#{f['folga_id']} — {f['nome']} — {f.get('canteiro_nome') or '—'} — {f['status']}": f["folga_id"]
                for f in (_folgas_abertas_chat_resp.data or [])
            }

            if len(propostas_lanc) > 1:
                col_all_ok, col_all_no = st.columns(2)
                confirmar_todas = col_all_ok.button(
                    f"✅ Confirmar todas ({len(propostas_lanc)})", use_container_width=True,
                    key="btn_confirmar_todas_propostas",
                )
                cancelar_todas = col_all_no.button(
                    "Cancelar todas", use_container_width=True, key="btn_cancelar_todas_propostas",
                )
                if confirmar_todas:
                    _registrados_agora = []
                    _ids_registrados = set()
                    _erros_lote = []
                    for p in propostas_lanc:
                        try:
                            _novo_id = supabase.rpc("viajai_registrar_lancamento_rapido", {
                                "p_origem": p["origem"], "p_destino": p["destino"],
                                "p_valor_total": p["valor_total"], "p_quantidade": p["quantidade"],
                                "p_modal": p["modal"], "p_data": p["data"],
                                "p_observacao": p.get("observacao") or None,
                                "p_colaborador_id": p.get("colaborador_id"),
                            }).execute().data
                            _resumo_txt = f"{p['quantidade']}x {p['origem']} -> {p['destino']}, R$ {p['valor_total']:.2f}"
                            if p.get("colaborador_nome"):
                                _resumo_txt += f" — {p['colaborador_nome']}"
                            _registrados_agora.append({"id": _novo_id, "resumo": _resumo_txt})
                            _ids_registrados.add(p["id"])
                        except Exception as e:
                            _erros_lote.append(f"{p['origem']} -> {p['destino']}: {e}")
                    st.session_state.registros_recentes_viajai = (
                        _registrados_agora + st.session_state.get("registros_recentes_viajai", [])
                    )
                    # so' fica pendente quem deu erro - o que gravou sai da
                    # lista pelo id (nao por texto, pra nao arriscar casar
                    # errado com origem/valor repetido entre propostas).
                    st.session_state.propostas_pendentes_viajai = [
                        p for p in propostas if p["id"] not in _ids_registrados
                    ]
                    if _registrados_agora:
                        _resumo_msg = "; ".join(r["resumo"] for r in _registrados_agora)
                        _texto_lote = f"Registrados {len(_registrados_agora)} lançamento(s): {_resumo_msg}."
                        st.session_state.mensagens_chat.append({"role": "assistant", "content": _texto_lote})
                        supabase.rpc("viajai_salvar_mensagem_chat", {
                            "p_papel": "assistant", "p_conteudo": _texto_lote,
                        }).execute()
                    if _erros_lote:
                        st.session_state["_erros_lote_viajai"] = _erros_lote
                    st.rerun()
                if cancelar_todas:
                    # so cancela as de lancamento_rapido - folga pendente (se houver)
                    # nao e' tocada por este botao, tem cancelar proprio no bloco dela.
                    st.session_state.propostas_pendentes_viajai = [
                        p for p in st.session_state.propostas_pendentes_viajai
                        if p.get("tipo", "lancamento_rapido") != "lancamento_rapido"
                    ]
                    st.rerun()
                _erros_pendentes = st.session_state.pop("_erros_lote_viajai", None)
                if _erros_pendentes:
                    st.error("Alguns não gravaram, ficaram pendentes pra revisar: " + "; ".join(_erros_pendentes))
                st.divider()

            for acao in list(propostas_lanc):
                _pid = acao["id"]
                _titulo = (
                    f"{acao['quantidade']}x {acao['origem']} → {acao['destino']} — "
                    f"R$ {acao['valor_total']:.2f}"
                )
                if acao.get("colaborador_nome"):
                    _titulo += f" — {acao['colaborador_nome']}"
                with st.expander(_titulo, expanded=(len(propostas_lanc) == 1)):
                    _indice_colab_default = 0
                    if acao.get("colaborador_nome") and acao["colaborador_nome"] in _colabs_opcoes:
                        _indice_colab_default = _colabs_opcoes.index(acao["colaborador_nome"])
                    # Origem/Destino ficam FORA do form de propósito
                    # (selectbox dentro de form so' reage no submit - ver
                    # _input_cidade_com_sugestao).
                    c_origem = _input_cidade_com_sugestao(
                        st, "Origem", f"origem_{_pid}", cidades_usadas, valor_atual=acao["origem"],
                    )
                    c_destino = _input_cidade_com_sugestao(
                        st, "Destino", f"destino_{_pid}", cidades_usadas, valor_atual=acao["destino"],
                    )
                    with st.form(f"form_confirmar_lancamento_ia_{_pid}"):
                        c_valor = st.number_input(
                            "Valor total (R$)", value=float(acao["valor_total"]), min_value=0.0,
                            step=0.01, key=f"valor_{_pid}",
                        )
                        c_qtd = st.number_input(
                            "Quantidade", value=int(acao["quantidade"]), min_value=1, step=1, key=f"qtd_{_pid}",
                        )
                        c_modal = st.selectbox(
                            "Modal", ["aviao", "onibus", "carro", "taxi", "outro"],
                            index=["aviao", "onibus", "carro", "taxi", "outro"].index(acao["modal"]) if acao["modal"] in ["aviao", "onibus", "carro", "taxi", "outro"] else 0,
                            key=f"modal_{_pid}",
                        )
                        try:
                            _data_default = date.fromisoformat(acao["data"])
                        except (ValueError, TypeError):
                            _data_default = date.today()
                        c_data = st.date_input("Data", value=_data_default, key=f"data_{_pid}")
                        c_obs = st.text_input("Observação", value=acao.get("observacao", ""), key=f"obs_{_pid}")
                        c_colab = st.selectbox(
                            "Colaborador (opcional)", _colabs_opcoes, index=_indice_colab_default, key=f"colab_{_pid}",
                        )
                        c_folga = st.selectbox(
                            "Folga vinculada (opcional)", _opcoes_folga_chat, key=f"folga_{_pid}",
                            help=(
                                "Só se essa passagem for de uma folga específica — precisa "
                                "do colaborador real escolhido acima, dono dessa folga."
                            ),
                        )
                        col_ok, col_no = st.columns(2)
                        confirmar = col_ok.form_submit_button("✅ Confirmar e registrar", use_container_width=True)
                        cancelar = col_no.form_submit_button("Cancelar", use_container_width=True)

                    if confirmar:
                        _colab_id_confirmar = _colabs_por_nome.get(c_colab)
                        _novo_id = supabase.rpc("viajai_registrar_lancamento_rapido", {
                            "p_origem": c_origem, "p_destino": c_destino, "p_valor_total": c_valor,
                            "p_quantidade": int(c_qtd), "p_modal": c_modal,
                            "p_data": c_data.isoformat(), "p_observacao": c_obs or None,
                            "p_colaborador_id": _colab_id_confirmar,
                            "p_folga_id": _folga_id_por_rotulo_chat.get(c_folga),
                        }).execute().data
                        st.session_state.propostas_pendentes_viajai = [
                            p for p in st.session_state.propostas_pendentes_viajai if p["id"] != _pid
                        ]
                        _resumo_txt = f"{int(c_qtd)}x {c_origem} -> {c_destino}, R$ {c_valor:.2f}"
                        if _colab_id_confirmar:
                            _resumo_txt += f" — {c_colab}"
                        # Guarda o id pra oferecer "Desfazer" na hora - pedido do
                        # Rafael 03/09. schema_v0.16 precisa estar rodado
                        # (viajai_apagar_lancamento_rapido) - se nao estiver,
                        # o botao "Desfazer" abaixo vai dar erro claro na hora.
                        st.session_state.registros_recentes_viajai = (
                            [{"id": _novo_id, "resumo": _resumo_txt}]
                            + st.session_state.get("registros_recentes_viajai", [])
                        )
                        st.session_state.mensagens_chat.append({
                            "role": "assistant",
                            "content": f"Registrado: {_resumo_txt}.",
                        })
                        supabase.rpc("viajai_salvar_mensagem_chat", {
                            "p_papel": "assistant",
                            "p_conteudo": f"Registrado: {_resumo_txt}.",
                        }).execute()
                        st.rerun()
                    elif cancelar:
                        st.session_state.propostas_pendentes_viajai = [
                            p for p in st.session_state.propostas_pendentes_viajai if p["id"] != _pid
                        ]
                        st.rerun()

        if propostas_folga:
            # v11.0 (propor_atualizar_folga): mesmo padrao de expander +
            # form individual do lancamento rapido, mas so' confirmacao
            # 1 a 1 (sem "confirmar todas" em lote aqui de proposito -
            # atualizar status de folga e' 1 pessoa por vez, sem o cenario
            # de "comprei 10 passagens" que justificou o lote no outro
            # tipo). Confirmar chama a MESMA RPC viajai_atualizar_folga
            # que a tela "Confirmar folgas" ja usa.
            for acao in list(propostas_folga):
                _pid = acao["id"]
                _titulo = f"Folga: {acao.get('colaborador_nome') or '?'} → {acao['status_novo']}"
                with st.expander(_titulo, expanded=(len(propostas_folga) == 1)):
                    with st.form(f"form_confirmar_folga_ia_{_pid}"):
                        c_status = st.selectbox(
                            "Status novo", _STATUS_OPCOES,
                            index=(
                                _STATUS_OPCOES.index(acao["status_novo"])
                                if acao["status_novo"] in _STATUS_OPCOES else 1
                            ),
                            key=f"status_folga_{_pid}",
                        )
                        c_tem_saida = st.checkbox(
                            "Informar data de saída real", value=bool(acao.get("data_saida_real")),
                            key=f"tem_saida_folga_{_pid}",
                        )
                        c_saida = None
                        if c_tem_saida:
                            try:
                                _saida_default = (
                                    date.fromisoformat(acao["data_saida_real"])
                                    if acao.get("data_saida_real") else date.today()
                                )
                            except (ValueError, TypeError):
                                _saida_default = date.today()
                            c_saida = st.date_input("Saída real", value=_saida_default, key=f"saida_folga_{_pid}")
                        c_tem_retorno = st.checkbox(
                            "Informar data de retorno real", value=bool(acao.get("data_retorno_real")),
                            key=f"tem_retorno_folga_{_pid}",
                        )
                        c_retorno = None
                        if c_tem_retorno:
                            try:
                                _retorno_default = (
                                    date.fromisoformat(acao["data_retorno_real"])
                                    if acao.get("data_retorno_real") else date.today()
                                )
                            except (ValueError, TypeError):
                                _retorno_default = date.today()
                            c_retorno = st.date_input(
                                "Retorno real", value=_retorno_default, key=f"retorno_folga_{_pid}"
                            )
                        c_motivo = st.text_input(
                            "Motivo (se vendida)", value=acao.get("motivo_venda") or "",
                            key=f"motivo_folga_{_pid}",
                        )
                        col_ok, col_no = st.columns(2)
                        confirmar_folga = col_ok.form_submit_button(
                            "✅ Confirmar e atualizar", use_container_width=True
                        )
                        cancelar_folga = col_no.form_submit_button("Cancelar", use_container_width=True)

                    if confirmar_folga:
                        supabase.rpc("viajai_atualizar_folga", {
                            "p_folga_id": int(acao["folga_id"]),
                            "p_status": c_status,
                            "p_data_saida_real": c_saida.isoformat() if c_saida else None,
                            "p_data_retorno_real": c_retorno.isoformat() if c_retorno else None,
                            "p_motivo_venda": c_motivo or None,
                        }).execute()
                        st.session_state.propostas_pendentes_viajai = [
                            p for p in st.session_state.propostas_pendentes_viajai if p["id"] != _pid
                        ]
                        _resumo_folga_txt = f"{acao.get('colaborador_nome') or '?'}: folga atualizada para {c_status}."
                        st.session_state.mensagens_chat.append({
                            "role": "assistant", "content": _resumo_folga_txt,
                        })
                        supabase.rpc("viajai_salvar_mensagem_chat", {
                            "p_papel": "assistant", "p_conteudo": _resumo_folga_txt,
                        }).execute()
                        _flash("success", _resumo_folga_txt)
                        st.rerun()
                    elif cancelar_folga:
                        st.session_state.propostas_pendentes_viajai = [
                            p for p in st.session_state.propostas_pendentes_viajai if p["id"] != _pid
                        ]
                        st.rerun()

        _registros = st.session_state.get("registros_recentes_viajai", [])
        if _registros:
            for _reg in list(_registros):
                st.success(f"Registrado: {_reg['resumo']}")
                col_undo, col_keep = st.columns(2)
                if col_undo.button("↩️ Desfazer", key=f"btn_desfazer_{_reg['id']}", use_container_width=True):
                    try:
                        supabase.rpc("viajai_apagar_lancamento_rapido", {"p_id": _reg["id"]}).execute()
                        st.session_state.registros_recentes_viajai = [
                            r for r in st.session_state.registros_recentes_viajai if r["id"] != _reg["id"]
                        ]
                        _flash("success", "Desfeito.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Não consegui desfazer (rodou o schema_v0.16 no Supabase?): {e}")
                if col_keep.button("Ok, manter", key=f"btn_manter_{_reg['id']}", use_container_width=True):
                    st.session_state.registros_recentes_viajai = [
                        r for r in st.session_state.registros_recentes_viajai if r["id"] != _reg["id"]
                    ]
                    st.rerun()
        if propostas or _registros:
            st.divider()

        st.caption("Painel — última consulta com dado")
        extra = st.session_state.get("dash_extra_viajai")
        if not extra:
            st.info(
                "Faça uma pergunta que puxe dado (folga, custo, canteiro...) pra ver a "
                "tabela (e mapa, se for canteiro com localização) aqui."
            )
        else:
            resultado = extra.get("resultado")
            if extra.get("tool") == "calcular_diaria_deslocamento" and isinstance(resultado, dict):
                _renderizar_calculo_diaria(resultado)
            elif extra.get("tool") == "consultar_urgencias" and isinstance(resultado, dict):
                _renderizar_urgencias_dash(resultado)
            elif not isinstance(resultado, list) or not resultado:
                st.write(resultado if resultado else "(sem dado pra essa consulta)")
            else:
                _renderizar_tabela_resultado_viajai(extra.get("tool"), pd.DataFrame(resultado))
                _botao_baixar_relatorio_html(extra, key="baixar_relatorio_dash")
                if extra.get("tool") == "consultar_localizacoes_canteiro" and {
                    "latitude", "longitude"
                }.issubset(df_dash.columns):
                    df_mapa = df_dash.dropna(subset=["latitude", "longitude"])
                    if not df_mapa.empty:
                        st.map(df_mapa, latitude="latitude", longitude="longitude", size=15)
                    else:
                        st.caption("Nenhum canteiro com latitude/longitude cadastrada ainda.")

        # NOVO (v9.0, pedido do Rafael 03/09): quadro separado, embaixo do
        # painel de cima, pra quando a pergunta em linguagem natural pedir uma
        # analise/comparacao (a IA pode chamar mais de 1 ferramenta pra montar
        # isso - o painel de cima so guarda a ULTIMA, esse guarda TODAS as
        # consultas da pergunta + o texto que a IA escreveu em cima delas).
        # Fica sempre disponivel (nao exige atalho nem forma especifica de
        # pergunta) porque a ideia e' nao perder um raciocinio elaborado que a
        # IA fizer, mesmo sem saber de antemao que forma ele vai tomar.
        st.divider()
        st.caption("🧩 Análise do assistente (última troca da conversa)")
        analise = st.session_state.get("analise_ia_viajai")
        if not analise or not analise.get("itens"):
            st.info(
                "Peça uma comparação ou análise mais elaborada no chat (ex.: "
                "'compara o gasto de outubro com novembro') pra essa área juntar "
                "os dados e o texto que a IA escreveu aqui, prontos pra virar "
                "relatório."
            )
        else:
            for _item in analise["itens"]:
                _titulo_item = TITULOS_RELATORIO_VIAJAI.get(_item["tool"], _item["tool"])
                st.markdown(f"**{_titulo_item}**")
                _resultado_item = _item.get("resultado")
                if _item["tool"] == "calcular_diaria_deslocamento" and isinstance(_resultado_item, dict):
                    _renderizar_calculo_diaria(_resultado_item)
                elif _item["tool"] == "consultar_urgencias" and isinstance(_resultado_item, dict):
                    _renderizar_urgencias_dash(_resultado_item)
                elif isinstance(_resultado_item, list) and _resultado_item:
                    _renderizar_tabela_resultado_viajai(_item["tool"], pd.DataFrame(_resultado_item))
                else:
                    st.write(_resultado_item if _resultado_item else "(sem dado)")
            _botao_baixar_relatorio_analise_html(analise, key="baixar_analise_ia")

    # chat_input FORA das colunas de proposito - so' assim o Streamlit fixa
    # ele no rodape da pagina (achado 03/09, confirmado na doc oficial:
    # dentro de st.columns ele nao fixa, vira widget comum). Fica largura
    # cheia, embaixo dos 2 paineis.
    pergunta = st.chat_input("Pergunte sobre folgas, urgência, custo...")

    # Mesmo padrao 2 fases do TIA.go (evita bug de ordem visto la ja em
    # producao): grava a pergunta e recarrega antes de chamar a API.
    if pergunta:
        st.session_state.mensagens_chat.append({"role": "user", "content": pergunta})
        supabase.rpc("viajai_salvar_mensagem_chat", {"p_papel": "user", "p_conteudo": pergunta}).execute()
        st.rerun()

    if st.session_state.mensagens_chat and st.session_state.mensagens_chat[-1]["role"] == "user":
        with st.spinner("Consultando..."):
            texto_final = None
            try:
                client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
                # janela deslizante (achado 03/09, ver JANELA_HISTORICO_CHAT no
                # topo do arquivo): sem esse corte, a lista cresce sem limite
                # dentro da sessao (append a cada resposta) e vai inteira pra
                # API em toda pergunta - mais token gasto com o tempo de uso E
                # mais chance do modelo reaproveitar resposta velha em vez de
                # consultar de novo. So corta o que vai pro contexto ativo, o
                # log completo continua salvo no banco pra sempre.
                mensagens_api = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.mensagens_chat[-JANELA_HISTORICO_CHAT:]
                    if isinstance(m["content"], str)
                ]
                system_prompt = _montar_system_prompt_viajai(st.session_state.usuario)

                resposta = client.messages.create(
                    model=MODEL_ID, max_tokens=8192, system=system_prompt,
                    tools=TOOLS_VIAJAI, messages=mensagens_api,
                )
                # Limite de voltas de ferramenta (protecao contra loop
                # longo demais em pergunta com muito calculo/data
                # encadeado - achado 02/09).
                #
                # dash_multi_viajai (novo 03/09, pedido do Rafael: "peço uma
                # comparacao especifica, a ia gera um dash... decido gerar o
                # relatorio mostrando esses dados estudados") - zera a cada
                # pergunta nova e ACUMULA todas as consultas dessa pergunta
                # (nao so a ultima, como dash_extra_viajai faz) - permite um
                # relatorio combinado quando a IA precisa de mais de 1 consulta
                # pra montar uma comparacao/analise.
                st.session_state.dash_multi_viajai = []
                _voltas_ferramenta = 0
                while resposta.stop_reason == "tool_use" and _voltas_ferramenta < 8:
                    _voltas_ferramenta += 1
                    tool_uses = [b for b in resposta.content if b.type == "tool_use"]
                    resultados = []
                    for tu in tool_uses:
                        resultado = _executar_ferramenta_viajai(supabase, tu.name, tu.input)
                        resultados.append(
                            {"type": "tool_result", "tool_use_id": tu.id, "content": str(resultado)}
                        )
                        if tu.name in FERRAMENTAS_VISUAIS_VIAJAI:
                            _item_dash = {
                                "tool": tu.name,
                                "input": tu.input,
                                "resultado": resultado,
                            }
                            st.session_state.dash_extra_viajai = _item_dash
                            st.session_state.dash_multi_viajai.append(_item_dash)
                    mensagens_api.append({"role": "assistant", "content": resposta.content})
                    mensagens_api.append({"role": "user", "content": resultados})
                    resposta = client.messages.create(
                        model=MODEL_ID, max_tokens=8192, system=system_prompt,
                        tools=TOOLS_VIAJAI, messages=mensagens_api,
                    )
                texto_final = "".join(b.text for b in resposta.content if b.type == "text")
                # Achado 02/09 + 03/09: pergunta com bastante calculo as
                # vezes corta a resposta no meio (stop_reason "max_tokens"),
                # e isso pode acontecer com OU sem texto ja escrito ate ali
                # (achado 03/09: um nome saiu cortado no meio da palavra,
                # sem aviso nenhum, porque so' tratava o caso 100% vazio).
                # max_tokens subiu de 4096 pra 8192 e agora qualquer corte
                # por tamanho fica marcado, mesmo com texto parcial.
                if resposta.stop_reason == "max_tokens":
                    if texto_final.strip():
                        texto_final = (
                            texto_final.rstrip()
                            + "\n\n⚠️ *(resposta cortada aqui — pergunta grande demais; "
                            "pergunta em partes menores pra ver o resto)*"
                        )
                    else:
                        texto_final = (
                            "A resposta ficou grande demais e foi cortada antes de começar a "
                            "escrever (pergunta com bastante cálculo/etapa junto). Tenta "
                            "perguntar em partes menores ou de um jeito mais direto."
                        )
                elif not texto_final.strip():
                    if _voltas_ferramenta >= 8:
                        texto_final = (
                            "Essa pergunta precisou de muitas consultas em sequencia e eu parei "
                            "antes de concluir, pra não travar. Tenta quebrar em perguntas menores."
                        )
                    else:
                        texto_final = "Não consegui gerar uma resposta pra essa pergunta — tenta reformular."
            except Exception as e:
                texto_final = f"Erro ao consultar o assistente: {e}"

            # guarda a analise dessa troca (texto + todas as consultas que a IA
            # fez pra chegar nela) pro quadro "Analise do assistente" e pro botao
            # de relatorio combinado - reflete sempre a ULTIMA troca, exportavel
            # antes de perguntar outra coisa (ver gerar_relatorio_analise_html_viajai).
            st.session_state.analise_ia_viajai = {
                "texto": texto_final,
                "itens": _filtrar_dash_multi_viajai(st.session_state.get("dash_multi_viajai", [])),
            }

        st.session_state.mensagens_chat.append({"role": "assistant", "content": texto_final})
        supabase.rpc("viajai_salvar_mensagem_chat", {"p_papel": "assistant", "p_conteudo": texto_final}).execute()
        st.rerun()

def pagina_urgencias(supabase):
    st.title("Urgências — Viaj.AI")
    st.caption(
        "Painel de alerta - pedido do Rafael 04/09 pensando como gestor de "
        "logística/compras: nada aqui precisa de pergunta no chat, já vem "
        "cruzado direto."
    )

    # v21.2 (schema_v0.35, pedido do Rafael 09/09: "vincular as urgências
    # tb com o histórico de import, é possível?") - as 2 RPCs de folga
    # (sem passagem / pra revisar) ja trazem import_batch_id/nome_arquivo_
    # origem/import_criado_em/nome_planilha_origem prontos (join feito no
    # banco); aqui so' formata num texto so' pra ficar legivel, mesmo
    # padrao "Origem do import" ja usado em Confirmar folgas (schema_v0.33).
    def _fmt_origem_urgencia(row):
        if pd.isna(row.get("nome_arquivo_origem")):
            return "— (sem import registrado)"
        data_txt = ""
        if pd.notna(row.get("import_criado_em")):
            try:
                data_txt = f" em {str(row['import_criado_em'])[:10]}"
            except Exception:
                data_txt = ""
        nome_txt = ""
        if pd.notna(row.get("nome_planilha_origem")) and row["nome_planilha_origem"]:
            nome_txt = f" (\"{row['nome_planilha_origem']}\" na planilha)"
        return f"{row['nome_arquivo_origem']}{data_txt}{nome_txt}"

    _HELP_ORIGEM_IMPORT = (
        "De qual import RE090 (arquivo + data) essa folga veio, e o nome "
        "exatamente como veio na planilha (schema_v0.35). '—' = folga sem "
        "import associado (criada antes da rastreabilidade ou por outro caminho)."
    )

    # NOVO schema_v0.40 (Caminho A, confirmado pelo Rafael 10/09: "2. sim
    # vamos deixar por 60 dias por enquanto") - substitui o antigo botao
    # "Resolvida" de pendencia por um alerta baseado em tempo: folga sem
    # vinculo com RH nunca fica esquecida pra sempre, so' vira alerta aqui
    # depois de N dias. Acao (vincular manual/automatico) fica centralizada
    # em Importar RE090, pra nao duplicar a mesma escrita em 2 telas.
    st.subheader("⏳ Folgas aguardando vínculo com RH há mais de 60 dias")
    st.caption(
        "Nome provisório (import ou lançamento manual) que passou de 60 dias "
        "sem achar match único no RH — não travou nada até aqui, mas merece "
        "revisar (RH ainda não cadastrou a pessoa? nome está errado? pessoa "
        "não existe mesmo?). Vincular manual ou tentar automático fica na "
        "página **Importar RE090**."
    )
    try:
        r0 = supabase.rpc("viajai_folgas_sem_vinculo_rh", {"p_dias": 60}).execute()
        if r0.data:
            st.dataframe(
                pd.DataFrame(r0.data),
                column_order=[
                    "folga_id", "nome_provisorio", "obra_texto_provisorio",
                    "origem_criacao", "status", "data_saida_prevista", "dias_sem_vinculo",
                ],
                column_config={
                    "folga_id": st.column_config.NumberColumn("🔒 Nº", format="%d"),
                    "nome_provisorio": st.column_config.TextColumn("🔒 Nome (provisório)"),
                    "obra_texto_provisorio": st.column_config.TextColumn("🔒 Obra/canteiro (texto)"),
                    "origem_criacao": st.column_config.TextColumn(
                        "🔒 Origem", help="re090 = veio de import de planilha; manual = lançada direto na tela.",
                    ),
                    "status": st.column_config.TextColumn("🔒 Status"),
                    "data_saida_prevista": st.column_config.DateColumn("🔒 Saída prevista"),
                    "dias_sem_vinculo": st.column_config.NumberColumn("🔒 Dias sem vínculo"),
                },
                use_container_width=True, hide_index=True, placeholder="",
            )
        else:
            st.success("Nenhuma folga passou de 60 dias sem vínculo com RH.")
    except Exception as e:
        st.error(f"Não consegui consultar (rodou o schema_v0.40 no Supabase?) — {e}")

    st.divider()
    st.subheader("🚨 Folgas chegando sem passagem lançada")
    st.caption(
        "O que fazer: lance a passagem em **Custo & Passagens** (aba "
        "'Lançamento rápido' ou 'Por folga'). Assim que existir um "
        "lançamento pra essa pessoa, ela some sozinha dessa lista — não "
        "tem botão de resolver aqui."
    )
    try:
        r1 = supabase.rpc("viajai_folgas_sem_passagem", {"p_dias_janela": 10}).execute()
        if r1.data:
            df1 = pd.DataFrame(r1.data)
            df1["origem_import"] = df1.apply(_fmt_origem_urgencia, axis=1)
            df1["nome"] = df1.apply(
                lambda r: (f"⏳ {r['nome']}" if r.get("aguardando_vinculo_rh") else r["nome"]), axis=1,
            )
            st.dataframe(
                df1,
                column_order=[
                    "nome", "obra_nome", "canteiro_nome",
                    "data_saida_prevista", "dias_restantes", "origem_import",
                ],
                column_config={
                    "nome": st.column_config.TextColumn("🔒 Nome"),
                    "obra_nome": st.column_config.TextColumn("🔒 Obra"),
                    "canteiro_nome": st.column_config.TextColumn("🔒 Canteiro"),
                    "data_saida_prevista": st.column_config.DateColumn("🔒 Saída prevista"),
                    "dias_restantes": st.column_config.NumberColumn(
                        "🔒 Dias restantes",
                        help="Negativo = já passou da data prevista de saída — mais urgente.",
                    ),
                    "origem_import": st.column_config.TextColumn(
                        "🔒 Origem do import", help=_HELP_ORIGEM_IMPORT,
                    ),
                },
                use_container_width=True, hide_index=True, placeholder="",
            )
        else:
            st.success("Nenhuma folga nos próximos 10 dias sem passagem lançada.")
    except Exception as e:
        st.error(f"Não consegui consultar (rodou o schema_v0.24 no Supabase?) — {e}")

    st.divider()
    st.subheader("💸 Preços fora do padrão da rota")
    st.caption(
        "Só informativo — não tem 'resolver' aqui. Serve pra revisar se o "
        "valor faz sentido (erro de digitação, rota atípica) e, se for o "
        "caso, corrigir o lançamento em Custo & Passagens."
    )
    try:
        r2 = supabase.rpc(
            "viajai_alerta_preco_fora_padrao", {"p_dias_janela": 30, "p_desvio_pct": 0.4}
        ).execute()
        if r2.data:
            df2 = pd.DataFrame(r2.data)
            df2["desvio_pct"] = df2["desvio_pct"] * 100
            st.dataframe(
                df2,
                column_order=[
                    "data", "colaborador_nome", "origem", "destino",
                    "valor_unitario", "media_rota", "desvio_pct", "amostras_rota",
                ],
                column_config={
                    "data": st.column_config.DateColumn("🔒 Data"),
                    "colaborador_nome": st.column_config.TextColumn("🔒 Colaborador"),
                    "origem": st.column_config.TextColumn("🔒 Origem"),
                    "destino": st.column_config.TextColumn("🔒 Destino"),
                    "valor_unitario": st.column_config.NumberColumn("🔒 Valor pago (R$)", format="R$ %.2f"),
                    "media_rota": st.column_config.NumberColumn("🔒 Média da rota (R$)", format="R$ %.2f"),
                    "desvio_pct": st.column_config.NumberColumn(
                        "🔒 Desvio", format="%.0f%%",
                        help="Quanto esse valor está acima/abaixo da média histórica da mesma rota.",
                    ),
                    "amostras_rota": st.column_config.NumberColumn(
                        "🔒 Amostras da rota", help="Quantos lançamentos dessa rota entraram na média.",
                    ),
                },
                use_container_width=True, hide_index=True, placeholder="",
            )
        else:
            st.success("Nenhum lançamento recente fora do padrão histórico da rota (desvio ≥ 40%).")
    except Exception as e:
        st.error(f"Não consegui consultar (rodou o schema_v0.24 no Supabase?) — {e}")

    st.divider()
    st.subheader("↩️ Passagem vinculada a folga vendida/cancelada")
    st.caption(
        "Candidatas a revisar estorno/crédito com a companhia — tanto lançada em "
        "'Lançamento rápido' (Custo & Passagens) quanto na aba 'Por folga', desde que "
        "vinculada à folga. Marque como 'revisada' quando resolver — o item some dessa "
        "lista (não acumula pendência), mas o registro fica guardado pra sempre em "
        "**Histórico de revisões** embaixo, com quem revisou e o resultado — dá pra "
        "somar por mês depois (ex.: quanto se perdeu em passagem não aproveitada)."
    )
    try:
        r3 = supabase.rpc("viajai_folga_passagem_para_revisar").execute()
        if r3.data:
            df_revisar = pd.DataFrame(r3.data)
            df_revisar["origem_import"] = df_revisar.apply(_fmt_origem_urgencia, axis=1)
            df_revisar["nome"] = df_revisar.apply(
                lambda r: (f"⏳ {r['nome']}" if r.get("aguardando_vinculo_rh") else r["nome"]), axis=1,
            )
            st.dataframe(
                df_revisar,
                column_order=[
                    "nome", "status_folga", "motivo_venda", "fonte",
                    "lancamento_id", "trecho_id", "data", "valor",
                    "origem", "destino", "origem_import",
                ],
                column_config={
                    "nome": st.column_config.TextColumn("🔒 Nome"),
                    "status_folga": st.column_config.TextColumn("🔒 Status da folga"),
                    "motivo_venda": st.column_config.TextColumn("🔒 Motivo (se vendida)"),
                    "fonte": st.column_config.TextColumn(
                        "🔒 Fonte",
                        help="lancamento_rapido = lançado em Custo & Passagens > Lançamento rápido; "
                             "por_folga = lançado em Custo & Passagens > Por folga.",
                    ),
                    "lancamento_id": st.column_config.NumberColumn("🔒 Lançamento nº", format="%d"),
                    "trecho_id": st.column_config.NumberColumn("🔒 Trecho nº", format="%d"),
                    "data": st.column_config.DateColumn("🔒 Data"),
                    "valor": st.column_config.NumberColumn("🔒 Valor (R$)", format="R$ %.2f"),
                    "origem": st.column_config.TextColumn("🔒 Origem"),
                    "destino": st.column_config.TextColumn("🔒 Destino"),
                    "origem_import": st.column_config.TextColumn(
                        "🔒 Origem do import", help=_HELP_ORIGEM_IMPORT,
                    ),
                },
                use_container_width=True, hide_index=True, placeholder="",
            )

            # v20.0: a lista agora mistura 2 fontes (fonte='lancamento_rapido'
            # ou 'por_folga', schema_v0.32) - o rotulo usa o id da fonte certa
            # (lancamento_id ou trecho_id) e o "marcar revisada" abaixo manda
            # o parametro certo pra RPC de acordo com a fonte da linha
            # escolhida (nunca os 2, nunca nenhum - a RPC valida isso tambem).
            df_revisar["_rotulo"] = df_revisar.apply(
                lambda r: (
                    f"#{r['trecho_id'] if r['fonte'] == 'por_folga' else r['lancamento_id']} "
                    f"({'Por folga' if r['fonte'] == 'por_folga' else 'Lançamento rápido'}) — "
                    f"{r['nome']} — {r['origem']} -> {r['destino']} — R$ {r['valor']:.2f} — "
                    f"folga {r['status_folga']}"
                ),
                axis=1,
            )
            with st.form("form_marcar_revisada"):
                st.write("Marcar como revisada")
                rotulo_rev = st.selectbox("Qual passagem?", df_revisar["_rotulo"], key="rev_select")
                resultado_rev = st.selectbox(
                    "Resultado",
                    ["estorno_solicitado", "credito_recebido", "sem_acao_necessaria", "outro"],
                    key="rev_resultado",
                    help=(
                        "estorno_solicitado = pediu o dinheiro de volta pra companhia; "
                        "credito_recebido = ganhou crédito pra usar depois; "
                        "sem_acao_necessaria = revisou e não precisa fazer nada; "
                        "outro = explica na observação."
                    ),
                )
                obs_rev = st.text_input("Observação (opcional)", key="rev_obs")
                enviar_rev = st.form_submit_button("Marcar revisada")
            if enviar_rev:
                _linha_rev = df_revisar.loc[df_revisar["_rotulo"] == rotulo_rev].iloc[0]
                _params_rev = {"p_resultado": resultado_rev, "p_observacao": obs_rev or None}
                if _linha_rev["fonte"] == "por_folga":
                    _params_rev["p_trecho_id"] = int(_linha_rev["trecho_id"])
                else:
                    _params_rev["p_lancamento_id"] = int(_linha_rev["lancamento_id"])
                try:
                    supabase.rpc("viajai_marcar_passagem_revisada", _params_rev).execute()
                    _flash("success", "Marcada como revisada — guardada no histórico.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao marcar como revisada: {e}")
        else:
            st.success("Nenhuma passagem vinculada a folga vendida/cancelada pendente de revisão.")
    except Exception as e:
        st.error(f"Não consegui consultar (rodou o schema_v0.32 no Supabase?) — {e}")

    with st.expander("🔗 Vincular lançamento existente a uma folga (retroativo)"):
        st.caption(
            "Pra quando a passagem já foi registrada em 'Lançamento rápido' sem apontar "
            "a folga na hora — vincula depois pra ela aparecer em 'Passagem pra revisar' "
            "acima, se/quando a folga for vendida ou cancelada. Só lançamentos com "
            "colaborador real (não provisório) e ainda sem folga vinculada aparecem aqui; "
            "só folga já vendida/cancelada do MESMO colaborador do lançamento pode ser "
            "escolhida (a RPC confere isso também)."
        )
        try:
            _lancs_todos_v = supabase.rpc("viajai_listar_lancamentos_rapidos", {"p_limite": 300}).execute().data or []
            _lancs_sem_folga_v = [
                l for l in _lancs_todos_v if not l.get("folga_id") and l.get("colaborador_id")
            ]
            _folgas_fechadas_v = supabase.rpc("viajai_listar_folgas_fechadas", {"p_limite": 300}).execute().data or []
            if not _lancs_sem_folga_v:
                st.caption("Nenhum lançamento (com colaborador real) sem folga vinculada no momento.")
            elif not _folgas_fechadas_v:
                st.caption("Nenhuma folga vendida/cancelada no momento.")
            else:
                _opcoes_lanc_v = {
                    (
                        f"#{l['id']} — {l.get('colaborador_nome') or '—'} — {l['origem']} -> "
                        f"{l['destino']} — R$ {l['valor_total']:.2f} ({l['data']})"
                    ): l["id"]
                    for l in _lancs_sem_folga_v
                }
                _opcoes_folga_v = {
                    f"#{f['folga_id']} — {f['nome']} — {f['status']}": f["folga_id"]
                    for f in _folgas_fechadas_v
                }
                with st.form("form_vincular_lancamento_folga"):
                    lanc_v = st.selectbox("Lançamento", list(_opcoes_lanc_v.keys()), key="vinc_lanc")
                    folga_v = st.selectbox("Folga vendida/cancelada", list(_opcoes_folga_v.keys()), key="vinc_folga")
                    enviar_v = st.form_submit_button("Vincular")
                if enviar_v:
                    try:
                        supabase.rpc("viajai_vincular_lancamento_folga", {
                            "p_lancamento_id": _opcoes_lanc_v[lanc_v],
                            "p_folga_id": _opcoes_folga_v[folga_v],
                        }).execute()
                        _flash("success", "Lançamento vinculado à folga — já aparece em 'Passagem pra revisar' acima.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao vincular: {e}")
        except Exception as e:
            st.error(f"Não consegui consultar (rodou o schema_v0.32 no Supabase?) — {e}")

    with st.expander("📜 Histórico de revisões (nunca apagado)"):
        st.caption(
            "Toda revisão marcada acima fica registrada aqui pra sempre — "
            "quem revisou, quando e o resultado. Base pra olhar padrão por "
            "mês depois (ex.: quanto se perdeu em passagem não aproveitada)."
        )
        try:
            r3h = supabase.rpc("viajai_listar_revisoes_passagem", {"p_limite": 200}).execute()
            if r3h.data:
                df_hist_rev = pd.DataFrame(r3h.data)
                st.dataframe(
                    df_hist_rev,
                    column_order=[
                        "revisado_em", "colaborador_nome", "resultado", "observacao",
                        "fonte", "lancamento_id", "trecho_id", "origem", "destino",
                        "valor", "revisado_por",
                    ],
                    column_config={
                        "revisado_em": st.column_config.DatetimeColumn("🔒 Revisado em"),
                        "colaborador_nome": st.column_config.TextColumn("🔒 Colaborador"),
                        "resultado": st.column_config.TextColumn("🔒 Resultado"),
                        "observacao": st.column_config.TextColumn("🔒 Observação"),
                        "fonte": st.column_config.TextColumn("🔒 Fonte"),
                        "lancamento_id": st.column_config.NumberColumn("🔒 Lançamento nº", format="%d"),
                        "trecho_id": st.column_config.NumberColumn("🔒 Trecho nº", format="%d"),
                        "origem": st.column_config.TextColumn("🔒 Origem"),
                        "destino": st.column_config.TextColumn("🔒 Destino"),
                        "valor": st.column_config.NumberColumn("🔒 Valor (R$)", format="R$ %.2f"),
                        "revisado_por": st.column_config.TextColumn("🔒 Revisado por"),
                    },
                    use_container_width=True, hide_index=True, placeholder="",
                )
                _botao_exportar_excel(df_hist_rev, "viajai_historico_revisoes_passagem.xlsx")
            else:
                st.caption("Nenhuma revisão registrada ainda.")
        except Exception as e:
            st.error(f"Não consegui consultar (rodou o schema_v0.29 no Supabase?) — {e}")

    st.divider()
    st.subheader("🪵 Últimos erros registrados")
    st.caption(
        "Erros do Assistente (chat) ficam gravados aqui desde o schema_v0.25 - "
        "pedido do Rafael 04/09 pensando em uso por terceiros: se algo der "
        "errado, dá pra investigar depois em vez de perder o erro na hora. "
        "Não precisa 'resolver' nada aqui — é só histórico."
    )
    try:
        r4 = supabase.rpc("viajai_listar_log_erro", {"p_limite": 20}).execute()
        if r4.data:
            st.dataframe(
                pd.DataFrame(r4.data),
                column_order=["criado_em", "ferramenta", "mensagem_erro", "usuario", "contexto", "entrada"],
                column_config={
                    "criado_em": st.column_config.DatetimeColumn("🔒 Quando"),
                    "ferramenta": st.column_config.TextColumn("🔒 Ferramenta"),
                    "mensagem_erro": st.column_config.TextColumn("🔒 Erro"),
                    "usuario": st.column_config.TextColumn("🔒 Usuário"),
                    "contexto": st.column_config.TextColumn("🔒 Contexto"),
                    "entrada": st.column_config.TextColumn("🔒 Entrada (dados)"),
                },
                use_container_width=True, hide_index=True, placeholder="",
            )
        else:
            st.success("Nenhum erro registrado.")
    except Exception as e:
        st.error(f"Não consegui consultar (rodou o schema_v0.25 no Supabase?) — {e}")


def pagina_ajuda():
    st.title("Central de Ajuda — Viaj.AI")
    st.markdown(
        """
### Fluxo geral
1. **Importar RE090** — carrega os dados de folga/deslocamento da planilha oficial pro banco. Sem match 1:1 com o RH, a folga é criada mesmo assim (não trava nada), com o selo "⏳ aguardando vínculo com RH" e nome provisório — dá pra vincular na mesma tela (manual, escolhendo o colaborador certo) ou clicar **"Tentar vincular automaticamente"** quando o RH cadastrar/ativar a pessoa; passado 60 dias sem vincular, vira alerta em Urgências. Também dá pra **adicionar folga manualmente** (sem esperar planilha) na mesma página, pra demanda emergencial.
2. **Confirmar folgas** — atualiza folga em aberto (status "prevista", "confirmada" ou "em_andamento") pra "confirmada" (data marcada, ainda não saiu), "em_andamento" (já saiu), "realizada" (já voltou), "vendida" (converteu os dias em pagamento, não saiu) ou "cancelada" — inclusive folga que já tinha passagem comprada e depois foi vendida/cancelada.
3. **Previsão de folgas** — mostra quando cada colaborador sai de folga.
4. **Custo & Passagens** — lançamento e histórico de compra de passagem. Aba "Por folga": adiciona trecho por trecho de uma mesma viagem (reenviar com o mesmo "Sentido" empilha na MESMA viagem, não cria outra) e dá pra marcar/desfazer reembolso de um trecho (some do gasto real, sem apagar o preço original). Aba "Lançamento rápido": dá pra registrar sem apontar colaborador (mesmo sem o RH ter a pessoa ainda) usando um nome provisório, e depois **atribuir o colaborador real** quando o RH subir — o app já sugere o match pelo nome; também dá pra **vincular a uma folga específica** (opcional, tela e chat) — é o que faz essa passagem aparecer em "Passagem pra revisar" (Urgências) se a folga for vendida/cancelada depois.
5. **Dashboard** — todas as métricas agregadas num só lugar: custo por mês, custo por obra, sazonalidade de folga, delay de envio do RE090, prazo de compra de passagem, e o desvio de planejamento (previsto x real, com e sem custo cruzado).
6. **Urgências** — alertas: folga aguardando vínculo com RH há mais de 60 dias, folga chegando sem passagem lançada, preço fora do padrão da rota, passagem pra revisar (folga vendida/cancelada depois de já comprada — cobre passagem lançada tanto em "Lançamento rápido" quanto em "Por folga", desde que vinculada à folga; dá pra marcar como revisada, fica guardado num histórico permanente; e dá pra vincular um lançamento antigo "solto" a uma folga retroativamente), e os últimos erros registrados pelo sistema.
7. **Viaj.AI** — chat que consulta e propõe ações nas telas acima. Nunca grava sozinho.

### O que o Assistente pode / não pode fazer
**Pode (com sua confirmação antes de gravar):**
- Lançar rapidamente uma compra de passagem
- Propor atualização de status de folga (saída/retorno real, vendida, cancelada)

**Só consulta (nunca grava):**
- Previsão de folga e de gasto
- Link do Skyscanner e ClickBus (nunca inventa preço)
- Distância/tempo de carro (Google Maps)
- Cálculo de diária de deslocamento (dias x valor fixo por tipo, fórmula simples)
- Resumo de urgências (mesma lógica da aba "Urgências")
- Pendências de import (lista, mas não reprocessa — isso é só na tela)
- Histórico de imports (quando, quantas folgas criou, quantas pendência por upload)

**Não faz (ainda) — só pela tela mesmo:**
- Cadastrar colaborador novo — use a tela de cadastro do RH
- Fórmula avançada de diária (pernoite, arredondamento) — usa fórmula simples por ora
- Reprocessar pendências de import (botão na tela "Importar RE090")
- Atribuir colaborador retroativo a um lançamento rápido (expander na aba "Lançamento rápido")
- Marcar passagem como revisada (formulário na aba "Urgências", seção "Passagem pra revisar")
- Vincular um lançamento antigo a uma folga retroativamente (expander na aba "Urgências")
- Marcar/desfazer reembolso de um trecho (expander na aba "Por folga", dentro de "Custo & Passagens")

### Regra de ouro
Você pede → o Assistente monta a proposta no painel lateral → **nada é gravado até você confirmar na tela**.
Passagem comprada e folga são registros independentes — uma não abre/fecha a outra.

### Frases-modelo
- "Lança uma passagem de R$[valor], [origem] pra [destino], colaborador [nome], dia [data]"
- "[Nome] retornou de folga dia [data], atualiza pra mim"
- "[Nome] vendeu a folga" / "cancela a folga do [nome]"
- "Qual a previsão de gasto do [colaborador/canteiro/obra]?"
- "Calcula a diária de deslocamento do [nome], [N] dias, tipo [folga/admissão-demissão]"
- "Me dá o link do ClickBus/Skyscanner pra rota [origem]-[destino]"

### Mensagens que confundem mas não são erro
- **"Não achei nenhuma folga em aberto (prevista/confirmada/em_andamento)"** → normal, não existe folga em aberto esperando ação pra esse colaborador agora. Vá em "Confirmar folgas" direto.
- **Quadro vermelho / "postgrest.exceptions.APIError"** → esse sim é erro real de sistema. Reporte a hora exata pro suporte.
        """
    )


def _rpc_dash_ou_vazio(supabase, nome_rpc, params):
    """Helper so' pro Dashboard (schema_v0.34): RPC de leitura que pode
    ainda nao existir (schema_v0.34 nao rodado) ou nao ter dado nenhum -
    nos 2 casos, degrada pra lista vazia em vez de quebrar a tela."""
    try:
        resp = supabase.rpc(nome_rpc, params).execute()
        return resp.data or []
    except Exception:
        return []


def pagina_dashboard(supabase):
    st.subheader("Dashboard")
    st.caption(
        "Métricas de custo e comportamento ao longo do tempo — evolui "
        "sozinho conforme a base populate com uso real (schema_v0.34). "
        "Com pouco dado (ex.: logo após a entrega, base zerada), os "
        "gráficos aparecem vazios — normal, não é erro."
    )

    p_meses = st.selectbox(
        "Período", [3, 6, 12, 24], index=2,
        format_func=lambda n: f"Últimos {n} meses",
    )

    st.divider()
    st.markdown("### 💰 Custo por mês")
    st.caption("Soma passagem (líquida de reembolso) + gasto extra + lançamento rápido.")
    dados = _rpc_dash_ou_vazio(supabase, "viajai_dash_custo_mensal", {"p_meses": p_meses})
    if dados:
        df = pd.DataFrame(dados)
        st.bar_chart(df.set_index("mes")[["custo_passagens", "custo_gastos", "custo_lancamento_rapido"]])
        _botao_exportar_excel(df, "viajai_dash_custo_mensal.xlsx")
    else:
        st.caption("Ainda não há dado suficiente nesse período.")

    st.divider()
    st.markdown("### 🏗️ Custo por obra")
    st.caption(
        "Passagem/gasto lançados em 'Por folga' usam a obra de quando a "
        "folga aconteceu. 'Lançamento rápido' sem folga vinculada usa a "
        "obra ATUAL do colaborador no RH — pode errar se ele trocou de "
        "obra depois do gasto."
    )
    dados = _rpc_dash_ou_vazio(supabase, "viajai_dash_custo_por_obra", {"p_meses": p_meses})
    if dados:
        df = pd.DataFrame(dados)
        st.bar_chart(df.set_index("obra_nome")[["custo_total"]])
        _botao_exportar_excel(df, "viajai_dash_custo_por_obra.xlsx")
    else:
        st.caption("Ainda não há dado suficiente nesse período.")

    st.divider()
    st.markdown("### 📅 Sazonalidade — quantidade de folga por mês")
    dados = _rpc_dash_ou_vazio(supabase, "viajai_dash_sazonalidade_folga", {"p_meses": p_meses})
    if dados:
        df = pd.DataFrame(dados)
        st.bar_chart(df.set_index("mes")[["quantidade"]])
        _botao_exportar_excel(df, "viajai_dash_sazonalidade_folga.xlsx")
    else:
        st.caption("Ainda não há dado suficiente nesse período.")

    st.divider()
    st.markdown("### ⏱️ Delay de envio do RE090, por obra")
    st.caption(
        "Dias entre a data em que a folga precisava ser informada (saída "
        "prevista) e a data em que o import RE090 chegou. Só conta folga "
        "criada por import — lançada manualmente não tem 'envio de "
        "planilha' pra medir."
    )
    dados = _rpc_dash_ou_vazio(supabase, "viajai_dash_delay_envio_re090", {"p_meses": p_meses})
    if dados:
        df = pd.DataFrame(dados)
        st.bar_chart(df.set_index("obra_nome")[["delay_medio_dias"]])
        st.dataframe(df, hide_index=True, use_container_width=True, placeholder="")
        _botao_exportar_excel(df, "viajai_dash_delay_envio.xlsx")
    else:
        st.caption("Ainda não há dado suficiente nesse período.")

    st.divider()
    st.markdown("### ✈️ Prazo de compra de passagem")
    st.caption(
        "Dias de antecedência entre a compra e a data da viagem. Só "
        "considera passagem lançada em 'Por folga' (tem campo de data de "
        "compra) — 'Lançamento rápido' não tem esse dado."
    )
    dados = _rpc_dash_ou_vazio(supabase, "viajai_dash_prazo_compra_passagem", {"p_meses": p_meses})
    if dados:
        df = pd.DataFrame(dados)
        st.line_chart(df.set_index("mes")[["prazo_medio_dias"]])
        _botao_exportar_excel(df, "viajai_dash_prazo_compra.xlsx")
    else:
        st.caption("Ainda não há dado suficiente nesse período.")

    # Reorganização 10/09: os 2 quadros de "desvio de planejamento" viviam
    # espalhados (um em Previsão de folgas, outro em Custo & Passagens) -
    # pedido do Rafael pra concentrar tudo que é "olhar métrica" aqui no
    # Dashboard. Não usa o filtro de período (p_meses) acima porque as RPCs
    # de origem (viajai_listar_folgas_desvio / viajai_comparativo_custo_folga)
    # sempre trabalharam só com p_limite, sem filtro de mês - mantido assim
    # pra não mudar a RPC nem o schema.
    st.divider()
    st.markdown("### 📆 Desvio de planejamento — previsto x real")
    st.caption(
        "Prevista x real, só datas. Positivo = atrasou em relação ao "
        "previsto; negativo = antecipou."
    )
    desvio = supabase.rpc("viajai_listar_folgas_desvio", {"p_limite": 200}).execute()
    if desvio.data:
        df_desvio = pd.DataFrame(desvio.data)
        st.dataframe(df_desvio, use_container_width=True, hide_index=True, placeholder="")
        _botao_exportar_excel(df_desvio, "viajai_desvio_planejamento.xlsx")
    else:
        st.caption("Nenhuma folga confirmada/realizada ainda pra comparar.")

    st.divider()
    st.markdown("### 💳 Comparativo de custo x desvio de planejamento")
    st.caption(
        "Mesma comparação acima, cruzada com o custo real (passagem + "
        "gastos) de cada folga."
    )
    comp = supabase.rpc("viajai_comparativo_custo_folga", {"p_limite": 200}).execute()
    if comp.data:
        df_comp = pd.DataFrame(comp.data)
        st.dataframe(df_comp, hide_index=True, use_container_width=True, placeholder="")
        _botao_exportar_excel(df_comp, "viajai_comparativo_custo.xlsx")
    else:
        st.caption("Nenhum custo registrado ainda pra comparar com o desvio de planejamento.")


def main():
    if "sessao" not in st.session_state:
        tela_login()
        return

    # Reanexa o token a cada rerun (padrão TIA.go — Streamlit recria o
    # cliente do zero a cada interação, sem isso a consulta vai como anônimo
    # e a RLS devolve vazio sem erro nenhum).
    supabase = get_client()

    # NOVO 09/09/2026 (achado testando com o Rafael - tela vermelha generica
    # em "Assistente" E "Confirmar folgas" apos uso prolongado): access_token
    # e' um JWT com validade curta (padrao Supabase Auth, geralmente ~1h) -
    # sem refresh, toda chamada RPC em QUALQUER pagina passa a falhar com
    # "JWT expired" (postgrest APIError code PGRST303) depois de logado por
    # muito tempo, nao tem nada a ver com o que a pessoa esta fazendo no chat
    # ou em qualquer tela especifica. Refresh proativo usando o
    # refresh_token antes do access_token expirar (60s de folga).
    _expira_em_viajai = getattr(st.session_state.sessao, "expires_at", None)
    if _expira_em_viajai and time.time() > _expira_em_viajai - 60:
        try:
            _nova_sessao_viajai = supabase.auth.refresh_session(
                st.session_state.sessao.refresh_token
            )
            if _nova_sessao_viajai.session:
                st.session_state.sessao = _nova_sessao_viajai.session
        except Exception:
            pass  # refresh falhou - segue com o token atual, se ainda for
            # o problema a proxima RPC que falhar vai indicar de novo

    supabase.postgrest.auth(st.session_state.sessao.access_token)

    with st.sidebar:
        render_logo(height=56)
        st.write(f"Logado como: {st.session_state.usuario}")
        pagina = st.radio(
            "Navegação",
            ["Importar RE090", "Confirmar folgas", "Urgências", "Previsão de folgas", "Custo & Passagens", "Dashboard", "Central de Ajuda", "Viaj.AI"],
        )
        if st.button("Sair"):
            supabase.auth.sign_out()
            del st.session_state.sessao
            st.rerun()
        # rodape de versao/contato (pedido do Rafael 03/09: "anotar a versao
        # e contato pra manter atualizando conforme evolucao", ajustado 04/09
        # "ta grudado em cima" -> position:fixed manda pro rodape de verdade
        # da sidebar. Ajustado de novo 04/09 "ficou cruzado" - no Streamlit
        # Cloud o proprio app injeta uma barra cinza no rodape da sidebar
        # (com "Manage app"), que colidia com o texto numa linha so'. Subido
        # pra bottom:45px (fica acima dessa barra) e quebrado em linhas
        # empilhadas, largura estreita, pra caber na coluna cinza sem cruzar.
        st.markdown(
            f"""
            <div style='position: fixed; bottom: 45px; left: 12px; max-width: 220px;
                        font-size: 0.75rem; color: gray; line-height: 1.35;'>
            <div>{VERSAO_EXIBIDA}</div>
            <div>dúvidas/manutenção:</div>
            <div>{CONTATO_SUPORTE}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    _renderizar_flash()

    if pagina == "Importar RE090":
        pagina_importar_re090(supabase)
    elif pagina == "Confirmar folgas":
        pagina_confirmar_folgas(supabase)
    elif pagina == "Urgências":
        pagina_urgencias(supabase)
    elif pagina == "Previsão de folgas":
        pagina_previsao(supabase)
    elif pagina == "Custo & Passagens":
        pagina_custo_passagens(supabase)
    elif pagina == "Dashboard":
        pagina_dashboard(supabase)
    elif pagina == "Central de Ajuda":
        pagina_ajuda()
    elif pagina == "Viaj.AI":
        pagina_chat(supabase)


if __name__ == "__main__":
    main()
