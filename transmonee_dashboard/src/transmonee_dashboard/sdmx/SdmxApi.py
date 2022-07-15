import requests
import pandas as pd


class SdmxApi:
    def __init__(self, endpoint):
        self.endpoint = ""
        if endpoint.endswith("/"):
            self.endpoint = endpoint
        else:
            self.endpoint = endpoint + "/"

    def get_structure(self, agency, id, version, query_params=None):
        """
        Get SDMX structure
        :param agency: the SDMX agency
        :param dfid: the Dataflow id
        :param version: the dataflow verions
        :param query_params optional query params to override the default ones
        :return: the Stucture in a dictionary
        """
        params = {
            "format": "sdmx-json",
            "detail": "full",
            "references": "all"
        }
        if query_params is not None:
            params = query_params

        to_call = f"{self.endpoint}dataflow/{agency}/{id}/{version}"
        r = requests.get(to_call, params=params)
        if r.ok:
            return r.json()
        else:
            raise (ConnectionError(
                "Error downloading " + to_call + " status code: " + str(r.status_code) + str(r.raise_for_status())))

    def get_codelist(self, agency, id, version="latest"):
        """
        Get a codelist
        :param agency: the SDMX agency
        :param clid: the codelist id
        :param version: the version
        :return: the codelist as a dict obj
        """
        params = {
            "format": "sdmx-json",
            "detail": "full",
            "references": "none"
        }
        to_call = f"{self.endpoint}codelist/{agency}/{id}/{version}"
        r = requests.get(to_call, params=params)
        if r.ok:
            return r.json()
        else:
            raise (ConnectionError(
                "Error downloading " + to_call + " status code: " + str(r.status_code) + str(r.raise_for_status())))

    def get_dataflow_as_dataframe(self, agency, dfid, version, dataquery=None, time_period=None, lastnobservations=-1,
                                  labels="id"):
        """
        Get a SDMX dataflow as Pandas dataframe
        :param agency: The SDMX Agency
        :param dfid: The dataflow's id
        :param version: The dataflows' id
        :param dataquery: The dataquery (optional, will download all the dataflow if omitted)
        :param labels: id=id only; both=id and labels; labels=labels only
        :return: A pandas dataframe
        """
        params = {
            "format": "sdmx-csv",
            "labels": labels
        }
        # use the Fusion-csv format if labels only
        if labels == "labels":
            params["format"] = "csv"
            params["labels"] = "name"
        if lastnobservations is not None:
            params["lastnobservations"] = lastnobservations
        if time_period is not None:
            params["startPeriod"] = time_period[0]
            if len(time_period) > 0:
                params["endPeriod"] = time_period[1]

        # is it there a dataquery?
        dq = "all"
        if dataquery is not None:
            dq = dataquery

        params_to_send = [f"{p[0]}={p[1]}" for p in params.items()]
        params_to_send = "&".join(params_to_send)

        # compose the url to call
        to_call = f"{self.endpoint}data/{agency},{dfid},{version}/{dq}?{params_to_send}"
        return pd.read_csv(to_call, encoding="utf8")
