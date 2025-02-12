from flask import Flask, request, jsonify

app = Flask(__name__)
app.config["DATABASE_FILENAME"] = "crafting.db"

import craft_card


if __name__ == '__main__':
    app.run(debug=True)