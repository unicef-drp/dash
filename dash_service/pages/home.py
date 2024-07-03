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
import dash
import dash_bootstrap_components as dbc

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import textwrap
import json 

from dash_service.pages.transmonee import (
    get_base_layout,
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
    update_domain_with_url,
)

from dash_service.static.page_config import (
    merged_page_config
)


# configure the Dash instance's layout
def layout(page_slug=None, **query_parmas):
    return html.Div(
        [
            dcc.Location(id='url', refresh=False),
            html.Br(),
            dcc.Store(id="store"),
            dcc.Store(id="data-store"),
            dcc.Store(id='current-indicator-store', storage_type='memory'),
            dcc.Store(id='initial-load', data={'is_first_load': True}),
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
    return "TOTAL"

@callback(
    Output({"type": "indicator-button", "index": ALL}, "active"),
    Input({"type": "indicator-button", "index": ALL}, "n_clicks"),
    State({"type": "indicator-button", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def set_active_button(_, buttons_id):
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
        Input({'type': "nav_buttons", 'index': "crm_view"}, 'active')
    ],
    [
        State({'type': "indicator-button", 'index': ALL}, 'id')
    ]
)
def update_current_indicator(dropdown_value, active_indicator_buttons, crm_view_active, indicator_button_ids):
    # Check if 'crm_view' button is active to set the view_toggle
    view_toggle = crm_view_active

    if view_toggle:  # If the view is based on 'crm_view' button
        active_index = next((i for i, active in enumerate(active_indicator_buttons) if active), None)
        if active_index is not None:
            return indicator_button_ids[active_index]['index']
    return dropdown_value  # Otherwise, return the dropdown value

@callback(
    [
        Output('search_by_indicator_div', 'style'),
        Output('crm_framework_view_div', 'style'),
        Output('indicator_buttons_div', 'style')
    ],
    [Input({'type': "nav_buttons", 'index': "crm_view"}, 'active')],
    [
        State('search_by_indicator_div', 'style'),
        State('crm_framework_view_div', 'style'),
        State('indicator_buttons_div', 'style')
    ]
)
def toggle_divs_visibility(crm_view_active, style_search_by_indicator, style_crm_framework_view, style_indicator_buttons):
    # Function to return default style or empty dict if None
    default_style = lambda style: {k: v for k, v in (style or {}).items() if k != 'display'}

    if crm_view_active:
        # Hide 'search_by_indicator_div', show other two divs
        style_search_by_indicator_updated = {**default_style(style_search_by_indicator), 'display': 'none'}
        style_crm_framework_view_updated = default_style(style_crm_framework_view)
        style_indicator_buttons_updated = default_style(style_indicator_buttons)
    else:
        # Show 'search_by_indicator_div', hide other two divs
        style_search_by_indicator_updated = default_style(style_search_by_indicator)
        style_crm_framework_view_updated = {**default_style(style_crm_framework_view), 'display': 'none'}
        style_indicator_buttons_updated = {**default_style(style_indicator_buttons), 'display': 'none'}

    return style_search_by_indicator_updated, style_crm_framework_view_updated, style_indicator_buttons_updated

    
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
    [Input("domain-dropdown", "value"),
     Input("url", "search")],
    [State("initial-load", "data")],
    prevent_initial_call=True
)
def apply_create_subdomain_buttons(domain_dropdown_value, url_search, initial_load_data):
    ctx = callback_context
    trigger_id = ctx.triggered[0]['prop_id']

    # Check if it's the initial load or domain-dropdown value change
    initial_load = initial_load_data.get('is_first_load', True)
    if initial_load or "domain-dropdown.value" in trigger_id:
        # Create and return subdomain buttons
        return create_subdomain_buttons(domain_dropdown_value, initial_load, url_search)
    
    # If not triggered by the initial load or domain-dropdown change, do not update
    return dash.no_update

@callback(
    Output({"type": "subdomain_button", "index": ALL}, "active"),
    [Input({"type": "subdomain_button", "index": ALL}, "n_clicks")],
    [State({"type": "subdomain_button", "index": ALL}, "id")]
)
def set_active_subdomain_button(button_clicks, buttons_id):
    ctx = callback_context
    trigger_id = ctx.triggered[0]['prop_id']
    print(f"trigger_id: {trigger_id}")
    # Check if the callback was triggered by a subdomain button click
    if 'subdomain_button' in trigger_id:
        # Extracting the index of the clicked button from the trigger_id
        button_index = json.loads(trigger_id.split('.')[0])['index']
        print(f"button_index: {button_index}")
        return [button_index == button['index'] for button in buttons_id]

    # If no button was clicked, do not update the active state
    print("no_update")
    return dash.no_update
  
@callback(
    Output('initial-load', 'data'),
    Input('url', 'search'),
    prevent_initial_call=True
)
def set_initial_load_flag(search):
    return {'is_first_load': False}

@callback(
    Output("domain-dropdown", "value"),
    Input('url', 'search'),
    Input('initial-load', 'data'),
    #prevent_initial_call=True
)
def update_domain_dropdown_on_initial_load(search, load_data):
    if load_data['is_first_load']:
        print("First load")
        print(search)
        subdomain_code = search.strip('?prj=tm&page=')
        if not subdomain_code:
            subdomain_code = 'DEM'  # Set 'DEM' by default if subdomain_code is empty
        domain_value = update_domain_with_url(subdomain_code)  # Map subdomain to domain
        return domain_value
    raise dash.exceptions.PreventUpdate     

# Callback to update the URL based on the active button
@callback(
    Output('url', 'search'),
    Input({"type": "subdomain_button", "index": ALL}, "active"),
    Input({'type': "nav_buttons", 'index': "crm_view"}, 'active'),
    State({"type": "subdomain_button", "index": ALL}, "id")
)
def update_url(active_buttons, crm_view, buttons_id):
    if crm_view:
        active_button_id = [button['index'] for button, is_active in zip(buttons_id, active_buttons) if is_active]
        if active_button_id:
            new_search = f'?prj=tm&page={active_button_id[0]}'
            print(f"active button: {new_search.lstrip('?prj=tm&page=')}")
            return new_search
        else:
            return dash.no_update
    return "?prj=tm"

@callback(
    Output({"type": "button_group", "index": "AIO_AREA"}, "children"),
    [Input({"type": "subdomain_button", "index": ALL}, "active")],
    [State({"type": "subdomain_button", "index": ALL}, "id")],
    prevent_initial_call=True,
)
def apply_create_indicator_buttons(active_button, subdomain_buttons):
    return create_indicator_buttons(active_button, subdomain_buttons)

@callback(
    Output({"type": "nav_buttons", "index": ALL}, "active"),
    Input({"type": "nav_buttons", "index": ALL}, "n_clicks"),
    State({"type": "nav_buttons", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def set_active_nav_button(_, buttons_id):
    return active_button(_, buttons_id)

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
        Output("aio_area_indicator_link", "children"),
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
        Input("show-average-checkbox", "value"),
    ],
        State({"type": "area_types", "index": "AIO_AREA"}, "value"),
    prevent_initial_call=True,
)
def apply_aio_area_figure(
    indicator,
    compare,
    years_slider,
    countries,
    country_group,
    average_line,
    selected_type,
):
    return aio_area_figure(
        indicator,
        compare,
        years_slider,
        countries,
        country_group,
        average_line,
        selected_type,
    )
