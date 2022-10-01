from dotenv import load_dotenv
load_dotenv()
import os
import MySQLdb
planetscale = MySQLdb.connect(
  host= os.getenv("HOST"),
  user=os.getenv("USERNAME"),
  passwd= os.getenv("PASSWORD"),
  db= os.getenv("DATABASE"),
  ssl_mode = "VERIFY_IDENTITY",
  ssl      = {
    "ca": "/etc/ssl/cert.pem"
  }
)

cursor = planetscale.cursor()

cursor.execute(
  "select @@version;"
)

version = cursor.fetchone()

if version:
  print("Version: ", version)
else:
  print("Not connected.")

# INSERT INTO Transcriptions VALUES ('1', 'https://www.youtube.com/watch\?v\=ZXsQAXx_ao0', '453', '0', 'Do it! Just do it! Don''t let your dreams be dreams. Yesterday, you said tomorrow. So just do it! Make your dreams come true! Just do it! Some people dream success while you''re going to wake up and work hard at it. Nothing is impossible. You should get to the point where anyone else would quit and you''re not going to stop there. No! What are you waiting for? Do it! Just do it! Yes you can! Just do it! If you''re tired of starting over, stop giving up!')