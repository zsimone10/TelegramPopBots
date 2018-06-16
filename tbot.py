import requests
import datetime

import time
import random
import string
import sys, getopt
import os, nltk


#from fbchat import log, Client
#from fbchat.models import *
from collections import *
from os import system
from utils import *
from get_response import get_text_from_db
from pymongo import MongoClient
from gtts import gTTS

onboarding_id = 7
relaxation_id = 4

timeout_seconds = 3600



keyword_dict = {
					Config().DEFAULT_YES:['yes', 'ok', 'sure', 'right', 'yea', 'ye', 'yup', 'yeah', 'okay'],
					Config().DEFAULT_NO:['no', 'not',  'neither', 'neg', 'don\'t', 'doesn\'', 'donnot', 'dont', '\'t', 'nothing', 'nah', 'na'],
					Config().DEFAULT_DK:["dk", "dunno", "dno", "don't know", "idk"]
				}



class BotHandler:

    def __init__(self, token, reply_dict, **kwargs):
		self.token = token
		self.api_url = "https://api.telegram.org/bot{}/".format(token)
		self.user_history = defaultdict(list)
		self.reply_dict = reply_dict
		self.user_name_dict = {}
		self.user_bot_dict = {}
		self.user_problem_dict = {}
		self.params = Params()
		self.config = Config()

		self.voice_choice = False

		additional_bot_control = kwargs.get('add_bot_ctl',{})
		if 'sleeping_time' in additional_bot_control:
			self.params.set_sleeping_time(additional_bot_control.get('sleeping_time'))

		if 'bot_choice' in additional_bot_control:
			self.params.set_bot_choice(additional_bot_control.get('bot_choice'))

		if 'mode' in additional_bot_control:
			self.params.set_mode(additional_bot_control.get('mode', 'text'))
			if self.params.MODE == Modes.VOICE:
				self.voice_choice == True
		if self.params.MODE == Modes.TEXT:
			self.db = MongoClient().textbot
		else:
			self.db = MongoClient().voicebot

		self.start_now = {}
		self.user_time = {}

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()
        last_update = {}
        if len(get_result) > 0:
            last_update = get_result[-1]
        '''else:
            last_update = get_result[len(get_result)]'''

        return last_update



reply_dict = get_text_from_db()
#print reply_dict
greet_bot = BotHandler(os.environ.get('TELEGRAM_BOT_TOKEN'), reply_dict)
print os.environ.get('TELEGRAM_BOT_TOKEN')
greetings = ('hello', 'hi', 'greetings', 'sup')
now = datetime.datetime.now()


