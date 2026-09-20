#!/usr/bin/env python3
"""
CycleAI LSTM Training Script

Reads cycle logs from PostgreSQL, trains an LSTM model to predict
next cycle length, and saves the trained model.

Run this script whenever you have new data:
    python3 app/ml/train_lstm.py

The model is saved to app/ml/cycle_predictor.h5
A scaler is saved to app/ml/scaler.pkl (normalizes input data)
"""

import numpy as np
import sys
import os
from sqlalchemy import create_engine, text
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import joblib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping
except ImportError:
    print("TensorFlow not installed. Run: pip install tensorflow")
    sys.exit(1)

from app.core.config import settings

SEQUENCE_LENGTH = 5
MODEL_PATH = "app/ml/cycle_predictor.h5"
SCALER_PATH = "app/ml/scaler.pkl"


def fetch_cycle_data():
    """
    Fetches all cycle logs from PostgreSQL.
    Returns a dict mapping user_id to their sorted list of cycle lengths.
    """
    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT user_id, cycle_length, start_date
            FROM cycle_logs
            WHERE cycle_length IS NOT NULL
              AND cycle_length BETWEEN 21 AND 45
            ORDER BY user_id, start_date ASC
        """))
        rows = result.fetchall()

    user_cycles = {}
    for row in rows:
        uid = row[0]
        length = row[1]
        if uid not in user_cycles:
            user_cycles[uid] = []
        user_cycles[uid].append(float(length))

    return user_cycles


def create_sequences(cycle_lengths, seq_length=SEQUENCE_LENGTH):
    """
    Converts a list of cycle lengths into (input_sequence, target) pairs.

    Example with seq_length=3:
    Input: [28, 27, 29, 28, 30, 27, 28, 28]
    Creates pairs:
      ([28, 27, 29], 28)  - given first 3, predict 4th
      ([27, 29, 28], 30)  - given cycles 2-4, predict 5th
      ([29, 28, 30], 27)  - given cycles 3-5, predict 6th
      ...and so on

    This is how we turn a sequence of numbers into
    supervised learning training examples.
    """
    X, y = [], []
    for i in range(len(cycle_lengths) - seq_length):
        X.append(cycle_lengths[i:i + seq_length])
        y.append(cycle_lengths[i + seq_length])
    return np.array(X), np.array(y)


def build_model(seq_length):
    """
    Builds the LSTM neural network architecture.

    Layer by layer:
    - LSTM(64): 64 memory cells, processes the sequence
    - Dropout(0.2): randomly disables 20% of neurons during training
      to prevent overfitting (memorizing training data)
    - LSTM(32): second LSTM layer for deeper pattern learning
    - Dropout(0.2): another dropout layer
    - Dense(16): fully connected layer, combines learned features
    - Dense(1): single output neuron, predicts one cycle length
    """
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(seq_length, 1)),
        Dropout(0.2),
        LSTM(32, return_sequences=False),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1)
    ])

    model.compile(
        optimizer='adam',
        loss='mean_squared_error',
        metrics=['mae']
    )

    return model


def train():
    print("=" * 60)
    print("CycleAI LSTM Training")
    print("=" * 60)

    print("\nFetching cycle data from PostgreSQL...")
    user_cycles = fetch_cycle_data()

    if not user_cycles:
        print("No cycle data found. Insert data first.")
        return False

    total_cycles = sum(len(v) for v in user_cycles.values())
    print(f"Found {len(user_cycles)} users with {total_cycles} total cycle logs")

    all_lengths = []
    for cycles in user_cycles.values():
        all_lengths.extend(cycles)

    print(f"Cycle length range: {min(all_lengths):.0f} - {max(all_lengths):.0f} days")
    print(f"Mean cycle length: {np.mean(all_lengths):.1f} days")

    scaler = MinMaxScaler(feature_range=(0, 1))
    all_lengths_array = np.array(all_lengths).reshape(-1, 1)
    scaler.fit(all_lengths_array)

    all_X, all_y = [], []
    for uid, cycles in user_cycles.items():
        if len(cycles) < SEQUENCE_LENGTH + 1:
            print(f"  Skipping {uid}: only {len(cycles)} cycles (need {SEQUENCE_LENGTH + 1})")
            continue

        normalized = scaler.transform(np.array(cycles).reshape(-1, 1)).flatten()
        X, y = create_sequences(normalized, SEQUENCE_LENGTH)
        all_X.extend(X)
        all_y.extend(y)

    if not all_X:
        print(f"Not enough data. Need at least {SEQUENCE_LENGTH + 1} cycles per user.")
        print("Using global sequence from all available data...")

        normalized_all = scaler.transform(all_lengths_array).flatten()
        all_X, all_y = create_sequences(normalized_all, SEQUENCE_LENGTH)

        if len(all_X) == 0:
            print("Still not enough data. Need more cycle logs.")
            return False

    X = np.array(all_X).reshape(-1, SEQUENCE_LENGTH, 1)
    y = np.array(all_y)

    print(f"\nTraining samples: {len(X)}")

    if len(X) > 10:
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        validation_data = (X_val, y_val)
    else:
        X_train, y_train = X, y
        validation_data = None
        print("Small dataset: training without validation split")

    print("\nBuilding LSTM model...")
    model = build_model(SEQUENCE_LENGTH)
    model.summary()

    callbacks = [
        EarlyStopping(
            monitor='loss',
            patience=15,
            restore_best_weights=True,
            verbose=1
        )
    ]

    print("\nTraining...")
    history = model.fit(
        X_train, y_train,
        epochs=100,
        batch_size=min(8, len(X_train)),
        validation_data=validation_data,
        callbacks=callbacks,
        verbose=1
    )

    os.makedirs("app/ml", exist_ok=True)
    model.save(MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    final_loss = history.history["loss"][-1]
    print(f"\nTraining complete!")
    print(f"Final loss: {final_loss:.6f}")
    print(f"Model saved: {MODEL_PATH}")
    print(f"Scaler saved: {SCALER_PATH}")

    print("\nTesting prediction on sample data...")
    sample = np.array([28, 27, 29, 28, 30]).reshape(-1, 1)
    sample_normalized = scaler.transform(sample).reshape(1, SEQUENCE_LENGTH, 1)
    prediction_normalized = model.predict(sample_normalized, verbose=0)
    prediction = scaler.inverse_transform(prediction_normalized)[0][0]
    print(f"Sample input: [28, 27, 29, 28, 30]")
    print(f"Predicted next cycle: {prediction:.1f} days")

    return True


if __name__ == "__main__":
    success = train()
    if success:
        print("\nModel ready for Phase 10 API integration.")
    else:
        print("\nTraining failed. Check data and try again.")
