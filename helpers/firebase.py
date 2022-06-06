from firebase_admin import credentials,initialize_app
from helpers.constants import credentials_path

def initializeFirebase():
    firebaseCredentials = credentials.Certificate(credentials_path)
    initialize_app(firebaseCredentials)