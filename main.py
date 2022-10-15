import os
import time
import requests
import datetime as dt
import pandas as pd
import json
import pytz

tz_CA = pytz.timezone('Canada/Central') 
frequency = 1

API_URL = "https://api.telegram.org/bot5715878772:AAGgBBSLkZpPPXdZ28i4DD3bhFVIj57S-0Q"

INFO_MSG_STRING = """The bot sends daily poll to the group to which it is added in. 
Participants can vote and submit their accountability. This acts as a daily reminder to to do the tasks. 

Developed by @Sahil_Vohra

Type /start to begin the bot
"""

WELCOME_TEXT = """Jazakallahukhairan @{username} for adding me.

I can help you to send automated daily polls to keep all your tasks on track.

Type /info for more information or get started by typing /start
"""

QUESTION_ADDED_TEXT = """Question added 👍.
Enter your first option
"""

ENTER_NEXT_OPTION_TEXT = """Option added 👍.
Enter next option or click here 👉 /done 👈 if you dont want to add any other options.
"""

ASK_ANONYMOUS_VOTING_TEXT = """Do you want the poll to be anonymous?

click here 👉 /yes 👈 for YES 
              or
click here 👉 /no 👈 for NO 
"""

ASK_MULTIPLE_ANSWERS_TEXT = """Do you want to allow participants to choose multiple options?

click here 👉 /yes 👈 for YES 
              or
click here 👉 /no 👈 for NO 
"""

TRY_AGAIN_YES_NO_TEXT = """Invalid response!!
Please try again

click here 👉 /yes 👈 for YES 
              or
click here 👉 /no 👈 for NO 
"""

CHOOSE_TIME_TEXT = """What time daily do you want the poll to be posted (Canada/Central timezone)?
(Note the 24 hour time format)

(HH_MM_SS)

/01_00_00 (01:00 AM)
 
/02_00_00 (02:00 AM)
 
/03_00_00 (03:00 AM)
 
/04_00_00 (04:00 AM)
 
/05_00_00 (05:00 AM)
 
/06_00_00 (06:00 AM)
 
/07_00_00 (07:00 AM)
 
/08_00_00 (08:00 AM)
 
/09_00_00 (09:00 AM)
 
/10_00_00 (10:00 AM)
 
/11_00_00 (11:00 AM)
 
/12_00_00 (12:00 PM)
 
/13_00_00 (01:00 PM)
 
/14_00_00 (02:00 PM)
 
/15_00_00 (03:00 PM)
 
/16_00_00 (04:00 PM)
 
/17_00_00 (05:00 PM)
 
/18_00_00 (06:00 PM)
 
/19_00_00 (07:00 PM)
 
/20_00_00 (08:00 PM)
 
/21_00_00 (09:00 PM)
 
/22_00_00 (10:00 PM)
 
/23_00_00 (11:00 PM)
 
/00_00_00 (12:00 AM)
 
You can also enter a custom time in this format:
/HH_MM_SS
"""

DONE_TEXT = """Done 👍.
Your poll has been successfully created and it will be posted daily on the given time. Starting {next_post}. In Shaa Allah.

The developer @Sahil_Vohra has spent a lot of time making this bot. If this bot benefits you a little bit then please make dua for him 🤗. 

Jazakallahukhairan. May Allah accepts your deeds from you. Ameen
"""


POLL_FILE_FOLDER = 'poll_files'
DB_PATH = 'poll_data.csv'

d_type= {'chat_id': int,
          'participant_id': int,
          'poll_file': str,
          'send_poll_time': str,
          'next_poll_time': str,
          'status': str} 

if not os.path.exists(DB_PATH):
    d = pd.DataFrame(columns = d_type.keys())
    d = d.astype(d_type)
    d['next_poll_time'] = pd.to_datetime(d['next_poll_time'])
    d.to_csv(DB_PATH, index=False)

os.makedirs(POLL_FILE_FOLDER, exist_ok=True)

