"""
Based on https://machinelearningmastery.com/deep-learning-models-for-multi-output-regression/
"""
import os

import numpy as np
from sklearn.model_selection import RepeatedKFold
from keras.models import Sequential
from keras.layers import Dense

from misc.definitions import ROOT_DIR


# get the dataset
def load_data(name):
    return np.load(os.path.join(ROOT_DIR, "..", "data", name))


# get the model
def get_model(n_inputs, n_outputs):
    model = Sequential()
    model.add(Dense(500, input_dim=n_inputs, kernel_initializer='he_uniform', activation='relu'))
    model.add(Dense(250, kernel_initializer='he_uniform', activation='relu'))
    model.add(Dense(n_outputs))
    model.compile(loss='mae', optimizer='adam')
    return model


# evaluate a model using repeated k-fold cross-validation
def evaluate_model(X, y):
    results = list()
    n_inputs, n_outputs = X.shape[1], y.shape[1]
    # define evaluation procedure
    cv = RepeatedKFold(n_splits=10, n_repeats=2, random_state=1)
    # enumerate folds
    for train_ix, test_ix in cv.split(X):
        # prepare data
        X_train, X_test = X[train_ix], X[test_ix]
        y_train, y_test = y[train_ix], y[test_ix]
        # define model
        model = get_model(n_inputs, n_outputs)
        # fit model
        model.fit(X_train, y_train, verbose=1, epochs=100)
        # evaluate model on test set
        mae = model.evaluate(X_test, y_test, verbose=1)
        # store result
        print('>%.3f' % mae)
        results.append(mae)
        break
    return results


def visualize_input(x):
    curr_i = 0
    game_time = x[curr_i]
    curr_i += 1
    allied_minions = x[curr_i:curr_i+80]
    curr_i += 80
    enemy_minions = x[curr_i:curr_i+80]
    curr_i += 80
    player_champions = x[curr_i:curr_i+6]
    curr_i += 6
    allied_champions = x[curr_i:curr_i+24]
    curr_i += 24
    enemy_champions = x[curr_i:curr_i+30]
    curr_i += 30
    allied_objectives = x[curr_i:curr_i+15]
    curr_i += 15
    enemy_objectives = x[curr_i:curr_i+15]
    curr_i += 15
    mouse_positions = x[curr_i:curr_i+150]
    curr_i += 150
    mouse_events = x[curr_i:curr_i+15]
    curr_i += 15
    keyboard_events = x[curr_i:curr_i+20]
    curr_i += 20

    print(f"Game time: {game_time}")
    print(f"Allied minions: {allied_minions}")
    print(f"Enemy minions: {enemy_minions}")
    print(f"Player champions: {player_champions}")
    print(f"Allied champions: {allied_champions}")
    print(f"Enemy champions: {enemy_champions}")
    print(f"Allied objectives: {allied_objectives}")
    print(f"Enemy objectives: {enemy_objectives}")
    print(f"Mouse positions: {mouse_positions}")
    print(f"Mouse events: {mouse_events}")
    print(f"Keyboard events: {keyboard_events}")


def visualize_output(y):
    curr_i = 0
    mouse_positions = y[curr_i:curr_i+150]
    curr_i += 150
    mouse_events = y[curr_i:curr_i+15]
    curr_i += 15
    keyboard_events = y[curr_i:curr_i+20]
    curr_i += 20

    print(f"Mouse positions: {mouse_positions}")
    print(f"Mouse events: {mouse_events}")
    print(f"Keyboard events: {keyboard_events}")


def feature_scaling(arr):
    # Scale each of the columns
    mean = []
    std = []
    for i in range(arr.shape[1]):
        mean.append(np.mean(arr[:, i]))
        std.append(np.std(arr[:, i]))
        arr[:, i] -= mean[i]
        if std[i] != 0:
            arr[:, i] /= std[i]
    return arr, mean, std


def inverse_feature_scaling(arr, mean, std):
    for i in range(arr.shape[1]):
        arr[:, i] = arr[:, i] * std[i] + mean[i]
    return arr


# load dataset
X = load_data("batch15_in.npy")
y = load_data("batch15_out.npy")
print(f"Dataset loaded with {X.shape[0]} samples, {X.shape[1]} features, and {y.shape[1]} outputs.")

# feature scaling
X, x_mean, x_std = feature_scaling(X)
y, y_mean, y_std = feature_scaling(y)

# get model
model = get_model(X.shape[1], y.shape[1])
# fit the model on all data
model.fit(X, y, verbose=1, epochs=1000)
# evaluate the model
mae = model.evaluate(X, y, verbose=0)
# store result
print(f"MAE: {mae:.3f}")

# make a prediction
test_x = np.asarray([X[0]])
test_y = np.asarray([y[0]])
pred_y = model.predict(test_x)
np.set_printoptions(suppress=True)
print("\nInput:")
visualize_input(inverse_feature_scaling(test_x, x_mean, x_std)[0])
print("\nAnswer:")
visualize_output(inverse_feature_scaling(test_y, y_mean, y_std)[0])
print("\nPrediction:")
visualize_output(inverse_feature_scaling(pred_y, y_mean, y_std)[0])

'''
# evaluate model
# results = evaluate_model(X, y)
# summarize performance
# noinspection PyStringFormat
# print('MAE: %.3f (%.3f)' % (np.mean(results), np.std(results)))
'''
