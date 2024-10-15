import collections
import json
import logging
from io import BytesIO
from pathlib import Path
import pathlib
from flask import request
from urllib.parse import urlsplit, urlunsplit
import re
from dash_service.static.page_config import (
    merged_page_config
)

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
import dash_daq as daq


from dash_service.components import fa
from dash_service.utils import get_geo_file
from ..sdmx import data_access_sdmx

# set defaults
pio.templates.default = "plotly_white"
px.defaults.color_continuous_scale = px.colors.sequential.BuGn
px.defaults.color_discrete_sequence = px.colors.qualitative.Dark24


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
                "text": "No data is available for the selected filters or the database is temporarily unavailable.",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 20},
            }
        ],
    }
}

average_text = "This option displays the simple (arithmetic) average, dynamically calculated based on the filtered data. As such, it is not always representative of the entire region, as it reflects only the available data. Furthermore, for indicators referring to populations, population-weighted averages are recommended for a more accurate regional overview."

help_text = html.Div([
        html.Strong("HOW TO USE DASHBOARD"),
        html.P([""]),
        html.P([
            html.Strong("Views: ", style={'color': '#1CABE2'}),
            "Choose between two primary views for data exploration. ",
            html.Strong("'Explore using the ECA Child Rights Monitoring Framework'"),
            " allows you to select a domain and view indicators within each of its sub-domains, providing a structured approach aligned with child rights priorities. Alternatively, ",
            html.Strong("'Search by Indicator'"),
            " lets you select specific indicators from a dropdown menu and filter by SDG indicators and/or by specific domains or sub-domains."
        ]),
        html.P([
            html.Strong("CRC Recommendations: ", style={'color': '#1CABE2'}),
            "At the bottom of the page, there are ",
            html.Strong("Committee on the Rights of the Child Recommendations"),
            " which are related to each sub-domain. These recommendations have been organized by three different types of bottlenecks and can be filtered by country and year of report."
        ]),
        html.P([
            html.Strong("Chart types: ", style={'color': '#1CABE2'}),
            "Visualize data with bar charts and regional maps displaying the latest data for each country, or use line graphs to track historical trends."
        ]),
        html.P([
            html.Strong("Filters and disaggregations: ", style={'color': '#1CABE2'}),
            "Enhance your analysis with filters for year range, country group, or individual countries. When disaggregated data is available, these options will appear on the chart."
        ]),
        html.P([
            html.Strong("Definitions: ", style={'color': '#1CABE2'}),
            "Hover over information icons to view definitions of indicators and sub-domains."
        ]),
        html.P([
            html.Strong("Download data: ", style={'color': '#1CABE2'}),
            "To download the data displayed in the chart in Excel format, click on the ",
            html.Strong("'Download data'"),
            " button below the chart. To download the chart as in PNG format, hover over the top right corner of the chart and click on the camera icon."
        ]),
        html.P([
            html.Strong("Data availability: ", style={'color': '#1CABE2'}),
            "To learn more about data availability for each indicator, hover over the ",
            html.Strong("'Countries with data'"),
            " and ",
            html.Strong("'Countries without data'"), 
            " buttons to see which countries have data within the selected year range."
        ]),
    ])

config_file_path = (
    f"{pathlib.Path(__file__).parent.parent.absolute()}/static/indicator_config.json"
)
with open(config_file_path) as config_file:
    indicators_config = json.load(config_file)


geo_json_countries = get_geo_file("ecaro.geo.json")

unicef = sdmx.Request("UNICEF", timeout=20)

metadata = unicef.dataflow("TRANSMONEE", provider="ECARO", version="1.0")
dsd = metadata.structure["DSD_ECARO_TRANSMONEE"]

indicator_names = {
    code.id: code.name.en
    for code in dsd.dimensions.get("INDICATOR").local_representation.enumerated
}

indicator_def_file_path = f"{pathlib.Path(__file__).parent.parent.absolute()}/static/indicator_definitions.json"
with open(indicator_def_file_path) as definitions_file:
    indicator_definitions = json.load(definitions_file)

# Load the descriptions from the JSON file
descriptions_file_path = f"{pathlib.Path(__file__).parent.parent.absolute()}/static/subdomain_descriptions.json"
with open(descriptions_file_path) as indicator_file:
    subdomain_descriptions = json.load(indicator_file)

# custom names as requested by siraj: update thousands for consistency, packed indicators
custom_names = {
    # erase_name_thousands
    "DM_BRTS": "Number of births",
    "DM_POP_TOT_AGE": "Population by age",
    "HT_SN_STA_OVWGTN": "Number of children moderately or severely overweight - SDG 2.2.2",
    "DM_CHLD_POP": "Child population aged 0-17 years",
    "DM_ADOL_POP": "Adolescent population aged 10-19 years",
    "DM_TOT_POP_PROSP": "Population prospects",
    "DM_ADOL_YOUTH_POP": "Adolescent, young and youth population aged 10-24 years",
    "DM_ADULT_YOUTH_POP": "Adult youth population aged 20-29 years",
    "DM_REPD_AGE_POP": "Population of reproductive age 15-49 years",
    "DM_CHLD_YOUNG_COMP_POP": "Child population aged 0-17 years",
    "ICT_SECURITY_CONCERN": "Percentage of 16-24 year olds who limited their personal internet activities in the last 12 months due to security concerns",
    "ICT_PERSONAL_DATA": "Percentage of 16-24 year olds who used the internet in the last 3 months and managed access to their personal data",
    "MT_SDG_SUICIDE": "Suicide mortality rate for 15-19 year olds (deaths per 100,000 population) - SDG 3.4.2",
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

years = list(range(2000, 2025))

# some indexes have been listed as ratios in SDG database so we need to specify not to round these indicators
codes_3_decimals = ['HVA_EPI_INF_RT_0-14', 'EDU_SE_TOT_GPI_L2_MAT', 'EDU_SE_TOT_GPI_L2_REA', 'EDU_SE_AGP_CPRA_L3']
codes_1_decimal = ['DM_FRATE_COMP', 'PV_GINI_COEF']

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

central_asia = [
    "Kazakhstan",
    "Kyrgyzstan",
    "Tajikistan",
    "Turkmenistan",
    "Uzbekistan",
]

western_europe = [
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
    "Portugal",
    "San Marino",
    "Spain",
    "Sweden",
    "Switzerland",
    "United Kingdom",
]

eastern_europe = [
    "Albania",
    "Armenia",
    "Azerbaijan",
    "Belarus",
    "Bosnia and Herzegovina",
    "Bulgaria",
    "Croatia",
    "Georgia",
    "Hungary",
    "Kosovo (UNSCR 1244)",
    "Montenegro",
    "North Macedonia",
    "Poland",
    "Republic of Moldova",
    "Romania",
    "Russian Federation",
    "Serbia",
    "Slovakia",
    "Slovenia",
    "Türkiye",
    "Ukraine",
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
    "BDDS_UIS": "UNESCO Institute for Statistics",
    "NEW_UIS": "UNESCO Institute for Statistics",
    "BDDS_UIS": "UNESCO Institute for Statistics",
    "UNDP": "United Nations Development Programme",
    "TMEE": "Transformative Monitoring for Enhanced Equity (TransMonEE)",
}

'''
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
''' 

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
    "child-rights": "crg-dropdown",
    "child-health": "han-dropdown",
    "child-education": "edu-dropdown",
    "child-protection": "chp-dropdown",
    "child-participation": "par-dropdown",
    "child-poverty": "pov-dropdown",
    "child-cross-cutting": "cci-dropdown",
}

# Read the CRC Excel file and skip the first row (header is in the second row)
crc_file_path = f"{pathlib.Path(__file__).parent.parent.absolute()}/static/Full CRC database_28_08_24.xlsx"
CRC_df = pd.read_excel(
    crc_file_path,
    sheet_name="Full CRC database ECA",
    header=1,  # Use the second row as column headers
)

