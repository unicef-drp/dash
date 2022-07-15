import textwrap

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_treeview_antd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from dash.dependencies import MATCH, ClientsideFunction, Input, Output, State
from scipy.stats import zscore

import datetime

from ..app import app
from ..components import fa
from . import (
    # countries,
    # countries_iso3_dict,
    # df_sources,
    # dimension_names,
    # geo_json_countries,
    # get_filtered_dataset,
    # indicator_names,
    # indicators_config,
    # programme_country_indexes,
    # selection_index,
    # selection_tree,
    # unicef_country_prog,
    # get_search_countries,
    get_codelist_as_tree,
    get_ml
)

# set defaults
pio.templates.default = "plotly_white"
px.defaults.color_continuous_scale = px.colors.sequential.BuGn
px.defaults.color_discrete_sequence = px.colors.qualitative.Dark24

lang = "en"

colours = [
    "primary",
    "success",
    "warning",
    "danger",
    "secondary",
    "info",
    "success",
    "danger",
]
AREA_KEYS = ["MAIN", "AREA_1", "AREA_2", "AREA_3", "AREA_4", "AREA_5", "AREA_6"]
DEFAULT_LABELS = {
    "Country_name": "Country",
    "TIME_PERIOD": "Year",
    "Sex_name": "Sex",
    "Residence_name": "Residence",
    "Age_name": "Age",
    "Wealth_name": "Wealth Quintile",
}
CARD_TEXT_STYLE = {"textAlign": "center", "color": "#0074D9"}

EMPTY_CHART = {
    "layout": {
        "xaxis": {"visible": False},
        "yaxis": {"visible": False},
        "annotations": [
            {
                "text": "No data is available for the selected filters",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 28},
            }
        ],
    }
}


def make_area(area_name):
    area_id = {"type": "area", "index": area_name}
    popover_id = {"type": "area_sources", "index": area_name}
    historical_data_style = {"display": "none"}
    exclude_outliers_style = {"paddingLeft": 20, "display": "block"}
    breakdowns_style = {"display": "block"}

    # TODO: still differentiating main area id from other areas ids because the call backs are still not unified
    if area_name == "MAIN":
        area_id = f"{area_name.lower()}_area"
        popover_id = f"{area_name.lower()}_area_sources"
        historical_data_style = {"display": "block"}
        exclude_outliers_style = {"display": "none"}
        breakdowns_style = {"display": "none"}

    # lbassil: unifying both main and figure area generations by tweaking the ids and styles
    area = dbc.Card(
        [
            dbc.CardHeader(
                id={"type": "area_title", "index": area_name},
                style={"fontWeight": "bold"},
            ),
            dbc.CardBody(
                [
                    dcc.Dropdown(
                        id={"type": "area_options", "index": area_name},
                        className="dcc_control",
                    ),
                    html.Br(),
                    dbc.Checklist(
                        options=[
                            {
                                "label": "Show historical data",
                                "value": 1,
                            }
                        ],
                        value=[],
                        id={
                            "type": "historical_data_toggle",
                            "index": area_name,
                        },
                        switch=True,
                        style=historical_data_style,
                    ),
                    html.Br(),
                    dbc.RadioItems(
                        id={"type": "area_types", "index": area_name},
                        inline=True,
                    ),
                    dcc.Loading([dcc.Graph(id=area_id)]),
                    dbc.Checklist(
                        options=[
                            {
                                "label": "Exclude outliers ",
                                "value": 1,
                            }
                        ],
                        value=[1],
                        id={
                            "type": "exclude_outliers_toggle",
                            "index": area_name,
                        },
                        switch=True,
                        style=exclude_outliers_style,
                    ),
                    html.Br(),
                    dbc.RadioItems(
                        id={"type": "area_breakdowns", "index": area_name},
                        inline=True,
                        style=breakdowns_style,
                    ),
                    html.Div(
                        fa("fas fa-info-circle"),
                        id=f"{area_name.lower()}_area_info",
                        className="float-right",
                    ),
                    dbc.Popover(
                        [
                            dbc.PopoverHeader("Sources"),
                            dbc.PopoverBody(id=popover_id),
                        ],
                        id="hover",
                        target=f"{area_name.lower()}_area_info",
                        trigger="hover",
                    ),
                ]
            ),
        ],
        id={"type": "area_parent", "index": area_name},
    )
    return area


