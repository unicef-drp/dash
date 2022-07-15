from collections import defaultdict
import plotly.express as px

from . import data, years
from .base_page import get_base_layout

indicators_dict = {
    "PARTICIPATION": {
        "NAME": "Education access and participation",
        "CARDS": [
            {
                "name": "Who are Out-of-School",
                "indicator": "EDUNF_OFST_L1,EDUNF_OFST_L2,EDUNF_OFST_L3",
                "suffix": "Primary to upper secondary aged Children and Adolescents",
                "age": "SCHOOL_AGE",
            },
            {
                "name": "Who are Out-of-School",
                "indicator": "EDUNF_OFST_L1,EDUNF_OFST_L2,EDUNF_OFST_L3",
                "suffix": "Primary to upper secondary aged Girls",
                "sex": "F",
                "age": "SCHOOL_AGE",
            },
            {
                "name": "Who are Out-of-School",
                "indicator": "EDUNF_OFST_L1_UNDER1",
                "suffix": "Children one year younger than the official primary entry age",
                "age": "UNDER1_SCHOOL_ENTRY",
            },
        ],
        "MAIN": {
            "name": "Out-of-School Children",
            "geo": "Country_name",  # REF_AREA
            "options": dict(
                locations="REF_AREA",
                featureidkey="id",
                color="OBS_VALUE",
                color_continuous_scale=px.colors.sequential.GnBu,
                mapbox_style="carto-positron",
                zoom=2,
                center={"lat": 62.995158, "lon": 88.048713},
                opacity=0.5,
                labels={
                    "OBS_VALUE": "Value",
                    "REF_AREA": "ISO3 Code",
                    "TIME_PERIOD": "Year",
                    "Country_name": "Country",
                },
                hover_data={
                    "OBS_VALUE": True,
                    "REF_AREA": False,
                    "Country_name": True,
                    "TIME_PERIOD": True,
                },
                animation_frame="TIME_PERIOD",
                height=750,
            ),
            "indicators": [
                "EDUNF_ROFST_L1",
                "EDUNF_ROFST_L2",
                "EDUNF_ROFST_L3",
                "EDUNF_OFST_L1",
                "EDUNF_OFST_L2",
                "EDUNF_OFST_L3",
                "EDU_SDG_PRYA",
                "EDUNF_ROFST_L1_UNDER1",
                "EDUNF_ROFST_L1T3",
            ],
            "default": "EDUNF_ROFST_L1",
        },
        "AREA_1": {
            "name": "Education entry and transition",
            "graphs": {
                "bar": {
                    "options": dict(
                        x="Country_name",
                        y="OBS_VALUE",
                        barmode="group",
                        # text="TIME_PERIOD",
                        text="OBS_VALUE",
                        hover_name="TIME_PERIOD",
                    ),
                    # "compare": "Sex",
                },
                "line": {
                    "options": dict(
                        x="TIME_PERIOD",
                        y="OBS_VALUE",
                        color="Country_name",
                        hover_name="Country_name",
                        line_shape="spline",
                        render_mode="svg",
                    ),
                    "trace_options": dict(mode="lines+markers"),
                },
            },
            "default_graph": "bar",
            "indicators": [
                "EDUNF_ROFST_L1",
                "EDUNF_ROFST_L2",
                "EDUNF_ROFST_L3",
                "EDUNF_ROFST_L1_UNDER1",
                "EDUNF_ROFST_L1T3",
                "EDUNF_STU_L1_TOT",
                "EDUNF_STU_L2_TOT",
                "EDUNF_STU_L3_TOT",
                "EDUNF_GER_L2_GEN",
                "EDUNF_GER_L2_VOC",
                "EDUNF_GER_L3",
                "EDUNF_GER_L3_GEN",
                "EDUNF_GER_L3_VOC",
            ],
            "default": "EDUNF_ROFST_L1",
        },
        "AREA_2": {
            "name": "Education entry and transition",
            "graphs": {
                "bar": {
                    "options": dict(
                        x="Country_name",
                        y="OBS_VALUE",
                        barmode="group",
                        # text="TIME_PERIOD",
                        text="OBS_VALUE",
                        hover_name="TIME_PERIOD",
                    ),
                    # "compare": "Sex",
                },
                "line": {
                    "options": dict(
                        x="TIME_PERIOD",
                        y="OBS_VALUE",
                        color="Country_name",
                        hover_name="Country_name",
                        line_shape="spline",
                        render_mode="svg",
                    ),
                    "trace_options": dict(mode="lines+markers"),
                },
            },
            "default_graph": "line",
            "indicators": [
                "EDUNF_NER_L02",
                "EDUNF_NERA_L1_UNDER1",
                "EDUNF_NERA_L1",
                "EDUNF_NERA_L2",
                "EDUNF_GER_L1",
                "EDUNF_GER_L2",
                "EDUNF_GER_L3",
                "EDUNF_NIR_L1_ENTRYAGE",
                "EDUNF_TRANRA_L2",
            ],
            "default": "EDUNF_TRANRA_L2",
        },
        "AREA_3": {
            "name": "Safe and inclusive learning environments",
            "graphs": {
                "bar": {
                    "options": dict(
                        x="Country_name",
                        y="OBS_VALUE",
                        barmode="group",
                        # text="TIME_PERIOD",
                        text="OBS_VALUE",
                        hover_name="TIME_PERIOD",
                    ),
                    # "compare": "Sex",
                },
                "line": {
                    "options": dict(
                        x="TIME_PERIOD",
                        y="OBS_VALUE",
                        color="Country_name",
                        hover_name="Country_name",
                        line_shape="spline",
                        render_mode="svg",
                    ),
                    "trace_options": dict(mode="lines+markers"),
                },
            },
            "default_graph": "bar",
            "indicators": [
                "EDU_SDG_SCH_L1",
                "EDU_SDG_SCH_L2",
                "EDU_SDG_SCH_L3",
                "WS_SCH_H-B",
                "WS_SCH_S-B",
                "WS_SCH_W-B",
                "EDU_CHLD_DISAB",
                "EDU_CHLD_DISAB_GENERAL",
                "EDU_CHLD_DISAB_SPECIAL",
                "EDU_CHLD_DISAB_GENERAL_BOARDING",
                "EDU_CHLD_DISAB_SPECIAL_BOARDING",
                "EDU_CHLD_DISAB_HOME",
                "EDU_SDG_PRYA",
            ],
            "default": "EDU_CHLD_DISAB",
        },
        "AREA_4": {
            "name": "Education completion",
            "graphs": {
                "bar": {
                    "options": dict(
                        x="Country_name",
                        y="OBS_VALUE",
                        barmode="group",
                        # text="TIME_PERIOD",
                        text="OBS_VALUE",
                        hover_name="TIME_PERIOD",
                    ),
                    # "compare": "Sex",
                },
                "line": {
                    "options": dict(
                        x="TIME_PERIOD",
                        y="OBS_VALUE",
                        color="Country_name",
                        hover_name="Country_name",
                        line_shape="spline",
                        render_mode="svg",
                    ),
                    "trace_options": dict(mode="lines+markers"),
                },
            },
            "default_graph": "bar",
            "indicators": [
                "EDUNF_CR_L1",
                "EDUNF_CR_L2",
                "EDUNF_CR_L3",
                "EDUNF_DR_L1",
                "EDUNF_DR_L2",
                "EDUNF_GER_L2",
            ],
            "default": "EDUNF_CR_L1",
        },
    },
    "QUALITY": {
        "NAME": "Learning quality and skills",
        "CARDS": [
            {
                "name": "(enrolled in the same grade for a second or further year) in primary and lower secondary education",
                "indicator": "EDUNF_RPTR_L1,EDUNF_RPTR_L2",
                "suffix": "Children and adolescent repeaters",
            },
            {
                "name": "from primary education",
                "indicator": "EDUNF_ESL_L1",
                "suffix": "Early school leavers",
            },
            {
                "name": "administering nationally representative learning assessment in both reading and math at the end of primary education",
                "indicator": "EDUNF_ADMIN_L1_GLAST_REA,EDUNF_ADMIN_L1_GLAST_MAT",
                "suffix": "Countries",
            },
            {
                "name": "participating in the latest round of PISA",
                "indicator": "EDU_PISA_MAT,EDU_PISA_REA,EDU_PISA_SCI",
                "suffix": "Countries",
                "absolute": True,
            },
        ],
        "MAIN": {
            "name": "What students know and can do",
            "geo": "Country_name",
            "options": dict(
                locations="REF_AREA",
                featureidkey="id",
                color="OBS_VALUE",
                color_continuous_scale=px.colors.sequential.GnBu,
                mapbox_style="carto-positron",
                zoom=2,
                center={"lat": 62.995158, "lon": 88.048713},
                opacity=0.5,
                labels={
                    "OBS_VALUE": "Value",
                    "Country_name": "Country",
                    "TIME_PERIOD": "Year",
                    "REF_AREA": "ISO3 Code",
                },
                hover_data={
                    "OBS_VALUE": True,
                    "REF_AREA": False,
                    "Country_name": True,
                    "TIME_PERIOD": True,
                },
                animation_frame="TIME_PERIOD",
                height=750,
            ),
            "indicators": ["EDU_PISA_MAT", "EDU_PISA_REA", "EDU_PISA_SCI"],
            "default": "EDU_PISA_MAT",
        },
        "AREA_1": {
            "name": "Literacy and Development",
            "graphs": {
                "bar": {
                    "options": dict(
                        x="Country_name",
                        y="OBS_VALUE",
                        barmode="group",
                        # text="TIME_PERIOD",
                        text="OBS_VALUE",
                        hover_name="TIME_PERIOD",
                    ),
                    # "compare": "Sex",
                },
                "line": {
                    "options": dict(
                        x="TIME_PERIOD",
                        y="OBS_VALUE",
                        color="Country_name",
                        hover_name="Country_name",
                        line_shape="spline",
                        render_mode="svg",
                    ),
                    "trace_options": dict(mode="lines+markers"),
                },
            },
            "default_graph": "bar",
            "indicators": [
                "ECD_CHLD_36-59M_LMPSL",
                "EDUNF_LR_YOUTH",
                "EDUNF_LR_ADULT",
            ],
            "default": "EDUNF_LR_YOUTH",
        },
        "AREA_2": {
            "name": "Foundational skills",
            "graphs": {
                "bar": {
                    "options": dict(
                        x="Country_name",
                        y="OBS_VALUE",
                        barmode="group",
                        # text="TIME_PERIOD",
                        text="OBS_VALUE",
                        hover_name="TIME_PERIOD",
                    ),
                    # "compare": "Sex",
                },
                "line": {
                    "options": dict(
                        x="TIME_PERIOD",
                        y="OBS_VALUE",
                        color="Country_name",
                        hover_name="Country_name",
                        line_shape="spline",
                        render_mode="svg",
                    ),
                    "trace_options": dict(mode="lines+markers"),
                },
            },
            "default_graph": "line",
            "indicators": [
                "EDU_SDG_STU_L2_GLAST_MAT",
                "EDU_SDG_STU_L2_GLAST_REA",
                "EDU_SDG_STU_L1_GLAST_MAT",
                "EDU_SDG_STU_L1_G2OR3_MAT",
                "EDU_SDG_STU_L1_GLAST_REA",
                "EDU_SDG_STU_L1_G2OR3_REA",
            ],
            "default": "EDU_SDG_STU_L2_GLAST_MAT",
        },
        "AREA_3": {
            "name": "Trained teachers",
            "graphs": {
                "bar": {
                    "options": dict(
                        x="Country_name",
                        y="OBS_VALUE",
                        barmode="group",
                        # text="TIME_PERIOD",
                        text="OBS_VALUE",
                        hover_name="TIME_PERIOD",
                    ),
                    # "compare": "Sex",
                },
                "line": {
                    "options": dict(
                        x="TIME_PERIOD",
                        y="OBS_VALUE",
                        color="Country_name",
                        hover_name="Country_name",
                        line_shape="spline",
                        render_mode="svg",
                    ),
                    "trace_options": dict(mode="lines+markers"),
                },
            },
            "default_graph": "bar",
            "indicators": [
                "EDU_SDG_TRTP_L02",
                "EDU_SDG_TRTP_L1",
                "EDU_SDG_TRTP_L2",
                "EDU_SDG_TRTP_L3",
            ],
            "default": "EDU_SDG_TRTP_L2",
        },
        "AREA_4": {
            "name": "Qualified teachers",
            "graphs": {
                "bar": {
                    "options": dict(
                        x="Country_name",
                        y="OBS_VALUE",
                        barmode="group",
                        # text="TIME_PERIOD",
                        text="OBS_VALUE",
                        hover_name="TIME_PERIOD",
                    ),
                    # "compare": "Sex",
                },
                "line": {
                    "options": dict(
                        x="TIME_PERIOD",
                        y="OBS_VALUE",
                        color="Country_name",
                        hover_name="Country_name",
                        line_shape="spline",
                        render_mode="svg",
                    ),
                    "trace_options": dict(mode="lines+markers"),
                },
            },
            "default_graph": "bar",
            "indicators": [
                "EDU_SDG_QUTP_L02",
                "EDU_SDG_QUTP_L1",
                "EDU_SDG_QUTP_L2",
                "EDU_SDG_QUTP_L3",
            ],
            "default": "EDU_SDG_QUTP_L2",
        },
    },
    "SYSTEM": {
        "NAME": "Education System",
        "CARDS": [
            {
                "name": "Guaranteeing at least one year of free pre-primary education in their legal frameworks",
                "indicator": "EDU_SDG_FREE_EDU_L02",
                "suffix": "Countries",
            },
            {
                "name": "Enrolled in private institutions (primary, lower secondary and upper secondary education)",
                "indicator": "EDUNF_STU_L1_PRV,EDUNF_STU_L2_PRV,EDUNF_STU_L3_PRV",
                "suffix": "Children and Adolescents",
            },
            {
                "name": "Total in primary, lower secondary and upper secondary education",
                "indicator": "EDUNF_TEACH_L1,EDUNF_TEACH_L2,EDUNF_TEACH_L3",
                "suffix": "Classroom Teachers",
            },
        ],
        "MAIN": {
            "name": "Guaranteeing and paying for education",  # "Education Expenditures and Legal Frameworks",
            "geo": "Country_name",
            "options": dict(
                locations="REF_AREA",
                featureidkey="id",
                color="OBS_VALUE",
                color_continuous_scale=px.colors.sequential.GnBu,
                mapbox_style="carto-positron",
                zoom=2,
                center={"lat": 62.995158, "lon": 88.048713},
                opacity=0.5,
                labels={
                    "OBS_VALUE": "Value",
                    "Country_name": "Country",
                    "TIME_PERIOD": "Year",
                    "REF_AREA": "ISO3 Code",
                },
                hover_data={
                    "OBS_VALUE": True,
                    "REF_AREA": False,
                    "Country_name": True,
                    "TIME_PERIOD": True,
                },
                animation_frame="TIME_PERIOD",
                height=750,
            ),
            "indicators": [
                "EDU_FIN_EXP_PT_GDP",
                "EDU_FIN_EXP_PT_TOT",
                "EDU_SDG_FREE_EDU_L02",
                "EDU_SDG_COMP_EDU_L02",
                "EDU_FIN_EXP_CONST_PPP",
            ],
            "default": "EDU_FIN_EXP_PT_GDP",
        },
        "AREA_1": {
            "name": "Public and private enrolments",
            "graphs": {
                "bar": {
                    "options": dict(
                        x="Country_name",
                        y="OBS_VALUE",
                        barmode="group",
                        # text="TIME_PERIOD",
                        text="OBS_VALUE",
                        hover_name="TIME_PERIOD",
                    ),
                    # "compare": "Sex",
                },
                "line": {
                    "options": dict(
                        x="TIME_PERIOD",
                        y="OBS_VALUE",
                        color="Country_name",
                        hover_name="Country_name",
                        line_shape="spline",
                        render_mode="svg",
                    ),
                    "trace_options": dict(mode="lines+markers"),
                },
            },
            "default_graph": "bar",
            "indicators": [
                "EDUNF_PRP_L02",
                "EDUNF_PRP_L1",
                "EDUNF_PRP_L2",
                "EDUNF_PRP_L3",
            ],
            "default": "EDUNF_PRP_L1",
        },
        "AREA_2": {
            "name": "Public and private enrolments",
            "graphs": {
                "bar": {
                    "options": dict(
                        x="Country_name",
                        y="OBS_VALUE",
                        barmode="group",
                        # text="TIME_PERIOD",
                        text="OBS_VALUE",
                        hover_name="TIME_PERIOD",
                    ),
                    # "compare": "Sex",
                },
                "line": {
                    "options": dict(
                        x="TIME_PERIOD",
                        y="OBS_VALUE",
                        color="Country_name",
                        hover_name="Country_name",
                        line_shape="spline",
                        render_mode="svg",
                    ),
                    "trace_options": dict(mode="lines+markers"),
                },
            },
            "default_graph": "line",
            "indicators": [
                "EDUNF_STU_L01_PUB",
                "EDUNF_STU_L02_PUB",
                "EDUNF_STU_L1_PUB",
                "EDUNF_STU_L2_PUB",
                "EDUNF_STU_L3_PUB",
                "EDUNF_STU_L01_PRV",
                "EDUNF_STU_L02_PRV",
                "EDUNF_STU_L1_PRV",
                "EDUNF_STU_L2_PRV",
                "EDUNF_STU_L3_PRV",
            ],
            "default": "EDUNF_STU_L1_PUB",
        },
        "AREA_3": {
            "name": "Government education expenditure",
            "graphs": {
                "bar": {
                    "options": dict(
                        x="Country_name",
                        y="OBS_VALUE",
                        barmode="group",
                        # text="TIME_PERIOD",
                        text="OBS_VALUE",
                        hover_name="TIME_PERIOD",
                    ),
                    # "compare": "Sex",
                },
                "line": {
                    "options": dict(
                        x="TIME_PERIOD",
                        y="OBS_VALUE",
                        color="Country_name",
                        hover_name="Country_name",
                        line_shape="spline",
                        render_mode="svg",
                    ),
                    "trace_options": dict(mode="lines+markers"),
                },
            },
            "default_graph": "bar",
            "indicators": [
                "EDU_FIN_EXP_L02",
                "EDU_FIN_EXP_L1",
                "EDU_FIN_EXP_L2",
                "EDU_FIN_EXP_L3",
                "EDU_FIN_EXP_L4",
                "EDU_FIN_EXP_L5T8",
                "EDU_FIN_EXP_CONST_PPP",
            ],
            "default": "EDU_FIN_EXP_L2",
        },
        "AREA_4": {
            "name": "Administration of learning assessments",
            "graphs": {
                "bar": {
                    "options": dict(
                        x="Country_name",
                        y="OBS_VALUE",
                        barmode="group",
                        # text="TIME_PERIOD",
                        text="OBS_VALUE",
                        hover_name="TIME_PERIOD",
                    ),
                },
                "line": {
                    "options": dict(
                        x="TIME_PERIOD",
                        y="OBS_VALUE",
                        color="Country_name",
                        hover_name="Country_name",
                        line_shape="spline",
                        render_mode="svg",
                    ),
                    "trace_options": dict(mode="lines+markers"),
                },
            },
            "default_graph": "bar",
            "indicators": {
                "EDUNF_ADMIN_L1_GLAST_REA": {},
                "EDUNF_ADMIN_L1_GLAST_MAT": {},
                "EDUNF_ADMIN_L2_REA": {},
                "EDUNF_ADMIN_L2_MAT": {"dtype": "str"},
                "EDUNF_ADMIN_L1_G2OR3_REA": {},
                "EDUNF_ADMIN_L1_G2OR3_MAT": {},
            },
            "default": "EDUNF_ADMIN_L2_MAT",
        },
    },
}


main_title = "Education, Leisure, and Culture"


def get_layout(**kwargs):
    kwargs["indicators"] = indicators_dict
    kwargs["main_title"] = main_title
    return get_base_layout(**kwargs)
