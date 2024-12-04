from dotenv import load_dotenv
import data_loader
import feature_transformer
import tester
import model
import os
from predictor import Predictor

# ---------------------- SETUP ENV FLAGS --------------------- #

load_dotenv()

SAVE_MODEL_FILE = os.getenv("SAVE_MODEL_FILE") in ['TRUE', 'True', 'true', '1']

# --------------------- PUBLIC FUNCTIONS --------------------- #


def make_model():
    df = data_loader.load_data()
    df = feature_transformer.transform_df(df)
    tester.test(df)  # throws if any test fails
    model_output = model.create(df)

    print(model_output.test_result)

    # save model locally?
    if SAVE_MODEL_FILE:
        model_output.model.save('data/model.keras')


def make_predictor(model_id: str) -> Predictor:
    return Predictor(model_id)


# --------------------------- START -------------------------- #

if __name__ == '__main__':
    make_model()
