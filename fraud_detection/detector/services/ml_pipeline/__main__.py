from dotenv import load_dotenv
import data_loader
import feature_transformer
import tester
import model
import os
from predictor import Predictor
import json

# ---------------------- SETUP FEATURE FLAGS --------------------- #

load_dotenv()

SAVE_MODEL_FILE = os.getenv("SAVE_MODEL_FILE") in ['TRUE', 'True', 'true', '1']

# --------------------- PUBLIC FUNCTIONS --------------------- #


def make_model() -> None:
    df = data_loader.load_data()
    res = feature_transformer.transform_df(df)

    # Combines stats and categories dictionaries
    metadata = res.stats | res.categories

    # Note - Throws if any test fails, but they should not unless bugs
    tester.test(res.df)

    model_output = model.create(res.df)

    if SAVE_MODEL_FILE:
        model_output.model.save('data/model.keras')

        with open('data/metadata.json', 'w') as f:
            json.dump(metadata, f, indent=4)


def make_predictor(model_id: str) -> Predictor:
    return Predictor(model_id)


# --------------------------- START -------------------------- #

if __name__ == '__main__':
    make_model()
