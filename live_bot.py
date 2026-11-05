import time
import requests
import joblib
import pandas as pd
import numpy as np

TOKEN = "9052325215"
CHAT_ID = "1826515593"
MODEL_PATH = "trading_ai_model.pkl"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending message: {e}")

model = joblib.load(MODEL_PATH)

send_telegram("🤖 *تم تشغيل بوت مؤشر آسيا (1M) بنجاح!*\n📊 جاري مراقبة السوق لإشارات بقدرة 70%+...")

while True:
    try:
        url = "https://api.olymptrade.com/v1/quotes/history?pair=ASIA_INDEX&tf=60&limit=50"
        res = requests.get(url, timeout=10).json()
        df = pd.DataFrame(res['data'])
        
        # Calculate features (matching model training)
        df['returns'] = df['close'].pct_change()
        df['sma_5'] = df['close'].rolling(5).mean()
        df['sma_20'] = df['close'].rolling(20).mean()
        df['rsi'] = 100 - (100 / (1 + (df['returns'].gt(0).rolling(14).sum() / df['returns'].lt(0).abs().rolling(14).sum())))
        
        latest_data = df.iloc[-1]
        features = [[latest_data['returns'], latest_data['sma_5'], latest_data['sma_20'], latest_data['rsi']]]
        
        probs = model.predict_proba(features)[0]
        confidence = max(probs)
        prediction = model.predict(features)[0]
        
        if confidence >= 0.70:
            action = "صعود (CALL 📈)" if prediction == 1 else "هبوط (PUT 📉)"
            msg = (
                f"🚨 *إشارة تداول عالية الثقة* 🚨\n\n"
                f"📊 *الأصل:* مؤشر آسيا المركب (1M)\n"
                f"🎯 *القرار:* {action}\n"
                f"💰 *السعر الحالي:* {latest_data['close']}\n"
                f"📈 *نسبة التأكيد:* {confidence*100:.2f}%\n"
                f"⏰ *الحديث:* {time.strftime('%H:%M:%S')}\n\n"
                f"👉 *نفذ الصفقة على أوليمب تريد الآن!*"
            )
            send_telegram(msg)
            time.sleep(60)
        else:
            time.sleep(10)
            
    except Exception as e:
        print(f"Loop error: {e}")
        time.sleep(10)
