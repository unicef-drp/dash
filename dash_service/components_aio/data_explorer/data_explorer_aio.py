from dash import html, dcc
import dash_bootstrap_components as dbc
import uuid
import datetime


class DataExplorerAIO(html.Div):
    _CFG_LASTN = "lastnobservations"
    _LAST1OBS_LABEL = "Show latest data only"

    class ids:
        dataexplorer = lambda aio_id: {
            "component": "DataExplorer",
            "subcomponent": "dataexplorer",
            "aio_id": aio_id,
        }
        lastnobs = lambda aio_id: {
            "component": "DataExplorer",
            "subcomponent": "lastnobs",
            "aio_id": aio_id,
        }
        time_period = lambda aio_id: {
            "component": "DataExplorer",
            "subcomponent": "time_period",
            "aio_id": aio_id,
        }

    ids = ids

    def __init__(self, aio_id=None, cfg=None, labels={}):
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        lastnobs = []
        if cfg is not None:
            if cfg.get(DataExplorerAIO._CFG_LASTN, 0) != 0:
                lastnobs = ["lastn"]

        txt_lastnobs = labels.get(
            DataExplorerAIO._CFG_LASTN, DataExplorerAIO._LAST1OBS_LABEL
        )

        filter_lastnobs = dcc.Checklist(
            id=self.ids.lastnobs(aio_id),
            options=[{"label": txt_lastnobs, "value": "lastn"}],
            value=lastnobs,
        )

        back_n_years = 10
        time_min = 2000
        time_max = datetime.datetime.now().year
        time_start = time_max - back_n_years
        time_end = time_max
        if cfg is not None:
            time_min = cfg.get("time_period_filter_start", time_min)
            time_start = datetime.datetime.now().year - cfg.get("start_n_years_back", back_n_years)

        filter_time = dcc.RangeSlider(
            time_min,
            time_max,
            marks={time_min: str(time_min), time_max: str(time_max)},
            value=[time_start, time_end],
            id=self.ids.time_period(aio_id),
            className="de_rangeslider",
            allowCross=False,
            tooltip={"placement": "bottom", "always_visible": True},
        )

        left_col = html.Div(
            className="col-sm-12 col-lg-3 bg-light",
            children=[
                html.Div(children=filter_lastnobs, className="row mb-2"),
                html.Div(children=filter_time, className="row mb-2"),
                html.Div(children=["Filters"], className="row mb-2"),
                html.Div(children=["Pivot control"], className="row mb-2"),
            ],
        )

        table_col = html.Div(
            className="col-sm-12 col-lg-9",
            children=["Table"],
        )

        super().__init__(className="row", children=[left_col, table_col])
