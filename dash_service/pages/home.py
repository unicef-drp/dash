from dash import html, register_page
import dash_bootstrap_components as dbc

# register_page(__name__, path="/transmonee", order=0, title="TransMonEE Dashboard")


def layout(base_url, req):
    ret = dbc.Container(
        [
            dbc.Row(
                [
                    html.Div(
                        [
                            html.ObjectEl(
                                html.Img(
                                    src=f"{base_url}/assets/SOCR_Diagram_Oct_2022_href.svg"
                                ),
                                type="image/svg+xml",
                                data=f"{base_url.replace('http://','https://')}/assets/SOCR_Diagram_Oct_2022_href.svg",
                                className="px-2",
                                style={
                                    "width": "80%",
                                    # "height": "200vh",
                                    # "height": "80rem",
                                    "display": "flex",
                                    "margin-left": "auto",
                                    "margin-right": "auto",
                                    "margin-top": "15px",
                                    "margin-bottom": "15px",
                                },
                            ),
                        ]
                    ),
                ],
            ),
            html.Script(),
        ],
        fluid=True,
    )

    return ret


"""
layout = dbc.Container(
    [
        dbc.Row(
            [
                html.Div(
                    [
                        html.ObjectEl(
                            html.Img(src="./assets/SOCR_Diagram_Oct_2022_href.svg"),
                            type="image/svg+xml",
                            data="./assets/SOCR_Diagram_Oct_2022_href.svg",
                            className="px-2",
                            style={
                                "width": "80%",
                                "height": "200vh",
                                # "height": "80rem",
                                "display": "flex",
                                "margin-left": "auto",
                                "margin-right": "auto",
                                "margin-top": "15px",
                                "margin-bottom": "15px",
                            },
                        ),
                    ]
                ),
            ],
            justify="center",
            align="center",
        ),
    ],
    fluid=True,
)
"""
