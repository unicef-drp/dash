import textwrap

import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd
import numbers
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from dash import callback, dcc, html
from dash.dependencies import MATCH, Input, Output, State, ALL
from dash_service.models import Page, Project, Dashboard

from dash_service.pages import get_data, is_float, years, get_geojson
from dash_service.pages import (
    add_structure,
    get_structure_id,
    get_code_from_structure_and_dq,
    get_col_name,
    merge_with_codelist,
    get_multilang_value,
    is_string_empty,
)


from flask import abort
from sqlalchemy import and_

from dash_service.components_aio.card_aio import CardAIO
from dash_service.components_aio.map_aio import MapAIO
from dash_service.components_aio.chart_aio import ChartAIO
from dash_service.components_aio.downloads_aio import DownloadsAIO
from dash_service.components_aio.heading_aio import HeadingAIO
from dash_service.components_aio.pages_navigation_aio import PagesNavigationAIO
from dash_service.components_aio.years_range_selector_aio import YearsRangeSelectorAIO

import copy
import requests

# pd.set_option("display.max_columns", None)
# pd.set_option("display.max_rows", None)
# pd.set_option("display.width", 0)

# A few constant values
ID_INDICATOR = "INDICATOR"
ID_REF_AREA = "REF_AREA"
ID_OBS_VALUE = "OBS_VALUE"
ID_DATA_SOURCE = "DATA_SOURCE"
ID_TIME_PERIOD = "TIME_PERIOD"
LABEL_COL_PREFIX = "_L_"
DEFAULT_LABELS = ["OBS_VALUE", "TIME_PERIOD", "REF_AREA"]

ELEM_ID_PAGE_NAV = "PAGE_NAV"
ELEM_ID_YEARS_RANGE_SEL = "YEARS_RANGE_SEL"
ELEM_ID_CARDS = "CARDS"
ELEM_ID_MAIN = "MAIN"
ELEM_ID_CHARTS = "CHARTS"
ELEM_ID_HEADING = "HEADING"

CFG_N_THEMES = "THEMES"

DBELEM = "DBELEM_"


# set defaults
pio.templates.default = "plotly_white"
# px.defaults.color_continuous_scale = px.colors.sequential.BuGn
UNICEF_color_continuous_scale = [
    "#002759",
    "#00377D",
    "#0058AB",
    "#0083CF",
    "#1CABE2",
    "#69DBFF",
    "#A3EAFF",
    "#CFF4FF",
]
UNICEF_color_qualitative = [
    "#0058AB",
    "#1CABE2",
    "#00833D",
    "#80BD41",
    "#6A1E74",
    "#961A49",
    "#E2231A",
    "#F26A21",
    "#FFC20E",
    "#FFF09C",
]
# px.defaults.color_discrete_sequence = px.colors.qualitative.Dark24
px.defaults.color_discrete_sequence = UNICEF_color_qualitative
px.defaults.color_continuous_scale = UNICEF_color_continuous_scale

default_font_family = "Roboto"
default_font_size = 12


# move this elsewhere
translations = {
    "sources": {"en": "Sources", "pt": "Fontes"},
    "years": {"en": "Years", "pt": "Anos"},
    "show_historical": {"en": "Show historical data", "pt": "Mostrar série histórica"},
    "bar": {"en": "Bar", "pt": "Gráfico em colunas"},
    "line": {"en": "Line", "pt": "Gráfico em linhas"},
    "scatter": {"en": "Scatter", "pt": "Scatter PT"},
    "download_excel": {"en": "Download Excel", "pt": "Download Excel"},
    "download_csv": {"en": "Download CSV", "pt": "Download CSV"},
    "OBS_VALUE": {"en": "Value", "pt": "Valores"},
    "TIME_PERIOD": {"en": "Time period", "pt": "Ano"},
    "REF_AREA": {"pt": "Estado"},
}

# the configuration of the "Download plot" button in the charts
cfg_plot = {
    "toImageButtonOptions": {
        "format": "png",  # one of png, svg, jpeg, webp
        "filename": "plot",
        "width": 1200,
        "height": 800,
        "scale": 1,  # Multiply title/legend/axis/canvas sizes by this factor
    },
    "displayModeBar": True,
    "displaylogo": False,
}

