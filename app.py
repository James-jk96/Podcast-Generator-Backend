from flask import Flask, request, jsonify
import openai
import requests
import json
import os

app = Flask(__name__)  # Define 'app' here

@app.route('/')
def home():
    return jsonify({"message": "Podcast API is live!"})

@app.route('/api/generate-script', methods=['POST'])
def generate_script():
    data = request.json
    topic = data.get("topic", "")

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    prompt = f"""
    Create a detailed podcast script for the topic: "{topic}". The script should include:
    - An engaging introduction
    - A structured breakdown (e.g., history, key facts, expert opinions, etc.)
    - A conclusion with key takeaways
    - A natural-sounding outro encouraging listeners to subscribe
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an expert podcast script writer."},
                  {"role": "user", "content": prompt}],
        temperature=0.7
    )

    script = response['choices'][0]['message']['content']
    return jsonify({"script": script})

@app.route('/api/generate-audio', methods=['POST'])
def generate_audio():
    data = request.json
    script = data.get("script", "")

    if not script:
        return jsonify({"error": "Script is required"}), 400

    ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY"
    ELEVENLABS_VOICE_ID = "Rachel"

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": script,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        audio_filename = "static/podcast_episode.mp3"
        with open(audio_filename, "wb") as file:
            file.write(response.content)
        return jsonify({"audioUrl": f"/{audio_filename}"})
    else:
        return jsonify({"error": "Failed to generate audio", "details": response.json()}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Render assigns a dynamic port
    app.run(host="0.0.0.0", port=port, debug=True)
