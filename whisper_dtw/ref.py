import whisper

# Load the model
model = whisper.load_model("tiny")

audio_path = "audio_teapot.mp3"

# Transcribe audio with timestamps
for i in range(1):
    result = model.transcribe(audio_path, language="en", task="transcribe", word_timestamps=True)

# print(result)

for segment in result['segments']:
    words = segment['words']
    for word in words:
        print(f"{word['start']:.2f}\t{word['end']:.2f}\t{word['word']}")
