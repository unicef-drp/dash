import collections
import json
import logging
from io import BytesIO
from pathlib import Path
import pathlib
from flask import request
from urllib.parse import urlsplit, urlunsplit
import re

import numpy as np
import pandas as pd
import pandasdmx as sdmx
import plotly.express as px
import plotly.io as pio
import plotly
from shapely.geometry import shape
import dash
import requests
import plotly.graph_objects as go
import textwrap
import time


import dash_bootstrap_components as dbc
from dash import dcc, html, get_asset_url, callback_context, no_update


from dash_service.components import fa
from dash_service.utils import get_geo_file
from ..sdmx import data_access_sdmx

# set defaults
pio.templates.default = "plotly_white"
px.defaults.color_continuous_scale = px.colors.sequential.BuGn
px.defaults.color_discrete_sequence = px.colors.qualitative.Dark24

colours = [
    "primary",
    "success",
    "warning",
    "danger",
    "secondary",
    "info",
    "success",
    "danger",
]


DEFAULT_LABELS = {
    "Country_name": "Country",
    "TIME_PERIOD": "Year",
    "Sex_name": "Sex",
    "Residence_name": "Residence",
    "Age_name": "Age",
    "Wealth_name": "Wealth Quintile",
    "OBS_FOOTNOTE": "Footnote",
    "DATA_SOURCE": "Primary Source",
}

EMPTY_CHART = {
    "layout": {
        "xaxis": {"visible": False},
        "yaxis": {"visible": False},
        "annotations": [
            {
                "text": "No indicator chosen or no data is available for the selected filters.",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 20},
            }
        ],
    }
}


# TODO: Move all of these to env/setting vars from production

# parent = Path(__file__).resolve().parent
# with open(parent / "../static/indicator_config.json") as config_file:
#     indicators_config = json.load(config_file)

config_file_path = (
    f"{pathlib.Path(__file__).parent.parent.absolute()}/static/indicator_config.json"
)
with open(config_file_path) as config_file:
    indicators_config = json.load(config_file)


geo_json_countries = get_geo_file("ecaro.geo.json")

unicef = sdmx.Request("UNICEF", timeout=5)

metadata = unicef.dataflow("TRANSMONEE", provider="ECARO", version="1.0")
dsd = metadata.structure["DSD_ECARO_TRANSMONEE"]

indicator_names = {
    code.id: code.name.en
    for code in dsd.dimensions.get("INDICATOR").local_representation.enumerated
}

button_name_file_path = (
    f"{pathlib.Path(__file__).parent.parent.absolute()}/static/indicator_buttons.json"
)
with open(button_name_file_path) as button_file:
    indicator_buttons = json.load(button_file)

indicator_def_file_path = f"{pathlib.Path(__file__).parent.parent.absolute()}/static/indicator_definitions.json"
with open(indicator_def_file_path) as definitions_file:
    indicator_definitions = json.load(definitions_file)


# custom names as requested by siraj: update thousands for consistency, packed indicators
custom_names = {
    # erase_name_thousands
    "DM_BRTS": "Number of births",
    "DM_POP_TOT_AGE": "Population by age",
    "HT_SN_STA_OVWGTN": "2.2.2. Number of children moderately or severely overweight",
    "DM_CHLD_POP": "Child population aged 0-17 years",
    "DM_ADOL_POP": "Adolescent population aged 10-19 years",
    "DM_TOT_POP_PROSP": "Population prospects",
    "DM_ADOL_YOUTH_POP": "Adolescent, young and youth population aged 10-24 years",
    "DM_ADULT_YOUTH_POP": "Adult youth population aged 20-29 years",
    "DM_REPD_AGE_POP": "Population of reproductive age 15-49 years",
    "DM_CHLD_YOUNG_COMP_POP": "Child population aged 0-17 years",
    "ICT_SECURITY_CONCERN": "Percentage of 16-24 year olds who limited their personal internet activities in the last 12 months due to security concerns",
    "ICT_PERSONAL_DATA": "Percentage of 16-24 year olds who used the internet in the last 3 months and managed access to their personal data",
    "MT_SDG_SUICIDE": "3.4.2 Suicide mortality rate for 15-19 year olds (deaths per 100,000 population)",
    "EC_SP_GOV_EXP_GDP": "General government expenditure on social protection (% of GDP)",
    # custom plots
    "packed_CRG": "National Human Rights Institutions in compliance with the Paris Principles",
    "packed_EXP": "Expenditure on education levels as a percentage of government expenditure on education",
}
indicator_names.update(custom_names)
# lbassil: get the age groups code list as it is not in the DSD
cl_age = unicef.codelist("CL_AGE", version="1.0")
age_groups = sdmx.to_pandas(cl_age)
dict_age_groups = age_groups["codelist"]["CL_AGE"].reset_index()
age_groups_names = {age.iloc[0]: age.iloc[1] for _, age in dict_age_groups.iterrows()}

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

years = list(range(2000, 2024))

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
    "Kosovo (UNSCR 1244)": "XKX",  # UNDP defines it as KOS
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
    "Türkiye": "TUR",
    "Turkmenistan": "TKM",
    "Ukraine": "UKR",
    "United Kingdom": "GBR",
    "Uzbekistan": "UZB",
}

#
reversed_countries_iso3_dict = {
    "ALB": "Albania",
    "AND": "Andorra",
    "ARM": "Armenia",
    "AUT": "Austria",
    "AZE": "Azerbaijan",
    "BLR": "Belarus",
    "BEL": "Belgium",
    "BIH": "Bosnia and Herzegovina",
    "BGR": "Bulgaria",
    "HRV": "Croatia",
    "CYP": "Cyprus",
    "CZE": "Czech Republic",
    "DNK": "Denmark",
    "EST": "Estonia",
    "FIN": "Finland",
    "FRA": "France",
    "GEO": "Georgia",
    "DEU": "Germany",
    "GRC": "Greece",
    "VAT": "Holy See",
    "HUN": "Hungary",
    "ISL": "Iceland",
    "IRL": "Ireland",
    "ITA": "Italy",
    "KAZ": "Kazakhstan",
    "XKX": "Kosovo (UNSCR 1244)",
    "KGZ": "Kyrgyzstan",
    "LVA": "Latvia",
    "LIE": "Liechtenstein",
    "LTU": "Lithuania",
    "LUX": "Luxembourg",
    "MLT": "Malta",
    "MCO": "Monaco",
    "MNE": "Montenegro",
    "NLD": "Netherlands",
    "MKD": "North Macedonia",
    "NOR": "Norway",
    "POL": "Poland",
    "PRT": "Portugal",
    "MDA": "Republic of Moldova",
    "ROU": "Romania",
    "RUS": "Russian Federation",
    "SMR": "San Marino",
    "SRB": "Serbia",
    "SVK": "Slovakia",
    "SVN": "Slovenia",
    "ESP": "Spain",
    "SWE": "Sweden",
    "CHE": "Switzerland",
    "TJK": "Tajikistan",
    "TUR": "Türkiye",
    "TKM": "Turkmenistan",
    "UKR": "Ukraine",
    "GBR": "United Kingdom",
    "UZB": "Uzbekistan",
}

# create a list of country names in the same order as the countries_iso3_dict
countries = list(countries_iso3_dict.keys())

# create a list of country names in the same order as the countries_iso3_dict
country_codes = list(reversed_countries_iso3_dict.keys())


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
    "Kosovo (UNSCR 1244)",
    "Kyrgyzstan",
    "Montenegro",
    "North Macedonia",
    "Republic of Moldova",
    "Romania",
    "Serbia",
    "Tajikistan",
    "Türkiye",
    "Turkmenistan",
    "Ukraine",
    "Uzbekistan",
]

eu_countries = [
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
]

efta_countries = ["Iceland", "Liechtenstein", "Norway", "Switzerland"]


all_countries = [
    "Albania",
    "Andorra",
    "Armenia",
    "Austria",
    "Azerbaijan",
    "Belarus",
    "Belgium",
    "Bosnia and Herzegovina",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czech Republic",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Georgia",
    "Germany",
    "Greece",
    "Holy See",
    "Hungary",
    "Iceland",
    "Ireland",
    "Italy",
    "Kazakhstan",
    "Kosovo (UNSCR 1244)",
    "Kyrgyzstan",
    "Latvia",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Monaco",
    "Montenegro",
    "Netherlands",
    "North Macedonia",
    "Norway",
    "Poland",
    "Portugal",
    "Republic of Moldova",
    "Romania",
    "Russian Federation",
    "San Marino",
    "Serbia",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden",
    "Switzerland",
    "Tajikistan",
    "Türkiye",
    "Turkmenistan",
    "Ukraine",
    "United Kingdom",
    "Uzbekistan",
]


data_sources = {
    "CDDEM": "CountDown 2030",
    "CCRI": "Children's Climate Risk Index",
    "UN Treaties": "UN Treaties",
    "ESTAT": "Eurostat",
    "Helix": "UNICEF Data Warehouse",
    "ILO": "International Labour Organization",
    "WHO": "World Health Organization",
    "Immunization Monitoring (WHO)": "Immunization Monitoring (WHO)",
    "WB": "World Bank",
    "OECD": "Organisation for Economic Co-operation and Development",
    "OECD CWD": "OECD Child Wellbeing Dashboard",
    "INFORM": "Inform Risk Index",
    "SDG": "Sustainable Development Goals",
    "UIS": "UNESCO Institute for Statistics",
    "NEW_UIS": "UNESCO Institute for Statistics",
    "UNDP": "United Nations Development Programme",
    "TMEE": "Transformative Monitoring for Enhanced Equity (TransMonEE)",
}

