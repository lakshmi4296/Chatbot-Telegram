from pymongo import MongoClient
from datetime import datetime

myclient =  MongoClient("mongodb+srv://user:user@cluster0.oklqw.mongodb.net/test")
mydb = myclient["plp_project"]

def insert_chatbot_user_data(date_of_msg,name,chat_id,status):
    schema = mydb["chatbot_user_details"]
    data = {"date":date_of_msg, "chat_id": chat_id, "name": name, "status":status}
    myquery = {"chat_id": chat_id}
    existing_user = list(schema.find(myquery))
    print(existing_user)
    if (len(existing_user) == 0):
        schema.insert_one(data)
    else:
        updated_values = {"$set": data}
        schema.update_one(myquery,updated_values)

def get_record_by_chat_id_and_date(date_of_msg,chat_id):
    schema = mydb["chatbot_user_details"]
    myquery = {"chat_id": chat_id}
    existing_user = list(schema.find(myquery))
    print(len(existing_user))
    if (len(existing_user) == 0):
        return False
    else:
        last_convo_date = existing_user[0]['date']
        print("Database date = " + last_convo_date)
        print("Message date = " + date_of_msg)

        if last_convo_date == date_of_msg:
            return True
        else:
            return False
        
def hire_request(chat_id):
    schema = mydb["resume_details"]
    ## join resume_details and interview_details fetch suitable candidates after jd upload
    
    """ remove the following dummy data"""
    records = []
    for record in schema.find():
        records.append((record['Name'],record['Skills'],record['_id']))
        
    return records


def schedule_interview(candidate_id,interview_datetime,chat_id):
    schema = mydb["interview_details"]
    """
    to be removed 
    candidate_id is of ObjectId type which is a FK 
    """
    candidate_id = mydb["resume_details"].find_one()['_id']  ## ObjectId(candidate_id) ## if int 

    data = { "candidate_id": candidate_id, "interview_date":interview_datetime,"manager_id":chat_id, "created_date": datetime.now()}
    x = schema.insert_one(data)
    ##x.acknowledgedtimestamp status 
    return(x.acknowledged)

def get_prev_intent(chat_id):
    schema = mydb["chatbot_user_details"]
    return schema.find_one({"chat_id":chat_id})['status']


