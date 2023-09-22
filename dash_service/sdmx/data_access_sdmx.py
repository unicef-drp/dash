import pandasdmx as psdmx
import pandas as pd
import time
import requests_cache
from typing import Union


from . import data_access

_CACHE_EXPIRE_AFTER_N_SECONDS = 5 * 60

_CACHE_CONFIG = {
    "cache_name": "pandasmx_cache",
    "backend": "sqlite",
    "fast_save": True,
    "expire_after": _CACHE_EXPIRE_AFTER_N_SECONDS,
}

KEY_OBS_VALUE = "OBS_VALUE"

# dsd query, parsing helpers
def _code_to_dict(code: psdmx.model.Code) -> dict:
    ret = {"id": code.id, "name": str(code.name)}
    if isinstance(code.parent, psdmx.model.Code):
        ret["parent"] = str(code.parent)
    return ret


def _component_to_dict(comp) -> dict:
    ret = {"id": comp.id, "name": str(comp.concept_identity.name), "is_time": False}
    if (
        not comp.local_representation is None
        and not comp.local_representation.enumerated is None
    ):
        codes = comp.local_representation.enumerated
        ret["codes"] = [_code_to_dict(codes[c]) for c in codes.items]

    if isinstance(comp, psdmx.model.TimeDimension):
        ret["is_time"] = True
    return ret


# data query, parsing helpers
def _data_query_is_all(dq):
    if dq is None:
        return True
    if isinstance(dq, str):
        if dq.strip() == "":
            return True
        return False
    for v in dq.values():
        if len(v) > 0:
            return False
    return True


def _get_methods(obj):
    object_methods = [
        method_name for method_name in dir(obj) if callable(getattr(obj, method_name))
    ]
    for m in object_methods:
        print(m)


