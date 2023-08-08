from dash import (
    html,
    dcc,
    callback_context,
    ALL,
    Input,
    Output,
    State,
    register_page,
    callback,
)
import dash_bootstrap_components as dbc

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import textwrap

from dash_service.pages.transmonee import (
    geo_json_countries,
    get_base_layout,
    make_card,
    indicator_card,
    graphs_dict,
    selections,
    themes,
    aio_options,
    active_button,
    breakdown_options,
    default_compare,
    aio_area_figure,
    fig_options,
    download_data,
    update_country_selection,
    filter_crc_data,
    fa,
)


min_max_card_suffix = "min - max values"

page_config = {
    "HSM": {
        "NAME": "Health system",
        "CARDS": [
            {
                "name": "",
                "indicator": "HT_UHC_IDX",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_SH_XPD_CHEX_GD_ZS",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_SH_XPD_GHED_GD_ZS",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_SH_XPD_GHED_GE_ZS",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_SH_XPD_GHED_PP_CD",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_SH_XPD_OOPC_CH_ZS",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_INS_COV",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "HT_UHC_IDX",
                "HT_SH_XPD_CHEX_GD_ZS",
                "HT_SH_XPD_GHED_GD_ZS",
                "HT_SH_XPD_GHED_GE_ZS",
                "HT_SH_XPD_GHED_PP_CD",
                "HT_SH_XPD_OOPC_CH_ZS",
                "HT_INS_COV",
            ],
            "default_graph": "bar",
            "default": "HT_UHC_IDX",
        },
    },
    "MNH": {
        "NAME": "Maternal, newborn and child health",
        "CARDS": [
            {
                "name": "",
                "indicator": "CME_MRM0",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "CME_MRY0",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "CME_MRY0T4",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "MNCH_SAB",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "CME_SBR",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "MNCH_CSEC",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "NT_BW_LBW",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "CME_MRM0",
                "CME_MRY0",
                "CME_MRY0T4",
                "MNCH_SAB",
                "CME_SBR",
                "MNCH_CSEC",
                "NT_BW_LBW",
            ],
            "default_graph": "bar",
            "default": "CME_MRM0",
        },
    },
    "IMM": {
        "NAME": "Immunization",
        "CARDS": [
            {
                "name": "",
                "indicator": "IM_MCV2",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "IM_DTP3",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "IM_PCV3",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "IM_HPV",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "IM_MCV2",
                "IM_DTP3",
                "IM_PCV3",
                "IM_HPV",
            ],
            "default_graph": "bar",
            "default": "IM_MCV2",
        },
    },
    "NUT": {
        "NAME": "Nutrition",
        "CARDS": [
            {
                "name": "",
                "indicator": "NT_BF_EXBF",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "NT_BF_EIBF",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "NT_CF_ISSSF_FL",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "NT_CF_MAD",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "NT_ANT_WHZ_PO2",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "NT_CHLD_OBESITY",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "NT_ANT_WHZ_NE2",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "NT_ANT_HAZ_NE2",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_SH_STA_ANEM",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_ANEM_U5",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "NT_BF_EXBF",
                "NT_BF_EIBF",
                "NT_CF_ISSSF_FL",
                "NT_CF_MAD",
                "NT_ANT_WHZ_PO2",
                "NT_CHLD_OBESITY",
                "NT_ANT_WHZ_NE2",
                "NT_ANT_HAZ_NE2",
                "HT_SH_STA_ANEM",
                "HT_ANEM_U5",
            ],
            "default_graph": "bar",
            "default": "NT_BF_EXBF",
        },
    },
    "ADO": {
        "NAME": "Adolescent physical, mental and reproductive health",
        "CARDS": [
            {
                "name": "",
                "indicator": "FT_SP_DYN_ADKL",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_ADOL_MT",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "MT_SDG_SUICIDE",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_CHLD_DAILY_EXER",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "FT_SP_DYN_ADKL",
                "HT_ADOL_MT",
                "MT_SDG_SUICIDE",
                "HT_CHLD_DAILY_EXER",
            ],
            "default_graph": "bar",
            "default": "FT_SP_DYN_ADKL",
        },
    },
    "HIV": {
        "NAME": "HIV/AIDS",
        "CARDS": [
            {
                "name": "",
                "indicator": "HVA_EPI_LHIV_0-19",
                "suffix": "estimated children living with HIV",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "HVA_EPI_INF_RT_0-14",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HVA_EPI_DTH_ANN_0-19",
                "suffix": "estimated AIDS-related deaths",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "HVA_PMTCT_MTCT",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HVA_PMTCT_STAT_CVG",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HVA_PED_ART_CVG",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HVA_PREV_KNOW",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "HVA_EPI_LHIV_0-19",
                "HVA_EPI_INF_RT_0-14",
                "HVA_EPI_DTH_ANN_0-19",
                "HVA_PMTCT_MTCT",
                "HVA_PMTCT_STAT_CVG",
                "HVA_PED_ART_CVG",
                # "HVA_PREV_KNOW",
            ],
            "default_graph": "bar",
            "default": "HVA_EPI_LHIV_0-19",
        },
    },
}

