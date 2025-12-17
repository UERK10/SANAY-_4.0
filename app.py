# -*- coding: utf-8 -*-
import datetime
import random
import pandas as pd
from flask import Flask, jsonify
from flask import Flask, jsonify, render_template
# --- Configuration ---
# Set the time for data simulation
START_TIME = datetime.datetime.now() - datetime.timedelta(hours=24)
NUM_HOURS = 24
ANOMALY_THRESHOLD_FACTOR = 1.3  # Anomaly is defined as consumption > (Average * 1.3)

# --- Data Simulation Function ---
def simulate_energy_data(start_time, num_hours):
    """
    Generates simulated hourly industrial energy consumption data for a single day.
    Includes typical base load, peak hours, and a controlled anomaly.
    """
    data = []
    
    # Define a single random time for a major anomaly
    anomaly_hour = random.randint(3, 21)
    
    for i in range(num_hours):
        current_time = start_time + datetime.timedelta(hours=i)
        hour = current_time.hour
        
        # Base consumption (typical machine operation)
        base_kwh = random.uniform(80.0, 100.0)
        
        # Peak Consumption Logic (Simulating high production periods)
        # Peak 1: 10:00 - 12:00
        # Peak 2: 18:00 - 20:00
        if (10 <= hour < 12) or (18 <= hour < 20):
            # Add a significant peak load
            energy_kwh = base_kwh + random.uniform(40.0, 70.0)
        else:
            # Normal load (with some minor fluctuation)
            energy_kwh = base_kwh + random.uniform(0.0, 15.0)

        # Anomaly Injection Logic (Simulating unexpected failure or misuse)
        if hour == anomaly_hour:
            # Inject a very high, anomalous value
            energy_kwh += random.uniform(80.0, 120.0)
        
        # Ensure the value is reasonable (e.g., max 250 kWh)
        energy_kwh = min(energy_kwh, 250.0)
        
        data.append({
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M"),
            "line": "Production Line A", # Simplified for a single line
            "energy_kwh": round(energy_kwh, 2)
        })
        
    return pd.DataFrame(data)

# --- Flask App Initialization ---
app = Flask(__name__)

# --- ANA SAYFA (ÇOK ÖNEMLÝ) ---
@app.route("/")
def home():
    return render_template("index.html")

# Initialize the data upon startup
ENERGY_DATA_DF = simulate_energy_data(START_TIME, NUM_HOURS)

# --- API Endpoints ---

@app.route('/api/energy', methods=['GET'])
def get_energy_data():
    """
    Endpoint 1: Returns the raw, simulated hourly energy consumption data.
    """
    # Return the DataFrame records as a list of dictionaries (JSON format)
    return jsonify(ENERGY_DATA_DF.to_dict('records'))

@app.route('/api/analysis', methods=['GET'])
def get_energy_analysis():
    """
    Endpoint 2: Performs energy analysis using pandas:
    - Average Consumption
    - Peak Consumption
    - Simple Anomaly Detection
    """
    df = ENERGY_DATA_DF['energy_kwh']
    
    average_consumption = df.mean()
    peak_consumption = df.max()
    
    # Simple Anomaly Detection: Any consumption significantly higher than average
    anomaly_threshold = average_consumption * ANOMALY_THRESHOLD_FACTOR
    anomaly_detected = peak_consumption > anomaly_threshold
    
    response = {
        "average_consumption_kwh": round(average_consumption, 2),
        "peak_consumption_kwh": round(peak_consumption, 2),
        "anomaly_threshold_kwh": round(anomaly_threshold, 2),
        "anomaly_detected": bool(anomaly_detected)
    }
    
    # Optionally, find the time of the peak/anomaly
    if anomaly_detected:
        peak_time_index = ENERGY_DATA_DF['energy_kwh'].idxmax()
        peak_time = ENERGY_DATA_DF.loc[peak_time_index, 'timestamp']
        response['peak_time'] = peak_time
        
    return jsonify(response)

@app.route('/api/forecast', methods=['GET'])
def get_energy_forecast():
    """
    Endpoint 3: Provides a simple "AI-supported" forecast using a Moving Average model.
    Predicts the energy consumption for the next two hours.
    """
    df = ENERGY_DATA_DF['energy_kwh']
    
    # Simple Moving Average (MA) of the last 4 hours
    window_size = 4
    
    # Calculate MA for the last few periods
    last_ma = df.tail(window_size).mean()

    # Simple Linear Projection (predicting the next 2 hours)
    forecast_kwh = round(last_ma * random.uniform(0.98, 1.02), 2)
    forecast_time = (START_TIME + datetime.timedelta(hours=NUM_HOURS)).strftime("%Y-%m-%d %H:%M")
    
    # Predict the hour after that (a bit more uncertainty)
    next_forecast_kwh = round(forecast_kwh * random.uniform(0.95, 1.05), 2)
    next_forecast_time = (START_TIME + datetime.timedelta(hours=NUM_HOURS + 1)).strftime("%Y-%m-%d %H:%M")

    response = {
        "model": "AI-Supported Moving Average Projection",
        "last_known_value_kwh": round(df.iloc[-1], 2),
        "forecast": [
            {
                "timestamp": forecast_time,
                "predicted_kwh": forecast_kwh,
                "note": "Next hour projection based on recent trend."
            },
            {
                "timestamp": next_forecast_time,
                "predicted_kwh": next_forecast_kwh,
                "note": "Subsequent hour projection (higher variance)."
            }
        ]
    }
    
    return jsonify(response)

# --- Run the application ---
if __name__ == '__main__':
    # Print a summary of the generated data for quick verification
    print(f"--- Energy Data Simulation Summary ---")
    print(f"Total hours simulated: {NUM_HOURS}")
    print(f"Average Consumption: {ENERGY_DATA_DF['energy_kwh'].mean():.2f} kWh")
    print(f"Peak Consumption: {ENERGY_DATA_DF['energy_kwh'].max():.2f} kWh")
    print("--------------------------------------")
    
    # Running in debug mode for development (hackathon setting)
    app.run(debug=True, port=5000)
    

