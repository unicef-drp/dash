from dash import html
import uuid
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import datetime

from dash import Input, Output, State, html, callback, MATCH


class YearsRangeSelectorAIO(html.Div):
    # _value_style = {"textAlign": "center", "color": "#1cabe2"}
    # A set of functions that create pattern-matching callbacks of the subcomponents
    class ids:
        years_range = lambda aio_id: {
            "component": "YearsRangeSelectorAIO",
            "subcomponent": "years_range",
            "aio_id": aio_id,
        }

        years_range_open_collapse_btn = lambda aio_id: {
            "component": "YearsRangeSelectorAIO",
            "subcomponent": "years_range_open_collapse_btn",
            "aio_id": aio_id,
        }

        years_range_open_collapse_elem = lambda aio_id: {
            "component": "YearsRangeSelectorAIO",
            "subcomponent": "years_range_open_collapse_elem",
            "aio_id": aio_id,
        }

    # Make the ids class a public class
    ids = ids

    # Define the arguments of the All-in-One component
    def __init__(
        self,
        year_min=2000,
        year_max=None,
        sel_year_min=2000,
        sel_year_max=None,
        years_label="Years",
        aio_id=None,
        additional_classes=None,
    ):
        # Allow developers to pass in their own `aio_id` if they're binding their own callback to a particular component.
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        if year_max is None:
            year_max = datetime.datetime.now().year
        if sel_year_max is None:
            sel_year_max = min(year_max, datetime.datetime.now().year)

        ret = [
            html.Div(
                className="d-flex justify-content-center",
                children=dbc.Button(
                    id=self.ids.years_range_open_collapse_btn(aio_id),
                    class_name="btn btn-secondary dropdown-toggle",
                    n_clicks=0,
                    children=f"{years_label}: {sel_year_min} - {sel_year_max}",
                ),
            ),
            # dbc.Collapse(
            #     dbc.Card(
            #         dbc.CardBody(
            #             dcc.RangeSlider(
            #                 className="w-100",
            #                 id=self.ids.years_range(aio_id),
            #                 min=year_min,
            #                 max=year_max,
            #                 step=1,
            #                 marks={year_min: str(year_min), year_max: str(year_min)},
            #                 value=[
            #                     sel_year_min,
            #                     sel_year_max,
            #                 ],
            #                 tooltip={"placement": "bottom", "always_visible": True},
            #             )
            #         )
            #     ),
            #     id=self.ids.years_range_open_collapse_elem(aio_id),
            #     is_open=False,
            #     style={"opacity":1}
            # ),
            html.Div(
                id=self.ids.years_range_open_collapse_elem(aio_id),
                children=[
                    dcc.RangeSlider(
                        className="w-100",
                        id=self.ids.years_range(aio_id),
                        min=year_min,
                        max=year_max,
                        step=1,
                        marks={year_min: str(year_min), year_max: str(year_min)},
                        value=[
                            sel_year_min,
                            sel_year_max,
                        ],
                        tooltip={"placement": "bottom", "always_visible": True},
                    )
                ],
            ),
        ]

        if additional_classes is None:
            className = ""
        else:
            className = additional_classes
        # Define the component's layout
        super().__init__(children=ret, className=className)

    @callback(
        Output(ids.years_range_open_collapse_elem(MATCH), "is_open"),
        [Input(ids.years_range_open_collapse_btn(MATCH), "n_clicks")],
        [State(ids.years_range_open_collapse_elem(MATCH), "is_open")],
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open
