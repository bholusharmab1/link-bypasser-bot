import os
import threading
import telebot
import requests
import re
from flask import Flask
import time

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
    bot.reply_to(message, "👋 Welcome Bhai! Mujhe koi bhi shortener link bhejo.")

@bot.message_handler(func=lambda message: True)
def handle_bypass(message):
    text = message.text.strip()
    urls = re.findall(r'(https?://[^\s]+)', text)
    
    if not urls:
        bot.reply_to(message, "❌ Please ek sahi link bhejo bhai.")
        return
        
    url = urls[0]
    processing_msg = bot.reply_to(message, "⏳ Multi-API System se bypass try kar raha hoon... Please wait...")
    
    # 3 alag-alag Free Bypasser APIs ka list
    api_list = [
        f"https://api.bypass.city/bypass?url={url}",
        f"https://api.bypass.lat/bypass?url={url}",
        f"https://api.bypass.vip/bypass?url={url}"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    final_link = None
    error_log = ""
    
    # Bot ek-ek karke saari API try karega
    for api_url in api_list:
        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Link nikaalne ki koshish
                final_link = data.get("destination") or data.get("url") or data.get("link") or data.get("bypassed_url")
                
                if final_link:
                    break # Agar link mil gaya, toh loop band karo aur aage badho
            else:
                error_log += f"[{response.status_code}] "
                
        except Exception as e:
            error_log += "[Timeout] "
            continue

    # Result bhejna
    if final_link:
        bot.edit_message_text(f"🎯 **Aapka Direct Link Mil Gaya:**\n\n🔗 {final_link}", chat_id=processing_msg.chat.id, message_id=processing_msg.message_id, disable_web_page_preview=False)
    else:
        bot.edit_message_text(f"❌ Saari APIs ne Render ka IP block kar diya hai ya down hain.\n\n*Security Errors:* {error_log}\n\n⚠️ **Note:** Agar ye lagatar hota hai, toh free APIs server IPs (Render) par kaam nahi karengi. Isko apne PC/Mobile par directly run karna padega.", chat_id=processing_msg.chat.id, message_id=processing_msg.message_id)

# 3. Main Function
if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.start()
    
    print("Bot is starting...")
    while True:
        try:
            bot.delete_webhook(drop_pending_updates=True)
            bot.polling(none_stop=True)
        except Exception as e:
            # Agar Telegram 409 Error de, toh bot marega nahi, 5 second baad fir koshish karega
            print(f"Error occurred: {e}. Retrying in 5 seconds...")
            time.sleep(5)
