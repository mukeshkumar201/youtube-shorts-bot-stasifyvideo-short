import os
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 1. GitHub Secrets se Data lena
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["REFRESH_TOKEN"]
SOURCE_FOLDER = os.environ["DRIVE_FOLDER_ID"]
DEST_FOLDER = os.environ["DONE_FOLDER_ID"]

def get_services():
    # Token Refresh Logic
    creds = Credentials(
        None, # Access token nahi hai, hum refresh karenge
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    # Token expire ho gaya to refresh karein
    if not creds.valid:
        request = google.auth.transport.requests.Request()
        creds.refresh(request)
    
    drive = build('drive', 'v3', credentials=creds)
    youtube = build('youtube', 'v3', credentials=creds)
    return drive, youtube

def main():
    try:
        drive, youtube = get_services()
        print("Login Successful!")

        # 2. Drive Check Karna
        query = f"'{SOURCE_FOLDER}' in parents and mimeType contains 'video/' and trashed=false"
        results = drive.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])

        if not files:
            print("No videos found to upload.")
            return

        video = files[0] # Pehli video uthao
        print(f"Found video: {video['name']}")

        # 3. Video Download Karna
        print("Downloading video...")
        request = drive.files().get_media(fileId=video['id'])
        with open("video.mp4", "wb") as f:
            f.write(request.execute())

        # 4. YouTube par Upload Karna
        print("Uploading to YouTube Shorts...")
        title = video['name'].replace(".mp4", "").replace("_", " ") # Clean filename
        
        body = {
            'snippet': {
                'title': f"{title} #Shorts #FunnyAnimals",
                'description': "Subscribe for more funny animal videos! #Shorts #Animals",
                'tags': ['shorts', 'funny', 'animals', 'cute'],
                'categoryId': '15' # Pets & Animals category
            },
            'status': {
                'privacyStatus': 'public', # 'private' rakhein agar test karna ho
                'selfDeclaredMadeForKids': False
            }
        }

        media = MediaFileUpload("video.mp4", chunksize=-1, resumable=True)
        upload = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        ).execute()

        print(f"Uploaded Successfully! Video ID: {upload['id']}")

        # 5. Video Move Karna (Queue -> Done)
        print("Moving video to Done folder...")
        file = drive.files().get(fileId=video['id'], fields='parents').execute()
        previous_parents = ",".join(file.get('parents'))
        
        drive.files().update(
            fileId=video['id'],
            addParents=DEST_FOLDER,
            removeParents=previous_parents
        ).execute()
        print("Process Complete!")

    except Exception as e:
        print(f"Error aa gaya: {e}")
        # Error aaye to fail kar do taaki GitHub email bheje
        exit(1)

if __name__ == "__main__":
    main()
