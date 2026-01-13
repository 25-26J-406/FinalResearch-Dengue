from flask import Flask, request, jsonify, send_from_directory
import joblib
import os

app = Flask(__name__, static_folder='../static')

# Load model + scaler
model = joblib.load("models/dengue_model_best.pkl")
scaler = joblib.load("models/scaler_best.pkl")

@app.route("/")
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json["features"]  # Expecting 5 values
        input_data = scaler.transform([data])
        prediction = model.predict(input_data)[0]

        return jsonify({"prediction": str(prediction)})

    except Exception as e:
        print("Prediction error:", e)
        return jsonify({"error": "Prediction failed. Try again!"}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
