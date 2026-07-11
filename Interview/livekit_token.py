import os
from livekit import api
from flask import Flask, request,jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from livekit.api import LiveKitAPI, ListRoomsRequest
import uuid

import sys

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

messages_add=[]

async def generate_room_name():
    name = "room-" + str(uuid.uuid4())[:8]
    rooms = await get_rooms()
    while name in rooms:
        name = "room-" + str(uuid.uuid4())[:8]
    return name

async def get_rooms():
    api = LiveKitAPI()
    rooms = await api.room.list_rooms(ListRoomsRequest())
    await api.aclose()
    return [room.name for room in rooms.rooms]

@app.route("/getToken")
async def get_token():
    name = request.args.get("name", "my name")
    room = request.args.get("room", None)
    
    if not room:
        room = await generate_room_name()
        
    token = api.AccessToken(os.getenv("LIVEKIT_API_KEY"), os.getenv("LIVEKIT_API_SECRET")) \
        .with_identity(name)\
        .with_name(name)\
        .with_grants(api.VideoGrants(
            room_join=True,
            room=room
        ))
    
    return token.to_jwt()


@app.route("/process-chat", methods=["POST"])
def process_chat():
    messages = request.get_json()

    if not messages:
        return jsonify({"error": "No messages received"}), 400

    print("\nReceived chat messages:\n")

    print(messages)
    messages_add.extend(messages)
    print("**********************************************")
    print(messages_add)

    return jsonify({
        "status": "success",
        "message":messages
    }),200

@app.route("/get-messages", methods=["GET"])
def get_messages():
    return jsonify(messages_add)

# ----------------------------
if __name__=="__main__":
    app.run(host="0.0.0.0",port=5001,debug=True)
