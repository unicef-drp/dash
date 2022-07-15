import json
import logging
import pathlib
import collections
from io import BytesIO
from re import L
import urllib

import dash_html_components as html
import numpy as np
import pandas as pd
import requests
from requests.exceptions import HTTPError

import pandasdmx as sdmx


# TODO: Move all of these to env/setting vars from production
sdmx_url = "https://sdmx.data.unicef.org/ws/public/sdmxapi/rest/data/ECARO,TRANSMONEE,1.0/.{}....?format=csv&startPeriod={}&endPeriod={}"

geo_json_file = (
    pathlib.Path(__file__).parent.parent.absolute() / "assets/countries.geo.json"
)
with open(geo_json_file) as shapes_file:
    geo_json_countries = json.load(shapes_file)

with open(
    pathlib.Path(__file__).parent.parent.absolute() / "assets/indicator_config.json"
) as config_file:
    indicators_config = json.load(config_file)

unicef = sdmx.Request("UNICEF")

metadata = unicef.dataflow("TRANSMONEE", provider="ECARO", version="1.0")
dsd = metadata.structure["DSD_ECARO_TRANSMONEE"]

indicator_names = {
    code.id: code.name.en
    for code in dsd.dimensions.get("INDICATOR").local_representation.enumerated
}
# lbassil: get the age groups code list as it is not in the DSD
cl_age = unicef.codelist("CL_AGE", version="1.0")
age_groups = sdmx.to_pandas(cl_age)
dict_age_groups = age_groups["codelist"]["CL_AGE"].reset_index()
age_groups_names = {
    age["CL_AGE"]: age["name"]
    for index, age in dict_age_groups.iterrows()
    if age["CL_AGE"] != "_T"
}

units_names = {
    unit.id: str(unit.name)
    for unit in dsd.attributes.get("UNIT_MEASURE").local_representation.enumerated
}

# lbassil: get the names of the residence dimensions
residence_names = {
    residence.id: str(residence.name)
    for residence in dsd.dimensions.get("RESIDENCE").local_representation.enumerated
}

# lbassil: get the names of the wealth quintiles dimensions
wealth_names = {
    wealth.id: str(wealth.name)
    for wealth in dsd.dimensions.get("WEALTH_QUINTILE").local_representation.enumerated
}

gender_names = {"F": "Female", "M": "Male", "_T": "Total"}

dimension_names = {
    "SEX": "Sex_name",
    "AGE": "Age_name",
    "RESIDENCE": "Residence_name",
    "WEALTH_QUINTILE": "Wealth_name",
}

adolescent_codes = [
    "DM_ASYL_FRST",
    "DM_ASYL_UASC",
    "HT_ADOL_UNMETMED_FEAR",
    "HT_ADOL_UNMETMED_HOPING",
    "HT_ADOL_UNMETMED_NOKNOW",
    "HT_ADOL_UNMETMED_NOTIME",
    "HT_ADOL_UNMETMED_NOUNMET",
    "HT_ADOL_UNMETMED_TOOEFW",
    "HT_ADOL_UNMETMED_TOOEXP",
    "HT_ADOL_UNMETMED_TOOFAR",
    "HT_ADOL_UNMETMED_WAITING",
    "HT_ADOL_UNMETMED_OTH",
    "HT_CDRT_SELF_HARM",
    "HT_SH_HIV_INCD",
    "HVA_EPI_LHIV_0-19",
    "HVA_EPI_LHIV_15-24",
    "JJ_PRISIONERS_RT",
    "MNCH_CSEC",
    "MNCH_PNCMOM",
    "PT_ADLT_PS_NEC",
    "PT_CHLD_1-14_PS-PSY-V_CGVR",
    "PT_CHLD_5-17_LBR_ECON",
    "PT_CHLD_5-17_LBR_ECON-HC",
    "PT_CHLD_CARED_BY_FOSTER",
    "PT_CHLD_ENTEREDFOSTER",
    "PT_CHLD_INRESIDENTIAL",
    "PT_F_15-49_W-BTNG",
    "PT_F_GE15_PS-SX-EM_V_PTNR_12MNTH",
    "PT_M_15-49_W-BTNG",
    "PT_ST_13-15_BUL_30-DYS",
    "PV_AROPE",
    "PV_AROPRT",
    "PV_SD_MDP_MUHC",
    "PV_SEV_MAT_DPRT",
    "PV_SI_POV_EMP1",
]

adolescent_age_groups = [
    "_T",
    "Y14T17",
    "Y0T13",
    "Y1T4",
    "Y0",
    "Y0T14",
    "Y14T15",
    "Y16T17",
    "Y16T19",
    "Y16T24",
    "Y10T14",
    "Y15T19",
    "Y15T24",
    "Y10T19",
    "Y0T17",
    "Y15T49",
    "Y20T24",
    "Y18T49",
    "Y18T29",
    "Y0T24",
    "Y25T39",
    "Y40T59",
    "Y_GE50",
    "Y_GE15",
    "Y1T14",
    "Y2T14",
    "Y5T14",
    "Y5T17",
    "Y7T17",
    "Y10T17",
    "Y13T15",
    "Y15",
    "Y11T15",
    "Y12T17",
    "Y0T15",
    "Y0T4",
    "M0",
]

