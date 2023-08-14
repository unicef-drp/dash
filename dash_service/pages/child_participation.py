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
    available_crc_years,
)


min_max_card_suffix = "min - max values"

page_config = {
    "REG": {
        "NAME": "Birth registration and identity",
        "CARDS": [
            {
                "name": "",
                "indicator": "PT_CHLD_Y0T4_REG",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PP_SG_REG_BRTH90N",
                "suffix": "countries",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "PP_SG_REG_DETH75N",
                "suffix": "countries",
                "min_max": False,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "PT_CHLD_Y0T4_REG",
                "PP_SG_REG_BRTH90N",
                "PP_SG_REG_DETH75N",
            ],
            "default_graph": "bar",
            "default": "PT_CHLD_Y0T4_REG",
        },
    },
    "ICT": {
        "NAME": "Information, internet and protection of privacy",
        "CARDS": [
            {
                "name": "",
                "indicator": "PP_IT_USE_ii99",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PP_SE_ADT_ACTS_PRGM",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PP_SE_ADT_ACTS_ATCH",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PP_SE_ADT_ACTS_SFWR",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "ICT_PERSONAL_DATA",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "ICT_SECURITY_CONCERN",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "PP_IT_USE_ii99",
                "PP_SE_ADT_ACTS_PRGM",
                "PP_SE_ADT_ACTS_ATCH",
                "PP_SE_ADT_ACTS_SFWR",
                "ICT_PERSONAL_DATA",
                "ICT_SECURITY_CONCERN",
            ],
            "default_graph": "bar",
            "default": "PP_IT_USE_ii99",
        },
    },
}

packed_config = {}

# register_page(
#     __name__,
#     # path_template="/transmonee/<page_slug>",
#     path="/transmonee/child-participation",
#     title="Participation",
#     # order=4,
# )
page_prefix = "par"
page_path = "child-participation"
domain_colour = "#861c3f"
light_domain_colour = "#eca7be"
dark_domain_colour = "#541228"
map_colour = "Brwnyl"


# configure the Dash instance's layout
def layout(page_slug=None, **query_parmas):
    return html.Div(
        [
            html.Br(),
            dcc.Store(id=f"{page_prefix}-store"),
            dcc.Store(id=f"{page_prefix}-data-store"),
            dbc.Container(
                fluid=True,
                children=get_base_layout(
                    indicators=page_config,
                    main_subtitle="Participation and Civil Rights",
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
    Output(f"{page_prefix}-year-filter-crc", "options"),
    Output(f"{page_prefix}-year-filter-crc", "value"),
    [
        Input(f"{page_prefix}-country-filter-crc", "value"),
        Input(f"{page_prefix}-store", "data"),
        Input(f"{page_prefix}-indicators", "data"),
    ],
    prevent_initial_call=True,
)
def apply_available_crc_years(country, selections, indicators_dict):
    return available_crc_years(country, selections, indicators_dict)


@callback(
    Output(f"{page_prefix}-crc-header", "children"),
    Output(f"{page_prefix}-crc-enabling", "children"),
    Output(f"{page_prefix}-crc-supply", "children"),
    Output(f"{page_prefix}-crc-demand", "children"),
    Input(f"{page_prefix}-year-filter-crc", "value"),
    Input(f"{page_prefix}-country-filter-crc", "value"),
    Input(f"{page_prefix}-store", "data"),
    Input(f"{page_prefix}-indicators", "data"),
    prevent_initial_call=True,
)
def apply_filter_crc_data(year, country, selections, indicators_dict):
    return filter_crc_data(year, country, selections, indicators_dict)


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
        Output(f"{page_prefix}-definition-popover", "children"),
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