packed_config = {}

# register_page(
#     __name__,
#     # path_template="/transmonee/<page_slug>",
#     path="/transmonee/child-health",
#     title="Health and Nutrition",
#     # order=2,
# )
page_prefix = "han"
page_path = "child-health"
domain_colour = "#3e7c49"
light_domain_colour = "#e0f0e3"
dark_domain_colour = "#24472a"
map_colour = "algae"


# configure the Dash instance's layout
def layout(page_slug=None, **query_parmas):
    print("In layout")
    print(page_slug)
    print(query_parmas)
    return html.Div(
        [
            html.Br(),
            dcc.Store(id=f"{page_prefix}-store"),
            dcc.Store(id=f"{page_prefix}-data-store"),
            dbc.Container(
                fluid=True,
                children=get_base_layout(
                    indicators=page_config,
                    main_subtitle="Health and Nutrition",
                    page_prefix=page_prefix,
                    page_path=page_path,
                    domain_colour=domain_colour,
                    query_params=query_parmas,
                ),
            ),
            html.Br(),
        ],
        id="mainContainer",
    )


# callback to navigate to different domain
@callback(
    Output(f"{page_prefix}-theme", "search"),
    Output(f"{page_prefix}-theme", "hash"),
    [Input(f"{page_prefix}-topic-dropdown", "value")],
    prevent_initial_call=True,
)
def update_url(value):
    # return f"/transmonee/{value}", ""
    return value, ""


@callback(
    Output(f"{page_prefix}-store", "data"),
    Input(f"{page_prefix}-theme", "hash"),
    State(f"{page_prefix}-indicators", "data"),
)
def apply_selections(theme, indicator):
    return selections(theme, indicator)


@callback(
    Output(f"{page_prefix}-main_title", "children"),
    Output(f"{page_prefix}-info-tooltip", "children"),
    Output(f"{page_prefix}-themes", "children"),
    Input(f"{page_prefix}-store", "data"),
    State(f"{page_prefix}-indicators", "data"),
    prevent_initial_call=True,
)
def show_themes(selections, indicators_dict):
    return themes(selections, indicators_dict, page_prefix)


@callback(
    Output({"type": "button_group", "index": f"{page_prefix}-AIO_AREA"}, "children"),
    Input(f"{page_prefix}-store", "data"),
    State(f"{page_prefix}-indicators", "data"),
    prevent_initial_call=True,
)
def set_aio_options(theme, indicators_dict):
    return aio_options(theme, indicators_dict, page_prefix)


