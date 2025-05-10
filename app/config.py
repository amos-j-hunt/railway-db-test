import os

class Config:
    # default database: your personal collection
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "COLLECTION_DATABASE_URL",
        "mysql+pymysql://mtg_user:password@localhost/mtg_collection"
    )

    # named bind for the full MTG printings
    SQLALCHEMY_BINDS = {
        "all_printings": os.getenv(
            "PRINTINGS_DATABASE_URL",
            "mysql+pymysql://mtg_user:password@localhost/mtg_all_printings"
        )
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False