colours = ["success", "warning", "danger", "info"]

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


# The entry point, retrieves the page from the storage and renderes the page
def layout(lang="en", **query_params):
    """
    Returns the page layout
    """

    project_slug = query_params.get("prj", None)
    page_slug = query_params.get("page", None)

    db_config = (
        Dashboard.query.join(Project)
        .filter(and_(Page.slug == page_slug, Project.slug == project_slug))
        .first()
    )

    page_config = db_config.content
    geography = db_config.geography

    return render_page_template(
        page_config, geography, lang, query_params, project_slug
    )


# Gets the element that will be rendered on the navigation bar
def get_page_nav_items(page_config, project_slug, lang):
    nav_type = None
    if "page_nav" in page_config and "type" in page_config["page_nav"]:
        nav_type = page_config["page_nav"]["type"]
    if nav_type is None:
        nav_type = "all"
    if nav_type == "all":
        nav_items = (
            Dashboard.query.with_entities(
                Dashboard.slug, Dashboard.title, Project.slug.label("prj_slug")
            )
            .join(Project)
            .filter(Project.slug == project_slug)
            .all()
        )

    ret = [
        {"name": ni.title, "prj_slug": ni.prj_slug, "slug": ni.slug, "lang": lang}
        for ni in nav_items
    ]
    return ret


def render_page_template(
    page_config: dict, geojson: str, lang: str, query_params, project_slug: str
) -> html.Div:

    elem_page_nav = None
    elem_main_title = None
    elem_years_selector = None

    nav_links = get_page_nav_items(page_config, project_slug, lang)

    if nav_links is not None and len(nav_links) > 0:
        elem_page_nav = PagesNavigationAIO(
            nav_links, query_params, aio_id=ELEM_ID_PAGE_NAV
        )

    if "main_title" in page_config:
        elem_main_title = HeadingAIO(page_config["main_title"], aio_id=ELEM_ID_HEADING)

    elem_years_selector = YearsRangeSelectorAIO(
        aio_id=ELEM_ID_YEARS_RANGE_SEL, additional_classes="pb-2"
    )

    ret = html.Div(
        [
            dcc.Store(id="lang", data=lang),  # stores the language
            dcc.Store(id="sel_state", data=None),  # stores the language
            dcc.Store(id="page_config", data=page_config),  # stores the page config
            dcc.Store(id="geoj", data=geojson),  # stores the geoJson
            dcc.Store(
                id="data_structures", data={}, storage_type="session"
            ),  # stores the data structure for caching
            dcc.Location(
                id="theme"
            ),  # controls the location hash (e.g. education#theme)
            elem_page_nav,
            elem_main_title,
            html.Div(
                className="bg-light mt-2",
                children=[
                    html.Div(
                        className="d-flex justify-content-center py-2",
                        children=[dbc.ButtonGroup(id="theme_buttons")],
                    ),
                    elem_years_selector,
                ],
            ),
            html.Div(id="dashboard_contents", className="mt-2", children=[]),
        ]
    )

    return ret


# Triggered when the theme or year slider changes
# It only updates the state of the selection: theme and year
@callback(
    Output("sel_state", "data"),
    Output(
        YearsRangeSelectorAIO.ids.years_range_open_collapse_btn(
            ELEM_ID_YEARS_RANGE_SEL
        ),
        "children",
    ),
    [
        Input("theme", "hash"),
        Input(
            YearsRangeSelectorAIO.ids.years_range(ELEM_ID_YEARS_RANGE_SEL),
            "value",
        ),
    ],
    [State("page_config", "data"), State("lang", "data")],
)
def new_selection_state(theme, years_slider, page_config, lang):

    # removes the leading # if a theme has been selected, the first theme available otherwise
    theme = theme[1:].upper() if theme else next(iter(page_config[CFG_N_THEMES].keys()))
    # The selected years range
    selected_years = [years_slider[0], years_slider[1]]

    selections = dict(theme=theme, years=selected_years)

    return (
        selections,
        f"{get_multilang_value(translations['years'], lang)}: {selected_years[0]} - {selected_years[-1]}",
    )


def _get_elem_id(row, col):
    return f"{DBELEM}{row}_{col}"


