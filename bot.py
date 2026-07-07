import os
import threading
import telebot
import requests
import re
from flask import Flask

# 1. Render Dummy Web Server
app = Flask('')

@app.route('/')
def home():
    return "Bhai, aapka bot bilkul zinda hai!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. Telegram Bot Setup
BOT_TOKEN = "8948341231:AAFGtG-axrVYZbp13E4-aJ4ka8FXRbTleDs"  # <--- Apna Token yahaan daalein
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
    processing_msg = bot.reply_to(message, "⏳ New API se link bypass ho raha hai... Please wait...")
    
    try:
        # Naya Free Bypasser API URL
        api_url = f"https://api.bypass.lat/bypass?url={url}"
        response = requests.get(api_url, timeout=15)
        data = response.json()
        
        # Sahi key se data nikaal rahe hain
        final_link = data.get("destination") or data.get("url") or data.get("link") or data.get("bypassed_url")
        
        if final_link:
            response_text = f"🎯 **Aapka Direct Link Mil Gaya:**\n\n🔗 {final_link}"
            bot.edit_message_text(response_text, chat_id=processing_msg.chat.id, message_id=processing_msg.message_id, disable_web_page_preview=False)
        else:
            error_msg = f"⚠️ Naye API ne bhi direct link nahi diya।\n\n**Raw Response:** `{str(data)}`"
            bot.edit_message_text(error_msg, chat_id=processing_msg.chat.id, message_id=processing_msg.message_id, parse_mode="Markdown")
            
    except Exception as e:
        bot.edit_message_text(f"❌ Error: Link process karne mein dikkat aayi। Details: {str(e)}", chat_id=processing_msg.chat.id, message_id=processing_msg.message_id)

# 3. Main Function
if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.start()
    bot.polling(none_stop=True)