@callback(
    Output({"type": "area_types", "index": f"{page_prefix}-AIO_AREA"}, "options"),
    Output({"type": "area_types", "index": f"{page_prefix}-AIO_AREA"}, "value"),
    [Input({"type": f"{page_prefix}-indicator_button", "index": ALL}, "active")],
    State({"type": f"{page_prefix}-indicator_button", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def set_fig_options(is_active_button, buttons_id):
    return fig_options(is_active_button, buttons_id, packed_config)


@callback(
    Output({"type": f"{page_prefix}-indicator_button", "index": ALL}, "active"),
    Input({"type": f"{page_prefix}-indicator_button", "index": ALL}, "n_clicks"),
    State({"type": f"{page_prefix}-indicator_button", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def set_active_button(_, buttons_id):
    return active_button(_, buttons_id)


@callback(
    Output({"type": "area_breakdowns", "index": f"{page_prefix}-AIO_AREA"}, "options"),
    [
        Input({"type": f"{page_prefix}-indicator_button", "index": ALL}, "active"),
        Input({"type": "area_types", "index": f"{page_prefix}-AIO_AREA"}, "value"),
    ],
    State({"type": f"{page_prefix}-indicator_button", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def set_breakdown_options(is_active_button, fig_type, buttons_id):
    return breakdown_options(is_active_button, fig_type, buttons_id, packed_config)


@callback(
    Output({"type": "area_breakdowns", "index": f"{page_prefix}-AIO_AREA"}, "value"),
    Input({"type": "area_breakdowns", "index": f"{page_prefix}-AIO_AREA"}, "options"),
    [
        State({"type": "area_types", "index": f"{page_prefix}-AIO_AREA"}, "value"),
        State(f"{page_prefix}-indicators", "data"),
        State(f"{page_prefix}-store", "data"),
    ],
    prevent_initial_call=True,
)
def set_default_compare(compare_options, selected_type, indicators_dict, theme):
    return default_compare(compare_options, selected_type, indicators_dict, theme)


@callback(
    Output(f"{page_prefix}-download-csv-info", "data"),
    Input(f"{page_prefix}-download_btn", "n_clicks"),
    State(f"{page_prefix}-data-store", "data"),
    prevent_initial_call=True,
)
def apply_download_data(n_clicks, data):
    return download_data(n_clicks, data)


@callback(
    Output(f"{page_prefix}-country-filter", "options"),
    Output(f"{page_prefix}-country-filter", "value"),
    [
        Input(f"{page_prefix}-country-group", "value"),
        Input(f"{page_prefix}-country-filter", "value"),
    ],
    prevent_initial_call=True,
)
def apply_update_country_selection(country_group, country_selection):
    return update_country_selection(country_group, country_selection)


@callback(
    Output(f"{page_prefix}-crc-header", "children"),
    Output(f"{page_prefix}-crc-year", "children"),
    Output(f"{page_prefix}-crc-enabling", "children"),
    Output(f"{page_prefix}-crc-supply", "children"),
    Output(f"{page_prefix}-crc-demand", "children"),
    Input(f"{page_prefix}-country-filter-crc", "value"),
    Input(f"{page_prefix}-store", "data"),
    State(f"{page_prefix}-indicators", "data"),
    prevent_initial_call=True,
)
def apply_filter_crc_data(country, selections, indicators_dict):
    return filter_crc_data(country, selections, indicators_dict)


@callback(
    [
        Output(f"{page_prefix}-collapse-years-button", "label"),
        Output({"type": "area", "index": f"{page_prefix}-AIO_AREA"}, "figure"),
        Output(f"{page_prefix}-aio_area_area_info", "children"),
        Output(f"{page_prefix}-indicator_card", "children"),
        Output(f"{page_prefix}-aio_area_data_info_rep", "children"),
        Output(f"{page_prefix}-data-hover-body", "children"),
        Output(f"{page_prefix}-aio_area_data_info_nonrep", "children"),
        Output(f"{page_prefix}-no-data-hover-body", "children"),
        Output(f"{page_prefix}-aio_area_graph_info", "children"),
        Output(f"{page_prefix}-data-store", "data"),
    ],
    [
        Input({"type": "area_breakdowns", "index": f"{page_prefix}-AIO_AREA"}, "value"),
        Input(f"{page_prefix}-year_slider", "value"),
        Input(f"{page_prefix}-country-filter", "value"),
        Input(f"{page_prefix}-country-group", "value"),
    ],
    [
        State(f"{page_prefix}-store", "data"),
        State(f"{page_prefix}-indicators", "data"),
        State({"type": "button_group", "index": f"{page_prefix}-AIO_AREA"}, "children"),
        State({"type": "area_types", "index": f"{page_prefix}-AIO_AREA"}, "value"),
    ],
    prevent_initial_call=True,
)
def apply_aio_area_figure(
    compare,
    years_slider,
    countries,
    country_group,
    selections,
    indicators_dict,
    buttons_properties,
    selected_type,
):
    return aio_area_figure(
        compare,
        years_slider,
        countries,
        country_group,
        selections,
        indicators_dict,
        buttons_properties,
        selected_type,
        page_prefix,
        packed_config,
        domain_colour,
        light_domain_colour,
        dark_domain_colour,
        map_colour,
    )
