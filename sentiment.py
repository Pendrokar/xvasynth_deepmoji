import os
from os.path import abspath, dirname

isDev = setupData["isDev"]
logger = setupData["logger"]

import sys
root_path = f'.' if isDev else f'./resources/app' # The root directories are different in dev/prod
if not isDev:
    sys.path.append("./resources/app")

# import DeepMoji/TorchMoji
sys.path.append(f"{root_path}/plugins/deepmoji_plugin/DeepMoji")

# TOP # emoticons out of 64 to take into account
emotion_count = 10
text_scores = []
isBatch = False
# the plugin's default settings
plugin_settings = {
	"use_on_generate": False,
	"use_on_batch": False,
	"load_deepmoji_model": True
}

from plugins.deepmoji_plugin.DeepMoji.xvasynth_torchmoji import scoreText
import csv

def setup(data=None):
	global plugin_settings
	try:
		plugin_settings = data["pluginsContext"]["deepmoji_plugin_settings"]
	except:
		logger.warning("Plugin settings not loaded")
		pass

	logger.log(f'Setting up plugin. App version: {data["appVersion"]} | CPU only: {data["isCPUonly"]} | Development mode: {data["isDev"]}')
	print("Emoji smily console print test: \U0001F604")

def fetch_text(data=None):
	global plugin_settings, emotion_count, text_scores, scoreText

	if (
		plugin_settings["load_deepmoji_model"]=="false"
		or plugin_settings["load_deepmoji_model"]==False
	):
		logger.log("DeepMoji model skipped")

	text_scores = scoreText(data["sequence"], emotion_count)
	logger.log(text_scores)

def fetch_batch_text(data=None):
	global isBatch, plugin_settings, emotion_count, text_scores, scoreText
	isBatch = True

	if (
		plugin_settings["use_on_batch"]=="false"
		or plugin_settings["use_on_batch"]==False
	):
		logger.log("DeepMoji Plugin skipped on batch")
		return

	if (
		plugin_settings["load_deepmoji_model"]=="false"
		or plugin_settings["load_deepmoji_model"]==False
	):
		logger.log("DeepMoji model skipped")
		return

	try:
		logger.log(data["linesBatch"][0][0])
		text_scores = scoreText(data["linesBatch"][0][0], emotion_count)
		logger.log(text_scores)
	except:
		logger.log("Could not parse line")
		return

# text_scores
# (['Text', 'Top#%',
#                     'Emoji_1', 'Emoji_2', 'Emoji_3', 'Emoji_4', 'Emoji_5',
#                     'Pct_1', 'Pct_2', 'Pct_3', 'Pct_4', 'Pct_5'])

