import os
import sys
import uuid
from livekit import api
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from livekit.api import LiveKitAPI, ListRoomsRequest

load_dotenv()

# Add parent directory to path so we can import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ━━━ Database-backed message storage (with in-memory fallback) ━━━
try:
    from utils.database import db_save_interview_messages, db_get_interview_messages, create_tables
    create_tables()
    USE_DATABASE = True
except ImportError:
    USE_DATABASE = False
    print("Warning: Database module not available. Using in-memory storage.")

# In-memory fallback
messages_add = []
current_room_name = None


async def generate_room_name():
    name = "room-" + str(uuid.uuid4())[:8]
    rooms = await get_rooms()
    while name in rooms:
        name = "room-" + str(uuid.uuid4())[:8]
    return name


async def get_rooms():
    lk_api = LiveKitAPI()
    rooms = await lk_api.room.list_rooms(ListRoomsRequest())
    await lk_api.aclose()
    return [room.name for room in rooms.rooms]


@app.route("/")
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route("/getToken")
async def get_token():
    global current_room_name
    
    name = request.args.get("name", "my name")
    room = request.args.get("room", None)

    if not room:
        room = await generate_room_name()

    current_room_name = room

    token = api.AccessToken(os.getenv("LIVEKIT_API_KEY"), os.getenv("LIVEKIT_API_SECRET")) \
        .with_identity(name) \
        .with_name(name) \
        .with_grants(api.VideoGrants(
            room_join=True,
            room=room
        ))

    return token.to_jwt()


@app.route("/process-chat", methods=["POST"])
def process_chat():
    global messages_add
    messages = request.get_json()

    if not messages:
        return jsonify({"error": "No messages received"}), 400

    print("\nReceived chat messages:\n")
    print(messages)

    # ━━━ Save to database (primary) ━━━
    if USE_DATABASE and current_room_name:
        try:
            db_save_interview_messages(current_room_name, messages)
        except Exception as e:
            print(f"Database save failed: {e}")

    # ━━━ Also keep in-memory for backward compatibility ━━━
    messages_add.extend(messages)
    print("**********************************************")
    print(messages_add)

    return jsonify({
        "status": "success",
        "message": messages
    }), 200


@app.route("/get-messages", methods=["GET"])
def get_messages():
    # ━━━ Try database first ━━━
    if USE_DATABASE and current_room_name:
        try:
            db_messages = db_get_interview_messages(current_room_name)
            if db_messages:
                return jsonify(db_messages)
        except Exception as e:
            print(f"Database load failed: {e}")

    # ━━━ Fallback to in-memory ━━━
    return jsonify(messages_add)


# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)