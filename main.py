from __future__ import unicode_literals
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, abort
import MySQLdb
import os
import whisper
import youtube_dl

TABLE='Transcriptions'

planetscale = MySQLdb.connect(
  host= os.getenv("HOST"),
  user=os.getenv("USERNAME"),
  passwd= os.getenv("PASSWORD"),
  db= os.getenv("DATABASE"),
  ssl = 0
)

app = Flask(__name__)

class DownloadLogger(object):
    def debug(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)

class YoutubeManager:
    def __init__(self, url):
        self.url = url
        self.downloading = False
        self.result_url = ''
        self.result_text = ''
        self.model = whisper.load_model('small.en')
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
            download_manager.cache.remove()
            download_manager.download([self.url])


    def on_finished(self, dl):
        if dl['status'] == 'finished':
            self.downloading = False
            self.result_url = dl['filename']
            transcript = self.model.transcribe(self.result_url, verbose=True, language='en', fp16=False)
            self.result_text = transcript['text']

@app.route('/')
def index():
    return 'Transcriber API'

@app.route('/download', methods=['GET', 'POST'])
def download():
    try:
        token = request.args['token']
        if token != os.getenv('TRANSCRIPT_API_TOKEN'):
            return abort(401)
    except KeyError:
        return abort(401)
    url = request.args['video']
    title = request.args['title']
    youtube_manager = YoutubeManager(url)
    youtube_manager.start_download()
    with planetscale.cursor() as cursor:
        insert_sql = "INSERT INTO Transcriptions (url, title, length, upvotes, transcript) VALUES (%s, %s, %s, %s);"
        insert_data = (url, title, str(len(youtube_manager.result_text)), 0, youtube_manager.result_text)
        cursor.execute(insert_sql, insert_data)
        planetscale.commit()
        cursor.close()
    return youtube_manager.result_text

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))