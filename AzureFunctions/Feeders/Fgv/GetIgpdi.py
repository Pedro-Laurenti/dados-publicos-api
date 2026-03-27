from Constants.Indices import IGP_DI
from Feeders.Fgv import scrape_fgv_index

NAV_CONFIG = {
    "step1": {
        "smg": "ctl00$updpCatalogo|ctl00$dlsCatalogoFixo$ctl00$imbOpNivelUm",
        "click_key": "ctl00$dlsCatalogoFixo$ctl00$imbOpNivelUm",
        "click_x": "8",
        "click_y": "0",
    },
    "step2": {
        "smg": "ctl00$updpCatalogo|ctl00$dlsCatalogoFixo$ctl01$imbOpNivelDois",
        "click_key": "ctl00$dlsCatalogoFixo$ctl01$imbOpNivelDois",
        "click_x": "2",
        "click_y": "6",
    },
    "step3": {
        "smg": "ctl00$updpCatalogo|ctl00$dlsMovelCorrente$ctl00$imbIncluiItem",
        "items": [0],
        "click_x": "9",
        "click_y": "3",
    },
}


def get_hist_igpdi():
    return scrape_fgv_index(NAV_CONFIG, IGP_DI)
