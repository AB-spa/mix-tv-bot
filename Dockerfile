# استخدم صورة بايثون الرسمية
FROM python:3.11

# إعداد مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ كل الملفات من المشروع إلى داخل الحاوية
COPY . .

# تثبيت الحزم المطلوبة
RUN pip install --no-cache-dir -r requirements.txt

# تشغيل البوت
CMD ["python", "bot.py"]
