from Constants.Indices import INCC_M
from Feeders.Fgv import scrape_fgv_index

NAV_CONFIG = {
    "step1": {
        "smg": "ctl00$updpCatalogo|ctl00$dlsCatalogoFixo$ctl00$imbOpNivelUm",
        "click_key": "ctl00$dlsCatalogoFixo$ctl00$imbOpNivelUm",
        "click_x": "8",
        "click_y": "0",
    },
    "step2": {
        "smg": "ctl00$updpCatalogo|ctl00$dlsCatalogoFixo$ctl04$imbOpNivelDois",
        "click_key": "ctl00$dlsCatalogoFixo$ctl04$imbOpNivelDois",
        "click_x": "1",
        "click_y": "8",
    },
    "step3": {
        "smg": "ctl00$updpCatalogo|ctl00$dlsMovelCorrente$ctl02$imbIncluiItem",
        "items": [2],
        "click_x": "13",
        "click_y": "6",
    },
}


def get_hist_incc():
    return scrape_fgv_index(NAV_CONFIG, INCC_M)
