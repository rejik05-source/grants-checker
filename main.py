import json
import os
import time
import requests
from bs4 import BeautifulSoup
from google import genai

# התחברות ל-Gemini
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# הגדרות פרטי טלגרם
telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

def send_telegram_msg(text):
    if telegram_token and telegram_chat_id:
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        payload = {"chat_id": telegram_chat_id, "text": text, "parse_mode": "HTML"}
        try:
            res = requests.post(url, json=payload, timeout=10)
            print(f"Telegram API Status: {res.status_code}")
            if res.status_code != 200:
                print(f"Telegram Response Error: {res.text}")
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")
    else:
        print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in GitHub Secrets!")

# הודעת בדיקה מידית לטלגרם
send_telegram_msg("🚀 בדיקה: הסורק האוטומטי מחובר ועובד בהצלחה!")

with open('federations.json', 'r', encoding='utf-8') as f:
    federations = json.load(f)

for fed in federations:
    print(f"Checking: {fed['name']}...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(fed['url'], headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text(separator=' ', strip=True)[:8000]

        prompt = f"""
        אתה עוזר למחקר מענקים. מצורף טקסט מעמוד אינטרנט של הפדרציה: "{fed['name']}".
        סרוק את הטקסט ותגיד לי אם יש כרגע קולות קוראים (Grants / RFPs) פתוחים להגשה.
        
        אם מצאת קול קורא פתוח, החזר תשובה בפורמט:
        - שם המענק: [שם המענק]
        - תאריך אחרון להגשה: [תאריך או "לא מצוין"]
        - תיאור קצר: [משפט אחד]
        
        אם אין קולות קוראים פתוחים, תכתוב רק: "אין קולות קוראים פתוחים".
        
        הטקסט מהאתר:
        {page_text}
        """

        res = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        if "אין קולות קוראים פתוחים" not in res.text:
            msg = f"<b>{fed['name']}</b>:\n{res.text}\nURL: {fed['url']}"
            send_telegram_msg(msg)

    except Exception as e:
        print(f"Error {fed['name']}: {e}")

    # השהיה של 12 שניות למניעת חריגת קצב בגרסה החינמית
    time.sleep(12)

print("Done scanning!")