def main():
    new_offset = None
    today = now.day
    hour = now.hour

    while True:
		greet_bot.get_updates(new_offset)

		last_update = greet_bot.get_last_update()
		print last_update
		if bool(last_update):
			last_update_id = last_update['update_id']
			last_chat_text = last_update['message']['text']
			last_chat_id = last_update['message']['chat']['id']
			last_chat_name = last_update['message']['chat']['first_name']
			print last_chat_id
			'''
			if last_chat_text.lower() in greetings and today == now.day and 6 <= hour < 12:
			    greet_bot.send_message(last_chat_id, 'Good Morning  {}'.format(last_chat_name))
			    today += 1
			elif last_chat_text.lower() in greetings and today == now.day and 12 <= hour < 17:
			    greet_bot.send_message(last_chat_id, 'Good Afternoon {}'.format(last_chat_name))
			    today += 1

			elif last_chat_text.lower() in greetings and today == now.day and 17 <= hour < 23:
			    greet_bot.send_message(last_chat_id, 'Good Evening  {}'.format(last_chat_name))
			    today += 1
			'''
			print greet_bot.start_now
			try:
				print "in"
				if last_chat_id not in greet_bot.start_now:
					greet_bot.start_now[last_chat_id] = True

				if not greet_bot.start_now[last_chat_id]:
					greet_bot.start_now[last_chat_id] = True
					return None
				print"2"

				if last_chat_id not in greet_bot.user_time:
					greet_bot.user_time[last_chat_id] = time.time()
				print "t"
				if (time.time() - greet_bot.user_time[last_chat_id])/timeout_seconds > 1 :
					greet_bot.clean_last_record(last_chat_id)
					greet_bot.delete_all_dict(last_chat_id)
				print "tt"
				msg = last_chat_text.lower()
				msg = ' '.join(msg.split()) # substitute multiple spaces into one
				if msg[-1] in list(string.punctuation):
					msg = msg[:-1]
				# if not chcek_rubbish_word(msg):
				# 	reply_text = "Sorry I didn't get that. Could you repeat yourgreet_bot?"
				# 	greet_bot.send_message(Message(text=reply_text), last_chat_id=last_chat_id, thread_type=thread_type)
				# 	if greet_bot.voice_choice:
				# 		#system('say -v Victoria ' + reply_text.replace("(", " ").replace(")", " "))#Alex
				# 		greet_bot.say(reply_text.replace("(", " ").replace(")", " "))
				# 	if not greet_bot.voice_choice:
				# 		time.sleep(greet_bot.params.SLEEPING_TIME)
				# 	return None
				print "ttt"
				'''if msg.strip().lower() in greeting_list:
					greet_bot.clean_last_record(last_chat_id)
					greet_bot.delete_all_dict(last_chat_id)
					print msg'''

				print '2.1'
				if msg.strip().lower() == 'restart':
					greet_bot.clean_last_record(last_chat_id)
					greet_bot.delete_all_dict(last_chat_id)
					return None
				print '2.2'
				if last_chat_id not in greet_bot.user_history or len(greet_bot.user_history[last_chat_id]) == 0 \
					or len(greet_bot.user_history[last_chat_id][-1]) == 0 \
						or len(greet_bot.user_history[last_chat_id][-1][-1]) < 2 \
							or greet_bot.user_history[last_chat_id][-1][-1][1] == greet_bot.config.CLOSING_INDEX\
								or greet_bot.user_history[last_chat_id][-1][-1][1] == greet_bot.config.ABRUPT_CLOSING_INDEX:
									_bot_choice = greet_bot.user_bot_dict[last_chat_id] if last_chat_id in greet_bot.user_bot_dict else greet_bot.params.BOT_CHOICE
									# bot_id = random.randint(0, greet_bot.params.BOT_NUM-1-1) if _bot_choice == -1 else _bot_choice #onboarding should only happens at first time or when we want it
									bot_id = random.choice(range(0, relaxation_id) + range(relaxation_id+1, onboarding_id) + range(onboarding_id+1, greet_bot.params.BOT_NUM)) if _bot_choice == -1 else _bot_choice #onboarding should only happens at first time or when we want it
									next_bot_id = (bot_id + random.randint(1, greet_bot.params.BOT_NUM-1)) % greet_bot.params.BOT_NUM
									if next_bot_id == onboarding_id:
										next_bot_id += 1
									while greet_bot.voice_choice and next_bot_id == relaxation_id:
										next_bot_id = (bot_id + random.randint(1, greet_bot.params.BOT_NUM-1)) % greet_bot.params.BOT_NUM
									greet_bot.user_bot_dict[last_chat_id] = next_bot_id

									query_name = client.fetchUserInfo(last_chat_id)[last_chat_id].name.split(" ")[0]
									if greet_bot.db.user.find({'name': query_name}).count() == 0:
										bot_id = onboarding_id
									greet_bot.user_history[last_chat_id].append([(bot_id, greet_bot.config.START_INDEX, 0, ["START_OF_CONVERSATION"])])
									if not greet_bot.voice_choice:
										bot_id = greet_bot.user_history[last_chat_id][-1][-1][0]
										greet_bot.changeThreadColor(greet_bot.params.bot_color_list[bot_id], last_chat_id=last_chat_id)
										title_to_changed = greet_bot.params.bot_name_list[bot_id][:-4]
										greet_bot.changeNickname(title_to_changed, greet_bot.uid, last_chat_id=last_chat_id, thread_type=thread_type)
				bot_id, current_id, _, _ = greet_bot.user_history[last_chat_id][-1][-1]  # ab_id, questions
				# greet_bot.user_history stores [(bot_id, current_id, ab_test, questions (list of texts), user_answer, timestamp)]
				print "3"

				if current_id == greet_bot.config.OPENNING_INDEX:
					if  any([each in msg.lower() for each in keyword_dict[greet_bot.config.DEFAULT_YES]]) and len(msg.split(" ")) < 4:
						if bot_id != onboarding_id:
							greet_bot.send_message(last_chat_id, "Please go on.")
							return None
				print '4'
				next_id = greet_bot.reply_dict[bot_id][current_id].next_id


				if bot_id != onboarding_id:
					if current_id == greet_bot.config.OPENNING_INDEX and  find_problem(msg) != None:
						greet_bot.user_problem_dict[last_chat_id] = find_problem(msg)
				problem = greet_bot.user_problem_dict.get(last_chat_id, 'that')

				#if msg.strip().lower() == 'change bot' or msg.strip().lower() in greet_bot.params.bot_tech_name_list:
				if msg.strip().lower() in greet_bot.params.bot_tech_name_list:
					whether_return = bot_id != onboarding_id
					if whether_return:
						greet_bot.clean_last_record(last_chat_id)
					greet_bot.delete_all_dict(last_chat_id, delete_name=False)
					# if msg.strip().lower() == 'change bot':
					# 	while True:
					# 		tmp = random.randint(0, greet_bot.params.BOT_NUM-1)
					# 		if tmp != bot_id:
					# 			greet_bot.user_bot_dict[last_chat_id] = tmp
					# 			break
					# else:
					greet_bot.user_bot_dict[last_chat_id] = greet_bot.params.bot_tech_name_list.index(msg.strip().lower())
					print(whether_return, bot_id)
					if whether_return:
						return None
				print '5'
				if current_id == 2 and bot_id == onboarding_id:
					greet_bot.user_name_dict[last_chat_id] = msg.lower().split()[0]

				#if current_id == greet_bot.config.START_INDEX or (current_id == 2 and bot_id == onboarding_id):
				if current_id == 2 and bot_id == onboarding_id:
					for each in ['i am', 'i\'m', 'this is', 'name is']:
						_index = msg.lower().find(each)
						if _index != -1:
							result = msg.lower()[_index + len(each)+1:]
							result = result.split()[0]
							for each_punc in list(string.punctuation):
								result = result.replace(each_punc,"")
							if len(result) > 0 and len(result) < 20:
								greet_bot.user_name_dict[last_chat_id] = result


				# if current_id == greet_bot.config.OPENNING_INDEX and any(map(lambda x: x != -1, [msg.lower().find(each) for each in ['nothing', 'not now', 'don\'t know']])):
				# 	next_id = greet_bot.config.DK_INDEX

				user_name = client.fetchUserInfo(last_chat_id)[last_chat_id].name.split(" ")[0]
				user_name = greet_bot.user_name_dict.get(last_chat_id, user_name)


				decider_dict = {
					greet_bot.config.DEFAULT_YES:find_keyword,
					greet_bot.config.DEFAULT_NO:find_keyword,
					greet_bot.config.DEFAULT_DK:find_keyword,
					greet_bot.config.DEFAULT_OTHERS:always_true,
				}




				if type(next_id) == list and len(next_id) > 0:
					if type(next_id[0][0]) == tuple:
						for (key, val) in next_id:
							if find_keyword(msg, key):
								next_id = val
								break
					elif type(next_id[0][0]) == str:
						for (key, val) in next_id:
							#print(msg, keyword_dict.get(key, [val]))
						 	if decider_dict.get(key, find_keyword)(str(msg).lower(), keyword_dict.get(key, [key])):
						 		if key == greet_bot.config.DEFAULT_NO and (len(msg.split(" ")) > 5 or len(msg) > 25):
						 			continue
						 		next_id = val
						 		break
					else:
						greet_bot.clean_last_record(last_chat_id)
						raise ValueError

				if type(next_id) != int:
					greet_bot.clean_last_record(last_chat_id)
					raise ValueError

				greet_bot.user_history[last_chat_id][-1][-1] += (msg, user_response_time,)

				next_texts = greet_bot.reply_dict[bot_id][next_id].texts.get(greet_bot.params.MODE, greet_bot.reply_dict[bot_id][next_id].texts[Modes.GENERAL])
				ab_test_index = random.randint(0, len(next_texts)-1) if greet_bot.params.ABTEST_CHOICE == -1 else min(len(next_texts)-1, greet_bot.params.ABTEST_CHOICE)
				greet_bot.user_history[last_chat_id][-1].append((bot_id, next_id, ab_test_index))

				reply_texts = []

				if next_id == greet_bot.config.OPENNING_INDEX and (not greet_bot.voice_choice):
					greet_bot.sendLocalImage('img/{}.png'.format(bot_id), last_chat_id=last_chat_id, thread_type=thread_type)

				for each in next_texts[ab_test_index]:
					reply_text = each.format(name=user_name.capitalize(), problem=problem, bot_name=greet_bot.params.bot_name_list[bot_id])
					reply_texts.append(reply_text)
					greet_bot.send_message(last_chat_id, message)
					# if greet_bot.voice_choice:
					# 	#system('say -v Victoria ' + reply_text.replace("(", " ").replace(")", " "))#Alex
					# 	greet_bot.say(reply_text.replace("(", " ").replace(")", " "))
					# else:
					time.sleep(greet_bot.params.SLEEPING_TIME)

				greet_bot.user_time[last_chat_id] = time.time()

				greet_bot.user_history[last_chat_id][-1][-1] += (reply_texts,)

				if next_id == greet_bot.config.CLOSING_INDEX or next_id == greet_bot.config.ABRUPT_CLOSING_INDEX:

					query_name = client.fetchUserInfo(last_chat_id)[last_chat_id].name.split(" ")[0]
					if greet_bot.db.user.find({'name': query_name}).count() == 0:
						greet_bot.db.user.insert(
								{
									'name':query_name,
									'user_id':last_chat_id
								}
							)


					greet_bot.user_history[last_chat_id][-1][-1] += ('END_OF_CONVERSATION', user_response_time,)

					greet_bot.db.user_history.insert(
							{
								'last_chat_id':last_chat_id,
								'user_history': greet_bot.user_history[last_chat_id][-1]
							}
						)



					#client.fetchUserInfo(last_chat_id)[last_chat_id].name.split(" ")[0]

					greet_bot.delete_all_dict(last_chat_id)
					greet_bot.start_now[last_chat_id] = False
			except:
				pass
			#greet_bot.on_message(last_chat_text, last_chat_id, 'message' )
			new_offset = last_update_id + 1

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
