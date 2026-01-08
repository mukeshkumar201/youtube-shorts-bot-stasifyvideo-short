import os
import json
import random
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from instagrapi import Client

# --- VIDEO EDITING ---
from moviepy.editor import VideoFileClip, vfx

# --- 1. SETUP GOOGLE LOGIN ---
def get_google_services():
    # Note: Maine variable names standardize kar diye hain (G_CLIENT_ID etc.)
    # Taaki YAML file same rahe.
    creds = Credentials(
        None,
        refresh_token=os.environ['G_REFRESH_TOKEN'],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ['G_CLIENT_ID'],
        client_secret=os.environ['G_CLIENT_SECRET']
    )
    return build('drive', 'v3', credentials=creds), build('youtube', 'v3', credentials=creds)

# --- 2. PRO EDITING FUNCTION (Speed + Color + Border) ---
def process_video(raw_path, final_path):
    print("🎬 Editing Started: Speed, Color & Border...")
    
    # 1. Video Load
    clip = VideoFileClip(raw_path)
    
    # 2. Speed 1.1x (Copyright Protection)
    clip = clip.fx(vfx.speedx, 1.1)
    
    # 3. Filter (Color Vibrance)
    clip = clip.fx(vfx.colorx, 1.2)
    
    # 4. Border (White Gap - Aesthetic Look)
    clip = clip.margin(top=40, bottom=40, left=40, right=40, color=(255, 255, 255))
    
    # 5. Save Final Video
    clip.write_videofile(
        final_path, 
        codec="libx264", 
        audio_codec="aac", 
        fps=24,
        verbose=False, 
        logger=None
    )
    print("✅ Video Processing Complete!")

# --- MAIN LOGIC ---
def main():
    print("🚀 Satisfying Bot (Pro Version) Started...")

    # -- DRIVE SETUP --
    try:
        drive, youtube = get_google_services()
        # Secrets ke naam check kar lena
        queue_folder_id = os.environ['DRIVE_QUEUE_FOLDER'] 
        done_folder_id = os.environ['DRIVE_DONE_FOLDER']
    except Exception as e:
        print(f"❌ Login Error: {e}")
        return

    # -- CHECK FOR VIDEO --
    print("🔍 Checking Drive for videos...")
    results = drive.files().list(
        q=f"'{queue_folder_id}' in parents and mimeType contains 'video/' and trashed=false",
        fields="files(id, name)",
        pageSize=1
    ).execute()
    items = results.get('files', [])

    if not items:
        print("❌ Folder Khali Hai (No Videos).")
        return

    video_file = items[0]
    raw_path = "raw_video.mp4"
    final_path = "final_video.mp4"
    print(f"📥 Found Video: {video_file['name']}")

    # -- DOWNLOAD VIDEO --
    request = drive.files().get_media(fileId=video_file['id'])
    with open(raw_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
    print("✅ Download Complete.")

    # -- EDIT & PROCESS --
    try:
        process_video(raw_path, final_path)
        upload_file = final_path
    except Exception as e:
        print(f"❌ Editing Failed: {e}. Uploading Raw Video.")
        upload_file = raw_path

    # -- GENERATE TITLE & DESCRIPTION --
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

    selected_title = random.choice(viral_titles_list)
    final_title = f"{selected_title} #Shorts #Satisfying"

    description_text = f"""
{selected_title}

This oddly satisfying video will help you relax, sleep, and relieve stress. 
Enjoy the visual ASMR triggers! 🎧✨

👇 SUBSCRIBE for Daily Relaxation!

---
#shorts #satisfying #oddlysatisfying #asmr #relaxing #stressrelief #calming #sleep #visualasmr #crunchy #viral #trending #cleaning #slime #satisfyingvideo
"""
    viral_tags = [
        'shorts', 'satisfying', 'oddly satisfying', 'asmr', 'relaxing', 
        'stress relief', 'calming', 'sleep', 'visual asmr', 'crunchy', 
        'slime', 'soap cutting', 'sand', 'viral', 'trending', 'youtube shorts'
    ]

    # -- YOUTUBE UPLOAD --
    try:
        print(f"🎥 YouTube Uploading: {final_title}")
        body = {
            'snippet': {
                'title': final_title,
                'description': description_text,
                'tags': viral_tags,
                'categoryId': '24' # Entertainment
            },
            'status': {'privacyStatus': 'public', 'selfDeclaredMadeForKids': False}
        }
        media = MediaFileUpload(upload_file, chunksize=-1, resumable=True)
        youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()
        print("✅ YouTube Upload Success!")
    except Exception as e: print(f"❌ YouTube Failed: {e}")

    # -- INSTAGRAM UPLOAD --
    try:
        print("📸 Instagram Uploading...")
        cl = Client()
        # Session load (INSTA_SETTINGS json secret se)
        cl.set_settings(json.loads(os.environ['INSTA_SETTINGS']))
        cl.login(os.environ['INSTA_USERNAME'], os.environ['INSTA_PASSWORD'])
        
        insta_caption = f"{selected_title}\n.\nDouble Tap if this relaxed you! ❤️\n.\n#satisfying #asmr #oddlysatisfying #relax"
        
        cl.clip_upload(upload_file, insta_caption)
        print("✅ Instagram Upload Success!")
    except Exception as e: print(f"❌ Instagram Failed: {e}")

    # -- CLEANUP --
    print("🧹 Cleaning up...")
    try:
        drive.files().update(
            fileId=video_file['id'], addParents=done_folder_id, removeParents=queue_folder_id
        ).execute()
    except Exception as e:
        print(f"⚠️ Drive Move Failed: {e}")

    if os.path.exists(raw_path): os.remove(raw_path)
    if os.path.exists(final_path): os.remove(final_path)
    print("🎉 All Done! Bot Finished.")

if __name__ == "__main__":
    main()