dict_topics_subtopics = {
    "Child Rights Landscape and Governance": [
        "Demographics",
        "Political economy",
        "Migration and displacement",
        "Access to Justice",
        "Data on children",
        "Public spending on children",
        "Child rights governance",
    ],
    "Health and Nutrition": [
        "Health system",
        "Maternal, newborn and child health",
        "Immunization",
        "Nutrition",
        "Adolescent physical, mental, and reproductive health",
        "HIV/AIDS",
        "Water, sanitation and hygiene",
    ],
    "Education, Leisure and Culture": [
        "Education access and participation",
        "Learning quality and skills",
        "Education system",
    ],
    "Family Environment and Protection": [
        "Violence against children and women",
        "Children without parental care",
        "Justice for children",
        "Child marriage and other harmful practices",
        "Child labour and other forms of exploitation",
    ],
    "Participation and Civil Rights": [
        "Birth registration and identity",
        "Information, internet and protection of privacy",
        "Leisure and culture",
    ],
    "Poverty and Adequate Standard of Living": [
        "Child poverty and material deprivation",
        "Social protection system",
    ],
    "Cross-Cutting": [
        "Gender",
        "Disability",
        "Early childhood development",
        "Adolescents",
        "Environment and climate change",
        "Disaster, conflict and displacement",
    ],
}

domain_pages = {
    "Child Rights Landscape and Governance": "child-rights",
    "Health and Nutrition": "child-health",
    "Education, Leisure and Culture": "child-education",
    "Family Environment and Protection": "child-protection",
    "Participation and Civil Rights": "child-participation",
    "Poverty and Adequate Standard of Living": "child-poverty",
    "Cross-Cutting": "child-cross-cutting",
}

domain_classes = {
    "Child Rights Landscape and Governance": "crg-dropdown",
    "Health and Nutrition": "han-dropdown",
    "Education, Leisure and Culture": "edu-dropdown",
    "Family Environment and Protection": "chp-dropdown",
    "Participation and Civil Rights": "par-dropdown",
    "Poverty and Adequate Standard of Living": "pov-dropdown",
    "Cross-Cutting": "cci-dropdown",
}

# Read the CRC Excel file and skip the first row (header is in the second row)
crc_file_path = f"{pathlib.Path(__file__).parent.parent.absolute()}/static/Full CRC database - v21-9-23.xlsx"
CRC_df = pd.read_excel(
    crc_file_path,
    sheet_name="Full CRC database ECA",
    header=1,  # Use the second row as column headers
)

# Renaming columns for easier access
CRC_df = CRC_df.rename(
    columns={
        "Name of the country": "Country",
        "Year of report ": "Year",
        "ECA child rights monitoring framework\nSub-Domain": "Sub-Domain",
        "Recommendation": "Recommendation",
        "Bottleneck type": "Bottleneck Type",
    }
)

# List of cross-cutting subdomain columns
crosscutting_columns = [
    "Gender",
    "Adolescents",
    "Disability",
    "Early childhood development",
    "Disaster, conflict and displacement",
    "Environment and climate",
]

# Read the master list Excel file and set the first row as header
master_file_path = (
    f"{pathlib.Path(__file__).parent.parent.absolute()}/static/master_list.xlsx"
)
master_df = pd.read_excel(
    master_file_path,
    sheet_name="Master List",
    header=0,  # Use the second row as column headers
)

framework_file_path = f"{pathlib.Path(__file__).parent.parent.absolute()}/static/crm_framework_indicators.json"
# Load the crm framework data
with open(framework_file_path, "r") as infile:
    data_dict = json.load(infile)


def get_card_popover_body(sources):
    """
    This function is used to generate the list of countries that are part of the card's
    displayed result; it displays the countries as a list, each on a separate line

    Args:
        sources (_type_): _description_

    Returns:
        _type_: _description_
    """
    country_list = []
    # lbassil: added this condition to stop the exception when sources is empty
    if len(sources) > 0:
        numeric = sources.OBS_VALUE.dtype.kind in "iufc"
        # sort by values if numeric else by country
        sort_col = "OBS_VALUE" if numeric else "Country_name"
        for index, source_info in sources.sort_values(by=sort_col).iterrows():
            country_list.append(f"- {index[0]}: {source_info[0]} ({index[1]})")
        card_countries = "\n".join(country_list)
        return card_countries
    else:
        return "NA"


def get_search_countries(add_all):
    """
    Get a list of countries for search, optionally including an "All" option.

    Args:
        add_all (bool): If True, include an "All" option in the list.

    Returns:
        list: A list of dictionaries, where each dictionary represents a country
              with 'label' as the country name and 'value' as the ISO3 code.

    """
    all_countries = {"label": "All", "value": "All"}  # Dictionary for "All" option
    countries_list = [
        {
            "label": key,
            "value": countries_iso3_dict[key],
        }
        for key in countries_iso3_dict.keys()
    ]  # List comprehension to create a list of country dictionaries

    if add_all:
        countries_list.insert(
            0, all_countries
        )  # Insert "All" option at the beginning of the list

    return countries_list


def update_country_dropdown(country_group):
    """
    Update the country dropdown options based on the selected country group.

    Args:
        country_group (str): The selected country group ("unicef", "eu", "efta", or any other value).

    Returns:
        tuple: A tuple containing two elements:
               - A list of dictionaries representing the country dropdown options,
                 where each dictionary has 'label' as the country name and 'value' as the country name.
               - The default value to be selected in the dropdown.

    """
    if country_group == "unicef":
        options = [
            {"label": country, "value": country} for country in unicef_country_prog
        ]
    elif country_group == "eu":
        options = [{"label": country, "value": country} for country in eu_countries]
    elif country_group == "efta":
        options = [{"label": country, "value": country} for country in efta_countries]
    elif country_group == "eu + efta":
        options = [
            {"label": country, "value": country}
            for country in eu_countries + efta_countries
        ]
    else:
        options = [{"label": country, "value": country} for country in all_countries]

    options_with_all = [
        {
            "label": "Select all",
            "value": "all_values",
        }
    ] + options

    return options_with_all, "all_values"


def update_country_selection(country_group, country_selection):
    """
    Update the country selection based on the selected country group and the current country selection.

    Args:
        country_group (str): The selected country group ("unicef", "eu", "efta", or any other value).
        country_selection (list): The current selected country values in the dropdown.

    Returns:
        tuple: A tuple containing two elements:
               - If the callback was not triggered by a dropdown item selection, return the updated
                 country dropdown options and the default selected value.
               - If the callback was triggered by a dropdown item selection, return no updates to the
                 dropdown options and the country selection value.

    """
    # Assign callback context to identify which input was triggered
    ctx = callback_context
    # Get input id
    # As well as the explicitly defined input there is an initial call when the app first loads with an empty trigger id
    inputId = ctx.triggered[0]["prop_id"].split(".")[0]

    # Check if the callback was not triggered by dropdown item selection
    if "country-filter" not in inputId:
        return update_country_dropdown(
            country_group
        )  # Update the country dropdown options

    # Callback triggered by dropdown item selection
    else:
        # Check if "all_values" has been added and other items are still in the selection
        if country_selection[-1] == "all_values" and len(country_selection) > 1:
            # No update to dropdown options, return only "all_values" in the selection
            return no_update, ["all_values"]
        # Check if an additional item has been added and "all_values" is still in the selection
        elif country_selection[0] == "all_values" and len(country_selection) > 1:
            # No update to dropdown options, return only the newly selected item in the selection
            return no_update, [country_selection[1]]
        else:
            # No update to dropdown options or value
            return no_update, no_update


def get_sector(subtopic):
    """
    Get the sector based on the given subtopic.
    Args:
        subtopic (str): The subtopic to match and find the corresponding sector.
    Returns:
        str: The sector that corresponds to the given subtopic. If no sector is found, an empty string is returned.
    """
    for key in dict_topics_subtopics.keys():
        if subtopic.strip() in dict_topics_subtopics.get(key):
            return key
    return ""


# function to check if the config of a certain indicator are only about its dtype and if its nominal data
def only_dtype(config):
    return list(config.keys()) == ["DTYPE", "NOMINAL"]


# function to check if a certain indicator is nominal data
def nominal_data(config):
    return only_dtype(config) and config["NOMINAL"]