def _get_elem_cfg_pos(elem_id):
    return {
        "row": int(elem_id.split("_")[1]),
        "col": int(elem_id.split("_")[2]),
    }


# Triggered when the selection state changes
@callback(
    Output(HeadingAIO.ids.subtitle(ELEM_ID_HEADING), "children"),
    Output("theme_buttons", "children"),
    # Output("dashboard_contents", "children"),
    [
        Input("sel_state", "data"),
    ],
    State("page_config", "data"),
)
def show_themes(selections, config):
    # Gets the theme's name to fill the Subtitle
    if (
        selections is None
        or selections["theme"] is None
        or selections["theme"].strip() == ""
    ):
        theme_key = list(config[CFG_N_THEMES].keys())[0]
        theme_node = config[CFG_N_THEMES][theme_key]
    else:
        theme_key = selections["theme"]
        theme_node = config[CFG_N_THEMES][selections["theme"]]

    subtitle = theme_node.get("NAME", "")

    # Creates the Themes' buttons
    # hide the buttons when only one option is available
    if len(config[CFG_N_THEMES].items()) == 1:
        theme_buttons = None
    else:
        theme_buttons = [
            dbc.Button(
                value["NAME"],
                id=key,
                color=colours[num % len(colours)],
                className="theme mx-1",
                href=f"#{key.lower()}",
                active=theme_key == key,
            )
            for num, (key, value) in enumerate(config[CFG_N_THEMES].items())
        ]

    return subtitle, theme_buttons


@callback(
    Output("data_structures", "data"),
    [Input("sel_state", "data")],
    [State("page_config", "data"), State("lang", "data")],
)
# Downloads all the DSD for the data.
# Typically 1 dataflow per page but can handle data from multiple Dataflows in 1 page
def download_structures(selections, page_config, lang):
    data_structures = {}

    theme_node = page_config[CFG_N_THEMES][selections["theme"]]

    if "ROWS" in theme_node:
        for row in theme_node["ROWS"]:
            if "elements" in row:
                for elem in row["elements"]:
                    if "data" in elem:
                        if isinstance(elem["data"], dict):
                            add_structure(data_structures, elem["data"], lang)
                        elif isinstance(elem["data"], list):
                            for data_elem in elem["data"]:


                                if "multi_indicator" in data_elem:
                                    for multi_indic_node in data_elem["multi_indicator"]:
                                        add_structure(data_structures, multi_indic_node, lang)
                                else:


                                    add_structure(data_structures, data_elem, lang)

    return data_structures


def _create_card(data_struct, page_config, elem_info, lang):
    elem = elem_info["elem"]
    data_node = None
    if "data" in elem:
        data_node = elem["data"]
    value = "-"
    label = ""
    data_source = ""
    time_period = ""
    lbl_sources = get_multilang_value(translations["sources"], lang)
    lbl_time_period = get_multilang_value(translations["TIME_PERIOD"], lang)

    if is_string_empty(elem, "label"):
        label = get_code_from_structure_and_dq(data_struct, data_node, ID_INDICATOR)[
            "name"
        ]
    else:
        label = get_multilang_value(elem["label"], lang)

    if data_node is not None:
        # we only need the most recent datapoint, no labels, just the value
        try:
            df = get_data(data_node, lastnobservations=1, labels="id")
        #except ConnectionError as conn_err:
        except requests.exceptions.HTTPError as e:
            print_exception("Exception while downloading data for card", e)
            df = pd.DataFrame()

        if len(df) > 0:
            value = df.iloc[0][ID_OBS_VALUE]
            if "round" in elem and is_float(value):
                value = round(float(value), elem["round"])

            time_period = df.iloc[0][ID_TIME_PERIOD]
            if ID_DATA_SOURCE in df.columns:
                data_source = df.iloc[0][ID_DATA_SOURCE]

    ret = html.Div(
        # className="col",
        children=CardAIO(
            aio_id=elem_info["elem_id"],
            value=value,
            suffix=label,
            info_head=lbl_sources,
            info_body=data_source,
            time_period=time_period,
            lbl_time_period=lbl_time_period,
        ),
    )

    return ret


