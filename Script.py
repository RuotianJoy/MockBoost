
import os

# DeepSeek API Key
os.environ["API_KEY"] = "sk-b3b2513642384b82980d65730ed10494"

# Baidu Speech Recognition API Keys
os.environ["BAIDU_APP_ID"] = "118047893"
os.environ["BAIDU_API_KEY"] = "hFWTIJVpL9dPKkr1f3ywmIru"
os.environ["BAIDU_SECRET_KEY"] = "QRdTgB3N6XbV98ZgvXrBH63muNuXyI7p"

# Verify API keys
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY is not set")

baidu_keys = ["BAIDU_APP_ID", "BAIDU_API_KEY", "BAIDU_SECRET_KEY"]
for key in baidu_keys:
    if not os.getenv(key):
        raise ValueError(f"{key} is not set")