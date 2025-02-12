from flask import Flask, request, jsonify

@app.route('/api/card', methods=['POST'])
def craft_card():
    data = request.json
    # Process the data and create a card
    return jsonify({"message": "Card created successfully!"})