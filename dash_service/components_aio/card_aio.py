from dash import html
import uuid
import dash_bootstrap_components as dbc


class CardAIO(html.Div):
    # A set of functions that create pattern-matching callbacks of the subcomponents
    class ids:
        card = lambda aio_id: {
            "component": "CardAIO",
            "subcomponent": "card",
            "aio_id": aio_id,
        }

    # Make the ids class a public class
    ids = ids

    # Define the arguments of the All-in-One component
    def __init__(
        self,
        value="-",
        suffix="",
        aio_id=None,
        info_head="",
        info_body="",
        time_period="",
        area="",
        lbl_time_period="Time period",
        lbl_area="Geographic area",
    ):

        card_children = []

        card_body = html.Div(
            className="card-body",
            children=[
                html.Span(
                    className="fs-2 fw-bold text-primary justify-content-center d-sm-flex p-2",
                    children=value,
                ),
                html.Span(
                    className="fs-4 justify-content-center d-sm-flex p-2",
                    children=suffix,
                ),
            ],
        )
        card_children.append(card_body)

        card_footer = []

        # Add the time period
        if time_period.strip() != "":
            time_p = html.Div(
                className="text-primary fw-bold float-start",
                #children=[f"{lbl_area}: {area}  ●  {lbl_time_period}: {time_period}"],
                children=[html.Div(f"{lbl_area}: {area}"), html.Div(f"{lbl_time_period}: {time_period}")],
            )
            card_footer.append(time_p)

        # if there is an info body add the "i" icon and the popup window
        if info_body is not None and info_body != "":
            popover_icon = html.Div(
                children=[
                    html.I(
                        id=f"card-info_icon{aio_id}",
                        className="fas fa-info-circle float-end",
                    ),
                    dbc.Popover(
                        target=f"card-info_icon{aio_id}",
                        trigger="hover",
                        children=[
                            dbc.PopoverHeader(info_head),
                            dbc.PopoverBody(info_body),
                        ],
                        style={"opacity": 1},
                    ),
                ],
            )
            card_footer.append(popover_icon)

        if len(card_footer) > 0:
            card_children.append(
                html.Div(className="align-middle m-3", children=card_footer)
            )

        # Define the component's layout
        super().__init__(
            id=self.ids.card(aio_id),
            className="card",
            children=card_children,
        )
