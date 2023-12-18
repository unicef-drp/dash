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
    update_indicator_dropdown_class,
    create_subdomain_buttons,
    create_indicator_buttons,
)

min_max_card_suffix = "min - max values"


merged_page_config = {
    'child-rights': {
        'domain_name': 'Child Rights Landscape and Governance',
        'page_prefix': 'crg',
        'domain_colour': '#562061',
        'light_domain_colour': '#e7c9ed',
        'dark_domain_colour': '#44194d',
        'map_colour': 'purpor',
        'SUBDOMAINS': {
            'DEM': {
                'NAME': 'Demographics',
                'CARDS': [
                    {
                        'name': 'Child population (0-17 years)',
                        'indicator': 'DM_CHLD_POP',
                        'suffix': 'children',
                        'min_max': 'False',
                    },
                    {
                        'name': 'Percentage of children as a share of the total population',
                        'indicator': 'DM_CHLD_POP_PT',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Number of births',
                        'indicator': 'DM_BRTS',
                        'suffix': 'births',
                        'min_max': 'False',
                    },
                    {
                        'name': 'Total fertility rate',
                        'indicator': 'DM_FRATE_TOT',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Net migration',
                        'indicator': 'DM_POP_NETM',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'DM_CHLD_POP',
                        'DM_CHLD_POP_PT',
                        'DM_BRTS',
                        'DM_FRATE_TOT',
                        'DM_POP_NETM',
                    ],
                    'default_graph': 'bar',
                    'default': 'DM_CHLD_POP',
                },
            },
            'PLE': {
                'NAME': 'Political economy',
                'CARDS': [
                    {
                        'name': 'Human Development Index',
                        'indicator': 'EC_HDI',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Total general government expenditure (% of GDP)',
                        'indicator': 'EC_TEC_GRL_GOV_EXP',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'GDP per capita, PPP (current international $)',
                        'indicator': 'EC_NY_GDP_PCAP_PP_CD',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'GNI per capita, Atlas method (current US$)',
                        'indicator': 'EC_NY_GNP_PCAP_CD',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Gini coefficient of equivalised disposable income (Eurostat estimate)',
                        'indicator': 'PV_GINI_COEF',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Unemployment, modelled ILO estimate (% of total labour force) - SDG 8.5.2',
                        'indicator': 'EC_SL_UEM_TOTL_ZS',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Labour force participation rate',
                        'indicator': 'EC_EAP_RT',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'EC_HDI',
                        'EC_TEC_GRL_GOV_EXP',
                        'EC_NY_GDP_PCAP_PP_CD',
                        'EC_NY_GNP_PCAP_CD',
                        'PV_GINI_COEF',
                        'EC_SL_UEM_TOTL_ZS',
                        'EC_EAP_RT',
                    ],
                    'default_graph': 'bar',
                    'default': 'EC_HDI',
                },
            },
            'CRG': {
                'NAME': 'Child rights governance',
                'CARDS': [
                    {
                        'name': 'Countries with National Human Rights Institutions in compliance with the Paris Principles (A status) - SDG 16.a.1',
                        'indicator': 'PP_SG_NHR_IMPLN',
                        'suffix': 'countries in compliance with the Paris Principles',
                        'min_max': 'False',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'PP_SG_NHR_IMPLN',
                    ],
                    'default_graph': 'map',
                    'default': 'PP_SG_NHR_IMPLN',
                },
            },
            'SPE': {
                'NAME': 'Public spending on children',
                'CARDS': [
                    {
                        'name': 'Government expenditure on education (% of GDP)',
                        'indicator': 'EDU_FIN_EXP_PT_GDP',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Expenditure on pre-primary (% of government expenditure on education)',
                        'indicator': 'EDU_FIN_EXP_L02',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Expenditure on primary (% of government expenditure on education)',
                        'indicator': 'EDU_FIN_EXP_L1',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Domestic general government health expenditure (% of GDP)',
                        'indicator': 'HT_SH_XPD_GHED_GD_ZS',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Domestic general government health expenditure (% of GDP)',
                        'indicator': 'HT_SH_XPD_GHED_GD_ZS',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'General government expenditure by function: Social protection (% of GDP)',
                        'indicator': 'EC_SP_GOV_EXP_GDP',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Expenditure on family-children benefits (% of expenditure on social benefits)',
                        'indicator': 'EC_EXP_FAM_CHLD_EXP',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'EDU_FIN_EXP_PT_GDP',
                        'EDU_FIN_EXP_L02',
                        'EDU_FIN_EXP_L1',
                        'HT_SH_XPD_GHED_GD_ZS',
                        'EC_SP_GOV_EXP_GDP',
                        'EC_EXP_FAM_CHLD_EXP',
                    ],
                    'default_graph': 'bar',
                    'default': 'EDU_FIN_EXP_PT_GDP',
                },
            },
            'DTA': {
                'NAME': 'Data on children',
                'CARDS': [
                    {
                        'name': 'Statistical capacity score',
                        'indicator': 'CR_IQ_SCI_OVRL',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Countries with national statistical legislation exists that complies with the Fundamental Principles of Official Statistics - SDG 17.18.2',
                        'indicator': 'CR_SG_STT_FPOS',
                        'suffix': 'countries',
                        'min_max': 'False',
                    },
                    {
                        'name': '',
                        'indicator': 'CR_SG_STT_CAPTY',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Countries with national statistical plans that are fully funded - SDG 17.18.3',
                        'indicator': 'CR_SG_STT_NSDSFND',
                        'suffix': 'countries',
                        'min_max': 'False',
                    },
                    {
                        'name': 'Countries with national statistical plans that are under implementation - SDG 17.18.3',
                        'indicator': 'CR_SG_STT_NSDSIMPL',
                        'suffix': 'countries',
                        'min_max': 'False',
                    },
                    {
                        'name': 'Countries with national statistical plans with funding from government - SDG 17.18.3',
                        'indicator': 'CR_SG_STT_NSDSFDGVT',
                        'suffix': 'countries',
                        'min_max': 'False',
                    },
                    {
                        'name': 'Countries with national statistical plans with funding from donors - SDG 17.18.3',
                        'indicator': 'CR_SG_STT_NSDSFDDNR',
                        'suffix': 'countries',
                        'min_max': 'False',
                    },
                    {
                        'name': 'Countries with national statistical plans with funding from others - SDG 17.18.3',
                        'indicator': 'CR_SG_STT_NSDSFDOTHR',
                        'suffix': 'countries',
                        'min_max': 'False',
                    },
                    {
                        'name': 'Countries that have conducted at least one population and housing census in the last 10 years - SDG 17.19.2',
                        'indicator': 'CR_SG_REG_CENSUSN',
                        'suffix': 'countries',
                        'min_max': 'False',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'CR_IQ_SCI_OVRL',
                        'CR_SG_STT_FPOS',
                        'CR_SG_STT_CAPTY',
                        'CR_SG_STT_NSDSFND',
                        'CR_SG_STT_NSDSIMPL',
                        'CR_SG_STT_NSDSFDGVT',
                        'CR_SG_STT_NSDSFDDNR',
                        'CR_SG_STT_NSDSFDOTHR',
                        'CR_SG_REG_CENSUSN',
                    ],
                    'default_graph': 'map',
                    'default': 'CR_IQ_SCI_OVRL',
                },
            },
            'REM': {
                'NAME': 'Right to remedy',
                'CARDS': [
                    {
                        'name': 'Number of children (0-17 years) who brought or on whose behalf a complaint was brought by an adult to independent human rights mechanisms during the year',
                        'indicator': 'JJ_CHLD_COMPLAINT_HHRR',
                        'suffix': 'children',
                        'min_max': 'False',
                    },
                    {
                        'name': 'Number of children with disabilities (0-17 years) who brought or on whose behalf a complaint was brought by an adult to independent human rights mechanisms during the year',
                        'indicator': 'JJ_CHLD_DISAB_COMPLAINT_HHRR',
                        'suffix': 'children',
                        'min_max': 'False',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'JJ_CHLD_COMPLAINT_HHRR',
                        'JJ_CHLD_DISAB_COMPLAINT_HHRR',
                    ],
                    'default_graph': 'bar',
                    'default': 'JJ_CHLD_COMPLAINT_HHRR',
                },
            },
        },
    },
    'child-health': {
        'domain_name': 'Health and Nutrition',
        'page_prefix': 'han',
        'domain_colour': '#3e7c49',
        'light_domain_colour': '#e0f0e3',
        'dark_domain_colour': '#24472a',
        'map_colour': 'algae',
        'SUBDOMAINS': {
            'HSM': {
                'NAME': 'Health system',
                'CARDS': [
                    {
                        'name': 'UHC Service Coverage Index - SDG 3.8.1',
                        'indicator': 'HT_UHC_IDX',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Current health expenditure (% of GDP)',
                        'indicator': 'HT_SH_XPD_CHEX_GD_ZS',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Domestic general government health expenditure (% of GDP)',
                        'indicator': 'HT_SH_XPD_GHED_GD_ZS',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Domestic general government health expenditure (% of general government expenditure)',
                        'indicator': 'HT_SH_XPD_GHED_GE_ZS',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Domestic general government health expenditure per capita, PPP (current international $)',
                        'indicator': 'HT_SH_XPD_GHED_PP_CD',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Out-of-pocket expenditure (% of current health expenditure)',
                        'indicator': 'HT_SH_XPD_OOPC_CH_ZS',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Total population covered by public and primary private health insurance',
                        'indicator': 'HT_INS_COV',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'HT_UHC_IDX',
                        'HT_SH_XPD_CHEX_GD_ZS',
                        'HT_SH_XPD_GHED_GD_ZS',
                        'HT_SH_XPD_GHED_GE_ZS',
                        'HT_SH_XPD_GHED_PP_CD',
                        'HT_SH_XPD_OOPC_CH_ZS',
                        'HT_INS_COV',
                    ],
                    'default_graph': 'bar',
                    'default': 'HT_UHC_IDX',
                },
            },
            'MNH': {
                'NAME': 'Maternal, newborn and child health',
                'CARDS': [
                    {
                        'name': 'Neonatal mortality rate - SDG 3.2.2',
                        'indicator': 'CME_MRM0',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Infant mortality rate',
                        'indicator': 'CME_MRY0',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Under-five mortality rate - SDG 3.2.1',
                        'indicator': 'CME_MRY0T4',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of births attended by skilled health personnel - SDG 3.1.2',
                        'indicator': 'MNCH_SAB',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Stillbirth rate',
                        'indicator': 'CME_SBR',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'C-section rate - percentage of deliveries by caesarean section',
                        'indicator': 'MNCH_CSEC',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Prevalence of low birth weight among newborns',
                        'indicator': 'NT_BW_LBW',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'CME_MRM0',
                        'CME_MRY0',
                        'CME_MRY0T4',
                        'MNCH_SAB',
                        'CME_SBR',
                        'MNCH_CSEC',
                        'NT_BW_LBW',
                    ],
                    'default_graph': 'bar',
                    'default': 'CME_MRM0',
                },
            },
            'IMM': {
                'NAME': 'Immunization',
                'CARDS': [
                    {
                        'name': 'Percentage of children who received the 2nd dose of measles-containing vaccine (MCV2) - SDG 3.b.1',
                        'indicator': 'IM_MCV2',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of surviving infants who received the third dose of DTP-containing vaccine (DTP3) - SDG 3.b.1',
                        'indicator': 'IM_DTP3',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of surviving infants who received the third dose of pneumococcal conjugate-containing vaccine (PCV3) - SDG 3.b.1',
                        'indicator': 'IM_PCV3',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of females who received the last dose of human papillomavirus (HPV) vaccine per national schedule - SDG 3.b.1',
                        'indicator': 'IM_HPV',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'IM_MCV2',
                        'IM_DTP3',
                        'IM_PCV3',
                        'IM_HPV',
                    ],
                    'default_graph': 'bar',
                    'default': 'IM_MCV2',
                },
            },
            'NUT': {
                'NAME': 'Nutrition',
                'CARDS': [
                    {
                        'name': 'Percentage of infants (under 6 months) who are exclusively breastfed',
                        'indicator': 'NT_BF_EXBF',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of children born in the last 24 months who were put to the breast within one hour of birth',
                        'indicator': 'NT_BF_EIBF',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Introduction to solid, semi-solid foods (6-8 months)',
                        'indicator': 'NT_CF_ISSSF_FL',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Minimum Acceptable Diet (6-23 months)',
                        'indicator': 'NT_CF_MAD',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Overweight prevalence (weight-for-height >+2 standard deviations from the median of the WHO Child Growth Standards) among children under 5 years of age - SDG 2.2.2',
                        'indicator': 'NT_ANT_WHZ_PO2',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Obesity prevalance among children and adolescents (5-19 years)',
                        'indicator': 'NT_CHLD_OBESITY',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Wasting prevalence (weight-for-height <-2 standard deviations from the median of the WHO Child Growth Standards) among children under 5 years of age - SDG 2.2.2',
                        'indicator': 'NT_ANT_WHZ_NE2',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Stunting prevalence (height-for-age <-2 standard deviations from the median of the WHO Child Growth Standards) among children under 5 years of age - SDG 2.2.2',
                        'indicator': 'NT_ANT_HAZ_NE2',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of women (15-49 years) with anaemia - SDG 2.2.3',
                        'indicator': 'HT_SH_STA_ANEM',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Prevalence of anaemia in children (6–59 months)',
                        'indicator': 'HT_ANEM_U5',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'NT_BF_EXBF',
                        'NT_BF_EIBF',
                        'NT_CF_ISSSF_FL',
                        'NT_CF_MAD',
                        'NT_ANT_WHZ_PO2',
                        'NT_CHLD_OBESITY',
                        'NT_ANT_WHZ_NE2',
                        'NT_ANT_HAZ_NE2',
                        'HT_SH_STA_ANEM',
                        'HT_ANEM_U5',
                    ],
                    'default_graph': 'bar',
                    'default': 'NT_BF_EXBF',
                },
            },
            'ADO': {
                'NAME': 'Adolescent physical, mental and reproductive health',
                'CARDS': [
                    {
                        'name': 'Adolescent birth rate - SDG 3.7.2',
                        'indicator': 'FT_SP_DYN_ADKL',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Adolescent mortality rate',
                        'indicator': 'HT_ADOL_MT',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Suicide mortality rate - SDG 3.4.2',
                        'indicator': 'MT_SDG_SUICIDE',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of 15-year-old students who report doing the WHO-recommended duration of daily exercise',
                        'indicator': 'HT_CHLD_DAILY_EXER',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'FT_SP_DYN_ADKL',
                        'HT_ADOL_MT',
                        'MT_SDG_SUICIDE',
                        'HT_CHLD_DAILY_EXER',
                    ],
                    'default_graph': 'bar',
                    'default': 'FT_SP_DYN_ADKL',
                },
            },
            'HIV': {
                'NAME': 'HIV/AIDS',
                'CARDS': [
                    {
                        'name': 'Estimated number of children  (0-19 years) living with HIV',
                        'indicator': 'HVA_EPI_LHIV_0-19',
                        'suffix': 'estimated children living with HIV',
                        'min_max': 'False',
                    },
                    {
                        'name': 'Estimated incidence rate among children (0-14 years) - SDG 3.3.1',
                        'indicator': 'HVA_EPI_INF_RT_0-14',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Estimated number of annual AIDS-related deaths among children (0-19 years)',
                        'indicator': 'HVA_EPI_DTH_ANN_0-19',
                        'suffix': 'estimated AIDS-related deaths',
                        'min_max': 'False',
                    },
                    {
                        'name': 'Mother-to-child HIV transmission rate',
                        'indicator': 'HVA_PMTCT_MTCT',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of pregnant women presenting at antenatal clinics who were tested for HIV or already knew their HIV positive status',
                        'indicator': 'HVA_PMTCT_STAT_CVG',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of children (0-14 years) living with HIV and receiving antiretroviral therapy',
                        'indicator': 'HVA_PED_ART_CVG',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': '',
                        'indicator': 'HVA_PREV_KNOW',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'HVA_EPI_LHIV_0-19',
                        'HVA_EPI_INF_RT_0-14',
                        'HVA_EPI_DTH_ANN_0-19',
                        'HVA_PMTCT_MTCT',
                        'HVA_PMTCT_STAT_CVG',
                        'HVA_PED_ART_CVG',
                    ],
                    'default_graph': 'bar',
                    'default': 'HVA_EPI_LHIV_0-19',
                },
            },
        },
    },
    'child-education': {
        'domain_name': 'Education, Leisure and Culture',
        'page_prefix': 'edu',
        'domain_colour': '#37568f',
        'light_domain_colour': '#bdcbe5',
        'dark_domain_colour': '#1d2c49',
        'map_colour': 'ice_r',
        'SUBDOMAINS': {
            'ESY': {
                'NAME': 'Education system',
                'CARDS': [
                    {
                        'name': 'Government expenditure on education (% of GDP)',
                        'indicator': 'EDU_FIN_EXP_PT_GDP',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Expenditure on pre-primary (% of government expenditure on education)',
                        'indicator': 'EDU_FIN_EXP_L02',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Expenditure on primary (% of government expenditure on education)',
                        'indicator': 'EDU_FIN_EXP_L1',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': '',
                        'indicator': 'EDU_FIN_EXP_L2',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': '',
                        'indicator': 'EDU_FIN_EXP_L3',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Number of years of free pre-primary education guaranteed in legal framework',
                        'indicator': 'EDU_SDG_FREE_EDU_L02',
                        'suffix': 'countries guaranteeing at least one year',
                        'min_max': 'False',
                    },
                    {
                        'name': 'Number of years of compulsory pre-primary education guaranteed in legal framework',
                        'indicator': 'EDU_SDG_COMP_EDU_L02',
                        'suffix': 'countries guaranteeing at least one year',
                        'min_max': 'False',
                    },
                    {
                        'name': 'Administration of nationally-representative learning assessment in math (end of primary education)',
                        'indicator': 'EDUNF_ADMIN_L1_GLAST_MAT',
                        'suffix': 'countries',
                        'min_max': 'False',
                    },
                    {
                        'name': 'Administration of nationally-representative learning assessment in reading (end of primary education)',
                        'indicator': 'EDUNF_ADMIN_L1_GLAST_REA',
                        'suffix': 'countries',
                        'min_max': 'False',
                    },
                    {
                        'name': 'Administration of nationally-representative learning assessment in math (end of lower secondary education)',
                        'indicator': 'EDUNF_ADMIN_L2_MAT',
                        'suffix': 'countries',
                        'min_max': 'False',
                    },
                    {
                        'name': 'Administration of nationally-representative learning assessment in reading (end of lower secondary education)',
                        'indicator': 'EDUNF_ADMIN_L2_REA',
                        'suffix': 'countries',
                        'min_max': 'False',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'EDU_FIN_EXP_PT_GDP',
                        'EDUNF_ADMIN_L1_GLAST_MAT',
                        'EDUNF_ADMIN_L1_GLAST_REA',
                        'EDUNF_ADMIN_L2_MAT',
                        'EDUNF_ADMIN_L2_REA',
                        'EDU_SDG_FREE_EDU_L02',
                        'EDU_SDG_COMP_EDU_L02',
                    ],
                    'default_graph': 'bar',
                    'default': 'EDU_FIN_EXP_PT_GDP',
                },
            },
            'EPA': {
                'NAME': 'Education access and participation',
                'CARDS': [
                    {
                        'name': 'Primary education completion rate - SDG 4.1.2.',
                        'indicator': 'EDUNF_CR_L1',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Lower secondary education completion rate -  SDG 4.1.2',
                        'indicator': 'EDUNF_CR_L2',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Upper secondary education completion rate -  SDG 4.1.2',
                        'indicator': 'EDUNF_CR_L3',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Out-of-school rate for children one year younger than the official entry age to primary education',
                        'indicator': 'EDUNF_ROFST_L1_UNDER1',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Out-of-school rate for children of primary school age',
                        'indicator': 'EDUNF_ROFST_L1',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Out-of-school rate for adolescents of lower secondary school age',
                        'indicator': 'EDUNF_ROFST_L2',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Out-of-school rate for youth of upper secondary school age',
                        'indicator': 'EDUNF_ROFST_L3',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Participation in organized learning (adjusted net enrolment rate, one year before official primary entry age - administrative data) - SDG 4.2.2',
                        'indicator': 'EDUNF_NERA_L1_UNDER1',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Pupils from age 3 to the starting age of compulsory education at primary level',
                        'indicator': 'ECD_EARLY_EDU',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of primary schools with access to adapted infrastructure and materials for students with disabilities - SDG 4.a.1',
                        'indicator': 'EDU_SDG_SCH_L1',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of lower secondary schools with access to adapted infrastructure and materials for students with disabilities - SDG 4.a.1',
                        'indicator': 'EDU_SDG_SCH_L2',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of upper secondary schools with access to adapted infrastructure and materials for students with disabilities - SDG 4.a.1',
                        'indicator': 'EDU_SDG_SCH_L3',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': '',
                        'indicator': 'EDUNF_ESL_L1',
                        'suffix': 'children',
                        'min_max': 'False',
                    },
                    {
                        'name': 'Percentage of early leavers from education and training',
                        'indicator': 'EDAT_LFSE_14',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Participation rate of youth and adults in formal and non-formal education and training - SDG 4.3.1',
                        'indicator': 'EDU_SDG_PRYA',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'EDUNF_CR_L1',
                        'EDUNF_CR_L2',
                        'EDUNF_CR_L3',
                        'EDUNF_ROFST_L1_UNDER1',
                        'EDUNF_ROFST_L1',
                        'EDUNF_ROFST_L2',
                        'EDUNF_ROFST_L3',
                        'EDUNF_NERA_L1_UNDER1',
                        'ECD_EARLY_EDU',
                        'EDU_SDG_SCH_L1',
                        'EDU_SDG_SCH_L2',
                        'EDU_SDG_SCH_L3',
                        'EDAT_LFSE_14',
                        'EDU_SDG_PRYA',
                    ],
                    'default_graph': 'bar',
                    'default': 'EDUNF_CR_L1',
                },
            },
            'EQU': {
                'NAME': 'Learning quality and skills',
                'CARDS': [
                    {
                        'name': 'Percentage of 15-year-olds achieving low scores in mathematics',
                        'indicator': 'EDU_PISA_LOW_ACHIEVE_MAT',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of 15-year-olds achieving low scores in reading',
                        'indicator': 'EDU_PISA_LOW_ACHIEVE_REA',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of 15-year-olds achieving low scores in science',
                        'indicator': 'EDU_PISA_LOW_ACHIEVE_SCI',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of children at the end of lower secondary education reaching minimum proficiency in math - SDG 4.1.1',
                        'indicator': 'EDU_SDG_STU_L2_GLAST_MAT',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of children at the end of lower secondary education reaching minimum proficiency in reading - SDG 4.1.1',
                        'indicator': 'EDU_SDG_STU_L2_GLAST_REA',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of youth (15-24 years) not in education, employment or training - SDG 8.6.1 ',
                        'indicator': 'EDU_SDG_YOUTH_NEET',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'EDU_PISA_LOW_ACHIEVE_MAT',
                        'EDU_PISA_LOW_ACHIEVE_REA',
                        'EDU_PISA_LOW_ACHIEVE_SCI',
                        'EDU_SDG_STU_L2_GLAST_MAT',
                        'EDU_SDG_STU_L2_GLAST_REA',
                        'EDU_SDG_YOUTH_NEET',
                    ],
                    'default_graph': 'bar',
                    'default': 'EDU_PISA_LOW_ACHIEVE_MAT',
                },
            },
            'ELE': {
                'NAME': 'Leisure and culture',
                'CARDS': [
                    {
                        'name': 'Percentage of 15-year-old students who watch TV or play video games, before or after school',
                        'indicator': 'PP_ADOL_TVGM',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of 15-year-old students who use the internet and social networks, before or after school',
                        'indicator': 'PP_ADOL_INET',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'PP_ADOL_TVGM',
                        'PP_ADOL_INET',
                    ],
                    'default_graph': 'bar',
                    'default': 'PP_ADOL_TVGM',
                },
            },
        },
    },
    'child-protection': {
        'domain_name': 'Family Environment and Protection',
        'page_prefix': 'chp',
        'domain_colour': '#e5ae4c',
        'light_domain_colour': '#f4daaf',
        'dark_domain_colour': '#9c6b16',
        'map_colour': 'YlOrBr',
        'SUBDOMAINS': {
            'VIO': {
                'NAME': 'Violence against children and women',
                'CARDS': [
                    {
                        'name': 'Percentage of children (1-14 years) who experienced any physical punishment and/or psychological aggression by caregivers - SDG 16.2.1',
                        'indicator': 'PT_CHLD_1-14_PS-PSY-V_CGVR',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of adults who think that physical punishment is necessary to raise/educate children',
                        'indicator': 'PT_ADLT_PS_NEC',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of ever-partnered women and girls (15 years and older) subjected to physical, sexual or psychological violence by a current or former intimate partner in the previous 12 months - SDG 5.2.1',
                        'indicator': 'PT_F_GE15_PS-SX-EM_V_PTNR_12MNTH',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of women (18-29 years) who experienced sexual violence by age 18 years - SDG 16.2.3',
                        'indicator': 'PT_F_18-29_SX-V_AGE-18',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of students (13-15 years) who reported being bullied on 1 or more days in the past 30 days',
                        'indicator': 'PT_ST_13-15_BUL_30-DYS',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Number of child victims of violence (0-17 years) registered by child/social welfare authorities during the year',
                        'indicator': 'PT_CHLD_VIOLENCE_WELFARE',
                        'suffix': 'child victims of violence',
                        'min_max': 'False',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'PT_CHLD_1-14_PS-PSY-V_CGVR',
                        'PT_ADLT_PS_NEC',
                        'PT_F_GE15_PS-SX-EM_V_PTNR_12MNTH',
                        'PT_F_18-29_SX-V_AGE-18',
                        'PT_ST_13-15_BUL_30-DYS',
                        'PT_CHLD_VIOLENCE_WELFARE',
                    ],
                    'default_graph': 'bar',
                    'default': 'PT_CHLD_1-14_PS-PSY-V_CGVR',
                },
            },
            'CPC': {
                'NAME': 'Children in alternative care',
                'CARDS': [
                    {
                        'name': 'Rate of children (0-17 years) in formal alternative care at the end of the year (per 100,000)',
                        'indicator': 'PT_CHLD_INFORMALCARE_RATE',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Rate of children (0-17 years) in formal residential care at the end of the year (per 100,000)',
                        'indicator': 'PT_CHLD_INRESIDENTIAL_RATE_B',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Rate of children (0-17 years) in formal family-based care at the end of the year (per 100,000)',
                        'indicator': 'PT_CHLD_INCARE_FOSTER_RATE',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Rate of formal adoption of children (0-17 years) during the year (per 100,000)',
                        'indicator': 'PT_CHLD_ADOPTION_RATE',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'PT_CHLD_INFORMALCARE_RATE',
                        'PT_CHLD_INRESIDENTIAL_RATE_B',
                        'PT_CHLD_INCARE_FOSTER_RATE',
                        'PT_CHLD_ADOPTION_RATE',
                    ],
                    'default_graph': 'bar',
                    'default': 'PT_CHLD_INFORMALCARE_RATE',
                },
            },
            'JUS': {
                'NAME': 'Justice for children',
                'CARDS': [
                    {
                        'name': 'Rate of children (0-17 years) in detention at the end of the year (per 100,000)',
                        'indicator': 'JJ_CHLD_DETENTION_RATE',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Rate of children (0-17 years) in pre-sentence detention at the end of the year (per 100,000)',
                        'indicator': 'JJ_CHLD_PRE_SENTENCE_DETENTION_RATE',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Rate of children (0-17 years) in post-sentence detention at the end of the year (per 100,000)',
                        'indicator': 'JJ_CHLD_POST_SENTENCE_DETENTION_RATE',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Rate of children (0-17 years) detained in pre-sentence detention during the year (per 100,000)',
                        'indicator': 'JJ_CHLD_ENTER_PRE_SENTENCE_DETENTION_RATE',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of children (0-17 years) sentenced to custodial sentences during the year',
                        'indicator': 'JJ_CHLD_CUSTODIAL_SENTENCE_PROP',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of children (0-17 years) sentenced with alternative measures during the year',
                        'indicator': 'JJ_CHLD_ALTERNATIVE_SENTENCE_PROP',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Rate of child victims of crime (0-17 years) registered by the police during the year (per 100,000)',
                        'indicator': 'JJ_CHLD_VICTIM_CRIME_RATE',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Rate of child witnesses of crime (0-17 years) registered by the police during the year (per 100,000)',
                        'indicator': 'JJ_CHLD_WITNESS_CRIME_RATE',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Unsentenced detainees as a proportion of overall prison population - SDG 16.3.2',
                        'indicator': 'JJ_VC_PRS_UNSNT',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'JJ_CHLD_DETENTION_RATE',
                        'JJ_CHLD_PRE_SENTENCE_DETENTION_RATE',
                        'JJ_CHLD_POST_SENTENCE_DETENTION_RATE',
                        'JJ_CHLD_ENTER_PRE_SENTENCE_DETENTION_RATE',
                        'JJ_CHLD_CUSTODIAL_SENTENCE_PROP',
                        'JJ_CHLD_ALTERNATIVE_SENTENCE_PROP',
                        'JJ_CHLD_VICTIM_CRIME_RATE',
                        'JJ_CHLD_WITNESS_CRIME_RATE',
                        'JJ_VC_PRS_UNSNT',
                    ],
                    'default_graph': 'bar',
                    'default': 'JJ_CHLD_DETENTION_RATE',
                },
            },
            'MAR': {
                'NAME': 'Child marriage and other harmful practices',
                'CARDS': [
                    {
                        'name': 'Percentage of women (20-24 years) married or in union before age 18 - SDG 5.3.1.',
                        'indicator': 'PT_F_20-24_MRD_U18',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of men (20-24 years) married or in union before age 18',
                        'indicator': 'PT_M_20-24_MRD_U18',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of girls (15-19 years) who are currently married or in union',
                        'indicator': 'PT_F_15-19_MRD',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of boys (15-19 years) who are currently married or in union',
                        'indicator': 'PT_M_15-19_MRD',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'PT_F_20-24_MRD_U18',
                        'PT_M_20-24_MRD_U18',
                        'PT_F_15-19_MRD',
                        'PT_M_15-19_MRD',
                    ],
                    'default_graph': 'bar',
                    'default': 'PT_F_20-24_MRD_U18',
                },
            },
            'LAB': {
                'NAME': 'Child exploitation',
                'CARDS': [
                    {
                        'name': 'Percentage of children (5-17 years) engaged in child labour (economic activities and household chores) - SDG 8.7.1',
                        'indicator': 'PT_CHLD_5-17_LBR_ECON-HC',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of children (5-17 years) engaged in child labour (economic activities)',
                        'indicator': 'PT_CHLD_5-17_LBR_ECON',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'PT_CHLD_5-17_LBR_ECON-HC',
                        'PT_CHLD_5-17_LBR_ECON',
                    ],
                    'default_graph': 'bar',
                    'default': 'PT_CHLD_5-17_LBR_ECON-HC',
                },
            },
        },
    },
    'child-participation': {
        'domain_name': 'Participation and Civil Rights',
        'page_prefix': 'par',
        'domain_colour': '#861c3f',
        'light_domain_colour': '#eca7be',
        'dark_domain_colour': '#541228',
        'map_colour': 'Brwnyl',
        'SUBDOMAINS': {
            'REG': {
                'NAME': 'Birth registration and identity',
                'CARDS': [
                    {
                        'name': 'Percentage of children whose births have been registered with a civil authority - SDG 16.9.1',
                        'indicator': 'PT_CHLD_Y0T4_REG',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Countries with birth registration data that are at least 90 percent complete - SDG 17.19.2',
                        'indicator': 'PP_SG_REG_BRTH90N',
                        'suffix': 'countries',
                        'min_max': 'False',
                    },
                    {
                        'name': 'Countries with death registration data that are at least 75 percent complete - SDG 17.19.2',
                        'indicator': 'PP_SG_REG_DETH75N',
                        'suffix': 'countries',
                        'min_max': 'False',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'PT_CHLD_Y0T4_REG',
                        'PP_SG_REG_BRTH90N',
                        'PP_SG_REG_DETH75N',
                    ],
                    'default_graph': 'bar',
                    'default': 'PT_CHLD_Y0T4_REG',
                },
            },
            'ICT': {
                'NAME': 'Information, internet and protection of privacy',
                'CARDS': [
                    {
                        'name': 'Internet users per 100 inhabitants - SDG 17.8.1',
                        'indicator': 'PP_IT_USE_ii99',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of youth and adults with ICT skill: writing a computer program using a specialized programming language - SDG 4.4.1',
                        'indicator': 'PP_SE_ADT_ACTS_PRGM',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of youth and adults with ICT skill: sending e-mails with attached files - SDG 4.4.1',
                        'indicator': 'PP_SE_ADT_ACTS_ATCH',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of youth and adults with ICT skill: finding, downloading, installing and configuring software - SDG 4.4.1',
                        'indicator': 'PP_SE_ADT_ACTS_SFWR',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of population who used the internet in the last 3 months and managed access to their personal data',
                        'indicator': 'ICT_PERSONAL_DATA',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of population who limited their personal internet activities in the last 12 months due to security concerns',
                        'indicator': 'ICT_SECURITY_CONCERN',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'PP_IT_USE_ii99',
                        'PP_SE_ADT_ACTS_PRGM',
                        'PP_SE_ADT_ACTS_ATCH',
                        'PP_SE_ADT_ACTS_SFWR',
                        'ICT_PERSONAL_DATA',
                        'ICT_SECURITY_CONCERN',
                    ],
                    'default_graph': 'bar',
                    'default': 'PP_IT_USE_ii99',
                },
            },
        },
    },
    'child-poverty': {
        'domain_name': 'Poverty and Social Protection',
        'page_prefix': 'pov',
        'domain_colour': '#4c8cbb',
        'light_domain_colour': '#c0d7e7',
        'dark_domain_colour': '#1c374a',
        'map_colour': 'GnBu',
        'SUBDOMAINS': {
            'SPS': {
                'NAME': 'Social protection system',
                'CARDS': [
                    {
                        'name': 'Percentage of population covered by at least one social protection benefit - SDG 1.3.1',
                        'indicator': 'PV_SI_COV_BENFTS',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of children/households receiving child/family cash benefit - SDG 1.3.1',
                        'indicator': 'PV_SI_COV_CHLD',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of mothers with newborns receiving maternity cash benefit - SDG 1.3.1',
                        'indicator': 'PV_SI_COV_MATNL',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of population with severe disabilities receiving disability cash benefit - SDG 1.3.1',
                        'indicator': 'PV_SI_COV_DISAB',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of unemployed persons receiving unemployment cash benefit - SDG 1.3.1',
                        'indicator': 'PV_SI_COV_UEMP',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of vulnerable population receiving social assistance cash benefit - SDG 1.3.1',
                        'indicator': 'PV_SI_COV_VULN',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of poor population receiving social assistance cash benefit - SDG 1.3.1',
                        'indicator': 'PV_SI_COV_POOR',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Expenditure on family-children benefits (% of expenditure on social benefits)',
                        'indicator': 'EC_EXP_FAM_CHLD_EXP',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'PV_SI_COV_BENFTS',
                        'PV_SI_COV_CHLD',
                        'PV_SI_COV_MATNL',
                        'PV_SI_COV_DISAB',
                        'PV_SI_COV_UEMP',
                        'PV_SI_COV_VULN',
                        'PV_SI_COV_POOR',
                        'EC_EXP_FAM_CHLD_EXP',
                    ],
                    'default_graph': 'bar',
                    'default': 'PV_SI_COV_BENFTS',
                },
            },
            'MAT': {
                'NAME': 'Child poverty and material deprivation',
                'CARDS': [
                    {
                        'name': 'Poverty headcount ratio at $6.85 a day (2017 PPP)',
                        'indicator': 'SI_POV_UMIC',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of population living below the national poverty line - SDG 1.2.1',
                        'indicator': 'PV_SDG_SI_POV_NAHC',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'People at risk of poverty or social exclusion',
                        'indicator': 'PV_AROPE',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Severe material and social deprivation rate',
                        'indicator': 'PV_SEV_MAT_SOC_DPRT',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'At-risk-of-poverty rate by threshold: 60% of national median equivalized disposable income after social transfers',
                        'indicator': 'PV_AROPRT',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'People living in households with very low work intensity',
                        'indicator': 'PV_LOW_WORK',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Share of households with dependent children with inability to afford a meal with protein every second day',
                        'indicator': 'PV_INABLE_PROTEIN',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'SI_POV_UMIC',
                        'PV_SDG_SI_POV_NAHC',
                        'PV_AROPE',
                        'PV_SEV_MAT_SOC_DPRT',
                        'PV_AROPRT',
                        'PV_LOW_WORK',
                        'PV_INABLE_PROTEIN',
                    ],
                    'default_graph': 'bar',
                    'default': 'SI_POV_UMIC',
                },
            },
            'WSH': {
                'NAME': 'Water and sanitation',
                'CARDS': [
                    {
                        'name': 'Percentage of population using safely managed drinking water services - SDG 6.1.1',
                        'indicator': 'WS_PPL_W-SM',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of population using safely managed sanitation services - SDG 6.1.2',
                        'indicator': 'WS_PPL_S-SM',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of population having neither a bath, nor a shower, nor indoor flushing toilet in their household',
                        'indicator': 'HT_NO_BTH_SHW_FLSH',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'WS_PPL_W-SM',
                        'WS_PPL_S-SM',
                        'HT_NO_BTH_SHW_FLSH',
                    ],
                    'default_graph': 'bar',
                    'default': 'WS_PPL_W-SM',
                },
            },
        },
    },
    'child-cross-cutting': {
        'domain_name': 'Cross-Cutting',
        'page_prefix': 'cci',
        'domain_colour': '#ec5e24',
        'light_domain_colour': '#f4d5c0',
        'dark_domain_colour': '#903717',
        'map_colour': 'coral',
        'SUBDOMAINS': {
            'GND': {
                'NAME': 'Gender',
                'CARDS': [
                    {
                        'name': 'Gender Development Index',
                        'indicator': 'EC_GDI',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Gender Inequality Index',
                        'indicator': 'EC_GII',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Adolescent birth rate - SDG 3.7.2',
                        'indicator': 'FT_SP_DYN_ADKL',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Adjusted gender parity index for upper secondary education completion rate - SDG 4.5.1',
                        'indicator': 'EDU_SE_AGP_CPRA_L3',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Adjusted gender parity index for students at the end of lower secondary education achieving a minimum proficiency level in mathematics - SDG 4.5.1',
                        'indicator': 'EDU_SE_TOT_GPI_L2_MAT',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Adjusted gender parity index for students at the end of lower secondary education achieving a minimum proficiency level in reading - SDG 4.5.1',
                        'indicator': 'EDU_SE_TOT_GPI_L2_REA',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of children (1-14 years) who experienced any physical punishment and/or psychological aggression by caregivers - SDG 16.2.1',
                        'indicator': 'PT_CHLD_1-14_PS-PSY-V_CGVR',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of ever-partnered women and girls (15 years and older) subjected to physical, sexual or psychological violence by a current or former intimate partner in the previous 12 months - SDG 5.2.1',
                        'indicator': 'PT_F_GE15_PS-SX-EM_V_PTNR_12MNTH',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of girls (15-19 years) who are currently married or in union',
                        'indicator': 'PT_F_15-19_MRD',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of women (20-24 years) married or in union before age 18 - SDG 5.3.1.',
                        'indicator': 'PT_F_20-24_MRD_U18',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'EC_GDI',
                        'EC_GII',
                        'FT_SP_DYN_ADKL',
                        'EDU_SE_AGP_CPRA_L3',
                        'EDU_SE_TOT_GPI_L2_MAT',
                        'EDU_SE_TOT_GPI_L2_REA',
                        'PT_CHLD_1-14_PS-PSY-V_CGVR',
                        'PT_F_GE15_PS-SX-EM_V_PTNR_12MNTH',
                        'PT_F_15-19_MRD',
                        'PT_F_20-24_MRD_U18',
                    ],
                    'default_graph': 'bar',
                    'default': 'EC_GDI',
                },
            },
            'DIS': {
                'NAME': 'Disability',
                'CARDS': [
                    {
                        'name': 'Percentage of children (0-17 years) registered as having disabilities at the end of the year',
                        'indicator': 'HT_REG_CHLD_DISAB_PROP',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of children (0-17 years) newly registered as having disabilities during the year',
                        'indicator': 'HT_NEW_REG_CHLD_DISAB_PROP',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of primary schools with access to adapted infrastructure and materials for students with disabilities - SDG 4.a.1',
                        'indicator': 'EDU_SDG_SCH_L1',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of lower secondary schools with access to adapted infrastructure and materials for students with disabilities - SDG 4.a.1',
                        'indicator': 'EDU_SDG_SCH_L2',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of upper secondary schools with access to adapted infrastructure and materials for students with disabilities - SDG 4.a.1',
                        'indicator': 'EDU_SDG_SCH_L3',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of children with disabilities (0-17 years) in formal residential care at the end of the year',
                        'indicator': 'PT_CHLD_DISAB_INRESIDENTIAL_PROP',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of children with disabilities (0-17 years) in formal family-based care at the end of the year',
                        'indicator': 'PT_CHLD_DISAB_INFAMILY_PROP',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of children with disabilities (0-17 years) in formal foster care of the total number of children in formal family-based care at the end of the year',
                        'indicator': 'PT_CHLD_DISAB_INFOSTER_PROP',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of population with severe disabilities receiving disability cash benefit - SDG 1.3.1',
                        'indicator': 'PV_SI_COV_DISAB',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'HT_REG_CHLD_DISAB_PROP',
                        'HT_NEW_REG_CHLD_DISAB_PROP',
                        'EDU_SDG_SCH_L1',
                        'EDU_SDG_SCH_L2',
                        'EDU_SDG_SCH_L3',
                        'PT_CHLD_DISAB_INRESIDENTIAL_PROP',
                        'PT_CHLD_DISAB_INFAMILY_PROP',
                        'PT_CHLD_DISAB_INFOSTER_PROP',
                        'PV_SI_COV_DISAB',
                    ],
                    'default_graph': 'bar',
                    'default': 'HT_REG_CHLD_DISAB_PROP',
                },
            },
            'ECD': {
                'NAME': 'Early childhood development',
                'CARDS': [
                    {
                        'name': '4.2.1. Percentage of children (36-59 months) developmentally on track in at least 3 of the 4 following domains: literacy-numeracy, physical, social-emotional and learning',
                        'indicator': 'ECD_CHLD_36-59M_LMPSL',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Neonatal mortality rate - SDG 3.2.2',
                        'indicator': 'CME_MRM0',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of infants (under 6 months) who are exclusively breastfed',
                        'indicator': 'NT_BF_EXBF',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of children (36-59 months) with whom any adult household member has engaged in 4 or more activities to provide early stimulation and responsive care in the last 3 days',
                        'indicator': 'ECD_CHLD_24-59M_ADLT_SRC',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Participation in organized learning (adjusted net enrolment rate, one year before official primary entry age - administrative data) - SDG 4.2.2',
                        'indicator': 'EDUNF_NERA_L1_UNDER1',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Children aged less than 3 years in formal childcare',
                        'indicator': 'ECD_IN_CHILDCARE',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Pupils from age 3 to the starting age of compulsory education at primary level',
                        'indicator': 'ECD_EARLY_EDU',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'ECD_CHLD_36-59M_LMPSL',
                        'CME_MRM0',
                        'NT_BF_EXBF',
                        'ECD_CHLD_24-59M_ADLT_SRC',
                        'EDUNF_NERA_L1_UNDER1',
                        'ECD_IN_CHILDCARE',
                        'ECD_EARLY_EDU',
                    ],
                    'default_graph': 'bar',
                    'default': 'ECD_CHLD_36-59M_LMPSL',
                },
            },
            'ENV': {
                'NAME': 'Environment and climate change',
                'CARDS': [
                    {
                        'name': "Children's Climate Risk Index (CCRI)",
                        'indicator': 'CR_CCRI',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': "CCRI Pillar 1: Children's exposure to climate and environmental hazards, shocks and stresses",
                        'indicator': 'CR_CCRI_EXP_CESS',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': "CCRI Pillar 2: Children's vulnerability to climate and environmental hazards, shocks and stresses",
                        'indicator': 'CR_CCRI_VUL_ES',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Percentage of population with primary reliance on clean fuels and technology - SDG 7.1.2',
                        'indicator': 'CR_EG_EGY_CLEAN',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Age-standardized mortality rate attributed to household and ambient air pollution - SDG 3.9.1',
                        'indicator': 'CR_SH_STA_ASAIRP',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Age-standardized mortality rate attributed to household air pollution - SDG 3.9.1',
                        'indicator': 'CR_SH_HAP_ASMORT',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Age-standardized mortality rate attributed to ambient air pollution - SDG 3.9.1',
                        'indicator': 'CR_SH_AAP_ASMORT',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Annual mean concentration of particles PM2.5 (ug/m3) - SDG 11.6.2',
                        'indicator': 'HT_SDG_PM25',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'CR_CCRI',
                        'CR_CCRI_EXP_CESS',
                        'CR_CCRI_VUL_ES',
                        'CR_EG_EGY_CLEAN',
                        'CR_SH_STA_ASAIRP',
                        'CR_SH_HAP_ASMORT',
                        'CR_SH_AAP_ASMORT',
                        'HT_SDG_PM25',
                    ],
                    'default_graph': 'bar',
                    'default': 'CR_CCRI',
                },
            },
            'DCD': {
                'NAME': 'Disaster, conflict and displacement',
                'CARDS': [
                    {
                        'name': 'INFORM Risk Index',
                        'indicator': 'CR_INFORM',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Number of deaths and missing persons attributed to disasters (per 100,000 population) - SDG 11.5.1',
                        'indicator': 'CR_VC_DSR_MTMP',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Number of directly affected persons attributed to disasters (per 100,000 population) - SDG 11.5.1',
                        'indicator': 'CR_VC_DSR_DAFF',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Score of adoption and implementation of national DRR strategies in line with the Sendai Framework - SDG 1.5.3',
                        'indicator': 'CR_SG_DSR_LGRGSR',
                        'suffix': min_max_card_suffix,
                        'min_max': 'True',
                    },
                    {
                        'name': 'Number of first time asylum applicants',
                        'indicator': 'DM_ASYL_FRST',
                        'suffix': 'persons',
                        'min_max': 'False',
                    },
                    {
                        'name': 'Number of asylum applicants considered to be unaccompanied minors',
                        'indicator': 'DM_ASYL_UASC',
                        'suffix': 'persons',
                        'min_max': 'False',
                    },
                ],
                'AIO_AREA': {
                    'graphs': graphs_dict,
                    'indicators': [
                        'CR_INFORM',
                        'CR_VC_DSR_MTMP',
                        'CR_VC_DSR_DAFF',
                        'CR_SG_DSR_LGRGSR',
                        'DM_ASYL_FRST',
                        'DM_ASYL_UASC',
                    ],
                    'default_graph': 'bar',
                    'default': 'CR_INFORM',
                },
            },
        },
    },
}

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
            dcc.Store(id=f'{page_prefix}-current-indicator-store', storage_type='memory'),
            dbc.Container(
                fluid=True,
                children=get_base_layout(
                    indicators=merged_page_config['child-rights']['SUBDOMAINS'],
                    page_prefix=page_prefix,
                    domain_colour=merged_page_config['child-rights']['domain_colour'],
                    query_params=query_parmas,
                ),
            ),
            html.Br(),
        ],
        id="mainContainer",
    )