# Add all indicators found in the data dictionary to get their data to the query data page
data_query_codes = [
    "DM_BRTS",
    # "DM_POP_TOT",
    # "DM_AVG_POP_TOT",
    # "DM_POP_PROP",
    "DM_DPR_AGE",
    "DM_DPR_CHD",
    "DM_DPR_OLD",
    # "DM_IMG",
    # "DM_EMG",
    # "DM_NEXTRT_MG",
    "DM_MRG_AGE",
    "DM_DIV",
    "DM_CRDIVRT",
    "DM_CHLD_DIV",
    "DM_CHLDRT_DIV",
    "DM_POP_TOT_AGE",
    "FT_WHS_PBR",
    "MT_SP_DYN_CDRT_IN",
    "DM_LIFE_EXP",
    "HT_SH_HAP_HBSAG",
    "HT_SH_TBS_INCD",
    "HT_SH_SUD_ALCOL",
    "HT_DIST79DTP3_P",
    "IM_MCV2",
    "HT_DIST79MCV2_P",
    "HT_SDG_PM25",
    "ECD_CHLD_36-59M_ADLT_SRC",
    "HT_SH_SUD_TREAT",
    "EDUNF_STU_L01_TOT",
    "EDU_SDG_GER_L01",
    "EDUNF_STU_L02_TOT",
    "EDUNF_FEP_L02",
    "EDUNF_NARA_L1_UNDER1",
    "EDUNF_FEP_L1",
    "EDUNF_FEP_L2",
    "EDUNF_FEP_L3",
    "EDUNF_STU_L3_GEN",
    "EDUNF_STU_L3_VOC",
    "EDUNF_STU_L3_GEN_PUB",
    "EDUNF_STU_L3_GEN_PRV",
    "EDUNF_STU_L3_VOC_PUB",
    "EDUNF_STU_L3_VOC_PRV",
    "EDUNF_GER_L1AND2",
    "EDU_TIMSS_MAT4",
    "EDU_TIMSS_SCI4",
    "EDU_TIMSS_MAT8",
    "EDU_TIMSS_SCI8",
    "EDU_PIRLS_REA",
    "EDUNF_REPP_L1",
    "EDUNF_REPP_L2",
    "EDUNF_FRP_L1",
    "EDUNF_SR_L1",
    "EDUNF_SR_L2",
    "EDUNF_STU_L4_TOT",
    "EDUNF_STU_L4_PUB",
    "EDUNF_STU_L4_PRV",
    "EDUNF_PRP_L4",
    "EDUNF_FEP_L4",
    "EDUNF_STU_L5T8_TOT",
    "EDUNF_STU_L5T8_PUB",
    "EDUNF_STU_L5T8_PRV",
    "EDUNF_PRP_L5T8",
    "EDUNF_FEP_L5T8",
    "EDUNF_GER_GPI_L02",
    "EDUNF_GER_GPI_L1",
    "EDUNF_GER_GPI_L2",
    "EDUNF_GER_GPI_L3",
    "EDUNF_GER_GPI_L2AND3",
    "EDUNF_PTR_L1",
    "EDUNF_PTR_L2",
    "EDUNF_PTR_L2AND3",
    "EDUNF_PTR_L3",
    "EDU_SDG_PTTR_L02",
    "EDU_SDG_PTTR_L1",
    "EDU_SDG_PTTR_L2",
    "EDU_SDG_PTTR_L3",
    "EDU_SDG_PQTR_L02",
    "EDU_SDG_PQTR_L1",
    "EDU_SDG_PQTR_L2",
    "EDU_SDG_PQTR_L3",
    "ECD_CHLD_U5_BKS-HM",
    "ECD_CHLD_U5_PLYTH-HM",
    "EDUNF_EA_L2T8",
    "EDU_PISA_MAT2",
    "EDU_PISA_MAT3",
    "EDU_PISA_MAT4",
    "EDU_PISA_MAT5",
    "EDU_PISA_MAT6",
    "EDU_PISA_REA2",
    "EDU_PISA_REA3",
    "EDU_PISA_REA4",
    "EDU_PISA_REA5",
    "EDU_PISA_REA6",
    "EDU_PISA_SCI2",
    "EDU_PISA_SCI3",
    "EDU_PISA_SCI4",
    "EDU_PISA_SCI5",
    "EDU_PISA_SCI6",
    "EDU_CHLD_DISAB_L02",
    "EDU_CHLD_DISAB_L1",
    "EDU_CHLD_DISAB_L2",
    "EDU_CHLD_DISAB_L3",
    "EDUNF_SAP_L02",
    "EDUNF_SAP_L1",
    "EDUNF_SAP_L2",
    "EDUNF_SAP_L3",
    "EDUNF_SAP_L2_GLAST",
    "EDUNF_FRP_L2AND3",
    "EDUNF_GER_GPI_L01",
    "EDUNF_OFST_L1T3",
    "EDUNF_PRP_L2AND3",
    "EDUNF_STU_L2AND3_PRV",
    "EDUNF_COMP_YR",
    "EDUNF_COMP_YR_L02T3",
    "EDUNF_PTR_L02",
    "EDUNF_GECER_L01",
    "EDUNF_GECER_L02",
    "ED_ANAR_L1",
    "ED_ANAR_L2",
    "ED_ANAR_L3",
    "EDU_SE_ACS_INTNT_L1",
    "EDU_SE_ACS_INTNT_L2",
    "EDU_SE_ACS_INTNT_L3",
    "EDU_SE_ACS_CMPTR_L1",
    "EDU_SE_ACS_CMPTR_L2",
    "EDU_SE_ACS_CMPTR_L3",
    "EDU_SE_ACS_ELECT_L1",
    "EDU_SE_ACS_ELECT_L2",
    "EDU_SE_ACS_ELECT_L3",
    "EDU_SE_TOT_GPI_L1_REA",
    "EDU_SE_TOT_GPI_L2_REA",
    "EDU_SE_TOT_GPI_L1_MAT",
    "EDU_SE_TOT_GPI_L2_MAT",
    "EDU_SE_TOT_GPI_FS_LIT",
    "EDU_SE_TOT_GPI_FS_NUM",
    "EDU_SE_AGP_CPRA_L1",
    "EDU_SE_AGP_CPRA_L2",
    "EDU_SE_AGP_CPRA_L3",
    "EDU_SE_GPI_PART",
    "EDU_SE_GPI_PTNPRE",
    "EDU_SE_GPI_TCAQ_L02",
    "EDU_SE_GPI_TCAQ_L1",
    "EDU_SE_GPI_TCAQ_L2",
    "EDU_SE_GPI_TCAQ_L3",
    "EDU_SE_NAP_ACHI_L1_REA",
    "EDU_SE_NAP_ACHI_L2_REA",
    "EDU_SE_NAP_ACHI_L1_MAT",
    "EDU_SE_NAP_ACHI_L2_MAT",
    "EDU_SE_IMP_FPOF_LIT",
    "EDU_SE_IMP_FPOF_NUM",
    "EDU_SE_LGP_ACHI_L1_REA",
    "EDU_SE_LGP_ACHI_L2_REA",
    "EDU_SE_LGP_ACHI_L1_MAT",
    "EDU_SE_LGP_ACHI_L2_MAT",
    "EDU_SE_ALP_CPLR_L1",
    "EDU_SE_ALP_CPLR_L2",
    "EDU_SE_ALP_CPLR_L3",
    "EDU_SE_TOT_SESPI_L1_REA",
    "EDU_SE_TOT_SESPI_L2_REA",
    "EDU_SE_TOT_SESPI_L1_MAT",
    "EDU_SE_TOT_SESPI_L2_MAT",
    "EDU_SE_TOT_SESPI_FS_LIT",
    "EDU_SE_TOT_SESPI_FS_NUM",
    "EDU_SE_TOT_RUPI_L1_REA",
    "EDU_SE_TOT_RUPI_L2_REA",
    "EDU_SE_TOT_RUPI_L1_MAT",
    "EDU_SE_TOT_RUPI_L2_MAT",
    "EDU_SE_AWP_CPRA_L1",
    "EDU_SE_AWP_CPRA_L2",
    "EDU_SE_AWP_CPRA_L3",
    "EDU_SE_GPI_ICTS_ATCH",
    "EDU_SE_GPI_ICTS_CPT",
    "EDU_SE_GPI_ICTS_CDV",
    "EDU_SE_GPI_ICTS_SSHT",
    "EDU_SE_GPI_ICTS_PRGM",
    "EDU_SE_GPI_ICTS_PST",
    "EDU_SE_GPI_ICTS_SFWR",
    "EDU_SE_GPI_ICTS_TRFF",
    "EDU_SE_GPI_ICTS_CMFL",
    "EDUNF_STEM_GRAD_RT",
    "DM_TOT_POP_PROSP",
    "DM_SP_POP_BRTH_MF",
    "DM_ADOL_YOUTH_POP",
    "DM_REPD_AGE_POP",
    "GN_MTNTY_LV_BNFTS",
    "GN_PTNTY_LV_BNFTS",
    "EC_GDI",
    "EC_HCI_OVRL",
    "EC_MIN_WAGE",
    "EC_IQ_CPA_GNDR_XQ",
    "EC_SIGI",
    "EC_YOUTH_UNE_RT",
    "EC_EAP_RT",
    "EC_GNI_PCAP_PPP",
    "EC_FB_BNK_ACCSS",
    "SL_DOM_TSPD",
    "SG_GEN_PARL",
    "CR_VC_VOV_GDSD",
    "PT_ADLS_10-14_LBR_HC",
    "ECD_CHLD_U5_LFT-ALN",
    "MNCH_MATERNAL_DEATHS",
    "MNCH_SH_MMR_RISK",
    "MNCH_SH_MMR_RISK_ZS",
    "MNCH_INSTDEL",
    "MNCH_BIRTH18",
    "HT_NCD_BMI_18A",
    "HVA_EPI_INF_ANN_15-24",
    "CR_CCRI_VUL_HT",
    "CR_CCRI_VUL_EDU",
    "CR_CCRI_VUL_WASH",
    "CR_CCRI_VUL_SP",
    "CR_CCRI_VUL_ES",
    "CR_CCRI",
    "CR_CCRI_EXP_WS",
    "CR_CCRI_EXP_RF",
    "CR_CCRI_EXP_CF",
    "CR_CCRI_EXP_TC",
    "CR_CCRI_EXP_VBD",
    "CR_CCRI_EXP_HEAT",
    "CR_CCRI_EXP_AP",
    "CR_CCRI_EXP_SWP",
    "CR_CCRI_EXP_CESS",
    "CR_UN_CHLD_RIGHTS",
    "CR_UN_CHLD_SALE",
    "CR_UN_RIGHTS_DISAB",
]

