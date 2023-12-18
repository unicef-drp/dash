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
    indicator_card,
    graphs_dict,
    selections,
    active_button,
    breakdown_options,
    default_compare,
    aio_area_figure,
    fig_options,
    download_data,
    update_country_selection,
    filter_crc_data,
    available_crc_years,
    update_indicator_dropdown,
    update_indicator_dropdown_class,
    create_subdomain_buttons,
    create_indicator_buttons,
)

from dash_service.static.page_config import (
    merged_page_config
)

# customization of plots requested by Siraj
packed_config = {}

# register_page(
#     __name__,
#     # path_template="/transmonee/<page_slug>",
#     path="/transmonee/child-rights",
#     title="Child Rights Landscape and Governance",
#     # order=1,
# )
page_prefix = "crg"
page_path = "child-rights"
domain_colour = "#562061"
light_domain_colour = "#e7c9ed"
dark_domain_colour = "#44194d"
map_colour = "purpor"


# configure the Dash instance's layout
def layout(page_slug=None, **query_parmas):
    return html.Div(
        [
            html.Br(),
            dcc.Store(id="store"),
            dcc.Store(id="data-store"),
            dcc.Store(id='current-indicator-store', storage_type='memory'),
            dbc.Container(
                fluid=True,
                children=get_base_layout(
                    domain_colour=merged_page_config['child-rights']['domain_colour'],
                    query_params=query_parmas,
                ),
            ),
            html.Br(),
        ],
        id="mainContainer",
    )

@callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@callback(
    Output("indicator-dropdown", "options"),
    Output("indicator-dropdown", "value"),
    Input("crm-dropdown", "value"),
    Input("sdg-toggle", "on")
)
def apply_update_indicator_dropdown(indicator_filter, sdg_toggle):
    return update_indicator_dropdown(indicator_filter, sdg_toggle)


@callback(
    Output({"type": "area_types", "index": "AIO_AREA"}, "options"),
    Output({"type": "area_types", "index": "AIO_AREA"}, "value"),
    [Input('current-indicator-store', 'data')],
    prevent_initial_call=True,
)
def set_fig_options(indicator):
    return fig_options(indicator)


@callback(
    Output({"type": "area_breakdowns", "index": "AIO_AREA"}, "options"),
    [
        Input('current-indicator-store', 'data'),
        Input({"type": "area_types", "index": "AIO_AREA"}, "value"),
    ],
    prevent_initial_call=True,
)
def set_breakdown_options(indicator, fig_type):
    return breakdown_options(indicator, fig_type)


@callback(
    Output({"type": "area_breakdowns", "index": "AIO_AREA"}, "value"),
    Input({"type": "area_breakdowns", "index": "AIO_AREA"}, "options"),
    [
        State({"type": "area_types", "index": "AIO_AREA"}, "value"),
        State('current-indicator-store', 'data'),
    ],
    prevent_initial_call=True,
)
def set_default_compare(compare_options, selected_type, indicator):
    return default_compare(compare_options, selected_type, indicator)