@callback(
    Output(f"{page_prefix}-collapse", "is_open"),
    [Input(f"{page_prefix}-collapse-button", "n_clicks")],
    [State(f"{page_prefix}-collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@callback(
    Output(f"{page_prefix}-indicator-dropdown", "options"),
    Output(f"{page_prefix}-indicator-dropdown", "value"),
    Input(f"{page_prefix}-crm-dropdown", "value"),
    Input(f"{page_prefix}-sdg-toggle", "on")
)
def apply_update_indicator_dropdown(indicator_filter, sdg_toggle):
    return update_indicator_dropdown(indicator_filter, sdg_toggle)


@callback(
    Output({"type": "area_types", "index": f"{page_prefix}-AIO_AREA"}, "options"),
    Output({"type": "area_types", "index": f"{page_prefix}-AIO_AREA"}, "value"),
    [Input(f'{page_prefix}-current-indicator-store', 'data')],
    prevent_initial_call=True,
)
def set_fig_options(indicator):
    return fig_options(indicator)


@callback(
    Output({"type": "area_breakdowns", "index": f"{page_prefix}-AIO_AREA"}, "options"),
    [
        Input(f'{page_prefix}-current-indicator-store', 'data'),
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
        State(f'{page_prefix}-current-indicator-store', 'data'),
    ],
    prevent_initial_call=True,
)
def set_default_compare(compare_options, selected_type, indicator):
    return default_compare(compare_options, selected_type, indicator)

@callback(
    Output({"type": f"{page_prefix}-indicator-button", "index": ALL}, "active"),
    Input({"type": "indicator-button", "index": ALL}, "n_clicks"),
    State({"type": "indicator-button", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def set_active_button(_, buttons_id):
    print(f"buttons_id: {buttons_id}")
    print(active_button(_, buttons_id))
    return active_button(_, buttons_id)


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
        Input(f'{page_prefix}-current-indicator-store', 'data'),
    ],
    prevent_initial_call=True,
)
def apply_available_crc_years(country, indicator):
    return available_crc_years(country, indicator)

@callback(
    Output(f'{page_prefix}-current-indicator-store', 'data'),
    [
        Input(f"{page_prefix}-indicator-dropdown", "value"),
        Input({'type': "indicator-button", 'index': ALL}, 'active'),
    ],
    [
        State({'type': "indicator-button", 'index': ALL}, 'id')
    ]
)
def update_current_indicator(dropdown_value, active_buttons, button_ids):
    view_toggle = True
    if view_toggle:  # If the view is based on indicator buttons
        active_index = next((i for i, active in enumerate(active_buttons) if active), None)
        if active_index is not None:
            print(f"current_indicator: {button_ids[active_index]['index']}")
            return button_ids[active_index]['index']
    print(f"dropdown_value")
    return dropdown_value  # Otherwise, return the dropdown value

@callback(
    Output(f"{page_prefix}-crc-header", "children"),
    Output(f"{page_prefix}-crc-header", "style"),
    Output(f"{page_prefix}-crc-accordion", "children"),
    Input(f"{page_prefix}-year-filter-crc", "value"),
    Input(f"{page_prefix}-country-filter-crc", "value"),
    Input(f'{page_prefix}-current-indicator-store', 'data'),
    State(f"{page_prefix}-crc-header", "style"),
    prevent_initial_call=True,
)
def apply_filter_crc_data(year, country, indicator, text_style):
    return filter_crc_data(year, country, indicator, page_prefix, text_style)

@callback(
        Output(f"{page_prefix}-indicator-dropdown", "className"),
        Output(f"{page_prefix}-domain-text", "children"),
        Input(f'{page_prefix}-current-indicator-store', 'data'),
        prevent_initial_call=True,
)
def apply_update_indicator_dropdown_class(indicator):
 return update_indicator_dropdown_class(indicator)

@callback(
    Output(f"{page_prefix}-themes", "children"),
    Input(f"{page_prefix}-domain-dropdown", "value"),
)
def apply_create_subdomain_buttons(domain_dropdown_value):
    return create_subdomain_buttons(domain_dropdown_value)

@callback(
    Output({"type": f"{page_prefix}-subdomain_button", "index": ALL}, "active"),
    Input({"type": "subdomain_button", "index": ALL}, "n_clicks"),
    State({"type": "subdomain_button", "index": ALL}, "id"),
    prevent_initial_call=True,
)
def set_active_subdomain_button(_, buttons_id):
    return active_button(_, buttons_id)


@callback(
    Output({"type": "button_group", "index": f"{page_prefix}-AIO_AREA"}, "children"),
    [Input({"type": "subdomain_button", "index": ALL}, "active")],
    [State({"type": "subdomain_button", "index": ALL}, "id")]
)
def apply_create_indicator_buttons(active_button, subdomain_buttons):
    return create_indicator_buttons(active_button, subdomain_buttons)

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
        Output(f"{page_prefix}-definition-popover", "children"),
    ],
    [
        Input(f'{page_prefix}-current-indicator-store', 'data'),
        Input({"type": "area_breakdowns", "index": f"{page_prefix}-AIO_AREA"}, "value"),
        Input(f"{page_prefix}-year_slider", "value"),
        Input(f"{page_prefix}-country-filter", "value"),
        Input(f"{page_prefix}-country-group", "value"),
        
    ],
    [
        State(f"{page_prefix}-indicators", "data"),
        State({"type": "area_types", "index": f"{page_prefix}-AIO_AREA"}, "value"),
        #State(f"{page_prefix}-definition-text", "style"),
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
    return aio_area_figure(
        indicator,
        compare,
        years_slider,
        countries,
        country_group,
        indicators_dict,
        selected_type,
        page_prefix,
    )
