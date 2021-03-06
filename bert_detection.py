import random
import tensorflow as tf
from tensorflow import keras
from bert import BertModelLayer
from bert.tokenization.bert_tokenization import FullTokenizer
import numpy as np
import json
import database_updates
from datetime import datetime
import tzlocal
import requests
import urllib.request
import slot_detection
from bson import ObjectId

model = keras.models.load_model("bert_intent_detection.hdf5",custom_objects={"BertModelLayer": BertModelLayer},compile=False)

tokenizer = FullTokenizer(vocab_file="vocab.txt")
classes = ['greetings', 'hiring_request', 'goodbye', 'interview_schedule', 'schedule_list']
print(classes)

with open('intents.json') as file:
    data = json.load(file)

def chat(inp):
    print(inp)
    user_text = inp.message.text.encode('utf-8').decode()
    sentences=[user_text]
    pred_tokens = map(tokenizer.tokenize, sentences)
    pred_tokens = map(lambda tok: ["[CLS]"] + tok + ["[SEP]"], pred_tokens)
    pred_token_ids = list(map(tokenizer.convert_tokens_to_ids, pred_tokens))

    pred_token_ids = map(lambda tids: tids +[0]*(21-len(tids)),pred_token_ids)
    pred_token_ids = np.array(list(pred_token_ids))
    predictions = model.predict(pred_token_ids)
    predictions_index=predictions.argmax(axis=-1)
    final_intent=''
    #if (predictions[predictions_index] < 0.9):
    #    final_intent = "unknown"
    #    response = "Sorry, I did not understand what you meant there."
    #    return response, final_intent

    for text, label in zip(sentences, predictions_index):
        confidence = predictions[0][label]
        if (confidence < 0.9):
            final_intent = "unknown"
            response = "Sorry, I did not understand what you meant there."
            return response, final_intent

        final_intent=classes[label]
        print("text:", text, "\nintent:", classes[label])
        print()
    
        response = getCorrectResponse(inp, final_intent)
    
    return response,final_intent


def getCorrectResponse(inp, final_intent):
    unix_timestamp = inp.message.date.timestamp()
    local_timezone = tzlocal.get_localzone()
    local_time = datetime.fromtimestamp(unix_timestamp, local_timezone)
    date_of_msg = local_time.strftime("%B %d %Y")

    first_name = inp.message.chat.first_name
    chat_id = inp.message.chat.id
    user_text = inp.message.text.encode('utf-8').decode()
  
    
    for tg in data["intents"]:
        if tg['tag'] == final_intent:
            if final_intent == 'greetings':
                if (database_updates.get_record_by_chat_id_and_date(date_of_msg,chat_id)):
                    responses = random.choice(tg['secondary_responses']).format(first_name)
                else:
                    responses = random.choice(tg['primary_responses'])
            
            elif final_intent == 'interview_schedule':
                if (database_updates.get_prev_intent(chat_id) == 'hiring_request'):
                    interview_datetime = slot_detection.schedule_slot_detection(user_text)
                    ### prefferably give ObjectId
                    candidate_id = ObjectId('601cca2524132720897f5c91')
                    if database_updates.schedule_interview(candidate_id,interview_datetime,chat_id):
                        responses = random.choice(tg['responses'])
                    else:
                        responses = "Sorry Couldn't process the request." ## can be added to secodary resp
                else:
                     responses = "Sorry please upload JD and then invoke this intent" ## can be tertiary response
            
            else:
                responses = random.choice(tg['responses'])

    database_updates.insert_chatbot_user_data(date_of_msg,first_name,chat_id,final_intent)
    return responses

def process_file(file_id,chat_id):
    url = 'https://api.telegram.org/bot1621891888:AAHBvpvmFNJDQoDlpB3ImaBwdQHOGn5d0Pg/getFile?file_id='+file_id
    r = requests.get(url)
    data = r.json()
    file_path = data['result']['file_path']
    download_url = "https://api.telegram.org/file/bot1621891888:AAHBvpvmFNJDQoDlpB3ImaBwdQHOGn5d0Pg/"+file_path
    response = urllib.request.urlopen(download_url)    
    file = open(str(chat_id) + ".pdf", 'wb')
    file.write(response.read())
    file.close()
