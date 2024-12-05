# --------------------- IMPORTS LIBRARIES -------------------- #

# misc
import pandas as pd  # Import Pandas for data manipulation using dataframes
import numpy as np  # Import Numpy for data statistical analysis
import matplotlib.pyplot as plt  # Import matplotlib for data visualisation
import seaborn as sns
from dataclasses import dataclass
import os
from dotenv import load_dotenv
import tensorflow as tf
import random

# sklearn
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix

# Keras
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout

# -------------------------- CLASSES ------------------------- #


@dataclass
class ModelOutput:
    model: keras.Model
    test_result: dict


# --------------------------- SETUP -------------------------- #

load_dotenv()
SHOW_PLOTS = os.getenv('SHOW_PLOTS') in ('TRUE', 'True', 'true', '1')
VERBOSE = os.getenv('VERBOSE') in ('TRUE', 'True', 'true', '1')

# Ensures reproducibility
np.random.seed(42)
tf.random.set_seed(42)
random.seed(42)

# ------------------------- PUBLIC FUNCTIONS ------------------------ #


def create(df: pd.DataFrame) -> ModelOutput:
    # note - random_state is the seed for shuffling
    df_train, df_test = train_test_split(df, test_size=0.3, random_state=42)

    # Create training and testing arrays
    training = np.array(df_train, dtype='float32')
    testing = np.array(df_test, dtype='float32')

    model = _train(training)
    test_result = _test(testing, model)

    return ModelOutput(model=model, test_result=test_result)


def predict(df: pd.DataFrame, model: keras.Model) -> float:
    input = np.array(df, dtype='float32')
    return model.predict(input, verbose=False)[0][0]


# ------------------------- PRIVATE FUNCTIONS ------------------------ #


def _train(training: np.ndarray) -> keras.Model:

    # Prepare the training dataset
    X_train = training[:, :-1]
    y_train = training[:, -1:]

    X_train, X_validate, y_train, y_validate = train_test_split(X_train, y_train, test_size=0.2, random_state=42)

    model = Sequential([
        Dense(90, activation='relu'),
        Dropout(0.2),
        Dense(50, activation='relu'),
        Dense(20, activation='relu'),
        Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer='adam', loss=keras.losses.binary_crossentropy, metrics=['accuracy'])

    # Note - Reduces false negatives
    class_weights = compute_class_weight('balanced', classes=np.unique(y_validate), y=y_validate[:, 0])
    class_weights_dict = dict(enumerate(class_weights))

    model.fit(X_train,
              y_train,
              validation_data=(X_validate, y_validate),
              epochs=15,
              batch_size=128,
              class_weight=class_weights_dict,
              verbose=VERBOSE)

    return model


def _test(testing: np.ndarray, model: keras.Model) -> dict:
    # Prepare the testing dataset
    X_test = testing[:, :-1]
    y_test = testing[:, -1:]

    y_pred = model.predict(X_test, verbose=False)
    predicted_classes = (y_pred > 0.5).astype(int)

    if SHOW_PLOTS:
        _plot(y_test, predicted_classes)

    target_names = ["Class {}".format(i) for i in range(2)]
    return classification_report(y_test,
                                 predicted_classes,
                                 target_names=target_names,
                                 output_dict=True,
                                 zero_division=0)


def _plot(y_test, predictions):
    # use seaborn library to plot the confusion matrix
    matrix = confusion_matrix(y_test, predictions)

    sns.heatmap(matrix, annot=True, fmt='d')
    plt.xlabel('Predicted labels')
    plt.ylabel('True labels')
    plt.title('Confusion Matrix')
    plt.show()
