import pandas
import numpy
import os

from . import extract
from .param import *

import tensorflow as tf
from keras.models import Sequential
from keras.layers.core import Dense, Activation
from keras.layers.recurrent import LSTM
from keras.optimizers import Adam
from keras.callbacks import (
    ReduceLROnPlateau,
    EarlyStopping,
    CSVLogger,
    TerminateOnNaN,
    ModelCheckpoint
)
import tensorflow.keras.backend as K
from keras import metrics

def run(data_dirpath, output_dirpath):
    train_data_dirpath = "{}/train".format(data_dirpath)
    test_data_dirpath = "{}/test".format(data_dirpath)
    train_x, train_y = _load_npy(train_data_dirpath)
    test_x, test_y = _load_npy(test_data_dirpath)
    
    model = build_model(LSTM_HIDDEN_NUM)
    csv_logger = CSVLogger("{}/logger.csv".format(output_dirpath), separator=",", append=False)
    #lr_reducer = ReduceLROnPlateau(factor=0.5, patience=5)
    #early_stopper = EarlyStopping(min_delta=0.00001, patience=10)
    nan_terminater = TerminateOnNaN()
    check_pointer = ModelCheckpoint("{}/best_model.h5".format(output_dirpath),
                                    monitor="val_loss",
                                    mode="min",
                                    save_best_only=True)
    print(train_y.sum(axis=0))
    print(test_y.sum(axis=0))
    a = test_y.sum(axis=0)
    print(a[1]/(a[0]+a[1]))
    model.fit(train_x, train_y, epochs=EPOCHS, validation_data=(test_x, test_y),
          callbacks=[csv_logger, nan_terminater, check_pointer])
    
    
def _load_npy(data_dirpath):
    data_list = []
    for filename in os.listdir(data_dirpath):
        xory, ymd, ba = filename.replace(".npy", "").split("_")
        data_list.append((ymd, ba))
    data_list = sorted(set(data_list))
    
    x_arr = None
    y_arr = None
    for d in data_list:
        ymd = d[0]
        ba = d[1]
        x = numpy.load("{}/x_{}_{}.npy".format(data_dirpath, ymd, ba))
        y = numpy.load("{}/y_{}_{}.npy".format(data_dirpath, ymd, ba))
        if x_arr is None:
            x_arr = x
            y_arr = y
        else:
            x_arr = numpy.vstack((x_arr, x))
            y_arr = numpy.vstack((y_arr, y))
    return x_arr, y_arr
    
def build_model(lstm_hidden_dim):
    model = Sequential()
    model.add(LSTM(
        lstm_hidden_dim,
        input_shape=(BACK_STEP, len(FEATURE_COLUMNS)),
        return_sequences=False, dropout=DROPOUT))
    model.add(Dense(len(TARGET_COLUMNS)))
    model.add(Activation("softmax"))
    model.compile(loss="categorical_crossentropy", optimizer=Adam(lr=0.001), metrics=["accuracy"])
    #model.compile(loss=myloss, optimizer=Adam(lr=0.001), metrics=["accuracy"])
    #model.compile(loss=myloss2, optimizer=Adam(lr=0.001), metrics=[metrics.categorical_accuracy, mymetric])
    #model.summary()
    return model

def myloss(y_true, y_pred):
    # (0.5 - t1)*([0, 1])*(-log(1-p1))
    # = (t1 - 0.5)*([0, 1]) * log(1 - p1)
    # t1正解が1のラベル, p1予測
    # p1 -> 1 and t1 = 0 => loss +
    # p1 -> 1 and t1 = 1 => loss -
    # p1 -> 0            => loss 0
    epsilon = 1.0e-6
    y_pred /= tf.reduce_sum(y_pred, axis=-1, keepdims=True)
    y_pred = tf.clip_by_value(y_pred, epsilon, 1.0 - epsilon)
    # p1=1 and t1=0 と p1=1 and t1=1 のlossのweight 0.9のときはt1=1に0.1, t1=0に0.9の重み
    const_beta = tf.constant(0.6)
    const_1 = tf.constant(1.0)
    zero = tf.constant([0.0, 1.0])
    exp1_1 = tf.subtract(y_true, const_beta)
    exp1 = tf.multiply(exp1_1, zero)
    #exp2 = tf.log(tf.subtract(const_1, y_pred))
    exp2 = tf.math.log(tf.subtract(const_1, y_pred))
    exp3 = tf.multiply(exp1, exp2)
    exp4 = tf.reduce_sum(exp3, axis=-1)
    return exp4

def myloss2(y_true, y_pred):
    reward = tf.constant(10.0)
    zero = tf.constant([0.0, 1.0])
    one = tf.constant([1.0, 0.0])
    epsilon = 1.0e-6
    y_pred /= tf.reduce_sum(y_pred, axis=-1, keepdims=True)
    y_pred = tf.clip_by_value(y_pred, epsilon, 1.0 - epsilon)
    exp1 = tf.multiply(y_pred, one)
    exp2 = tf.multiply(exp1, reward)
    exp3 = tf.multiply(exp2, y_true)

    exp4 = tf.multiply(y_pred, zero)
    exp5 = tf.add(exp3, exp4)
    exp6 = tf.reduce_sum(exp5, axis=1)
    exp7 = -tf.math.log(exp6)
    #exp8 = -tf.math.log(tf.clip_by_value(exp6, epsilon, 1.0))
    return exp7


def mymetric(y_true, y_pred):
    one = tf.constant([1.0, 0.0])
    exp1 = K.round(y_true * y_pred)
    exp2 = tf.multiply(exp1, one)
    true_positive = K.sum(exp2)

    const_one = tf.constant([1.0, 1.0])
    exp3 = tf.subtract(const_one, y_true)
    exp4 = K.round(exp3 * y_pred)
    exp5 = tf.multiply(exp4, one)
    false_positive = K.sum(exp5)
    metric = tf.divide(true_positive, tf.add(true_positive, false_positive) + 0.001)
    return metric
