from flask import Flask, request, jsonify
from producer_kafka import publish_event

app = Flask(__name__)

@app.route("/pix/kafka", methods=["POST"])
def pix_kafka():
    data = request.json
    topic = data.get("topic", "pix.payment.requested")
    publish_event(topic, data)
    return jsonify({"status": "Event sent to Kafka", "topic": topic}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
