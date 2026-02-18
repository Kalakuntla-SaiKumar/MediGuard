from flask import Flask, request, jsonify
from flask_cors import CORS
from src.engine.mediguard_engine import mediguard_assess

app = Flask(__name__)
CORS(app)  # Allow frontend access

@app.route("/")
def home():
    return jsonify({
        "message": "MediGuard API is running"
    })

@app.route("/assess", methods=["POST"])
def assess():
    try:
        data = request.get_json()

        # Validate input
        required_fields = ["drug1", "drug2", "condition"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    "error": f"{field} is required"
                }), 400

        drug1 = data["drug1"]
        drug2 = data["drug2"]
        condition = data["condition"]

        # Call engine
        result = mediguard_assess(drug1, drug2, condition)

        return jsonify({
            "status": "success",
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)