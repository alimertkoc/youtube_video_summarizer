from pytubefix import YouTube
from pytubefix.cli import on_progress
from pydub import AudioSegment
import subprocess
import logging

# Basic configuration for logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='app.log',  # Log to a file, remove this to log to stdout
                    filemode='w')  # Use 'a' to append to the file instead of 'w' to overwrite

# Example usage
# logging.debug('This is a debug message')
# logging.info('This is an info message')
# logging.warning('This is a warning message')
# logging.error('This is an error message')
# logging.critical('This is a critical message')


# Step 1: Donwload Audio of the YouTube Video
def youtube_audio_downloader(video_url):
    yt = YouTube(video_url, on_progress_callback = on_progress)
    ys = yt.streams.get_audio_only()
    logging.info("Downloading audio...")
    audio_path = ys.download(mp3=True, filename=".1") # pass the parameter mp3=True to save in .mp3
    logging.info("Audio downloaded successfully.")
    return audio_path  # Returns the full path of the downloaded video file

# Step 2: Convert Audio
def convert_audio(audio_filename):
    # Convert MP3 to WAV
    try:
        sound = AudioSegment.from_file(audio_filename, "mp3")
    except:
        sound = AudioSegment.from_file(audio_filename, format="mp4")
    logging.debug("Segmentation Succesfull")
    
    wav_filename = audio_filename.replace(".mp3", ".wav")    
    sound.export(wav_filename, format="wav")

    return wav_filename  # Returns the full path of the converted audio file

# Step 3: Transcribe Audio
import speech_recognition as sr
def transcribe_audio(audio_filename):
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(audio_filename)
    with audio_file as source:
        audio_data = recognizer.record(source)
    transcription = recognizer.recognize_google(audio_data)
    return transcription  # Returns the transcription of the audio


# Step 4: Summarize Transcription
def summarize_transcription(transcription):
    # Use subprocess.run for better handling of spaces and special characters
    cmd = ["ollama", "run", "llama3.1:8b", f"Summarize this context: {transcription}"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        logging.info("Summarization successful")
        return result.stdout
    else:
        logging.error("Error in summarization")
        return result.stderr


import sys

# Assuming all necessary functions (download_video, extract_audio, transcribe_audio, summarize_transcription) are defined above

def main():
    print("Welcome to the YouTube Video Summarizer CLI Tool!")
    video_url = input("Please enter the YouTube video URL: ")
    
    try:
        print("Downloading video...")
        audio_filename = youtube_audio_downloader(video_url)
        print("Video downloaded successfully.")
        print()

        print("Converting Audio...")
        converted_audio_filename = convert_audio(audio_filename)
        print("Audio converted succesfully...")
        print()
        
        print("Transcribing audio...")
        transcription = transcribe_audio(converted_audio_filename)
        print(transcription)
        print("Audio transcribed successfully.")
        print()

        print("Summarizing transcription...")
        summary = summarize_transcription(transcription)
        print("Summary generated successfully.")
        print()

        print("\nSummary:\n", summary)
    except Exception as e:
        logging.error("There was a problem in main flow: ", e)
        sys.exit(1)

if __name__ == "__main__":
    main()