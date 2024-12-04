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

# -------------------- SETUP FEATURE FLAGS ------------------- #

load_dotenv()

USE_LOCAL_MODEL = os.getenv('USE_LOCAL_MODEL') in ('TRUE', 'True', 'true', '1')

# -------------------------- CLASSES ------------------------- #

@dataclass
class Prediction:
    probability: float
    is_fraud: bool
    explanation: str


class Predictor:

    # -------------------------- PUBLIC -------------------------- #

    def predict(self, input: dict) -> Prediction:
        ''' Throws ValueError '''

        df = feature_transformer.transform_single(input, self._col_data)

        probability = model.predict(df, self.model)
        is_fraud = probability > 0.5
        explanation = f'Probability of fraud: {probability}'
        return Prediction(probability=probability, is_fraud=is_fraud, explanation=explanation)


    def __init__(self, model_id: str):
        self._load_model(model_id)

    # ------------------------- PRIVATE ------------------------- #

    def _load_model(self, model_id: str) -> None:

        if USE_LOCAL_MODEL:
            self.model: keras.Model = load_model('data/model.keras')

            with open('data/metadata.json', 'r') as f:
                self._col_data: dict[str, list[str] | dict[str, float]] = json.load(f)

            self.trained_date_start = '2021-10-01'
            self.trained_date_end = '2021-10-01'
        else:
            raise NotImplementedError('Remote model loading not implemented yet :(')


if __name__ == '__main__':

    df = data_loader.load_data(sample_size=10)

    predictor = Predictor(model_id='1')
    print('Made predictor')

    for i in range(len(df)):
        row = df.iloc[i]
        prediction = predictor.predict(row.to_dict())
        print(f'{i}th chance of fraud is: {prediction.probability:.4f} with oracle:  {row['is_fraud']}')