# loops the data node and returns the options for the dropdownlists: options + default value
def get_ddl_values(data_node, data_structures, column_id, lang):
    items = []
    default_item = ""
    for idx, data_cfg in enumerate(data_node):
        # is it there a label? Override the one read from the data
        if not is_string_empty(data_cfg):
            lbl = get_multilang_value(data_cfg["label"], lang)
        elif "multi_indicator" in data_cfg:
            labels = []
            for multi_cfg in data_cfg["multi_indicator"]:
                tmp_lbl = get_code_from_structure_and_dq(
                    data_structures, multi_cfg, column_id
                )["name"]
                labels.append(tmp_lbl)
            lbl = " - ".join(labels)

        else:
            lbl = get_code_from_structure_and_dq(data_structures, data_cfg, column_id)[
                "name"
            ]

        items.append({"label": lbl, "value": str(idx)})
        if idx == 0:
            default_item = str(idx)
    return items, default_item


def _create_chart_placeholder(data_struct, page_config, elem_info, lang):
    elem = elem_info["elem"]
    title = elem.get("label", "")
    # The dropdownlist elements
    ddl_items, default_item = get_ddl_values(
        elem["data"], data_struct, ID_INDICATOR, lang
    )

    # The chart types
    chart_types = []
    if "graphs" in elem:
        for type_key in elem["graphs"].keys():
            type_lbl = type_key
            if type_key.lower() in translations:
                type_lbl = get_multilang_value(translations[type_key.lower()], lang)
            chart_types.append(
                {
                    "label": type_lbl,
                    "value": type_key,
                }
            )
    default_graph = elem.get("default_graph", "")

    ret = ChartAIO(
        aio_id=elem_info["elem_id"],
        title=title,
        plot_cfg=cfg_plot,
        info_title=get_multilang_value(translations["sources"], lang),
        lbl_excel=get_multilang_value(translations["download_excel"], lang),
        lbl_csv=get_multilang_value(translations["download_csv"], lang),
        dropdownlist_options=ddl_items,
        dropdownlist_value=default_item,
        chart_types=chart_types,
        default_graph=default_graph,
    )

    # return html.Div(className="col", children=ret)
    return html.Div(children=ret)


def _create_map_placeholder(data_struct, page_config, elem_info, lang):
    elem = elem_info["elem"]
    title = elem.get("label", "")
    ddl_items, default_item = get_ddl_values(
        elem["data"], data_struct, ID_INDICATOR, lang
    )

    ret = MapAIO(
        aio_id=elem_info["elem_id"],
        title=title,
        plot_cfg=cfg_plot,
        info_title=get_multilang_value(translations["sources"], lang),
        lbl_show_hist=get_multilang_value(translations["show_historical"], lang),
        lbl_excel=get_multilang_value(translations["download_excel"], lang),
        lbl_csv=get_multilang_value(translations["download_csv"], lang),
        dropdownlist_options=ddl_items,
        dropdownlist_value=default_item,
    )

    # return html.Div(className="col", children=ret)
    return html.Div(children=ret)


def _create_elem(data_struct, page_config, elem_info, lang):
    elem = elem_info["elem"]
    ret = None
    if not "type" in elem:
        ret = html.Div(
            className="col",
            children=[
                f"No type for elem at row {elem_info['idx_row']} - position {elem_info['idx_elem']}"
            ],
            id=elem_info["elem_id"],
        )
        return ret

    if elem["type"] == "card":
        ret = _create_card(data_struct, page_config, elem_info, lang)
    elif elem["type"] == "chart":
        ret = _create_chart_placeholder(data_struct, page_config, elem_info, lang)
    elif elem["type"] == "map":
        ret = _create_map_placeholder(data_struct, page_config, elem_info, lang)

    return ret