def update_indicator_dropdown(indicator_filter):
    print(f"Update domain and indicator - Selected_subdomain: {indicator_filter}")

    # Function to get indicators for a specific subdomain
    def get_indicators_for_subdomain(subdomain_name):
        return data_dict["subdomains"][subdomain_name]["indicators"]

    # Function to get all indicators for a specific domain
    def get_indicators_for_domain(domain):
        indicators = []
        if domain in data_dict["domains"]:
            subdomains = data_dict["domains"][domain]
            for subdomain in subdomains:
                indicators.extend(get_indicators_for_subdomain(subdomain))
        return indicators

    # Initialize indicator options and value
    indicator_options = []

    if indicator_filter is not None and indicator_filter != "all":
        # Check if indicator_filter is a domain
        if indicator_filter in data_dict["domains"]:
            indicators = get_indicators_for_domain(indicator_filter)
        # Check if indicator_filter is a subdomain code
        elif any(indicator_filter == data_dict["subdomains"][sub]["code"] for sub in data_dict["subdomains"]):
            subdomain_name = next(sub for sub, details in data_dict["subdomains"].items() if details["code"] == indicator_filter)
            indicators = get_indicators_for_subdomain(subdomain_name)
        else:
            indicators = []

        indicator_options = [{"label": indicator["Indicator Name"], "value": indicator["Code"]} for indicator in indicators]

    else:
        # Show all indicators if no subdomain or domain is selected
        for subdomain in data_dict["subdomains"].values():
            indicator_options.extend([
                {"label": indicator["Indicator Name"], "value": indicator["Code"]}
                for indicator in subdomain["indicators"]
            ])

    # Sort the indicator options alphabetically by label
    indicator_options = sorted(indicator_options, key=lambda x: x['label'])

    # Return the sorted indicator options and the first value as default
    return indicator_options, indicator_options[0]["value"] if indicator_options else None

def update_domain_and_subdomain_values(selected_indicator_code):
    """
    Finds and returns the domain name, subdomain name, and subdomain code corresponding to a given indicator code.

    Args:
    selected_indicator_code (str): The indicator code to search for.

    Returns:
    tuple: The matching domain name, subdomain name, and subdomain code, or (None, None, None) if no match is found.
    """
    for domain, subdomains in data_dict['domains'].items():
        for subdomain in subdomains:
            indicators = data_dict['subdomains'][subdomain]['indicators']
            if any(indicator['Code'] == selected_indicator_code for indicator in indicators):
                subdomain_code = data_dict['subdomains'][subdomain]['code']
                return domain, subdomain, subdomain_code  # Return domain, subdomain, and subdomain code

    return None, None, None  # Return None for all if no match is found


def get_subdomain_name_by_code(subdomain_code):
    # Iterate over all subdomain items in the data_dict['subdomains'] dictionary
    for subdomain_name, subdomain_info in data_dict["subdomains"].items():
        # Check if the code matches the one we're looking for
        if subdomain_info["code"] == subdomain_code:
            # Return the name of the subdomain if the code matches
            return subdomain_name
    # Return None or an appropriate value if no match is found
    return None


def create_CRM_dropdown(data_dict):
    dropdown_data = [{"label": "Select All", "value": "all"}]  

    for domain, subdomains in data_dict['domains'].items():
        # Add the domain as a main entry
        dropdown_data.append({"label": html.Span([f"{domain} Domain"], style={'color': '#00acef', 'font-size': 16}),
                              "value": domain})
        for subdomain in subdomains:
            subdomain_code = data_dict['subdomains'][subdomain]['code']
            # Add each subdomain under its domain
            dropdown_data.append({"label": f" {subdomain}", "value": subdomain_code})
    return dropdown_data

# Example usage
dropdown_options = create_CRM_dropdown(data_dict)

def get_data(
    indicators: list,
    years: list,
    selected_countries: list,
    breakdown: str = "TOTAL",  # send default breakdown as Total
    dimensions: dict = {},
    latest_data: bool = True,
):
    """
    Get data based on the given parameters.

    Args:
        indicators (list): A list of indicators.
        years (list): A list of years.
        selected_countries (list): A list of selected countries.
        breakdown (str, optional): The breakdown parameter. Defaults to "TOTAL".
        dimensions (dict, optional): Additional dimensions for the data query. Defaults to an empty dictionary.
        latest_data (bool, optional): Flag to determine whether to retrieve the latest data. Defaults to True.

    Returns:
        pandas.DataFrame: The retrieved data.

    """
    data_endpoint_id = "ECARO"
    data_endpoint_url = "https://sdmx.data.unicef.org/ws/public/sdmxapi/rest/"
    api_access = data_access_sdmx.DataAccess_SDMX(data_endpoint_id, data_endpoint_url)

    keys = {
        "REF_AREA": selected_countries,
        "INDICATOR": indicators,
        "SEX": [],
        "AGE": [],
        "RESIDENCE": [],
        "WEALTH_QUINTILE": [],
        **dimensions,
    }

    indicator_config = indicators_config.get(indicators[0], {})

    if indicator_config and not only_dtype(indicator_config):
        card_keys = indicator_config.get(breakdown, {})
        card_keys.update(dimensions)
        keys.update(card_keys)

    # Build data query string
    data_query = "".join(
        ["+".join(keys[param]) + "." if keys[param] else "." for param in keys]
    )

    start_period = years[0] if years else 2000
    end_period = years[-1] if years else 2023

    # Get data using the API access
    data = api_access.get_data(
        agency="ECARO",
        id="TRANSMONEE",
        ver="1.0",
        dq=data_query,
        lastnobs=latest_data,
        startperiod=start_period,
        endperiod=end_period,
        labels="id",
        print_stats=True,
    )

    # Convert data types and perform data transformations
    dtype = (
        eval(indicator_config.get("DTYPE"))
        if indicator_config and "DTYPE" in indicator_config
        else np.float64
    )
    data = data.astype({"OBS_VALUE": dtype, "TIME_PERIOD": "int32"})
    data = data.sort_values(by=["TIME_PERIOD"]).reset_index(drop=True)

    data = data.rename(columns={"INDICATOR": "CODE"})

    footnote_mask = data.OBS_VALUE.astype(str).str.contains("[<>]")
    data.loc[footnote_mask, "OBS_FOOTNOTE"] += (
        "<br>Note: The estimated value is "
        + data.loc[footnote_mask, "OBS_VALUE"].astype(str)
        + "<br>"
    )

    data.OBS_VALUE.replace(
        {"(?i)Yes": "1", "(?i)No": "0", "<": "", ">": ""}, inplace=True, regex=True
    )

    data["OBS_VALUE"] = pd.to_numeric(data.OBS_VALUE, errors="coerce")
    data.dropna(subset=["OBS_VALUE"], inplace=True)

    if "3" in data.UNIT_MULTIPLIER.values and "DM_CHLD_POP" not in data["CODE"].values:
        data["OBS_VALUE"] *= 10 ** pd.to_numeric(data.UNIT_MULTIPLIER, errors="coerce")

    data.replace(np.nan, "N/A", inplace=True)

    data["OBS_FOOTNOTE"] = data.OBS_FOOTNOTE.str.wrap(70).str.replace("\n", "<br>")
    data["DATA_SOURCE"] = data.DATA_SOURCE.str.wrap(70).str.replace("\n", "<br>")

    if "IDX" in data.UNIT_MEASURE.values or "HVA_EPI_INF_RT_0-14" in data.CODE.values:
        data.OBS_VALUE = data.OBS_VALUE.round(3)
    elif "DM_FRATE_TOT" in data.CODE.values:
        data.OBS_VALUE = data.OBS_VALUE.round(1)
    else:
        data.OBS_VALUE = data.OBS_VALUE.round(1)
        data.loc[data.OBS_VALUE > 1, "OBS_VALUE"] = data[
            data.OBS_VALUE > 1
        ].OBS_VALUE.round()

    if "YES_NO" in data.UNIT_MEASURE.values:
        data["Status"] = data["OBS_VALUE"].map({1: "Yes", 0: "No"})

    data["Country_name"] = data["REF_AREA"].map(reversed_countries_iso3_dict)

    def create_labels(row):
        row["Unit_name"] = str(units_names.get(str(row["UNIT_MEASURE"]), ""))
        row["Sex_name"] = str(gender_names.get(str(row["SEX"]), ""))
        row["Residence_name"] = str(residence_names.get(str(row["RESIDENCE"]), ""))
        row["Wealth_name"] = str(wealth_names.get(str(row["WEALTH_QUINTILE"]), ""))
        row["Age_name"] = str(age_groups_names.get(str(row["AGE"]), ""))
        return row

    data = data.apply(create_labels, axis="columns")

    return data


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
    lambda x: data_sources[x] if not pd.isna(x) and x in data_sources else ""
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


### All code above this line should be refactored to use common SDMX access libs and config at some point


