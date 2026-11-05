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

send_telegram("🤖 *تم تشغيل بوت مؤشر آسيا (1M) بنجاح مع تتبع النتائج!*\n📊 جاري مراقبة السوق وإرسال النتيجة بعد كل إشارة...")

while True:
    try:
        url = "https://api.olymptrade.com/v1/quotes/history?pair=ASIA_INDEX&tf=60&limit=50"
        res = requests.get(url, timeout=10).json()
        df = pd.DataFrame(res['data'])
        
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
            entry_price = latest_data['close']
            action = "صعود (CALL 📈)" if prediction == 1 else "هبوط (PUT 📉)"
            is_call = (prediction == 1)
            
            msg = (
                f"🚨 *إشارة تداول عالية الثقة* 🚨\n\n"
                f"📊 *الأصل:* مؤشر آسيا المركب (1M)\n"
                f"🎯 *القرار:* {action}\n"
                f"💰 *سعر الدخول:* {entry_price}\n"
                f"📈 *نسبة التأكيد:* {confidence*100:.2f}%\n"
                f"⏰ *الوقت:* {time.strftime('%H:%M:%S')}\n\n"
                f"👉 *سيتم متابعة النتيجة بعد دقيقة واحدة...*"
            )
            send_telegram(msg)
            
            # الانتظار لمدة دقيقة واحدة لفحص نتيجة الشمعة التالية
            time.sleep(60)
            
            # جلب السعر الجديد بعد دقيقة لمعرفة النتيجة
            res_after = requests.get(url, timeout=10).json()
            df_after = pd.DataFrame(res_after['data'])
            exit_price = df_after.iloc[-1]['close']
            
            # تحديد الربح أو الخسارة
            if is_call:
                won = exit_price > entry_price
            else:
                won = exit_price < entry_price
                
            if won:
                result_msg = f"✅ *نتيجة الصفقة: ربح (WIN 🟢)*\n💰 سعر الدخول: {entry_price}\n🎯 سعر الخروج: {exit_price}"
            else:
                result_msg = f"❌ *نتيجة الصفقة: خسارة (LOSS 🔴)*\n💰 سعر الدخول: {entry_price}\n🎯 سعر الخروج: {exit_price}"
                
            send_telegram(result_msg)
        else:
            time.sleep(10)
            
    except Exception as e:
        print(f"Loop error: {e}")
        time.sleep(10)
