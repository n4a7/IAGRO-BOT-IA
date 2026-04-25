import telebot
import requests
import base64
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "JVN IAGRO PRO ONLINE"

def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURAÇÕES ---
TOKEN_TELEGRAM = "8786694886:AAEnDlyo4Hj7il5xu-y_NCZPHbo5-Hn6A2U"
CHAVE_GEMINI = "AIzaSyCQvNspR5K7rNXU-UfUD7iD5lRsnaA50Ro"
bot = telebot.TeleBot(TOKEN_TELEGRAM)

# URL DEFINITIVA (v1beta é a chave do sucesso aqui)
URL_API = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-001:generateContent?key={CHAVE_GEMINI}"
def enviar_mensagem_longa(chat_id, texto):
    if not texto: return
    for i in range(0, len(texto), 4000):
        bot.send_message(chat_id, texto[i:i+4000])

@bot.message_handler(commands=['start'])
def boas_vindas(message):
    bot.reply_to(message, "🚀 JVN IAGRO PRO Ativado! Mande sua foto ou dúvida agronômica.")

@bot.message_handler(content_types=['photo'])
def analisar_foto(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "📸 Analisando lavoura no Modo Pro...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        foto_carregada = bot.download_file(file_info.file_path)
        foto_base64 = base64.b64encode(foto_carregada).decode('utf-8')
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": "Aja como um Engenheiro Agrônomo Sênior. Analise esta foto de plantação e forneça um diagnóstico técnico detalhado sobre pragas, doenças ou nutrição."},
                    {"inline_data": {"mime_type": "image/jpeg", "data": foto_base64}}
                ]
            }]
        }
        
        response = requests.post(URL_API, json=payload)
        dados = response.json()
        
        if 'candidates' in dados:
            res = dados['candidates'][0]['content']['parts'][0]['text']
            enviar_mensagem_longa(chat_id, res)
        elif 'error' in dados:
            bot.send_message(chat_id, f"⚠️ Erro no Google: {dados['error']['message']}")
        else:
            bot.send_message(chat_id, "O Google não conseguiu processar essa imagem agora.")
            
    except Exception as e:
        bot.send_message(chat_id, f"Erro interno: {str(e)}")

@bot.message_handler(func=lambda m: True)
def responder_texto(message):
    try:
        payload = {"contents": [{"parts": [{"text": f"Responda como consultor agrícola: {message.text}"}]}]}
        response = requests.post(URL_API, json=payload)
        res = response.json()['candidates'][0]['content']['parts'][0]['text']
        enviar_mensagem_longa(message.chat.id, res)
    except:
        bot.reply_to(message, "Estou processando muita informação, tente novamente em instantes.")

if __name__ == "__main__":
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    bot.infinity_polling(timeout=20, skip_pending=True)