def send_welcome_msg(msg):
  parameters = {
      "chat_id": msg['chat']['id'],
      "text": WELCOME_TEXT.format(username=msg['from']['username'])
  }

  resp = requests.get(API_URL + "/sendMessage", data=parameters)


def send_msg(chat_id, text):
  parameters = {
        "chat_id": chat_id,
        "text": text
    }
  resp = requests.get(API_URL + "/sendMessage", data=parameters)


def log_entry(msg, offset):
  chat_id = msg['chat']['id']

  if chat_id not in poll_data[poll_data['status'] == 'start']['chat_id'].to_list():
    participant_id = msg['from']['id']
    poll_file = str(chat_id) + "_" + str(offset) + '.json'
    poll_file_path = os.path.join(POLL_FILE_FOLDER, poll_file)
    with open(poll_file_path, 'w') as outfile:
      json.dump({"chat_id":chat_id}, outfile)


    new_data = {
        'chat_id': chat_id,
            'participant_id': participant_id,
            'poll_file': poll_file,
            'send_poll_time': None,
            'next_poll_time': None,
            'status': 'start'
    }

    poll_data.append(new_data, ignore_index=True).to_csv(DB_PATH, index=False)

def add_question(msg):
  question = msg['text']
  chat_id = msg['chat']['id']
  chat_data = poll_data[poll_data['chat_id'] == chat_id]
  poll_files = chat_data[chat_data['status'] == 'start']['poll_file']
  idx = poll_files.index[0]
  poll_file = poll_files[0]
  poll_file_path = os.path.join(POLL_FILE_FOLDER, poll_file)
  update_info = {'question': question, 'options': []}

  with open(poll_file_path) as json_file:
    data = json.load(json_file)
  
  data.update(update_info)

  with open(poll_file_path, 'w') as outfile:
    json.dump(data, outfile)
  
  poll_data.loc[idx, 'status'] = 'add_option'
  poll_data.to_csv(DB_PATH, index=False)

  send_msg(chat_id=msg['chat']['id'], text=QUESTION_ADDED_TEXT)



def add_option(msg):
  option = msg['text']
  chat_id = msg['chat']['id']
  chat_data = poll_data[poll_data['chat_id'] == chat_id]
  poll_files = chat_data[chat_data['status'] == 'add_option']['poll_file']
  idx = poll_files.index[0]

  if option != '/done':
    poll_file = poll_files[0]
    poll_file_path = os.path.join(POLL_FILE_FOLDER, poll_file)
    with open(poll_file_path) as json_file:
      data = json.load(json_file)
    
    data['options'].append(option)

    with open(poll_file_path, 'w') as outfile:
      json.dump(data, outfile)
    
    send_msg(chat_id=msg['chat']['id'], text=ENTER_NEXT_OPTION_TEXT)

  else:
    poll_data.loc[idx, 'status'] = 'choose_anonymous_voting'
    poll_data.to_csv(DB_PATH, index=False)
    send_msg(chat_id=msg['chat']['id'], text=ASK_ANONYMOUS_VOTING_TEXT)
    

def choose_anonymous_voting(msg):
  answer = msg['text']
  if answer in ['/yes', '/no']:
    chat_id = msg['chat']['id']
    chat_data = poll_data[poll_data['chat_id'] == chat_id]
    poll_files = chat_data[chat_data['status'] == 'choose_anonymous_voting']['poll_file']
    idx = poll_files.index[0]
    poll_file = poll_files[0]
    poll_file_path = os.path.join(POLL_FILE_FOLDER, poll_file)

    with open(poll_file_path) as json_file:
      data = json.load(json_file)
            
    data.update({'anonymous_voting': True if answer == '/yes' else False})

    with open(poll_file_path, 'w') as outfile:
      json.dump(data, outfile)
    
    poll_data.loc[idx, 'status'] = 'choose_multiple_answers'
    poll_data.to_csv(DB_PATH, index=False)
    send_msg(chat_id=msg['chat']['id'], text=ASK_MULTIPLE_ANSWERS_TEXT)
  
  else:
    send_msg(chat_id=msg['chat']['id'], text="Invalid response")
    send_msg(chat_id=msg['chat']['id'], text=ASK_ANONYMOUS_VOTING_TEXT)

