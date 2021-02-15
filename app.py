from flask import Flask, request
import telegram
from pymongo import MongoClient
import bert_detection
import database_updates

app = Flask(__name__)

bot_token = "1537657914:AAEspo0IA7tiW2CCAnWLfsxOd0YabGC-r50"
bot_username = "VirtualRecruiterBot"
bot_url = "https://b9e5a020b8d7.ngrok.io/" #change this URL to your ngrok url
#https://c53f5f38a8d6.ngrok.io/set_webhook
bot = telegram.Bot(token=bot_token)

@app.route("/{}".format(bot_token), methods = ['POST'])
def process_input_message():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id
    first_name = update.message.chat.first_name
    print(update)
    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode('utf-8').decode()
    # for debugging purposes only
    print("got text message :", text)

    if(text=="/start"):
        welcome_msg = "Welcome!"
        bot.sendMessage(chat_id=chat_id, text=welcome_msg, reply_to_message_id=msg_id)
    else:
        response,intent = bert_detection.chat(update)
        print(response)
        bot.sendMessage(chat_id=chat_id, text=response, reply_to_message_id=msg_id)
    
    return 'ok'
    
@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    print("Inside setting webhook")
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=bot_url, HOOK=bot_token))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

@app.route('/delete_webhook', methods=['GET'])
def delete_webhook():
    print("Inside deleting webhook")
    s = bot.delete_webhook(drop_pending_updates=True)
    if s:
        return "webhook deleted"
    else:
        return "webhook delete failed"

@app.route('/runMongo', methods=['GET'])
def run_mongo():
    print("YOOOOOO")
    try:
        myclient =  MongoClient("mongodb+srv://user:user@cluster0.oklqw.mongodb.net/test")
        mydb = myclient["plp_project"]
        mycol = mydb["resume_details"]
        print(mycol.find_one())
    except Exception as e:
        print(e) 

if __name__ == "__main__":
    app.run(threaded=True)