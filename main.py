from __future__ import unicode_literals
from flask import Flask, request, abort
import os
import validators
import whisper
import youtube_dl

app = Flask(__name__)

class DownloadLogger(object):
    def debug(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)

result = ''

def hook(arg):
    print(arg)

class YoutubeManager:
    def __init__(self, url):
        self.url = url
        self.downloading = False
        self.result_url = ''
        self.result_text = ''
        self.model = whisper.load_model('base.en')
        self.ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'logger': DownloadLogger(),
        'progress_hooks': [self.on_finished],
        }
        self.download_manager = youtube_dl.YoutubeDL(self.ydl_opts)

    def start_download(self):
        self.downloading = True
        with self.download_manager as download_manager:
            download_manager.download([self.url])


    def on_finished(self, dl):
        if dl['status'] == 'finished':
            self.downloading = False
            self.result_url = dl['filename']
            transcript = self.model.transcribe(self.result_url, verbose=True, language='en', fp16=False)
            self.result_text = transcript['text']
            

class DownloadLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

def on_finished(dl):
    if dl['status'] == 'finished':
        print('Done downloading, now converting...')

def is_valid_url(url):
    return validators.url(url)

def is_yt_url(url):
    return url.find('youtube') > -1

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/download', methods=['POST'])
def download():
    content = request.get_json()
    url = content['data']
    print(url)
    if not is_valid_url(url):
        abort(400)
    if not is_yt_url(url):
        abort(400)
    youtube_manager = YoutubeManager(url)
    youtube_manager.start_download()
    return youtube_manager.result_text

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))