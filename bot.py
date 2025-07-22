import logging
import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext

# إعداد السجل
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# المتغيرات البيئية
TOKEN = os.getenv("BOT_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
SHORTENER_API_KEY = os.getenv("SHORTENER_API_KEY")

# اختصار الروابط عبر shrinkme.io
def shorten_link(original_url: str) -> str:
    try:
        api_url = "https://shrinkme.io/api/v1/shorten"
        response = requests.post(api_url, data={
            'api': SHORTENER_API_KEY,
            'url': original_url
        })
        data = response.json()
        return data['shortenedUrl'] if data['status'] == 'success' else original_url
    except Exception as e:
        return original_url

# /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("🎬 أهلاً بك في Mix TV Bot!\nاستخدم /actor لعرض أعمال أي ممثل.\nمثال:\n/actor Tom Hanks")

# /actor
def actor(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("❗️يرجى كتابة اسم الممثل بعد الأمر.\nمثال:\n/actor Brad Pitt")
        return

    actor_name = ' '.join(context.args)
    search_url = f"https://api.themoviedb.org/3/search/person?api_key={TMDB_API_KEY}&query={actor_name}"
    search_response = requests.get(search_url).json()

    if not search_response.get("results"):
        google_url = f"https://www.google.com/search?q={actor_name.replace(' ', '+')}+movies"
        keyboard = [[InlineKeyboardButton("🔍 ابحث في Google", url=google_url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(f"❌ لم يتم العثور على نتائج لـ '{actor_name}'.", reply_markup=reply_markup)
        return

    person = search_response["results"][0]
    person_id = person["id"]
    real_name = person["name"]

    credits_url = f"https://api.themoviedb.org/3/person/{person_id}/combined_credits?api_key={TMDB_API_KEY}"
    credits_response = requests.get(credits_url).json()

    works = credits_response.get("cast", [])
    works = sorted(works, key=lambda x: x.get("popularity", 0), reverse=True)[:10]

    message_lines = [f"🔍 تم العثور على: *{real_name}*\n"]

    for i, work in enumerate(works, 1):
        title = work.get("title") or work.get("name") or "بدون عنوان"
        google_url = f"https://www.google.com/search?q={title.replace(' ', '+')}"
        short_link = shorten_link(google_url)
        message_lines.append(f"🎬 {i}. [{title}]({short_link})")

    google_search_url = f"https://www.google.com/search?q={real_name.replace(' ', '+')}+movies"
    keyboard = [[InlineKeyboardButton("🔍 ابحث في Google", url=google_search_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("\n".join(message_lines), parse_mode="Markdown", reply_markup=reply_markup)

# تشغيل البوت
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("actor", actor))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
