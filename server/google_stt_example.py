"""
Example helpers for integrating Google Cloud Speech-to-Text.

This file contains example code (not executed by default) showing how to call
Google Cloud Speech-to-Text longRunningRecognize for longer audio files.

Prerequisites (local dev):
- pip install google-cloud-speech google-cloud-storage
- Set environment variable: GOOGLE_APPLICATION_CREDENTIALS to a service account JSON path

This is a reference only. Keep credentials server-side and do not commit keys.
"""
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage


def upload_blob(bucket_name: str, source_file_name: str, destination_blob_name: str):
    """Uploads a file to GCS. Used for longRunningRecognize on large files."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    return f"gs://{bucket_name}/{destination_blob_name}"


def transcribe_gcs(gcs_uri: str):
    """Transcribes audio file from GCS using longRunningRecognize and returns transcript segments.

    Note: customize config (encoding, sample_rate_hertz, language_code) based on your audio.
    """
    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        sample_rate_hertz=48000,
        language_code="en-US",
        enable_word_time_offsets=True,
        enable_speaker_diarization=False,
    )

    operation = client.long_running_recognize(config=config, audio=audio)
    print("Waiting for operation to complete...")
    response = operation.result(timeout=600)

    segments = []
    time_cursor = 0
    for result in response.results:
        alternative = result.alternatives[0]
        # alternative.words contains per-word timestamps if enabled
        segments.append({
            "startMs": int(alternative.words[0].start_time.seconds * 1000) if alternative.words else time_cursor,
            "endMs": int(alternative.words[-1].end_time.seconds * 1000) if alternative.words else time_cursor + 1000,
            "speaker": "unknown",
            "text": alternative.transcript,
        })
    return segments


if __name__ == '__main__':
    # Simple local run example (requires GCS and credentials configured)
    example_gcs_uri = 'gs://your-bucket/path/to/audio.webm'
    print(transcribe_gcs(example_gcs_uri))
