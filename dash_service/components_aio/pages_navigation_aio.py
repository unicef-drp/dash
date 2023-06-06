from dash import html
import uuid
import dash_bootstrap_components as dbc


class PagesNavigationAIO(html.Header):
    class ids:
        heading = lambda aio_id: {
            "component": "PagesNavigationAIO",
            "subcomponent": "menu",
            "aio_id": aio_id,
        }

    # Make the ids class a public class
    ids = ids

    # Define the arguments of the All-in-One component
    def __init__(
        self,
        pages=None,
        query_params=None,
        aio_id=None,
    ):
        # Allow developers to pass in their own `aio_id` if they're binding their own callback to a particular component.
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        if pages is None or len(pages) == 0:
            return None

        nav_links = []

        qparams_to_remove = ["prj", "page", "lang", "hash"]
        cleaned_qparams = [qp for qp in query_params if qp not in qparams_to_remove]

        for p in pages:
            url_params = ["prj=" + p["prj_slug"], "page=" + p["slug"]]
            if p["lang"] != "en":
                url_params.append("lang=" + p["lang"])
            for qp in cleaned_qparams:
                url_params.append(qp + "=" + query_params[qp])
            nav_links.append({"name": p["name"], "href": "?" + "&".join(url_params)})

        # create all the ul - li - A structure for each link
        nav_link_ul = [
            html.Ul(
                className="navbar-nav mt-0 d-flex",
                children=[
                    html.Li(
                        className="nav-item",
                        children=[
                            html.A(
                                className="nav-link text-primary fw-bolder fs-6",
                                href=nlink["href"],
                                children=nlink["name"],
                                style={"textShadow": "none"},
                            )
                        ],
                    )
                ],
            )
            for nlink in nav_links
        ]

        nav = html.Nav(
            className="navbar navbar-expand-lg navbar-light justify-content-evenly",
            children=nav_link_ul,
        )

        super().__init__(
            id=self.ids.heading(aio_id),
            className="row shadow p-3 mb-5 bg-white",
            children=nav,
        )
