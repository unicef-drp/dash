from dash import html

from .app import app
from .utils import DashRouter
from .pages import dashboard, data_explorer, empty_renderer
from .components import fa


# Ordered iterable of routes: tuples of (route, layout), where 'route' is a
# string corresponding to path of the route (will be prefixed with Dash's
# 'routes_pathname_prefix' and 'layout' is a Dash Component.
urls = (("", dashboard.layout),)

renderers = (
    ("", empty_renderer.layout),
    ("ds", dashboard.layout),
    ("de", data_explorer.layout),
    ("tm", empty_renderer.layout),
)

# keyword argument for a Dash component (ie a Dash Component or a string).
nav_items = (
    ("", html.Div([fa("fas fa-home"), "Home"]), []),
    ("overview", html.Div([fa("fas fa-info-circle"), "Overview"]), []),
    (
        "sectors",
        "Domains",
        [
            ("child-education", html.Div([fa("fas fa-book"), "Education"])),
            (
                "child-protection",
                html.Div([fa("fas fa-child"), "Family Environment and Protection"]),
            ),
            (
                "child-health",
                html.Div([fa("fas fa-heartbeat"), "Health and Nutrition"]),
            ),
            (
                "child-poverty",
                html.Div([fa("fas fa-hand-holding-usd"), "Poverty"]),
            ),
            (
                "child-rights",
                html.Div(
                    [
                        fa("fas fa-balance-scale"),
                        "Child Rights Landscape",
                    ]
                ),
            ),
            (
                "child-participation",
                html.Div([fa("fas fa-users"), "Participation"]),
            ),
        ],
    ),
    (
        "cross-sectors",
        "Cross-Sectoral Issues",
        [
            ("adolescent", html.Div([fa("fas fa-user-friends"), "Adolescent"])),
            ("disability", html.Div([fa("fas fa-blind"), "Disability"])),
            ("gender", html.Div([fa("fas fa-venus-mars"), "Gender"])),
            ("ecd", html.Div([fa("fas fa-baby"), "ECD"])),
            (
                "risks",
                html.Div([fa("fas fa-exclamation-triangle"), "Risks and Humanitarian"]),
            ),
            ("climate", html.Div([fa("fas fa-sun"), "Climate Change"])),
        ],
    ),
    ("profiles", html.Div([fa("fas fa-globe"), "Country Snapshots"]), []),
    ("data_query", html.Div([fa("fas fa-table"), "Query Data"]), []),
    ("resources", html.Div([fa("fas fa-database"), "Resources"]), []),
)

nav_items_full_names = {
    "education": "Education",
    "child-protection": "Family environment and protection from violence and harmful practices",
    "child-health": "Health and Nutrition",
    "child-poverty": "Poverty and Social Protection",
    "child-rights": "Child Rights Landscape",
    "participation": "Participation",
}

# router = DashRouter(app, urls)
router = DashRouter(app, renderers)
