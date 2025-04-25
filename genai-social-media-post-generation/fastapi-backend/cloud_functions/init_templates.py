import os
from google.cloud import firestore
from loguru import logger

# --- GCP Project Configuration ---
PROJECT_ID = os.environ.get("PROJECT_ID")
PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER")
FIRESTORE_INSTANCE_ID = "(default)"
db = firestore.Client(project=PROJECT_ID, database=FIRESTORE_INSTANCE_ID)

# --- Firestore Functions ---
collection_post_template = db.collection("post_template")

template_list = [
    {
        "templateName": "SQUARE_FORMAL_TEMPLATE_1",
        "layouts": [
            {
                "actorPosition": {"height": 728, "width": 616, "x": 193, "y": 138},
                "backgroundSize": {
                    "height": 1080,
                    "width": 1080,
                },
                "textActionPosition": {"height": 140, "width": 131, "x": 864, "y": 179},
                "textDetailsPosition": {
                    "height": 147,
                    "width": 854,
                    "x": 207,
                    "y": 901,
                },
                "textHeader1Position": {"height": 121, "width": 781, "x": 150, "y": 12},
                "textTaglinePosition": {
                    "height": 116,
                    "width": 269,
                    "x": 811,
                    "y": 751,
                },
                "layoutName": "SQUARE_FORMAL_TEMPLATE_CTA_4_V2",
            },
            {
                "actorPosition": {"height": 701, "width": 676, "x": 231, "y": 49},
                "backgroundSize": {"height": 1080, "width": 1080},
                "textActionPosition": {"height": 130, "width": 135, "x": 60, "y": 679},
                "textDetailsPosition": {
                    "height": 188,
                    "width": 520,
                    "x": 361,
                    "y": 880,
                },
                "textHeader1Position": {
                    "height": 117,
                    "width": 699,
                    "x": 350,
                    "y": 751,
                },
                "textTaglinePosition": {
                    "height": 110,
                    "width": 182,
                    "x": 890,
                    "y": 959,
                },
                "layoutName": "SQUARE_FORMAL_TEMPLATE_CTA_3",
            },
            {
                "actorPosition": {"height": 567, "width": 594, "x": 350, "y": 302},
                "backgroundSize": {
                    "height": 1080,
                    "width": 1080,
                },
                "textActionPosition": {"height": 172, "width": 175, "x": 78, "y": 417},
                "textDetailsPosition": {
                    "height": 174,
                    "width": 689,
                    "x": 369,
                    "y": 887,
                },
                "textHeader1Position": {"height": 173, "width": 889, "x": 64, "y": 60},
                "textTaglinePosition": {"height": 106, "width": 335, "x": 2, "y": 773},
                "layoutName": "SQUARE_FORMAL_TEMPLATE_CTA_1",
            },
            {
                "actorPosition": {"height": 625, "width": 566, "x": 185, "y": 241},
                "backgroundSize": {
                    "height": 1080,
                    "width": 1080,
                },
                "textActionPosition": {"height": 156, "width": 151, "x": 814, "y": 435},
                "textDetailsPosition": {
                    "height": 176,
                    "width": 860,
                    "x": 202,
                    "y": 886,
                },
                "textHeader1Position": {"height": 169, "width": 887, "x": 173, "y": 60},
                "textTaglinePosition": {
                    "height": 115,
                    "width": 311,
                    "x": 761,
                    "y": 750,
                },
                "layoutName": "SQUARE_FORMAL_TEMPLATE_CTA_2_V2",
            },
        ],
    },
    {
        "templateName": "VERTICAL_TEMPLATE_1",
        "layouts": [
            {
                "actorPosition": {"height": 979, "width": 797, "x": 150, "y": 307},
                "backgroundSize": {
                    "height": 1920,
                    "width": 1080,
                },
                # "qrCodePosition": {"height": 260, "width": 244, "x": 64, "y": 68},
                "textActionPosition": {"height": 200, "width": 189, "x": 799, "y": 96},
                "textDetailsPosition": {
                    "height": 255,
                    "width": 891,
                    "x": 105,
                    "y": 1500,
                },
                "textHeader1Position": {
                    "height": 117,
                    "width": 854,
                    "x": 114,
                    "y": 1298,
                },
                "textTaglinePosition": {
                    "height": 157,
                    "width": 892,
                    "x": 105,
                    "y": 1760,
                },
                "layoutName": "VERTICAL_INFORMAL_TEMPLATE_CTA_5_V2",
            },
            {
                "actorPosition": {"height": 909, "width": 985, "x": 51, "y": 318},
                "backgroundSize": {"height": 1920, "width": 1080},
                # "qrCodePosition": {"height": 248, "width": 253, "x": 63, "y": 81},
                "textActionPosition": {"height": 197, "width": 189, "x": 799, "y": 99},
                "textDetailsPosition": {
                    "height": 287,
                    "width": 842,
                    "x": 204,
                    "y": 1498,
                },
                "textHeader1Position": {
                    "height": 126,
                    "width": 843,
                    "x": 202,
                    "y": 1304,
                },
                "textTaglinePosition": {
                    "height": 119,
                    "width": 843,
                    "x": 204,
                    "y": 1794,
                },
                "layoutName": "VERTICAL_INFORMAL_TEMPLATE_CTA_4",
            },
            {
                "actorPosition": {"height": 968, "width": 897, "x": 101, "y": 486},
                "backgroundSize": {"height": 1920, "width": 1080},
                # "qrCodePosition": {"height": 261, "width": 264, "x": 86, "y": 78},
                "textActionPosition": {"height": 202, "width": 202, "x": 751, "y": 113},
                "textDetailsPosition": {
                    "height": 299,
                    "width": 872,
                    "x": 182,
                    "y": 1499,
                },
                "textHeader1Position": {
                    "height": 128,
                    "width": 873,
                    "x": 111,
                    "y": 372,
                },
                "textTaglinePosition": {
                    "height": 108,
                    "width": 872,
                    "x": 182,
                    "y": 1805,
                },
                "layoutName": "VERTICAL_INFORMAL_TEMPLATE_CTA_3",
            },
            {
                "actorPosition": {"height": 952, "width": 684, "x": 396, "y": 503},
                "backgroundSize": {"height": 1920, "width": 1080},
                # "qrCodePosition": {"height": 300, "width": 300, "x": 100, "y": 399},
                "textActionPosition": {
                    "height": 204,
                    "width": 211,
                    "x": 155,
                    "y": 1156,
                },
                "textDetailsPosition": {
                    "height": 294,
                    "width": 874,
                    "x": 25,
                    "y": 1482,
                },
                "textHeader1Position": {"height": 147, "width": 884, "x": 21, "y": 85},
                "textTaglinePosition": {
                    "height": 123,
                    "width": 876,
                    "x": 24,
                    "y": 1779,
                },
                "layoutName": "VERTICAL_INFORMAL_TEMPLATE_CTA_2",
            },
        ],
    },
    {
        "templateName": "SQUARE_FULL_IMAGE_TEMPLATE_1",
        "layouts": [
            {
                "actorPosition": {"height": 1080, "width": 1080, "x": 0, "y": 0},
                "backgroundSize": {"height": 1080, "width": 1080},
                "textActionPosition": {"height": 159, "width": 162, "x": 84, "y": 242},
                "textDetailsPosition": {
                    "height": 219,
                    "width": 610,
                    "x": 452,
                    "y": 665,
                },
                "textHeader1Position": {"height": 101, "width": 887, "x": 101, "y": 13},
                "textTaglinePosition": {"height": 102, "width": 343, "x": 8, "y": 970},
                "layoutName": "SQUARE_FORMAL_TEMPLATE_BLANK_4",
            },
            {
                "actorPosition": {"height": 1080, "width": 1080, "x": 0, "y": 0},
                "backgroundSize": {"height": 1080, "width": 1080},
                "textActionPosition": {"height": 151, "width": 157, "x": 107, "y": 252},
                "textDetailsPosition": {"height": 287, "width": 434, "x": 17, "y": 701},
                "textHeader1Position": {"height": 255, "width": 306, "x": 767, "y": 45},
                "textTaglinePosition": {"height": 97, "width": 311, "x": 769, "y": 983},
                "layoutName": "SQUARE_FORMAL_TEMPLATE_BLANK_3",
            },
            {
                "actorPosition": {"height": 1080, "width": 1080, "x": 0, "y": 0},
                "backgroundSize": {"height": 1080, "width": 1080},
                "textActionPosition": {"height": 144, "width": 143, "x": 102, "y": 243},
                "textDetailsPosition": {
                    "height": 165,
                    "width": 849,
                    "x": 115,
                    "y": 790,
                },
                "textHeader1Position": {"height": 93, "width": 851, "x": 115, "y": 18},
                "textTaglinePosition": {"height": 106, "width": 295, "x": 0, "y": 974},
                "layoutName": "SQUARE_FORMAL_TEMPLATE_BLANK_2",
            },
            {
                "actorPosition": {"height": 1080, "width": 1080, "x": 0, "y": 0},
                "backgroundSize": {"height": 1080, "width": 1080},
                "textActionPosition": {"height": 145, "width": 144, "x": 119, "y": 272},
                "textDetailsPosition": {"height": 191, "width": 724, "x": 16, "y": 875},
                "textHeader1Position": {"height": 275, "width": 326, "x": 754, "y": 26},
                "textTaglinePosition": {
                    "height": 119,
                    "width": 295,
                    "x": 785,
                    "y": 961,
                },
                "layoutName": "SQUARE_FORMAL_TEMPLATE_BLANK_1",
            },
        ],
    },
]

async def add_new_templates_to_db():
    logger.info("Adding new templates to db")
    templates = template_list
    for template in templates:
        collection_post_template.document(template.get("templateName")).set(
            template
        )
    logger.info("New templates added to db")
    return

if __name__ == "__main__":
    add_new_templates_to_db()