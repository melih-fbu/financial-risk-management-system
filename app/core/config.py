from dotenv import load_dotenv
import os

# .env dosyasını oku
load_dotenv()

# Değişkenleri buradan al
DATABASE_URL = os.getenv("DATABASE_URL")
APP_NAME = os.getenv("APP_NAME")
DEBUG = os.getenv("DEBUG")