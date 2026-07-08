import requests
import json
import time
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional

try:
    from app_store_scraper import AppStore
    HAS_APP_STORE_SCRAPER = True
except ImportError:
    HAS_APP_STORE_SCRAPER = False

class AppStoreReviewCollector:
    def __init__(self):
        self.base_url = "https://itunes.apple.com"
        self.request_delay = 2
        self.max_retries = 3

    def extract_app_id(self, url: str) -> str:
        match = re.search(r'id(\d+)', url)
        if match:
            return match.group(1)
        raise ValueError(f"无法从链接中提取App ID: {url}")

    def fetch_reviews_with_scraper(self, app_id: str, country: str = "us", limit: int = 500) -> List[Dict]:
        if not HAS_APP_STORE_SCRAPER:
            print("app-store-scraper 库未安装，跳过此方法")
            return []
        
        try:
            print(f"使用 app-store-scraper 采集评论，应用ID: {app_id}")
            app = AppStore(country=country, app_id=app_id, app_name="workout-for-women")
            app.review(how_many=limit)
            
            reviews = []
            for review in app.reviews:
                review_date = review.get("date", datetime.now())
                date_str = review_date.isoformat() if hasattr(review_date, 'isoformat') else str(review_date)
                
                reviews.append({
                    "review_id": str(review.get("id", "")),
                    "title": review.get("title", ""),
                    "content": review.get("review", ""),
                    "rating": review.get("rating", 0),
                    "version": review.get("version", ""),
                    "username": review.get("userName", ""),
                    "date": date_str,
                    "source": "app-store-scraper (Apple App Store US)"
                })
            
            print(f"app-store-scraper 成功采集 {len(reviews)} 条评论")
            return reviews[:limit]
        except Exception as e:
            print(f"app-store-scraper 采集失败: {e}")
            return []

    def fetch_reviews_rss_xml(self, app_id: str, country: str = "us", limit: int = 500) -> List[Dict]:
        reviews = []
        page = 1
        
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            print("beautifulsoup4 未安装，无法解析XML")
            return []
        
        while len(reviews) < limit:
            try:
                url = f"{self.base_url}/{country}/rss/customerreviews/id={app_id}/sortBy=mostRecent/xml"
                print(f"请求XML URL: {url}")
                response = requests.get(url, params={"page": page}, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, "xml")
                entries = soup.find_all("entry")
                
                if not entries:
                    print("没有更多评论")
                    break
                
                for entry in entries:
                    try:
                        review_id = entry.find("id").get_text() if entry.find("id") else ""
                        title = entry.find("title").get_text() if entry.find("title") else ""
                        content_elem = entry.find("content", {"type": "text"})
                        content = content_elem.get_text() if content_elem else ""
                        rating = entry.find("im:rating").get_text() if entry.find("im:rating") else "0"
                        version = entry.find("im:version").get_text() if entry.find("im:version") else ""
                        
                        author_elem = entry.find("author")
                        username = author_elem.find("name").get_text() if author_elem and author_elem.find("name") else ""
                        
                        date_str = entry.find("updated").get_text() if entry.find("updated") else ""
                        
                        try:
                            date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
                        except:
                            date = datetime.now()
                        
                        reviews.append({
                            "review_id": review_id,
                            "title": title,
                            "content": content,
                            "rating": int(rating),
                            "version": version,
                            "username": username,
                            "date": date.isoformat(),
                            "source": "Apple RSS XML Feed (US Storefront)"
                        })
                    except Exception as parse_e:
                        print(f"解析单条评论失败: {parse_e}")
                
                if len(entries) < 50:
                    break
                
                page += 1
                time.sleep(self.request_delay)
                
            except requests.exceptions.RequestException as e:
                print(f"RSS XML请求失败: {e}")
                break
        
        return reviews[:limit]

    def save_reviews(self, reviews: List[Dict], app_id: str, output_dir: str = "data/raw") -> str:
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{output_dir}/reviews_{app_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(reviews, f, ensure_ascii=False, indent=2)
        
        return filename

    def load_reviews(self, filepath: str) -> List[Dict]:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_cached_reviews(self, app_id: str, cache_dir: str = "data/cached") -> List[Dict]:
        cache_file = os.path.join(cache_dir, f"reviews_{app_id}.json")
        if os.path.exists(cache_file):
            print(f"加载缓存数据: {cache_file}")
            return self.load_reviews(cache_file)
        return []

    def collect(self, app_store_url: str, output_dir: str = "data/raw") -> Dict:
        try:
            app_id = self.extract_app_id(app_store_url)
            print(f"开始采集应用ID: {app_id}")
            
            reviews = []
            data_source = ""
            
            reviews = self.fetch_reviews_with_scraper(app_id)
            if reviews:
                data_source = "app-store-scraper (Apple App Store US Storefront)"
            
            if not reviews:
                reviews = self.fetch_reviews_rss_xml(app_id)
                if reviews:
                    data_source = "Apple RSS XML Feed (US Storefront)"
            
            if not reviews:
                reviews = self.load_cached_reviews(app_id)
                if reviews:
                    data_source = "本地缓存数据（之前采集的真实数据）"
            
            if not reviews:
                reviews = self._generate_sample_data(app_id)
                data_source = "示例数据（网络环境限制，用于演示）"
            
            print(f"成功采集 {len(reviews)} 条评论")
            
            filepath = self.save_reviews(reviews, app_id, output_dir)
            print(f"数据已保存到: {filepath}")
            
            limitations = "数据来源于美区App Store，仅获取最近评论"
            if data_source == "示例数据（网络环境限制，用于演示）":
                limitations = "⚠️ 网络环境限制，当前使用示例数据。建议在有海外网络环境时重新采集真实数据。"
            
            return {
                "success": True,
                "app_id": app_id,
                "total_reviews": len(reviews),
                "file_path": filepath,
                "data_source": data_source,
                "limitations": limitations
            }
        except Exception as e:
            print(f"采集异常: {e}")
            return {
                "success": False,
                "error": str(e),
                "data_source": "Apple App Store",
                "limitations": "API请求失败或数据解析异常"
            }

    def _generate_sample_data(self, app_id: str) -> List[Dict]:
        today = datetime.now()
        
        sample_reviews = [
            {
                "review_id": "100001",
                "title": "App crashes on launch after update",
                "content": "Since updating to version 3.3.0, the app crashes immediately when I try to open it. I've tried restarting my phone and reinstalling the app, but nothing works. This is very frustrating!",
                "rating": 1,
                "version": "3.3.0",
                "username": "crash_user",
                "date": (today - timedelta(days=1)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100002",
                "title": "Great app but crashes during workouts",
                "content": "I love the workout videos and the variety of exercises. However, the app crashes about halfway through every workout. This makes it hard to track my progress.",
                "rating": 3,
                "version": "3.3.0",
                "username": "fitness_junkie",
                "date": (today - timedelta(days=2)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100003",
                "title": "Freezes when switching exercises",
                "content": "The app keeps freezing when I try to switch between different exercises in a workout. Sometimes I have to force quit and start over. Please fix this bug!",
                "rating": 2,
                "version": "3.3.0",
                "username": "gym_rat",
                "date": (today - timedelta(days=3)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100004",
                "title": "Please add dark mode!",
                "content": "I workout at night and the bright white screen is really hard on my eyes. Adding a dark mode would be a huge improvement. Other fitness apps have this feature.",
                "rating": 4,
                "version": "3.2.1",
                "username": "night_owl",
                "date": (today - timedelta(days=4)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100005",
                "title": "Apple Watch integration needed",
                "content": "I use my Apple Watch for all my fitness tracking. It would be amazing if the app could sync with Apple Watch to track heart rate, calories, and workout duration automatically.",
                "rating": 4,
                "version": "3.2.1",
                "username": "apple_fan",
                "date": (today - timedelta(days=5)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100006",
                "title": "Add yoga sessions",
                "content": "The strength training workouts are great! But I also do yoga and would love to see yoga sessions added to the app. It would make this a complete fitness solution.",
                "rating": 4,
                "version": "3.3.0",
                "username": "yoga_lover",
                "date": (today - timedelta(days=6)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100007",
                "title": "Battery drain is terrible",
                "content": "After using this app for 30 minutes, my phone battery drops by 25%. This is way too much. Other similar apps don't drain the battery nearly as much. Please optimize!",
                "rating": 2,
                "version": "3.3.0",
                "username": "battery_concerned",
                "date": (today - timedelta(days=7)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100008",
                "title": "App is very slow to load",
                "content": "The app takes forever to load the workout videos and menus. Sometimes I have to wait 10+ seconds just to navigate to the next screen. This needs to be fixed.",
                "rating": 2,
                "version": "3.3.0",
                "username": "speed_freak",
                "date": (today - timedelta(days=8)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100009",
                "title": "Lag during video playback",
                "content": "The workout videos lag and stutter, especially when I'm doing HIIT workouts. It's hard to follow along when the video keeps pausing. This is a major issue.",
                "rating": 2,
                "version": "3.3.0",
                "username": "video_watcher",
                "date": (today - timedelta(days=9)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100010",
                "title": "UI is confusing",
                "content": "I find the user interface really confusing. It's hard to find the workouts I want, and the navigation is not intuitive. A redesign would be very helpful.",
                "rating": 3,
                "version": "3.2.1",
                "username": "confused_user",
                "date": (today - timedelta(days=10)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100011",
                "title": "Better progress tracking",
                "content": "The progress tracking is basic. I would like to see charts and stats showing my improvement over time. Maybe weekly summaries and achievements.",
                "rating": 4,
                "version": "3.2.1",
                "username": "stats_lover",
                "date": (today - timedelta(days=11)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100012",
                "title": "Subscription is too expensive",
                "content": "$19.99/month is way too expensive for what this app offers. I can get similar features from other apps for half the price. I would subscribe if it was cheaper.",
                "rating": 2,
                "version": "3.3.0",
                "username": "budget_user",
                "date": (today - timedelta(days=12)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100013",
                "title": "Free version is too limited",
                "content": "The free version only gives you 3 workouts per week. That's not enough to make any progress. You basically have to pay to use the app properly.",
                "rating": 2,
                "version": "3.3.0",
                "username": "free_trial_user",
                "date": (today - timedelta(days=13)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100014",
                "title": "Best fitness app ever!",
                "content": "I've tried so many fitness apps and this is by far the best. The workouts are challenging but doable, the trainers are great, and I've seen amazing results in just 2 months!",
                "rating": 5,
                "version": "3.2.1",
                "username": "happy_customer",
                "date": (today - timedelta(days=14)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100015",
                "title": "Love the meal planner",
                "content": "The meal planner feature is awesome! It helps me stay on track with my diet and the recipes are delicious. This app has everything I need for my fitness journey.",
                "rating": 5,
                "version": "3.3.0",
                "username": "foodie_fitness",
                "date": (today - timedelta(days=15)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100016",
                "title": "Sync issues between devices",
                "content": "My workout history doesn't sync properly between my iPhone and iPad. I completed a workout on my phone but it doesn't show up on my iPad. Very annoying!",
                "rating": 2,
                "version": "3.3.0",
                "username": "multi_device_user",
                "date": (today - timedelta(days=16)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100017",
                "title": "Progress not saving",
                "content": "I completed a 45-minute workout yesterday, but today it shows I only did 0 minutes. My progress isn't being saved properly. This is very discouraging.",
                "rating": 1,
                "version": "3.3.0",
                "username": "progress_lost",
                "date": (today - timedelta(days=17)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100018",
                "title": "More beginner workouts",
                "content": "I'm new to working out and some of the exercises are too hard. I would like to see more beginner-friendly workouts. Maybe a 'getting started' program.",
                "rating": 3,
                "version": "3.2.1",
                "username": "fitness_newbie",
                "date": (today - timedelta(days=18)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100019",
                "title": "Social features would be great",
                "content": "It would be fun to connect with friends using the app, share workout achievements, and maybe even compete. A social aspect would make working out more motivating.",
                "rating": 4,
                "version": "3.2.1",
                "username": "social_butterfly",
                "date": (today - timedelta(days=19)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100020",
                "title": "Custom workout plans",
                "content": "I wish I could create my own custom workout plans instead of just following the pre-made ones. It would be great to select specific exercises and arrange them as I like.",
                "rating": 4,
                "version": "3.3.0",
                "username": "custom_user",
                "date": (today - timedelta(days=20)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100021",
                "title": "Video quality is poor",
                "content": "The workout videos are often blurry and the audio quality is bad. I can't always hear what the trainer is saying. Please improve the video production quality.",
                "rating": 2,
                "version": "3.3.0",
                "username": "video_quality",
                "date": (today - timedelta(days=21)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100022",
                "title": "No offline mode",
                "content": "I travel a lot and don't always have internet access. It would be great if I could download workouts for offline use. This is a must-have feature.",
                "rating": 3,
                "version": "3.2.1",
                "username": "traveler",
                "date": (today - timedelta(days=22)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100023",
                "title": "Excellent customer support",
                "content": "I had an issue with my subscription and the support team responded within hours. They were very helpful and resolved my issue quickly. Great service!",
                "rating": 5,
                "version": "3.2.1",
                "username": "satisfied_customer",
                "date": (today - timedelta(days=23)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100024",
                "title": "Workout reminders",
                "content": "I often forget to workout. Adding reminders or push notifications would help me stay consistent. Maybe weekly workout reminders based on my schedule.",
                "rating": 4,
                "version": "3.2.1",
                "username": "forgetful_fitness",
                "date": (today - timedelta(days=24)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100025",
                "title": "Glitch: sound not working",
                "content": "The audio doesn't work on some workout videos. I've tried adjusting the volume and restarting the app, but it's still broken. This makes it impossible to follow the workouts.",
                "rating": 1,
                "version": "3.3.0",
                "username": "audio_issues",
                "date": (today - timedelta(days=25)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100026",
                "title": "Recovery mode missing",
                "content": "After intense workouts, I need recovery stretches. It would be great to have a dedicated recovery mode with stretching exercises and foam rolling guides.",
                "rating": 4,
                "version": "3.2.1",
                "username": "recovery_seeker",
                "date": (today - timedelta(days=26)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100027",
                "title": "Statistics page is confusing",
                "content": "The statistics page is hard to understand. I can't easily see my workout history, calories burned, or progress. A cleaner, more organized stats page would be better.",
                "rating": 3,
                "version": "3.3.0",
                "username": "stats_confused",
                "date": (today - timedelta(days=27)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100028",
                "title": "Yearly subscription discount",
                "content": "I would be happy to pay for a yearly subscription if there was a significant discount. Monthly is too expensive, but a yearly plan at 50% off would be great.",
                "rating": 3,
                "version": "3.3.0",
                "username": "yearly_subscriber",
                "date": (today - timedelta(days=28)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100029",
                "title": "Love the challenges!",
                "content": "The 30-day challenges are awesome! They keep me motivated and I've seen great results. Please add more challenges like a 60-day transformation challenge.",
                "rating": 5,
                "version": "3.3.0",
                "username": "challenge_lover",
                "date": (today - timedelta(days=29)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100030",
                "title": "App won't play music",
                "content": "When I try to play my own music while working out, the app's audio takes over and my music stops. I want to listen to my own playlist while following the workout.",
                "rating": 2,
                "version": "3.3.0",
                "username": "music_lover",
                "date": (today - timedelta(days=30)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100031",
                "title": "Add meditation sessions",
                "content": "I practice mindfulness meditation daily and would love to see guided meditation sessions added to the app. It would be great for mental health alongside physical fitness.",
                "rating": 4,
                "version": "3.2.1",
                "username": "meditation_fan",
                "date": (today - timedelta(days=31)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100032",
                "title": "Search function broken",
                "content": "The search bar doesn't work properly. When I search for specific workouts or exercises, it returns no results even though I know they exist in the app.",
                "rating": 2,
                "version": "3.3.0",
                "username": "search_user",
                "date": (today - timedelta(days=32)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100033",
                "title": "Timer feature is great",
                "content": "I love the built-in timer for rest periods between exercises. It helps me keep track of my workout and not waste time. This is a really useful feature!",
                "rating": 5,
                "version": "3.2.1",
                "username": "timer_fan",
                "date": (today - timedelta(days=33)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100034",
                "title": "Profile page needs update",
                "content": "The profile page looks outdated and doesn't show much information. I would like to see more stats, achievements, and customization options for my profile.",
                "rating": 3,
                "version": "3.3.0",
                "username": "profile_user",
                "date": (today - timedelta(days=34)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100035",
                "title": "Notifications are annoying",
                "content": "I get too many push notifications from this app. Even when I turn them off in settings, I still get some. Can you please fix the notification settings?",
                "rating": 2,
                "version": "3.3.0",
                "username": "notification_hater",
                "date": (today - timedelta(days=35)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100036",
                "title": "Great for busy people",
                "content": "As a busy mom, I don't have much time for workouts. The 15-minute quick workouts are perfect for me. I can squeeze in a workout during naptime!",
                "rating": 5,
                "version": "3.2.1",
                "username": "busy_mom",
                "date": (today - timedelta(days=36)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100037",
                "title": "Bug: cannot share workouts",
                "content": "When I try to share my workout progress on social media, the app crashes. I've tried multiple times and it always happens. This feature needs to be fixed.",
                "rating": 2,
                "version": "3.3.0",
                "username": "social_sharer",
                "date": (today - timedelta(days=37)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100038",
                "title": "Add Pilates workouts",
                "content": "I do Pilates regularly and would love to see more Pilates workouts in the app. The current selection is very limited. Please add more variety!",
                "rating": 4,
                "version": "3.2.1",
                "username": "pilates_fan",
                "date": (today - timedelta(days=38)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100039",
                "title": "App crashes when trying to purchase",
                "content": "When I try to upgrade to the premium version, the app crashes. I've tried on multiple devices and it's the same issue. I want to subscribe but can't!",
                "rating": 1,
                "version": "3.3.0",
                "username": "payment_issue",
                "date": (today - timedelta(days=39)).isoformat(),
                "source": "Sample Data"
            },
            {
                "review_id": "100040",
                "title": "Best value for money",
                "content": "After trying many fitness apps, this one offers the best value. The workouts are high quality, the trainers are knowledgeable, and the price is reasonable. Highly recommend!",
                "rating": 5,
                "version": "3.2.1",
                "username": "value_seeker",
                "date": (today - timedelta(days=40)).isoformat(),
                "source": "Sample Data"
            }
        ]
        return sample_reviews