class DataAccess_SDMX(data_access.Data_access):
    def __init__(self, data_endpoint_id, data_endpoint_url):
        super(DataAccess_SDMX, self).__init__(data_endpoint_id, data_endpoint_url)

    # Start DSD

    def _get_cont_constraints(self, sdmx_msg):
        constraints = sdmx_msg.constraint
        ret = {}
        for c in constraints:
            constr = constraints[c]
            data_content_keys = constr.data_content_keys
            keys = data_content_keys.keys

            for data_key in keys:
                if data_key.included:
                    key_value = data_key.key_value
                    for kv in key_value:
                        if not kv in ret:
                            ret[str(kv)] = []
                        ret[str(kv)].append(key_value[kv].value)
        return ret

    def get_dataflow_info(
        self, agency: str, id: str, ver: str, lang: str, print_stats=False
    ) -> dict:
        start_time = time.time()
        unicef = psdmx.Request(self.data_endpoint_id, **_CACHE_CONFIG)
        unicef.default_locale = lang
        sdmx_msg = unicef.dataflow(id, provider=agency)
        if print_stats:
            print("get_dsd: %s seconds" % (time.time() - start_time))

        ret = {"name": "", "dsd": {}}
        dataflow = sdmx_msg.dataflow[id]
        dsd = dataflow.structure

        dims = dsd.dimensions.components
        attribs = dsd.attributes.components
        measures = dsd.measures.components

        ret["dsd"]["dims"] = [_component_to_dict(c) for c in dims]
        ret["dsd"]["attribs"] = [_component_to_dict(c) for c in attribs]
        ret["dsd"]["measures"] = [_component_to_dict(c) for c in measures]
        ret["name"] = str(dataflow.name)

        constr = self._get_cont_constraints(sdmx_msg)

        for idx, dim in enumerate(ret["dsd"]["dims"]):
            if dim["id"] in constr:
                ret["dsd"]["dims"][idx]["codes"] = [
                    c
                    for c in ret["dsd"]["dims"][idx]["codes"]
                    if c["id"] in constr[dim["id"]]
                ]

        return ret

    # End DSD

    # Start data load and parsing
    """
    get_data (manual) parsing: 30.285801887512207 seconds
    to_dict: 46.50679588317871 seconds
    """

    def _parse_sdmxjson_data(self, jdata: dict, labels="both"):
        series = jdata["data"]["dataSets"][0]["series"]
        struct = jdata["data"]["structure"]

        data = []

        # Loop the series
        for ser_k, ser_v in series.items():

            series_vals = {}
            # Split the keys (1:14:0:1)
            # assign to the series_vals obj[dim_id] the value taken from the structure
            for idx, k in enumerate(ser_k.split(":")):
                if labels == "both":
                    dim_val = (
                        struct["dimensions"]["series"][idx]["values"][int(k)]["id"]
                        + ":"
                        + struct["dimensions"]["series"][idx]["values"][int(k)]["name"]
                    )
                elif labels == "name":
                    dim_val = struct["dimensions"]["series"][idx]["values"][int(k)][
                        "name"
                    ]
                elif labels == "id":
                    dim_val = struct["dimensions"]["series"][idx]["values"][int(k)][
                        "id"
                    ]

                series_vals[struct["dimensions"]["series"][idx]["id"]] = dim_val
            # loop through the observation nodes getting the key (e.g. 1,2...) and the val, the val is another set of keys
            for ser_obs_k, ser_obs_v in ser_v["observations"].items():
                # data_row = series_vals.copy()
                data_row = {}
                for idx, k in enumerate(ser_obs_k.split(":")):
                    data_row[struct["dimensions"]["observation"][idx]["id"]] = struct[
                        "dimensions"
                    ]["observation"][idx]["values"][int(k)]["name"]
                # self._get_info_from_series_key_observation(struct, ser_obs_k, data_row)

                data_row[KEY_OBS_VALUE] = ser_obs_v[0]

                for idx, attr in enumerate(ser_obs_v[1:]):
                    # self._get_info_from_series_key_attrib(struct, idx, attr, data_row)
                    if attr is None:
                        data_row[struct["attributes"]["observation"][idx]["id"]] = None
                    else:
                        if labels == "both":
                            data_row[struct["attributes"]["observation"][idx]["id"]] = (
                                struct["attributes"]["observation"][idx]["values"][
                                    attr
                                ]["id"]
                                + ":"
                                + struct["attributes"]["observation"][idx]["values"][
                                    attr
                                ]["name"]
                            )
                        elif labels == "name":

                            data_row[
                                struct["attributes"]["observation"][idx]["id"]
                            ] = struct["attributes"]["observation"][idx]["values"][
                                attr
                            ][
                                "name"
                            ]
                        elif labels == "id":
                            data_row[
                                struct["attributes"]["observation"][idx]["id"]
                            ] = struct["attributes"]["observation"][idx]["values"][
                                attr
                            ][
                                "id"
                            ]

                # data.append(data_row)
                data.append({**series_vals, **data_row})

        df = pd.DataFrame(data)

        dataflow_name = struct["name"]
        data_point_count = len(df)

        return df

    def get_data(
        self,
        agency: str,
        id: str,
        ver: str,
        dq: Union[dict, str] = None,
        startperiod=None,
        endperiod=None,
        lastnobs=False,
        print_stats=False,
        labels="both",
    ) -> pd.DataFrame:
        url = self.data_endpoint_url

        url = url + f"data/{agency},{id},{ver}/"

        # Data query can be a string: AFG.._T or a dict
        is_all = _data_query_is_all(dq)
        if is_all:
            dq_to_send = "all"
        else:
            if isinstance(dq, str):
                dq_to_send = dq
            else:
                dq_to_send = []
                for v in dq.values():
                    dq_to_send.append("+".join(v))
                dq_to_send = ".".join(dq_to_send)

        url = url + dq_to_send

        params = {"format": "sdmx-json"}
        if startperiod is not None:
            params["startPeriod"] = startperiod
        if endperiod is not None:
            params["endPeriod"] = endperiod
        if lastnobs:
            params["startPeriod"] = startperiod if startperiod is not None else 1900
            params["lastnobservations"] = 1

        start_time = time.time()
        # r = requests.get(url, params=params)

        # session = requests.Session()
        session = requests_cache.CachedSession(
            "data_cache", expire_after=_CACHE_EXPIRE_AFTER_N_SECONDS
        )
        r = session.get(url, params=params)

        if r.ok:
            jdata = r.json()
        else:
            raise (
                ConnectionError(
                    "Error downloading "
                    + url
                    + " status code: "
                    + str(r.status_code)
                    + r.raise_for_status()
                )
            )
        if print_stats:
            print("get_data download: %s seconds" % (time.time() - start_time))

        start_time = time.time()
        ret = self._parse_sdmxjson_data(jdata, labels)
        if print_stats:
            print("get_data (manual) parsing: %s seconds" % (time.time() - start_time))
            print(r.request.url)
            print(f"{str(len(ret))} data points downloaded")

        return ret

    # def get_data_(self, agency: str, id: str, ver: str, dq: dict = None, startperiod=None, endperiod=None,
    #               lastnobs=None, print_stats=False) -> pd.DataFrame:
    #     start_time = time.time()
    #     unicef = psdmx.Request(agency, **_CACHE_CONFIG)
    #     unicef.default_locale = "en"

    #     sdmx_msg = unicef.dataflow(id)
    #     dataflow = sdmx_msg.dataflow["GLOBAL_DATAFLOW"]
    #     dsd = dataflow.structure

    #     dq_to_send = {}
    #     if _data_query_is_all(dq):
    #         dq_to_send = None
    #     else:
    #         for d in dq:
    #             if len(dq[d]) > 0:
    #                 dq_to_send[d] = "+".join(dq[d])

    #     if print_stats:
    #         print("Getting data")
    #     resp = unicef.data(id, key=dq_to_send, dsd=dsd)
    #     if print_stats:
    #         print("get_data: %s seconds" % (time.time() - start_time))

    #     start_time = time.time()
    #     df = resp.to_pandas(dtype=str, rtype="rows")
    #     if print_stats:
    #         print("to_pandas: %s seconds" % (time.time() - start_time))
    #     start_time = time.time()
    #     df = df.reset_index()
    #     if print_stats:
    #         print("reset_index: %s seconds" % (time.time() - start_time))

    #     return df


"""PANDASDMX
Getting data dq = {"REF_AREA": ["AFG", "DZA","ITA","FRA"]}
get_data: 16.06649351119995 seconds
to_pandas: 4.512367248535156 seconds
reset_index: 0.0037381649017333984 seconds
27157
getting data_total from data_table: 20.583716869354248 seconds
to_dict: 0.20978999137878418 seconds

Manual parsing
get_data Dan: 0.37897562980651855 seconds
27157
getting data_total from data_table: 0.7742812633514404 seconds
to_dict: 0.6215243339538574 seconds
"""
