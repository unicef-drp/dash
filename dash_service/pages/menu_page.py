# https://dash.plotly.com/dash-ag-grid

from dash import callback, dcc, html
from dash.exceptions import PreventUpdate
from dash_service.models import MenuPage, Project
from dash.dependencies import MATCH, Input, Output, State, ALL


import dash_bootstrap_components as dbc

from dash_service.components_aio.pages_navigation_aio import PagesNavigationAIO
from dash_service.components_aio.heading_aio import HeadingAIO

"""
Creates a splash page
"""


def layout(lang="en", **query_params):

    project_slug = query_params.get("prj", None)
    page_slug = query_params.get("page", None)

    if project_slug is None or page_slug is None:
        # return render_page_template({}, "Validation Page", [], "", lang)
        return render_no_menupage_cfg_found(project_slug, page_slug)

    # uses SmartQueryMixin documented here: https://github.com/absent1706/sqlalchemy-mixins#django-like-queries
    menupage = MenuPage.where(
        project___slug=project_slug, slug=page_slug
    ).first_or_404()

    config = menupage.content
    t = menupage.title

    return render_page_template(config, lang, query_params)


def render_no_menupage_cfg_found(prj, page):
    if prj is None:
        err = "No page found, prj parameter needed, e.g. prj=rosa"
    if page is None:
        err = "No page found, page parameter needed, e.g. page=rosa_de"
    if prj is not None and page is not None:
        err = f"No page found for parameters prj={prj}&page={page}"
    template = html.Div(
        children=dbc.Col(
            [
                dbc.Row(html.H3(err)),
            ]
        ),
    )
    return template


_color_maps = {
    "purple": {"c": "#561e60", "s": "#eeeaf1"},
    "green": {"c": "#3e7c4b", "s": "#ebf2ed"},
    "light_blue": {"c": "#4d8bba", "s": "#ebeff2"},
    "red": {"c": "#861b3e", "s": "#f2ebed"},
    "blue": {"c": "#38558e", "s": "#ebedf2"},
    "yellow": {"c": "#e4af4f", "s": "#f2f0eb"},
    "orange": {"c": "#ec5e23", "s": "#f2edeb"},
}

_menu_items_size = {
    "2xl": {
        "title_font_size": "fs-4",
        "icon_size": "fa-2xl",
        "button_padding": "p-2",
        "button_margin": "m-3",
        "button_w": "160px",
        "button_h": "120px",
    },
    "xl": {
        "title_font_size": "fs-5",
        "icon_size": "fa-xl",
        "button_padding": "p-2",
        "button_margin": "m-2",
        "button_w": "130px",
        "button_h": "100px",
    },
}


def _create_button(link, menu_size, color=None):
    icon_size = _menu_items_size[menu_size]["icon_size"]
    button_padding = _menu_items_size[menu_size]["button_padding"]
    button_margin = _menu_items_size[menu_size]["button_margin"]
    button_w = _menu_items_size[menu_size]["button_w"]
    button_h = _menu_items_size[menu_size]["button_h"]

    if "icon" in link:
        icon_class = link["icon"] + " " + icon_size
    else:
        icon_class = ""

    href = ""
    if "link" in link:
        href = link["link"]

    btn = html.A(
        className=f"btn {button_padding} {button_margin} text-white",
        style={
            "width": button_w,
            "height": button_h,
            "backgroundColor": color,
        },
        children=[
            html.Div(
                className="h-100 w-100 d-flex flex-grow-1 justify-content-center align-items-center",
                children=[
                    html.Div(
                        children=[
                            html.Div(
                                className="mb-3 align-items-center",
                                children=html.I(className=icon_class),
                            ),
                            html.Div(children=link["title"]),
                        ],
                    )
                ],
            )
        ],
        href=href,
    )
    ret = html.Div(className="m-2 d-inline", children=btn)
    return ret


def _get_params_from_link(lnk):
    if lnk.strip() == "":
        return {}

    split_params = lnk.replace("?", "")
    ret = {}
    if "#" in split_params:
        ret["hash"] = split_params.split("#")[1]
        split_params = split_params.split("#")[0]

    split_params = split_params.split("&")

    for p in split_params:
        split = p.split("=")
        ret[split[0]] = split[1]
    return ret


def _get_params_string(link_params, additional_params):
    params = []
    for k, v in link_params.items():
        if k != "hash":
            params.append(f"{k}={v}")
    for k, v in additional_params.items():
        params.append(f"{k}={v}")
    ret = "?" + "&".join(params)
    if "hash" in link_params:
        ret = ret + "#" + link_params["hash"]
    return ret


def create_links_row(row, query_params_to_pass_through, menu_size):
    # The colors
    ch = []
    color = "blue"
    secondary = "white"
    if "color" in row and row["color"] in _color_maps:
        color = _color_maps[row["color"]]["c"]
        secondary = _color_maps[row["color"]]["s"]

    # The header of he section
    cardHeader = None
    if "title" in row:
        font_size = _menu_items_size[menu_size]["title_font_size"]
        cardHeader = html.Div(
            className=f"card-header {font_size} fw-bold text-center",
            style={"backgroundColor": secondary, "color": color},
            children=row["title"],
        )

    # Create the buttons, creating the links is quite complex because the page can be embedded.
    # Links stored in the configuration must be parsed and merged with the params og the hosting page that must be carried on
    if "links" in row:
        links_div = []
        for l in row["links"]:
            link_to_use = ""
            if "link" in l:
                link_to_use = l["link"]
            if not (
                link_to_use.lower().startswith("http://")
                or link_to_use.lower().startswith("https://")
            ):
                params_from_link = _get_params_from_link(link_to_use)
                params_string = _get_params_string(
                    params_from_link, query_params_to_pass_through
                )
                l["link"] = params_string
            lnk = _create_button(l, menu_size, color)
            links_div.append(lnk)
        ch.append(html.Div(className="text-center", children=links_div))

    row_card = html.Div(
        className="card mb-3",
        style={"backgroundColor": secondary},
        children=[cardHeader, html.Div(className="card-body", children=ch)],
    )

    return row_card


def render_page_template(
    page_config: dict,
    lang,
    query_params,
    **kwargs,
) -> html.Div:
    """Renders the page template based on the page config and other parameters

    Args:
        config (dict): config from the database

    Returns:
        html.Div: The dash Div representing the redenderd page against the config
    """

    # remove some params that will be replaced
    query_params_to_remove = ["prj", "page", "hash"]
    for qp in query_params_to_remove:
        if qp in query_params:
            del query_params[qp]

    row_elems = []

    # The page's main title
    if "main_title" in page_config:
        elem_main_title = HeadingAIO(page_config["main_title"], aio_id="menu_page_head")
        row_elems.append(elem_main_title)

    # The buttons size
    menu_size = "2xl"
    if "menu_size" in page_config:
        menu_size = page_config["menu_size"]

    # For all the rows defined in the cfg
    for row in page_config["ROWS"]:
        row_div = create_links_row(row, query_params, menu_size)
        row_elems.append(row_div)

    template = html.Div(
        className="row justify-content-center",
        children=html.Div(className="col-sm-12 col-xxl-10", children=row_elems),
    )

    return template
