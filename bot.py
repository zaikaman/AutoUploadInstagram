from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import random
import json
import os
import yt_dlp
import schedule
from datetime import datetime
from insta_uploader import upload_to_instagram

# Constants
VIDEOS_DIR = "videos"
TRACKED_URLS_FILE = "tracked_urls.json"
TIKTOK_PROFILE = "https://www.tiktok.com/@kienvocal"
INSTA_USERNAME = "kien.vocal"
INSTA_PASSWORD = "lovelybaby"

def ensure_directory_exists():
    if not os.path.exists(VIDEOS_DIR):
        os.makedirs(VIDEOS_DIR)

def load_tracked_urls():
    if os.path.exists(TRACKED_URLS_FILE):
        with open(TRACKED_URLS_FILE, 'r') as f:
            return json.load(f)
    return {"downloaded_urls": []}

def save_tracked_urls(urls_data):
    with open(TRACKED_URLS_FILE, 'w') as f:
        json.dump(urls_data, f, indent=4)

def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(VIDEOS_DIR, '%(id)s.%(ext)s'),
        'quiet': False,  # Enable output for debugging
        'no_warnings': False,
        'extractor_args': {
            'tiktok': {
                'download_timeout': 30,
                'extract_flat': True,
                'allow_redirects': True
            }
        },
        # Add cookies and headers to bypass restrictions
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }
    }
    
    try:
        # First try with yt-dlp's built-in extractor
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                return True
            except Exception as e:
                print(f"First attempt failed: {e}")
                
                # If first attempt fails, try with different format
                ydl_opts['format'] = 'bestvideo*+bestaudio/best'
                try:
                    info = ydl.extract_info(url, download=True)
                    return True
                except Exception as e:
                    print(f"Second attempt failed: {e}")
                    return False
                    
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def create_stealth_driver():
    # Use undetected-chromedriver instead of regular Chrome
    options = uc.ChromeOptions()
    
    # Basic stealth settings
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--window-size=1920,1080")
    
    # Block notifications and popups
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.automatic_downloads": 1
    }
    options.add_experimental_option("prefs", prefs)
    
    # Additional privacy settings
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-infobars')
    
    # Random user agent
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
    ]
    options.add_argument(f'--user-agent={random.choice(user_agents)}')
    
    # Create driver with undetected-chromedriver
    driver = uc.Chrome(options=options)
    
    # Set window size and position randomly
    driver.set_window_size(random.randint(1050, 1200), random.randint(800, 960))
    driver.set_window_position(random.randint(0, 100), random.randint(0, 100))
    
    # Execute additional stealth scripts
    driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        window.chrome = {
            runtime: {}
        };
    """)
    
    return driver

def get_video_urls(driver, num_videos=10):
    try:
        # Wait for video links to be present
        wait = WebDriverWait(driver, 10)
        video_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-e2e="user-post-item"] a')))
        
        # Skip first 3 pinned videos and get next 10 video URLs
        video_urls = []
        for element in video_elements[3:13]:  # Skip first 3, get next 10
            try:
                url = element.get_attribute('href')
                if url and url.startswith('https://www.tiktok.com/@kienvocal/video/'):
                    video_urls.append(url)
            except:
                continue
                
        return video_urls
    except Exception as e:
        print(f"Error getting video URLs: {e}")
        return []

def process_new_videos(video_urls):
    if not video_urls:
        print("No videos to process")
        return
        
    # Load existing tracked URLs
    tracked_data = load_tracked_urls()
    downloaded_urls = tracked_data["downloaded_urls"]
    
    # Find new URLs
    new_urls = [url for url in video_urls if url not in downloaded_urls]
    
    if not new_urls:
        print("No new videos found")
        return
        
    print(f"\nFound {len(new_urls)} new videos to download")
    
    # Download new videos and update tracked URLs
    successful_downloads = 0
    for url in new_urls:
        print(f"\nDownloading: {url}")
        if download_video(url):
            downloaded_urls.append(url)
            save_tracked_urls(tracked_data)
            successful_downloads += 1
            print("Download successful")
        else:
            print("Download failed")
    
    print(f"\nDownloaded {successful_downloads} out of {len(new_urls)} new videos")

def visit_tiktok_profile():
    max_retries = 50000000
    current_retry = 0
    video_urls = []
    
    while current_retry < max_retries and not video_urls:
        if current_retry > 0:
            print(f"\nRetry attempt {current_retry}/{max_retries}...")
            time.sleep(random.uniform(3, 6))
            
        driver = create_stealth_driver()
        
        try:
            time.sleep(random.uniform(2, 4))
            driver.get("https://www.tiktok.com/@kienvocal")
            time.sleep(3)
            
            for _ in range(3):
                scroll_amount = random.randint(300, 700)
                driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
                time.sleep(random.uniform(1, 2))
            
            video_urls = get_video_urls(driver)
            
            if video_urls:
                print("\nSuccessfully found video URLs:")
                for i, url in enumerate(video_urls, 1):
                    print(f"{i}. {url}")
            else:
                print("No video URLs found in this attempt")
            
        except Exception as e:
            print(f"An error occurred: {e}")
            
        finally:
            try:
                driver.quit()
            except:
                pass
        
        current_retry += 1
    
    if not video_urls:
        print("\nFailed to get video URLs after all retries")
    
    return video_urls

def job():
    print("\nStarting scheduled job...")
    ensure_directory_exists()
    video_urls = visit_tiktok_profile()
    process_new_videos(video_urls)
    
    # Upload new videos to Instagram
    try:
        print("\nStarting Instagram upload...")
        upload_to_instagram(INSTA_USERNAME, INSTA_PASSWORD)
    except Exception as e:
        print(f"Error during Instagram upload: {e}")
    
    print("Job completed")

def main():
    # Run job immediately once
    job()
    
    # Schedule job to run every 12 hours
    schedule.every(12).hours.do(job)
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()