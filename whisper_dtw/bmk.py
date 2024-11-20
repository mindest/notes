# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License

import argparse
import glob

import readline

import onnxruntime_genai as og
import numpy as np

import torch
import whisper
from whisper.audio import N_FRAMES, TOKENS_PER_SECOND, log_mel_spectrogram

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
        # audio_paths = ["1272-141231-0002.mp3"]

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
            actual_n_frames = mel_segment.shape[-1]
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

            cross_qk = generator.get_output("cross_qk")
            print(f"cross_qk: shape={cross_qk.shape}")  # (batch_size, beam_size, n, token_length, num_frames)

            def find_alignment(cross_qk: np.ndarray, actual_n_frames: int, text_tokens: list):
                from whisper.timing import median_filter, dtw

                qk = torch.tensor(cross_qk).to("cuda")
                qk = qk[:, :, : actual_n_frames // 2]
                print(f"qk: shape={qk.shape}")
                qk = qk.softmax(dim=-1)
                std, mean = torch.std_mean(qk, dim=-2, keepdim=True, unbiased=False)
                qk = (qk - mean) / std
                qk = median_filter(qk, filter_width=7)
                matrix = qk.mean(axis=0)
                len_sot = 3
                matrix = matrix[len_sot:-1]
                print(f"matrix: {matrix}")

                text_indices, time_indices = dtw(-matrix)
                print("text_indices:", ", ".join(map(str, text_indices)))
                print("time_indices:", ", ".join(map(str, time_indices)))
                print(f"len_text_indices={len(text_indices)}, len_time_indices={len(time_indices)}")

                tokens = text_tokens[len_sot:-1]
                texts = list(map(lambda x: processor.decode(x), tokens))
                print("texts:", len(texts), texts)

                start_end_frames = []
                for i, idx in enumerate(text_indices):
                    if len(start_end_frames) == idx:
                        start_end_frames.append([i, i])
                    else:
                        start_end_frames[idx][1] = i
                print("start_end_frames:", len(start_end_frames), start_end_frames)

                valid_texts = texts[1:]
                valid_start_end_frames = start_end_frames[1:]
                words = []
                word_timestamps = []
                for i, text in enumerate(valid_texts):
                    start, end = valid_start_end_frames[i]
                    start, end = time_indices[start], time_indices[end]
                    start, end = start / TOKENS_PER_SECOND, end / TOKENS_PER_SECOND
                    if text.startswith(" "):
                        words.append(text.strip())
                        word_timestamps.append([start, end])
                    else:
                        words[-1] += text
                        word_timestamps[-1][1] = end

                print("Word timestamps:")
                for word, (start, end) in zip(words, word_timestamps):
                    print(f"    {start:.2f}\t{end:.2f}\t{word}")

            batch_size = cross_qk.shape[0]
            for b in range(batch_size):
                cross_qk_b = cross_qk[b, 0, :, :, :].squeeze()
                # Pick the first beam for each batch
                tokens = generator.get_sequence(b * args.num_beams)
                find_alignment(cross_qk_b, actual_n_frames, tokens)

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