# Renaming columns for easier access
CRC_df = CRC_df.rename(
    columns={
        "Name of the country": "Country",
        "Year of report": "Year",
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
        sources_sorted = sources.sort_values(by=sort_col)
        for i in range(len(sources_sorted)):
            source_info = sources_sorted.iloc[i]
            value = source_info.iloc[0]

            # Check if the value is an integer
            if isinstance(value, float) and value.is_integer():
                # Format it as an integer with thousands separators
                formatted_value = "{:,}".format(int(value))
            else:
                # Otherwise, convert the value directly to a string
                formatted_value = str(value)

            country_list.append(f"- {source_info.name[0]}: {formatted_value} ({source_info.name[1]})")
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
    elif country_group == "central_asia":
        options = [{"label": country, "value": country} for country in central_asia]
    elif country_group == "eastern_europe":
        options = [{"label": country, "value": country} for country in eastern_europe]
    elif country_group == "western_europe":
        options = [{"label": country, "value": country} for country in western_europe]
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


# function to check if the config of a certain indicator are only about its dtype and if its nominal data
def only_dtype(config):
    return list(config.keys()) == ["DTYPE", "NOMINAL"]


# function to check if a certain indicator is nominal data
def nominal_data(config):
    return only_dtype(config) and config["NOMINAL"]


def update_indicator_dropdown(indicator_filter, sdg_toggle_state):

    # Function to get indicators for a specific subdomain
    def get_indicators_for_subdomain(subdomain_code):
        for domain_path, domain_details in merged_page_config.items():
            for sub_code, subdomain_info in domain_details['SUBDOMAINS'].items():
                if sub_code == subdomain_code:
                    return [card for card in subdomain_info['CARDS']]
        return []

    # Function to get all indicators for a specific domain
    def get_indicators_for_domain(domain_path):
        indicators = []
        domain_details = merged_page_config.get(domain_path)
        if domain_details:
            for subdomain_info in domain_details['SUBDOMAINS'].values():
                indicators.extend([card for card in subdomain_info['CARDS']])
        return indicators

   # Initialize indicator options and value
    indicator_options = []

    if indicator_filter is not None and indicator_filter != "all":
        # Split the filter to determine if it's a domain or a subdomain
        filter_parts = indicator_filter.split("|")
        if len(filter_parts) == 2:
            # If it's a domain
            if filter_parts[1] in merged_page_config:
                indicators = get_indicators_for_domain(filter_parts[1])
            # If it's a subdomain
            else:
                indicators = get_indicators_for_subdomain(filter_parts[1])
        else:
            indicators = []

        indicator_options = [{"label": card["name"], "value": card["indicator"]} for card in indicators]

    else:
        # Show all indicators if no subdomain or domain is selected
        for domain_details in merged_page_config.values():
            for subdomain_info in domain_details['SUBDOMAINS'].values():
                indicator_options.extend([
                    {"label": card["name"], "value": card["indicator"]}
                    for card in subdomain_info['CARDS']
                ])

    # Filter the indicator options based on SDG toggle state, if active
    if sdg_toggle_state:
        indicator_options = [option for option in indicator_options if 'SDG' in option['label']]

    # Return the sorted indicator options and the first value as default
    return indicator_options, indicator_options[0]["value"] if indicator_options else None


def update_domain_and_subdomain_values(selected_indicator_code):
    """
    Finds and returns the domain page-path, subdomain name, and subdomain code corresponding to a given indicator code.

    Args:
    selected_indicator_code (str): The indicator code to search for.

    Returns:
    tuple: The matching domain page-path, subdomain name, and subdomain code, or (None, None, None) if no match is found.
    """
    for domain_page_path, domain_info in merged_page_config.items():
        for subdomain_code, subdomain_info in domain_info['SUBDOMAINS'].items():
            # Check if the selected indicator code is in any of the subdomain's cards
            if any(card['indicator'] == selected_indicator_code for card in subdomain_info['CARDS']):
                return domain_page_path, subdomain_info['NAME'], subdomain_code  # Return domain page-path, subdomain, and subdomain code

    return None, None, None  # Return None for all if no match is found

def update_domain_with_url(subdomain_code):
    """
    Finds and returns the domain value corresponding to a given subdomain code in the format "{domain_name}|{page_path}".

    Args:
    subdomain_code (str): The subdomain code to search for.

    Returns:
    str or None: The matching domain value in the specified format, or None if no match is found.
    """
    for domain_page_path, domain_info in merged_page_config.items():
        if subdomain_code in domain_info['SUBDOMAINS']:
            domain_name = domain_info['domain_name']  # Assuming this key holds the domain name
            domain_value = f"{domain_name}|{domain_page_path}"
            return domain_value  # Return the domain value in the specified format

    return None  # Return None if no match is found

def get_subdomain_name_by_code(subdomain_code):
    # Iterate over all subdomain items in the data_dict['subdomains'] dictionary
    for subdomain_name, subdomain_info in data_dict["subdomains"].items():
        # Check if the code matches the one we're looking for
        if subdomain_info["code"] == subdomain_code:
            # Return the name of the subdomain if the code matches
            return subdomain_name
    # Return None or an appropriate value if no match is found
    return None


def create_CRM_dropdown(data_dict, only_domain=False):
    dropdown_data = []

    # Add "Select All" option only if only_domain is False
    if not only_domain:
        dropdown_data.append({"label": "Select All", "value": "all"})

    for page_path, domain_details in data_dict.items():
        domain_name = domain_details['domain_name']
        domain_colour = domain_details['domain_colour']
        domain_value = f"{domain_name}|{page_path}"

        # Set the domain name with its color
        dropdown_data.append({
            "label": html.Span(f"{domain_name} Domain", style={'color': domain_colour, 'font-weight': 'bold'}),
            "value": domain_value
        })

        # Add subdomains only if only_domain is False
        if not only_domain:
            for subdomain_code, subdomain_info in domain_details['SUBDOMAINS'].items():
                subdomain_name = subdomain_info['NAME']
                subdomain_value = f"{subdomain_name}|{subdomain_code}"

                # Set the subdomain name with the domain color
                dropdown_data.append({
                    "label": html.Span(f" {subdomain_name}", style={'color': domain_colour}),
                    "value": subdomain_value
                })

    return dropdown_data



# dropdown with domains and subdomains
all_crm_dropdown_options = create_CRM_dropdown(merged_page_config, False)

# dropdown with just domains
domain_dropdown_options = create_CRM_dropdown(merged_page_config, True)

# Define a function to create a popover for a subdomain
def create_subdomain_popover(subdomain, subdomain_description, domain_colour):
    return dbc.Popover(
        dbc.PopoverBody(subdomain_description),
        target=f"popover-target",  # Unique ID for the popover target
        trigger="hover",
        style={
            "color": domain_colour,
            "overflowY": "auto",
            "whiteSpace": "pre-wrap",
            "opacity": 1,
        },
        delay={
            "hide": 0,
            "show": 0,
        },
    )

def update_indicator_dropdown_class(indicator):
    if indicator is None:
        return (
            "crm_dropdown",
            html.P(
                "No indicator selected",
                style={
                    "color": "black",
                    "display": "inline-block",
                    "position": "relative",
                    "marginBottom": "5px",
                    "marginTop": "0px",
                    "font-weight": "bold"
                }
            )
        )

    domain, _, subdomain = update_domain_and_subdomain_values(indicator)
    domain_colour = merged_page_config[domain]['domain_colour']
    subdomain_description = subdomain_descriptions[subdomain]  # Assuming subdomain_descriptions is defined

    # Create popover for the subdomain
    popover = create_subdomain_popover(subdomain, subdomain_description, domain_colour)

    # Map the selected domain to its corresponding CSS class
    if domain and domain in domain_classes:
        return (
            domain_classes[domain],
            html.Div([
                html.P(
                    [
                        html.Span(f"{merged_page_config[domain]['domain_name']}/ "),
                        html.Br(),
                        html.Span(f"{merged_page_config[domain]['SUBDOMAINS'][subdomain]['NAME']}"),
                        html.I(
                            id="popover-target",
                            className="fas fa-info-circle",
                            style={
                                "paddingLeft": "5px",
                            },
                        ),
                        popover 
                    ],
                    style={
                        "color": domain_colour,
                        "display": "inline-block",
                        "position": "relative",
                        "marginBottom": "5px",
                        "marginTop": "0px",
                        "font-weight": "bold"
                    }
                ),
            ])
        )

    return (
        "crm_dropdown",
        html.Div([
            html.P(
                [
                    html.Span(f"{merged_page_config[domain]['domain_name']} Choose indicator/ ", style={"font-weight": "bold"}),
                    html.Br(),
                    html.Span(f"{merged_page_config[domain]['SUBDOMAINS'][subdomain]['NAME']}"),
                    html.I(
                        id="popover-target",
                        className="fas fa-info-circle",
                        style={
                            "paddingLeft": "5px",
                        },
                    ),
                    popover 
                ],
                style={
                    "color": domain_colour,
                    "display": "inline-block",
                    "position": "relative",
                    "marginBottom": "5px",
                    "marginTop": "0px",
                    "font-weight": "bold"
                }
            ),
        ])
    )


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

    start_period = years[0] if years else 2010
    end_period = years[-1] if years else 2024

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

    if "IDX" in data.UNIT_MEASURE.values or any(code in data.CODE.values for code in codes_3_decimals):
        data.OBS_VALUE = data.OBS_VALUE.round(3)
    elif any(code in data.CODE.values for code in codes_1_decimal):
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

    if indicators[0] == 'IM_MCV2':
        data['OBS_FOOTNOTE'] = data['Age_name']
        data['Age_name'] = 'Total'
        data['AGE'] = '_T'

        if latest_data:
            # Group by 'REF_AREA', find the max 'TIME_PERIOD' for each group
            recent_obs = data.groupby('REF_AREA')['TIME_PERIOD'].max().reset_index()

            # Merge the recent observations with the original DataFrame to filter the most recent for each 'REF_AREA'
            data = pd.merge(data, recent_obs, on=['REF_AREA', 'TIME_PERIOD'])

    return data

# path to excel data dictionary
data_dict_content = f"{pathlib.Path(__file__).parent.parent.absolute()}/static/indicator_dictionary_TM_v8.xlsx"

# turning it into a pandas dataframe and read Snapshot sheet from excel data-dictionary
snapshot_df = pd.read_excel(data_dict_content, sheet_name="Snapshot")
snapshot_df.dropna(subset=["Source_name"], inplace=True)
snapshot_df["Source"] = snapshot_df["Source_name"].apply(lambda x: x.split(":")[0])
# read indicators table from excel data-dictionary
df_topics_subtopics = pd.read_excel(data_dict_content, sheet_name="Indicator")
df_topics_subtopics.dropna(subset=["Sub-Domain"], inplace=True)
df_sources = pd.merge(df_topics_subtopics, snapshot_df, how="outer", on=["Code"])
# assign source = TMEE to all indicators without a source since they all come from excel data collection files
df_sources.fillna("TMEE", inplace=True)

df_sources.rename(
    columns={
        "Name_x": "Indicator",
    },
    inplace=True,
)

df_sources["Source_Full"] = df_sources["Source"].apply(
    lambda x: data_sources[x] if not pd.isna(x) and x in data_sources else ""
)

# read source table from excel data-dictionary and merge
source_table_df = pd.read_excel(data_dict_content, sheet_name="Source")
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
    domain_colour = kwargs.get("domain_colour")
    qparams = kwargs.get("query_params")

    sdg_icon_path = f"{request.root_url}assets/sdg_icon.png"
    wheel_icon_path = f"{request.root_url}assets/SOCR_Wheel.png"
    unicef_icon_file_path = f"{request.root_url}assets/UNICEF_ForEveryChild_White_Vertical.png"

    pass_through_params = ["prj=tm"]
    for k, v in qparams.items():
        if k not in ["prj", "page", "hash"]:
            pass_through_params.append(f"{k}={v}")

    home_icon_href = "https://www.transmonee.org/transmonee-dashboard-wheel"

    domain_pages_links = []
    for k, v in domain_pages.items():
        domain_pages_params = pass_through_params + ["page=" + v]
        domain_pages_params = "?" + "&".join(domain_pages_params)
        domain_pages_links.append({"label": k, "value": domain_pages_params})
        if "page" in qparams and v == qparams["page"]:
            current_page_ddl_value = domain_pages_params

    return html.Div(
        [
            dbc.Row(
                children=[
                    dbc.Col(
                        html.Img(id="unicef-icon", src=unicef_icon_file_path, alt="UNICEF logo"),
                        lg=2, md=4, sm=6, xs=12,
                        align="center",
                    ),
                    dbc.Col(
                        html.Div([
                            html.H2("TransMonEE Dashboard", style={'color': 'white', 'marginTop': '0.75em', 'marginBottom': '0.2em','fontWeight': 'bold'}),
                            html.H5("Monitoring child rights data in Europe and Central Asia", style={'color': 'white', 'marginTop': '0.2em'})
                        ]),
                        lg=6, md=8, sm=12,
                    ),
                    dbc.Col(
                        html.Div([
                            dbc.Button(
                                "Explore using the ECA Child Rights Monitoring Framework",
                                id={"type": "nav_buttons", "index": "crm_view"},  
                                className="nav-btn mb-2",
                                active=True,
                                ),
                            dbc.Button(
                                "Search by indicator", 
                                id={"type": "nav_buttons", "index": "indicator_view"}, 
                                className="nav-btn mb-2"
                                ),
                            html.Div(
                                [
                                html.P(
                                        "How to use dashboard",
                                        style={
                                            "display": "inline-block",
                                            "textAlign": "center",
                                            "position": "relative",
                                            "color":"#ffc685",
                                            "font-size": "16px",
                                            "font-weight": "bold",
                                            "text-decoration":"underline",
                                            "text-decoration-color":"#ffc685",
                                            "marginTop":"0px",
                                            "marginBottom":"0px"
                                        },
                                    ),
                                html.I(
                                        id="help-button",
                                        className="fas fa-question-circle",
                                        style={
                                            "display": "flex",
                                            "alignContent": "center",
                                            "flexWrap": "wrap",
                                            "paddingLeft": "5px",
                                            "color":"#ffc685"
                                        },
                                    ),
                                dbc.Popover(
                                        [
                                            dbc.PopoverBody(
                                                help_text,
                                                id="help-popover",
                                            )
                                        ],
                                        target="help-button",
                                        trigger="hover",
                                        className="custom-popover",
                                        style={
                                            "overflowY": "auto",
                                            "whiteSpace": "pre-wrap",
                                            "opacity": 1,
                                            "max-width":"600px"
                                        },
                                        delay={
                                            "hide": 0,
                                            "show": 0,
                                        },
                                    ),
                                ],
                                style={
                                    "display": "inline-flex",
                                    "marginTop":"10px",
                                },
                            ),                             
                        ], style={"display": "flex", "flexDirection": "column", "alignItems": "center"}),
                        lg=4, md=12, align="center",
                    ),
                ],
                justify="between",
                align="center",
                style={"background-color": '#00acef', "minHeight": 200},
            ),
            html.Br(),
            dbc.Row(
                children=[
                    html.Div(
                        [
                            dbc.Row(
                                dbc.Col(
                                    html.Div(
                                        [
                                            # "Select ECA CRM Domain" text and Dropdown
                                            html.Div(
                                                [
                                                    #html.P(
                                                        #"Select ECA CRM Domain:", 
                                                        #style={"margin-bottom": "10px", "display": "inline-block", "margin-right": "10px"}
                                                    #),
                                                    html.Label('Select ECA CRM Domain:', htmlFor='domain-dropdown', 
                                                               style={"display": "inline-block", "margin-right": "10px"}),
                                                    dcc.Dropdown(
                                                        id="domain-dropdown",
                                                        options=domain_dropdown_options,
                                                        value=domain_dropdown_options[0]['value'],
                                                        placeholder="Select a domain",
                                                        optionHeight=55,
                                                        clearable=False,
                                                        className="crm_dropdown domain_dropdown",
                                                        style={"display": "inline-block", "vertical-align": "middle"}
                                                    ),
                                                ],
                                                className="domain-dropdown-container",
                                                style={"display": "inline-flex", "align-items": "center"}
                                            ),
                                            # Wheel icon and "ECA CRM Framework" text
                                            html.Div(
                                                [
                                                    html.Img(id="wheel-icon",src=wheel_icon_path, style={"margin-right": "5px", "margin-left": "15px", "height":"45px"}),
                                                    html.A("Learn about ECA CRM Framework",
                                                        href="https://www.transmonee.org/child-rights-monitoring-framework",
                                                        target="_blank",
                                                        className= "tm-link",
                                                        style={"color": '#374EA2'}
                                                    ),
                                                ],
                                                className="learn-more-container",
                                                style={"display": "inline-flex", "align-items": "center", "color": '#374EA2'}
                                            ),
                                        ],
                                        style={"text-align": "center", "display": "flex", "justify-content": "center", "align-items": "center", "flex-wrap": "wrap"}
                                    ),
                                    width=12
                                ),
                                justify="center",
                                className="responsive-row"
                            ),
                            html.Br(),                            
                            dbc.Row(
                                dbc.Col(
                                    html.Div(
                                        [
                                            dbc.ButtonGroup(
                                                id="themes",
                                                style={"align-self": "center", "flex-wrap": "wrap"}
                                            ),
                                        ],
                                        style={"display": "flex", "justify-content": "center", "align-items": "center", "flex-wrap": "wrap"}
                                    ),
                                    width="auto",
                                ),
                                id="theme-row",
                                className="my-2 theme_buttons",
                                justify="center",
                                align="center",
                                style={"verticalAlign": "center", "display": "flex"}
                            ),
                        ],
                        id = 'crm_framework_view_div',
                        style={"margin-bottom": "15px"}
                    ),
                    html.Br(),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    # Container for Toggle and Image
                                    html.Div(
                                        [
                                            daq.BooleanSwitch(
                                                on=False,
                                                id="sdg-toggle",
                                                #label="Only SDGs",
                                                labelPosition="right",
                                                className="boolean-switch",
                                            ),
                                            html.Img(
                                                id="sdg-icon",
                                                src=sdg_icon_path,
                                                style={"align-self": "center", "margin-top":"2.5em", "height":"50px"}  # Added for vertical alignment
                                            ),
                                            dbc.Popover(
                                                        [
                                                            dbc.PopoverBody(
                                                                "Filter list to show only SDG indicators.",
                                                                id="sdg-popover",
                                                            )
                                                        ],
                                                        target="sdg-icon",
                                                        trigger="hover",
                                                        placement="top",
                                                        style={
                                                            "overflowY": "auto",
                                                            "whiteSpace": "pre-wrap",
                                                            "opacity": 1,
                                                            "minWidth":"200px"
                                                        },
                                                        delay={
                                                            "hide": 0,
                                                            "show": 0,
                                                        },
                                                    ),
                                        ],
                                        style={"display": "flex", "align-items": "center", "justify-content": "right"}  # Flexbox layout
                                    )
                                ],
                                width=12, sm=12, md=2,
                            ),
                            dbc.Col(
                                [
                                    html.P("Filter indicators by ECA CRM Framework (optional)", style={"margin-bottom": "10px"}),
                                    dcc.Dropdown(
                                        id="crm-dropdown",
                                        options=all_crm_dropdown_options,
                                        value="all",  # Default value
                                        placeholder="Select a domain or sub-domain"
                                    ),
                                ],
                                width=12, sm=12, md=4, 
                            ),
                            dbc.Col(
                                [
                                    html.P("Select indicator", style={"margin-bottom": "10px"}),
                                    dcc.Dropdown(
                                        id="indicator-dropdown",
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
                                width=12, sm=12, md=6,
                            ),
                        ],
                        id = "search_by_indicator_div",
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
                                                        label="2000 - 2024",
                                                        id="collapse-years-button",
                                                        className="m-2",
                                                        color="secondary",
                                                        children=[
                                                            dbc.Card(
                                                                dcc.RangeSlider(
                                                                    id="year_slider",
                                                                    min=2000,
                                                                    max=2024,
                                                                    step=1,
                                                                    marks={year: str(year) for year in range(2000, 2025) if year % 2 == 0},
                                                                    value=[2010, 2024],
                                                                ),
                                                                style={"maxHeight": "250px", "minWidth": "500px"},
                                                                className="overflow-auto",
                                                                body=True,
                                                            ),
                                                        ],
                                                    ),
                                                ]),
                                                width="auto",
                                                align="start"
                                            ),
                                            dbc.Col(
                                                html.Div([
                                                    html.P("Country groupings:", style={"margin-bottom": "10px", "margin-top": "5px"}),
                                                    dcc.Dropdown(
                                                        id="country-group",
                                                        options=[
                                                            {"label": "All countries", "value": "all"},
                                                            {"label": "UNICEF programme countries", "value": "unicef"},
                                                            {"label": "EU countries", "value": "eu"},
                                                            {"label": "EFTA countries", "value": "efta"},
                                                            {"label": "EU + EFTA countries", "value": "eu + efta"},
                                                            {"label": "Central Asian countries", "value": "central_asia"},
                                                            {"label": "Eastern European countries", "value": "eastern_europe"},
                                                            {"label": "Western European countries", "value": "western_europe"},
                                                        ],
                                                        value="all",
                                                        placeholder="Select country group",
                                                        style={"width": "250px"},
                                                    ),
                                                ]),
                                                width="auto",
                                                align="start"
                                            ),
                                            dbc.Col(
                                                html.Div([
                                                    html.P("Countries:", style={"margin-bottom": "10px", "margin-top": "5px"}),
                                                    dcc.Dropdown(
                                                        id="country-filter",
                                                        options=[{"label": "Select all", "value": "all_values"}] + [{"label": country, "value": country} for country in all_countries],
                                                        value=["all_values"],
                                                        placeholder="Select country",
                                                        multi=True,
                                                        clearable=False,
                                                        style={"width": "300px"},
                                                    ),
                                                ]),
                                                width="auto",
                                                align="start"
                                            ),
                                            dbc.Col(
                                                html.Div([
                                                    html.P("Choose chart type:", style={"margin-bottom": "10px", "margin-top": "5px"}),
                                                    dbc.RadioItems(
                                                        id={
                                                            "type": "area_types",
                                                            "index": "AIO_AREA",
                                                        },
                                                        className="custom-control-input-crg force-inline-control align-middle",
                                                        inline=True,
                                                    ),
                                                ]),                                                
                                                width="auto",
                                                align="start"
                                            ),
                                        ],
                                        justify="start"
                                    ),
                                ],
                                style={"display":"flex", "justify-content":"center"},
                                lg=12, md=12, sm=12, xs=12
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
                                                                dbc.ButtonGroup(
                                                                    id={"type": "button_group", "index": "AIO_AREA"},
                                                                    vertical=True,
                                                                    style={"marginBottom": "20px", "flexGrow": "1"},
                                                                    class_name="theme_buttons",
                                                                ),
                                                            ],
                                                            style={"maxHeight": "500px", "overflowY": "scroll", "width": "95%", "display": "flex", "flex-direction": "column"},
                                                        ),
                                                    ],
                                                    id='indicator_buttons_div',
                                                    class_name="indic_btn_col",
                                                    width=12, lg=3,
                                                ),                                              
                                                dbc.Col(
                                                    html.Div(
                                                        [
                                                            html.Div(
                                                                [
                                                                    dbc.Row(
                                                                        [
                                                                            # Checkbox and Label
                                                                            dbc.Col(
                                                                                [
                                                                                    dbc.Checkbox(
                                                                                        id='show-average-checkbox',
                                                                                        className='custom-checkbox',
                                                                                        value=True,
                                                                                    ),
                                                                                    html.Label(
                                                                                        'Show average line',
                                                                                        htmlFor='show-average-checkbox',
                                                                                        style={
                                                                                            'margin-top': '3px',
                                                                                            'white-space': 'nowrap',  # Prevent text from breaking into multiple lines
                                                                                        }
                                                                                    ),
                                                                                    html.I(
                                                                                        id="average-icon",
                                                                                        className="fas fa-info-circle",
                                                                                        style={
                                                                                            "display": "flex",
                                                                                            "alignContent": "center",
                                                                                            "flexWrap": "wrap",
                                                                                            "paddingLeft": "5px",
                                                                                        },
                                                                                    ),
                                                                                    dbc.Popover(
                                                                                        [
                                                                                            dbc.PopoverBody(
                                                                                                average_text,
                                                                                                id="average-popover",
                                                                                            )
                                                                                        ],
                                                                                        target="average-icon",
                                                                                        trigger="hover",
                                                                                        className="custom-popover",
                                                                                        style={
                                                                                            "overflowY": "auto",
                                                                                            "whiteSpace": "pre-wrap",
                                                                                            "opacity": 1,
                                                                                        },
                                                                                        delay={
                                                                                            "hide": 0,
                                                                                            "show": 0,
                                                                                        },
                                                                                    ),
                                                                                ],
                                                                                id='average_option',
                                                                                xs=12,  # Full width on small screens
                                                                                sm='auto',  # Auto width on larger screens
                                                                                style={'display': 'flex', 'align-items': 'center'},
                                                                            ),
                                                                            # Radio Items
                                                                            dbc.Col(
                                                                                dbc.RadioItems(
                                                                                    id={
                                                                                        "type": "area_breakdowns",
                                                                                        "index": "AIO_AREA",
                                                                                    },
                                                                                    value="TOTAL",
                                                                                    class_name="force-inline-control responsive-radio-items",
                                                                                    inline=True,
                                                                                ),
                                                                                xs=12,  # Full width on small screens
                                                                                sm='auto',  # Auto width on larger screens
                                                                                className="radio-items-col",
                                                                            ),
                                                                            # Dropdown and label
                                                                            dbc.Col(
                                                                                html.Div([
                                                                                    html.P(
                                                                                        "Select country to highlight:",
                                                                                        style={
                                                                                            "margin-bottom": "10px",
                                                                                            "margin-top": "5px",
                                                                                            "margin-right": "5px",
                                                                                            'white-space': 'nowrap',  # Prevent label wrapping
                                                                                        }
                                                                                    ),
                                                                                    dcc.Dropdown(
                                                                                        id="highlighted_countries",
                                                                                        placeholder="Select a country",
                                                                                        style={"width": "100%"},
                                                                                    ),
                                                                                ], style={"display": "none"}),
                                                                                id="highlight_option",
                                                                                xs=12,  # Full width on small screens
                                                                                sm='auto',  # Auto width on larger screens
                                                                            ),
                                                                        ],
                                                                        style={
                                                                            "display": "flex",
                                                                            "align-items": "center",
                                                                            "flex-wrap": "wrap",  # Enable wrapping of elements when screen is small
                                                                        },
                                                                    )
                                                                ],
                                                                style={
                                                                    "paddingBottom": 10,
                                                                    "display": "flex",
                                                                    "justifyContent": "flex-end",
                                                                },
                                                            ),
                                                            html.Div(
                                                                dcc.Graph(
                                                                    id={
                                                                        "type": "area",
                                                                        "index": "AIO_AREA",
                                                                    },
                                                                    config={
                                                                        "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale"],
                                                                        "displaylogo": False,
                                                                        "autosizable": True,
                                                                        "showTips": True,
                                                                    },
                                                                    responsive=True,
                                                                ),
                                                                style={
                                                                    'overflowX': 'auto',  
                                                                    'minWidth': '700px', 
                                                                    'width': '100%',  
                                                                    'minHeight':'500px',  
                                                                },
                                                                className="graph-scroll" 
                                                            ),
                                                            html.Div([
                                                                html.Div(
                                                                id="aio_area_indicator_link",
                                                                ),
                                                            html.P(
                                                                id="aio_area_graph_info",
                                                                style={"margin-top":"5px"},
                                                                ),
                                                            ]),
                                                            html.Div(
                                                                    [
                                                                        html.P(
                                                                            "Source:  ",
                                                                            style={
                                                                                "display": "inline-block",
                                                                            },
                                                                        ),
                                                                    ],
                                                                id="aio_area_area_info",
                                                            ),                                            
                                                        ],
                                                        style={"overflowX":"scroll"},
                                                    ),
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Col([
                                                                dbc.Card(
                                                                id="indicator_card",
                                                                color="primary",
                                                                outline=True,
                                                                    style={
                                                                    "width": "95%",
                                                                    "marginTop": "15px",
                                                                },
                                                                ),  
                                                        ],
                                                        width=12, md=4
                                                        ),
                                                        dbc.Col([
                                                                html.Div(
                                                                    [
                                                                    html.P(
                                                                            "Indicator definition",
                                                                            style={
                                                                                "display": "inline-block",
                                                                                "textAlign": "center",
                                                                                "position": "relative",
                                                                            },
                                                                        ),
                                                                    html.I(
                                                                            id="definition-button",
                                                                            className="fas fa-info-circle",
                                                                            style={
                                                                                "display": "flex",
                                                                                "alignContent": "center",
                                                                                "flexWrap": "wrap",
                                                                                "paddingLeft": "5px",
                                                                            },
                                                                        ),
                                                                    dbc.Popover(
                                                                            [
                                                                                dbc.PopoverBody(
                                                                                    id="definition-popover",
                                                                                )
                                                                            ],
                                                                            target="definition-button",
                                                                            trigger="hover",
                                                                            style={
                                                                                "overflowY": "auto",
                                                                                "whiteSpace": "pre-wrap",
                                                                                "opacity": 1,
                                                                            },
                                                                            delay={
                                                                                "hide": 0,
                                                                                "show": 0,
                                                                            },
                                                                        ),
                                                                    ],
                                                                    style={
                                                                        "display": "inline-flex",
                                                                        "marginTop":"10px",
                                                                    },
                                                                ),    
                                                                html.P("ECA CRM Framework location: ", style={"marginBottom": "5px", "marginTop": "0px"}),
                                                                html.Div(
                                                                id="domain-text",
                                                                ),                                                                 
                                                            ],
                                                        width=12, md=3
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                html.Div([
                                                                            html.Div([
                                                                                html.Button([
                                                                                        html.Div(
                                                                                                [
                                                                                                    html.P(
                                                                                                        "Countries with data: ",
                                                                                                        style={
                                                                                                            "display": "inline-block",
                                                                                                            "fontWeight": "bold",
                                                                                                        },
                                                                                                    ),
                                                                                                ]
                                                                                        )],
                                                                                    id="aio_area_data_info_rep",
                                                                                    className="country-data-btn",
                                                                                    style={
                                                                                        "padding-right": "15px"
                                                                                    },
                                                                                )],
                                                                            ),
                                                                            dbc.Popover(
                                                                                [
                                                                                    dbc.PopoverHeader(
                                                                                        html.P(
                                                                                            "Countries with data for selected years"
                                                                                        )
                                                                                    ),
                                                                                    dbc.PopoverBody(
                                                                                        id="data-hover-body",
                                                                                        style={
                                                                                            "height": "200px",
                                                                                            "overflowY": "auto",
                                                                                            "whiteSpace": "pre-wrap",
                                                                                        },
                                                                                    ),
                                                                                ],
                                                                                id="data-hover",
                                                                                target="aio_area_data_info_rep",
                                                                                placement="top-start",
                                                                                trigger="hover",
                                                                                style={"opacity": 1},
                                                                            ),
                                                                            html.Div([
                                                                                html.Button([
                                                                                        html.Div(
                                                                                                [
                                                                                                    html.P(
                                                                                                        "Countries without data: ",
                                                                                                        style={
                                                                                                            "display": "inline-block",
                                                                                                            "fontWeight": "bold",
                                                                                                        },
                                                                                                    ),
                                                                                                ]
                                                                                        )],
                                                                                    id="aio_area_data_info_nonrep",
                                                                                    className="country-data-btn",
                                                                                    style={
                                                                                        "padding-right": "15px"
                                                                                    },
                                                                                )],
                                                                            ),
                                                                            dbc.Popover(
                                                                                [
                                                                                    dbc.PopoverHeader(
                                                                                        html.P(
                                                                                            "Countries without data for selected years"
                                                                                        )
                                                                                    ),
                                                                                    dbc.PopoverBody(
                                                                                        id="no-data-hover-body",
                                                                                        style={
                                                                                            "height": "200px",
                                                                                            "overflowY": "auto",
                                                                                            "whiteSpace": "pre-wrap",
                                                                                        },
                                                                                    ),
                                                                                ],
                                                                                id="no-data-hover",
                                                                                target="aio_area_data_info_nonrep",
                                                                                placement="top-start",
                                                                                trigger="hover",
                                                                                style={"opacity": 1},
                                                                            ),
                                                                ],
                                                                style={"width":"100%"},
                                                                ),                                                                                                                                                                                                                        
                                                            ],
                                                        style={"display":"flex", "justifyContent":"center"},
                                                        width=12, md=3
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Row(
                                                                    [
                                                                        html.Button(
                                                                            [
                                                                                html.I(className="fas fa-download", style={'color':'#00acef'}),  # Font Awesome download icon
                                                                                " Download data"
                                                                            ],
                                                                            id="download_btn",
                                                                            className="download_btn custom-download-button",
                                                                        ),
                                                                        dcc.Download(id="download-csv-info"),
                                                                        dbc.Tooltip(
                                                                            "Click to download the data displayed in graph as a CSV file.",
                                                                            target="download_btn",
                                                                            placement="bottom",
                                                                        ),
                                                                    ],
                                                                    align="center",
                                                                ),
                                                            ],
                                                            width=12, md=2
                                                       , )               
                                                    ],
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
                            "index": "AIO_AREA",
                        },
                    )
                )
            ),
            html.Br(),
            dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            html.H5(
                                id="crc-header",
                                children="Committee on the Rights of the Child Recommendations - ",
                                style={
                                    "color": domain_colour,
                                    "marginTop": "10px",
                                    "marginBottom": "0px",
                                },
                            )
                        ),
                        html.Br(),
                        html.Div(
                            className="responsive-container",
                            children=[
                                html.P(
                                    "Select country:",
                                    style={"margin-right": "10px"},
                                ),
                                dcc.Dropdown(
                                    id="country-filter-crc",
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
                                    id="year-filter-crc",
                                    multi=False,
                                    clearable=False,
                                    style={"width": "220px"},
                                ),
                                html.P(
                                    [
                                        html.I(
                                            className="fa-solid fa-arrow-up-right-from-square",
                                            style={
                                                "color": '#374EA2',
                                                "margin-left": "20px",
                                                "margin-right": "5px",
                                            },
                                        ),
                                        html.A(
                                            "Explore CRC Recommendations Dashboard",
                                            href="https://www.transmonee.org/recommendations-committee-rights-child",
                                            target="_blank",
                                            className="tm-link",
                                            style={
                                                "color": '#374EA2',
                                                "text-decoration": "underline",
                                            },
                                        ),
                                    ],
                                    className="crc-link",
                                ),
                            ],
                        ),
                        html.Br(),
                        html.Div(id="crc-accordion"),
                    ],
                ),
                className="crc_card",
            ),
        ],
    )