def get_base_layout(**kwargs):
    indicators_conf = kwargs.get("indicators")
    page_prefix = kwargs.get("page_prefix")
    domain_colour = kwargs.get("domain_colour")
    qparams = kwargs.get("query_params")

    home_icon_file_path = f"{request.root_url}assets/home-icon-2.svg"
    unicef_icon_file_path = f"{request.root_url}assets/unicef_icon.png"

    pass_through_params = ["prj=tm"]
    for k, v in qparams.items():
        if k not in ["prj", "page", "hash"]:
            pass_through_params.append(f"{k}={v}")

    home_icon_href = "?" + "&".join(pass_through_params) + "e&page=home"

    domain_pages_links = []
    for k, v in domain_pages.items():
        domain_pages_params = pass_through_params + ["page=" + v]
        domain_pages_params = "?" + "&".join(domain_pages_params)
        domain_pages_links.append({"label": k, "value": domain_pages_params})
        if "page" in qparams and v == qparams["page"]:
            current_page_ddl_value = domain_pages_params

    return html.Div(
        [
            dcc.Store(id=f"{page_prefix}-indicators", data=indicators_conf),
            dcc.Location(id=f"{page_prefix}-theme"),
            dbc.Row(
                children=[
                    dbc.Col(
                        html.Img(id="unicef-icon", src=unicef_icon_file_path),
                        lg=2, md=4, sm=6, xs=12,
                        align="center",
                    ),
                    dbc.Col(
                        html.Div([
                            html.H2("TransMonEE Dashboard", style={'color': 'white', 'marginTop': '0.75em', 'fontWeight': 'bold'}),
                            html.H5("Monitoring child rights data in Europe and Central Asia", style={'color': 'white', 'marginTop': '0.5em'})
                        ]),
                        lg=7, md=8, sm=12,
                    ),
                    dbc.Col(
                        html.Div([
                            dbc.Button("Explore using ECA CRM Framework", className="nav-btn mb-2"),
                            dbc.Button("Search by indicator", className="nav-btn mb-2"),
                            dbc.Button("View country profiles", className="nav-btn")
                        ], style={"display": "flex", "flexDirection": "column", "alignItems": "center"}),
                        lg=3, md=12, align="center",
                    ),
                ],
                justify="between",
                align="center",
                style={"background-color": '#00acef', "paddingBottom": 15, "minHeight": 200},
            ),
            html.Br(),
            dbc.Row(
                children=[
                    dbc.Row(
                        [
                            # Column for Step 1
                            dbc.Col(
                                [
                                    html.P("Filter list of indicators (optional)", style={"margin-bottom": "10px"}),
                                    dcc.Dropdown(
                                        id=f"{page_prefix}-crm-dropdown",
                                        options=dropdown_options,
                                        value="all",  # Default value
                                        placeholder="Select a domain or subdomain"
                                    ),
                                ],
                                # Define width for different screen sizes
                                width=12,  # Full width on extra small screens
                                sm=12,  # Full width on small screens
                                md=4,  # 4 columns wide on medium and larger screens
                            ),

                            # Column for Step 2
                            dbc.Col(
                                [
                                    html.P("Select indicator", style={"margin-top": "0.75em","margin-bottom": "10px"}),
                                    dcc.Dropdown(
                                        id=f"{page_prefix}-indicator-dropdown",
                                        options=[
                                            {
                                                "label": indicator["Indicator Name"],
                                                "value": indicator["Code"],
                                            }
                                            for sublist in [sd["indicators"] for sd in data_dict["subdomains"].values()]
                                            for indicator in sublist
                                        ],
                                        value=None,  # No default value, showing all options
                                        placeholder="Select an indicator",
                                        optionHeight=55,
                                        clearable=True,
                                        className="crm_dropdown",
                                    ),
                                ],
                                # Define width for different screen sizes
                                width=12,  # Full width on extra small screens
                                sm=12,  # Full width on small screens
                                md=8,  # 8 columns wide on medium and larger screens
                            ),
                        ],
                        style={"margin-bottom": "15px"}
                    ),
                    html.Br(),
                    dbc.Row(
                        [
                            dbc.Col(width=1),
                            dbc.Col(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                html.Div([
                                                    html.P("Years:", style={"margin-bottom": "10px", "margin-top": "5px"}),
                                                    dbc.DropdownMenu(
                                                        label=f"{years[0]} - {years[-1]}",
                                                        id=f"{page_prefix}-collapse-years-button",
                                                        className="m-2",
                                                        color="secondary",
                                                        children=[
                                                            dbc.Card(
                                                                dcc.RangeSlider(
                                                                    id=f"{page_prefix}-year_slider",
                                                                    min=0,
                                                                    max=len(years) - 1,
                                                                    step=1,
                                                                    marks={index: str(year) for index, year in enumerate(years) if index % 2 == 0},
                                                                    value=[0, len(years) - 1],
                                                                ),
                                                                style={"maxHeight": "250px", "minWidth": "500px"},
                                                                className="overflow-auto",
                                                                body=True,
                                                            ),
                                                        ],
                                                    ),
                                                ]),
                                                width="auto",
                                                align="start"  # Aligns content at the top
                                            ),
                                            dbc.Col(
                                                html.Div([
                                                    html.P("Country groupings:", style={"margin-bottom": "10px", "margin-top": "5px"}),
                                                    dcc.Dropdown(
                                                        id=f"{page_prefix}-country-group",
                                                        options=[
                                                            {"label": "All countries", "value": "all"},
                                                            {"label": "UNICEF programme countries", "value": "unicef"},
                                                            {"label": "EU countries", "value": "eu"},
                                                            {"label": "EFTA countries", "value": "efta"},
                                                            {"label": "EU + EFTA countries", "value": "eu + efta"},
                                                        ],
                                                        value="all",
                                                        placeholder="Select country group",
                                                        style={"width": "250px"},
                                                    ),
                                                ]),
                                                width="auto",
                                                align="start"  # Aligns content at the top
                                            ),
                                            dbc.Col(
                                                html.Div([
                                                    html.P("Countries:", style={"margin-bottom": "10px", "margin-top": "5px"}),
                                                    dcc.Dropdown(
                                                        id=f"{page_prefix}-country-filter",
                                                        options=[{"label": "Select all", "value": "all_values"}] + [{"label": country, "value": country} for country in all_countries],
                                                        value=["all_values"],
                                                        placeholder="Select country",
                                                        multi=True,
                                                        clearable=False,
                                                        style={"width": "300px"},
                                                    ),
                                                ]),
                                                width="auto",
                                                align="start"  # Aligns content at the top
                                            ),
                                            dbc.Col(
                                                html.Div([
                                                    html.P("Chart type:", style={"margin-bottom": "10px", "margin-top": "5px"}),
                                                    dbc.RadioItems(
                                                        id={
                                                            "type": "area_types",
                                                            "index": f"{page_prefix}-AIO_AREA",
                                                        },
                                                        className="custom-control-input-crg force-inline-control align-middle",
                                                        inline=True,
                                                    ),
                                                ]),                                                
                                                width="auto",
                                                align="start"  # Aligns content at the top
                                            ),
                                        ],
                                        justify="start"
                                    ),
                                ],
                                lg=10, md=10, sm=12, xs=12
                            ),
                            dbc.Col(width=1),
                        ],
                        style={"border": "1px solid #ddd", "margin": "auto", "padding": "15px 0px"},
                        align="center",
                        className="bg-light",
                        justify="center"
                    ),
                ],
                style={"padding": "0px 15px"},
            ),
            html.Br(),
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    dbc.Container(
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.Div(
                                                            [
                                                                dbc.Button(
                                                                    [
                                                                        html.I(className="fas fa-plus mr-2"),  # Icon with a right margin
                                                                        " Indicator Definition"
                                                                    ],
                                                                    id=f"{page_prefix}-collapse-button",
                                                                    className="def-btn mb-2",
                                                                    #color="primary", 
                                                                    n_clicks=0,
                                                                ),
                                                                dbc.Collapse(
                                                                    html.Div(
                                                                        id=f"{page_prefix}-definition-text",
                                                                        style={
                                                                            "color": domain_colour,
                                                                            "border": "1px solid #ccc",
                                                                            "padding": "5px",
                                                                            "marginBottom": "10px",
                                                                            "height": "120px",
                                                                            "overflowY": "auto",
                                                                            "whiteSpace": "pre-wrap",
                                                                            "textAlign": "left",
                                                                            "border-radius": "10px",
                                                                        },
                                                                    ),
                                                                    id=f"{page_prefix}-collapse",
                                                                ),
                                                            ],
                                                            style={
                                                                "display": "block",
                                                            },
                                                        ),
                                                        html.Br(),
                                                        html.P(
                                                            id=f"{page_prefix}-domain-text",
                                                            style={
                                                                "color": domain_colour,
                                                                "display": "inline-block",
                                                                "textAlign": "center",
                                                                "position": "relative",
                                                            },
                                                        ),
                                                        html.P(
                                                            id=f"{page_prefix}-subdomain-text",
                                                            style={
                                                                "color": domain_colour,
                                                                "display": "inline-block",
                                                                "textAlign": "center",
                                                                "position": "relative",
                                                            },
                                                        ),
                                                        dbc.Card(
                                                           id=f"{page_prefix}-indicator_card",
                                                           color="primary",
                                                           outline=True,
                                                            style={
                                                            "width": "95%",
                                                         },
                                                         ),
                                                    ],
                                                     # Define width for different screen sizes
                                                    width=12,  # Full width on extra small screens
                                                    sm=12,  # Full width on small screens
                                                    md=3,  # 4 columns wide on medium and larger screens
                                                ),
                                                dbc.Col(
                                                    html.Div(
                                                        [
                                                            html.Div(
                                                                [
                                                                    dbc.Row(
                                                                        [
                                                                            dbc.Col(
                                                                                dbc.RadioItems(
                                                                                    id={
                                                                                        "type": "area_breakdowns",
                                                                                        "index": f"{page_prefix}-AIO_AREA",
                                                                                    },
                                                                                    value = "TOTAL",
                                                                                    inputStyle={
                                                                                        "color": domain_colour
                                                                                    },
                                                                                    class_name="force-inline-control",
                                                                                    inline=True,
                                                                                ),
                                                                                width="auto",
                                                                            ),
                                                                            dbc.Col(
                                                                                [
                                                                                    html.Button(
                                                                                        [
                                                                                            html.I(className="fas fa-download", style={'color':'#00acef'}),  # Font Awesome download icon
                                                                                            " Download data"  
                                                                                        ],
                                                                                        id=f"{page_prefix}-download_btn",
                                                                                        className="download_btn custom-download-button",  # Add custom class
                                                                                    ),
                                                                                    dcc.Download(id=f"{page_prefix}-download-csv-info"),
                                                                                    dbc.Tooltip(
                                                                                        "Click to download the data displayed in graph as a CSV file.",
                                                                                        target=f"{page_prefix}-download_btn",
                                                                                        placement="bottom",
                                                                                    ),
                                                                                ],
                                                                                class_name="force-inline-control",
                                                                                width="auto",
                                                                            )
                                                                        ],
                                                                    )
                                                                ],
                                                                style={
                                                                    "paddingBottom": 10,
                                                                    "display": "flex",
                                                                    "justifyContent": "flex-end",
                                                                },
                                                            ),
                                                            dcc.Loading(
                                                                children=[
                                                                    html.Div(
                                                                        dcc.Graph(
                                                                            id={
                                                                                "type": "area",
                                                                                "index": f"{page_prefix}-AIO_AREA",
                                                                            },
                                                                            config={
                                                                                "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale"],
                                                                                "displaylogo": False,
                                                                                "autosizable": False,
                                                                                "showTips": True,
                                                                            },
                                                                            responsive=True,
                                                                        ),
                                                                        style={
                                                                            'overflowX': 'scroll',  # Enable horizontal scrolling
                                                                            'minWidth': '700px'         # Set the width of the div
                                                                        }
                                                                    )
                                                                ]
                                                            ),
                                                            dcc.Markdown(
                                                                id=f"{page_prefix}-aio_area_graph_info",
                                                            ),
                                                            html.Div(
                                                                dbc.Alert(
                                                                    color="secondary",
                                                                ),
                                                                id=f"{page_prefix}-aio_area_data_info_rep",
                                                                className="float-start",
                                                                style={
                                                                    "padding-right": "15px"
                                                                },
                                                            ),
                                                            dbc.Popover(
                                                                [
                                                                    dbc.PopoverHeader(
                                                                        html.P(
                                                                            "Countries with data for selected years"
                                                                        )
                                                                    ),
                                                                    dbc.PopoverBody(
                                                                        id=f"{page_prefix}-data-hover-body",
                                                                        style={
                                                                            "height": "200px",
                                                                            "overflowY": "auto",
                                                                            "whiteSpace": "pre-wrap",
                                                                        },
                                                                    ),
                                                                ],
                                                                id=f"{page_prefix}-data-hover",
                                                                target=f"{page_prefix}-aio_area_data_info_rep",
                                                                placement="top-start",
                                                                trigger="hover",
                                                                style={"opacity": 1},
                                                            ),
                                                            html.Div(
                                                                dbc.Alert(
                                                                    color="secondary",
                                                                ),
                                                                id=f"{page_prefix}-aio_area_data_info_nonrep",
                                                                className="float-start",
                                                            ),
                                                            dbc.Popover(
                                                                [
                                                                    dbc.PopoverHeader(
                                                                        html.P(
                                                                            "Countries without data for selected years"
                                                                        )
                                                                    ),
                                                                    dbc.PopoverBody(
                                                                        id=f"{page_prefix}-no-data-hover-body",
                                                                        style={
                                                                            "height": "200px",
                                                                            "overflowY": "auto",
                                                                            "whiteSpace": "pre-wrap",
                                                                        },
                                                                    ),
                                                                ],
                                                                id=f"{page_prefix}-no-data-hover",
                                                                target=f"{page_prefix}-aio_area_data_info_nonrep",
                                                                placement="top-start",
                                                                trigger="hover",
                                                                style={"opacity": 1},
                                                            ),
                                                            html.Div(
                                                                dbc.Alert(
                                                                    color="secondary",
                                                                ),
                                                                id=f"{page_prefix}-aio_area_area_info",
                                                                className="float-end",
                                                            ),
                                                        ],
                                                    ),
                                                    # Define width for different screen sizes
                                                    width=12,  # Full width on extra small screens
                                                    sm=12,  # Full width on small screens
                                                    md=9,  # 9 columns wide on medium and larger screens
                                                ),
                                            ],
                                            justify="evenly",
                                            align="start",
                                        ),
                                        fluid=True,
                                    ),
                                ]
                            ),
                        ],
                        id={
                            "type": "area_parent",
                            "index": f"{page_prefix}-AIO_AREA",
                        },
                    )
                )
            ),
            html.Br(),
            dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            html.H3(
                                id=f"{page_prefix}-crc-header",
                                children="CRC Recommendations - ",
                                style={
                                    "color": domain_colour,
                                    "marginTop": "10px",
                                    "marginBottom": "0px",
                                },
                            )
                        ),
                        html.Br(),
                        html.Div(
                            className="flex-container",
                            children=[
                                html.P(
                                    "Select country:",
                                    style={"margin-right": "10px"},
                                ),
                                dcc.Dropdown(
                                    id=f"{page_prefix}-country-filter-crc",
                                    options=[
                                        {
                                            "label": "All countries",
                                            "value": "all_countries",
                                        }
                                    ]
                                    + [
                                        {"label": country, "value": country}
                                        for country in all_countries
                                    ],
                                    value="all_countries",
                                    placeholder="Select country",
                                    multi=False,
                                    clearable=True,
                                    style={"width": "200px"},
                                ),
                                html.P(
                                    "Select report year:",
                                    style={
                                        "margin-right": "10px",
                                        "margin-left": "10px",
                                    },
                                ),
                                dcc.Dropdown(
                                    id=f"{page_prefix}-year-filter-crc",
                                    multi=False,
                                    clearable=False,
                                    style={"width": "220px"},
                                ),
                                html.P(
                                    [
                                        html.I(
                                            className="fa-solid fa-arrow-up-right-from-square",
                                            style={
                                                "color": domain_colour,
                                                "margin-left": "20px",
                                                "margin-right": "5px",
                                            },
                                        ),
                                        html.A(
                                            "Explore CRC Recommendations Dashboard",
                                            href="https://public.tableau.com/app/profile/ecaro.data/viz/RecommendationsoftheCommitteeontheRightsoftheChild/Overview",
                                            target="_blank",
                                            style={
                                                "color": domain_colour,
                                                "text-decoration": "underline",
                                            },
                                        ),
                                    ]
                                ),
                            ],
                        ),
                        html.Br(),
                        html.Div(id=f"{page_prefix}-crc-accordion"),
                    ],
                ),
                className="crc_card",
                # style={"display": "None"},
            ),
        ],
    )


