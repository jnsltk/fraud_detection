''' imports libraries '''

# misc
import pandas as pd # Import Pandas for data manipulation using dataframes
import numpy as np # Import Numpy for data statistical analysis 
import matplotlib.pyplot as plt # Import matplotlib for data visualisation
import seaborn as sns
import random
from currency_converter import CurrencyConverter, ECB_URL
from datetime import datetime
import urllib.request # for obtaining currency data

# sklearn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix

# Keras
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.optimizers import Adam
from keras.callbacks import TensorBoard

''' defines functions for feature transformation '''

def one_hot_encode(feature):
    global df_enabled

    if not feature in df_enabled.columns: 
        print(f'WARN: tried to one-hot encode missing feature {feature}')
        return

    # prefix appends feature name to each categorie's column
    one_hot = pd.get_dummies(df_enabled[feature], prefix=feature)

    # adds one boolean column for each discrete value
    df_enabled = pd.concat([df_enabled, one_hot], axis=1)

    # drops previous column
    df_enabled.drop(feature, axis=1, inplace=True)


# note - uses mean normalisation
def normalise(feature):
    global df_enabled

    if not feature in df_enabled.columns: 
        print(f'WARN: tried to normalise missing feature {feature}')
        return

    feature_row = df_enabled[feature]
    df_enabled[f'{feature}'] = (feature_row - feature_row.mean()) / (feature_row.max() - feature_row.min())
    df_enabled.rename(columns={feature: f'{feature}_normalised'}, inplace=True)
    
''' dataframes creation for both training and testing datasets '''

df = pd.read_csv('data/dataset_sample.csv',sep=',')

# selects features
enabled_features = [
    'merchant_category', 
    'merchant_type', 
    'country', 
    'currency', 
    'city_size', 
    'amount', 
    'distance_from_home', 
    'transaction_hour',
    'weekend_transaction',
    'high_risk_merchant',
    'card_type'
]
df_enabled = df[enabled_features].copy()

''' Creates feature for value in Euros '''

# sets up currency converter with recent data
urllib.request.urlretrieve(ECB_URL, 'data/eurofxref-hist.zip')
c = CurrencyConverter('data/eurofxref-hist.zip', fallback_on_missing_rate=True, fallback_on_wrong_date=True)


def toEUR(row):
    if row[2] == 'NGN': # note - the ECB does not have NGN for some reason
        return row[0] * 0.00057 
    else:
        return c.convert(row[0], row[2], date=datetime.fromisoformat(row[1]))


amount_cols = np.array(df[['amount', 'timestamp', 'currency']])
euro = np.array([ toEUR(row) for row in amount_cols ])

df_enabled['euros'] = euro

# normalises features
for feature in ['amount', 'distance_from_home', 'transaction_hour', 'euros']:
    normalise(feature)

# one-hot encodes features
for feature in ['merchant_category', 'merchant_type', 'country', 'currency', 'city_size', 'card_type']:
    one_hot_encode(feature)

# adds the label to the last position
df_enabled['is_fraud'] = df['is_fraud']

# prints overview
print(df_enabled.shape)
print(df_enabled.columns)

# throws if is_fraud column is not last
if df_enabled.columns[-1] != 'is_fraud':
    raise Exception('Invalid label-column')

# throws if unhandled null-values
sum_of_nulls = df_enabled.isnull().sum().sum()
if sum_of_nulls > 0: 
    raise Exception(f'{sum_of_nulls} unhandled null-values')

# note - random_state is the seed for shuffling
df_train, df_test = train_test_split(df_enabled, test_size=0.3, random_state=42)

# Create training and testing arrays
training = np.array(df_train, dtype = 'float32')
testing = np.array(df_test, dtype='float32')

# Prepare the training and testing dataset 
X_train = training[:,:-1]
y_train = training[:,-1:]

X_test = testing[:,:-1]
y_test = testing[:,-1:]

# validation dataset that might used to help the model to generalize
X_train, X_validate, y_train, y_validate = train_test_split(X_train, y_train, test_size = 0.2, random_state = 32415)

model = Sequential([
    Dense(90, activation='relu'),
    Dropout(0.2),
    Dense(50, activation='relu'),
    Dense(20, activation='relu'),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss=keras.losses.binary_crossentropy, metrics=['accuracy'])

# note - reduces false negatives
class_weights = compute_class_weight('balanced', classes=np.unique(y_validate), y=y_validate[:, 0])
class_weights_dict = dict(enumerate(class_weights))

history = model.fit(
    X_train, 
    y_train, 
    validation_data=(X_validate, y_validate), 
    epochs=15, batch_size=128, 
    class_weight=class_weights_dict
)

print('Last validation accuracy:')
last_epoch_accuracy = history.history['val_accuracy'][-1]
print(f'{last_epoch_accuracy:.4f}')
print('Test accuracy:')
test_loss, test_acc = model.evaluate(X_test, y_test, verbose=1)

y_pred = model.predict(X_test)
predicted_classes = (y_pred > 0.5).astype(int)

# use seaborn library to plot the confusion matrix 
matrix = confusion_matrix(y_test, predicted_classes)

sns.heatmap(matrix, annot=True, fmt='d')
plt.xlabel('Predicted labels')
plt.ylabel('True labels')
plt.title('Confusion Matrix')
plt.show()

# Sum the diagonal element to get the total true correct values
identity = np.eye(matrix.shape[0])
diagonal = np.multiply(matrix, identity)
sum_correct = np.sum(diagonal)
sum_total = np.sum(matrix)
print(f'Correct guesses: {sum_correct:.0f} out of {sum_total:.0f}')

target_names = ["Class {}".format(i) for i in range(2)]
print(classification_report(y_test, predicted_classes, target_names = target_names))