'''
    This module is the main entry point for the ml_pipeline service.
    It provides all the necessary functions to train a model and make predictions.
'''

# -------------------------- IMPORTS ------------------------- #

import sys
sys.path.append('detector/services/ml_pipeline')

from dotenv import load_dotenv
import _data_loader
import _feature_transformer
import _tester
import _model
import os
from _predictor import Predictor
import json
from dataclasses import dataclass
import keras
from datetime import datetime

# -------------------------- CLASSES ------------------------- #


@dataclass
class ModelDetails:
    model: keras.Model
    test_result: dict
    metadata: dict
    true_sample_size: int = 0


# ---------------------- SETUP FEATURE FLAGS --------------------- #

load_dotenv()

SAVE_MODEL_FILE = os.getenv("SAVE_MODEL_FILE") in ['TRUE', 'True', 'true', '1']

# --------------------- PUBLIC FUNCTIONS --------------------- #


def make_model(start_data_date=None, end_data_date=None, sample_size: int = 20000) -> ModelDetails:
    ''' 
        Trains a new model for the data interval specified.
        Needs to be run within try-except block to catch any errors.
    '''

    df = _data_loader.load_data(start=start_data_date, end=end_data_date, sample_size=sample_size)

    res = _feature_transformer.transform_df(df, col_data=None)

    # Combines stats and categories dictionaries
    metadata = res.stats | res.categories

    # Note - Throws if any test fails, but they should not unless bugs
    _tester.test(res.df)

    model_output = _model.create(res.df)

    if SAVE_MODEL_FILE:
        parent = ''      

        if not os.path.exists('data'):
            parent = 'detector/services/ml_pipeline/'

        model_output.model.save(f'{parent}data/model.keras')

        with open(f'{parent}data/metadata.json', 'w') as f:
            json.dump(metadata, f, indent=4)

        print('Saved model and metadata locally to data/')

    return ModelDetails(model=model_output.model, test_result=model_output.test_result, metadata=metadata, true_sample_size=df.shape[0])


def make_predictor(model_id: str, model_details: ModelDetails = None) -> Predictor:
    ''' 
        Makes a predictor based on either the provided model id, or the output from make_model().
        Needs to be run within try-except block to catch any errors.
    '''

    if model_details:
        return Predictor(model_id, model_details.model, model_details.metadata)
    else:
        return Predictor(model_id)


# --------------------------- START - (for testing) -------------------------- #

if __name__ == '__main__':
    output = make_model(start_data_date=datetime(2024, 12, 3), end_data_date=datetime(2024, 12, 6), sample_size=10000)

    predictor = make_predictor('probably does not matter', output)
    df = _data_loader.load_data(sample_size=1)
    predictor = Predictor(model_id='1')

    for i in range(len(df)):
        row = df.iloc[i]
        prediction = predictor.predict(row.to_dict())

        print(f'\n{i} - chance: {prediction.probability:.4f} ; oracle: {row['is_fraud']}')
        for reason in prediction.reasons:
            print(reason)