def make_card(
    name,
    suffix,
    indicator_sources,
    source_link,
    indicator_header,
    numerator_pairs,
    page_prefix,
    domain_colour,
):
    card = [
        dbc.CardBody(
            [
                html.Span(
                    indicator_header,
                    className="fs-1 w-bold",
                    style={
                        "textAlign": "center",
                        "color": domain_colour,
                    },
                ),
                html.H4(suffix, className="card-title"),
                html.P(name, className="lead"),
            ],
            style={
                "textAlign": "center",
            },
        ),
    ]

    return card, get_card_popover_body(numerator_pairs)

def available_crc_years(country, indicator, indicators_dict):
    if indicator is None:
        return {"label": 'Select subdomain', "value": None}, None
    _, _, subdomain = update_domain_and_subdomain_values(indicator)
    subdomain = indicators_dict[subdomain].get("NAME")

    if country == "all_countries":
        all_years = sorted(CRC_df["Year"].unique(), reverse=True)
        all_years_options = [{"label": str(year), "value": year} for year in all_years]
        all_years_options.insert(
            0, {"label": "Latest year for each country", "value": "All"}
        )
        latest_year = "All"
        return all_years_options, latest_year

    # Check if the subdomain is one of the cross-cutting subdomains
    if subdomain in crosscutting_columns:
        country_filtered_df = CRC_df.loc[
            (CRC_df["Country"] == country) & (CRC_df[subdomain] == "Yes")
        ]
    else:
        country_filtered_df = CRC_df.loc[
            (CRC_df["Country"] == country) & (CRC_df["Sub-Domain"] == subdomain)
        ]

    available_years = country_filtered_df["Year"].unique()

    if len(available_years) > 0:
        latest_year = max(available_years)
    else:
        latest_year = None

    return [
        {"label": str(year), "value": year} for year in available_years
    ], latest_year


# stop automatic numbering of CRC recommendations
def escape_markdown_numbering(text):
    """Escape numbering in markdown to prevent auto-formatting."""
    # Use regex to find patterns like "27." and replace them with "27\."
    return re.sub(r"(\d+)\.", r"\1\.", text)


# Function to format recommendations by bottleneck type
def format_recommendations_by_bottleneck(df, country, year):
    recommendations = {
        "Enabling environment": [],
        "Supply": [],
        "Demand": [],
    }
    for bottleneck in recommendations.keys():
        recs = df.loc[
            df["Bottleneck Type"].str.contains(bottleneck, case=False), "Recommendation"
        ]
        formatted_recs = [
            escape_markdown_numbering(rec.replace("; and", ".").replace(";", "."))
            for rec in recs
        ]
        if formatted_recs:
            recommendations[bottleneck].append(
                f"\n\n**{country} ({year}):**\n\n" + "\n\n".join(formatted_recs)
            )
    return recommendations


