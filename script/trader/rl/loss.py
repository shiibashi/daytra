import numpy

epsilon = 0.001

def log_loss(y_true, y_pred):
    y_true = numpy.clip(y_true, epsilon, 1 - epsilon)
    y_pred = numpy.clip(y_pred, epsilon, 1 - epsilon)
    minus_loss = y_true * numpy.log(y_pred)
    return -minus_loss.mean()
