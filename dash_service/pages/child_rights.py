from dash import (
    html,
    dcc,
    callback_context,
    ALL,
    Input,
    Output,
    State,
    register_page,
    callback,
)
import dash_bootstrap_components as dbc

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import textwrap

from dash_service.pages.transmonee import (
    geo_json_countries,
    get_base_layout,
    make_card,
    indicator_card,
    graphs_dict,
    selections,
    themes,
    aio_options,
    active_button,
    breakdown_options,
    default_compare,
    aio_area_figure,
    fig_options,
    download_data,
    update_country_selection,
    filter_crc_data,
    available_crc_years,
    update_indicator_dropdown,
)

min_max_card_suffix = "min - max values"

page_config = {
    "DEM": {
        "NAME": "Demographics",
        "CARDS": [
            {
                "name": "",
                "indicator": "DM_CHLD_POP",
                "suffix": "children",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "DM_CHLD_POP_PT",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "DM_BRTS",
                "suffix": "births",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "DM_FRATE_TOT",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "DM_POP_NETM",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "DM_CHLD_POP",
                "DM_CHLD_POP_PT",
                "DM_BRTS",
                "DM_FRATE_TOT",
                "DM_POP_NETM",
            ],
            "default_graph": "bar",
            "default": "DM_CHLD_POP",
        },
    },
    "PLE": {
        "NAME": "Political economy",
        "CARDS": [
            {
                "name": "",
                "indicator": "EC_HDI",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EC_TEC_GRL_GOV_EXP",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EC_NY_GDP_PCAP_PP_CD",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EC_NY_GNP_PCAP_CD",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PV_GINI_COEF",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EC_SL_UEM_TOTL_ZS",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EC_EAP_RT",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "EC_HDI",
                "EC_TEC_GRL_GOV_EXP",
                "EC_NY_GDP_PCAP_PP_CD",
                "EC_NY_GNP_PCAP_CD",
                "PV_GINI_COEF",
                "EC_SL_UEM_TOTL_ZS",
                "EC_EAP_RT",
            ],
            "default_graph": "bar",
            "default": "EC_HDI",
        },
    },
    "CRG": {
        "NAME": "Child rights governance",
        "CARDS": [
            {
                "name": "",
                "indicator": "PP_SG_NHR_IMPLN",
                "suffix": "countries in compliance with the Paris Principles",
                "min_max": False,
                # "data_provided": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": ["PP_SG_NHR_IMPLN"],
            "default_graph": "map",
            "default": "PP_SG_NHR_IMPLN",
        },
    },
    "SPE": {
        "NAME": "Public spending on children",
        "CARDS": [
            {
                "name": "",
                "indicator": "EDU_FIN_EXP_PT_GDP",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_FIN_EXP_L02",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_FIN_EXP_L1",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_SH_XPD_GHED_GD_ZS",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_SH_XPD_GHED_GD_ZS",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EC_SP_GOV_EXP_GDP",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EC_EXP_FAM_CHLD_EXP",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "EDU_FIN_EXP_PT_GDP",
                "EDU_FIN_EXP_L02",
                "EDU_FIN_EXP_L1",
                "HT_SH_XPD_GHED_GD_ZS",
                "EC_SP_GOV_EXP_GDP",
                "EC_EXP_FAM_CHLD_EXP",
            ],
            "default_graph": "bar",
            "default": "EDU_FIN_EXP_PT_GDP",
        },
    },
    "DTA": {
        "NAME": "Data on children",
        "CARDS": [
            {
                "name": "",
                "indicator": "CR_IQ_SCI_OVRL",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "CR_SG_STT_FPOS",
                "suffix": "countries",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "CR_SG_STT_CAPTY",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "CR_SG_STT_NSDSFND",
                "suffix": "countries",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "CR_SG_STT_NSDSIMPL",
                "suffix": "countries",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "CR_SG_STT_NSDSFDGVT",
                "suffix": "countries",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "CR_SG_STT_NSDSFDDNR",
                "suffix": "countries",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "CR_SG_STT_NSDSFDOTHR",
                "suffix": "countries",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "CR_SG_REG_CENSUSN",
                "suffix": "countries",
                "min_max": False,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "CR_IQ_SCI_OVRL",
                "CR_SG_STT_FPOS",
                "CR_SG_STT_CAPTY",
                "CR_SG_STT_NSDSFND",
                "CR_SG_STT_NSDSIMPL",
                "CR_SG_STT_NSDSFDGVT",
                "CR_SG_STT_NSDSFDDNR",
                "CR_SG_STT_NSDSFDOTHR",
                "CR_SG_REG_CENSUSN",
            ],
            "default_graph": "map",
            "default": "CR_IQ_SCI_OVRL",
        },
    },
    "REM": {
        "NAME": "Right to remedy",
        "CARDS": [
            {
                "name": "",
                "indicator": "JJ_CHLD_COMPLAINT_HHRR",
                "suffix": "children",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "JJ_CHLD_DISAB_COMPLAINT_HHRR",
                "suffix": "children",
                "min_max": False,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": ["JJ_CHLD_COMPLAINT_HHRR", "JJ_CHLD_DISAB_COMPLAINT_HHRR"],
            "default_graph": "bar",
            "default": "JJ_CHLD_COMPLAINT_HHRR",
        },
    },
    "VIO": {
        "NAME": "Violence against children and women",
        "CARDS": [
            {
                "name": "",
                "indicator": "PT_CHLD_1-14_PS-PSY-V_CGVR",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PT_ADLT_PS_NEC",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PT_F_GE15_PS-SX-EM_V_PTNR_12MNTH",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PT_F_18-29_SX-V_AGE-18",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PT_ST_13-15_BUL_30-DYS",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PT_CHLD_VIOLENCE_WELFARE",
                "suffix": "child victims of violence",
                "min_max": False,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "PT_CHLD_1-14_PS-PSY-V_CGVR",
                "PT_ADLT_PS_NEC",
                "PT_F_GE15_PS-SX-EM_V_PTNR_12MNTH",
                "PT_F_18-29_SX-V_AGE-18",
                "PT_ST_13-15_BUL_30-DYS",
                "PT_CHLD_VIOLENCE_WELFARE",
            ],
            "default_graph": "bar",
            "default": "PT_CHLD_1-14_PS-PSY-V_CGVR",
        },
    },
    "CPC": {
        "NAME": "Children in alternative care",
        "CARDS": [
            {
                "name": "",
                "indicator": "PT_CHLD_INFORMALCARE_RATE",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PT_CHLD_INRESIDENTIAL_RATE_B",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PT_CHLD_INCARE_FOSTER_RATE",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PT_CHLD_ADOPTION_RATE",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "PT_CHLD_INFORMALCARE_RATE",
                "PT_CHLD_INRESIDENTIAL_RATE_B",
                "PT_CHLD_INCARE_FOSTER_RATE",
                "PT_CHLD_ADOPTION_RATE",
            ],
            "default_graph": "bar",
            "default": "PT_CHLD_INFORMALCARE_RATE",
        },
    },
    "JUS": {
        "NAME": "Justice for children",
        "CARDS": [
            {
                "name": "",
                "indicator": "JJ_CHLD_DETENTION_RATE",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "JJ_CHLD_PRE_SENTENCE_DETENTION_RATE",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "JJ_CHLD_POST_SENTENCE_DETENTION_RATE",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "JJ_CHLD_ENTER_PRE_SENTENCE_DETENTION_RATE",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "JJ_CHLD_CUSTODIAL_SENTENCE_PROP",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "JJ_CHLD_ALTERNATIVE_SENTENCE_PROP",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "JJ_CHLD_VICTIM_CRIME_RATE",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "JJ_CHLD_WITNESS_CRIME_RATE",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "JJ_VC_PRS_UNSNT",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "JJ_CHLD_DETENTION_RATE",
                "JJ_CHLD_PRE_SENTENCE_DETENTION_RATE",
                "JJ_CHLD_POST_SENTENCE_DETENTION_RATE",
                "JJ_CHLD_ENTER_PRE_SENTENCE_DETENTION_RATE",
                "JJ_CHLD_CUSTODIAL_SENTENCE_PROP",
                "JJ_CHLD_ALTERNATIVE_SENTENCE_PROP",
                "JJ_CHLD_VICTIM_CRIME_RATE",
                "JJ_CHLD_WITNESS_CRIME_RATE",
                "JJ_VC_PRS_UNSNT",
            ],
            "default_graph": "bar",
            "default": "JJ_CHLD_DETENTION_RATE",
        },
    },
    "MAR": {
        "NAME": "Child marriage and other harmful practices",
        "CARDS": [
            {
                "name": "",
                "indicator": "PT_F_20-24_MRD_U18",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PT_M_20-24_MRD_U18",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PT_F_15-19_MRD",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PT_M_15-19_MRD",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "PT_F_20-24_MRD_U18",
                "PT_M_20-24_MRD_U18",
                "PT_F_15-19_MRD",
                "PT_M_15-19_MRD",
            ],
            "default_graph": "bar",
            "default": "PT_F_20-24_MRD_U18",
        },
    },
    "LAB": {
        "NAME": "Child exploitation",
        "CARDS": [
            {
                "name": "",
                "indicator": "PT_CHLD_5-17_LBR_ECON-HC",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PT_CHLD_5-17_LBR_ECON",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "PT_CHLD_5-17_LBR_ECON-HC",
                "PT_CHLD_5-17_LBR_ECON",
            ],
            "default_graph": "bar",
            "default": "PT_CHLD_5-17_LBR_ECON-HC",
        },
    },
    "SPS": {
        "NAME": "Social protection system",
        "CARDS": [
            {
                "name": "",
                "indicator": "PV_SI_COV_BENFTS",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PV_SI_COV_CHLD",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PV_SI_COV_MATNL",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PV_SI_COV_DISAB",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PV_SI_COV_UEMP",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PV_SI_COV_VULN",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PV_SI_COV_POOR",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EC_EXP_FAM_CHLD_EXP",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "PV_SI_COV_BENFTS",
                "PV_SI_COV_CHLD",
                "PV_SI_COV_MATNL",
                "PV_SI_COV_DISAB",
                "PV_SI_COV_UEMP",
                "PV_SI_COV_VULN",
                "PV_SI_COV_POOR",
                "EC_EXP_FAM_CHLD_EXP",
            ],
            "default_graph": "bar",
            "default": "PV_SI_COV_BENFTS",
        },
    },
    "MAT": {
        "NAME": "Child poverty and material deprivation",
        "CARDS": [
            {
                "name": "",
                "indicator": "SI_POV_UMIC",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PV_SDG_SI_POV_NAHC",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PV_AROPE",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PV_SEV_MAT_SOC_DPRT",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PV_AROPRT",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PV_LOW_WORK",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PV_INABLE_PROTEIN",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "SI_POV_UMIC",
                "PV_SDG_SI_POV_NAHC",
                "PV_AROPE",
                "PV_SEV_MAT_SOC_DPRT",
                "PV_AROPRT",
                "PV_LOW_WORK",
                "PV_INABLE_PROTEIN",
            ],
            "default_graph": "bar",
            "default": "SI_POV_UMIC",
        },
    },
    "WSH": {
        "NAME": "Water and sanitation",
        "CARDS": [
            {
                "name": "",
                "indicator": "WS_PPL_W-SM",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "WS_PPL_S-SM",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_NO_BTH_SHW_FLSH",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "WS_PPL_W-SM",
                "WS_PPL_S-SM",
                "HT_NO_BTH_SHW_FLSH",
            ],
            "default_graph": "bar",
            "default": "WS_PPL_W-SM",
        },
    },
    "REG": {
        "NAME": "Birth registration and identity",
        "CARDS": [
            {
                "name": "",
                "indicator": "PT_CHLD_Y0T4_REG",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PP_SG_REG_BRTH90N",
                "suffix": "countries",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "PP_SG_REG_DETH75N",
                "suffix": "countries",
                "min_max": False,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "PT_CHLD_Y0T4_REG",
                "PP_SG_REG_BRTH90N",
                "PP_SG_REG_DETH75N",
            ],
            "default_graph": "bar",
            "default": "PT_CHLD_Y0T4_REG",
        },
    },
    "ICT": {
        "NAME": "Information, internet and protection of privacy",
        "CARDS": [
            {
                "name": "",
                "indicator": "PP_IT_USE_ii99",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PP_SE_ADT_ACTS_PRGM",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PP_SE_ADT_ACTS_ATCH",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PP_SE_ADT_ACTS_SFWR",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "ICT_PERSONAL_DATA",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "ICT_SECURITY_CONCERN",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "PP_IT_USE_ii99",
                "PP_SE_ADT_ACTS_PRGM",
                "PP_SE_ADT_ACTS_ATCH",
                "PP_SE_ADT_ACTS_SFWR",
                "ICT_PERSONAL_DATA",
                "ICT_SECURITY_CONCERN",
            ],
            "default_graph": "bar",
            "default": "PP_IT_USE_ii99",
        },
    },
    "HSM": {
        "NAME": "Health system",
        "CARDS": [
            {
                "name": "",
                "indicator": "HT_UHC_IDX",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_SH_XPD_CHEX_GD_ZS",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_SH_XPD_GHED_GD_ZS",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_SH_XPD_GHED_GE_ZS",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_SH_XPD_GHED_PP_CD",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_SH_XPD_OOPC_CH_ZS",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_INS_COV",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "HT_UHC_IDX",
                "HT_SH_XPD_CHEX_GD_ZS",
                "HT_SH_XPD_GHED_GD_ZS",
                "HT_SH_XPD_GHED_GE_ZS",
                "HT_SH_XPD_GHED_PP_CD",
                "HT_SH_XPD_OOPC_CH_ZS",
                "HT_INS_COV",
            ],
            "default_graph": "bar",
            "default": "HT_UHC_IDX",
        },
    },
    "MNH": {
        "NAME": "Maternal, newborn and child health",
        "CARDS": [
            {
                "name": "",
                "indicator": "CME_MRM0",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "CME_MRY0",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "CME_MRY0T4",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "MNCH_SAB",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "CME_SBR",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "MNCH_CSEC",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "NT_BW_LBW",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "CME_MRM0",
                "CME_MRY0",
                "CME_MRY0T4",
                "MNCH_SAB",
                "CME_SBR",
                "MNCH_CSEC",
                "NT_BW_LBW",
            ],
            "default_graph": "bar",
            "default": "CME_MRM0",
        },
    },
    "IMM": {
        "NAME": "Immunization",
        "CARDS": [
            {
                "name": "",
                "indicator": "IM_MCV2",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "IM_DTP3",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "IM_PCV3",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "IM_HPV",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "IM_MCV2",
                "IM_DTP3",
                "IM_PCV3",
                "IM_HPV",
            ],
            "default_graph": "bar",
            "default": "IM_MCV2",
        },
    },
    "NUT": {
        "NAME": "Nutrition",
        "CARDS": [
            {
                "name": "",
                "indicator": "NT_BF_EXBF",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "NT_BF_EIBF",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "NT_CF_ISSSF_FL",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "NT_CF_MAD",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "NT_ANT_WHZ_PO2",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "NT_CHLD_OBESITY",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "NT_ANT_WHZ_NE2",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "NT_ANT_HAZ_NE2",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_SH_STA_ANEM",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_ANEM_U5",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "NT_BF_EXBF",
                "NT_BF_EIBF",
                "NT_CF_ISSSF_FL",
                "NT_CF_MAD",
                "NT_ANT_WHZ_PO2",
                "NT_CHLD_OBESITY",
                "NT_ANT_WHZ_NE2",
                "NT_ANT_HAZ_NE2",
                "HT_SH_STA_ANEM",
                "HT_ANEM_U5",
            ],
            "default_graph": "bar",
            "default": "NT_BF_EXBF",
        },
    },
    "ADO": {
        "NAME": "Adolescent physical, mental and reproductive health",
        "CARDS": [
            {
                "name": "",
                "indicator": "FT_SP_DYN_ADKL",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_ADOL_MT",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "MT_SDG_SUICIDE",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_CHLD_DAILY_EXER",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "FT_SP_DYN_ADKL",
                "HT_ADOL_MT",
                "MT_SDG_SUICIDE",
                "HT_CHLD_DAILY_EXER",
            ],
            "default_graph": "bar",
            "default": "FT_SP_DYN_ADKL",
        },
    },
    "HIV": {
        "NAME": "HIV/AIDS",
        "CARDS": [
            {
                "name": "",
                "indicator": "HVA_EPI_LHIV_0-19",
                "suffix": "estimated children living with HIV",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "HVA_EPI_INF_RT_0-14",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HVA_EPI_DTH_ANN_0-19",
                "suffix": "estimated AIDS-related deaths",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "HVA_PMTCT_MTCT",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HVA_PMTCT_STAT_CVG",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HVA_PED_ART_CVG",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HVA_PREV_KNOW",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "HVA_EPI_LHIV_0-19",
                "HVA_EPI_INF_RT_0-14",
                "HVA_EPI_DTH_ANN_0-19",
                "HVA_PMTCT_MTCT",
                "HVA_PMTCT_STAT_CVG",
                "HVA_PED_ART_CVG",
                # "HVA_PREV_KNOW",
            ],
            "default_graph": "bar",
            "default": "HVA_EPI_LHIV_0-19",
        },
    },
    "ESY": {
        "NAME": "Education system",
        "CARDS": [
            {
                "name": "",
                "indicator": "EDU_FIN_EXP_PT_GDP",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_FIN_EXP_L02",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_FIN_EXP_L1",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_FIN_EXP_L2",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_FIN_EXP_L3",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_SDG_FREE_EDU_L02",
                "suffix": "countries guaranteeing at least one year",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "EDU_SDG_COMP_EDU_L02",
                "suffix": "countries guaranteeing at least one year",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "EDUNF_ADMIN_L1_GLAST_MAT",
                "suffix": "countries",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "EDUNF_ADMIN_L1_GLAST_REA",
                "suffix": "countries",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "EDUNF_ADMIN_L2_MAT",
                "suffix": "countries",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "EDUNF_ADMIN_L2_REA",
                "suffix": "countries",
                "min_max": False,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "EDU_FIN_EXP_PT_GDP",
                # taking these indicators out for the moment as they are no longer being published
                # "EDU_FIN_EXP_L02",
                # "EDU_FIN_EXP_L1",
                # "EDU_FIN_EXP_L2",
                # "EDU_FIN_EXP_L3",
                "EDUNF_ADMIN_L1_GLAST_MAT",
                "EDUNF_ADMIN_L1_GLAST_REA",
                "EDUNF_ADMIN_L2_MAT",
                "EDUNF_ADMIN_L2_REA",
                "EDU_SDG_FREE_EDU_L02",
                "EDU_SDG_COMP_EDU_L02",
            ],
            "default_graph": "bar",
            "default": "EDU_FIN_EXP_PT_GDP",
        },
    },
    "EPA": {
        "NAME": "Education access and participation",
        "CARDS": [
            {
                "name": "",
                "indicator": "EDUNF_CR_L1",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDUNF_CR_L2",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDUNF_CR_L3",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDUNF_ROFST_L1_UNDER1",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDUNF_ROFST_L1",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDUNF_ROFST_L2",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDUNF_ROFST_L3",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDUNF_NERA_L1_UNDER1",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "ECD_EARLY_EDU",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_SDG_SCH_L1",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_SDG_SCH_L2",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_SDG_SCH_L3",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDUNF_ESL_L1",
                "suffix": "children",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "EDAT_LFSE_14",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_SDG_PRYA",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "EDUNF_CR_L1",
                "EDUNF_CR_L2",
                "EDUNF_CR_L3",
                "EDUNF_ROFST_L1_UNDER1",
                "EDUNF_ROFST_L1",
                "EDUNF_ROFST_L2",
                "EDUNF_ROFST_L3",
                "EDUNF_NERA_L1_UNDER1",
                "ECD_EARLY_EDU",
                "EDU_SDG_SCH_L1",
                "EDU_SDG_SCH_L2",
                "EDU_SDG_SCH_L3",
                "EDAT_LFSE_14",
                "EDU_SDG_PRYA",
            ],
            "default_graph": "bar",
            "default": "EDUNF_CR_L1",
        },
    },
    "EQU": {
        "NAME": "Learning quality and skills",
        "CARDS": [
            {
                "name": "",
                "indicator": "EDU_PISA_LOW_ACHIEVE_MAT",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_PISA_LOW_ACHIEVE_REA",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_PISA_LOW_ACHIEVE_SCI",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_SDG_STU_L2_GLAST_MAT",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_SDG_STU_L2_GLAST_REA",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_SDG_YOUTH_NEET",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "EDU_PISA_LOW_ACHIEVE_MAT",
                "EDU_PISA_LOW_ACHIEVE_REA",
                "EDU_PISA_LOW_ACHIEVE_SCI",
                "EDU_SDG_STU_L2_GLAST_MAT",
                "EDU_SDG_STU_L2_GLAST_REA",
                "EDU_SDG_YOUTH_NEET",
            ],
            "default_graph": "bar",
            "default": "EDU_PISA_LOW_ACHIEVE_MAT",
        },
    },
    "ELE": {
        "NAME": "Leisure and culture",
        "CARDS": [
            {
                "name": "",
                "indicator": "PP_ADOL_TVGM",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PP_ADOL_INET",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "PP_ADOL_TVGM",
                "PP_ADOL_INET",
            ],
            "default_graph": "bar",
            "default": "PP_ADOL_TVGM",
        },
    },
    "GND": {
        "NAME": "Gender",
        "CARDS": [
            {
                "name": "",
                "indicator": "EC_GDI",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EC_GII",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "FT_SP_DYN_ADKL",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_SE_AGP_CPRA_L3",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_SE_TOT_GPI_L2_MAT",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_SE_TOT_GPI_L2_REA",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PT_CHLD_1-14_PS-PSY-V_CGVR",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PT_F_GE15_PS-SX-EM_V_PTNR_12MNTH",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PT_F_15-19_MRD",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PT_F_20-24_MRD_U18",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "EC_GDI",
                "EC_GII",
                "FT_SP_DYN_ADKL",
                "EDU_SE_AGP_CPRA_L3",
                "EDU_SE_TOT_GPI_L2_MAT",
                "EDU_SE_TOT_GPI_L2_REA",
                "PT_CHLD_1-14_PS-PSY-V_CGVR",
                "PT_F_GE15_PS-SX-EM_V_PTNR_12MNTH",
                "PT_F_15-19_MRD",
                "PT_F_20-24_MRD_U18",
            ],
            "default_graph": "bar",
            "default": "EC_GDI",
        },
    },
    "DIS": {
        "NAME": "Disability",
        "CARDS": [
            {
                "name": "",
                "indicator": "HT_REG_CHLD_DISAB_PROP",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_NEW_REG_CHLD_DISAB_PROP",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_SDG_SCH_L1",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_SDG_SCH_L2",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_SDG_SCH_L3",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PT_CHLD_DISAB_INRESIDENTIAL_PROP",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PT_CHLD_DISAB_INFAMILY_PROP",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PT_CHLD_DISAB_INFOSTER_PROP",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PV_SI_COV_DISAB",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "HT_REG_CHLD_DISAB_PROP",
                "HT_NEW_REG_CHLD_DISAB_PROP",
                "EDU_SDG_SCH_L1",
                "EDU_SDG_SCH_L2",
                "EDU_SDG_SCH_L3",
                "PT_CHLD_DISAB_INRESIDENTIAL_PROP",
                "PT_CHLD_DISAB_INFAMILY_PROP",
                "PT_CHLD_DISAB_INFOSTER_PROP",
                "PV_SI_COV_DISAB",
            ],
            "default_graph": "bar",
            "default": "HT_REG_CHLD_DISAB_PROP",
        },
    },
    "ECD": {
        "NAME": "Early childhood development",
        "CARDS": [
            {
                "name": "",
                "indicator": "ECD_CHLD_36-59M_LMPSL",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "CME_MRM0",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "NT_BF_EXBF",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "ECD_CHLD_24-59M_ADLT_SRC",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDUNF_NERA_L1_UNDER1",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "ECD_IN_CHILDCARE",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "ECD_EARLY_EDU",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "ECD_CHLD_36-59M_LMPSL",
                "CME_MRM0",
                "NT_BF_EXBF",
                "ECD_CHLD_24-59M_ADLT_SRC",
                "EDUNF_NERA_L1_UNDER1",
                "ECD_IN_CHILDCARE",
                "ECD_EARLY_EDU",
            ],
            "default_graph": "bar",
            "default": "ECD_CHLD_36-59M_LMPSL",
        },
    },
    "ODA": {
        "NAME": "Adolescents",
        "CARDS": [
            {
                "name": "",
                "indicator": "FT_SP_DYN_ADKL",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "MT_SDG_SUICIDE",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_SDG_YOUTH_NEET",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_SDG_STU_L2_GLAST_MAT",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDU_SDG_STU_L2_GLAST_REA",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "EDUNF_CR_L3",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "PT_CHLD_1-14_PS-PSY-V_CGVR",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "ICT_PERSONAL_DATA",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "FT_SP_DYN_ADKL",
                "MT_SDG_SUICIDE",
                "EDU_SDG_YOUTH_NEET",
                "EDU_SDG_STU_L2_GLAST_MAT",
                "EDU_SDG_STU_L2_GLAST_REA",
                "EDUNF_CR_L3",
                "PT_CHLD_1-14_PS-PSY-V_CGVR",
                "ICT_PERSONAL_DATA",
            ],
            "default_graph": "bar",
            "default": "FT_SP_DYN_ADKL",
        },
    },
    "ENV": {
        "NAME": "Environment and climate change",
        "CARDS": [
            {
                "name": "",
                "indicator": "CR_CCRI",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "CR_CCRI_EXP_CESS",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "CR_CCRI_VUL_ES",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "CR_EG_EGY_CLEAN",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "CR_SH_STA_ASAIRP",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "CR_SH_HAP_ASMORT",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "CR_SH_AAP_ASMORT",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "HT_SDG_PM25",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "CR_CCRI",
                "CR_CCRI_EXP_CESS",
                "CR_CCRI_VUL_ES",
                "CR_EG_EGY_CLEAN",
                "CR_SH_STA_ASAIRP",
                "CR_SH_HAP_ASMORT",
                "CR_SH_AAP_ASMORT",
                "HT_SDG_PM25",
            ],
            "default_graph": "bar",
            "default": "CR_CCRI",
        },
    },
    "DCD": {
        "NAME": "Disaster, conflict and displacement",
        "CARDS": [
            {
                "name": "",
                "indicator": "CR_INFORM",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "CR_VC_DSR_MTMP",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "CR_VC_DSR_DAFF",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "CR_SG_DSR_LGRGSR",
                "suffix": min_max_card_suffix,
                "min_max": True,
            },
            {
                "name": "",
                "indicator": "DM_ASYL_FRST",
                "suffix": "persons",
                "min_max": False,
            },
            {
                "name": "",
                "indicator": "DM_ASYL_UASC",
                "suffix": "persons",
                "min_max": False,
            },
        ],
        "AIO_AREA": {
            "graphs": graphs_dict,
            "indicators": [
                "CR_INFORM",
                "CR_VC_DSR_MTMP",
                "CR_VC_DSR_DAFF",
                "CR_SG_DSR_LGRGSR",
                "DM_ASYL_FRST",
                "DM_ASYL_UASC",
            ],
            "default_graph": "bar",
            "default": "CR_INFORM",
        },
    },
}

# customization of plots requested by Siraj
packed_config = {}

# register_page(
#     __name__,
#     # path_template="/transmonee/<page_slug>",
#     path="/transmonee/child-rights",
#     title="Child Rights Landscape and Governance",
#     # order=1,
# )
page_prefix = "crg"
page_path = "child-rights"
domain_colour = "#562061"
light_domain_colour = "#e7c9ed"
dark_domain_colour = "#44194d"
map_colour = "purpor"


# configure the Dash instance's layout
def layout(page_slug=None, **query_parmas):
    return html.Div(
        [
            html.Br(),
            dcc.Store(id=f"{page_prefix}-store"),
            dcc.Store(id=f"{page_prefix}-data-store"),
            dbc.Container(
                fluid=True,
                children=get_base_layout(
                    indicators=page_config,
                    page_prefix=page_prefix,
                    domain_colour=domain_colour,
                    query_params=query_parmas,
                ),
            ),
            html.Br(),
        ],
        id="mainContainer",
    )


@callback(
    Output(f"{page_prefix}-indicator-dropdown", "options"),
    Output(f"{page_prefix}-indicator-dropdown", "value"),
    Input(f"{page_prefix}-crm-dropdown", "value"),
)
def apply_update_indicator_dropdown(indicator_filter):
    print(f"update_indicator_dropdown - indicator_filter: {indicator_filter}")
    return update_indicator_dropdown(indicator_filter)


@callback(
    Output({"type": "button_group", "index": f"{page_prefix}-AIO_AREA"}, "children"),
    Input(f"{page_prefix}-store", "data"),
    State(f"{page_prefix}-indicators", "data"),
    prevent_initial_call=True,
)
def set_aio_options(theme, indicators_dict):
    return aio_options(theme, indicators_dict, page_prefix)


@callback(
    Output({"type": "area_types", "index": f"{page_prefix}-AIO_AREA"}, "options"),
    Output({"type": "area_types", "index": f"{page_prefix}-AIO_AREA"}, "value"),
    [Input(f"{page_prefix}-indicator-dropdown", "value")],
    prevent_initial_call=True,
)
def set_fig_options(indicator):
    return fig_options(indicator)


@callback(
    Output({"type": "area_breakdowns", "index": f"{page_prefix}-AIO_AREA"}, "options"),
    [
        Input(f"{page_prefix}-indicator-dropdown", "value"),
        Input({"type": "area_types", "index": f"{page_prefix}-AIO_AREA"}, "value"),
    ],
    prevent_initial_call=True,
)
def set_breakdown_options(indicator, fig_type):
    return breakdown_options(indicator, fig_type)


@callback(
    Output({"type": "area_breakdowns", "index": f"{page_prefix}-AIO_AREA"}, "value"),
    Input({"type": "area_breakdowns", "index": f"{page_prefix}-AIO_AREA"}, "options"),
    [
        State({"type": "area_types", "index": f"{page_prefix}-AIO_AREA"}, "value"),
        State(f"{page_prefix}-indicators", "data"),
        State(f"{page_prefix}-indicator-dropdown", "value"),
    ],
    prevent_initial_call=True,
)
def set_default_compare(compare_options, selected_type, indicators_dict, indicator):
    print(f"Indicator (default_compare): {indicator}")
    return default_compare(compare_options, selected_type, indicators_dict, indicator)


@callback(
    Output(f"{page_prefix}-download-csv-info", "data"),
    Input(f"{page_prefix}-download_btn", "n_clicks"),
    State(f"{page_prefix}-data-store", "data"),
    prevent_initial_call=True,
)
def apply_download_data(n_clicks, data):
    return download_data(n_clicks, data)


@callback(
    Output(f"{page_prefix}-country-filter", "options"),
    Output(f"{page_prefix}-country-filter", "value"),
    [
        Input(f"{page_prefix}-country-group", "value"),
        Input(f"{page_prefix}-country-filter", "value"),
    ],
    prevent_initial_call=True,
)
def apply_update_country_selection(country_group, country_selection):
    return update_country_selection(country_group, country_selection)


@callback(
    Output(f"{page_prefix}-year-filter-crc", "options"),
    Output(f"{page_prefix}-year-filter-crc", "value"),
    [
        Input(f"{page_prefix}-country-filter-crc", "value"),
        Input(f"{page_prefix}-indicator-dropdown", "value"),
        Input(f"{page_prefix}-indicators", "data"),
    ],
    prevent_initial_call=True,
)
def apply_available_crc_years(country, indicator, indicators_dict):
    return available_crc_years(country, indicator, indicators_dict)


@callback(
    Output(f"{page_prefix}-crc-header", "children"),
    Output(f"{page_prefix}-crc-accordion", "children"),
    Input(f"{page_prefix}-year-filter-crc", "value"),
    Input(f"{page_prefix}-country-filter-crc", "value"),
    Input(f"{page_prefix}-indicator-dropdown", "value"),
    prevent_initial_call=True,
)
def apply_filter_crc_data(year, country, indicator):
    return filter_crc_data(year, country, indicator, page_prefix)


@callback(
    [
        Output(f"{page_prefix}-collapse-years-button", "label"),
        Output({"type": "area", "index": f"{page_prefix}-AIO_AREA"}, "figure"),
        Output(f"{page_prefix}-aio_area_area_info", "children"),
        Output(f"{page_prefix}-indicator_card", "children"),
        Output(f"{page_prefix}-aio_area_data_info_rep", "children"),
        Output(f"{page_prefix}-data-hover-body", "children"),
        Output(f"{page_prefix}-aio_area_data_info_nonrep", "children"),
        Output(f"{page_prefix}-no-data-hover-body", "children"),
        Output(f"{page_prefix}-aio_area_graph_info", "children"),
        Output(f"{page_prefix}-data-store", "data"),
        Output(f"{page_prefix}-definition-text", "children"),
    ],
    [
        Input(f"{page_prefix}-indicator-dropdown", "value"),
        Input({"type": "area_breakdowns", "index": f"{page_prefix}-AIO_AREA"}, "value"),
        Input(f"{page_prefix}-year_slider", "value"),
        Input(f"{page_prefix}-country-filter", "value"),
        Input(f"{page_prefix}-country-group", "value"),
        
    ],
    [
        State(f"{page_prefix}-indicators", "data"),
        State({"type": "area_types", "index": f"{page_prefix}-AIO_AREA"}, "value"),
    ],
    prevent_initial_call=True,
)
def apply_aio_area_figure(
    indicator,
    compare,
    years_slider,
    countries,
    country_group,
    indicators_dict,
    selected_type,
):
    print(f"Area_Fig - Indicator: {indicator}")
    return aio_area_figure(
        indicator,
        compare,
        years_slider,
        countries,
        country_group,
        indicators_dict,
        selected_type,
        page_prefix,
        domain_colour,
        map_colour,
    )
