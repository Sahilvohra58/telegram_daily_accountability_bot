import os
import sys
import time
import requests
import logging
import json
import pytz
import datetime as dt

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s: %(message)s",
                          datefmt="%Y-%m-%d - %H:%M:%S")
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
fh = logging.FileHandler("poll_log.log", "w")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
log.addHandler(ch)
log.addHandler(fh)

tz_CA = pytz.timezone('Canada/Central')
frequency = 1
POLL_FILE_FOLDER = 'poll_files'
DB_PATH = 'poll_data.json'
d_type= {'chat_id': int,
          'participant_id': int,
          'poll_file': str,
          'send_poll_time': str,
          'next_poll_time': str,
          'status': str}

API_KEY = os.environ.get("API_KEY", "")

API_URL = f"https://api.telegram.org/bot{API_KEY}"

INFO_MSG_STRING = """The bot sends daily poll to the group to which it is added in.
Participants can vote and submit their accountability. This acts as a daily reminder to do the tasks.

Developed by @Sahil_Vohra

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

You can always delete the poll by typing /delete
"""

def save_json(json_data, path):
  with open(path, "w") as outfile:
    json.dump(json_data, outfile)


os.makedirs(POLL_FILE_FOLDER, exist_ok=True)
if not os.path.exists(DB_PATH):
  initial_dictionary = {
          'add_question': {},
          'add_option': {},
          'choose_anonymous_voting': {},
          'choose_multiple_answers': {},
          'choose_time': {},
          'done': {}
      }
  save_json(json_data=initial_dictionary, path=DB_PATH)


def get_json(path):
  with open(path, 'r') as openfile:
     json_object = json.load(openfile)
  return json_object


def send_welcome_msg(msg):
  parameters = {
      "chat_id": msg['chat']['id'],
      "text": WELCOME_TEXT.format(username=msg['from']['username'])
  }

  requests.get(API_URL + "/sendMessage", data=parameters)


def send_msg(chat_id, text):
  parameters = {
        "chat_id": chat_id,
        "text": text
    }
  requests.get(API_URL + "/sendMessage", data=parameters)


def log_entry(msg, offset):
  chat_id = msg['chat']['id']
  poll_data = get_json(path=DB_PATH)

  if chat_id not in poll_data['add_question'].keys():
    participant_id = msg['from']['id']
    poll_file = str(chat_id) + "_" + str(offset) + '.json'
    poll_file_path = os.path.join(POLL_FILE_FOLDER, poll_file)

    save_json(json_data={"chat_id":chat_id}, path=poll_file_path)

    poll_data['add_question'][chat_id] = [participant_id, poll_file]
    save_json(json_data=poll_data, path=DB_PATH)


def add_question(msg):
  question = msg['text']
  chat_id = str(msg['chat']['id'])

  poll_data = get_json(path=DB_PATH)
  poll_file = poll_data['add_question'][chat_id][1]
  poll_file_path = os.path.join(POLL_FILE_FOLDER, poll_file)
  update_info = {'question': question, 'options': []}

  poll_dict = get_json(path=poll_file_path)
  poll_dict.update(update_info)
  save_json(json_data=poll_dict, path=poll_file_path)

  poll_data = get_json(path=DB_PATH)
  poll_data['add_option'][chat_id] = poll_data['add_question'][chat_id]
  poll_data['add_question'].pop(chat_id)
  save_json(json_data=poll_data, path=DB_PATH)

  send_msg(chat_id=msg['chat']['id'], text=QUESTION_ADDED_TEXT)



def add_option(msg):
  option = msg['text']
  chat_id = str(msg['chat']['id'])

  poll_data = get_json(path=DB_PATH)
  if option != '/done':
    poll_file = poll_data['add_option'][chat_id][1]
    poll_file_path = os.path.join(POLL_FILE_FOLDER, poll_file)

    poll_dict = get_json(path=poll_file_path)
    poll_dict['options'].append(option)
    save_json(json_data=poll_dict, path=poll_file_path)

    send_msg(chat_id=msg['chat']['id'], text=ENTER_NEXT_OPTION_TEXT)

  else:
    poll_data = get_json(path=DB_PATH)
    poll_data['choose_anonymous_voting'][chat_id] = poll_data['add_option'][chat_id]
    poll_data['add_option'].pop(chat_id)
    save_json(json_data=poll_data, path=DB_PATH)

    send_msg(chat_id=msg['chat']['id'], text=ASK_ANONYMOUS_VOTING_TEXT)


