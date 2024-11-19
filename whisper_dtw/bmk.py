# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License

import argparse
import glob

import readline

import onnxruntime_genai as og
import numpy as np

import torch
import whisper
from whisper.audio import N_FRAMES, log_mel_spectrogram

# og.set_log_options(enabled=True, model_input_values=True)

# import onnxruntime as ort


def _complete(text, state):
    return (glob.glob(text + "*") + [None])[state]


class Format:
    end = "\033[0m"
    underline = "\033[4m"


def run(args: argparse.Namespace):
    print("Loading model...")
    model = og.Model(args.model_path)
    processor = model.create_multimodal_processor()
    tokenizer = og.Tokenizer(model)

    # Run ORT GenAI
    for i in range(1):
        readline.set_completer_delims(" \t\n;")
        readline.parse_and_bind("tab: complete")
        readline.set_completer(_complete)
        audio_paths = ["audio_teapot.mp3"]

        audio = whisper.load_audio(audio_paths[0])
        mel = log_mel_spectrogram(audio, 80, padding=0)

        batch_size = 1
        print("mel:", mel.shape)
        decoder_prompt_tokens = ["<|startoftranscript|>", "<|en|>", "<|transcribe|>", "<|notimestamps|>"]

        params = og.GeneratorParams(model)
        params.set_search_options(
            do_sample=False,
            num_beams=args.num_beams,
            num_return_sequences=args.num_beams,
            min_length=0,
            max_length=448,
        )

        offset = 0
        while offset < mel.shape[-1]:
            mel_segment = mel[:, offset : offset + N_FRAMES]
            offset += N_FRAMES
            mel_segment = whisper.pad_or_trim(mel_segment, N_FRAMES).to("cuda").to(torch.float16)
            mel_segment = mel_segment.unsqueeze(0).repeat(batch_size, 1, 1)

            params.audio_features = np.ascontiguousarray(mel_segment.cpu().numpy().astype(np.float16))
            params.input_ids = [[tokenizer.to_token_id(token) for token in decoder_prompt_tokens]] * batch_size
            params.alignment_heads = np.ascontiguousarray(
                np.array([[2, 2], [3, 0], [3, 2], [3, 3], [3, 4], [3, 5]]).astype(np.int32)
            )

            generator = og.Generator(model, params)

            while not generator.is_done():
                generator.compute_logits()
                generator.generate_next_token()
                # print('generator.get_output("logits"):', generator.get_output("logits"))

            print()
            for i in range(batch_size * args.num_beams):
                print("Batch:", i // args.num_beams, "Beam:", i % args.num_beams)
                tokens = generator.get_sequence(i)
                print("Tokens:", tokens)
                transcription = processor.decode(tokens)

                print(f"Transcription:")
                print(
                    f"    {Format.underline}batch {i // args.num_beams}, beam {i % args.num_beams}{Format.end}: {transcription}"
                )

        for _ in range(3):
            print()

    # Run ORT for output QK
    # sess = ort.InferenceSession(os.path.join(args.model_path, "whisper-large-v3_decoder.onnx"), providers=["CUDAExecutionProvider"])
    # outputs = sess.run(None, inputs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--model_path",
        type=str,
        default="whisper_new_export/wtiny-fp16",
        help="Path to the model",
    )
    parser.add_argument("-b", "--num_beams", type=int, default=1, help="Number of beams")
    args = parser.parse_args()
    run(args)