def choose_multiple_answers(msg):
  answer = msg['text']
  if answer in ['/yes', '/no']:
    chat_id = msg['chat']['id']
    chat_data = poll_data[poll_data['chat_id'] == chat_id]
    poll_files = chat_data[chat_data['status'] == 'choose_multiple_answers']['poll_file']
    idx = poll_files.index[0]
    poll_file = poll_files[0]
    poll_file_path = os.path.join(POLL_FILE_FOLDER, poll_file)

    with open(poll_file_path) as json_file:
      data = json.load(json_file)
            
    data.update({'multiple_answers': True if answer == '/yes' else False})

    with open(poll_file_path, 'w') as outfile:
      json.dump(data, outfile)
    
    poll_data.loc[idx, 'status'] = 'choose_time'
    poll_data.to_csv(DB_PATH, index=False)
    send_msg(chat_id=msg['chat']['id'], text=CHOOSE_TIME_TEXT)
  
  else:
    send_msg(chat_id=msg['chat']['id'], text="Invalid response")
    send_msg(chat_id=msg['chat']['id'], text=ASK_MULTIPLE_ANSWERS_TEXT)

def get_now_time():
  timezone = pytz.timezone("US/Eastern")
  timezone_aware_date = timezone.localize(dt.datetime.now())
  now_time =  dt.datetime.now(tz_CA) - dt.timedelta(hours = int(timezone_aware_date.isoformat()[-4])-5)
  return dt.datetime.combine(now_time.date(), now_time.time())

def choose_time(msg):
  time_text = msg['text'][1:]
  try:
    post_time = dt.datetime.strptime(time_text, "%H_%M_%S").time()
    chat_id = msg['chat']['id']
    chat_data = poll_data[poll_data['chat_id'] == chat_id]
    idx = chat_data[chat_data['status'] == 'choose_time'].index[0]
    poll_data.loc[idx, 'send_poll_time'] = time_text
    now_time = get_now_time()
    if post_time > now_time.time():
      next_post = dt.datetime.combine(now_time.date(), 
                                      post_time)
    else:
      next_post = dt.datetime.combine(now_time.date() + dt.timedelta(days=frequency), 
                                      post_time)
    poll_data.loc[idx, 'next_poll_time'] = next_post
    poll_data.loc[idx, 'status'] = 'done'
    poll_data.to_csv(DB_PATH, index=False)
    send_msg(chat_id=msg['chat']['id'], text=DONE_TEXT.format(next_post=next_post))
  
  except Exception as E:
    print(f"ERROR - {E}")
    send_msg(chat_id=msg['chat']['id'], text="Something went wrong. Please try again.")
    send_msg(chat_id=msg['chat']['id'], text=CHOOSE_TIME_TEXT)

def send_poll(poll_file, idx, chat_id):
  poll_file_path = os.path.join(POLL_FILE_FOLDER, poll_file)

  try:
    with open(poll_file_path) as json_file:
        data = json.load(json_file)

    parameters = {
        "chat_id": data['chat_id'],
        "question": data['question'],
        "options": json.dumps(data['options']),
        "is_anonymous": data['anonymous_voting'],
        "allows_multiple_answers": data['multiple_answers'],

    }

    response = requests.get(API_URL + "/sendPoll", data=parameters)
    print(response.text)
    poll_data.loc[idx, 'next_poll_time'] = poll_data.loc[idx, 'next_poll_time'] + dt.timedelta(days=frequency)
    poll_data.to_csv(DB_PATH, index=False)
  except Exception as E:
    print(f"ERROR - {E}")
    send_msg(chat_id=chat_id, text="Something went wrong in sending the poll. Please contact @Sahil_Vohra.")


