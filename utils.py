# -*- coding: UTF-8 -*-


import random
import string
import nltk
import enchant
from rake_nltk import Rake
from enum import Enum

from fbchat import Client
from fbchat.models import *

from collections import *
r = Rake()

class Params:
	def __init__(self, bot_num=9, sleeping_time=2, abtest_choice=-1, bot_choice=-1):
		self.BOT_NUM = bot_num#3
		self.SLEEPING_TIME = sleeping_time
		self.ABTEST_CHOICE = abtest_choice #   -1 random choice, > -1, the index of selected reply
		self.BOT_CHOICE = bot_choice # -1 random, 0 worse case bot, 1 problem solving bot, 2 positive thining bot
		self.MODE = Modes.TEXT
		assert self.BOT_CHOICE < self.BOT_NUM, 'Bot_num: {}, Bot_choice: {}'.format(self.BOT_NUM, self.BOT_CHOICE)
		self.bot_name_list = ['Doom Bot', 'Sherlock Bot', 'Glass-half-full Bot', 'Sir Laughs Bot', 'Chill bot', 'Treat yourself Bot', 'Dunno Bot', 'Onboarding Bot', 'Checkin Bot']
		self.bot_tech_name_list = ['worst case', 'problem solving', 'positive thinking', 'humor', 'relaxation', 'self love', 'distraction', 'introduce', 'check']
		self.bot_color_list = [ThreadColor.BILOBA_FLOWER, ThreadColor.BRILLIANT_ROSE, ThreadColor.CAMEO, ThreadColor.DEEP_SKY_BLUE, ThreadColor.FERN, ThreadColor.PUMPKIN, ThreadColor.RADICAL_RED, ThreadColor.SHOCKING, ThreadColor.VIKING]

	def set_sleeping_time(self, sleeping_time):
		self.SLEEPING_TIME = sleeping_time

	def set_bot_choice(self, bot_choice):
		self.BOT_CHOICE = bot_choice
		assert self.BOT_CHOICE < self.BOT_NUM, 'Bot_num: {}, Bot_choice: {}'.format(self.BOT_NUM, self.BOT_CHOICE)

	def set_mode(self, mode):
		if mode == 'text':
			self.MODE = Modes.TEXT
		elif mode == 'voice':
			self.MODE = Modes.VOICE


class Config:
	def __init__(self):
		self.OPENNING_INDEX = -1
		self.CLOSING_INDEX = -2
		self.START_INDEX = -3
		self.DK_INDEX = -4
		self.ARE_YOU_DONE_INDEX = -5
		self.CONTINUE_INDEX = -6
		self.ABRUPT_CLOSING_INDEX = -7
		self.QUESTION_INDEX = -8


		self.DEFAULT_YES = "__YES__"
		self.DEFAULT_NO = "__NO__"
		self.DEFAULT_DK = "__DK__"
		self.DEFAULT_OTHERS = "__OTHERS__"

# class Topics:
# 	def __init__(self):
# 		self.GENERAL = 'general'
# 		# self.TRAFFIC = 'traffic'
# 		# self.TIRED = 'tired'
# 		# self.LATE = 'late'
# 		# self.DRIVER = 'driver'
# 		# self.VEHICLE = 'vehicle'
# 		self.TEXT = 'text'
# 		self.VOICE = 'voice'

class Modes(Enum):
	GENERAL = 'general'
	TEXT = 'text'
	VOICE = 'voice'



class Reply:
	def __init__(self, bot_id, in_group_id, texts, next_id):
		self.bot_id = bot_id
		self.in_group_id = in_group_id
		self.texts = texts
		self.next_id = next_id


def find_keyword(input_str, word_list):
	if word_list[0] == Config().DEFAULT_OTHERS:
		return True
	input_str = input_str.lower()
	return any([str(each) in str(input_str) for each in word_list])


def always_true(*args):
	return True


# def find_topic(problem):
# 	topics = Topics()
# 	topic_list = [topics.TIRED, topics.LATE, topics.DRIVER, topics.VEHICLE, topics.TRAFFIC]
# 	for topic in topic_list:
# 		if topic in problem:
# 			return topic
# 	return topics.GENERAL

# def find_problem(input_str):
# 	topics = Topics()

# 	nervous_words = ["stressed", "nervous", "stress out", "stressed out", "stressful"]
# 	because_words = ['for the reason that', 'on the grounds that', 'in the interest of', 'for the sake of', 'as a result of', 'in as much as', 'as things go', 'by reason of', 'by virtue of', 'in behalf of', 'by cause of', 'considering', 'as long as', 'because of', 'in view of', 'thanks to', 'now that', 'owing to', 'because', 'in that', 'through', 'whereas', 'due to', 'seeing', 'being', 'since', 'over', 'for', 'as', 'about', 'at']
# 	first_person_list = [('our', 'your'), ('I ', 'you '), ('we', 'you'), ("my", 'your')]


# 	if any([each in input_str for each in ['tired', 'tiring', 'exhausted']]):
# 		return 'feeling tired', topics.TIRED
# 	elif any([each in input_str for each in ['late']]):
# 		return 'being late', topics.LATE
# 	elif any([each in input_str for each in ['traffic']]):
# 		return 'traffic', topics.TRAFFIC
# 	elif any([each in input_str for each in ['driver']]):
# 		return 'other drivers', topics.DRIVER
# 	elif any([each in input_str for each in ['vehicle']]):
# 		return 'your vehicle', topics.VEHICLE

# 	for nervous_word in nervous_words:
# 		for because_word in because_words:
# 			_target = nervous_word+" "+because_word
# 			_index = input_str.find(_target)
# 			if _index != -1:
# 				result = input_str[_index + len(_target)+1:]
# 				#print(result)
# 				tokens = nltk.word_tokenize(result)
# 				tagged = nltk.pos_tag(tokens)
# 				result = ""

# 				for word, tag in tagged:
# 					if tag.startswith('N') or tag.startswith('PRP'):
# 						result += word + " "
# 				for each in list(string.punctuation):
# 					result = result.replace(each,"")
# 					#print(result)
# 				for each in first_person_list:
# 					result = result.replace(each[0], each[1])

# 				if len(result) > 0:# and len(result) < 20:
# 					_kind = find_topic(result)
# 					return result, _kind
# 	return None, None


def find_problem(input_str):
	r.extract_keywords_from_text(input_str)
	result = r.get_ranked_phrases()
	result = [''.join(c for c in s if c not in string.punctuation) for s in result]
	result = [s for s in result if (s and not s.endswith('ful'))]
	cand = None
	for keyword in result:
		tagged_list = [(token, pos) for token, pos in nltk.pos_tag(keyword.split()) if pos.startswith('N') or pos.startswith('V') or pos.startswith('J')]
		if len(tagged_list) == 0:
			continue
		tokens, poses = map(list, zip(*tagged_list))
		if not any([pos for pos in poses if pos.startswith('N')]):
			continue
		cand = ' '.join(tokens)
		break
	return cand



def chcek_rubbish_word(input_str):
	english_vocab = set(w.lower() for w in nltk.corpus.words.words())
	d = enchant.Dict("en_US")
	num_success_0 = sum(map(d.check, [each for each in input_str.split()]))
	num_success_1 = 0
	for each in input_str.split():
		if each in english_vocab:
			num_success_1 += 1
	return False if num_success_0 < 0.5 * len(input_str.split()) and num_success_1 < 0.5 * len(input_str.split()) else True