def _get_years_range(time_period: list):
    if type(time_period[1]) == str and time_period[1] == "now":
        time_period[1] = datetime.datetime.now().year
    return list(range(time_period[0], time_period[1]))


def get_base_layout(**kwargs):
    page_config = kwargs.get("page_cfg")
    # indicators_dict = kwargs.get("indicators")
    main_title = page_config["main_title"]
    years = _get_years_range(page_config["default_timeperiod"])
    ref_area_cl = page_config["ref_areas_cl"]
    ref_area_tree = get_codelist_as_tree(ref_area_cl["agency"], ref_area_cl["id"])

    is_country_profile = kwargs.get("is_country_profile")

    # Default styles
    country_dropdown_style = {"display": "none"}
    themes_row_style = {"verticalAlign": "center", "display": "flex"}
    countries_filter_style = {"display": "block"}
    programme_toggle_style = {"display": "block"}
    main_area_style = {"display": "block"}
    # If country profile the default styles are set
    if is_country_profile:
        country_dropdown_style = {
            "minWidth": 400,
            "maxWidth": 600,
            "paddingRight": 4,
            "verticalAlign": "center",
            "display": "visible",
        }
        themes_row_style = {"display": "none"}
        countries_filter_style = {"display": "none"}
        programme_toggle_style = {"display": "none"}
        main_area_style = {"display": "none"}

    return html.Div(
        [
            dcc.Store(id="page_config", data=page_config),
            dcc.Location(id="theme"),
            html.Div(
                className="heading",
                style={"padding": 36},
                children=[
                    html.Div(
                        className="heading-content",
                        children=[
                            html.Div(
                                className="heading-panel",
                                style={"padding": 20},
                                children=[
                                    html.H1(
                                        main_title,
                                        id="main_title",
                                        className="heading-title",
                                    ),
                                    html.P(

                                        id="subtitle",
                                        className="heading-subtitle",
                                    ),
                                ],
                            ),
                        ],
                    )
                ],
            ),
            dbc.Row(
                children=[
                    dbc.Col(
                        [
                            dbc.Row(
                                [
                                    dbc.ButtonGroup(
                                        id="themes",
                                    ),
                                ],
                                id="theme-row",
                                # width=4,
                                className="my-2",
                                # no_gutters=True,
                                justify="center",
                                style=themes_row_style,
                            ),
                            dbc.Row(
                                [
                                    dbc.DropdownMenu(
                                        label=f"Years: {years[0]} - {years[-1]}",
                                        id="collapse-years-button",
                                        className="m-2",
                                        color="info",
                                        # block=True,
                                        children=[
                                            dbc.Card(
                                                dcc.RangeSlider(
                                                    id="year_slider",
                                                    min=0,
                                                    max=len(years) - 1,
                                                    step=None,
                                                    marks={
                                                        index: str(year)
                                                        for index, year in enumerate(
                                                            years
                                                        )
                                                    },
                                                    value=[0, len(years) - 1],
                                                ),
                                                style={
                                                    "maxHeight": "250px",
                                                    "minWidth": "500px",
                                                },
                                                className="overflow-auto",
                                                body=True,
                                            ),
                                        ],
                                    ),
                                    #TODO: how to handle the country profiles in the Generic version?
                                    # dcc.Dropdown(
                                    #     id="country_profile_selector",
                                    #     options=get_search_countries(False),
                                    #     value="ALB",
                                    #     multi=False,
                                    #     placeholder="Select a country...",
                                    #     className="m-2",
                                    #     style=country_dropdown_style,
                                    # ),
                                    dbc.DropdownMenu(
                                        # label=f"Countries: {len(countries)}",
                                        label=f"{get_ml(lang, 'REF_AREA')}: {str(len(ref_area_tree['checked']))}",
                                        id="collapse-countries-button",
                                        className="m-2",
                                        color="info",
                                        style=countries_filter_style,
                                        children=[
                                            dbc.Card(
                                                dash_treeview_antd.TreeView(
                                                    id="country_selector",
                                                    multiple=True,
                                                    checkable=True,
                                                    checked=ref_area_tree["checked"],
                                                    # selected=[],
                                                    expanded=["0"],
                                                    data=ref_area_tree["tree"],

                                                ),
                                                style={
                                                    "maxHeight": "250px",
                                                    # "maxWidth": "300px",
                                                },
                                                className="overflow-auto",
                                                body=True,
                                            ),
                                        ],
                                    ),
                                    dbc.FormGroup(
                                        [
                                            dbc.Checkbox(
                                                id="programme-toggle",
                                                className="custom-control-input",
                                            ),
                                            dbc.Label(
                                                "UNICEF Country Programmes",
                                                html_for="programme-toggle",
                                                className="custom-control-label",
                                                color="primary",
                                            ),
                                        ],
                                        className="custom-control custom-switch m-2",
                                        check=True,
                                        inline=True,
                                        style=programme_toggle_style,
                                    ),
                                ],
                                id="filter-row",
                                no_gutters=True,
                                justify="center",
                            ),
                        ]
                    ),
                ],
                # sticky="top",
                className="sticky-top bg-light",
            ),
            dbc.Row(
                [
                    dbc.CardDeck(
                        id="cards_row",
                        className="mt-3",
                    ),
                ],
                justify="center",
            ),
            html.Br(),
            dbc.CardDeck(
                [make_area(area) for area in ["MAIN"]],
                style=main_area_style,
            ),
            html.Br(),
            dbc.CardDeck(
                [make_area(area) for area in ["AREA_1", "AREA_2"]],
            ),
            html.Br(),
            dbc.CardDeck(
                [make_area(area) for area in ["AREA_3", "AREA_4"]],
            ),
            html.Br(),
            dbc.CardDeck(
                [make_area(area) for area in ["AREA_5", "AREA_6"]],
            ),
            html.Br(),
        ],
    )


