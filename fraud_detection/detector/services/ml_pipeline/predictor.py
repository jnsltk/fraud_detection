import numpy as np
from keras.models import load_model
from dataclasses import dataclass
import data_loader
import feature_transformer
import keras
import model


@dataclass
class Prediction:
    probability: float
    is_fraud: bool
    explanation: str


class Predictor:

    # -------------------------- PUBLIC -------------------------- #

    def predict(self, input: dict) -> Prediction:
        df = feature_transformer.transform_single(input, self.stats)

        probability = model.predict(df, self.model)
        is_fraud = probability > 0.5
        explanation = f'Probability of fraud: {probability}'
        return Prediction(probability=probability, is_fraud=is_fraud, explanation=explanation)

    def __init__(self, model_id: str):
        self._load_model(model_id)
        self._load_data_stats()

    # ------------------------- PRIVATE ------------------------- #

    def _load_model(self, model_id: str) -> None:
        # temporarily load the model from local file
        self.model: keras.Model = load_model('data/model.keras')

        self.trained_date_start = '2021-10-01'
        self.trained_date_end = '2021-10-01'

    def _load_data_stats(self) -> None:
        df = data_loader.get_all()
        amount_cols = np.array(df[['amount', 'timestamp', 'currency']])

        df['euros'] = [feature_transformer.row_to_eur(row) for row in amount_cols]

        self.stats = {}

        for col in feature_transformer.NUM_COLS:
            mean = df[col].mean()
            std = df[col].std()

            self.stats[col] = feature_transformer.Stat(mean=mean, std=std)

        print(self.stats)


if __name__ == '__main__':

    df = data_loader.load_data(sample_size=1)
    print('raw', df)

    predictor = Predictor(model_id='1')
    prediction = predictor.predict(df.iloc[0].to_dict())

    print(prediction)
