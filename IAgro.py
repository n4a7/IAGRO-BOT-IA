import telebot
import requests
import base64
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "JVN AGROSYSTEM ONLINE"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

TOKEN_TELEGRAM = "8786694886:AAEnDlyo4Hj7il5xu-y_NCZPHbo5-Hn6A2U"
CHAVE_GEMINI = "AIzaSyCQvNspR5K7rNXU-UfUD7iD5lRsnaA50Ro"
bot = telebot.TeleBot(TOKEN_TELEGRAM)

def enviar_mensagem_longa(chat_id, texto, reply_to=None):
    for i in range(0, len(texto), 4000):
        parte = texto[i:i+4000]
        if reply_to: bot.reply_to(reply_to, parte)
        else: bot.send_message(chat_id, parte)

@bot.message_handler(commands=['start'])
def boas_vindas(message):
    bot.reply_to(message, "Opaa! JVN AGROSYSTEM PRO ONLINE!.")

@bot.message_handler(content_types=['photo'])
def analisar_foto(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "📸 Analisando lavoura no Modo Pro...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        foto_carregada = bot.download_file(file_info.file_path)
        foto_base64 = base64.b64encode(foto_carregada).decode('utf-8')
        
        # AJUSTE AQUI: Versão 'v1' e modelo 'gemini-1.5-flash' puro
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={CHAVE_GEMINI}"
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": "Você é o Engenheiro Agrônomo Sênior do JVN AGRO SYSTEM. Analise esta imagem técnica e forneça um diagnóstico detalhado."},
                    {"inlineData": {"mimeType": "image/jpeg", "data": foto_base64}}
                ]
            }],
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        }
        
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        dados = response.json()
        
        if 'candidates' in dados and len(dados['candidates']) > 0:
            res = dados['candidates'][0]['content']['parts'][0]['text']
            enviar_mensagem_longa(chat_id, res)
        elif 'error' in dados:
            bot.send_message(chat_id, f"⚠️ Erro no Google: {dados['error']['message']}")
        else:
            bot.send_message(chat_id, "🔍 O Google não retornou uma resposta. Tente uma foto mais de perto da planta.")
            
    except Exception as e:
        bot.send_message(chat_id, f"Erro: {str(e)}")

@bot.message_handler(func=lambda m: True)
def responder_texto(message):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={CHAVE_GEMINI}"
        payload = {"contents": [{"parts": [{"text": message.text}]}]}
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        res = response.json()['candidates'][0]['content']['parts'][0]['text']
        enviar_mensagem_longa(message.chat.id, res, reply_to=message)
    except: pass

if __name__ == "__main__":
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    print("🚀 Bot Online!")
    bot.infinity_polling(timeout=20, skip_pending=True)