@callback(
    Output({"type": "indicator-button", "index": ALL}, "active"),
    Input({"type": "indicator-button", "index": ALL}, "n_clicks"),
    State({"type": "indicator-button", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def set_active_button(_, buttons_id):
    print(f"buttons_id: {buttons_id}")
    print(active_button(_, buttons_id))
    return active_button(_, buttons_id)


@callback(
    Output("download-csv-info", "data"),
    Input("download_btn", "n_clicks"),
    State("data-store", "data"),
    prevent_initial_call=True,
)
def apply_download_data(n_clicks, data):
    return download_data(n_clicks, data)


@callback(
    Output("country-filter", "options"),
    Output("country-filter", "value"),
    [
        Input("country-group", "value"),
        Input("country-filter", "value"),
    ],
    prevent_initial_call=True,
)
def apply_update_country_selection(country_group, country_selection):
    return update_country_selection(country_group, country_selection)


@callback(
    Output("year-filter-crc", "options"),
    Output("year-filter-crc", "value"),
    [
        Input("country-filter-crc", "value"),
        Input('current-indicator-store', 'data'),
    ],
    prevent_initial_call=True,
)
def apply_available_crc_years(country, indicator):
    return available_crc_years(country, indicator)

@callback(
    Output('current-indicator-store', 'data'),
    [
        Input("indicator-dropdown", "value"),
        Input({'type': "indicator-button", 'index': ALL}, 'active'),
    ],
    [
        State({'type': "indicator-button", 'index': ALL}, 'id')
    ]
)
def update_current_indicator(dropdown_value, active_buttons, button_ids):
    view_toggle = True
    if view_toggle:  # If the view is based on indicator buttons
        active_index = next((i for i, active in enumerate(active_buttons) if active), None)
        if active_index is not None:
            print(f"current_indicator: {button_ids[active_index]['index']}")
            return button_ids[active_index]['index']
    print(f"dropdown_value")
    return dropdown_value  # Otherwise, return the dropdown value

@callback(
    Output("crc-header", "children"),
    Output("crc-header", "style"),
    Output("crc-accordion", "children"),
    Input("year-filter-crc", "value"),
    Input("country-filter-crc", "value"),
    Input('current-indicator-store', 'data'),
    State("crc-header", "style"),
    prevent_initial_call=True,
)
def apply_filter_crc_data(year, country, indicator, text_style):
    return filter_crc_data(year, country, indicator, text_style)

@callback(
        Output("indicator-dropdown", "className"),
        Output("domain-text", "children"),
        Input('current-indicator-store', 'data'),
        prevent_initial_call=True,
)
def apply_update_indicator_dropdown_class(indicator):
 return update_indicator_dropdown_class(indicator)

@callback(
    Output("themes", "children"),
    Input("domain-dropdown", "value"),
)
def apply_create_subdomain_buttons(domain_dropdown_value):
    return create_subdomain_buttons(domain_dropdown_value)

@callback(
    Output({"type": "subdomain_button", "index": ALL}, "active"),
    Input({"type": "subdomain_button", "index": ALL}, "n_clicks"),
    State({"type": "subdomain_button", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def set_active_subdomain_button(_, buttons_id):
    return active_button(_, buttons_id)


@callback(
    Output({"type": "button_group", "index": "AIO_AREA"}, "children"),
    [Input({"type": "subdomain_button", "index": ALL}, "active")],
    [State({"type": "subdomain_button", "index": ALL}, "id")]
)
def apply_create_indicator_buttons(active_button, subdomain_buttons):
    return create_indicator_buttons(active_button, subdomain_buttons)

@callback(
    [
        Output("collapse-years-button", "label"),
        Output({"type": "area", "index": "AIO_AREA"}, "figure"),
        Output("aio_area_area_info", "children"),
        Output("indicator_card", "children"),
        Output("aio_area_data_info_rep", "children"),
        Output("data-hover-body", "children"),
        Output("aio_area_data_info_nonrep", "children"),
        Output("no-data-hover-body", "children"),
        Output("aio_area_graph_info", "children"),
        Output("data-store", "data"),
        Output("definition-popover", "children"),
    ],
    [
        Input('current-indicator-store', 'data'),
        Input({"type": "area_breakdowns", "index": "AIO_AREA"}, "value"),
        Input("year_slider", "value"),
        Input("country-filter", "value"),
        Input("country-group", "value"),
        
    ],
    [
        State({"type": "area_types", "index": "AIO_AREA"}, "value"),
    ],
    prevent_initial_call=True,
)
def apply_aio_area_figure(
    indicator,
    compare,
    years_slider,
    countries,
    country_group,
    selected_type,
):
    return aio_area_figure(
        indicator,
        compare,
        years_slider,
        countries,
        country_group,
        selected_type,
    )
