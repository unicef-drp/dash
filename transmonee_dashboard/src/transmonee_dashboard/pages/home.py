import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, State, Output

from ..app import app


def get_layout(**kwargs):
    return html.Div(children=[html.H2("Home"), html.Img(src="assets/home.png")])
