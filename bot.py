import telebot
import logging
from config import config
from cache.redis_client import redis_client
from cache.cache_handlers import news_cache, user_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(config.telegram.token)

@bot.message_handler(commands="start")
def start(message):
    user_data = {
        'id' : message.from_user.id,
        'name' : message.from_user.first_name,
        'last_seen' : str(message.date)
    }
    user_cache.set(f"user:{message.from_user.id}", user_data, ttl=86400)

    redis_status = "run" if redis_client.is_connected() else "not connected"

    bot.reply_to(
        message,
        f"Hello!/n/n"
        f"Redis status: {redis_status}"
        f"Mode: {'DEBUG' if config.debug else 'PRODUCTION'}"
    )

@bot.message_handler(commands="stats")
def stats(message):
    cmd_count = redis_client.incr(f"stats:commands:{message.date//3600}")

    bot.reply_to(
        message,
        f"Stats:/n"
        f"Teams per hour: {cmd_count}/n"
        f"Redis: {'run' if redis_client.is_connected() else 'not connected'}"
    )

@bot.message_handler(commands=[clearcache])
def clear_cache(message):
    if message.from_user.id == 123456789:
        cleared = news_cache.clear()
        bot.reply_to(message, f"{cleared} keys were cleared from the cache")
    else:
        bot.reply_to(message, f"Not enough rigths")

@bot.message_handler(func=lambda m: True)
def echo(message):
    redis_client.rpush(f"history:{message.from_user.id}", message.text)
    redis_client.expire(f"history:{message.from_user.id}", 3600)

    bot.reply_to(message, f"Yoy are talks: {message.text}")

if __name__ == "__main__":
    logger.info("Bot starts")
    bot.polling()


