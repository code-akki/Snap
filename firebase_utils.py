import pyrebase

config = {
  "apiKey": "AIzaSyDpXXiXKrHB4EX0WtrrLGVaCxiJInEHToE",
  "authDomain": "snap-8a7b3.firebaseapp.com",
  "databaseURL": "https://snap-8a7b3.firebaseio.com",
  "projectId": "snap-8a7b3",
  "storageBucket": "snap-8a7b3.appspot.com"
}

firebase = pyrebase.initialize_app(config)

def createFirebase():
    