# Function to generate Accordion items
def generate_accordion_items(recommendations, page_prefix):
    titles = [
        (
            "Enabling environment",
            "Enabling environment - legislation, policy, resources, coordination, data",
        ),
        (
            "Supply",
            "Supply - adequately staffed services, facilities, information, commodities",
        ),
        ("Demand", "Demand - financial access and social behavioural drivers"),
    ]
    accordion_items = [
        dbc.AccordionItem(
            title=title,
            item_id=f"accordion-{idx}",
            class_name="crc-accordion",
            children=[
                dcc.Loading(
                    [
                        dcc.Markdown(
                            id=f"{page_prefix}-crc-{bottleneck.lower()}", children=recs
                        )
                    ]
                )
            ],
            style={"margin-bottom": "10px"},
        )
        for idx, (bottleneck, title) in enumerate(titles)
        if (recs := recommendations.get(bottleneck))
    ]
    return accordion_items

# Function to filter CRC_df based on country, subdomain, and bottleneck type
def filter_crc_data(year, country, indicator, page_prefix):
    _, _, subdomain_code = update_domain_and_subdomain_values(indicator)
    # Get the subdomain name based on the subdomain code
    subdomain_name = None
    for subdomain, details in data_dict["subdomains"].items():
        if details["code"] == subdomain_code:
            subdomain_name = subdomain
            break

    if subdomain_name is None:
        # Handle the case where the subdomain code doesn't match any subdomain
        return (
            "CRC Recommendations - Select subdomain or indicator",
            f"No related recommendations for this {'subdomain' if country == 'all_countries' else 'country and subdomain'}.",
        )

    # Adjusting the filter condition for cross-cutting subdomains
    if subdomain_name in crosscutting_columns:
        filter_condition = CRC_df[subdomain_name] == "Yes"
    else:
        filter_condition = CRC_df["Sub-Domain"] == subdomain_name

    if country == "all_countries":
        if year == "All":
            latest_years = CRC_df.groupby("Country")["Year"].max().to_dict()
            all_recommendations = {}
            for country_name, latest_year in latest_years.items():
                df = CRC_df[
                    filter_condition
                    & (CRC_df["Year"] == latest_year)
                    & (CRC_df["Country"] == country_name)
                ]
                recommendations = format_recommendations_by_bottleneck(
                    df, country_name, latest_year
                )
                for key, value in recommendations.items():
                    all_recommendations.setdefault(key, []).extend(value)
        else:
            df = CRC_df[filter_condition & (CRC_df["Year"] == year)]
            all_recommendations = {}
            unique_countries = df["Country"].unique()
            for country_name in unique_countries:
                country_df = df[df["Country"] == country_name]
                recommendations = format_recommendations_by_bottleneck(
                    country_df, country_name, year
                )
                for key, value in recommendations.items():
                    all_recommendations.setdefault(key, []).extend(value)
    else:
        df = CRC_df[
            filter_condition & (CRC_df["Year"] == year) & (CRC_df["Country"] == country)
        ]
        all_recommendations = format_recommendations_by_bottleneck(df, country, year)

    header_text = f"CRC Recommendations - {subdomain_name}"
    # Check if there are no recommendations
    if not any(all_recommendations.values()):
        return header_text, f"No related recommendations for this {'subdomain' if country == 'all_countries' else 'country and subdomain'}."
        
    accordion_items = generate_accordion_items(all_recommendations, page_prefix)
    return header_text, dbc.Accordion(accordion_items, active_item="-1")


def indicator_card(
    filters,
    name,
    indicator,
    suffix,
    absolute=False,
    average=False,
    min_max=False,
    sex_code=None,
    age_group=None,
    page_prefix=None,
    domain_colour="#1cabe2",
):
    try:
        indicators = [indicator] # adapting code as now only one indicator is used

        # TODO: Change to use albertos config
        # lbassil: had to change this to cater for 2 dimensions set to the indicator card like age and sex
        breakdown = "TOTAL"
        # define the empty dimensions dict to be filled based on the card data filters
        dimensions = {}
        if age_group is not None:
            dimensions["AGE"] = [age_group]
        if sex_code is not None:
            dimensions["SEX"] = [sex_code]

        filtered_data = get_data(
            indicators,
            filters["years"],
            filters["countries"],
            breakdown,
            dimensions,
            latest_data=True,
        )

        df_indicator_sources = df_sources[df_sources["Code"].isin(indicators)]
        unique_indicator_sources = df_indicator_sources["Source_Full"].unique()
        indicator_sources = (
            "; ".join(list(unique_indicator_sources))
            if len(unique_indicator_sources) > 0
            else ""
        )
        source_link = (
            df_indicator_sources["Source_Link"].unique()[0]
            if len(unique_indicator_sources) > 0
            else ""
        )
        # lbassil: add this check because we are getting an exception where there is no data; i.e. no totals for all dimensions mostly age for the selected indicator
        if filtered_data.empty:
            indicator_header = "No data"
            indicator_sources = "NA"
            suffix = ""
            numerator_pairs = []
            return make_card(
                name,
                suffix,
                indicator_sources,
                source_link,
                indicator_header,
                numerator_pairs,
                page_prefix,
                domain_colour,
            )[0]

    except requests.exceptions.HTTPError as err:
        indicator_header = "No data"
        indicator_sources = "NA"
        suffix = ""
        numerator_pairs = []
        return make_card(
            name,
            suffix,
            indicator_sources,
            source_link,
            indicator_header,
            numerator_pairs,
            page_prefix,
            domain_colour,
        )[0]

    # select last value for each country
    indicator_values = (
        filtered_data.groupby(
            [
                "Country_name",
                "TIME_PERIOD",
            ]
        ).agg({"OBS_VALUE": "sum", "CODE": "count"})
    ).reset_index()

    numerator_pairs = (
        indicator_values[indicator_values.CODE == len(indicators)]
        .groupby("Country_name", as_index=False)
        .last()
        .set_index(["Country_name", "TIME_PERIOD"])
    )

    if "countries" in suffix.lower():
        # this is a hack to accomodate small cases (to discuss with James)
        if "FREE" in indicator or "COMP" in indicator:
            # trick to filter number of years of free education
            indicator_sum = (numerator_pairs.OBS_VALUE >= 1).to_numpy().sum()
            sources = numerator_pairs.index.tolist()
            numerator_pairs = numerator_pairs[numerator_pairs.OBS_VALUE >= 1]
        elif absolute:
            # trick cards data availability among group of indicators and latest time_period
            # doesn't require filtering by count == len(numors)
            numerator_pairs = indicator_values.groupby(
                "Country_name", as_index=False
            ).last()
            max_time_filter = (
                numerator_pairs.TIME_PERIOD < numerator_pairs.TIME_PERIOD.max()
            )
            numerator_pairs.drop(numerator_pairs[max_time_filter].index, inplace=True)
            numerator_pairs.set_index(["Country_name", "TIME_PERIOD"], inplace=True)
            sources = numerator_pairs.index.tolist()
            indicator_sum = len(sources)
        else:
            # trick to accomodate cards for admin exams (AND for boolean indicators)
            # filter exams according to number of indicators
            indicator_sum = (
                (numerator_pairs.OBS_VALUE == len(indicators)).to_numpy().sum()
            )
            sources = numerator_pairs.index.tolist()
            numerator_pairs = numerator_pairs[
                numerator_pairs.OBS_VALUE == len(indicators)
            ]

    else:
        indicator_sum = numerator_pairs["OBS_VALUE"].to_numpy().sum()
        sources = numerator_pairs.index.tolist()
        if average and len(sources) > 1:
            indicator_sum = indicator_sum / len(sources)

    # define indicator header text: the resultant number except for the min-max range
    if min_max and len(sources) > 1:
        min_val = numerator_pairs["OBS_VALUE"].min()
        max_val = numerator_pairs["OBS_VALUE"].max()
        # string format for cards: thousands separator and number of decimals
        min_format = (
            "{:,."
            + (
                "0"
                if np.isnan(min_val) or "." not in str(min_val)
                else (
                    "0"
                    if str(min_val)[::-1][0] == "0"
                    else str(str(min_val)[::-1].find("."))
                )
            )
            + "f}"
        )
        max_format = (
            "{:,."
            + (
                "0"
                if np.isnan(max_val) or "." not in str(max_val)
                else (
                    "0"
                    if str(max_val)[::-1][0] == "0"
                    else str(str(max_val)[::-1].find("."))
                )
            )
            + "f}"
        )
        indicator_min = min_format.format(min_val)
        indicator_max = max_format.format(max_val)

        if "%" in filtered_data["Unit_name"].values:
            min_max_suffix = "%"
        else:
            min_max_suffix = ""

        indicator_header = (
            f"{indicator_min}{min_max_suffix} - {indicator_max}{min_max_suffix}"
        )
    else:
        # string format for cards: thousands separator and number of decimals
        sum_format = (
            "{:,."
            + (
                "0"
                if np.isnan(indicator_sum) or "." not in str(indicator_sum)
                else (
                    "0"
                    if str(indicator_sum)[::-1][0] == "0"
                    else str(str(indicator_sum)[::-1].find("."))
                )
            )
            + "f}"
        )
        indicator_header = sum_format.format(indicator_sum)

    return make_card(
        name,
        suffix,
        indicator_sources,
        source_link,
        indicator_header,
        numerator_pairs,
        page_prefix,
        domain_colour,
    )


