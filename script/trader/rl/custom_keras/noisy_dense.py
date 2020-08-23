from keras import backend as K
from keras.layers import Dense
from keras.engine.base_layer import InputSpec
from keras import initializers

# 追加
import tensorflow as tf


# Eigene Implementierung einer NoisyDense Layer sowie einer NoisyConv2D Layer, welche modifizierte Versionen der
# entsprechenden Keras-Layers sind, deren Implementierung als Grundlage benutzt wurde.

#https://github.com/chucnorrisful/dqn/blob/master/noisyNetLayers.py

class NoisyDense(Dense):
    def __init__(self, units, **kwargs):
        self.output_dim = units
        super(NoisyDense, self).__init__(units, **kwargs)

    def build(self, input_shape):
        assert len(input_shape) >= 2
        self.input_dim = input_shape[-1]

        self.kernel = self.add_weight(shape=(self.input_dim, self.units),
                                      initializer=self.kernel_initializer,
                                      name='kernel',
                                      regularizer=None,
                                      constraint=None)

        # Zweiter Kernel (trainable weights) fur Steuerung des Zufalls.
        self.kernel_sigma = self.add_weight(shape=(self.input_dim, self.units),
                                      initializer=initializers.Constant(0.017),
                                      name='sigma_kernel',
                                      regularizer=None,
                                      constraint=None)

        if self.use_bias:
            self.bias = self.add_weight(shape=(self.units,),
                                        initializer=self.bias_initializer,
                                        name='bias',
                                        regularizer=None,
                                        constraint=None)

            # trainable, Steuerung des Zufalls des Bias.
            self.bias_sigma = self.add_weight(shape=(self.units,),
                                        initializer=initializers.Constant(0.017),
                                        name='bias_sigma',
                                        regularizer=None,
                                        constraint=None)
        else:
            self.bias = None

        self.input_spec = InputSpec(min_ndim=2, axes={-1: self.input_dim})
        self.built = True

    def call(self, inputs):
        # Erzeugen der Matrix mit Zufallszahlen (bei jedem Aufruf neu erzeugt) - Vektor-Version
        # (siehe Noisy Nets Paper) ware effizienter.
        self.kernel_epsilon = K.random_normal(shape=(self.input_dim, self.units))

        # 変更
        #w = self.kernel + K.tf.multiply(self.kernel_sigma, self.kernel_epsilon)
        w = self.kernel + tf.multiply(self.kernel_sigma, self.kernel_epsilon)

        output = K.dot(inputs, w)

        if self.use_bias:
            # Erzeugung Zufallsvektor fur Bias-Zufall.
            self.bias_epsilon = K.random_normal(shape=(self.units,))

            # 変更
            #b = self.bias + K.tf.multiply(self.bias_sigma, self.bias_epsilon)
            b = self.bias + tf.multiply(self.bias_sigma, self.bias_epsilon)

            output = output + b
        if self.activation is not None:
            output = self.activation(output)
        return output
