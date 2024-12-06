from instagrapi import Client
import os
import json
import time
from datetime import datetime
import moviepy.editor as mp

VIDEOS_DIR = "c:/Users/ADMIN/Desktop/AutoPost/videos"
POSTED_URLS_FILE = "c:/Users/ADMIN/Desktop/AutoPost/posted_urls.json"

def load_posted_urls():
    if os.path.exists(POSTED_URLS_FILE):
        with open(POSTED_URLS_FILE, 'r') as f:
            return json.load(f)
    return {"posted_urls": []}

def save_posted_urls(urls_data):
    with open(POSTED_URLS_FILE, 'w') as f:
        json.dump(urls_data, f, indent=4)

def validate_video(video_path):
    try:
        # Load video to verify it's valid
        video = mp.VideoFileClip(video_path)
        duration = video.duration
        video.close()
        
        # Check if video meets Instagram requirements
        if duration > 90:  # Instagram reels max duration
            print(f"Warning: Video duration ({duration}s) exceeds Instagram limit (90s)")
        return True
    except Exception as e:
        print(f"Error validating video: {e}")
        return False

def upload_single_video(cl, video_path, caption):
    max_retries = 3
    retry_count = 0
    
    # Validate video before attempting upload
    if not validate_video(video_path):
        print("Video validation failed")
        return False
    
    while retry_count < max_retries:
        try:
            print(f"Attempting upload (try {retry_count + 1}/{max_retries})")
            
            # Upload as reel
            media = cl.clip_upload(
                video_path,
                caption=caption,
                extra_data={
                    "custom_accessibility_caption": "",
                    "like_and_view_counts_disabled": False,
                    "disable_comments": False
                }
            )
            
            if media:
                print("Upload successful!")
                return True
                
        except Exception as e:
            print(f"Error on attempt {retry_count + 1}: {e}")
        
        retry_count += 1
        if retry_count < max_retries:
            print(f"Waiting 30 seconds before retry...")
            time.sleep(30)
    
    return False

def upload_to_instagram(username, password):
    # Initialize client
    cl = Client()
    
    try:
        # Login
        print(f"Logging in as {username}...")
        cl.login(username, password)
        
        # Load tracking data
        posted_data = load_posted_urls()
        posted_urls = posted_data["posted_urls"]
        
        # Get list of video files
        video_files = []
        for file in os.listdir(VIDEOS_DIR):
            if file.endswith('.mp4'):
                full_path = os.path.join(VIDEOS_DIR, file)
                if full_path not in posted_urls:
                    video_files.append(full_path)
        
        if not video_files:
            print("No new videos to upload")
            return
        
        total_videos = len(video_files)
        print(f"\nFound {total_videos} new videos to upload")
        
        # Upload each video
        for index, video_path in enumerate(video_files, 1):
            try:
                print(f"\nUploading video {index}/{total_videos}")
                print(f"Video path: {video_path}")
                
                # Generate caption
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                caption = f"🎥✨ #reels #trending #viral #music #cover"
                
                # Upload video with retries
                if upload_single_video(cl, video_path, caption):
                    print(f"Upload successful for video {index}!")
                    posted_urls.append(video_path)
                    save_posted_urls(posted_data)
                else:
                    print(f"Upload failed for video {index} after all retries!")
                
                # 60 second delay between uploads
                if index < total_videos:  # Don't wait after the last video
                    print(f"Waiting 60 seconds before uploading next video...")
                    time.sleep(60)
                
            except Exception as e:
                print(f"Error uploading video {index} ({video_path}): {e}")
        
        print("\nUpload session completed!")
        
    except Exception as e:
        print(f"Error during Instagram session: {e}")
        
    finally:
        # Logout
        try:
            cl.logout()
        except:
            pass

if __name__ == "__main__":
    # Replace these with your Instagram credentials
    USERNAME = "kien.vocal"
    PASSWORD = "lovelybaby"
    
    upload_to_instagram(USERNAME, PASSWORD)