@callback(
    Output("dashboard_contents", "children"),
    [Input("data_structures", "data")],
    [State("sel_state", "data"), State("page_config", "data"), State("lang", "data")],
)
def create_elements(data_struct, selections, page_config, lang):
    bootstrap_cols_map = {
        "1": "col",
        "2": "col-lg-6 col-sm-12",
        "3": "col-lg-4 col-sm-12",
        "4": "col-lg-3 col-sm-12",
        "5": "col-lg-2 col-sm-6",
        "6": "col-lg-2 col-sm-6",
    }
    theme_node = page_config[CFG_N_THEMES][selections["theme"]]

    dashboard_contents = []

    elem_rows = {}

    elems_to_create = []
    if "ROWS" in theme_node:
        for idx_row, row in enumerate(theme_node["ROWS"]):
            for idx_elem, elem in enumerate(row["elements"]):
                elems_to_create.append(
                    {
                        "idx_row": idx_row,
                        "idx_elem": idx_elem,
                        "elem": elem,
                        "elem_id": _get_elem_id(idx_row, idx_elem),
                        "elem_per_row": len(row["elements"]),
                    }
                )

    for elem_info in elems_to_create:
        idx_key = str(elem_info["idx_row"])
        if not idx_key in elem_rows:
            elem_rows[idx_key] = []

        bs_col = bootstrap_cols_map.get(str(elem_info["elem_per_row"]), "col-1")
        elem = _create_elem(data_struct, page_config, elem_info, lang)
        elem = html.Div(className=bs_col, children=elem)
        elem_rows[idx_key].append(elem)

    for elem_row_k in sorted(elem_rows.keys()):
        dashboard_contents.append(
            html.Div(className="row mb-4", children=elem_rows[elem_row_k])
        )

    return dashboard_contents


# Util function: creates the label node for the chart configs
def get_labels(data_structs, struct_id, df_cols, lang, lbl_override):
    labels = {}
    for col in df_cols:
        # check if there is a _L_ col meaning that there is an original column + a label one for the coded column
        if not col.startswith(LABEL_COL_PREFIX):
            labels[col] = get_col_name(data_structs, struct_id, col, lang, lbl_override)
            if LABEL_COL_PREFIX + col in df_cols:
                labels[LABEL_COL_PREFIX + col] = labels[col]
    return labels


