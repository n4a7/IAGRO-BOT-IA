import telebot
import requests
import base64

TOKEN_TELEGRAM = "8786694886:AAEnDlyo4Hj7il5xu-y_NCZPHbo5-Hn6A2U"
CHAVE_GEMINI = "AIzaSyCQvNspR5K7rNXU-UfUD7iD5lRsnaA50Ro"

bot = telebot.TeleBot(TOKEN_TELEGRAM)

print("🚀 JVN AGROSYSTEM: Motor 2.5 ATIVADO e Fatiador de Textos ligado!")

# --- FUNÇÃO ANTI-TRAVAMENTO DO TELEGRAM ---
def enviar_mensagem_longa(chat_id, texto, reply_to=None):
    # Corta o texto em blocos de 4000 caracteres para ter uma margem de segurança
    for i in range(0, len(texto), 4000):
        parte_texto = texto[i:i+4000]
        if reply_to:
            bot.reply_to(reply_to, parte_texto)
        else:
            bot.send_message(chat_id, parte_texto)

@bot.message_handler(commands=['start'])
def boas_vindas(message):
    texto = "Opaa! O sistema JVN AGROSYSTEM está ativo.\n\nMande sua dúvida ou uma foto da lavoura para eu analisar."
    bot.reply_to(message, texto)

@bot.message_handler(content_types=['photo'])
def analisar_foto(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "📸 Imagem recebida. Elaborando o laudo agronômico...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        foto_carregada = bot.download_file(file_info.file_path)
        foto_base64 = base64.b64encode(foto_carregada).decode('utf-8')
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={CHAVE_GEMINI}"
        
        prompt = "Aja como um Engenheiro Agrônomo Sênior do JVN AGROSYSTEM. Analise esta foto e identifique possíveis doenças, pragas ou deficiências. Dê um diagnóstico e uma recomendação prática e direta."
        
        payload = {"contents": [{"parts": [{"text": prompt}, {"inlineData": {"mimeType": "image/jpeg", "data": foto_base64}}]}]}
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        dados = response.json()
        
        if 'error' in dados:
            bot.send_message(chat_id, f"⚠️ Erro no Google: {dados['error']['message']}")
            return
            
        resposta_texto = dados['candidates'][0]['content']['parts'][0]['text']
        
        # Envia usando a nossa nova função que fatia o texto
        enviar_mensagem_longa(chat_id, resposta_texto)
        
    except Exception as e:
        bot.send_message(chat_id, f"Erro interno: {str(e)}")

@bot.message_handler(func=lambda m: True)
def responder_texto(message):
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, 'typing')
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={CHAVE_GEMINI}"
        
        payload = {"contents": [{"parts": [{"text": f"Você é o assistente do JVN AGROSYSTEM. Responda ao produtor de forma técnica, direta e prática: {message.text}"}]}]}
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        dados = response.json()
        
        if 'error' in dados:
            bot.reply_to(message, f"⚠️ Erro no Google: {dados['error']['message']}")
            return
            
        resposta_texto = dados['candidates'][0]['content']['parts'][0]['text']
        
        # Envia usando a nossa nova função que fatia o texto
        enviar_mensagem_longa(chat_id, resposta_texto, reply_to=message)
        
    except Exception as e:
        bot.reply_to(message, f"Erro interno: {str(e)}")

bot.infinity_polling()
