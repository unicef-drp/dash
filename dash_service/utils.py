import inspect
import json

from functools import wraps
from urllib.parse import parse_qs

import dash
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from dash.development.base_component import Component
from flask import current_app as server
from werkzeug.datastructures import MultiDict

from .pages import page_not_found

from .exceptions import InvalidLayoutError

from pathlib import Path
import importlib

parent = Path(__file__).resolve().parent


def get_geo_file(name):
    """Get a geojson file from the assets folder"""
    path = parent / "static/{}".format(name)
    with open(path) as shapes_file:
        return json.load(shapes_file)


def fa(className):
    """A convenience component for adding Font Awesome icons"""
    return html.I(className=f"{className} mx-1")


def component(func):
    """Decorator to help vanilla functions as pseudo Dash Components"""

    @wraps(func)
    def function_wrapper(*args, **kwargs):
        # remove className and style args from input kwargs so the component
        # function does not have to worry about clobbering them.
        className = kwargs.pop("className", None)
        style = kwargs.pop("style", None)

        # call the component function and get the result
        result = func(*args, **kwargs)

        # now restore the initial classes and styles by adding them
        # to any values the component introduced

        if className is not None:
            if hasattr(result, "className"):
                result.className = f"{className} {result.className}"
            else:
                result.className = className

        if style is not None:
            if hasattr(result, "style"):
                result.style = style.update(result.style)
            else:
                result.style = style

        return result

    return function_wrapper


class DashRouter:
    """A URL Router for Dash multipage apps"""

    def __init__(self, app, urls):
        """Initialise the router.

        Params:
        app:   A Dash instance to associate the router with.
        urls:  Ordered iterable of routes: tuples of (route, layout). 'route' is a
               string corresponding to the URL path of the route (will be prefixed
               with Dash's 'routes_pathname_prefix' and 'layout' is a Dash Component
               or callable that returns a Dash Component. The callable will also have
               any URL query parameters passed in as keyword arguments.
        """
        self.routes = {get_url(route): layout for route, layout in urls}

        @app.callback(
            # Output(app.server.config["CONTENT_CONTAINER_ID"], "children"),
            Output("MAIN_CONTAINER", "children"),
            [
                # Input(server.config["LOCATION_COMPONENT_ID"], "pathname"),
                # Input(server.config["LOCATION_COMPONENT_ID"], "search"),
                Input("dash-location", "pathname"),
                Input("dash-location", "search"),
            ],
            [
                # State(server.config["LOCATION_COMPONENT_ID"], "hash"),
                State("dash-location", "hash"),
            ],
        )
        def router_callback(pathname, search, url_hash):
            """The router"""

            if pathname is None:
                raise PreventUpdate("Ignoring first Location.pathname callback")

            page = self.routes.get("/")

            # Needs to be cleaned when transmonee will use the Database
            # It is quite messy: dynaically load the page module needed for transmonee using the query param
            if search is not None and search != "":
                qparams = parse_qs(search.lstrip("?"))
                param_viz = "/"
                if "viz" in qparams:
                    param_viz = "/" + qparams["viz"][0]
                    if param_viz == "/tm":
                        if "page" in qparams:
                            param_page = qparams["page"][0]
                            param_page = param_page.replace("-", "_")
                        else:
                            param_page = "home"
                        tm_module = importlib.import_module(
                            f"dash_service.pages.{param_page}"
                        )

                        page = tm_module.layout
                    else:
                        page = self.routes.get(param_viz, self.routes.get("/"))

                # file:///C:/gitRepos/dash/minimal_dash_embedding_test_static.html?prj=brazil&page=health

            if page is None:
                layout = page_not_found(pathname)
            elif isinstance(page, Component):
                layout = page
            # elif callable(page) or is_callable:
            elif callable(page):
                kwargs = MultiDict(parse_qs(search.lstrip("?")))
                kwargs["hash"] = url_hash
                layout = page(**kwargs)
                if not isinstance(layout, Component):
                    msg = (
                        "Layout function must return a Dash Component.\n\n"
                        f"Function {page.__name__} from module {page.__module__} "
                        f"returned value of type {type(layout)} instead."
                    )
                    raise InvalidLayoutError(msg)
            else:
                msg = (
                    "Page layouts must be a Dash Component or a callable that "
                    f"returns a Dash Component. Received value of type {type(page)}."
                )
                raise InvalidLayoutError(msg)
            return layout


def get_dash_args_from_flask_config(config):
    """Get a dict of Dash params that were specified"""
    # all arg names less 'self'
    dash_args = set(inspect.getfullargspec(dash.Dash.__init__).args[1:])
    return {key.lower(): val for key, val in config.items() if key.lower() in dash_args}


def get_url(path):
    """Expands an internal URL to include prefix the app is mounted at"""
    return f"{server.config['ROUTES_PATHNAME_PREFIX']}{path}"
