import os
import whisper

def transcribe_audio(audio_file_path, model_path):
    model = whisper.load_model(model_path)
    result = model.transcribe(audio_file_path)
    text_file_path = os.path.splitext(audio_file_path)[0] + ".txt"
    with open(text_file_path, "w") as text_file:
        text_file.write(result['text'])
    
audio_file_path = 'test.mp3'

if audio_file_path is not None:
    transcribe_audio(audio_file_path, model_path='medium')
