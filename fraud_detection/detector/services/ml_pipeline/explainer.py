import shap
import keras
import data_loader
import feature_transformer
import numpy as np
import pandas as pd


def create(model: keras.Model, col_data, start_data_date, end_data_date) -> shap.Explainer:
    print('Loading data for SHAP explainer...')
    data_sample = data_loader.load_data(sample_size=500, start=start_data_date, end=end_data_date)

    res = feature_transformer.transform_df(data_sample, col_data=col_data)
    arr = np.array(res.df, dtype='float32')
    x_matrix = arr[:, :-1]

    print('Training SHAP explainer...')
    return shap.DeepExplainer(model, x_matrix)


def explain(explainer: shap.Explainer, data: pd.DataFrame, is_fraud: bool, raw_input: dict) -> np.array:
    # Prepares the data
    arr = np.array(data, dtype='float32')
    columns = np.array(data.columns.tolist())  # TODO - save instead of recalculating
    values = arr[0]

    # Explains the prediction
    shap_values = np.array(explainer.shap_values(arr).flatten())

    # Selects the most relevant features
    sorted_idx = np.argsort(shap_values)
    relevant_idx = sorted_idx[-5:][::-1] if is_fraud else sorted_idx[:5]

    # Finds info about the relevant features
    relavent_shap_values = shap_values[relevant_idx]
    relavent_columns = columns[relevant_idx]
    relavent_values = values[relevant_idx]

    reasons = []

    # Note - The most two relevant features are always included
    for i in range(2):
        description = _describe_explanation(relavent_shap_values[i], relavent_columns[i], relavent_values[i], raw_input, is_fraud)
        reasons.append(description)

    # Note - Three more features are included if their absolute contribution is above 5%
    for i in range(2, 5):
        if np.abs(relavent_shap_values[i]) > 0.05:
            description = _describe_explanation(relavent_shap_values[i], relavent_columns[i], relavent_values[i], raw_input, is_fraud)
            reasons.append(description)

    return reasons


def _describe_explanation(shap_value: float, column: str, value: float, raw_input: dict, is_fraud: bool) -> str:
    ''' Returns a human-readable description of the explanation '''

    feature, _, category = column.partition('=')
    raw_input_value = raw_input.get(feature)

    feature_print = feature.replace('_', ' ')
    shap_str = f'{round(abs(shap_value) * 100)}%'
    altered_str = 'increased' if is_fraud else 'decreased'

    if feature == 'euros':
        return f'The amount being equivalent to {float(raw_input_value):.2f}€, {altered_str} the probability of fraud by {shap_str}'

    if feature in feature_transformer.CAT_COLS:
        return f'The {feature_print} {'' if value else 'not '}being "{category}", {altered_str} the probability of fraud by {shap_str}'

    elif feature in feature_transformer.NUM_COLS:
        return f'The {feature_print} being {raw_input_value:.2f}, {altered_str} the probability of fraud by {shap_str}'
    
    elif feature in feature_transformer.BOOL_COLS:
        return f'"{feature_print.capitalize()}" {'' if value else 'not '}being selected, {altered_str} the probability of fraud by {shap_str}'

    else:
        raise ValueError(f'Unknown feature: {feature}')
