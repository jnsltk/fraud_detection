''' Creates and uses a SHAP explainer to explain the predictions of the model '''

import shap
import keras
import _data_loader
import _feature_transformer
import numpy as np
import pandas as pd

MIN_EXPLANATIONS = 3
MAX_EXPLANATIONS = 7


def create(model: keras.Model, col_data) -> shap.Explainer:
    print('Loading data for SHAP explainer...')
    data_sample = _data_loader.load_data(sample_size=1000)

    transform_res = _feature_transformer.transform_df(data_sample, col_data=col_data)
    arr = np.array(transform_res.df, dtype='float32')
    x_matrix = arr[:, :-1]

    print('Training SHAP explainer...')
    return shap.DeepExplainer(model, x_matrix)


def explain(explainer: shap.Explainer, data: pd.DataFrame, is_fraud: bool, raw_input: dict) -> np.array:
    # Prepares the data
    arr = np.array(data, dtype='float32')
    columns = data.columns.to_numpy()
    values = arr[0]

    # Explains the prediction
    shap_values = np.array(explainer.shap_values(arr).flatten())

    # Selects the most relevant features
    sorted_idx = np.argsort(shap_values)
    relevant_idx = sorted_idx[-MAX_EXPLANATIONS:][::-1] if is_fraud else sorted_idx[:MAX_EXPLANATIONS]

    # Finds info about the relevant features
    relavent_shap_values = shap_values[relevant_idx]
    relavent_columns = columns[relevant_idx]
    relavent_values = values[relevant_idx]

    # Group contributions for time-related features
    time_related_features = {"hour_sin", "hour_cos", "transaction_hour"}
    time_shap_value = 0
    time_contributed = False
    time_reason = ""
    time_value = values[columns.tolist().index("transaction_hour")]

    for i in range(len(relavent_columns)):
        if relavent_columns[i] in time_related_features:
            time_shap_value += relavent_shap_values[i]
            time_contributed = True

    if time_contributed and np.abs(time_shap_value) >= 0.05:
        time_reason = _describe_explanation(time_shap_value, "transaction_hour", time_value, raw_input, is_fraud)

    reasons = []

    # Note - The n most relevant features are always included
    for i in range(MIN_EXPLANATIONS):
        if relavent_columns[i] in time_related_features:
            continue
        description = _describe_explanation(relavent_shap_values[i], relavent_columns[i], relavent_values[i], raw_input, is_fraud)
        reasons.append(description)

    # Note - More features are included if their absolute contribution is more or equal to 5%
    for i in range(MIN_EXPLANATIONS, MAX_EXPLANATIONS):
        if relavent_columns[i] in time_related_features:
            continue
        if np.abs(relavent_shap_values[i]) >= 0.05:
            description = _describe_explanation(relavent_shap_values[i], relavent_columns[i], relavent_values[i], raw_input, is_fraud)
            reasons.append(description)
        else:
            break

    if time_reason != "":
        reasons.append(time_reason)

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

    elif feature in _feature_transformer.CAT_COLS:
        return f'The {feature_print} {'' if value else 'not '}being "{category}", {altered_str} the probability of fraud by {shap_str}'

    elif feature in _feature_transformer.NUM_COLS:
        return f'The {feature_print} being {raw_input_value:.2f}, {altered_str} the probability of fraud by {shap_str}'
    
    elif feature in _feature_transformer.BOOL_COLS:
        return f'"{feature_print.capitalize()}" {'' if value else 'not '}being selected, {altered_str} the probability of fraud by {shap_str}'

    else:
        raise ValueError(f'Unknown feature: {feature}')
