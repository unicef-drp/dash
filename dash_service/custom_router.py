from dash import html, dcc, Input, Output, State
from urllib.parse import parse_qs, urlparse
from .db_utils import db_utils

from dash_service.pages import empty_renderer, dashboard, data_explorer, menu_page
from dash_service.pages import home
from dash.development.base_component import Component
from werkzeug.datastructures import MultiDict
from .exceptions import InvalidLayoutError
from dash.exceptions import PreventUpdate
from dash_service.pages import empty_renderer
from dash_service.pages import data_explorer
from dash_service.pages import dashboard
from flask import request


class CustomRouter:
    """Query string router for DASH multipage apps"""

    def _is_component(layout):
        if isinstance(layout, Component):
            return True
        return False

    def __init__(self, app, html_container_id) -> None:
        """
        Initialize the router
        Params:
        app: A Dash instance to associate the router with
        html_container_id: the id of the HTML container where the page qill be injected
        """

        @app.callback(
            [Output(html_container_id, "children")],
            [Input("dash-location", "pathname"), Input("dash-location", "search")],
            [State("dash-location", "hash")],
            prevent_initial_call=True,
        )
        def custom_router_callb(pathname, search, url_hash):
            if pathname is None:
                raise PreventUpdate("Ignoring first Location. pathname callback")

            parsedurl = urlparse(request.base_url)
            parsed_scheme = parsedurl.scheme
            if request.is_secure and parsed_scheme == "http":
                parsed_scheme = "https"

            parsedurl = f"{parsed_scheme}://{parsedurl.netloc}"

            qparams = parse_qs(search.lstrip("?"))

            param_prj = ""
            param_page = ""
            layout_to_use = None
            layout = None
            if "page" in qparams and len(qparams["page"]) > 0:
                param_page = qparams["page"][0]
            if "prj" in qparams and len(qparams["prj"]) > 0:
                param_prj = qparams["prj"][0]

            kwargs = MultiDict(qparams)
            kwargs["hash"] = url_hash

            if param_prj == "im":
                if param_page == "":
                    layout_to_use = home.layout()
                else:
                    layout_to_use = home.layout()
                    # removing domain pages for the moment
                    #layout_to_use = CustomRouter.tm_layouts[param_page]
            else:
                page_type = db_utils().get_page_type(param_prj, param_page)
                if page_type == db_utils.TYPE_DASHBOARD:
                    layout_to_use = dashboard.layout(**kwargs)
                elif page_type == db_utils.TYPE_DATAEXPLORER:
                    layout_to_use = data_explorer.layout(**kwargs)
                elif page_type == db_utils.TYPE_MENU:
                    layout_to_use = menu_page.layout(**kwargs)

            if CustomRouter._is_component(layout_to_use):
                layout = layout_to_use
            elif callable(layout_to_use):
                kwargs = MultiDict(qparams)
                kwargs["hash"] = url_hash
                layout = layout_to_use(**kwargs)

                if not CustomRouter._is_component(layout):
                    msg = (
                        "Layout function must return a Dash Component.\n\n"
                        f"Function {layout_to_use.__name__} from module {layout_to_use.__module__} "
                        f"returned value of type {type(layout)} instead."
                    )
                    raise InvalidLayoutError(msg)

            if layout is None:
                layout = empty_renderer.layout()

            return [layout]