def make_card(
        card_id,
        name,
        suffix,
        indicator_sources,
        source_link,
        indicator_header,
        numerator_pairs,
):
    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H1(
                        indicator_header,
                        className="display-4",
                        style={
                            # "fontSize": 50,
                            "textAlign": "center",
                            "color": "#1cabe2",
                        },
                    ),
                    html.H4(suffix, className="card-title"),
                    html.P(name, className="lead"),
                    html.Div(
                        fa("fas fa-info-circle"),
                        id=f"{card_id}_info",
                        # className="float-right",
                        style={
                            "position": "absolute",
                            "bottom": "10px",
                            "right": "10px",
                        },
                    ),
                ],
                style={
                    # "fontSize": 50,
                    "textAlign": "center",
                },
            ),
            dbc.Popover(
                [
                    dbc.PopoverHeader(
                        html.A(
                            html.P(f"Sources: {indicator_sources}"),
                            href=source_link,
                            target="_blank",
                        )
                    ),
                    dbc.PopoverBody(
                        dcc.Markdown(get_card_popover_body(numerator_pairs))
                    ),
                ],
                id="hover",
                target=f"{card_id}_info",
                trigger="hover",
            ),
        ],
        color="primary",
        outline=True,
        id=card_id,
    )
    return card


def get_card_popover_body(sources):
    """This function is used to generate the list of countries that are part of the card's
        displayed result; it displays the countries as a list, each on a separate line

    Args:
        sources (_type_): _description_

    Returns:
        _type_: _description_
    """
    countries = []
    # lbassil: added this condition to stop the exception when sources is empty
    if len(sources) > 0:
        for index, source_info in sources.sort_values(by="OBS_VALUE").iterrows():
            countries.append(f"- {index[0]}, {source_info[0]} ({index[1]})")
        card_countries = "\n".join(countries)
        return card_countries
    else:
        return "NA"


'''
@app.callback(
    Output({"type": "area_parent", "index": MATCH}, "hidden"),
    Input("theme", "hash"),
    [
        State("page_config", "data"),
        State({"type": "area_parent", "index": MATCH}, "id"),
    ],
)
def display_areas(theme, page_config, id):
    print("Theme")
    print(theme)
    print("id")
    print(id)
    print("page c")
    print(page_config)
    area = id["index"]
    themes = page_config["THEMES"]
    theme = theme[1:].upper() if theme else next(iter(themes.keys()))
    return area not in themes[theme]
'''

@app.callback(
    Output("subtitle", "children"),
    [Input('url','pathname')]
)
def url_params(pathname):
    print("pathname")
    print(pathname)

