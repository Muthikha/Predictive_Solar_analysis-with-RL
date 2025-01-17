# -*- coding: utf-8 -*-
"""Combining RL and ANN

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ck_Fvttoc4DKf9dWF4hffWR90HybIbz6
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from google.colab import files
import io

# Function to implement the Q-learning algorithm
def q_learning(num_episodes, learning_rate, discount_factor, epsilon, ac_power_data, merged_data):
    num_states = len(ac_power_data)  # Number of states in the RL problem
    num_actions = 3  # Number of actions in the RL problem

    q_table = np.zeros((num_states, num_actions))

    for episode in range(num_episodes):
        state = 0  # Initial state

        for _ in range(max_steps):
            # Choose action using epsilon-greedy policy
            if np.random.uniform(0, 1) < epsilon:
                action = np.random.randint(num_actions)
            else:
                action = np.argmax(q_table[state])

            # Perform action and observe next state and reward
            next_state = state + 1 if state < num_states - 1 else state
            reward = get_reward(state, action, ac_power_data, merged_data)

            # Update Q-table using the Q-learning update rule
            q_table[state, action] += learning_rate * (
                reward + discount_factor * np.max(q_table[next_state]) - q_table[state, action]
            )

            state = next_state

    return q_table

# Function to get the reward for a given state and action
def get_reward(state, action, ac_power_data, merged_data):
    actual_ac_power = ac_power_data.loc[state, 'power(kW)']
    predicted_solar_power = merged_data.loc[state, 'Predicted Solar Power']

    deviation = actual_ac_power - predicted_solar_power
    reward = -deviation  # Example: Negative deviation as reward (encourage closer match)

    return reward

# Upload the "V1.csv" file
uploaded = files.upload()

# Read the uploaded file
for filename in uploaded.keys():
    data = pd.read_csv(io.BytesIO(uploaded[filename]), delimiter=',')
    print(data.columns)  # Print the column names to identify the correct column name

# Preprocess the training data
# ...

# Split the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(data.drop('Solar_power', axis=1),
                                                    data['Solar_power'],
                                                    test_size=0.2,
                                                    random_state=42)

# Train the ANN model for solar power prediction
model = Sequential()
model.add(Dense(128, activation='relu', input_shape=(X_train.shape[1],)))
model.add(Dense(256, activation='relu'))
model.add(Dense(512, activation='relu'))
model.add(Dense(512, activation='relu'))
model.add(Dense(256, activation='relu'))
model.add(Dense(128, activation='relu'))
model.add(Dense(1, activation='linear'))

model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(X_train, y_train, epochs=50, batch_size=32)

# Predict solar power using the trained ANN model
predictions = model.predict(X_test)
predictions_df = pd.DataFrame(predictions, columns=['Predicted Solar Power'])

# Merge predicted solar power with the uploaded prediction data
merged_data = pd.merge(data, predictions_df, left_index=True, right_index=True)

# Save the merged data as a CSV file
merged_data.to_csv('merged_data.csv', index=False)

# Manually upload the "ac_power_data.csv" file
ac_power_data = files.upload()

# Read the uploaded AC power data
for filename in ac_power_data.keys():
    if filename.endswith('.csv'):
        ac_power_data = pd.read_csv(io.BytesIO(ac_power_data[filename]), delimiter=',')
    elif filename.endswith('.xlsx'):
        ac_power_data = pd.read_excel(io.BytesIO(ac_power_data[filename]))

# Create the AC power data DataFrame with Decision column
ac_power_data['Decision'] = ""

# Parameters for Q-learning
num_episodes = 1000  # Number of episodes for Q-learning
learning_rate = 0.1  # Learning rate
discount_factor = 0.9  # Discount factor (controls the importance of future rewards)
epsilon = 0.1  # Exploration-exploitation trade-off parameter
max_steps = len(ac_power_data)  # Maximum number of steps in an episode

# Get the Q-table using Q-learning
q_table = q_learning(num_episodes, learning_rate, discount_factor, epsilon, ac_power_data, merged_data)

# RL algorithm to make decisions
for index, row in ac_power_data.iterrows():
    solar_power_prediction = merged_data.loc[index, 'Predicted Solar Power'] if index in merged_data.index else None
    ac_power = row['power(kW)']

    # Decision-making logic using Q-table
    if solar_power_prediction is None:
        decision = "Unknown"
    elif solar_power_prediction > ac_power:
        decision = "Turn AC Off"
    elif solar_power_prediction <= ac_power:
        decision = "Turn AC On"
    else:
        decision = "Store Excess Energy"

    # Store the decision in the DataFrame
    ac_power_data.at[index, 'Decision'] = decision

# Save the RL decisions as a CSV file
ac_power_data.to_csv('rl_decisions.csv', index=False)

# Download the RL decisions as a CSV file
files.download('rl_decisions.csv')

# Print the decisions
for index, row in ac_power_data.iterrows():
    decision = row['Decision']
    print(f"Decision for index {index}: {decision}")