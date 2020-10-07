from . import noisy_dense
import keras
from keras.layers.core import Dense, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D, Concatenate, Dropout, Lambda, Add
from keras.layers.normalization import BatchNormalization
from keras import Input, Sequential
from keras.models import model_from_config
from keras.optimizers import SGD, Adam
from keras import backend as K
import tensorflow as tf


def nn(action_size, feature_size, dueling, noisy_dense):
    print("action_size = {}".format(action_size), flush=True)
    print("dueling = {}".format(dueling), flush=True)
    print("noisy_dense = {}".format(noisy_dense), flush=True)
    
    dueling_str = "1" if dueling else "0"
    noisy_dense_str = "1" if noisy_dense else "0"
    key = "{}{}".format(dueling_str, noisy_dense_str)
    print(key)
    if key == "00":
        model = model_00(action_size, feature_size)
    elif key == "01":
        model = model_01(action_size, feature_size)
    elif key == "10":
        model = model_10(action_size, feature_size)
    elif key == "11":
        model = model_11(action_size, feature_size)
    model.summary()
    return model

def logloss(y_true, y_pred):
    epsilon = 0.001
    y_true = K.clip(y_true, epsilon, 1 - epsilon)
    y_pred = K.clip(y_pred, epsilon, 1 - epsilon)
    term = y_true * K.log(y_pred)
    loss = -K.sum(term, -1)
    return loss

def model_00(action_size, feature_size):
    input_x = Input(name="input", shape=(feature_size, ))
    x = Dense(16, activation="relu", name="dense_1")(input_x)
    x = Dense(8, activation="relu", name="dense_2")(x)
    out = Dense(action_size, name="output")(x)
    model = keras.Model(input_x, out)
    model.compile(Adam(), loss="mse")
    return model

def model_01(action_size, feature_size):
    input_x = Input(name="input", shape=(feature_size, ))
    x = Dense(16, activation="relu", name="dense_1")(input_x)
    x = Dense(8, activation="relu", name="dense_2")(x)
    out = noisy_dense.NoisyDense(action_size,
        activation="linear",
        kernel_initializer="lecun_uniform",
        bias_initializer="lecun_uniform",
        name="output")(x)
    model = keras.Model(input_x, out)
    model.compile(Adam(), loss="mse")
    return model


def model_10(action_size, feature_size):
    input_x = Input(name="input", shape=(feature_size, ))
    x = Dense(16, activation="relu", name="dense_1")(input_x)
    x = Dense(8, activation="relu", name="dense_2")(x)
    value = Dense(8, activation="relu", name="head_value")(x)
    advantage = Dense(8, activation="relu", name="head_advantage")(x)
    value = Dense(1, name="value")(value)
    advantage = Dense(action_size, name="advantage")(advantage)
    concat = Concatenate()([value, advantage])
    out = Lambda(lambda a: K.expand_dims(a[:, 0], -1) + a[:, 1:] - K.mean(a[:, 1:], axis=1, keepdims=True),
                output_shape=(action_size, )
    )(concat)
    #model = keras.Model(input=input_x, output=out) # keras==2.2.5
    model = keras.Model(input_x, out)
    model.compile(Adam(), loss="mse")
    return model


def model_11(action_size, feature_size):
    input_x = Input(name="input", shape=(feature_size, ))
    #x = Dense(32, activation="relu", name="dense_1")(input_x)

    #value = Dense(16, activation="relu", name="head_value")(x)
    #advantage = Dense(16, activation="relu", name="head_advantage")(x)

    x = Dense(8, activation="relu", name="dense_1")(input_x)

    value = Dense(4, activation="relu", name="head_value")(x)
    advantage = Dense(4, activation="relu", name="head_advantage")(x)

    value = Dense(1, name="value")(value)
    advantage = noisy_dense.NoisyDense(action_size,
        activation="linear",
        kernel_initializer="lecun_uniform",
        bias_initializer="lecun_uniform",
        name="advantage")(advantage)

    concat = Concatenate()([value, advantage])
    out = Lambda(lambda a: K.expand_dims(a[:, 0], -1) + a[:, 1:] - K.mean(a[:, 1:], axis=1, keepdims=True),
                output_shape=(action_size, )
    )(concat)
    model = keras.Model(input_x, out)
    model.compile(Adam(), loss="mse")
    return model

