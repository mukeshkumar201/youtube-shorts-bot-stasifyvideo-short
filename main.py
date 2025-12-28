import os
import random  # <-- Ye naya import hai random title ke liye
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
    creds = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
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

        video = files[0]
        print(f"Found video file: {video['name']}")

        # 3. Video Download Karna
        print("Downloading video...")
        request = drive.files().get_media(fileId=video['id'])
        with open("video.mp4", "wb") as f:
            f.write(request.execute())

        # 4. RANDOM TITLE GENERATOR (Magic Yahan Hai)
        print("Generating Viral Title...")

        # Ye wo list hai jisme se bot title pick karega
        viral_titles_list = [
            "Oddly Satisfying Video to Relax 🤤",
            "The Most Satisfying Video Ever! ✨",
            "Relaxing Visuals for Stress Relief 🎧",
            "Can You Watch This Without Tingles? 😴",
            "Deeply Satisfying ASMR 💤",
            "Satisfying Art That Relaxes You ✨",
            "This Will Make You Sleep Instantly 🌙",
            "Oddly Satisfying Things 🤤",
            "Brain Massage: Visual ASMR 🧠",
            "Ultimate Stress Relief Video 💆‍♂️",
            "Satisfying Cleaning & Crushing 💥",
            "Wait for the end... So Satisfying! 😱",
            "Instant Stress Relief (100% Works) ✨",
            "Smooth and Relaxing Moments 🧊",
            "Why is this so satisfying? 🧐",
            "Video to Calm Your Anxiety 💖",
            "Perfectly Satisfying Shorts 💯",
            "Pure Satisfaction for Your Brain 🧠✨",
            "Daily Dose of Satisfaction 💊",
            "You Need to Watch This! 😲"
        ]

        # Randomly ek title chuno
        selected_title = random.choice(viral_titles_list)
        
        # Title ke aage hashtags lagao
        final_title = f"{selected_title} #Shorts #Satisfying"

        print(f"Selected Title: {final_title}")

        # --- DESCRIPTION ---
        description_text = f"""
{selected_title}

This oddly satisfying video will help you relax, sleep, and relieve stress. 
Enjoy the visual ASMR triggers! 🎧✨

👇 SUBSCRIBE for Daily Relaxation!
https://www.youtube.com/@YOUR_CHANNEL_HANDLE?sub_confirmation=1

---
#shorts #satisfying #oddlysatisfying #asmr #relaxing #stressrelief #calming #sleep #visualasmr #crunchy #viral #trending #cleaning #slime #satisfyingvideo
"""

        viral_tags = [
            'shorts', 'satisfying', 'oddly satisfying', 'asmr', 'relaxing', 
            'stress relief', 'calming', 'sleep', 'visual asmr', 'crunchy', 
            'slime', 'soap cutting', 'sand', 'viral', 'trending', 'youtube shorts'
        ]

        body = {
            'snippet': {
                'title': final_title,  
                'description': description_text,
                'tags': viral_tags,
                'categoryId': '24' # Entertainment
            },
            'status': {
                'privacyStatus': 'public', 
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

        # 5. Video Move Karna
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
        exit(1)

if __name__ == "__main__":
    main()