years = list(range(2010, 2022))

# a key:value dictionary of countries where the 'key' is the country name as displayed in the selection
# tree whereas the 'value' is the country name as returned by the sdmx list: https://sdmx.data.unicef.org/ws/public/sdmxapi/rest/codelist/UNICEF/CL_COUNTRY/1.0
countries_iso3_dict = {
    "Albania": "ALB",
    "Andorra": "AND",
    "Armenia": "ARM",
    "Austria": "AUT",
    "Azerbaijan": "AZE",
    "Belarus": "BLR",
    "Belgium": "BEL",
    "Bosnia and Herzegovina": "BIH",
    "Bulgaria": "BGR",
    "Croatia": "HRV",
    "Cyprus": "CYP",
    "Czech Republic": "CZE",
    "Denmark": "DNK",
    "Estonia": "EST",
    "Finland": "FIN",
    "France": "FRA",
    "Georgia": "GEO",
    "Germany": "DEU",
    "Greece": "GRC",
    "Holy See": "VAT",
    "Hungary": "HUN",
    "Iceland": "ISL",
    "Ireland": "IRL",
    "Italy": "ITA",
    "Kazakhstan": "KAZ",
    "Kosovo (UN SC resolution 1244)": "XKX",  # UNDP defines it as KOS
    "Kyrgyzstan": "KGZ",
    "Latvia": "LVA",
    "Liechtenstein": "LIE",
    "Lithuania": "LTU",
    "Luxembourg": "LUX",
    "Malta": "MLT",
    "Monaco": "MCO",
    "Montenegro": "MNE",
    "Netherlands": "NLD",
    "North Macedonia": "MKD",
    "Norway": "NOR",
    "Poland": "POL",
    "Portugal": "PRT",
    "Republic of Moldova": "MDA",
    "Romania": "ROU",
    "Russian Federation": "RUS",
    "San Marino": "SMR",
    "Serbia": "SRB",
    "Slovakia": "SVK",
    "Slovenia": "SVN",
    "Spain": "ESP",
    "Sweden": "SWE",
    "Switzerland": "CHE",
    "Tajikistan": "TJK",
    "Turkey": "TUR",
    "Turkmenistan": "TKM",
    "Ukraine": "UKR",
    "United Kingdom": "GBR",
    "Uzbekistan": "UZB",
}

