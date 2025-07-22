import logging
from aiogram import Bot, Dispatcher, types, executor
import os
import requests

# إعدادات عامة
logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
SHRINKME_API_KEY = os.getenv("SHRINKME_API_KEY")
LANGUAGES = os.getenv("LANGUAGES", "en,ar")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# أمر /start – يرحب ويعرض اللغات
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    langs = LANGUAGES.split(",")
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for lang in langs:
        keyboard.insert(types.InlineKeyboardButton(text=lang.upper(), callback_data=f"lang:{lang}"))
    await message.answer("🎬 أهلاً في MixTV! اختر اللغة اللي تفضلها:", reply_markup=keyboard)

# اختيار اللغة
@dp.callback_query_handler(lambda c: c.data.startswith("lang:"))
async def choose_language(c: types.CallbackQuery):
    lang = c.data.split(":")[1]
    await c.message.answer(f"🔍 اختر الآن اسم الفيلم أو المسلسل باللغة *{lang.upper()}*:") 
    await bot.answer_callback_query(c.id)

# التعامل مع النص – بحث في TMDb
@dp.message_handler()
async def handle_search(message: types.Message):
    query = message.text.strip()
    url = f"https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": query}
    res = requests.get(url, params=params).json()
    if res.get("results"):
        first = res["results"][0]
        title = first.get("title", first.get("name"))
        link = f"https://www.themoviedb.org/movie/{first['id']}"
        # تقصير الرابط
        shrink = requests.get("https://shrinkme.io/api", params={
            "apiKey": SHRINKME_API_KEY, "url": link
        }).json().get("shortenedUrl", link)
        await message.answer(f"🎞️ *{title}*\n🔗 {shrink}", parse_mode="Markdown")
    else:
        await message.reply("😕 ما حصلت شيء، جرّب كلمة ثانية!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
