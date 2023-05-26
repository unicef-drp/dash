from dash import html, dcc, callback, ctx
from dash.dependencies import MATCH, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import uuid
import dash_treeview_antd

import time


class DataExplorerFilterAIO(html.Div):
    class ids:
        dataexplorerfilter = lambda aio_id: {
            "component": "DataExplorerFilterAIO",
            "subcomponent": "dataexplorerfilter",
            "aio_id": aio_id,
        }

    ids = ids

    # Not efficient: to review, it loops the whole codelist each time
    def _add_tree_level(tree_node, parent_code, items):
        # check if the current code is a child of the parent code
        for c in items:
            if "parent" in c and c["parent"] == parent_code:
                if "children" not in tree_node:  # create a new tree node
                    tree_node["children"] = []
                tree_node["children"].append({"key": c["id"], "title": c["name"]})
                DataExplorerFilterAIO._add_tree_level(
                    tree_node["children"][-1], c["id"], items
                )

    def _get_tree_items(items):
        ret = []
        for c in items:
            # it is a root node, add it and start the recursion
            if "parent" not in c or c["parent"] == "":
                ret.append({"key": c["id"], "title": c["name"]})
                # recursion
                DataExplorerFilterAIO._add_tree_level(ret[-1], c["id"], items)
        return ret

    def __init__(
        self,
        aio_id=None,
        filters=None,
        expanded=False,
        selected=None,
        lbl_sel_all="All",
    ):
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        accordionItems = []

        for idx, f in enumerate(filters):
            sel = []
            if f["id"] in selected:
                sel = selected[f["id"]]
            tree_items = DataExplorerFilterAIO._get_tree_items(f["codes"])
            tree = dash_treeview_antd.TreeView(
                id={"type": "filter_tree", "index": aio_id},
                checkable=True,
                multiple=True,
                checked=sel,
                expanded=["_root_" + aio_id],
                data={
                    "title": lbl_sel_all,
                    "key": "_root_" + aio_id,
                    "children": tree_items,
                },
            )
            tree_div = html.Div(
                className="overflow-auto m-0 p-0 div_de_filter",
                children=tree,
            )

            head_btn_id = f["id"]
            is_show = "d-none"
            if idx == 0:
                is_show = "d-block"

            accitem = html.Div(
                className="accordion-item",
                children=[
                    html.Div(
                        className="accordion-header",
                        id="_de_acc_head_" + f["id"],
                        children=[
                            html.Button(
                                id={"type": "de_filter_acc_btn", "index": head_btn_id},
                                className="accordion-button",
                                type="button",
                                children=f["name"],
                            )
                        ],
                    ),
                    html.Div(
                        className=is_show,
                        id={"type": "de_filter_acc_body", "index": head_btn_id},
                        children=[
                            html.Div(
                                className="accordion-body p-0", children=[tree_div]
                            )
                        ],
                    ),
                ],
            )
            accordionItems.append(accitem)

        accordion = html.Div(
            className="accordion accordion-flush", id="_de_acc", children=accordionItems
        )

        super().__init__(children=[accordion], className="p-0 m-0")

    @callback(
        Output({"type": "de_filter_acc_body", "index": ALL}, "className"),
        Input({"type": "de_filter_acc_btn", "index": ALL}, "n_clicks"),
        State({"type": "de_filter_acc_body", "index": ALL}, "className"),
        State({"type": "de_filter_acc_body", "index": ALL}, "id"),
        prevent_initial_call=True,
    )
    def de_acc_toggle(n_clicks, classNames, ids):
        ret = []
        button_id = ctx.triggered_id
        # cl_name="accordion-collapse collapse"
        # cl_name_show = "accordion-collapse collapse show"

        for idx in range(len(ids)):
            # this button has been clicked
            if button_id["index"] == ids[idx]["index"]:
                # toggle
                if "show" in classNames[idx]:
                    ret.append("d-none")
                else:
                    ret.append("d-block")
            else:
                ret.append("d-none")

        return ret
