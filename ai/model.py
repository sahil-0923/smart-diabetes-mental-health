import os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

def build_gru_model(input_shape=(36, 5), output_units=2, learning_rate=0.001):
    """
    Builds a lightweight, robust Gated Recurrent Unit (GRU) model
    for multi-horizon glucose forecasting (30-min and 60-min).
    """
    model = keras.Sequential([
        layers.Input(shape=input_shape),
        layers.GRU(64, return_sequences=True, name="gru_layer_1"),
        layers.Dropout(0.2, name="dropout_1"),
        layers.GRU(32, return_sequences=False, name="gru_layer_2"),
        layers.Dropout(0.2, name="dropout_2"),
        layers.Dense(32, activation="relu", name="dense_1"),
        layers.Dense(output_units, activation="linear", name="output_forecast")
    ], name="DiabetesAI_GRU_Forecaster")
    
    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss=keras.losses.Huber(delta=1.0),
        metrics=["mae", keras.metrics.RootMeanSquaredError(name="rmse")]
    )
    
    return model

if __name__ == "__main__":
    model = build_gru_model()
    model.summary()
