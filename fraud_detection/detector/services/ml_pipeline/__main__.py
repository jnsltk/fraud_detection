from dotenv import load_dotenv
import data_loader
import feature_transformer
import tester
import model
import os
from predictor import Predictor

load_dotenv()

SAVE_MODEL_FILE = os.getenv("SAVE_MODEL_FILE") in ['TRUE', 'True', 'true', '1']


def make_model():
    df = data_loader.load_data()
    df = feature_transformer.transform_df(df)
    tester.test(df)  # throws if any test fails
    model_output = model.create(df)

    if SAVE_MODEL_FILE:
        model_output.model.save('data/model.keras')

    print(model_output)
    print(df.head())


def make_predictor() -> Predictor:
    pass


if __name__ == '__main__':
    make_model()