def download_data(n_clicks, data):
    download_df = pd.DataFrame.from_dict(data)
    download_df["Indicator_name"] = download_df["CODE"].map(indicator_names)

    # Rename columns
    download_df = download_df.rename(
        columns={
            "REF_AREA": "Country_code",
            "CODE": "Indicator_Code",
            "Sex_name": "Sex",
            "Residence_name": "Residence",
            "Wealth_name": "Wealth_quintile",
            "Age_name": "Age",
        }
    )

    # Select desired columns in the specified order
    columns_to_keep = [
        "Country_code",
        "Country_name",
        "Indicator_Code",
        "Indicator_name",
        "OBS_VALUE",
        "TIME_PERIOD",
        "Sex",
        "Residence",
        "Wealth_quintile",
        "Age",
        "OBS_FOOTNOTE",
        "FREQ",
        "DATA_SOURCE",
    ]
    download_df = download_df[columns_to_keep]

    # Return the downloadable CSV file
    return dcc.send_data_frame(
        download_df.to_csv, f"{download_df['Indicator_Code'][0]}.csv"
    )


graphs_dict = {
    "bar": {
        "options": dict(
            x="Country_name",
            y="OBS_VALUE",
            barmode="group",
            text="OBS_VALUE",
            custom_data=[
                "OBS_VALUE",
                "Country_name",
                "TIME_PERIOD",
                "OBS_FOOTNOTE",
                "DATA_SOURCE",
                "Sex_name",
                "Age_name",
                "Wealth_name",
                "Residence_name",
            ],
            height=500,
            text_auto=".3s",
        ),
        "layout_options": dict(
            xaxis_title={"standoff": 0},
            margin_t=30,
            margin_b=0,
        ),
    },
    "count_bar": {
        "options": dict(
            x="Status",
            color="Status",
            color_discrete_map={"Yes": "#1CABE2", "No": "#fcba03"},
            custom_data=[
                "OBS_VALUE",
                "Country_name",
                "TIME_PERIOD",
                "OBS_FOOTNOTE",
                "DATA_SOURCE",
                "Status",
            ],
            height=450,
            width=1000,
        ),
        "layout_options": dict(
            xaxis_title={"standoff": 0},
            margin_t=50,
            margin_b=0,
        ),
    },
    "line": {
        "options": dict(
            x="TIME_PERIOD",
            y="OBS_VALUE",
            color="Country_name",
            custom_data=[
                "OBS_VALUE",
                "Country_name",
                "TIME_PERIOD",
                "OBS_FOOTNOTE",
                "DATA_SOURCE",
            ],
            line_shape="spline",
            render_mode="svg",
            height=500,
        ),
        "trace_options": dict(mode="markers+lines", line=dict(width=0.8)),
        "layout_options": dict(
            xaxis_title={"standoff": 10},
            margin_t=40,
            margin_b=0,
        ),
    },
    "map": {
        "options": dict(
            locations="REF_AREA",
            featureidkey="id",
            color="OBS_VALUE",
            mapbox_style="carto-positron",
            geojson=geo_json_countries,
            zoom=2.5,
            center={"lat": 51.9194, "lon": 19.040236},
            opacity=0.6,
            custom_data=[
                "OBS_VALUE",
                "Country_name",
                "TIME_PERIOD",
                "OBS_FOOTNOTE",
                "DATA_SOURCE",
            ],
            height=500,
            width=None,
        ),
        "layout_options": dict(margin={"r": 0, "t": 80, "l": 2, "b": 5}),
    },
}


def selections(theme, indicators):
    current_theme = theme[1:].upper() if theme else next(iter(indicators.keys()))
    selections = dict(
        theme=current_theme,
        indicators_dict=indicators,
    )
    return selections


def get_filters(years_slider, countries, country_group):
    # start_time = time.time()

    if "all_values" in countries:
        if country_group == "unicef":
            countries = unicef_country_prog
        elif country_group == "eu":
            countries = eu_countries
        elif country_group == "efta":
            countries = efta_countries
        elif country_group == "eu + efta":
            countries = eu_countries + efta_countries
        else:
            countries = all_countries

    filter_countries = countries
    country_text = f"{len(filter_countries)}"
    # need to include the last selected year as it was exluded in the previous method
    selected_years = years[years_slider[0] : years_slider[1] + 1]

    # Use the dictionary to return the values of the selected countries based on the SDMX ISO3 codes
    countries_selected_codes = [
        countries_iso3_dict[country] for country in filter_countries
    ]
    filter_dict = dict(
        years=selected_years,
        countries=countries_selected_codes,
        count_names=filter_countries,
    )
    return (filter_dict, filter_countries, selected_years, country_text)


def themes(subdomain_code, indicators_dict, page_prefix):
    url_hash = "#{}".format(subdomain_code.lower())

    # Load the descriptions from the JSON file
    descriptions_file_path = f"{pathlib.Path(__file__).parent.parent.absolute()}/static/subdomain_descriptions.json"
    with open(descriptions_file_path) as indicator_file:
        descriptions = json.load(indicator_file)

    # Get the description for the current subdomain
    description = descriptions.get(subdomain_code, "")

    return subdomain_code, description


def aio_options(theme, indicators_dict, page_prefix):
    # start_time = time.time()
    area = "AIO_AREA"
    current_theme = theme["theme"]
    if area in indicators_dict[subdomain]:
        indicators = indicators_dict[current_theme][area].get("indicators")
        area_indicators = indicators.keys() if indicators is dict else indicators

        default_option = (
            indicators_dict[current_theme][area].get("default")
            if area in indicators_dict[current_theme]
            else ""
        )

    area_buttons = [
        dbc.Button(
            [
                html.Span(
                    re.sub(r"\s*\(SDG.*\)", " ", indicator_buttons[code]),
                    className="mr-2",
                ),  # Button label without "(SDG ...)"
                dbc.Badge("SDG", color="primary", className="mr-1")
                if "SDG" in indicator_buttons[code]
                else None,
            ],
            id={"type": f"{page_prefix}-indicator_button", "index": code},
            color=f"{page_prefix}",
            className="my-1",
            active=code == default_option if default_option != "" else num == 0,
        )
        for num, code in enumerate(area_indicators)
    ]

    # return html.Div(className="force-inline-controls", children=area_buttons)
    return area_buttons


def breakdown_options(indicator, fig_type):
    options = [{"label": "Total", "value": "TOTAL"}]
    # lbassil: change the disaggregation to use the names of the dimensions instead of the codes
    all_breakdowns = [
        {"label": "Sex", "value": "SEX"},
        {"label": "Age", "value": "AGE"},
        {"label": "Residence", "value": "RESIDENCE"},
        {"label": "Wealth Quintile", "value": "WEALTH_QUINTILE"},
    ]
    dimensions = indicators_config.get(indicator, {}).keys()
    # disaggregate only bar charts
    if dimensions and fig_type == "bar":
        for breakdown in all_breakdowns:
            if breakdown["value"] in dimensions:
                options.append(breakdown)
    return options


def fig_options(indicator):
    # get the first indicator of the list... we have more than one indicator in the cards
    indicator_config = indicators_config.get(indicator, {})

    # check if the indicator has is string type and give only bar and map as options
    if indicator_config and nominal_data(indicator_config):
        area_types = [
            {"label": "Bar", "value": "count_bar"},
            {"label": "Map", "value": "map"},
        ]
        default_graph = "map"
    else:
        area_types = [
            {"label": "Bar", "value": "bar"},
            {"label": "Line", "value": "line"},
            {"label": "Map", "value": "map"},
        ]
        default_graph = "bar"

    return area_types, default_graph


def active_button(_, buttons_id):
    # figure out which button was clicked
    ctx = callback_context
    button_code = eval(ctx.triggered[0]["prop_id"].split(".")[0])["index"]

    # return active properties accordingly
    return [button_code == id_button["index"] for id_button in buttons_id]


def default_compare(compare_options, selected_type, indicators_dict, indicator):
    if indicator is None:
        return "TOTAL"
    area = "AIO_AREA"
    _, _, subdomain = update_domain_and_subdomain_values(indicator)
    config = indicators_dict[subdomain][area]["graphs"][selected_type]
    default_compare = config.get("compare")

    if selected_type != "bar":
        return "TOTAL"
    elif default_compare is None:
        return "TOTAL"
    elif default_compare in compare_options:
        return default_compare
    elif len(compare_options) > 1:
        return compare_options[1]["value"]
    else:
        return compare_options[0]["value"]


