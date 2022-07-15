import pandas as pd
import re
from . import SdmxApi

import threading


class SdmxData:
    __cache_str = {}
    __cache_data = {}
    __cache_codelists = {}
    __lock = threading.Lock()

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    @staticmethod
    def _get_cache_ids(id: list, dq: str = None, time_period: list = None, lastnobservations: int = 0):
        tmp_dq = ""
        tmp_tp = ""
        tmp_lastn = ""
        if dq is not None:
            tmp_dq = dq
        if time_period is not None:
            tmp_tp = "|".join(time_period)
        if lastnobservations != 0:
            tmp_lastn = str(lastnobservations)

        struct_id = "|".join(id)
        data_id = f"{struct_id}_{tmp_dq}_{tmp_tp}_{tmp_lastn}"

        return struct_id, data_id

    def get_data(self, id: list, dq: str = None, time_period: list = None, lastnobservations: int = 0):
        struct_id, data_id = SdmxData._get_cache_ids(id, dq, time_period, lastnobservations)
        struct = None
        data = None
        SdmxData.__lock.acquire()
        if struct_id in SdmxData.__cache_str:
            struct = SdmxData.__cache_str[struct_id]
            print("Struct " + struct_id + " read from cache")
        else:
            sdmx_api = SdmxApi.SdmxApi(self.endpoint)
            struct = sdmx_api.get_structure(id[0], id[1], id[2])
            SdmxData.__cache_str[struct_id] = struct
            print("Struct " + struct_id + " read from API")

        if data_id in SdmxData.__cache_data:
            data = SdmxData.__cache_data[data_id]
            print("Data " + data_id + " read from cache")
        else:
            sdmx_api = SdmxApi.SdmxApi(self.endpoint)
            data = sdmx_api.get_dataflow_as_dataframe(id[0], id[1], id[2], dq, time_period, lastnobservations)
            SdmxData.__cache_data[data_id] = data
            print("Data " + data_id + " read from API")
        SdmxData.__lock.release()

        return struct, data

    def get_codelist(self, agency:str, id:str, version:str="latest"):
        cl_id = f"{agency}|{id}|{version}"
        if cl_id in SdmxData.__cache_codelists:
            print("CL " + id + " already downloaded")
            return SdmxData.__cache_codelists[cl_id]
        print("CL " + id + " new downloaded")

        sdmx_api = SdmxApi.SdmxApi(self.endpoint)
        cl = sdmx_api.get_codelist(agency,id,version)
        SdmxData.__cache_codelists[cl_id] = cl

        return cl["data"]["codelists"][0]["codes"]
