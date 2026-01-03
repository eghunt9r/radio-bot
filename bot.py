import telebot
from telebot import types
import yt_dlp
import os
import time

# ==========================================
# 1. الإعدادات الأساسية
# ==========================================
# ضع التوكن الخاص بك هنا
BOT_TOKEN = '7702297641:AAFG-0n3ZVt8UPRyU3oG_OKTswnudyuzcsE'

# تهيئة البوت
bot = telebot.TeleBot(BOT_TOKEN)

# حقوق المطور
DEV_NAME = "abu_aly3zid"

# ملف الكوكيز (يجب أن يكون في نفس المجلد)
COOKIES_FILE = 'cookies.txt'

# ==========================================
# 2. دالة التحميل (yt-dlp) مع دعم الكوكيز
# ==========================================
def download_media(url):
    """
    تقوم بتحميل الفيديو من الرابط باستخدام الكوكيز إذا توفرت.
    """
    timestamp = int(time.time())
    # قالب حفظ الملف (في مجلد downloads)
    output_template = f"downloads/{timestamp}_%(title)s.%(ext)s"

    ydl_opts = {
        # اختيار أفضل جودة فيديو وصوت بشرط أن تكون الصيغة MP4 لسهولة العرض
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
    }

    # إضافة ملف الكوكيز للإعدادات في حال وجوده
    if os.path.exists(COOKIES_FILE):
        ydl_opts['cookiefile'] = COOKIES_FILE
        print(f"[{time.strftime('%H:%M:%S')}] ✅ تم استخدام ملف الكوكيز.")
    else:
        print(f"[{time.strftime('%H:%M:%S')}] ⚠️ ملف الكوكيز غير موجود، التحميل مستمر بدونه.")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        print(f"❌ خطأ تحميل: {e}")
        return None

# ==========================================
# 3. معالجة الأوامر والرسائل
# ==========================================

# أمر البدء /start
@bot.message_handler(commands=['start'])
def start_command(message):
    user_name = message.from_user.first_name
    
    # رسالة ترحيبية احترافية
    welcome_msg = (
        f"👋 **أهلاً بك يا {user_name} في بوت التحميل الذكي!**\n\n"
        f"يمكنني التحميل من:\n"
        f"📺 **YouTube** | 📱 **TikTok**\n"
        f"📸 **Instagram** | 🐦 **X (Twitter)**\n"
        f"🔞 **Adult Sites** | 📝 **Blogs**\n\n"
        f"💡 **فقط أرسل لي الرابط وسأبدأ العمل فوراً.**\n"
        f"---"
    )
    
    # أزرار تفاعلية
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("❓ كيفية الاستخدام", callback_data="help")
    btn2 = types.InlineKeyboardButton("👨‍💻 المطور", callback_data="dev")
    markup.add(btn1, btn2)
    
    bot.send_message(message.chat.id, welcome_msg, reply_markup=markup, parse_mode='Markdown')
    # عرض اسم المطور في الأسفل
    bot.send_message(message.chat.id, f"🛠️ بواسطة: `{DEV_NAME}`", parse_mode='Markdown')

# التعامل مع ضغطات الأزرار
@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    if call.data == "help":
        help_txt = "كل ما عليك فعله هو نسخ رابط الفيديو من أي منصة ولصقه هنا. سأقوم بمعالجة الرابط وتحميله بأفضل جودة ممكنة ثم إرساله لك كملف فيديو."
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, help_txt)
    elif call.data == "dev":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"👨‍💻 مبرمج البوت هو: **{DEV_NAME}**", parse_mode='Markdown')

# استقبال الروابط وتحميلها
@bot.message_handler(func=lambda message: True)
def handle_links(message):
    url = message.text.strip()
    
    # التأكد من أنه رابط
    if not url.startswith("http"):
        bot.reply_to(message, "⚠️ من فضلك أرسل رابطاً صحيحاً يبدأ بـ http أو https.")
        return

    # رسالة مؤقتة للمستخدم
    status_msg = bot.reply_to(message, "⏳ **جاري معالجة الرابط والتحميل...**\n(قد يستغرق ذلك لحظات حسب طول الفيديو)", parse_mode='Markdown')

    # استدعاء دالة التحميل
    video_file = download_media(url)

    if video_file and os.path.exists(video_file):
        try:
            # التحقق من حجم الملف لسياسة تيليجرام (50 ميجا)
            size_mb = os.path.getsize(video_file) / (1024 * 1024)
            
            if size_mb > 50:
                bot.edit_message_text(f"❌ **عذراً، الملف كبير جداً!**\nحجم الفيديو: {size_mb:.1f}MB\nتيليجرام يسمح برفع 50MB فقط للبوتات العادية.", 
                                      chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode='Markdown')
            else:
                bot.edit_message_text("⬆️ **جاري رفع الفيديو إلى تيليجرام...**", chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode='Markdown')
                
                with open(video_file, 'rb') as v:
                    bot.send_video(
                        message.chat.id, 
                        v, 
                        caption=f"✅ تم التحميل بنجاح!\n\n👨‍💻 المطور: {DEV_NAME}",
                        supports_streaming=True
                    )
                # حذف رسالة الحالة
                bot.delete_message(message.chat.id, status_msg.message_id)
        
        except Exception as e:
            bot.reply_to(message, f"❌ حدث خطأ أثناء إرسال الفيديو: {e}")
        
        finally:
            # حذف الملف من السيرفر لتوفير المساحة
            if os.path.exists(video_file):
                os.remove(video_file)
    else:
        bot.edit_message_text("❌ **فشل التحميل!**\nتأكد من أن الرابط يعمل، أو جرب تحديث ملف الكوكيز.", chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode='Markdown')

# ==========================================
# 4. تشغيل البوت
# ==========================================
if __name__ == "__main__":
    # إنشاء مجلد التحميلات إذا لم يكن موجوداً
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    print(f"--- البوت يعمل الآن تحت إشراف {DEV_NAME} ---")
    bot.infinity_polling()
