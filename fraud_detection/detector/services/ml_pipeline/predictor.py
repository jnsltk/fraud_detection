import numpy as np
from keras.models import load_model
from dataclasses import dataclass
import data_loader
import feature_transformer
import keras
import model
import json
import os
from dotenv import load_dotenv
import shap
import matplotlib.pyplot as plt  # Import matplotlib for data visualisation
import explainer

# -------------------- SETUP FEATURE FLAGS ------------------- #

load_dotenv()

USE_LOCAL_MODEL = os.getenv('USE_LOCAL_MODEL') in ('TRUE', 'True', 'true', '1')

# -------------------------- CLASSES ------------------------- #

@dataclass
class Prediction:
    probability: float
    is_fraud: bool
    reasons: list[str]


class Predictor:

    # -------------------------- PUBLIC -------------------------- #

    def predict(self, input: dict) -> Prediction:
        ''' Throws ValueError '''

        # Prepares the data
        res = feature_transformer.transform_single(input, self._col_data)
        input['euros'] = res.euros

        # Makes the prediction
        probability = model.predict(res.df, self.model)
        is_fraud = probability > 0.5

        # Explains the prediction
        reasons = explainer.explain(self.explainer, res.df, is_fraud, input)

        # Returns the prediction
        return Prediction(probability=probability, is_fraud=is_fraud, reasons=reasons)


    def __init__(self, model_id: str):
        self._load_model(model_id)
        self._setup_explainer()

    # ------------------------- PRIVATE ------------------------- #

    def _load_model(self, model_id: str) -> None:

        if USE_LOCAL_MODEL:
            self.model: keras.Model = load_model('data/model.keras')

            with open('data/metadata.json', 'r') as f:
                self._col_data: dict[str, list[str] | dict[str, float]] = json.load(f)

            self.trained_date_start = None
            self.trained_date_end = None
        else:
            raise NotImplementedError('Remote model loading not implemented yet :(')


    def _setup_explainer(self) -> None:
        self.explainer = explainer.create(self.model, self._col_data, self.trained_date_start, self.trained_date_end)


if __name__ == '__main__':

    df = data_loader.load_data(sample_size=10)

    predictor = Predictor(model_id='1')
    print('Made predictor')

    for i in range(len(df)):
        row = df.iloc[i]
        prediction = predictor.predict(row.to_dict())

        print(f'\n{i} - chance: {prediction.probability:.4f} ; oracle: {row['is_fraud']}')
        for reason in prediction.reasons:
            print(reason)
