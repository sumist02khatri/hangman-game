from flask import Flask, jsonify, request, send_from_directory, make_response
from hangman import Hangman
from flask_cors import CORS
import logging
import mimetypes

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Ensure MP3 MIME type is registered
mimetypes.add_type('audio/mpeg', '.mp3')

game = None

@app.route("/start", methods=["POST", "OPTIONS"])
def start_game():
    if request.method == "OPTIONS":
        logger.debug("Handling OPTIONS request for /start")
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response
    
    logger.debug("Received /start request: %s", request.get_json())
    data = request.get_json()
    difficulty = data.get("difficulty", "medium")
    try:
        global game
        game = Hangman(difficulty)
        response = {
            "question": game.get_question(),
            "word": game.display_word(),
            "turns": game.get_turns_left(),
            "stage": game.get_stage(),
            "feedback": "Guess a letter!",
            "game_over": False,
            "hint": game.get_hint()
        }
        logger.debug("Sending response: %s", response)
        return jsonify(response)
    except Exception as e:
        logger.error("Error in start_game: %s", str(e), exc_info=True)
        return jsonify({"error": f"Failed to start game: {str(e)}"}), 500

@app.route("/guess", methods=["POST", "OPTIONS"])
def guess():
    if request.method == "OPTIONS":
        logger.debug("Handling OPTIONS request for /guess")
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response
    
    global game
    if not game:
        logger.error("No game instance found")
        return jsonify({"error": "Start a new game!"}), 400
    logger.debug("Received /guess request: %s", request.get_json())
    data = request.get_json()
    letter = data.get("letter")
    try:
        success, feedback = game.guess(letter)
        game_over, message = game.is_game_over()
        response = {
            "question": game.get_question(),
            "word": game.display_word(),
            "turns": game.get_turns_left(),
            "stage": game.get_stage(),
            "feedback": feedback,
            "game_over": game_over,
            "message": message if game_over else "",
            "hint": game.get_hint()
        }
        logger.debug("Sending response: %s", response)
        return jsonify(response)
    except Exception as e:
        logger.error("Error in guess: %s", str(e), exc_info=True)
        return jsonify({"error": f"Failed to process guess: {str(e)}"}), 500

@app.route("/hint", methods=["POST", "OPTIONS"])
def use_hint():
    if request.method == "OPTIONS":
        logger.debug("Handling OPTIONS request for /hint")
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response
    
    global game
    if not game:
        logger.error("No game instance found")
        return jsonify({"error": "Start a new game!"}), 400
    try:
        success, feedback = game.use_hint()
        game_over, message = game.is_game_over()
        response = {
            "question": game.get_question(),
            "word": game.display_word(),
            "turns": game.get_turns_left(),
            "stage": game.get_stage(),
            "feedback": feedback,
            "game_over": game_over,
            "message": message if game_over else "",
            "hint": game.get_hint()
        }
        logger.debug("Sending response: %s", response)
        return jsonify(response)
    except Exception as e:
        logger.error("Error in use_hint: %s", str(e), exc_info=True)
        return jsonify({"error": f"Failed to process hint: {str(e)}"}), 500

@app.route("/static/sounds/<path:filename>")
def serve_sound(filename):
    logger.debug("Serving sound: %s", filename)
    try:
        response = make_response(send_from_directory('static/sounds', filename))
        response.headers['Content-Type'] = 'audio/mpeg'
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Cache-Control'] = 'public, max-age=0'
        return response
    except Exception as e:
        logger.error("Error serving sound %s: %s", filename, str(e))
        return jsonify({"error": f"Failed to serve sound: {str(e)}"}), 404

@app.route("/static/images/<path:filename>")
def serve_image(filename):
    logger.debug("Serving image: %s", filename)
    try:
        return send_from_directory('static/images', filename, mimetype='image/png')
    except Exception as e:
        logger.error("Error serving image %s: %s", filename, str(e))
        return jsonify({"error": f"Failed to serve image: {str(e)}"}), 404

@app.after_request
def add_cors_headers(response):
    logger.debug("Adding CORS headers to response: %s", response.headers)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

if __name__ == "__main__":
    app.run(debug=True, port=5000)