# create a list of country names in the same order as the countries_iso3_dict
countries = list(countries_iso3_dict.keys())

unicef_country_prog = [
    "Albania",
    "Armenia",
    "Azerbaijan",
    "Belarus",
    "Bosnia and Herzegovina",
    "Bulgaria",
    "Croatia",
    "Georgia",
    "Greece",
    "Kazakhstan",
    "Kosovo (UN SC resolution 1244)",
    "Kyrgyzstan",
    "Montenegro",
    "North Macedonia",
    "Republic of Moldova",
    "Romania",
    "Serbia",
    "Tajikistan",
    "Turkey",
    "Turkmenistan",
    "Ukraine",
    "Uzbekistan",
]

country_selections = [
    {
        "label": "Eastern Europe and Central Asia",
        "value": [
            {"label": "Caucasus", "value": ["Armenia", "Azerbaijan", "Georgia"]},
            {
                "label": "Western Balkans",
                "value": [
                    "Albania",
                    "Bosnia and Herzegovina",
                    "Croatia",
                    "Kosovo (UN SC resolution 1244)",
                    "North Macedonia",
                    "Montenegro",
                    "Serbia",
                ],
            },
            {
                "label": "Central Asia",
                "value": [
                    "Kazakhstan",
                    "Kyrgyzstan",
                    "Tajikistan",
                    "Turkmenistan",
                    "Uzbekistan",
                ],
            },
            {
                "label": "Eastern Europe",
                "value": [
                    "Bulgaria",
                    "Belarus",
                    "Republic of Moldova",
                    "Romania",
                    "Russian Federation",
                    "Turkey",
                    "Ukraine",
                ],
            },
        ],
    },
    {
        "label": "Western Europe",
        "value": [
            "Andorra",
            "Austria",
            "Belgium",
            "Cyprus",
            "Czech Republic",
            "Denmark",
            "Estonia",
            "Finland",
            "France",
            "Germany",
            "Greece",
            "Holy See",
            "Hungary",
            "Iceland",
            "Ireland",
            "Italy",
            "Latvia",
            "Liechtenstein",
            "Lithuania",
            "Luxembourg",
            "Malta",
            "Monaco",
            "Netherlands",
            "Norway",
            "Poland",
            "Portugal",
            "San Marino",
            "Slovakia",
            "Slovenia",
            "Spain",
            "Sweden",
            "Switzerland",
            "United Kingdom",
        ],
    },
    {
        "label": "By EU Engagement",
        "value": [
            {
                "label": "Central Asia",
                "value": [
                    "Kazakhstan",
                    "Kyrgyzstan",
                    "Tajikistan",
                    "Turkmenistan",
                    "Uzbekistan",
                ],
            },
            {
                "label": "Eastern Partnership",
                "value": [
                    "Armenia",
                    "Azerbaijan",
                    "Belarus",
                    "Georgia",
                    "Republic of Moldova",
                    "Ukraine",
                ],
            },
            {
                "label": "EFTA",
                "value": ["Iceland", "Liechtenstein", "Norway", "Switzerland"],
            },
            {
                "label": "EU Member States",
                "value": [
                    "Andorra",
                    "Austria",
                    "Belgium",
                    "Bulgaria",
                    "Croatia",
                    "Cyprus",
                    "Czech Republic",
                    "Denmark",
                    "Estonia",
                    "Finland",
                    "France",
                    "Germany",
                    "Greece",
                    "Hungary",
                    "Ireland",
                    "Italy",
                    "Latvia",
                    "Lithuania",
                    "Luxembourg",
                    "Malta",
                    "Netherlands",
                    "Poland",
                    "Portugal",
                    "Romania",
                    "Slovakia",
                    "Slovenia",
                    "Spain",
                    "Sweden",
                ],
            },
            {
                "label": "Other",
                "value": [
                    "Andorra",
                    "Monaco",
                    "Holy See",
                    "San Marino",
                ],
            },
            {
                "label": "Pre-accession countries",
                "value": [
                    "Albania",
                    "Bosnia and Herzegovina",
                    "Kosovo (UN SC resolution 1244)",
                    "North Macedonia",
                    "Montenegro",
                    "Serbia",
                    "Turkey",
                ],
            },
            {
                "label": "Russian Federation",
                "value": ["Russian Federation"],
            },
            {
                "label": "United Kingdom (left EU on January 31, 2020)",
                "value": ["United Kingdom"],
            },
        ],
    },
]

