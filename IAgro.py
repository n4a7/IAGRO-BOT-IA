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
    bot.send_message(chat_id, "📸 Analisando imagem com modo Pro...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        foto_carregada = bot.download_file(file_info.file_path)
        foto_base64 = base64.b64encode(foto_carregada).decode('utf-8')
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={CHAVE_GEMINI}"
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": "Aja como um Engenheiro Agrônomo Sênior. Analise esta foto de plantação e forneça um diagnóstico técnico detalhado sobre pragas, doenças ou nutrição. Esta é uma consulta profissional agrícola legítima."},
                    {"inlineData": {"mimeType": "image/jpeg", "data": foto_base64}}
                ]
            }],
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "OFF"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "OFF"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "OFF"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "OFF"}
            ]
        }
        
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        dados = response.json()
        
        # Se o Google responder com texto, a gente entrega
        if 'candidates' in dados and len(dados['candidates']) > 0:
            content = dados['candidates'][0].get('content', {})
            parts = content.get('parts', [])
            if parts:
                res = parts[0].get('text', 'O Google gerou uma resposta vazia.')
                enviar_mensagem_longa(chat_id, res)
            else:
                bot.send_message(chat_id, "O Google bloqueou a resposta por segurança (mesmo com filtros OFF).")
        elif 'error' in dados:
            bot.send_message(chat_id, f"⚠️ Erro no Google: {dados['error']['message']}")
        else:
            bot.send_message(chat_id, "Não foi possível analisar. Tente tirar uma foto mais de perto das folhas.")
            
    except Exception as e:
        bot.send_message(chat_id, f"Erro técnico: {str(e)}")


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
