import dash_html_components as html

from .app import app
from .utils import DashRouter, DashNavBar
from .pages import (
    child_education,
    # child_protection,
    # child_health,
    # child_poverty,
    # child_rights,
    # child_participation,
    home,
    overview,
    # resources,
    # country_profiles,
    # data_query,
    # adolescent,
    # disability,
    # gender,
    # ecd,
    # risks,
    # climate,
)
from .components import fa


# Ordered iterable of routes: tuples of (route, layout), where 'route' is a
# string corresponding to path of the route (will be prefixed with Dash's
# 'routes_pathname_prefix' and 'layout' is a Dash Component.
urls = (
    ("", home.get_layout),
    ("overview", overview.get_layout),
    ("child-education", child_education.get_layout),
    # ("child-protection", child_protection.get_layout),
    # ("child-health", child_health.get_layout),
    # ("child-poverty", child_poverty.get_layout),
    # ("child-rights", child_rights.get_layout),
    # ("child-participation", child_participation.get_layout),
    # ("profiles", country_profiles.get_layout),
    # ("data_query", data_query.get_layout),
    # ("resources", resources.get_layout),
    # ("adolescent", adolescent.get_layout),
    # ("disability", disability.get_layout),
    # ("gender", gender.get_layout),
    # ("ecd", ecd.get_layout),
    # ("risks", risks.get_layout),
    # ("climate", climate.get_layout),
)

# Ordered iterable of navbar items: tuples of `(route, display)`, where `route`
# is a string corresponding to path of the route (will be prefixed with
# 'routes_pathname_prefix') and 'display' is a valid value for the `children`
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

router = DashRouter(app, urls)
navbar = DashNavBar(app, nav_items)