data_sources = {
    "CDDEM": "CountDown 2030",
    "CCRI": "Children's Climate Risk Index",
    "UN Treaties": "UN Treaties",
    "ESTAT": "Euro Stat",
    "Helix": " Health Entrepreneurship and LIfestyle Xchange",
    "ILO": "International Labour Organization",
    "WHO": "World Health Organization",
    "Immunization Monitoring (WHO)": "Immunization Monitoring (WHO)",
    "WB": "World Bank",
    "OECD": "Organisation for Economic Co-operation and Development",
    "SDG": "Sustainable Development Goals",
    "UIS": "UNESCO Institute for Statistics",
    "UNDP": "United Nations Development Programme",
    "TMEE": "Transformative Monitoring for Enhanced Equity",
}

topics_subtopics = {
    "All": ["All"],
    "Education, Leisure, and Culture": [
        {"Participation": "Education access and participation"},
        {"Quality": "Learning quality and skills"},
        {"System": "Education system"},
    ],
    "Family Environment and Protection": [
        {"Violence": "Violence against Children and Women"},
        {"Care": "Children without parental care"},
        {"Justice": "Justice for Children"},
        {"Marriage": "Child marriage and other harmful practices"},
        {"Labour": "Child labour and other forms of exploitation"},
    ],
    "Health and Nutrition": [
        {"HS": "Health System"},
        {"MNCH": "Maternal, newborn and child health"},
        {"Immunization": "Immunization"},
        {"Nutrition": "Nutrition"},
        {"Adolescent": "Adolescent physical, mental, and reproductive health"},
        {"HIVAIDS": "HIV/AIDS"},
        {"Wash": "Water, sanitation and hygiene"},
    ],
    "Poverty and Social Protection": [
        {"Poverty": "Child Poverty and Material Deprivation"},
        {"Protection": "Social protection system"},
    ],
    "Child Rights Landscape and Governance": [
        {"Demography": "Demographics"},
        {"Economy": "Political Economy"},
        {"Migration": "Migration and Displacement"},
        {"Access": "Access to Justice"},
        {"Data": "Data on Children"},
        {"Spending": "Public spending on Children"},
    ],
    "Participation and Civil Rights": [
        {"Registration": "Birth registration and identity"},
        {"Information": "Information, Internet and Protection of privacy"},
        {"Leisure": "Leisure and Culture"},
    ],
}