def adjust_values(data=None):
	global root_path, os, csv, example_helper, isBatch, logger, emotion_count, text_scores, plugin_settings

	if (
		isBatch
		and (
			plugin_settings["use_on_batch"] == "false"
			or plugin_settings["use_on_batch"] == False
		)
	):
		logger.log("DeepMoji Plugin skipped on batch")
		return

	em_angry = float(0)
	em_happy = float(0)
	em_sad = float(0)
	em_surprise = float(0)
	emojis = ''
	with open(f'{root_path}/plugins/deepmoji_plugin/emoji_unicode_emotions.csv', encoding='utf-8') as csvfile:
		reader = csv.DictReader(csvfile)
		index = 0
		for emoji_row in reader:
			if (len(text_scores) == 0):
				break
			for em_index in range(emotion_count):
				# emotion is not one of detected emotions?
				if (index != text_scores[2 + em_index]):
					# skip
					continue

				em_angry += float(emoji_row['anger']) * float(text_scores[2 + em_index + emotion_count])
				em_happy += float(emoji_row['happiness']) * float(text_scores[2 + em_index + emotion_count])
				em_sad += float(emoji_row['sadness']) * float(text_scores[2 + em_index + emotion_count])
				em_surprise += float(emoji_row['surprise']) * float(text_scores[2 + em_index + emotion_count])
				emojis += emoji_row['emoji']+' '
			index += 1
	# Show Top emojis in console
	try:
		# can crash on batch
		print(emojis)
	except:
		pass

	em_emotion_max = 0.8
	em_angry_max = 0.3
	try:
		em_angry += float(data["pluginsContext"]["mantella_settings"]["emAngry"]) * 100
		em_angry_max = 0.8
		logger.log(f"Manual em_angry adjustment => em_angry_max: {em_angry_max}")
	except:
		pass
	try:
		em_happy += float(data["pluginsContext"]["mantella_settings"]["emHappy"]) * 100
	except:
		pass
	try:
		em_sad += float(data["pluginsContext"]["mantella_settings"]["emSad"]) * 100
	except:
		pass
	try:
		em_surprise += float(data["pluginsContext"]["mantella_settings"]["emSurprise"]) * 100
	except:
		pass

	# highest wins all
	em_angry = em_angry if (em_angry == max(em_angry, em_happy, em_sad)) else 0
	em_happy = em_happy if (em_happy == max(em_angry, em_happy, em_sad)) else 0
	# ampified sadness ratio
	em_sad = (em_sad * 3) if (em_sad == max(em_angry, em_happy, em_sad)) else 0

	# amplifier
	ratio = 1.5
	if ('!!!' in text_scores[0]):
		ratio += 1.5
		em_angry_max = 0.9
		logger.log(f"!!! detected => em_angry_max: {em_angry_max}")
	elif (('!!' in text_scores[0]) or ('!?!' in text_scores[0])):
		ratio += 1.25
		em_angry_max = 0.8
		logger.log(f"!! detected => em_angry_max: {em_angry_max}")
	elif ('!' in text_scores[0]):
		ratio += 1
		em_angry_max = max(0.7, em_angry_max)
		logger.log(f"! detected => em_angry_max: {em_angry_max}")

	em_angry = min(em_angry_max, em_angry / 100 * ratio)
	em_happy = min(em_emotion_max, em_happy / 100 * ratio)
	em_sad = min(em_emotion_max, em_sad / 100 * ratio)
	em_surprise = min(em_emotion_max, em_surprise / 100 * ratio)
	# def lerp(v1, v2, d):
	# 	return v1 * (1 - d) + v2 * d

	if (em_angry > 0):
		logger.log(f"Adjusting em_angry: {em_angry}")
		for line_i in range(len(data["emAngry"])):
			for char_i in range(len(data["emAngry"][line_i])):
				data["emAngry"][line_i][char_i] = em_angry

	if (em_happy > 0):
		logger.log(f"Adjusting em_happy: {em_happy}")
		for line_i in range(len(data["emHappy"])):
			for char_i in range(len(data["emHappy"][line_i])):
				data["emHappy"][line_i][char_i] = em_happy

	if (em_sad > 0):
		logger.log(f"Adjusting em_sad: {em_sad}")
		adjusted_pacing = False
		for line_i in range(len(data["emSad"])):
			for char_i in range(len(data["emSad"][line_i])):
				data["emSad"][line_i][char_i] = em_sad
				# slower the speech
				try:
					for char_d in range(len(data["duration"][line_i][char_i])):
						data["duration"][line_i][char_i][char_d] *= (1 + em_sad / 2)
						adjusted_pacing = True
				except:
					pass
		if adjusted_pacing:
			# FIXME: xVASynth cutoff workaround
			data["duration"][-1][-1][-1] = 30
			logger.log(f"Adjusting pacing: {1 + em_sad / 2}")

	if (em_surprise > 0):
		logger.log(f"Adjusting em_surprise: {em_surprise}")
		for line_i in range(len(data["emSurprise"])):
			for char_i in range(len(data["emSurprise"][line_i])):
				data["emSurprise"][line_i][char_i] = em_surprise
	return
