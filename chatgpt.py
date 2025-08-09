#!/usr/bin/env python3
import sys
import json
import os
import requests

# === SETTINGS ===
MODEL = "gpt-5"

# === USAGE ===
# python3 chatGPT.py <session_id> <payload_text> <history_file_path> <service_name>

if len(sys.argv) != 5:
    print("Usage: chatGPT.py <session_id> <payload_text> <history_file_path> <service_name>")
    sys.exit(1)

session_id = sys.argv[1]
user_input = sys.argv[2]
history_file = sys.argv[3]
service_name = sys.argv[4]  # e.g., "ChatGPT" or "mistral"

# === LOAD CONFIG.JSON FROM SAME DIRECTORY AS SCRIPT ===
script_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_dir, "config.json")

try:
    with open(config_path, 'r') as f:
        config = json.load(f)
except Exception as e:
    print(f"Error reading config.json: {e}")
    sys.exit(1)

# === GET API KEY FOR SERVICE ===
try:
    api_keys = config["keys"][service_name]
    if not api_keys:
        raise ValueError(f"No keys found for {service_name}")
    API_KEY = api_keys[0]  # use the first key
except KeyError:
    print(f"Service '{service_name}' not found in config.json")
    sys.exit(1)

# === LOAD OR CREATE CONVERSATION HISTORY ===
if not os.path.exists(history_file):
    conversation_history = [{"role": "system", "content": "You are a helpful assistant."}]
    try:
        with open(history_file, 'w') as f:
            json.dump(conversation_history, f, indent=2)
        print(f"Created new history file: {history_file}")
    except Exception as e:
        print(f"Failed to create {history_file}: {e}")
        sys.exit(1)
else:
    try:
        with open(history_file, 'r') as f:
            conversation_history = json.load(f)
    except Exception as e:
        print(f"Error reading conversation history from {history_file}: {e}")
        sys.exit(1)

# === APPEND USER MESSAGE ===
conversation_history.append({"role": "user", "content": user_input})

# === API REQUEST ===
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": MODEL,
    "messages": conversation_history,
    "user": session_id
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)

if response.status_code == 200:
    reply = response.json()['choices'][0]['message']['content'].strip()
    print(reply)

    # Append assistant's reply to history
    conversation_history.append({"role": "assistant", "content": reply})
    try:
        with open(history_file, 'w') as f:
            json.dump(conversation_history, f, indent=2)
    except Exception as e:
        print(f"Failed to write updated history: {e}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)