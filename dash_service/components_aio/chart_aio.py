from dash import html, dcc, MATCH
import uuid
import dash_bootstrap_components as dbc
from .downloads_aio import DownloadsAIO

from dash import html, dcc

class ChartAIO(html.Div):
    _header_style = {"fontWeight": "bold"}

    class ids:
        card = lambda aio_id: {
            "component": "ChartAIO",
            "subcomponent": "card",
            "aio_id": aio_id,
        }

        card_title = lambda aio_id: {
            "component": "ChartAIO",
            "subcomponent": "card_title",
            "aio_id": aio_id,
        }

        ddl = lambda aio_id: {
            "component": "ChartAIO",
            "subcomponent": "ddl",
            "aio_id": aio_id,
        }

        chart_types = lambda aio_id: {
            "component": "ChartAIO",
            "subcomponent": "chart_types",
            "aio_id": aio_id,
        }

        chart = lambda aio_id: {
            "component": "ChartAIO",
            "subcomponent": "chart",
            "aio_id": aio_id,
        }

        info_icon = lambda aio_id: {
            "component": "ChartAIO",
            "subcomponent": "info_icon",
            "aio_id": aio_id,
        }
        info_text = lambda aio_id: {
            "component": "ChartAIO",
            "subcomponent": "info_text",
            "aio_id": aio_id,
        }
        missing_areas = lambda aio_id: {
            "component": "ChartAIO",
            "subcomponent": "missing_areas",
            "aio_id": aio_id,
        }
        download_api_call = lambda aio_id: {
            "component": "ChartAIO",
            "subcomponent": "download_api_call",
            "aio_id": aio_id,
        }

    # Make the ids class a public class
    ids = ids

    def __init__(
        self,
        aio_id=None,
        title="",
        plot_cfg=None,
        info_title="",
        lbl_excel="Download Excel",
        lbl_csv="Download CSV",
        dropdownlist_options=None,
        dropdownlist_value=None,
        chart_types=[],
        default_graph=None,
    ):

        if aio_id is None:
            aio_id = str(uuid.uuid4())

        chart_type_visibility = ""
        if chart_types is None or len(chart_types) < 2:
            chart_type_visibility = " d-none"

        card_header = dbc.CardHeader(
            id=self.ids.card_title(aio_id),
            style=ChartAIO._header_style,
            children=[title],
        )

        card_body = dbc.CardBody(
            children=[
                html.Div(
                    className="my-2",
                    children=[
                        dcc.Dropdown(
                            id=self.ids.ddl(aio_id),
                            className="dcc_control",
                            options=dropdownlist_options,
                            value=dropdownlist_value,
                        )
                    ],
                ),
                html.Div(
                    className="my-2" + chart_type_visibility,
                    children=[
                        dbc.RadioItems(
                            id=self.ids.chart_types(aio_id),
                            options=chart_types,
                            value=default_graph,
                            inline=True,
                            class_name="force-inline-control",
                        )
                    ],
                ),
                dcc.Loading(
                    children=[
                        dcc.Graph(
                            id=self.ids.chart(aio_id),
                            config=plot_cfg,
                            # style={"min-height": "100px"},
                            # style={"width": "200px"},
                            # style={"width": "inherit"},
                        )
                    ],
                ),
                html.Div(
                    className="row",
                    children=[
                        html.Div(
                            className="col-5",
                            children=[
                                DownloadsAIO(
                                    aio_id, lbl_excel=lbl_excel, lbl_csv=lbl_csv
                                ),
                                dcc.Input(
                                    type="hidden", id=self.ids.download_api_call(aio_id)
                                ),
                            ],
                        ),
                        html.Div(
                            id=self.ids.missing_areas(aio_id),
                            className="col-5 text-secondary",
                            children=[],
                        ),
                        html.Div(
                            id=self.ids.info_icon(aio_id),
                            className="col-2",
                            children=[
                                html.I(
                                    id="chart_aio_inf_icon_" + aio_id,
                                    className="fas fa-info-circle mx-1 float-end",
                                    style={"paddingRight": "30px"},
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        dbc.Popover(
                            [
                                dbc.PopoverHeader(info_title),
                                dbc.PopoverBody(id=self.ids.info_text(aio_id)),
                            ],
                            id="hover",
                            target="chart_aio_inf_icon_" + aio_id,
                            trigger="hover",
                            style={"opacity": 1},
                        )
                    ],
                ),
            ]
        )

        card = dbc.Card(children=[card_header, card_body])

        # Define the component's layout
        super().__init__(
            id=self.ids.card(aio_id),
            # className="col",
            children=[card],
        )