'''
@app.callback(
    Output("subtitle", "children"),
    Output("themes", "children"),
    [
        Input("store", "data"),
        Input("country_profile_selector", "value"),
    ],
    State("indicators", "data"),
)
def show_themes(selections, selected_country, indicators_dict):
    # check if it is the country profile page
    is_country_profile = selections["theme"] == "COUNTRYPROFILE"
    ctx = dash.callback_context
    ctrl_id = ctx.triggered[0]["prop_id"].split(".")[0]
    # check if the countries dropdown is causing this callback in order to set the sub-title to the country's name
    if is_country_profile or ctrl_id == "countries":
        key_list = list(countries_iso3_dict.keys())
        val_list = list(countries_iso3_dict.values())
        subtitle = (
            key_list[val_list.index(selected_country)]
            if selected_country
            else "Country Name"
        )
        return subtitle, []

    subtitle = indicators_dict[selections["theme"]].get("NAME")
    url_hash = "#{}".format((next(iter(selections.items())))[1].lower())
    # hide the buttons when only one option is available
    if len(indicators_dict.items()) == 1:
        return subtitle, []
    buttons = [
        dbc.Button(
            value["NAME"],
            id=key,
            color=colours[num],
            className="theme mx-1",
            href=f"#{key.lower()}",
            active=url_hash == f"#{key.lower()}",
        )
        for num, (key, value) in enumerate(indicators_dict.items())
    ]
    return subtitle, buttons
'''