# Triggered when the selection changes. Updates the charts.
@callback(
    Output(ChartAIO.ids.chart(MATCH), "figure"),
    Output(ChartAIO.ids.info_text(MATCH), "children"),
    Output(ChartAIO.ids.info_icon(MATCH), "style"),
    [
        Input(ChartAIO.ids.ddl(MATCH), "value"),
        Input(ChartAIO.ids.chart_types(MATCH), "value"),
    ],
    [
        State("data_structures", "data"),
        State("sel_state", "data"),
        State("page_config", "data"),
        State(ChartAIO.ids.card_title(MATCH), "id"),
        State("lang", "data"),
    ],
)
def update_charts(
    ddl_value, chart_type, data_structures, selection, page_config, component_id, lang
):
    selected_theme = selection["theme"]
    elem_cfg_pos = _get_elem_cfg_pos(component_id["aio_id"])

    # find the elem matching the updated item in the page config
    elem = page_config[CFG_N_THEMES][selected_theme]["ROWS"][elem_cfg_pos["row"]][
        "elements"
    ][elem_cfg_pos["col"]]

    # find the data node in the configuration for the user's selection
    data_cfg = elem["data"][int(ddl_value)]
    # the selected time period
    time_period = [min(selection["years"]), max(selection["years"])]
    # Fallback to a default chart type if not selected
    if chart_type is None or chart_type == "":
        chart_type = elem.get(["default_graph"], "bar")

    fig_config = elem["graphs"][chart_type]
    options = fig_config.get("options")
    traces = fig_config.get("trace_options")

    df = pd.DataFrame()
    indicator_name = ""
    indic_labels = {}

    if "multi_indicator" in data_cfg:
        tmp_inidic_label = []
        for multi_indic_cfg in data_cfg["multi_indicator"]:
            try:
                data_chunk = get_data(multi_indic_cfg, years=time_period)
            except requests.exceptions.HTTPError as e:
                print_exception("Exception while downloading data for charts in multi indicator", e)
                data_chunk = pd.DataFrame()
            struct_id = get_structure_id(multi_indic_cfg)
            data_chunk = merge_with_codelist(
                data_chunk, data_structures, struct_id, ID_REF_AREA
            )
            data_chunk = merge_with_codelist(
                data_chunk, data_structures, struct_id, ID_DATA_SOURCE
            )
            indic_code = get_code_from_structure_and_dq(
                data_structures, multi_indic_cfg, ID_INDICATOR
            )
            indic_labels[indic_code["id"]] = indic_code["name"]
            tmp_inidic_label.append(indic_code["name"])
            df = pd.concat([df, data_chunk])
        tmp_inidic_label = list(set(tmp_inidic_label))  # remove duplicates
        indicator_name = " - ".join(tmp_inidic_label)
    else:
        lastnobservations=None
        if chart_type == "line":
            lastnobservations=None
        else:
            lastnobservations=1

        try:
            df = get_data(data_cfg, years=time_period, lastnobservations=lastnobservations)
        except requests.exceptions.HTTPError as e:
            print_exception("Exception while downloading data for charts", e)
            df = pd.DataFrame()

        struct_id = get_structure_id(data_cfg)
        # Assign labels to codes
        df = merge_with_codelist(df, data_structures, struct_id, ID_REF_AREA)
        df = merge_with_codelist(df, data_structures, struct_id, ID_DATA_SOURCE)
        indicator_name = get_code_from_structure_and_dq(
            data_structures, data_cfg, ID_INDICATOR
        )["name"]

    if df.empty:
        return EMPTY_CHART, ""

    df[ID_OBS_VALUE] = pd.to_numeric(df[ID_OBS_VALUE], errors="coerce")
    df[ID_TIME_PERIOD] = pd.to_numeric(df[ID_TIME_PERIOD], errors="coerce")

    # The source icon and information
    source = ""
    display_source = {"display": "none"}
    if LABEL_COL_PREFIX + ID_DATA_SOURCE in df.columns:
        source = ", ".join(list(df[LABEL_COL_PREFIX + ID_DATA_SOURCE].unique()))
    if source != "":
        display_source = {"display": "visible"}

    # Change the labels to the option codes (in options we have REF_AREA, TIME_PERIOD replace with the concept's label)
    options_to_check_for_label = ["x", "y", "text", "color", "hover_name"]
    for o in options_to_check_for_label:
        if o in options and LABEL_COL_PREFIX + options[o] in df.columns:
            options[o] = LABEL_COL_PREFIX + options[o]
    options["labels"] = get_labels(
        data_structures, struct_id, df.columns, lang, translations
    )
    for k, v in indic_labels.items():
        options["labels"][k] = v

    if "label" in elem["data"][int(ddl_value)]:
        indicator_name = get_multilang_value(
            elem["data"][int(ddl_value)]["label"], lang
        )

    # set the chart title, wrap the text when the indicator name is too long
    chart_title = textwrap.wrap(
        indicator_name,
        width=55,
    )

    chart_title = "<br>".join(chart_title)

    xaxis = {"categoryorder": "total descending"}
    if chart_type == "line":
        xaxis["tickformat"] = "d"
    elif chart_type == "scatter":
        keep_cols = ["REF_AREA", "_L_REF_AREA"]
        df_scatter = pd.pivot_table(
            df, values=ID_OBS_VALUE, index=keep_cols, columns=[ID_INDICATOR]
        )
        df = df_scatter.reset_index()

        options["hover_data"] = ["_L_REF_AREA"]

    if "color_discrete_sequence" not in options:
        options["color_discrete_sequence"] = UNICEF_color_qualitative

    # set the layout to center the chart title and change its font size and color
    layout = go.Layout(
        title=chart_title,
        title_x=0.5,
        font=dict(family=default_font_family, size=default_font_size),
        legend=dict(x=0.9, y=0.5),
        xaxis=xaxis,
        modebar={"orientation": "v"},
    )

    fig = getattr(px, chart_type)(df, **options)
    fig.update_layout(layout)

    if traces:
        fig.update_traces(**traces)

    return fig, source, display_source


