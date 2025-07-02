from flask import Flask, request, jsonify
from producer_rabbit import publish_event

app = Flask(__name__)

@app.route("/pix/rabbit", methods=["POST"])
def pix_rabbit():
    data = request.json
    routing_key = data.get("topic", "pix.payment.requested")
    publish_event(routing_key, data)
    return jsonify({"status": "Event sent to RabbitMQ", "routing_key": routing_key}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
