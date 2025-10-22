import queue
import time
import threading

import numpy as np
import webrtcvad
import pyaudio
from faster_whisper import WhisperModel


class FasterWhisperRecorder:
    def __init__(
        self,
        model_size="base.en",  # Changed from medium to base for speed
        device="cuda",
        compute_type="float16",
        silence_duration=0.5,
        frame_duration=30,
        sample_rate=16000,
        aggressiveness=2,
        min_audio_length=0.3,  # Minimum audio length to process (seconds)
    ):
        # Adjust compute_type for CPU
        if device == "cpu" and compute_type == "float16":
            compute_type = "int8"
        
        self.model = WhisperModel(
            model_size, 
            device=device, 
            compute_type=compute_type,
            num_workers=4,  # Parallel processing
            cpu_threads=4   # For CPU inference
        )
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration
        self.frame_size = int(sample_rate * frame_duration / 1000)
        self.vad = webrtcvad.Vad(aggressiveness)
        self.silence_duration = silence_duration
        self.min_audio_length = min_audio_length
        self.min_samples = int(sample_rate * min_audio_length)

        self.audio_interface = pyaudio.PyAudio()
        self.stream = None
        self.buffer_queue = queue.Queue()
        self.stop_event = threading.Event()

    def _callback(self, in_data, frame_count, time_info, status):
        self.buffer_queue.put(in_data)
        return (in_data, pyaudio.paContinue)

    def start_stream(self):
        self.stream = self.audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.frame_size,
            stream_callback=self._callback,
        )

    def stop_stream(self):
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.audio_interface.terminate()

    def listen_once(self):
        """Collect audio until silence is detected"""
        frames = []
        silence_start = None
        speech_detected = False

        while not self.stop_event.is_set():
            try:
                frame = self.buffer_queue.get(timeout=1)
            except queue.Empty:
                continue

            is_speech = self.vad.is_speech(frame, self.sample_rate)
            
            if is_speech:
                speech_detected = True
                frames.append(frame)
                silence_start = None
            elif speech_detected:
                # Only append silence frames after speech detected
                frames.append(frame)
                if silence_start is None:
                    silence_start = time.time()
                elif time.time() - silence_start > self.silence_duration:
                    break

        if not frames:
            return np.array([], dtype=np.float32)

        audio_data = b"".join(frames)
        audio_np = np.frombuffer(audio_data, np.int16).astype(np.float32) / 32768.0
        
        # Skip very short audio clips
        if len(audio_np) < self.min_samples:
            return np.array([], dtype=np.float32)
            
        return audio_np

    def transcribe(self, audio):
        """Run Faster-Whisper on captured audio with optimized settings"""
        segments, _ = self.model.transcribe(
            audio,
            language="en",
            beam_size=1,  # Reduced from 5 for speed (greedy decoding)
            best_of=1,    # Single pass instead of multiple
            temperature=0.0,  # Deterministic output
            vad_filter=True,
            vad_parameters=dict(
                threshold=0.5,
                min_speech_duration_ms=250,
                min_silence_duration_ms=100,
            ),
            condition_on_previous_text=False,  # Faster for short segments
            no_speech_threshold=0.6,  # Skip silent segments
            compression_ratio_threshold=2.4,
            log_prob_threshold=-1.0,
            initial_prompt=None,  # Remove if not needed
            word_timestamps=False,  # Disable unless needed
        )

        full_text = ""
        for segment in segments:
            full_text += segment.text.strip() + " "

        return full_text.strip()

    def start_transcription(self):
        """Start continuous transcription and yield transcribed text"""
        self.start_stream()
        try:
            while True:
                audio = self.listen_once()
                if len(audio) == 0:
                    continue

                final_text = self.transcribe(audio)
                if final_text:
                    yield final_text
        finally:
            self.stop_stream()
