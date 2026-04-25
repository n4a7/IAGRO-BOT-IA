import telebot
import requests
import base64
import os
from flask import Flask
from threading import Thread

# --- CONFIGURAÇÃO DO SERVIDOR WEB (Para o Render não derrubar) ---
app = Flask('')

@app.route('/')
def home():
    return "JVN IAGRO PRO ONLINE"

def run_web():
    # O Render usa a porta 10000 por padrão, ou a que estiver na variável PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURAÇÕES DO BOT ---
TOKEN_TELEGRAM = "8786694886:AAEnDlyo4Hj7il5xu-y_NCZPHbo5-Hn6A2U"
CHAVE_GEMINI = "AIzaSyCQvNspR5K7rNXU-UfUD7iD5lRsnaA50Ro"

bot = telebot.TeleBot(TOKEN_TELEGRAM)

# URL UNIVERSAL (v1beta + gemini-1.5-flash)
URL_API = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={CHAVE_GEMINI}"

def enviar_mensagem_longa(chat_id, texto):
    if not texto: return
    for i in range(0, len(texto), 4000):
        bot.send_message(chat_id, texto[i:i+4000])

@bot.message_handler(commands=['start'])
def boas_vindas(message):
    bot.reply_to(message, "🚀 JVN IAGRO PRO Online!\nO sistema está rodando na nuvem. Mande uma foto da lavoura ou sua dúvida técnica.")

@bot.message_handler(content_types=['photo'])
def analisar_foto(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "📸 Imagem recebida. Consultando inteligência agronômica...")
    try:
        # Baixa a foto do Telegram
        file_info = bot.get_file(message.photo[-1].file_id)
        foto_carregada = bot.download_file(file_info.file_path)
        foto_base64 = base64.b64encode(foto_carregada).decode('utf-8')
        
        # Monta o pedido para o Google
        payload = {
            "contents": [{
                "parts": [
                    {"text": "Aja como um Engenheiro Agrônomo Sênior. Analise esta foto de plantação e forneça um diagnóstico técnico sobre pragas, doenças ou nutrição. Seja prático."},
                    {"inline_data": {"mime_type": "image/jpeg", "data": foto_base64}}
                ]
            }],
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        }
        
        response = requests.post(URL_API, json=payload)
        dados = response.json()
        
        if 'candidates' in dados and len(dados['candidates']) > 0:
            res = dados['candidates'][0]['content']['parts'][0]['text']
            enviar_mensagem_longa(chat_id, res)
        elif 'error' in dados:
            bot.send_message(chat_id, f"⚠️ Erro no Google: {dados['error']['message']}")
        else:
            bot.send_message(chat_id, "🔍 O Google não conseguiu analisar esta imagem específica. Tente uma foto mais próxima das folhas.")
            
    except Exception as e:
        bot.send_message(chat_id, f"Erro técnico: {str(e)}")

@bot.message_handler(func=lambda m: True)
def responder_texto(message):
    try:
        payload = {
            "contents": [{"parts": [{"text": f"Responda como assistente técnico agrícola: {message.text}"}]}]
        }
        response = requests.post(URL_API, json=payload)
        dados = response.json()
        res = dados['candidates'][0]['content']['parts'][0]['text']
        enviar_mensagem_longa(message.chat.id, res)
    except Exception as e:
        print(f"Erro no texto: {e}")

if __name__ == "__main__":
    # Inicia o servidor web em uma thread separada
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    
    print("🚀 Bot JVN IAGRO PRO iniciado com sucesso!")
    # Inicia o monitoramento de mensagens do Telegram
    bot.infinity_polling(timeout=20, skip_pending=True)
