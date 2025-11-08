import sys
import os
try:
    import imghdr
except ModuleNotFoundError:
    sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime
import asyncio
from telethon import TelegramClient

from config import API_ID, API_HASH, PHONE
from database import Database
from analytics import Analytics
from parser import ChannelParser

class PerformanceAnalytics:
    def __init__(self):
        self.client = TelegramClient('user_session', API_ID, API_HASH)
        self.db = Database()
        self.parser = ChannelParser(self.client)
        self.analytics = Analytics(self.client)
    
    async def start_monitoring(self):
        await self.client.start(phone=PHONE)
        
        await self.analytics.update_subscribers()

        while True:
            try:
                await self.analytics.update_subscribers()
                print(f"\nНачало цикла в {datetime.now()}")

                posts_data = await self.parser.parse_active_posts()
                print(f"Найдено постов: {len(posts_data)}")

                for post in posts_data:
                    effectiveness = self.analytics.calculate_effectiveness(post)
                    self.db.save_post_data(post, effectiveness)

                self.db.deactivate_old_posts(hours_old=48)

                self.db.export_to_excel()
 
                await asyncio.sleep(3600)
                
            except Exception as e:
                print(f"Ошибка в цикле: {e}")
                await asyncio.sleep(300)

async def main():
    bot = PerformanceAnalytics()
    await bot.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())