dict_topics_subtopics = {
    "Education, Leisure, and Culture": [
        "Education access and participation",
        "Learning quality and skills",
        "Education System",
    ],
    "Family Environment and Protection": [
        "Violence against Children and Women",
        "Children without parental care",
        "Justice for Children",
        "Child marriage and other harmful practices",
        "Child labour and other forms of exploitation",
    ],
    "Health and Nutrition": [
        "Health System",
        "Maternal, newborn and child health",
        "Immunization",
        "Nutrition",
        "Adolescent physical, mental, and reproductive health",
        "HIV/AIDS",
        "Water, sanitation and hygiene",
    ],
    "Poverty and Social Protection": [
        "Child Poverty and Material Deprivation",
        "Social protection system",
    ],
    "Child Rights Landscape and Governance": [
        "Demographics",
        "Political Economy",
        "Migration and Displacement",
        "Access to Justice",
        "Data on Children",
        "Public spending on Children",
    ],
    "Participation and Civil Rights": [
        "Birth registration and identity",
        "Information, Internet and Protection of privacy",
        "Education, Leisure, and Culture",
    ],
}


def get_search_countries(add_all):
    all_countries = {"label": "All", "value": "All"}
    countries_list = [
        {
            "label": key,
            "value": countries_iso3_dict[key],
        }
        for key in countries_iso3_dict.keys()
    ]
    if add_all:
        countries_list.insert(0, all_countries)
    return countries_list


def get_sector(subtopic):
    for key in dict_topics_subtopics.keys():
        if subtopic.strip() in dict_topics_subtopics.get(key):
            return key
    return ""


# function to check if the config of a certain indicator are only about its dtype
def only_dtype(config):
    return list(config.keys()) == ["DTYPE"]


def get_filtered_dataset(
    indicators: list,
    years: list,
    country_codes: list,
    breakdown: str = "TOTAL",  # send default breakdown as Total
    dimensions: dict = {},
    latest_data: bool = True,
) -> pd.DataFrame:

    # TODO: This is temporary, need to move to config
    # Add all dimensions by default to the keys
    keys = {
        "REF_AREA": country_codes,
        "INDICATOR": indicators,
        "SEX": [],
        "AGE": [],
        "RESIDENCE": [],
        "WEALTH_QUINTILE": [],
    }

    # get the first indicator of the list... we have more than one indicator in the cards
    indicator_config = (
        indicators_config[indicators[0]] if indicators[0] in indicators_config else {}
    )
    # check if the indicator has special config, update the keys from the config
    if indicator_config and not only_dtype(indicator_config):
        # TODO: need to confirm that a TOTAL is always available when a config is available for the indicator
        card_keys = indicator_config[breakdown]
        if (
            dimensions
        ):  # if we are sending cards related filters, update the keys with the set values
            card_keys.update(dimensions)
        keys.update(card_keys)  # update the keys with the sent values

    try:
        data = unicef.data(
            "TRANSMONEE",
            provider="ECARO",
            key=keys,
            params=dict(
                startPeriod=years[0],
                endPeriod=years[-1],
                lastNObservations=1 if latest_data else 0,
            ),
            dsd=dsd,
        )
        logging.debug(f"URL: {data.response.url} CACHED: {data.response.from_cache}")
    except HTTPError as e:
        logging.exception(f"URL: {e.response}", e)
        # TODO: Maybe do something better here
        return pd.DataFrame()

    # lbassil: add sorting by Year to display the years in proper order on the x-axis
    dtype = (
        eval(indicator_config["DTYPE"]) if "DTYPE" in indicator_config else np.float64
    )
    data = (
        data.to_pandas(attributes="o", rtype="rows", dtype=dtype)
        .sort_values(by=["TIME_PERIOD"])
        .reset_index()
    )
    data.rename(columns={"value": "OBS_VALUE", "INDICATOR": "CODE"}, inplace=True)
    # replace Yes by 1 and No by 0
    data.OBS_VALUE.replace({"Yes": "1", "No": "0", "<": "", ">": ""}, inplace=True)

    # convert to numeric and round
    data["OBS_VALUE"] = pd.to_numeric(data.OBS_VALUE, errors="coerce")
    data.dropna(subset=["OBS_VALUE"], inplace=True)
    # round based on indicator unit: index takes 3 decimals
    ind_unit = data.UNIT_MEASURE.iloc[0].value
    data = data.round({"OBS_VALUE": 3 if ind_unit == "IDX" else 1})
    # round to whole number if values greater than one (and not index)
    if ind_unit != "IDX":
        data.loc[data.OBS_VALUE > 1, "OBS_VALUE"] = data[
            data.OBS_VALUE > 1
        ].OBS_VALUE.round()
    # converting TIME_PERIOD to numeric: we should get integers by default
    data["TIME_PERIOD"] = pd.to_numeric(data.TIME_PERIOD)

    # lbassil: add the code to fill the country names
    countries_val_list = list(countries_iso3_dict.values())

    def create_labels(row):
        row["Country_name"] = countries[countries_val_list.index(row["REF_AREA"])]
        row["Unit_name"] = str(units_names.get(str(row["UNIT_MEASURE"]), ""))
        row["Sex_name"] = str(gender_names.get(str(row["SEX"]), ""))
        row["Residence_name"] = str(residence_names.get(str(row["RESIDENCE"]), ""))
        row["Wealth_name"] = str(wealth_names.get(str(row["WEALTH_QUINTILE"]), ""))
        row["Age_name"] = str(age_groups_names.get(str(row["AGE"]), ""))
        return row

    data = data.apply(create_labels, axis="columns")

    return data


