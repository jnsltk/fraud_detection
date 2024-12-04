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
        df = feature_transformer.transform_single(input, self.stats, self.categories)

        probability = model.predict(df, self.model)
        is_fraud = probability > 0.5
        explanation = f'Probability of fraud: {probability}'
        return Prediction(probability=probability, is_fraud=is_fraud, explanation=explanation)


    def __init__(self, model_id: str):
        self._load_model(model_id)
        self._load_data_stats()
        self._load_categories()

    # ------------------------- PRIVATE ------------------------- #

    def _load_model(self, model_id: str) -> None:
        # temporarily load the model from local file
        self.model: keras.Model = load_model('data/model.keras')

        self.trained_date_start = '2021-10-01'
        self.trained_date_end = '2021-10-01'


    def _load_data_stats(self) -> None:
        df = data_loader.get_all()
        amount_cols = np.array(df[['amount', 'timestamp', 'currency']])

        df['euros'] = [feature_transformer.row_to_eur(row, None) for row in amount_cols]

        self.stats = {}

        for col in feature_transformer.NUM_COLS:
            mean = df[col].mean()
            std = df[col].std()

            self.stats[col] = feature_transformer.Stat(mean=mean, std=std)


    def _load_categories(self) -> None:
        self.categories = {}

        for col in feature_transformer.CAT_COLS:
            self.categories[col] = data_loader.get_unique(col, feature_transformer.CAT_COLS) + [feature_transformer.UNKNOWN]


if __name__ == '__main__':

    df = data_loader.load_data(sample_size=10)
    df.drop(columns=['is_fraud'], inplace=True)

    predictor = Predictor(model_id='1')
    print('Made predictor')

    for i in range(len(df)):
        row = df.iloc[i]
        prediction = predictor.predict(row.to_dict())
        print(f'{i}th chance of fraud is: {prediction.probability:.4f} with oracle:  {row['is_fraud']}')
