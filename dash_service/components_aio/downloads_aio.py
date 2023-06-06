from dash import html, dcc
import uuid
import dash_bootstrap_components as dbc


class DownloadsAIO(dbc.ButtonGroup):
    # _value_style = {"textAlign": "center", "color": "#1cabe2"}
    # A set of functions that create pattern-matching callbacks of the subcomponents
    class ids:

        btn_down_group = lambda aio_id: {
            "component": "CardAIO",
            "subcomponent": "btn_down_group",
            "aio_id": aio_id,
        }
        btn_down_excel = lambda aio_id: {
            "component": "CardAIO",
            "subcomponent": "btn_down_excel",
            "aio_id": aio_id,
        }

        btn_down_csv = lambda aio_id: {
            "component": "CardAIO",
            "subcomponent": "btn_down_csv",
            "aio_id": aio_id,
        }

        dcc_down_excel = lambda aio_id: {
            "component": "CardAIO",
            "subcomponent": "dcc_down_excel",
            "aio_id": aio_id,
        }

        dcc_down_csv = lambda aio_id: {
            "component": "CardAIO",
            "subcomponent": "dcc_down_csv",
            "aio_id": aio_id,
        }

    # Make the ids class a public class
    ids = ids

    # Define the arguments of the All-in-One component
    def __init__(self, aio_id=None, lbl_excel="Download Excel", lbl_csv="Download CSV"):
        # Allow developers to pass in their own `aio_id` if they're binding their own callback to a particular component.
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        # Create the card body
        ret = [
            dbc.Button(
                lbl_excel, id=self.ids.btn_down_excel(aio_id), className="btn-sm", color="success"
            ),
            dbc.Button(lbl_csv, id=self.ids.btn_down_csv(aio_id), className="btn-sm", color="info"),
            dcc.Download(id=self.ids.dcc_down_excel(aio_id)),
            dcc.Download(id=self.ids.dcc_down_csv(aio_id)),
        ]

        # Define the component's layout
        super().__init__(id=self.ids.btn_down_group(aio_id), children=ret)