# create two dicts, one for display tree and one with the index of all possible selections
selection_index = collections.OrderedDict({"0": countries})
selection_tree = dict(title="Select All", key="0", children=[])
for num1, group in enumerate(country_selections):
    parent = dict(title=group["label"], key=f"0-{num1}", children=[])
    group_countries = []

    for num2, region in enumerate(group["value"]):
        child_region = dict(
            title=region["label"] if "label" in region else region,
            key=f"0-{num1}-{num2}",
            children=[],
        )
        parent.get("children").append(child_region)
        if "value" in region:
            selection_index[f"0-{num1}-{num2}"] = (
                region["value"]
                if isinstance(region["value"], list)
                else [region["value"]]
            )
            for num3, country in enumerate(region["value"]):
                child_country = dict(title=country, key=f"0-{num1}-{num2}-{num3}")
                if len(region["value"]) > 1:
                    # only create child nodes for more then one child
                    child_region.get("children").append(child_country)
                    selection_index[f"0-{num1}-{num2}-{num3}"] = [country]
                group_countries.append(country)
        else:
            selection_index[f"0-{num1}-{num2}"] = [region]
            group_countries.append(region)

    selection_index[f"0-{num1}"] = group_countries
    selection_tree.get("children").append(parent)

programme_country_indexes = [
    next(
        key
        for key, value in selection_index.items()
        if value[0] == item and len(value) == 1
    )
    for item in unicef_country_prog
]

data = pd.DataFrame()
data_query_inds = set(data_query_codes)

# column data types coerced
col_types = {
    "COVERAGE_TIME": str,
    "OBS_FOOTNOTE": str,
    "OBS_VALUE": str,
    "Frequency": str,
    "Unit multiplier": str,
    "OBS_STATUS": str,
    "Observation Status": str,
    "TIME_PERIOD": int,
}

# avoid a loop to query SDMX
try:
    data_query_sdmx = pd.read_csv(
        sdmx_url.format("+".join(data_query_inds), years[0], years[-1]),
        dtype=col_types,
        storage_options={"Accept-Encoding": "gzip"},
        low_memory=False,
    )
except urllib.error.HTTPError as e:
    raise e

data = data.append(data_query_sdmx)
# no need to create column CODE, just rename indicator
data.rename(columns={"INDICATOR": "CODE"}, inplace=True)

# replace Yes by 1 and No by 0
data.OBS_VALUE.replace({"Yes": "1", "No": "0"}, inplace=True)


# check and drop non-numeric observations, eg: SDMX accepts > 95 as an OBS_VALUE
filter_non_num = pd.to_numeric(data.OBS_VALUE, errors="coerce").isnull()
if filter_non_num.any():
    not_num_code_val = data[["CODE", "OBS_VALUE"]][filter_non_num]
    f"Non-numeric observations in {not_num_code_val.CODE.unique()}\ndiscarded: {not_num_code_val.OBS_VALUE.unique()}"
    data.drop(data[filter_non_num].index, inplace=True)

# convert to numeric
data["OBS_VALUE"] = pd.to_numeric(data.OBS_VALUE)
data = data.round({"OBS_VALUE": 2})
# print(data.shape)

# TODO: calculations for children age population
indicators = data["Indicator"].unique()

# extract the indicators that have gender/sex disaggregation
gender_indicators = data.groupby("CODE").agg({"SEX": "nunique"}).reset_index()
# Keep only indicators with gender/sex disaggregation
gender_indicators = gender_indicators[gender_indicators["SEX"] > 1]

# path to excel data dictionary in repo
github_url = "https://github.com/UNICEFECAR/data-etl/raw/proto_API/tmee/data_in/data_dictionary/indicator_dictionary_TM_v8.xlsx"
data_dict_content = requests.get(github_url).content
# Reading the downloaded content and turning it into a pandas dataframe and read Snapshot sheet from excel data-dictionary
snapshot_df = pd.read_excel(BytesIO(data_dict_content), sheet_name="Snapshot")
snapshot_df.dropna(subset=["Source_name"], inplace=True)
snapshot_df["Source"] = snapshot_df["Source_name"].apply(lambda x: x.split(":")[0])
# read indicators table from excel data-dictionary
df_topics_subtopics = pd.read_excel(BytesIO(data_dict_content), sheet_name="Indicator")
df_topics_subtopics.dropna(subset=["Issue"], inplace=True)
df_sources = pd.merge(df_topics_subtopics, snapshot_df, how="outer", on=["Code"])
# assign source = TMEE to all indicators without a source since they all come from excel data collection files
df_sources.fillna("TMEE", inplace=True)
# Concatenate sectors/subtopics dictionary value lists (mapping str lower)
sitan_subtopics = list(map(str.lower, sum(dict_topics_subtopics.values(), [])))