# Triggered when the Map area changes: show historical data is changed or indicator selected
@callback(
    Output(MapAIO.ids.graph(MATCH), "figure"),
    Output(MapAIO.ids.info_text(MATCH), "children"),
    Output(MapAIO.ids.info_icon(MATCH), "style"),
    Output(MapAIO.ids.map_timpe_period(MATCH), "children"),
    [
        Input(MapAIO.ids.ddl(MATCH), "value"),
        Input(MapAIO.ids.toggle_historical(MATCH), "value"),
        # Input("data_structures", "data"),
    ],
    [
        Input("data_structures", "data"),
        State("sel_state", "data"),
        State("page_config", "data"),
        State("geoj", "data"),
        State(MapAIO.ids.card_title(MATCH), "id"),
        State("lang", "data"),
    ],
)
def update_maps(
    ddl_value,
    show_historical_data,
    data_structs,
    selections,
    page_config,
    geoj,
    component_id,
    lang,
):
    # Ret
    fig = None
    source = None
    display_source = None
    time_periods_in_df = None

    selected_theme = selections["theme"]
    elem_cfg_pos = _get_elem_cfg_pos(component_id["aio_id"])
    # find the elem matching the updated item in the page config
    elem = page_config[CFG_N_THEMES][selected_theme]["ROWS"][elem_cfg_pos["row"]][
        "elements"
    ][elem_cfg_pos["col"]]
    # find the data node in the configuration for the user's selection
    elem_data_node = elem["data"][int(ddl_value)]
    elem_options_node = copy.deepcopy(elem["options"])

    time_period = [min(selections["years"]), max(selections["years"])]
    lastnobs = None
    if not show_historical_data:
        lastnobs = 1

    try:
        df = get_data(elem_data_node, years=time_period, lastnobservations=lastnobs)
    except requests.exceptions.HTTPError as e:
        print_exception("Exception while downloading data for maps", e)
        df = pd.DataFrame()
    
    if df.empty:
        return EMPTY_CHART, "", "", ""

    # we need the ref_area and data source codelists (DATA_SOURCE can be coded)
    # get and merge the ref area labels
    struct_id = get_structure_id(elem_data_node)
    df = merge_with_codelist(df, data_structs, struct_id, ID_REF_AREA)
    if ID_DATA_SOURCE in df.columns:
        df = merge_with_codelist(df, data_structs, struct_id, ID_DATA_SOURCE)
    df[ID_OBS_VALUE] = pd.to_numeric(df[ID_OBS_VALUE])
    df = df.sort_values(by=ID_TIME_PERIOD, ascending=True)

    # The data sources, hide the icon if data source is ""
    source = ""
    display_source = {"display": "none"}
    if ID_DATA_SOURCE in df.columns:
        # use the _L_ column that has been generated at the "merge_with_codelist" step
        source = ", ".join(list(df[LABEL_COL_PREFIX + ID_DATA_SOURCE].unique()))
    if source != "":
        display_source = {"display": "visible"}

    # Generate the labels for the chart from the data structure, override with translations
    elem_options_node["labels"] = get_labels(
        data_structs, struct_id, df.columns, lang, translations
    )

    # This chart has hodes some data in the Hover, also hide the label columns for coded dimensions (are added when merged with codelists)
    if "hover_data" in elem_options_node:
        hover_keys = list(elem_options_node["hover_data"].keys())
        for hover_k in hover_keys:
            if LABEL_COL_PREFIX + hover_k in df.columns:
                if elem_options_node["hover_data"][hover_k]:
                    elem_options_node["hover_data"][hover_k] = False
                    elem_options_node["hover_data"][LABEL_COL_PREFIX + hover_k] = True
                else:
                    elem_options_node["hover_data"][LABEL_COL_PREFIX + hover_k] = False

    # the geoJson
    elem_options_node["geojson"] = get_geojson(geoj)
    if "color_continuous_scale" not in elem_options_node:
        elem_options_node["color_continuous_scale"] = UNICEF_color_continuous_scale

    if not show_historical_data:
        del elem_options_node["animation_frame"]
    main_figure = px.choropleth_mapbox(df, **elem_options_node)
    main_figure.update_layout(
        margin={"r": 0, "t": 1, "l": 2, "b": 1},
        font=dict(family=default_font_family, size=default_font_size),
    )

    time_periods_in_df = ""

    if not show_historical_data:

        time_periods_in_df = list(df["TIME_PERIOD"].unique())
        time_periods_in_df.sort()
        time_periods_in_df = f"{get_multilang_value(translations['TIME_PERIOD'], lang)}: {', '.join(time_periods_in_df)}"

    return main_figure, source, display_source, time_periods_in_df

def print_exception(message,exc):
    print(message)
    print("Exception type:")
    print(type(exc))
    print("Exception args:")
    print(exc.args)