'''
# TODO: Move to client side call back
@app.callback(
    Output("collapse-years", "is_open"),
    Output("collapse-countries", "is_open"),
    Output("collapse-engagements", "is_open"),
    [
        Input("collapse-years-button", "n_clicks"),
        Input("collapse-countries-button", "n_clicks"),
        Input("collapse-engagements-button", "n_clicks"),
    ],
    [
        State("collapse-years-button", "is_open"),
        State("collapse-countries-button", "is_open"),
        State("collapse-engagements-button", "is_open"),
    ],
)
def toggle_collapse(n1, n2, n3, is_open1, is_open2, is_open3):
    ctx = dash.callback_context

    if not ctx.triggered:
        return False, False, False
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "collapse-years-button" and n1:
        return not is_open1, False, False
    elif button_id == "collapse-countries-button" and n2:
        return False, not is_open2, False
    elif button_id == "collapse-engagements-button" and n3:
        return False, False, not is_open3
    return False, False, False





@app.callback(
    Output("store", "data"),
    Output("country_selector", "checked"),
    Output("programme-toggle", "checked"),
    Output("collapse-years-button", "label"),
    Output("collapse-countries-button", "label"),
    [
        Input("theme", "hash"),
        Input("year_slider", "value"),
        Input("country_selector", "checked"),
        Input("programme-toggle", "checked"),
        Input("country_profile_selector", "value"),
    ],
    State("indicators", "data"),
)
def apply_filters(
    theme,
    years_slider,
    country_selector,
    programme_toggle,
    selected_country,
    indicators,
):
    ctx = dash.callback_context
    selected = ctx.triggered[0]["prop_id"].split(".")[0]
    countries_selected = set()
    current_theme = theme[1:].upper() if theme else next(iter(indicators.keys()))
    # check if it is the country profile page
    is_country_profile = current_theme == "COUNTRYPROFILE"
    # check if the user clicked on the generate button in the country profile page
    if is_country_profile:
        key_list = list(countries_iso3_dict.keys())
        val_list = list(countries_iso3_dict.values())
        # get the name of the selected country in the dropdown to filter the data accordingly
        countries_selected = (
            [key_list[val_list.index(selected_country)]] if selected_country else []
        )
    elif programme_toggle and selected == "programme-toggle":
        countries_selected = unicef_country_prog
        country_selector = programme_country_indexes
    # Add the condition to know when the user unchecks the UNICEF country programs!
    elif not country_selector or (
        not programme_toggle and selected == "programme-toggle"
    ):
        countries_selected = countries
        # Add this to check all the items in the selection tree
        country_selector = ["0"]
    else:
        for index in country_selector:
            countries_selected.update(selection_index[index])
            if countries_selected == countries:
                # if all countries are all selected then stop
                break

    countries_selected = list(countries_selected)
    country_text = f"{len(countries_selected)} Selected"
    # need to include the last selected year as it was exluded in the previous method
    selected_years = years[years_slider[0] : years_slider[1] + 1]
    # selected_years = years[slice(*years_slider)]

    # Use the dictionary to return the values of the selected countries based on the SDMX ISO3 codes
    countries_selected_codes = [
        countries_iso3_dict[country] for country in countries_selected
    ]
    selections = dict(
        theme=current_theme,
        indicators_dict=indicators,
        years=selected_years,
        countries=countries_selected_codes,
        is_adolescent=("ADOLESCENT" in indicators),
    )

    return (
        selections,
        country_selector,
        countries_selected == unicef_country_prog,
        f"Years: {selected_years[0]} - {selected_years[-1]}",
        "Countries: {}".format(country_text),
    )


def indicator_card(
    selections,
    card_id,
    name,
    numerator,
    suffix,
    denominator=None,
    absolute=False,
    average=False,
    min_max=False,
    sex_code=None,
    age_group=None,
):
    indicators = numerator.split(",")

    # TODO: Change to use albertos config
    # lbassil: had to change this to cater for 2 dimensions set to the indicator card like age and sex
    breakdown = "TOTAL"
    # define the empty dimensions dict to be filled based on the card data filters
    dimensions = {}
    if age_group is not None:
        dimensions["AGE"] = [age_group]
    if sex_code is not None:
        dimensions["SEX"] = [sex_code]

    filtered_data = get_filtered_dataset(
        indicators,
        selections["years"],
        selections["countries"],
        breakdown,
        dimensions,
        latest_data=True,
    )

    df_indicator_sources = df_sources[df_sources["Code"].isin(indicators)]
    unique_indicator_sources = df_indicator_sources["Source_Full"].unique()
    indicator_sources = (
        "; ".join(list(unique_indicator_sources))
        if len(unique_indicator_sources) > 0
        else ""
    )
    source_link = (
        df_indicator_sources["Source_Link"].unique()[0]
        if len(unique_indicator_sources) > 0
        else ""
    )
    # lbassil: add this check because we are getting an exception where there is no data; i.e. no totals for all dimensions mostly age for the selected indicator
    if filtered_data.empty:
        indicator_header = "No data"
        indicator_sources = "NA"
        numerator_pairs = []
        return make_card(
            card_id,
            name,
            indicator_header,
            indicator_sources,
            source_link,
            numerator_pairs,
        )

    # select last value for each country
    indicator_values = (
        filtered_data.groupby(
            [
                "Country_name",
                "TIME_PERIOD",
            ]
        ).agg({"OBS_VALUE": "sum", "CODE": "count"})
    ).reset_index()

    numerator_pairs = (
        indicator_values[indicator_values.CODE == len(indicators)]
        .groupby("Country_name", as_index=False)
        .last()
        .set_index(["Country_name", "TIME_PERIOD"])
    )

    if suffix.lower() == "countries":
        # this is a hack to accomodate small cases (to discuss with James)
        if "FREE" in numerator:
            # trick to filter number of years of free education
            indicator_sum = (numerator_pairs.OBS_VALUE >= 1).to_numpy().sum()
            sources = numerator_pairs.index.tolist()
            numerator_pairs = numerator_pairs[numerator_pairs.OBS_VALUE >= 1]
        elif absolute:
            # trick cards data availability among group of indicators and latest time_period
            # doesn't require filtering by count == len(numors)
            numerator_pairs = indicator_values.groupby(
                "REF_AREA", as_index=False
            ).last()
            max_time_filter = (
                numerator_pairs.TIME_PERIOD < numerator_pairs.TIME_PERIOD.max()
            )
            numerator_pairs.drop(numerator_pairs[max_time_filter].index, inplace=True)
            numerator_pairs.set_index(["REF_AREA", "TIME_PERIOD"], inplace=True)
            sources = numerator_pairs.index.tolist()
            indicator_sum = len(sources)
        else:
            # trick to accomodate cards for admin exams (AND for boolean indicators)
            # filter exams according to number of indicators
            indicator_sum = (
                (numerator_pairs.OBS_VALUE == len(indicators)).to_numpy().sum()
            )
            sources = numerator_pairs.index.tolist()

    else:
        indicator_sum = numerator_pairs["OBS_VALUE"].to_numpy().sum()
        sources = numerator_pairs.index.tolist()
        if average and len(sources) > 1:
            indicator_sum = indicator_sum / len(sources)

    # define indicator header text: the resultant number except for the min-max range
    if min_max and len(sources) > 1:
        indicator_min = "{:,.1f}".format(numerator_pairs["OBS_VALUE"].min())
        indicator_max = "{:,.1f}".format(numerator_pairs["OBS_VALUE"].max())
        indicator_header = f"[{indicator_min} - {indicator_max}]"
    else:
        indicator_header = "{:,.0f}".format(indicator_sum)

    return make_card(
        card_id,
        name,
        suffix,
        indicator_sources,
        source_link,
        indicator_header,
        numerator_pairs,
    )


@app.callback(
    Output("cards_row", "children"),
    [
        Input("store", "data"),
    ],
    [State("cards_row", "children"), State("indicators", "data")],
)
def show_cards(selections, current_cards, indicators_dict):
    cards = [
        indicator_card(
            selections,
            f"card-{num}",
            card["name"],
            card["indicator"],
            card["suffix"],
            card.get("denominator"),
            card.get("absolute"),
            card.get("average"),
            card.get("min_max"),
            card.get("sex"),
            card.get("age"),
        )
        for num, card in enumerate(indicators_dict[selections["theme"]]["CARDS"])
    ]
    return cards


@app.callback(
    Output("subtitle", "children"),
    Output("themes", "children"),
    [
        Input("store", "data"),
        Input("country_profile_selector", "value"),
    ],
    State("indicators", "data"),
)
def show_themes(selections, selected_country, indicators_dict):
    # check if it is the country profile page
    is_country_profile = selections["theme"] == "COUNTRYPROFILE"
    ctx = dash.callback_context
    ctrl_id = ctx.triggered[0]["prop_id"].split(".")[0]
    # check if the countries dropdown is causing this callback in order to set the sub-title to the country's name
    if is_country_profile or ctrl_id == "countries":
        key_list = list(countries_iso3_dict.keys())
        val_list = list(countries_iso3_dict.values())
        subtitle = (
            key_list[val_list.index(selected_country)]
            if selected_country
            else "Country Name"
        )
        return subtitle, []

    subtitle = indicators_dict[selections["theme"]].get("NAME")
    url_hash = "#{}".format((next(iter(selections.items())))[1].lower())
    # hide the buttons when only one option is available
    if len(indicators_dict.items()) == 1:
        return subtitle, []
    buttons = [
        dbc.Button(
            value["NAME"],
            id=key,
            color=colours[num],
            className="theme mx-1",
            href=f"#{key.lower()}",
            active=url_hash == f"#{key.lower()}",
        )
        for num, (key, value) in enumerate(indicators_dict.items())
    ]
    return subtitle, buttons


@app.callback(
    Output({"type": "area_title", "index": MATCH}, "children"),
    Output({"type": "area_options", "index": MATCH}, "options"),
    Output({"type": "area_types", "index": MATCH}, "options"),
    Output({"type": "area_options", "index": MATCH}, "value"),
    Output({"type": "area_types", "index": MATCH}, "value"),
    Input("store", "data"),
    [
        State("indicators", "data"),
        State({"type": "area_options", "index": MATCH}, "id"),
    ],
)
def set_options(theme, indicators_dict, id):

    area = id["index"]

    area_options = area_types = []
    if area in indicators_dict[theme["theme"]]:
        indicators = indicators_dict[theme["theme"]][area].get("indicators")
        area_indicators = indicators.keys() if indicators is dict else indicators
        area_options = [
            {
                "label": indicator_names[code],
                "value": code,
            }
            for code in area_indicators
        ]

        area_types = [
            {
                "label": name.capitalize(),
                "value": name,
            }
            for name in indicators_dict[theme["theme"]][area].get("graphs", {}).keys()
        ]

    name = (
        indicators_dict[theme["theme"]][area].get("name")
        if area in indicators_dict[theme["theme"]]
        else ""
    )
    default_option = (
        indicators_dict[theme["theme"]][area].get("default")
        if area in indicators_dict[theme["theme"]]
        else ""
    )
    default_graph = (
        indicators_dict[theme["theme"]][area].get("default_graph")
        if area in indicators_dict[theme["theme"]]
        else ""
    )

    return name, area_options, area_types, default_option, default_graph


@app.callback(
    Output({"type": "area_breakdowns", "index": MATCH}, "options"),
    [
        Input({"type": "area_options", "index": MATCH}, "value"),
        Input({"type": "area_types", "index": MATCH}, "value"),
    ],
    [
        State({"type": "area_breakdowns", "index": MATCH}, "id"),
    ],
)
def breakdown_options(indicator, fig_type, id):

    options = [{"label": "Total", "value": "TOTAL"}]
    # lbassil: change the disaggregation to use the names of the dimensions instead of the codes
    all_breakdowns = [
        {"label": "Sex", "value": "SEX"},
        {"label": "Age", "value": "AGE"},
        {"label": "Residence", "value": "RESIDENCE"},
        {"label": "Wealth Quintile", "value": "WEALTH_QUINTILE"},
    ]
    dimensions = indicators_config.get(indicator, {}).keys()
    # keep only TOTAL for line charts
    if dimensions and fig_type != "line":
        for breakdown in all_breakdowns:
            if breakdown["value"] in dimensions:
                options.append(breakdown)
    return options


@app.callback(
    Output({"type": "area_breakdowns", "index": MATCH}, "value"),
    [
        Input("store", "data"),
        Input({"type": "area_breakdowns", "index": MATCH}, "options"),
        Input({"type": "area_types", "index": MATCH}, "value"),
    ],
    [
        State("indicators", "data"),
        State({"type": "area_breakdowns", "index": MATCH}, "id"),
    ],
)
def set_default_compare(
    selections, compare_options, selected_type, indicators_dict, id
):
    area = id["index"]
    # lbassil: add this condition to stop the exception for the main area
    if area in indicators_dict[selections["theme"]] and area != "MAIN":
        default = indicators_dict[selections["theme"]][area]["default_graph"]
        fig_type = selected_type if selected_type else default
        config = indicators_dict[selections["theme"]][area]["graphs"][fig_type]
        default_compare = config.get("compare")

        return (
            "TOTAL"
            if fig_type == "line" or default_compare is None
            else default_compare
            if default_compare in compare_options
            else compare_options[1]["value"]
            if len(compare_options) > 1
            else compare_options[0]["value"]
        )
    return "TOTAL"


@app.callback(
    Output("main_area", "figure"),
    Output("main_area_sources", "children"),
    [
        Input({"type": "area_options", "index": "MAIN"}, "value"),
        Input({"type": "historical_data_toggle", "index": "MAIN"}, "value"),
        Input("store", "data"),
    ],
    [
        State("indicators", "data"),
    ],
)
def main_figure(indicator, show_historical_data, selections, indicators_dict):
    latest_data = not show_historical_data
    options = indicators_dict[selections["theme"]]["MAIN"]["options"]

    data = get_filtered_dataset(
        [indicator],
        selections["years"],
        selections["countries"],
        latest_data=latest_data,
    )

    # check if the dataframe is empty meaning no data to display as per the user's selection
    if data.empty:
        return EMPTY_CHART, ""

    # lbassil: replace UNIT_MEASURE by Unit_name to use the name of the unit instead of the code
    name = (
        data[data["CODE"] == indicator]["Unit_name"].astype(str).unique()[0]
        if len(data[data["CODE"] == indicator]["Unit_name"].astype(str).unique()) > 0
        else ""
    )
    df_indicator_sources = df_sources[df_sources["Code"] == indicator]
    unique_indicator_sources = df_indicator_sources["Source_Full"].unique()
    source = (
        "; ".join(list(unique_indicator_sources))
        if len(unique_indicator_sources) > 0
        else ""
    )
    source_link = (
        df_indicator_sources["Source_Link"].unique()[0]
        if len(unique_indicator_sources) > 0
        else ""
    )

    options["labels"] = DEFAULT_LABELS.copy()
    options["labels"]["OBS_VALUE"] = name
    options["labels"]["text"] = "OBS_VALUE"
    options["geojson"] = geo_json_countries
    if latest_data:
        # remove the animation frame and show all countries at once
        options.pop("animation_frame")
        # add the year to show on hover
        options["hover_name"] = "TIME_PERIOD"

    main_figure = px.choropleth_mapbox(data, **options)
    main_figure.update_layout(margin={"r": 0, "t": 1, "l": 2, "b": 1})

    # check if this area's config has an animation frame and hence a slider
    if len(main_figure.layout["sliders"]) > 0:
        # set last frame as the active one; i.e. select the max year as the default displayed year
        main_figure.layout["sliders"][0]["active"] = len(main_figure.frames) - 1
        # assign the data of the last year to the map; without this line the data will show the first year;
        main_figure = go.Figure(
            data=main_figure["frames"][-1]["data"],
            frames=main_figure["frames"],
            layout=main_figure.layout,
        )
    return main_figure, html.A(html.P(source), href=source_link, target="_blank")


@app.callback(
    Output({"type": "area", "index": MATCH}, "figure"),
    Output({"type": "area_sources", "index": MATCH}, "children"),
    [
        Input("store", "data"),
        Input({"type": "area_options", "index": MATCH}, "value"),
        Input({"type": "area_breakdowns", "index": MATCH}, "value"),
        Input({"type": "area_types", "index": MATCH}, "value"),
        Input({"type": "exclude_outliers_toggle", "index": MATCH}, "value"),
    ],
    [
        State("indicators", "data"),
        State({"type": "area_options", "index": MATCH}, "id"),
    ],
)
def area_figure(
    selections,
    indicator,
    compare,
    selected_type,
    exclude_outliers,
    indicators_dict,
    id,
):
    # only run if indicator not empty
    if not indicator:
        return {}, {}
    # check if it is the country profile page
    is_country_profile = selections["theme"] == "COUNTRYPROFILE"

    area = id["index"]
    indicators = indicators_dict[selections["theme"]][area]["indicators"]
    default_graph = indicators_dict[selections["theme"]][area].get(
        "default_graph", "line"
    )
    fig_type = selected_type if selected_type else default_graph
    fig_config = indicators_dict[selections["theme"]][area]["graphs"][fig_type]
    options = fig_config.get("options")
    traces = fig_config.get("trace_options")
    dimension = False if fig_type == "line" or compare == "TOTAL" else compare

    indicator_name = str(indicator_names.get(indicator, ""))
    # do we need `indicator_settings` below?
    indicator_settings = (
        indicators.get(indicator, {}) if type(indicators) is dict else {}
    )
    data = get_filtered_dataset(
        [indicator],
        selections["years"],
        selections["countries"],
        compare,
        latest_data=False if fig_type == "line" or is_country_profile else True,
    )
    # check if the dataframe is empty meaning no data to display as per the user's selection
    if data.empty:
        return EMPTY_CHART, ""

    # check if the exclude outliers checkbox is checked
    if exclude_outliers:
        # filter the data to the remove the outliers
        # (df < df.quantile(0.1)).any() (df > df.quantile(0.9)).any()
        data["z_scores"] = np.abs(zscore(data["OBS_VALUE"]))  # calculate z-scores of df
        # filter the data entries to remove the outliers
        data = data[(data["z_scores"] < 3) | (data["z_scores"].isnull())]

    # lbassil: was UNIT_MEASURE
    name = (
        data[data["CODE"] == indicator]["Unit_name"].astype(str).unique()[0]
        if len(data[data["CODE"] == indicator]["Unit_name"].astype(str).unique()) > 0
        else ""
    )
    df_indicator_sources = df_sources[df_sources["Code"] == indicator]
    unique_indicator_sources = df_indicator_sources["Source_Full"].unique()
    source = (
        "; ".join(list(unique_indicator_sources))
        if len(unique_indicator_sources) > 0
        else ""
    )
    source_link = (
        df_indicator_sources["Source_Link"].unique()[0]
        if len(unique_indicator_sources) > 0
        else ""
    )

    options["labels"] = DEFAULT_LABELS.copy()
    options["labels"]["OBS_VALUE"] = name

    # set the chart title, wrap the text when the indicator name is too long
    chart_title = textwrap.wrap(
        indicator_name,
        width=74,
    )
    chart_title = "<br>".join(chart_title)

    # set the layout to center the chart title and change its font size and color
    layout = go.Layout(
        title=chart_title,
        title_x=0.5,
        font=dict(family="Arial", size=12),
        legend=dict(x=0.9, y=0.5),
        xaxis={"categoryorder": "total descending"},
    )

    # Add this code to avoid having decimal year on the x-axis for time series charts
    if fig_type == "line" or is_country_profile:
        data.sort_values(by=["TIME_PERIOD", "Country_name"], inplace=True)
        layout["xaxis"] = dict(
            tickmode="linear",
            tick0=selections["years"][0],
            dtick=1,
            categoryorder="total ascending",
        )
        layout["legend"] = dict(y=0.5, x=1)

    if dimension:
        # lbassil: use the dimension name instead of the code
        dimension_name = str(dimension_names.get(dimension, ""))
        options["color"] = dimension_name
        if compare == "WEALTH_QUINTILE":
            wealth_dict = {
                "Lowest": 0,
                "Second": 1,
                "Middle": 2,
                "Fourth": 3,
                "Highest": 4,
            }
            data.sort_values(
                by=[dimension], key=lambda x: x.map(wealth_dict), inplace=True
            )
        else:
            # sort by the compare value to have the legend in the right ascending order
            data.sort_values(by=[dimension], inplace=True)

    fig = getattr(px, fig_type)(data, **options)
    fig.update_layout(layout)
    if traces:
        fig.update_traces(**traces)

    return fig, html.A(html.P(source), href=source_link, target="_blank")
    
    
    
'''