def make_card(
    suffix,
    indicator_header,
    numerator_pairs,
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
            ],
            style={
                "textAlign": "center",
            },
        ),
    ]

    return card, get_card_popover_body(numerator_pairs)

def available_crc_years(country, indicator):
    if indicator is None:
        return {"label": 'Select sub-domain', "value": None}, None
    domain, _, subdomain = update_domain_and_subdomain_values(indicator)
    subdomain = merged_page_config[domain]['SUBDOMAINS'][subdomain].get("NAME")

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
def generate_accordion_items(recommendations):
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
                            id="crc-{bottleneck.lower()}", children=recs
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
def filter_crc_data(year, country, indicator, text_style):
    if indicator is None:
        return 'Committee on the Rights of the Child Recommendations - Select indicator', {**text_style, 'color': 'black'}, []
    
    domain, subdomain_name, subdomain_code = update_domain_and_subdomain_values(indicator)
    domain_colour = merged_page_config[domain]['domain_colour']

    if subdomain_name is None:
        # Handle the case where the subdomain code doesn't match any subdomain
        return (
            "Committee on the Rights of the Child Recommendations - Select indicator",
            {**text_style, 'color': 'black'},
            f"No related recommendations for this {'sub-domain' if country == 'all_countries' else 'country and sub-domain'}.",
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

    header_text = f"Committee on the Rights of the Child Recommendations - {subdomain_name}"
    # Check if there are no recommendations
    if not any(all_recommendations.values()):
        return header_text, {**text_style}, f"No related recommendations for this {'sub-domain' if country == 'all_countries' else 'country and sub-domain'}."
        
    accordion_items = generate_accordion_items(all_recommendations)
    return header_text, {**text_style, 'color': domain_colour}, dbc.Accordion(accordion_items, active_item="-1")


def indicator_card(
    filters,
    indicator,
    suffix,
    absolute=False,
    average=False,
    min_max=False,
    sex_code=None,
    age_group=None,
    domain_colour="#1cabe2",
):
    try:    
        # extract indicator code if it has a cross-cutting suffix
        base_indicator = get_base_indicator(indicator)
        indicators = [base_indicator] # adapting code as now only one indicator is used

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

        # lbassil: add this check because we are getting an exception where there is no data; i.e. no totals for all dimensions mostly age for the selected indicator
        if filtered_data.empty:
            indicator_header = "No data"
            suffix = ""
            numerator_pairs = []
            return make_card(
                suffix,
                indicator_header,
                numerator_pairs,
                domain_colour,
            )[0]

    except requests.exceptions.HTTPError as err:
        indicator_header = "No data"
        suffix = ""
        numerator_pairs = []
        return make_card(
            suffix,
            indicator_header,
            numerator_pairs,
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

        elif base_indicator == 'PP_SG_NHR_STATUS':
            indicator_sum = ((numerator_pairs.OBS_VALUE == 1).to_numpy().sum())
            sources = numerator_pairs.index.tolist()
            if average and len(sources) > 1:
                indicator_sum = indicator_sum / len(sources)    

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

    if base_indicator in ['HVA_EPI_LHIV_0-19', 'HVA_EPI_INF_RT_0-14', 'HVA_PED_ART_CVG', 'HVA_PMTCT_STAT_CVG', 'HVA_EPI_DTH_ANN_0-19']:
        # add less than sign for HIV indicators
        indicator_header = f"<{indicator_header}"

    if base_indicator == 'PP_SG_NHR_STATUS':
        status_mapping = {0: "No status", 1: "B status", 2: "A status"}
        # Map the OBS_VALUE to the corresponding status
        numerator_pairs["OBS_VALUE"] = numerator_pairs["OBS_VALUE"].map(status_mapping)
    
    if base_indicator in ['CR_UN_CHLD_SALE','CR_UN_CHLD_ARMED','CR_UN_CHLD_COMM', 'CR_SG_STT_FPOS',
                          'CR_SG_STT_NSDSFND', 'CR_SG_STT_NSDSIMPL', 'CR_SG_STT_NSDSFDGVT', 'CR_SG_STT_NSDSFDDNR',
                           'CR_SG_STT_NSDSFDOTHR', 'CR_SG_REG_CENSUSN', 'PP_SG_REG_BRTH90N', 'PP_SG_REG_DETH75N']:
        status_mapping = {1: "Yes", 0: "No"}
        # Map the OBS_VALUE to the corresponding status
        numerator_pairs["OBS_VALUE"] = numerator_pairs["OBS_VALUE"].map(status_mapping)

    return make_card(
        suffix,
        indicator_header,
        numerator_pairs,
        domain_colour,
    )


def download_data(n_clicks, data):
    download_df = pd.DataFrame.from_dict(data)
    download_df["Indicator_name"] = indicator_names[download_df["CODE"].unique()[0]]

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
            category_orders={'Country_name': all_countries},
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
            color_discrete_map={"Yes": "#1CABE2", "No": "#fcba03", "A status": "#3e7c49", "B status": "#e5ae4c", "No status": "#861c3f"},
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
        "trace_options": dict(mode="markers+lines", line=dict(width=1.5), marker=dict(size=4)),
        "layout_options": dict(
            xaxis_title={"standoff": 10},
            margin_t=40,
            margin_b=0,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False), 
            showlegend=False, 
        ),
    },
    "map": {
        "options": dict(
            locations="REF_AREA",
            featureidkey="id",
            color="OBS_VALUE",
            mapbox_style="carto-positron",
            geojson=geo_json_countries,
            zoom=2.2,
            center={"lat": 51.5194, "lon": 35.0},
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

def get_base_indicator(indicator):
    # Cross-cutting suffixes to check
    suffixes = ['-GND', '-ADO', '-ECD', '-DIS', '-SPE']

    # Extract the base indicator code if it contains any of the suffixes
    base_indicator = next((indicator.split(suffix)[0] for suffix in suffixes if indicator.endswith(suffix)), indicator)

    return base_indicator

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
        elif country_group == "central_asia":
            countries = central_asia
        elif country_group == "eastern_europe":
            countries = eastern_europe
        elif country_group == "western_europe":
            countries = western_europe
        else:
            countries = all_countries

    filter_countries = countries
    country_text = f"{len(filter_countries)}"
    # need to include the last selected year as it was exluded in the previous method
    selected_years = list(range(years_slider[0], years_slider[1] + 1))

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

def create_subdomain_buttons(domain_dropdown_value, initial_load, url_search):
    buttons = []
    if domain_dropdown_value:
        _, domain_page_path = domain_dropdown_value.split("|")
        domain_info = merged_page_config.get(domain_page_path)

        # Extract and strip the subdomain code from the URL
        url_subdomain_code = url_search.strip('?prj=tm&page=') if url_search else ''

        if domain_info:
            page_prefix = domain_info.get('page_prefix')

            for subdomain_code, subdomain_info in domain_info['SUBDOMAINS'].items():
                is_active = False
                if initial_load and url_subdomain_code:
                    is_active = (subdomain_code == url_subdomain_code)
                else:
                    # Set the first button as active if it's not the initial load
                    is_first_button = subdomain_code == next(iter(domain_info['SUBDOMAINS']))
                    is_active = is_first_button

                button_id = {"type": "subdomain_button", "index": subdomain_code}
                button = dbc.Button(
                    subdomain_info["NAME"],
                    id=button_id,
                    color=f"{page_prefix}-sub",
                    className="theme mx-1",
                    active=is_active
                )

                buttons.append(button)

    return buttons

def create_indicator_buttons(subdomain_button_active, subdomain_button_ids):
    # Initialize variables
    page_prefix = None
    indicators = []

    # Find the index of the active subdomain button
    active_subdomain_index = next((i for i, active in enumerate(subdomain_button_active) if active), None)

    # If no subdomain is active, return an empty list
    if active_subdomain_index is None:
        return []

    # Get the subdomain code from the id of the active button
    active_subdomain_code = subdomain_button_ids[active_subdomain_index]["index"]

    # Find the domain containing the given subdomain and get indicators
    for domain_path, domain_details in merged_page_config.items():
        for sub_code, sub_details in domain_details['SUBDOMAINS'].items():
            if sub_code == active_subdomain_code:
                page_prefix = domain_details['page_prefix']
                indicators = sub_details['CARDS']
                break
        if page_prefix:
            break

    # Create buttons for each indicator
    indicator_buttons = [
        dbc.Button(
            [
                html.Span(
                    re.sub(r"\s*\(SDG.*\)", " ", indicator['button_name']),
                    className="mr-2"
                ),  # Button label without "(SDG ...)"
                dbc.Badge("SDG", color="primary", className="mr-1")
                if "SDG" in indicator['name']
                else None,
            ],
            id={"type": "indicator-button", "index": indicator['indicator']},
            color=f"{page_prefix}",
            className="my-1",
            active=num == 0  # Set the first indicator button as active
        )
        for num, indicator in enumerate(indicators)
    ]

    return indicator_buttons



def themes(subdomain_code):

    # Load the descriptions from the JSON file
    descriptions_file_path = f"{pathlib.Path(__file__).parent.parent.absolute()}/static/subdomain_descriptions.json"
    with open(descriptions_file_path) as indicator_file:
        descriptions = json.load(indicator_file)

    # Get the description for the current subdomain
    description = descriptions.get(subdomain_code, "")

    return subdomain_code, description

def manage_highlighted_countries(selected_countries, all_values="all_values"):
    """
    Manages the behavior of 'highlighted_countries' dropdown.

    Args:
        selected_countries (list): List of currently selected countries.
        all_values (str): The 'all_values' string that indicates all countries are selected.

    Returns:
        list: Updated list of selected countries.
    """
    # If the dropdown is cleared, set to 'all_values'
    if not selected_countries:
        return [all_values]
    
    # If 'all_values' is the first selection and more than 1 item is selected, remove 'all_values'
    if selected_countries and selected_countries[0] == all_values and len(selected_countries) > 1:
        return [country for country in selected_countries if country != all_values]
    
    # If more than 1 item is selected and 'all_values' is anywhere in the list, keep only 'all_values'
    if len(selected_countries) > 1 and all_values in selected_countries:
        return [all_values]
    
    # Return the selected countries as is if no special conditions are met
    return selected_countries

def breakdown_options(indicator, fig_type):

    if indicator is None:
        return []
    
    if fig_type != "bar":
        return []
    
    # extract indicator code if it has a cross-cutting suffix
    indicator = get_base_indicator(indicator)

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

    if indicator is None:
        return {}, []

    # extract indicator code if it has a cross-cutting suffix
    indicator = get_base_indicator(indicator)

    # Use base_indicator for the rest of the function
    indicator_config = indicators_config.get(indicator, {})


    # Check if the indicator has is string type and give only bar and map as options
    if indicator_config and nominal_data(indicator_config):
        area_types = [
            {"label": "Latest data", "value": "count_bar"},
            {"label": "Map of data", "value": "map"},
        ]
        default_graph = "map"
    else:
        area_types = [
            {"label": "Latest data", "value": "bar"},
            {"label": "Trend data", "value": "line"},
            {"label": "Map of data", "value": "map"},
        ]
        if indicator == 'DM_POP_NETM':
            default_graph = "map"
        else:
            default_graph = "bar"

    return area_types, default_graph


def active_button(_, buttons_id):
    # figure out which button was clicked
    ctx = callback_context
    button_code = eval(ctx.triggered[0]["prop_id"].split(".")[0])["index"]

    # return active properties accordingly
    return [button_code == id_button["index"] for id_button in buttons_id]


def default_compare(compare_options, selected_type, indicator):
    if indicator is None:
        return "TOTAL"
    elif selected_type != "bar":
        return "TOTAL"
    elif len(compare_options) > 1:
        return compare_options[1]["value"]
    else:
        return compare_options[0]["value"]


def average_option(compare, selected_type):
    if selected_type == "bar" and compare == 'TOTAL':
        return { 
                "display": "flex", 
                "align-items": "center"
            }
    else:
        return {
                "display": "none"
            }
    
        
def highlight_option(fig_type, indicator, years_slider, countries, country_group, compare):
    if fig_type == "line" and indicator:
        filters, country_selector, selected_years, country_text = get_filters(
                years_slider,
                countries,
                country_group,
            )
        
        base_indicator = get_base_indicator(indicator)
        
        # make API request to retrieve data
        data = get_data(
            [base_indicator],
            filters["years"],
            filters["countries"],
            "TOTAL",
            {},
            latest_data=False,
        )

        # Extract unique country names from the dataframe
        available_countries = sorted(data['Country_name'].unique())

        return html.Div([
                        html.P(
                            "Select countries to highlight:", 
                            style={"margin-bottom": "10px", "margin-top": "5px", "margin-right": "10px", "white-space": "nowrap"}  # Ensure the text stays on one line
                        ),
                        dcc.Dropdown(
                            id="highlighted_countries",
                            options=[{"label": "Select all", "value": "all_values"}] + [{"label": country, "value": country} for country in available_countries],
                            value=available_countries[0],  # Default country selection
                            placeholder="Select countries",
                            multi=True,
                            clearable=False,
                        ),
                    ], style={
                        "display": "flex",  
                        "align-items": "center",  
                        "flex-wrap": "wrap", 
                        "width": "100%",
                    })
    else:
        return html.Div([
                        html.P("Select country to highlight:", style={"margin-bottom": "10px", "margin-top": "5px", "margin-right": "5px"}),
                        dcc.Dropdown(
                            id="highlighted_countries"
                                ),
                            ], style={"display": "none"})

def aio_area_figure(
    indicator,
    compare,
    years_slider,
    countries,
    country_group,
    average_line,
    highlighted_countries,
    selected_type,
):
    
    filters, country_selector, selected_years, country_text = get_filters(
        years_slider,
        countries,
        country_group,
    )

    if indicator is None:
        return (
            f"{selected_years[0]} - {selected_years[-1]}",
            EMPTY_CHART,
            [
                html.Div(
                    [
                        html.P(
                            "Source:  ",
                            style={
                                "display": "inline-block",
                            },
                        ),
                    ],
                    style={"lineHeight": "0.3"}
                )
            ],
            [],
            html.Div(
                [
                    html.P(
                        "Countries with data: ",
                        style={
                            "display": "inline-block",
                            "fontWeight": "bold",
                        },
                    ),
                ]
            ),
            "",
            html.Div(
                [
                    html.P(
                        "Countries without data: ",
                        style={
                            "display": "inline-block",
                            "fontWeight": "bold",
                        },
                    ),
                ]
            ),
            "",
            [],
            [],
            [],
            "",
        )

    try:
        area = "AIO_AREA"
        domain, _, subdomain = update_domain_and_subdomain_values(indicator)
        domain_colour = merged_page_config[domain]['domain_colour']
        map_colour = merged_page_config[domain]['map_colour']
        default_graph = merged_page_config[domain]['SUBDOMAINS'][subdomain][area].get("default_graph", "line")

        fig_type = selected_type if selected_type else default_graph
        fig_config = graphs_dict[fig_type]
        options = fig_config.get("options")
        traces = fig_config.get("trace_options")
        layout_opt = fig_config.get("layout_options")
        dimension = (
            False
            if fig_type in ["count_bar", "line", "map"] or compare == "TOTAL"
            else compare
        )

        # extract indicator code if it has a cross-cutting suffix
        base_indicator = get_base_indicator(indicator)
        indicator_name = str(indicator_names.get(base_indicator, ""))
        indicator_description = indicator_definitions.get(base_indicator, "")

        # make API request to retrieve data
        data = get_data(
            [base_indicator],
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
                [
                    html.Div(
                        [
                            html.P(
                                "Source:  ",
                                style={
                                    "display": "inline-block",
                                },
                            ),
                        ],
                        style={"lineHeight": "0.3"}
                    )
                ],
                [],
                html.Div(
                    [
                        html.P(
                            "Countries with data: ",
                            style={
                                "display": "inline-block",
                                "fontWeight": "bold",
                            },
                        ),
                    ]
                ),
                "",
                html.Div(
                    [
                        html.P(
                            "Countries without data: ",
                            style={
                                "display": "inline-block",
                                "fontWeight": "bold",
                            },
                        ),
                    ]
                ),
                "",
                [],
                [],
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
        print("HTTP error")
        return (
            f"{selected_years[0]} - {selected_years[-1]}",
            EMPTY_CHART,
            [
                html.Div(
                    [
                        html.P(
                            "Source:  ",
                            style={
                                "display": "inline-block",
                            },
                        ),
                    ],
                    style={"lineHeight": "0.3"}
                )
            ],
            [],
            html.Div(
                [
                    html.P(
                        "Countries with data: ",
                        style={
                            "display": "inline-block",
                            "fontWeight": "bold",
                        },
                    ),
                ]
            ),
            "",
            html.Div(
                [
                    html.P(
                        "Countries without data: ",
                        style={
                            "display": "inline-block",
                            "fontWeight": "bold",
                        },
                    ),
                ]
            ),
            "",
            [],
            [],
            [],
            "",
        )

    data['type'] = 'country'

    # indicator card
    card_key = indicator

    # Retrieve the card configuration for the current indicator
    card_config = next(
        (card for card in merged_page_config[domain]['SUBDOMAINS'][subdomain]['CARDS'] if card['indicator'] == indicator),
        None
    )

    # Retrieve the y-axis title 
    y_axis_title = card_config.get('yaxis', '') 

    # Create the indicator card if configuration is available
    ind_card = (
        []
        if not card_config
        else indicator_card(
            filters,
            card_config["indicator"],
            card_config["suffix"],
            card_config.get("absolute"),
            card_config.get("average"),
            card_config.get("min_max"),
            card_config.get("sex"),
            card_config.get("age"),
            domain_colour,
        )
    )

    # Ensure highlighted_countries is always a list, even if only one country is selected
    if isinstance(highlighted_countries, str):
        highlighted_countries = [highlighted_countries]

    # lbassil: was UNIT_MEASURE
    name = (
        data[data["CODE"] == card_key]["Unit_name"].astype(str).unique()[0]
        if len(data[data["CODE"] == card_key]["Unit_name"].astype(str).unique()) > 0
        else ""
    )
    df_indicator_sources = df_sources[df_sources["Code"] == base_indicator]
    unique_indicator_sources = df_indicator_sources["Source_Full"].unique()

    if data["CODE"].isin(["DM_CHLD_POP", "DM_CHLD_POP_PT", "DM_FRATE_COMP","DM_ADOL_POP", "DM_UFIVE_POP", "DM_BRTS_COMP"]).any():
        source = "Multiple Sources"
    elif len(unique_indicator_sources) > 0:
        source = "; ".join(list(unique_indicator_sources))
    else:
        source = ""

    source_link = (
        df_indicator_sources["Source_Link"].unique()[0]
        if len(unique_indicator_sources) > 0
        and not data["CODE"].isin(["DM_CHLD_POP", "DM_CHLD_POP_PT", "DM_FRATE_COMP", "DM_ADOL_POP", "DM_UFIVE_POP", "DM_BRTS_COMP"]).any()
        else "https://ec.europa.eu/eurostat/cache/metadata/en/demo_pop_esms.htm"
    )

    options["labels"] = DEFAULT_LABELS.copy()
    options["labels"]["OBS_VALUE"] = name

    # set the chart title, wrap the text when the indicator name is too long
    chart_title = textwrap.wrap(
        indicator_name,
        width=74,
    )
    chart_title = "<br>".join(chart_title)

    # Define the desired order of countries
    sorted_data = data.sort_values(by=['OBS_VALUE', 'Country_name'], ascending=[False, True])
    country_order = sorted_data['Country_name'].tolist()

    # set the layout to center the chart title and change its font size and color
    layout = go.Layout(
        title=chart_title,
        title_x=0.5,
        font=dict(family="Verdana", size=11),
        legend=dict(x=1, y=0.5),
        xaxis={
            "categoryorder": "array",
            "categoryarray": country_order,
            "tickangle": -45,
            "tickmode": "linear",
            "tickfont_size": 11,
        },
    )
    if layout_opt:
        layout.update(layout_opt)

    
    if fig_type == "line":
        # Add this code to avoid having decimal year on the x-axis for time series charts
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
    indicator_link = []

    if base_indicator in ['JJ_CHLD_DISAB_COMPLAINT_HHRR', 'PV_SI_COV_DISAB', 'HT_REG_CHLD_DISAB_PROP', 'HT_NEW_REG_CHLD_DISAB_PROP', 
            'PT_CHLD_DISAB_INRESIDENTIAL_PROP', 'PT_CHLD_DISAB_INFAMILY_PROP', 'PV_SI_COV_DISAB']:
        graph_info = "Note: the definition of disability may differ across countries and indicators."
    
    if base_indicator == 'IM_MCV2':
        graph_info = "Note: the reporting age for this indicator differs by country; see footnote in tooltip for reporting age."

    if base_indicator in ['HT_SH_STA_ANEM', 'HT_ANEM_U5']:
        indicator_link =  html.A(
                                "Click here to learn more about WHO's global anaemia estimates.",
                                href="https://www.who.int/data/gho/data/themes/topics/anaemia_in_women_and_children",
                                target="_blank",
                                style={"color": '#374EA2'},
                                className= "indicator-link")
        
    if base_indicator in ['IM_MCV2', 'IM_DTP3', 'IM_PCV3', 'IM_HPV']:
        indicator_link =  html.A(
                                "Click here to explore UNICEF's Immunization Regional Snapshots.",
                                href="https://data.unicef.org/resources/regional-immunization-snapshots/",
                                target="_blank",
                                style={"color": '#374EA2'},
                                className= "indicator-link")
    
    if base_indicator in ['NT_BW_LBW']:
        indicator_link =  html.A(
                                "Click here to learn more about low birthweight prevalence around the world.",
                                href="https://data.unicef.org/resources/low-birthweight-prevalence-interactive-dashboard/",
                                target="_blank",
                                style={"color": '#374EA2'},
                                className= "indicator-link")
    
    if base_indicator in ['CME_MRM0','CME_MRY0','CME_MRY0T4','HT_ADOL_MT', 'CME_SBR']:
        indicator_link =  html.A(
                                "Click here to learn more about child mortality rates around the world.",
                                href="https://childmortality.org/",
                                target="_blank",
                                style={"color": '#374EA2'},
                                className= "indicator-link")
        
    if base_indicator in ['NT_BF_EXBF','NT_BF_EIBF', 'MNCH_SAB']:
        indicator_link =  html.A(
                                "Click here to explore UNICEF's child health and well-being dashboard.",
                                href="https://data.unicef.org/resources/child-health-and-well-being-dashboard/",
                                target="_blank",
                                style={"color": '#374EA2'},
                                className= "indicator-link")
    
    if base_indicator in ['NT_ANT_WHZ_NE2','NT_ANT_HAZ_NE2','NT_ANT_WHZ_PO2']:
        indicator_link =  html.A(
                                "Click here to explore UNICEF-WHO-World Bank: Joint Child Malnutrition Estimates 2023.",
                                href="https://data.unicef.org/resources/unicef-who-world-bank-joint-child-malnutrition-estimates-2023-edition-interactive-dashboard-2/",
                                target="_blank",
                                style={"color": '#374EA2'},
                                className= "indicator-link")

    if base_indicator in ['PT_F_20-24_MRD_U18', 'PT_M_20-24_MRD_U18', 'PT_F_15-19_MRD', 'PT_M_15-19_MRD']:
        indicator_link =  html.A(
                                "Click here to learn more about child marriage around the world.",
                                href="https://childmarriagedata.org/",
                                style={"color": '#374EA2'},
                                target="_blank",
                                className= "indicator-link")

    if base_indicator in ['FT_SP_DYN_ADKL','HT_ADOL_MT','MT_SDG_SUICIDE','HT_CHLD_DAILY_EXER']:
        indicator_link =  html.A(
                                "Click here to explore UNICEF's country profiles for adolescent health.",
                                href="https://data.unicef.org/resources/adolescent-health-dashboards-country-profiles/",
                                style={"color": '#374EA2'},
                                target="_blank",
                                className= "indicator-link")    

    if base_indicator in ['HVA_EPI_LHIV_0-19','HVA_EPI_INF_RT_0-14','HVA_EPI_DTH_ANN_0-19','HVA_PMTCT_MTCT','HVA_PMTCT_STAT_CVG','HVA_PED_ART_CVG']:
        indicator_link =  html.A(
                                "Click here to explore more UNICEF HIV estimates for children.",
                                href="https://data.unicef.org/resources/hiv-estimates-for-children-dashboard/",
                                style={"color": '#374EA2'},
                                target="_blank",
                                className= "indicator-link")         
        
    if indicator in ['ECD_CHLD_36-59M_LMPSL','CME_MRM0-ECD','NT_BF_EXBF-ECD','ECD_CHLD_24-59M_ADLT_SRC','EDUNF_NERA_L1_UNDER1-ECD','ECD_IN_CHILDCARE','ECD_EARLY_EDU-ECD']:
        indicator_link =  html.A(
                                "Click here to explore UNICEF's country profiles for early childhood development.",
                                href="https://nurturing-care.org/resources/country-profiles/",
                                style={"color": '#374EA2'},
                                target="_blank",
                                className= "indicator-link")

    if indicator in ['EDUNF_CR_L1','EDUNF_CR_L2','EDUNF_CR_L3','EDUNF_ROFST_L1_UNDER1','EDUNF_ROFST_L1','EDUNF_ROFST_L2','EDUNF_ROFST_L3','EDUNF_NERA_L1_UNDER1','ECD_EARLY_EDU']:
        indicator_link =  html.A(
                                "Click here to explore UNICEF's education pathway analysis.",
                                href="https://data.unicef.org/resources/how-are-children-progressing-through-school/",
                                style={"color": '#374EA2'},
                                target="_blank",
                                className= "indicator-link")
        

    if base_indicator == 'ECD_CHLD_36-59M_LMPSL' and 'UZB' in data['REF_AREA'].values:
        graph_info = "This indicator has been calculated for Uzbekistan using data for children aged 24-59 months. "
    
    if base_indicator in ['HVA_EPI_LHIV_0-19', 'HVA_EPI_DTH_ANN_0-19']:
        graph_info = "Many countries only report data for this indicator for the 15-19 years age group; this data can be viewed in the age-disaggregated bar chart. "

    if base_indicator == 'PP_SG_NHR_STATUS':
        data.sort_values("OBS_VALUE", ascending=True, inplace=True)
        status_mapping = {0: "No status", 1: "Status B", 2: "Status A"}
        # Map the OBS_VALUE to the corresponding status
        data['Status'] = data['OBS_VALUE'].map(status_mapping)
        graph_info = "Status A: compliant with Paris Principles, Status B: parially compliant with Paris Principles."

    # rename figure_type 'map': 'choropleth' (plotly express)
    if fig_type == "map":
        # map disclaimer text
        graph_info = "Maps on this site do not reflect a position by UNICEF on the legal status of any country or territory or the delimitation of any frontiers. " + graph_info
        fig_type = "choropleth_mapbox"
        if "YES_NO" in data.UNIT_MEASURE.values or base_indicator == 'PP_SG_NHR_STATUS':
            options["color"] = "Status"
            options["color_discrete_map"] = {"Yes": "#1CABE2", "No": "#fcba03", "Status A": "#3e7c49", "Status B": "#e5ae4c", "No status": "#861c3f"}
        else:
            options["color"] = "OBS_VALUE"
            options["color_continuous_scale"] = map_colour
            options["range_color"] = [data.OBS_VALUE.min(), data.OBS_VALUE.max()]

    if fig_type == "bar":
        # turn off number formatting of data labels under 100
        if max(data.OBS_VALUE) <= 100:
            options["text_auto"] = False
        if (data['OBS_VALUE'] == 0).any() and base_indicator != 'PP_SG_NHR_STATUS':
            graph_info =  graph_info + "Zero values not showing on graph; see 'Countries with data' for more information."
    
    if fig_type == "bar" and not dimension:
        # Calculate the average of the 'Value' column
        average_value = data["OBS_VALUE"].mean()

        if "IDX" in data.UNIT_MEASURE.values or any(code in data.CODE.values for code in codes_3_decimals):
            average_value = round(average_value, 3)
        else:
            average_value = round(average_value, 1)

    # removing zero values from bar chart as they cause a bug where countries without data display on chart
    fig_data = data[data['OBS_VALUE'] != 0] if fig_type == "bar" and base_indicator != 'PP_SG_NHR_STATUS' else data

    if fig_type == "line":
        if highlighted_countries and "all_values" not in highlighted_countries:
        # Set lines for all other countries to grey
            options["color_discrete_map"] = {country: "#D3D3D3" for country in data['Country_name'].unique()}
            fig_data = fig_data[~fig_data['Country_name'].isin(highlighted_countries)]
        else:
            options["color"] = "Country_name"
            options["color_discrete_map"] = {}
            options["color_discrete_sequence"] = px.colors.qualitative.Dark24

    if fig_type == "count_bar":
        # change to fig type to generate px.bar
        fig_type = "bar"

    fig = getattr(px, fig_type)(fig_data, **options)
    fig.update_layout(layout)
    # Update layout with title for the Y-axis
    fig.update_layout(yaxis_title=y_axis_title)
    # remove x-axis title but keep space below
    fig.update_layout(xaxis_title="")
    if fig_type == "bar" and not dimension and "YES_NO" not in fig_data.UNIT_MEASURE.values and base_indicator != 'PP_SG_NHR_STATUS':
        fig.update_traces(marker_color=domain_colour)
        fig.update_layout(showlegend=False)
        if average_line and all(unit not in fig_data.UNIT_MEASURE.values for unit in ["PS", "NUMBER"]):
            annotation_text = f"Average: {average_value}% " if any(unit in fig_data.UNIT_MEASURE.values for unit in ["PCNT", "GOV_EXP_EDU"]) else f"Average: {average_value}"
            fig.add_hline(
                y=average_value, 
                line_color="#1cabe2", 
                line_width=2, 
                line_dash="dot",
                annotation_text=annotation_text, 
                annotation_position="top right"
            )
    if fig_type == "line":
        fig.update_traces(**traces)
        # Adding invisible line at zero to ensure the y-axis starts at zero
        fig.add_hline(y=-0.3, line_color="rgba(0,0,0,0)")

        if isinstance(highlighted_countries, str):
            highlighted_countries = [highlighted_countries]

        if highlighted_countries and "all_values" not in highlighted_countries:

            # Set legend visibility for non-highlighted countries to False
            for trace in fig.data:
                if trace.name not in highlighted_countries:
                    trace.showlegend = False
            print("all values not selected")
            print(f"highlighted_countries: {highlighted_countries}")

            # Define a color palette for multiple countries
            color_palette = px.colors.qualitative.Dark24

            # Check if more than one country is selected
            if len(highlighted_countries) > 1:
                fig.update_layout(showlegend=True)  # Show legend when more than one country is selected
                for idx, country in enumerate(highlighted_countries):
                    country_data = data[data['Country_name'] == country]

                    # Only proceed if there's data for the country
                    if not country_data.empty:
                        # Add the line for the highlighted country with different colors
                        fig.add_scatter(
                            x=country_data['TIME_PERIOD'],
                            y=country_data['OBS_VALUE'],
                            mode='lines',
                            line_shape="spline",
                            line=dict(width=2, color=color_palette[idx % len(color_palette)]),
                            name=country,  # Add the country name to the legend
                            showlegend=True
                        )

                        # Add markers for the highlighted country
                        fig.add_scatter(
                            x=country_data['TIME_PERIOD'],
                            y=country_data['OBS_VALUE'],
                            mode='markers',
                            marker=dict(size=5, color=color_palette[idx % len(color_palette)], opacity=0.8),
                            name=country,
                            showlegend=False,
                            customdata=country_data[["OBS_VALUE", "Country_name", "TIME_PERIOD", "OBS_FOOTNOTE", "DATA_SOURCE"]],
                            hovertemplate=(
                                "Time Period: %{x}<br>"
                                "Value: %{customdata[0]}<br>"
                                "Country: %{customdata[1]}<br>"
                                "Footnote: %{customdata[3]}<br>"
                                "Source: %{customdata[4]}<br>"
                                "<extra></extra>"
                            )
                        )

            else:
                # For only one country, keep the blue line and add annotation
                country = highlighted_countries[0]
                country_data = data[data['Country_name'] == country]

                # Only proceed if there's data for the country
                if not country_data.empty:
                    # Add the line for the single highlighted country in blue
                    fig.add_scatter(
                        x=country_data['TIME_PERIOD'],
                        y=country_data['OBS_VALUE'],
                        mode='lines',
                        line_shape="spline",
                        line=dict(width=4, color="#1CABE2"),
                        name=country  # Add the country name to the legend
                    )

                    # Add markers for the single highlighted country
                    fig.add_scatter(
                        x=country_data['TIME_PERIOD'],
                        y=country_data['OBS_VALUE'],
                        mode='markers',
                        marker=dict(size=8, color="#1CABE2", opacity=0.8),
                        name=country,
                        customdata=country_data[["OBS_VALUE", "Country_name", "TIME_PERIOD", "OBS_FOOTNOTE", "DATA_SOURCE"]],
                        hovertemplate=(
                            "Time Period: %{x}<br>"
                            "Value: %{customdata[0]}<br>"
                            "Country: %{customdata[1]}<br>"
                            "Footnote: %{customdata[3]}<br>"
                            "Source: %{customdata[4]}<br>"
                            "<extra></extra>"
                        )
                    )

                    # Add annotation at the end of the highlighted country's line
                    last_time_period = country_data['TIME_PERIOD'].iloc[-1]
                    last_value = country_data['OBS_VALUE'].iloc[-1]

                    fig.add_annotation(
                        x=last_time_period + 0.5,
                        y=last_value + (last_value * 0.05),
                        text=country,
                        showarrow=False,
                        font=dict(size=12, color="#1CABE2"),
                        xanchor="left",
                        yanchor="middle",
                        align="left"
                    )
        else:
            fig.update_layout(showlegend=True)

    fig.update_traces(hovertemplate=hovertext)

    if fig_type == "bar" and "YES_NO" in fig_data.UNIT_MEASURE.values:
        dfs = fig_data.groupby("Status").count()
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
                        "Source:  ",
                        style={
                            "display": "inline-block",
                        },
                    ),
                    html.A(
                        f" {source}",
                        href=source_link,
                        target="_blank",
                        id={
                            "type": "area_sources",
                            "index": "AIO_AREA",
                        },
                        className="tm-link",
                        style={"color": domain_colour,
                               "textDecoration": "underline",
                               "display":"inline-flex"},
                    ),
                ],
                style={"lineHeight": "0.3"}
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
        indicator_link, 
        graph_info,
        json_data,
        indicator_description,
    )
