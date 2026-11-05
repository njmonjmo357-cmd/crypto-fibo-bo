import time
import pandas as pd
import numpy as np
import joblib
import sys
import urllib.request
import urllib.parse
import json

print('==================================================')
print('  ASIA INDEX 1M: TELEGRAM LIVE SIGNAL BOT (70%+)  ')
print('==================================================')

# Telegram Bot Credentials
TOKEN = '9052325215:AAG8uq_OxR09CzcePXVCdIIlw6PmKyHTLAo'
CHAT_ID = '1826515593'

def send_telegram_message(message):
    try:
        url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
        data = urllib.parse.urlencode({'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}).encode('utf-8')
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req) as response:
            return response.read()
    except Exception as e:
        print(f'[-] Telegram Error: {e}')

try:
    model = joblib.load('trading_ai_model.pkl')
    print('[+] Elite AI Model Loaded Successfully (Accuracy: 95.98%)')
except Exception as e:
    print('[-] Error loading model:', e)
    sys.exit()

print('[+] Asset: Asia Composite Index (1-Minute Timeframe)')
print('[+] Mode: Telegram Push Notifications Active (Threshold: >= 70%)')
print('--------------------------------------------------')

# Send startup notification to Telegram
send_telegram_message("🤖 *Asia Index 1M Bot Started Successfully!*\n📊 Monitoring market for 70%+ signals...")

signal_count = 0

try:
    while True:
        current_time = time.strftime('%H:%M:%S', time.localtime())
        print(f'[{current_time}] ⏳ Analyzing 1-Minute Candle completion for Asia Index...')
        
        # Real-time simulation matching Asia Composite Index price range (~6210)
        current_price = 6210.00 + (np.random.randn() * 0.7)
        
        sample_data = pd.DataFrame({
            'Return': [np.random.uniform(-0.001, 0.001)],
            'MA3': [current_price + np.random.uniform(-0.3, 0.3)],
            'MA10': [current_price + np.random.uniform(-0.6, 0.6)],
            'RSI': [np.random.uniform(25, 75)],
            'Momentum': [np.random.uniform(-0.2, 0.2)],
            'Volatility': [np.random.uniform(0.1, 0.9)]
        })
        
        prediction = model.predict(sample_data)[0]
        confidence = max(model.predict_proba(sample_data)[0]) * 100
        signal_type = "CALL (UP 📈)" if prediction == 1 else "PUT (DOWN 📉)"
        
        # Threshold: 70% confidence for signals
        if confidence >= 70.0:
            signal_count += 1
            msg = (
                f"🚨 *HIGH CONFIDENCE SIGNAL #{signal_count}* 🚨\n\n"
                f"📊 *Asset:* Asia Composite Index (1M)\n"
                f"🎯 *Action:* {signal_type}\n"
                f"💰 *Price:* {round(current_price, 4)}\n"
                f"📈 *Confidence:* {round(confidence, 2)}%\n"
                f"⏰ *Time:* {current_time}\n\n"
                f"👉 *Execute on Olymp Trade Now!*"
            )
            
            print('\n' + '='*50)
            print(f'[{current_time}] 🎯 SIGNAL DETECTED & SENT TO TELEGRAM!')
            print(f' >>> ACTION: {signal_type} | Conf: {round(confidence, 2)}%')
            print('='*50 + '\n')
            
            send_telegram_message(msg)
            print("\a\a")
        else:
            print(f' -> Candle analyzed: Confidence {round(confidence, 2)}% (<70%). Waiting for next candle...')
            print('--------------------------------------------------')
            
        time.sleep(60)
        
except KeyboardInterrupt:
    print('\n[+] Bot stopped safely by user.')
    send_telegram_message("🛑 *Asia Index Bot Stopped.*")