def choose_anonymous_voting(msg):
  answer = msg['text']
  if answer in ['/yes', '/no']:
    chat_id = str(msg['chat']['id'])

    poll_data = get_json(path=DB_PATH)
    poll_file = poll_data['choose_anonymous_voting'][chat_id][1]
    poll_file_path = os.path.join(POLL_FILE_FOLDER, poll_file)

    poll_dict = get_json(path=poll_file_path)
    poll_dict.update({'anonymous_voting': True if answer == '/yes' else False})
    save_json(json_data=poll_dict, path=poll_file_path)


    poll_data['choose_multiple_answers'][chat_id] = poll_data['choose_anonymous_voting'][chat_id]
    poll_data['choose_anonymous_voting'].pop(chat_id)
    save_json(json_data=poll_data, path=DB_PATH)

    send_msg(chat_id=msg['chat']['id'], text=ASK_MULTIPLE_ANSWERS_TEXT)

  else:
    send_msg(chat_id=msg['chat']['id'], text="Invalid response")
    send_msg(chat_id=msg['chat']['id'], text=ASK_ANONYMOUS_VOTING_TEXT)

def choose_multiple_answers(msg):
  answer = msg['text']
  if answer in ['/yes', '/no']:
    chat_id = str(msg['chat']['id'])

    poll_data = get_json(path=DB_PATH)
    poll_file = poll_data['choose_multiple_answers'][chat_id][1]
    poll_file_path = os.path.join(POLL_FILE_FOLDER, poll_file)

    poll_dict = get_json(path=poll_file_path)
    poll_dict.update({'multiple_answers': True if answer == '/yes' else False})
    save_json(json_data=poll_dict, path=poll_file_path)

    poll_data = get_json(path=DB_PATH)
    poll_data['choose_time'][chat_id] = poll_data['choose_multiple_answers'][chat_id]
    poll_data['choose_multiple_answers'].pop(chat_id)
    save_json(json_data=poll_data, path=DB_PATH)

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
    chat_id = str(msg['chat']['id'])

    poll_data = get_json(path=DB_PATH)
    poll_file = poll_data['choose_time'][chat_id][1]
    poll_file_path = os.path.join(POLL_FILE_FOLDER, poll_file)

    poll_dict = get_json(path=poll_file_path)
    poll_dict.update({'daily_poll_time': time_text})
    save_json(json_data=poll_dict, path=poll_file_path)

    now_time = get_now_time()
    if post_time > now_time.time():
      next_post = dt.datetime.combine(now_time.date(),
                                      post_time)
    else:
      next_post = dt.datetime.combine(now_time.date() + dt.timedelta(days=frequency),
                                      post_time)


    log.debug(f"Created new poll {poll_file} at time - {next_post}")
    poll_data['done'][poll_file] = next_post.isoformat()
    poll_data['choose_time'].pop(chat_id)
    save_json(json_data=poll_data, path=DB_PATH)

    send_msg(chat_id=msg['chat']['id'], text=DONE_TEXT.format(next_post=next_post))

  except Exception as E:
    print(f"ERROR - {E}")
    send_msg(chat_id=msg['chat']['id'], text="Something went wrong. Please try again.")
    send_msg(chat_id=msg['chat']['id'], text=CHOOSE_TIME_TEXT)

def send_poll(poll_file):
  poll_file_path = os.path.join(POLL_FILE_FOLDER, poll_file)
  poll_dict = get_json(path=poll_file_path)
  chat_id = poll_dict['chat_id']

  try:
    parameters = {
        "chat_id": chat_id,
        "question": poll_dict['question'],
        "options": json.dumps(poll_dict['options']),
        "is_anonymous": poll_dict['anonymous_voting'],
        "allows_multiple_answers": poll_dict['multiple_answers']
    }

    response = requests.get(API_URL + "/sendPoll", data=parameters)
    log.debug(f"Poll sent - {response.text}")

  except Exception as E:
    print(f"ERROR - {E}")
    log.error(f"Failed to post the poll {poll_file} -  Error: {E}", exc_info=True)
    send_msg(chat_id=chat_id, text="Something went wrong in sending the poll. Please contact @Sahil_Vohra.")


