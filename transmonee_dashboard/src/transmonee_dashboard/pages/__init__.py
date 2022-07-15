import json
import logging
import pathlib
import collections
from io import BytesIO
from re import L
import urllib

import dash_html_components as html
import numpy as np
import pandas as pd
import requests
from requests.exceptions import HTTPError

from ..sdmx import SdmxData
from ..assets import translations

import pandasdmx as sdmx

# TODO: Move to cfg
app_cfg = {
    "sdmx_url": "https://sdmx.data.unicef.org/ws/public/sdmxapi/rest/",
    "REF_AREA": "REF_AREA"
}

# TODO: Move all of these to env/setting vars from production
sdmx_url = "https://sdmx.data.unicef.org/ws/public/sdmxapi/rest/data/ECARO,TRANSMONEE,1.0/.{}....?format=csv&startPeriod={}&endPeriod={}"

# TODO: Move to cfg
geo_json_file = (
        pathlib.Path(__file__).parent.parent.absolute() / "assets/countries.geo.json"
)
with open(geo_json_file) as shapes_file:
    geo_json_countries = json.load(shapes_file)


def get_ml(lang: str, id: str) -> str:
    if not lang in translations.ml:
        lang = "en"
    if id in translations.ml[lang]:
        return translations.ml[lang][id]
    return id


def get_data(id: list, dq: str, time_period: list, lastnobs: int = 0):
    sdmx_data = SdmxData.SdmxData(app_cfg["sdmx_url"])
    struct, data = sdmx_data.get_data(id, dq, time_period, lastnobs)

    return data


def _add_tree_level(tree_node, parent_code, codes):
    # add all the descendants of parent_code
    for c in codes:
        if "parent" in c and c["parent"] == parent_code:
            if "children" not in tree_node:
                tree_node["children"] = []
            tree_node["children"].append({"key": c["id"], "title": c["name"]})
            _add_tree_level(tree_node["children"][-1], c["id"], codes)


def get_codelist_as_tree(agency: str, id: str, version: str = "latest"):
    sdmx_data = SdmxData.SdmxData(app_cfg["sdmx_url"])
    cl = sdmx_data.get_codelist(agency, id, version)

    all_codes = [c["id"] for c in cl]

    ch = []
    # first loop add the codes without a parent, then add the children
    for c in cl:
        if "parent" not in c:
            ch.append({"key": c["id"], "title": c["name"]})
            # recursion
            _add_tree_level(ch[-1], c["id"], cl)

    return {"tree": {"title": "Select all", "key": "0", "children": ch}, "checked": all_codes}


def page_not_found(pathname):
    return html.P("No page '{}'".format(pathname))