df_sources.rename(
    columns={
        "Name_x": "Indicator",
        "Issue": "Subdomain",
    },
    inplace=True,
)
# filter the sources to keep only sitan related sectors and sub-topics
df_sources["Subdomain"] = df_sources["Subdomain"].str.strip()
df_sources["Domain"] = df_sources["Subdomain"].apply(
    lambda x: get_sector(x) if not pd.isna(x) else ""
)
df_sources["Source_Full"] = df_sources["Source"].apply(
    lambda x: data_sources[x] if not pd.isna(x) else ""
)

df_sources = df_sources[df_sources["Subdomain"].str.lower().isin(sitan_subtopics)]
# read source table from excel data-dictionary and merge
source_table_df = pd.read_excel(BytesIO(data_dict_content), sheet_name="Source")
df_sources = df_sources.merge(
    source_table_df[["Source_Id", "Source_Link"]],
    on="Source_Id",
    how="left",
    sort=False,
)
# assign source link for TMEE, url: UNICEF_RDM/indicator_code
tmee_source_link = df_sources.Source_Link.isnull()
unicef_rdm_url = "https://data.unicef.org/indicator-profile/{helix_code}/"
df_sources.loc[tmee_source_link, "Source_Link"] = df_sources[
    tmee_source_link
].Code.apply(lambda x: unicef_rdm_url.format(helix_code=x))
df_sources_groups = df_sources.groupby("Source")
df_sources_summary_groups = df_sources.groupby("Source_Full")
# Extract the indicators' potential unique disaggregations.
# Group by indicator code and keep only unique aggregations for the 4 possible dimensions:
# Sex, Age, Residence and Wealth.
indicators_disagg = (
    data.groupby("CODE")
    .agg(
        {
            "AGE": "nunique",
            "SEX": "nunique",
            "RESIDENCE": "nunique",
            "WEALTH_QUINTILE": "nunique",
        }
    )
    .reset_index()
)
# Filter the dimensions with count greater than 1 which means Total is there (default) in addition to other possible values.
indicators_disagg_no_total = indicators_disagg[
    (indicators_disagg["AGE"] > 1)
    | (indicators_disagg["SEX"] > 1)
    | (indicators_disagg["RESIDENCE"] > 1)
    | (indicators_disagg["WEALTH_QUINTILE"] > 1)
]

# include the indicators with Total only to show in the data query
indicators_disagg_with_total = indicators_disagg[
    (indicators_disagg["AGE"] >= 1)
    | (indicators_disagg["SEX"] >= 1)
    | (indicators_disagg["RESIDENCE"] >= 1)
    | (indicators_disagg["WEALTH_QUINTILE"] >= 1)
]
# Get the data for all the indicators having disaggregated data by any of the 4 dimensions.
indicators_disagg_details = data[
    data["CODE"].isin(indicators_disagg_with_total["CODE"])
]

# Filter the dataframe to be used in the data query to keep indicators code and the possible disaggregations.
indicators_disagg_details = indicators_disagg_details[
    ["CODE", "Age", "Sex", "Residence", "Wealth Quintile"]
]
indicators_disagg_details = indicators_disagg_details.drop_duplicates()

# extract the indicators that have gender/sex disaggregation
age_indicators_counts = data.groupby("CODE").agg({"AGE": "nunique"}).reset_index()
# Keep only indicators with gender/sex disaggregation
age_indicators_counts = age_indicators_counts[age_indicators_counts["AGE"] > 1]
# age_indicators_counts.to_csv("age_indicators_counts.csv", index=True)
age_indicators = pd.merge(data, age_indicators_counts, on=["CODE"])
age_indicators = age_indicators[["CODE", "Indicator", "Age"]]
age_indicators = age_indicators.drop_duplicates()
age_indicators = age_indicators.sort_values(by=["CODE", "Age"])
# age_indicators.to_csv("age_indicators.csv", index=False)

# extract the indicators that have gender/sex disaggregation
age_indicators_counts = data.groupby("CODE").agg({"AGE": "nunique"}).reset_index()
# Keep only indicators with gender/sex disaggregation
age_indicators_counts = age_indicators_counts[age_indicators_counts["AGE"] > 1]
# age_indicators_counts.to_csv("age_indicators_counts.csv", index=True)
age_indicators = pd.merge(data, age_indicators_counts, on=["CODE"])
age_indicators = age_indicators[["CODE", "Indicator", "Age"]]
age_indicators = age_indicators.drop_duplicates()
age_indicators = age_indicators.sort_values(by=["CODE", "Age"])
# age_indicators.to_csv("age_indicators.csv", index=False)


def page_not_found(pathname):
    return html.P("No page '{}'".format(pathname))
