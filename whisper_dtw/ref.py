import argparse
import whisper

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--audio_path", type=str, default=None, help="Path to the audio file")

args = parser.parse_args()

# Load the model
model = whisper.load_model("tiny")

# audio_path = "audios/audio_teapot.mp3"
audio_path = "audios/1272-141231-0002.mp3"

audio_path = args.audio_path or audio_path

# Transcribe audio with timestamps
for i in range(1):
    result = model.transcribe(audio_path, language="en", task="transcribe", word_timestamps=True)

# print(result)

header = "start\tend\tword\n-----\t---\t----"
print(header)

f = open("output_ref.txt", "w")
f.write(header + "\n")

for segment in result["segments"]:
    words = segment["words"]
    for word in words:
        line = f"{word['start']:.2f}\t{word['end']:.2f}\t{word['word'].lstrip()}"
        print(line)
        f.write(line + "\n")
f.close()
