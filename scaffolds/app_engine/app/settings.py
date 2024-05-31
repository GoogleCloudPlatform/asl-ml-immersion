""" Config retrieves and stores all the constant settings..
"""

import os


class Config:
    """Configurations"""

    BUCKET = os.environ.get("BUCKET")
    LOCATION = os.environ.get("LOCATION")
    PROJECT = os.environ.get("PROJECT")
    LOCAL_STORAGE = os.environ.get("LOCAL_STORAGE", "/tmp/answernaut")

    # Datasheet Service Config
    DATASHEET_PATH = os.environ.get(
        "DATASHEET_PATH", f"gs://{BUCKET}/data.csv"
    )
    DATASHEET_CONTENT_COLUMNS = list(
        os.environ.get(
            "DATASHEET_CONTENT_COLUMNS",
            [
                "title",
                "abstract",
            ],
        )
    )
    DATASHEET_METADATA_COLUMNS = list(
        os.environ.get(
            "DATASHEET_METADATA_COLUMNS",
            [
                "title",
                "url",
            ],
        )
    )

    # Retrieval Service Config
    PALM_TEXT_MODEL = os.environ.get("PALM_MODEL", "text-bison")
    PALM_EMBBEDING_MODEL = os.environ.get(
        "PALM_EMBBEDING_MODEL", "textembedding-gecko"
    )
    PALM_TEMPERATURE = float(os.environ.get("PALM_TEMPERATURE", 0.0))
    PALM_TOP_P = float(os.environ.get("PALM_TOP_P", 0.95))
    PALM_TOP_K = int(os.environ.get("PALM_TOP_K", 40))
    PALM_MAX_OUTPUT_TOKENS = int(os.environ.get("PALM_MAX_OUTPUT_TOKENS", 1024))
    RETRIEVAL_CHUNK_SIZE = int(os.environ.get("RETRIEVAL_CHUNK_SIZE", 800))
    RETRIEVAL_OVERLAP_SIZE = int(os.environ.get("RETRIEVAL_CHUNK_SIZE", 400))
    RETRIEVAL_SEARCH_TYPE = os.environ.get(
        "RETRIEVAL_SEARCH_TYPE", "similarity"
    )
    RETRIEVAL_NEAREST_NEIGHBORS = int(
        os.environ.get("RETRIEVAL_NEAREST_NEIGHBORS", 30)
    )
