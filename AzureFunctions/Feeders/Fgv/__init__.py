import logging
import time
import ssl
import requests
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from config import DADPUBAPI_FGV_USER, DADPUBAPI_FGV_PASSWORD

BASE_URL = "https://extra-ibre.fgv.br/ibre/sitefgvdados"
AUTH_URL = "https://autenticacao-ibre.fgv.br"


class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers("DEFAULT:@SECLEVEL=1")
        if hasattr(ssl, "OP_LEGACY_SERVER_CONNECT"):
            ctx.options |= ssl.OP_LEGACY_SERVER_CONNECT
        ctx.minimum_version = ssl.TLSVersion.TLSv1
        kwargs["ssl_context"] = ctx
        return super().init_poolmanager(*args, **kwargs)


def _extract_viewstate(html):
    soup = BeautifulSoup(html, "html.parser")
    vs = soup.find("input", {"id": "__VIEWSTATE"})["value"]
    vsg = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"]
    return vs, vsg


def _authenticate():
    session = requests.Session()
    session.get(f"{AUTH_URL}/ProdutosDigitais/Login", timeout=30)

    url = f"{AUTH_URL}/ProdutosDigitais/screenservices/ProdutosDigitais/Blocks/BL01_Login/DataActionGET_Dados"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": AUTH_URL,
        "Referer": f"{AUTH_URL}/ProdutosDigitais/Login",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/142.0.0.0 Safari/537.36",
        "X-CSRFToken": "T6C+9iB49TLra4jEsMeSckDMNhQ=",
    }
    data = {
        "versionInfo": {
            "moduleVersion": "A9DvXpRHtWt57+mijPBfsg",
            "apiVersion": "eZh6ZQgjDiHTkxmj7q6svQ",
        },
        "viewName": "MainFlow.Login",
        "screenData": {
            "variables": {
                "DS_Login": DADPUBAPI_FGV_USER,
                "DS_Password": DADPUBAPI_FGV_PASSWORD,
                "FLG_ExibirSenha": False,
                "MSG_Erro": "",
                "Prompt_Login": "",
                "Prompt_Senha": "",
                "FLG_PopupAtivarConta": False,
                "Loading": True,
                "FLG_AtivacaoCadastro": False,
                "MSG_AtivacaoCadastro": "",
                "WidgetIdFlare": "b4-b3-CfTurnstile",
                "FLG_ativarConta": False,
                "_fLG_ativarContaInDataFetchStatus": 1,
                "token": "",
                "_tokenInDataFetchStatus": 1,
                "Email": "",
                "_emailInDataFetchStatus": 1,
            }
        },
        "clientVariables": {"RL_Produtos": "", "NM_Usuario": ""},
    }

    response = session.post(url, headers=headers, json=data, timeout=30)
    if response.status_code != 200:
        raise Exception(f"Auth failed: {response.status_code}")

    url_gratuito = response.json().get("data", {}).get("URL_Gratuito")
    if not url_gratuito:
        raise Exception("URL_Gratuito not found in response")

    session.mount("https://", TLSAdapter())
    ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/142.0.0.0 Safari/537.36"}
    page = session.get(url_gratuito, headers=ua, timeout=30)
    vs, vsg = _extract_viewstate(page.text)
    return vs, vsg, session


def get_token():
    for attempt in range(1, 6):
        try:
            return _authenticate()
        except Exception as e:
            logging.warning(f"Auth attempt {attempt}/5 failed: {e}")
            if attempt < 5:
                time.sleep(2)
    logging.error("All authentication attempts failed")
    return None, None, None


def _base_params(vs, vsg, extra=None):
    params = {
        "__ASYNCPOST": "true",
        "__VIEWSTATE": vs,
        "__VIEWSTATEGENERATOR": vsg,
        "ctl00$drpFiltro": "E",
        "ctl00$cphConsulta$rblConsultaHierarquia": "COMPARATIVA",
        "ctl00$cphConsulta$cpeLegenda_ClientState": "false",
        "ctl00$cphConsulta$chkEscolhida": "on",
        "ctl00$cphConsulta$dlsSerie$ctl00$chkSerieEscolhida": "on",
        "ctl00$cphConsulta$gnResultado": "rbtSerieHistorica",
        "ctl00$rblTipoTexto": "E",
    }
    if extra:
        params.update(extra)
    return params


def scrape_fgv_index(nav_config, column_name):
    vs, vsg, session = get_token()
    if not vs:
        raise Exception(f"Failed to authenticate for {column_name}")

    step1 = nav_config["step1"]
    params = _base_params(vs, vsg, step1.get("extra"))
    params["ctl00$smg"] = step1["smg"]
    params[step1["click_key"] + ".x"] = step1["click_x"]
    params[step1["click_key"] + ".y"] = step1["click_y"]
    session.post(f"{BASE_URL}/default.aspx", data=params)

    req = session.get(f"{BASE_URL}/consulta.aspx")
    vs, vsg = _extract_viewstate(req.text)

    step2 = nav_config["step2"]
    params = _base_params(vs, vsg, step2.get("extra"))
    params["ctl00$smg"] = step2["smg"]
    params[step2["click_key"] + ".x"] = step2["click_x"]
    params[step2["click_key"] + ".y"] = step2["click_y"]
    session.post(f"{BASE_URL}/consulta.aspx", data=params)

    req = session.get(f"{BASE_URL}/consulta.aspx")
    vs, vsg = _extract_viewstate(req.text)

    step3 = nav_config["step3"]
    for item in step3["items"]:
        item_params = _base_params(vs, vsg, step3.get("extra"))
        item_params[f"ctl00$dlsMovelCorrente$ctl0{item}$imbIncluiItem.x"] = step3["click_x"]
        item_params[f"ctl00$dlsMovelCorrente$ctl0{item}$imbIncluiItem.y"] = step3["click_y"]
        item_params["ctl00$smg"] = step3["smg"]
        session.post(f"{BASE_URL}/consulta.aspx", data=item_params)

    session.get(f"{BASE_URL}/consulta.aspx")
    vs, vsg = _extract_viewstate(req.text)

    hist_params = _base_params(vs, vsg)
    hist_params["ctl00$smg"] = "ctl00$cphConsulta$updpOpcoes|ctl00$cphConsulta$rbtSerieHistorica"
    hist_params["__EVENTTARGET"] = "ctl00$cphConsulta$rbtSerieHistorica"
    session.post(f"{BASE_URL}/default.aspx", data=hist_params)

    req = session.get(f"{BASE_URL}/consulta.aspx")
    vs, vsg = _extract_viewstate(req.text)

    view_params = _base_params(vs, vsg)
    view_params["ctl00$smg"] = "ctl00$updpAreaConsulta|ctl00$cphConsulta$butVisualizarResultado"
    view_params["ctl00$cphConsulta$dlsSerie$ctl01$chkSerieEscolhida"] = "on"
    view_params["ctl00$cphConsulta$dlsSerie$ctl02$chkSerieEscolhida"] = "on"
    view_params["ctl00$cphConsulta$butVisualizarResultado"] = "Visualizar e salvar"
    session.post(f"{BASE_URL}/consulta.aspx", data=view_params)

    session.get(f"{BASE_URL}/visualizaconsulta.aspx")
    result = session.get(f"{BASE_URL}/VisualizaConsultaFrame.aspx")
    df = pd.read_html(StringIO(result.text), thousands=".", decimal=",", header=0)[2]
    df.columns = ["dt_ref", column_name]
    return df