def delete_poll(msg):
  chat_id = msg['chat']['id']
  chat_data = poll_data[poll_data['chat_id'] == chat_id]
  for poll_file in chat_data['poll_file']:
    poll_file_path = os.path.join(POLL_FILE_FOLDER, poll_file)
    if os.path.exists(poll_file_path):
      os.remove(poll_file_path)
  idxs = list(chat_data.index)
  poll_data.drop(poll_data.index[idxs], inplace=True)
  poll_data.reset_index(drop=True)
  poll_data.to_csv(DB_PATH, index=False)
  send_msg(chat_id=chat_id, text="Poll deleted!!")

def get_updates(offset):
  parameters = {
      "offset": offset
  }

  response = requests.get(API_URL + "/getUpdates", data=parameters)
  data = response.json()


  if data['result']:
    msg = data['result'][-1].get('message')

    ############### if msg text received #############
    if msg and msg.get('text'):
      chat_id = msg['chat']['id']
      participant_id = msg['from']['id']
      data_received = {
          "offset": offset,
          "user": msg['from']['username'],
          "chat": msg['chat']['title'],
          "text": msg['text']
      }
      print(data_received)

      if msg['text'] == '/start':
        send_msg(chat_id=msg['chat']['id'], text="Enter the question that you want to be asked in the grp")          
        log_entry(msg, offset)
      
      if msg['text'] == '/info':
        send_msg(msg=msg, text=INFO_MSG_STRING)
      
      if msg['text'] == '/delete':
        delete_poll(msg) ###########
      
      if msg['text'].lower().startswith(tuple(['salam', 
                                               'assamualaikum', 
                                               'assalamualeikumwarehmatullahewabarakatahu', 
                                               'assalamualeikum warehmatullahe wabarakatahu'])):
        send_msg(msg=msg, text='Walaikumsalam Warahmatullahe Wabarkatohu')
      
      if chat_id in poll_data.chat_id.to_list():
        chat_data = poll_data[poll_data['chat_id'] == chat_id]
        if participant_id in chat_data.participant_id.to_list():
          participant_data = chat_data[chat_data['participant_id'] == participant_id]
          incomplete_poll_data = participant_data[participant_data['status'] != 'done']
          if len(incomplete_poll_data) == 1:
            if incomplete_poll_data['status'][0] == 'start':
              add_question(msg)
            if incomplete_poll_data['status'][0] == 'add_option':
              add_option(msg)
            if incomplete_poll_data['status'][0] == 'choose_anonymous_voting':
              choose_anonymous_voting(msg)
            if incomplete_poll_data['status'][0] == 'choose_multiple_answers':
              choose_multiple_answers(msg) 
            if incomplete_poll_data['status'][0] == 'choose_time':
              choose_time(msg)


    elif msg and msg.get('new_chat_participant'):
      print("New member added - ", msg)
      if msg['new_chat_participant'].get('username') == 'daily_accountability_poll_bot':
        send_welcome_msg(msg)
    
    elif msg and msg.get('left_chat_participant'):
      if msg['left_chat_participant'].get('username') == 'daily_accountability_poll_bot':
        print("Bot removed from group - ", msg)
        delete_poll(msg)

    else:
      print("New msg type - ", msg)

    return data["result"][-1]["update_id"] + 1 # return offset number

    
      

  else: # No data received
    return offset

offset = '0'
while True:
  poll_data = pd.read_csv(DB_PATH, dtype=d_type) # parse_dates=['next_poll_time', 'send_poll_time'])
  # poll_data['send_poll_time'] = pd.to_datetime(poll_data['send_poll_time'])
  poll_data['next_poll_time'] = pd.to_datetime(poll_data['next_poll_time'])
  now_time = get_now_time()
  if len(poll_data['next_poll_time'])>0:
    send_poll_data = poll_data[poll_data['next_poll_time']<=now_time]
    if len(send_poll_data) >= 1:
      send_poll(poll_file=send_poll_data['poll_file'][0], 
                idx=send_poll_data.index[0], 
                chat_id=send_poll_data['chat_id'][0])
  offset = get_updates(offset)
  time.sleep(1)
