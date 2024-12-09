# noinspection PyUnresolvedReferences
from keras.models import load_model
from dataclasses import dataclass
import _data_loader
import _feature_transformer
import keras
import _model
import json
import os
from dotenv import load_dotenv
import _explainer

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
    ''' 
        This class serves as a stateful predictor for fraud detection.
        It will set everything up when instantiated, and then can be used to make predictions.
    '''

    # -------------------------- PUBLIC -------------------------- #

    def predict(self, input: dict) -> Prediction:
        ''' Throws ValueError '''

        # Prepares the data
        res = _feature_transformer.transform_single(input, self._col_data)

        # Adds calculated features to the input for use in the explainer
        input['euros'] = res.euros
        input['hour_sin'] = res.hour_sin
        input['hour_cos'] = res.hour_cos

        # Makes the prediction
        probability = _model.predict(res.df, self._model)
        is_fraud = probability > 0.5

        # Explains the prediction
        reasons = _explainer.explain(self.explainer, res.df, is_fraud, input)

        # Returns the prediction
        return Prediction(probability=probability, is_fraud=is_fraud, reasons=reasons)


    def __init__(self, model_id: str, model: keras.Model = None, metadata: dict = None):
        if model is not None and metadata is not None:
            self._model = model
            self._col_data = metadata
        else:
            self._load_model(model_id)

        self._setup_explainer()

    # ------------------------- PRIVATE ------------------------- #

    def _load_model(self, model_id: str) -> None:

        if USE_LOCAL_MODEL:
            self._model: keras.Model = load_model('data/model.keras')

            with open('data/metadata.json', 'r') as f:
                self._col_data: dict[str, list[str] | dict[str, float]] = json.load(f)

        else:
            raise NotImplementedError('Remote model loading not implemented yet :(')


    # Note - Ideally the explainer should be loaded from the database, but the library is immature and 
    #        doing so is very problematic for multiple reasons including lacking documentation and what seems to be a bug.
    #        Now, it will be re-created every time a backend start, which is good enough.
    def _setup_explainer(self) -> None:
        if self._model is None:
            raise ValueError('Model is not loaded yet.')
        
        self.explainer = _explainer.create(self._model, self._col_data)


if __name__ == '__main__':

    df = _data_loader.load_data(sample_size=10)

    predictor = Predictor(model_id='1')

    for i in range(len(df)):
        row = df.iloc[i]
        prediction = predictor.predict(row.to_dict())

        print(f'\n{i} - chance: {prediction.probability:.4f} ; oracle: {row['is_fraud']}')
        for reason in prediction.reasons:
            print(reason)
