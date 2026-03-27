from Constants.Indices import IGP_M
from Feeders.Fgv import scrape_fgv_index

_EXTRA_FIELDS = {
    "ctl00$cphConsulta$txtMes": "__/__/____",
    "ctl00$cphConsulta$txtPeriodoInicio": "__/__/____",
    "ctl00$cphConsulta$txtPeriodoFim": "__/__/____",
}

NAV_CONFIG = {
    "step1": {
        "smg": "ctl00$updpCatalogo|ctl00$dlsCatalogoFixo$ctl00$imbOpNivelUm",
        "click_key": "ctl00$dlsCatalogoFixo$ctl00$imbOpNivelUm",
        "click_x": "9",
        "click_y": "4",
        "extra": _EXTRA_FIELDS,
    },
    "step2": {
        "smg": "ctl00$updpCatalogo|ctl00$dlsCatalogoFixo$ctl01$imbOpNivelDois",
        "click_key": "ctl00$dlsCatalogoFixo$ctl01$imbOpNivelDois",
        "click_x": "5",
        "click_y": "3",
        "extra": _EXTRA_FIELDS,
    },
    "step3": {
        "smg": "ctl00$updpCatalogo|ctl00$dlsMovelCorrente$ctl00$imbIncluiItem",
        "items": [2],
        "click_x": "2",
        "click_y": "3",
        "extra": _EXTRA_FIELDS,
    },
}


def get_hist_igpm():
    return scrape_fgv_index(NAV_CONFIG, IGP_M)
