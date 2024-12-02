import nvtx
import torch
import whisper
from whisper.tokenizer import get_tokenizer
from whisper.audio import N_FRAMES, log_mel_spectrogram

def get_model_tokenizer(model_card):
    model = whisper.load_model(model_card)
    tokenizer = get_tokenizer(
        model.is_multilingual,
        num_languages=model.num_languages,
        language="en",
        task="transcribe",
    )
    return model, tokenizer

def transcribe_bmk(audio_path, batch_size=3, beam_size=4):
    model, tokenizer = get_model_tokenizer(os.environ.get("WHISPER_MODEL_SIZE", "tiny"))
    audio = whisper.load_audio(audio_path)
    offset = 0
    mel = log_mel_spectrogram(audio, model.dims.n_mels, padding=0)
    while offset < mel.shape[-1]:
        mel_segment = mel[:, offset : offset + N_FRAMES]
        mel_segment = whisper.pad_or_trim(mel_segment, N_FRAMES).to(model.device).to(torch.float16)
        mel_segment = mel_segment.unsqueeze(0).repeat(batch_size, 1, 1)
        options = whisper.DecodingOptions(beam_size=beam_size, temperature=0.0)
        with nvtx.annotate("decode", color="blue"):
            result = whisper.decode(model, mel_segment, options)

        print(result[0].text)

        tokens = result[0].tokens if batch_size > 1 else result.tokens
        tokens = [item for item in tokens if item < tokenizer.eot]
        tokens = torch.tensor(tokens).repeat(batch_size, 1).to(model.device)

        # Calculate model forward for all output tokens, to use in word-timestamping
        with nvtx.annotate("ts model run", color="green"):
            _ = model(mel_segment, tokens)

        offset += N_FRAMES

if __name__ == "__main__":
    import os
    idx = os.environ.get("FILE_INDEX", "1")
    audio_path = f"concat_audios/{idx}.flac"
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-B", "--batch_size", type=int, default=3, help="Batch size")
    parser.add_argument("-b", "--beam_size", type=int, default=4, help="Beam size")
    parser.add_argument("-p", "--profile", action="store_true", help="Enable profiling")
    parser.add_argument("-a", "--audio_path", type=str, default=None, help="Path to the audio file")
    args = parser.parse_args()

    audio_path = args.audio_path or audio_path

    for i in range(5 if args.profile else 1):
        with nvtx.annotate(f"transcribe_{i}", color="red"):
            transcribe_bmk(audio_path, args.batch_size, args.beam_size)
