from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, DocumentAttributeVideo
from datetime import datetime, timedelta
from config import CHANNEL_ID
from database import Database

class ChannelParser:
    def __init__(self, telegram_client):
        self.client = telegram_client
        self.db = Database()
    
    async def parse_active_posts(self):

        channel = await self.client.get_entity(CHANNEL_ID)
        time_limit = datetime.now() - timedelta(hours=48)

        posts_data = []
        async for message in self.client.iter_messages(channel, limit=100):
            if message.date.replace(tzinfo=None) < time_limit:
                break

            post_data = await self.parse_single_post(message)
            if post_data: 
                posts_data.append(post_data)
        return posts_data

    async def parse_single_post(self, message):
        try:
            return {
                'post_id': message.id,
                'author': await self.get_author(message),
                'post_type': self.get_content_type(message),
                'views': message.views or 0,
                'reactions': await self.get_reactions_count(message),
                'publish_time': message.date
            }
        except Exception as e:
            print(f"Ошибка парсинга: {e}")
            return None
        
    async def get_author(self, message):
        if message.from_id:
            try:
                user = await self.client.get_entity(message.from_id)
                return user.username
            except Exception as e:
                print(f"Ошибка: {e}")
                return "unknown"
        return "channel"
    
    def get_content_type(self, message):
       if not message.media:
           return "text"

       if isinstance(message.media, MessageMediaPhoto):
           return "photo"
       elif isinstance(message.media, MessageMediaDocument):
          document = message.media.document
          if any(isinstance(attr, DocumentAttributeVideo) for attr in document.attributes):
              return "video"
          return "document"
       return "other"
    
    async def get_reactions_count(self, message):
        if hasattr(message, 'reactions') and message.reactions:
            return sum(reaction.count for reaction in message.reactions.results)
        return 0