def delete_poll(msg):
  chat_id = str(msg['chat']['id'])

  poll_data = get_json(path=DB_PATH)
  polls_to_delete = [key for key in poll_data['done'].keys() if key.startswith(str(chat_id))]
  if polls_to_delete:
    for poll_file in polls_to_delete:
      poll_file_path = os.path.join(POLL_FILE_FOLDER, poll_file)
      if os.path.exists(poll_file_path):
        os.remove(poll_file_path)
      poll_data['done'].pop(poll_file)
      log.debug(f"Poll deleted - {poll_file}")

    save_json(json_data=poll_data, path=DB_PATH)
    send_msg(chat_id=chat_id, text="Poll deleted!!")
  else:
    send_msg(chat_id=chat_id, text="No poll to delete!!")

def get_updates(offset):

    parameters = {
          "offset": offset
    }

    response = requests.get(API_URL + "/getUpdates", data=parameters)
    data = response.json()

    # try:
    if data.get('result'):
        msg = data['result'][-1].get('message')

        ############### if msg text received #############
        if msg and msg.get('text'):
          chat_id = str(msg['chat']['id'])
          participant_id = msg['from']['id']
          data_received = {
              "text": msg['text'],
              "user": msg['from']['username'],
              "chat": msg['chat']['title'],
              "time": get_now_time().isoformat(),
              "offset": offset

          }
          print(data_received)

          if msg['text'] == '/start':
            send_msg(chat_id=msg['chat']['id'], text=INFO_MSG_STRING + "You can add a poll by clicking here 👉 /add 👈")


          if msg['text'] == '/add':
            send_msg(chat_id=msg['chat']['id'], text="Enter the question that you want to be asked in the group")
            log_entry(msg, offset)

          if msg['text'] == '/info':
            send_msg(chat_id=msg['chat']['id'], text=INFO_MSG_STRING)

          if msg['text'] == '/delete':
            delete_poll(msg)

          if msg['text'].lower().startswith(tuple(['salam',
                                                   'assamualaikum',
                                                   'assalamualeikumwarehmatullahewabarakatahu',
                                                   'assalamualeikum warehmatullahe wabarakatahu'])):
            send_msg(chat_id=msg['chat']['id'], text='Walaikumsalam Warahmatullahe Wabarkatohu')

          if chat_id in poll_data['add_question'].keys():
            if participant_id == poll_data['add_question'][chat_id][0]:
              add_question(msg)

          if chat_id in poll_data['add_option'].keys():
            if participant_id == poll_data['add_option'][chat_id][0]:
              add_option(msg)

          if chat_id in poll_data['choose_anonymous_voting'].keys():
            if participant_id == poll_data['choose_anonymous_voting'][chat_id][0]:
              choose_anonymous_voting(msg)

          if chat_id in poll_data['choose_multiple_answers'].keys():
            if participant_id == poll_data['choose_multiple_answers'][chat_id][0]:
              choose_multiple_answers(msg)

          if chat_id in poll_data['choose_time'].keys():
            if participant_id == poll_data['choose_time'][chat_id][0]:
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
  try:
    poll_data = get_json(path=DB_PATH)

    if poll_data['done']:
      now_time = get_now_time()
      for poll_file, poll_time in poll_data['done'].items():
        poll_time = dt.datetime.fromisoformat(poll_time)
        if now_time>=poll_time:
          send_poll(poll_file=poll_file)
          poll_data['done'][poll_file] = (poll_time + dt.timedelta(days=frequency)).isoformat()
          save_json(json_data=poll_data, path=DB_PATH)
    try:
      offset = get_updates(offset)
    except Exception as E:
      log.error(f"Failed to get updates - Error - {E}", exc_info=True)

  except Exception as E:
    log.error(f"Fatal error - {E}", exc_info=True)

  time.sleep(1)
