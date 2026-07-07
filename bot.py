import os
import threading
import telebot
import requests
import re
from flask import Flask

# 1. Render ke liye ek dummy Web Server banana
app = Flask('')

@app.route('/')
def home():
    return "Bhai, aapka bot bilkul zinda hai!"

def run_flask():
    # Render khud PORT environment variable deta hai
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. Telegram Bot Setup
BOT_TOKEN = "8948341231:AAFGtG-axrVYZbp13E4-aJ4ka8FXRbTleDs"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome Bhai! Mujhe koi bhi shortener link (jaise InstantLinks) bhejo, main uska direct link nikaal dunga।")

@bot.message_handler(func=lambda message: True)
def handle_bypass(message):
    text = message.text.strip()
    urls = re.findall(r'(https?://[^\s]+)', text)
    
    if not urls:
        bot.reply_to(message, "❌ Please ek sahi link bhejo bhai।")
        return
        
    url = urls[0]
    processing_msg = bot.reply_to(message, "⏳ Link bypass ho raha hai... Please wait...")
    
    try:
        api_url = f"https://api.bypass.vip/bypass?url={url}"
        response = requests.get(api_url, timeout=15)
        data = response.json()
        
        if data.get("status") == "success" or "destination" in data:
            final_link = data.get("destination")
            response_text = f"🎯 **Aapka Direct Link Mil Gaya:**\n\n🔗 {final_link}"
            bot.edit_message_text(response_text, chat_id=processing_msg.chat.id, message_id=processing_msg.message_id, disable_web_page_preview=False)
        else:
            bot.edit_message_text("⚠️ Yeh link abhi bypass nahi ho pa rha hai।", chat_id=processing_msg.chat.id, message_id=processing_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text("❌ Error: Link process karne mein dikkat aayi।", chat_id=processing_msg.chat.id, message_id=processing_msg.message_id)

# 3. Dono (Flask + Bot) ko ek sath chalane ka main function
if __name__ == "__main__":
    # Flask server ko background thread mein chalu karein
    t = threading.Thread(target=run_flask)
    t.start()
    
    # Main thread mein Telegram bot ko chalne dein
    bot.polling(none_stop=True)
                    
