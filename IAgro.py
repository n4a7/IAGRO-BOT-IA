import telebot
import requests
import base64
import os
from flask import Flask
from threading import Thread

# --- CONFIGURAÇÃO DO SERVIDOR FANTASMA (Para o Render não derrubar) ---
app = Flask('')

@app.route('/')
def home():
    return "JVN AGROSYSTEM ONLINE"

def run_web():
    # O Render fornece a porta automaticamente na variável PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURAÇÕES DO BOT ---
TOKEN_TELEGRAM = "8786694886:AAEnDlyo4Hj7il5xu-y_NCZPHbo5-Hn6A2U"
CHAVE_GEMINI = "AIzaSyCQvNspR5K7rNXU-UfUD7iD5lRsnaA50Ro"

bot = telebot.TeleBot(TOKEN_TELEGRAM)

def enviar_mensagem_longa(chat_id, texto, reply_to=None):
    for i in range(0, len(texto), 4000):
        parte_texto = texto[i:i+4000]
        if reply_to: bot.reply_to(reply_to, parte_texto)
        else: bot.send_message(chat_id, parte_texto)

@bot.message_handler(commands=['start'])
def boas_vindas(message):
    bot.reply_to(message, "Olá, João Vitor! JVN AGROSYSTEM operacional na nuvem.")

@bot.message_handler(content_types=['photo'])
def analisar_foto(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "📸 Analisando imagem...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        foto_carregada = bot.download_file(file_info.file_path)
        foto_base64 = base64.b64encode(foto_carregada).decode('utf-8')
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={CHAVE_GEMINI}"
        payload = {"contents": [{"parts": [{"text": "Aja como Agrônomo Sênior. Analise a foto e dê diagnóstico técnico."}, {"inlineData": {"mimeType": "image/jpeg", "data": foto_base64}}]}]}
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        resposta_texto = response.json()['candidates'][0]['content']['parts'][0]['text']
        enviar_mensagem_longa(chat_id, resposta_texto)
    except Exception as e:
        bot.send_message(chat_id, f"Erro: {str(e)}")

@bot.message_handler(func=lambda m: True)
def responder_texto(message):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={CHAVE_GEMINI}"
        payload = {"contents": [{"parts": [{"text": f"IA JVN AGROSYSTEM responda: {message.text}"}]}]}
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        resposta_texto = response.json()['candidates'][0]['content']['parts'][0]['text']
        enviar_mensagem_longa(message.chat.id, resposta_texto, reply_to=message)
    except: pass

# --- PARTE CRUCIAL: RODAR AMBOS JUNTOS ---
if __name__ == "__main__":
    # Inicia o servidor web em uma linha separada (thread)
    t = Thread(target=run_web)
    t.start()
    # Inicia o bot do Telegram
    print("🚀 Bot JVN AGROSYSTEM rodando como Web Service!")
    bot.infinity_polling()