def aio_area_figure(
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
):
    # start_time = time.time()
    filters, country_selector, selected_years, country_text = get_filters(
        years_slider,
        countries,
        country_group,
    )

    if indicator is None:
        return (
            f"{selected_years[0]} - {selected_years[-1]}",
            EMPTY_CHART,
            "",
            [],
            [],
            "",
            [],
            "",
            [],
            [],
            "",
        )

    try:
        area = "AIO_AREA"
        _, _, subdomain = update_domain_and_subdomain_values(indicator)
        default_graph = indicators_dict[subdomain][area].get("default_graph", "line")

        fig_type = selected_type if selected_type else default_graph
        fig_config = indicators_dict[subdomain][area]["graphs"][fig_type].copy()
        options = fig_config.get("options")
        traces = fig_config.get("trace_options")
        layout_opt = fig_config.get("layout_options")
        dimension = (
            False
            if fig_type in ["count_bar", "line", "map"] or compare == "TOTAL"
            else compare
        )
        indicator_name = str(indicator_names.get(indicator, ""))
        indicator_description = indicator_definitions.get(indicator, "")

        # make API request to retrieve data
        data = get_data(
            [indicator],
            filters["years"],
            filters["countries"],
            compare,
            latest_data=False if fig_type == "line" else True,
        )

        # check if the dataframe is empty meaning no data to display as per the user's selection
        if data.empty:
            return (
                f"{selected_years[0]} - {selected_years[-1]}",
                EMPTY_CHART,
                "",
                [],
                [],
                "",
                [],
                "",
                [],
                [],
                "",
            )
        else:
            data.sort_values(
                "OBS_VALUE",
                ascending=False if data.OBS_VALUE.dtype.kind in "iufc" else True,
                inplace=True,
            )

    except requests.exceptions.HTTPError as err:
        return (
            f"{selected_years[0]} - {selected_years[-1]}",
            EMPTY_CHART,
            "",
            [],
            [],
            "",
            [],
            "",
            [],
            [],
            "",
        )

    # indicator card
    card_key = indicator
    card_config = [
        elem
        for elem in indicators_dict[subdomain]["CARDS"]
        if elem["indicator"] == card_key
    ]

    ind_card = (
        []
        if not card_config or "CARDS" not in indicators_dict[subdomain]
        else indicator_card(
            filters,
            card_config[0]["name"],
            card_config[0]["indicator"],
            card_config[0]["suffix"],
            card_config[0].get("absolute"),
            card_config[0].get("average"),
            card_config[0].get("min_max"),
            card_config[0].get("sex"),
            card_config[0].get("age"),
            page_prefix,
            domain_colour,
        )
    )

    # lbassil: was UNIT_MEASURE
    name = (
        data[data["CODE"] == card_key]["Unit_name"].astype(str).unique()[0]
        if len(data[data["CODE"] == card_key]["Unit_name"].astype(str).unique()) > 0
        else ""
    )
    df_indicator_sources = df_sources[df_sources["Code"] == card_key]
    unique_indicator_sources = df_indicator_sources["Source_Full"].unique()

    if data["CODE"].isin(["DM_CHLD_POP", "DM_CHLD_POP_PT"]).any():
        source = "Multiple Sources"
    elif len(unique_indicator_sources) > 0:
        source = "; ".join(list(unique_indicator_sources))
    else:
        source = ""

    source_link = (
        df_indicator_sources["Source_Link"].unique()[0]
        if len(unique_indicator_sources) > 0
        and not data["CODE"].isin(["DM_CHLD_POP", "DM_CHLD_POP_PT"]).any()
        else ""
    )

    options["labels"] = DEFAULT_LABELS.copy()
    options["labels"]["OBS_VALUE"] = name

    # set the chart title, wrap the text when the indicator name is too long
    chart_title = textwrap.wrap(
        indicator_name,
        width=74,
    )
    chart_title = "<br>".join(chart_title)

    # set the layout to center the chart title and change its font size and color
    layout = go.Layout(
        title=chart_title,
        title_x=0.5,
        font=dict(family="Verdana", size=11),
        legend=dict(x=1, y=0.5),
        xaxis={
            "categoryorder": "total descending",
            "tickangle": -45,
            "tickmode": "linear",
            "tickfont_size": 11,
        },
    )
    if layout_opt:
        layout.update(layout_opt)

    # Add this code to avoid having decimal year on the x-axis for time series charts
    if fig_type == "line":
        data.sort_values(by=["TIME_PERIOD", "Country_name"], inplace=True)
        layout["xaxis"] = dict(
            tickmode="linear",
            tick0=filters["years"][0],
            dtick=1,
            categoryorder="total ascending",
        )

    if fig_type == "count_bar":
        layout["xaxis"] = dict(tickfont_size=14, tickangle=None)

    hovertext = (
        "Country: %{customdata[1]}  </br>"
        + "Year: %{customdata[2]}  </br><br>"
        + "Footnote: %{customdata[3]}  </br>"
        + "Primary Source: %{customdata[4]}  </br>"
    )

    if "YES_NO" not in data.UNIT_MEASURE.values:
        hovertext = "%{customdata[0]:,}  </br><br>" + hovertext

    if dimension:
        # lbassil: use the dimension name instead of the code
        dimension_name = str(dimension_names.get(dimension, ""))
        options["color"] = dimension_name

        if dimension_name == "Sex_name":
            options["color_discrete_map"] = {"Female": "#944a9d", "Male": "#1a9654"}
            hovertext = "%{customdata[5]}  </br><br>" + hovertext

        elif dimension_name == "Age_name":
            hovertext = "%{customdata[6]}  </br><br>" + hovertext

        elif dimension_name == "Wealth_name":
            hovertext = "%{customdata[7]}  </br><br>" + hovertext

        else:
            options["color_discrete_map"] = {"Rural": "#5dd763", "Urban": "#d9b300"}
            hovertext = "%{customdata[8]}  </br><br>" + hovertext

        # sort by the compare value to have the legend in the right ascending order
        data.sort_values(by=[dimension], inplace=True)

    graph_info = ""
    # rename figure_type 'map': 'choropleth' (plotly express)
    if fig_type == "map":
        # map disclaimer text
        graph_info = "Maps on this site do not reflect a position by UNICEF on the legal status of any country or territory or the delimitation of any frontiers."
        fig_type = "choropleth_mapbox"
        if "YES_NO" in data.UNIT_MEASURE.values:
            options["color"] = "Status"
            options["color_discrete_map"] = {"Yes": "#1CABE2", "No": "#fcba03"}
        else:
            options["color_continuous_scale"] = map_colour
            options["range_color"] = [data.OBS_VALUE.min(), data.OBS_VALUE.max()]

    if fig_type == "bar":
        # turn off number formatting of data labels under 100
        if max(data.OBS_VALUE) <= 100:
            options["text_auto"] = False

    if fig_type == "count_bar":
        # change to fig type to generate px.bar
        fig_type = "bar"

    fig = getattr(px, fig_type)(data, **options)
    fig.update_layout(layout)
    # remove x-axis title but keep space below
    fig.update_layout(xaxis_title="")
    if fig_type == "bar" and not dimension and "YES_NO" not in data.UNIT_MEASURE.values:
        fig.update_traces(marker_color=domain_colour)
        # if (data.OBS_VALUE == 0).any():
        # fig.update_traces(textposition="outside")
    if fig_type == "line":
        fig.update_traces(**traces)
        # adding invisible line at zero to make sure the y-axis starts at zero
        fig.add_hline(y=-0.3, line_color="rgba(0,0,0,0)")

    fig.update_traces(hovertemplate=hovertext)

    if fig_type == "bar" and "YES_NO" in data.UNIT_MEASURE.values:
        dfs = data.groupby("Status").count()
        fig.add_trace(
            go.Scatter(
                x=dfs.index,
                y=dfs["OBS_VALUE"],
                text=dfs["OBS_VALUE"],
                mode="text",
                textposition="top center",
                textfont=dict(
                    size=14,
                ),
                showlegend=False,
            )
        )
    # countries not reporting
    not_rep_count = np.setdiff1d(filters["count_names"], data.Country_name.unique())
    # number of countries from selection
    count_sel = len(filters["countries"])

    # countries reporting
    rep_count = count_sel - len(not_rep_count)

    json_data = data.to_dict()

    return (
        f"{selected_years[0]} - {selected_years[-1]}",
        fig,
        [
            html.Div(
                [
                    html.P(
                        "Source: ",
                        style={
                            "display": "inline-block",
                            "textDecoration": "underline",
                            "fontWeight": "bold",
                        },
                    ),
                    html.A(
                        f" {source}",
                        href=source_link,
                        target="_blank",
                        id={
                            "type": "area_sources",
                            "index": f"{page_prefix}-AIO_AREA",
                        },
                        className="alert-link",
                        style={"color": domain_colour},
                    ),
                ],
            )
        ],
        ind_card[0],
        [
            html.Div(
                [
                    html.P(
                        "Countries with data: ",
                        style={
                            "display": "inline-block",
                            "textDecoration": "underline",
                            "fontWeight": "bold",
                        },
                    ),
                    html.P(
                        f" {rep_count} / {count_sel}",
                        style={
                            "display": "inline-block",
                            "fontWeight": "bold",
                            "color": domain_colour,
                            "whiteSpace": "pre",
                        },
                    ),
                ]
            )
        ],
        ind_card[1],
        [
            html.Div(
                [
                    html.P(
                        "Countries without data: ",
                        style={
                            "display": "inline-block",
                            "textDecoration": "underline",
                            "fontWeight": "bold",
                        },
                    ),
                    html.P(
                        f" {len(not_rep_count)} / {count_sel}",
                        style={
                            "display": "inline-block",
                            "fontWeight": "bold",
                            "color": domain_colour,
                            "whiteSpace": "pre",
                        },
                    ),
                ]
            )
        ],
        dcc.Markdown(["- " + "\n- ".join(sorted(not_rep_count, key=str.lower))]),
        graph_info,
        json_data,
        indicator_description,
    )
