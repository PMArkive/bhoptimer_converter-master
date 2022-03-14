import configparser
import datetime
import gc
import os
import time

from threading import Thread

from common import common
from replayreader import reader
from replaywriter import writer

import pymysql
import pymysql.cursors

config = configparser.ConfigParser()
config.read("database.ini")

connection = None
id_steam3 = dict()
errors = []

# https://gist.github.com/PMArkive/b582fd38a8b26baadbc279e01b802233
def convert(steamid):
	steamid_split = steamid.split(':')
	usteamid = []
	usteamid.append('[U:1:')

	y = int(steamid_split[1])
	z = int(steamid_split[2])

	steamacct = z * 2 + y

	usteamid.append(str(steamacct) + ']')

	return ''.join(usteamid)

if config.get("db", "connect") != "no"	:
	connection = pymysql.connect(host = config.get("db", "host"),
								user = config.get("db", "user"),
								password = config.get("db", "password"),
								db = config.get("db", "db"),
								charset = config.get("db", "charset"),
								cursorclass=pymysql.cursors.DictCursor)

	try:
		with connection.cursor() as cursor:
			cursor.execute("SELECT PlayerID, SteamID, User, LastConnection FROM players;")
			result = cursor.fetchall()

			for user in result:
				if not user["SteamID"].startswith("STEAM_"):
					continue

				id_steam3[int(user["PlayerID"])] = convert(user["SteamID"])

		print("Retrieved all SteamIDs.")

	finally:
		connection.close()

timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H-%M-%S')

def convert_btimes2_to_shavit(path):
	pReplay = None

	try:
		pReplay = reader.read_replay(path, common.Timers.btimes_2_0, None)

	except Exception as ex:
		errors.append("Error converting %s. Error: %s" % (path, ex))

	if pReplay == None:
		return

	# no TAS
	if pReplay.bTAS:
		return

	if pReplay.iPlayerID in id_steam3:
		pReplay.sAuthID = id_steam3[pReplay.iPlayerID]

	else:
		pReplay.sAuthID = "invalid"

	writer.save_btimes2_to_shavit(pReplay, "output/%s/data/" % (timestamp))
	del pReplay.aFrames[:]

def convert_btimes1_8_3_to_shavit(path):
	pReplay = None

	try:
		pReplay = reader.read_replay(path, common.Timers.btimes_1_8_3, None, "r")

	except Exception as ex:
		errors.append("Error converting %s. Error: %s" % (path, ex))

	if pReplay == None:
		return

	if pReplay.iPlayerID in id_steam3:
		pReplay.sAuthID = id_steam3[pReplay.iPlayerID]

	else:
		pReplay.sAuthID = "invalid"

	writer.save_btimes2_to_shavit(pReplay, "output/%s/data/" % (timestamp))
	del pReplay.aFrames[:]

def convert_whole_directory_btimes_to_shavit(path):
	for file in os.listdir(path):
		if file.endswith(".txt"):
			convert_btimes2_to_shavit("%s/%s" % (path, file))

		elif file.endswith(".rec"):
			convert_btimes1_8_3_to_shavit("%s/%s" % (path, file))

		gc.collect()

convert_whole_directory_btimes_to_shavit("input")

print("Done converting.")

if len(errors) > 0:
	print("%d replays could not be converted. Errors:" % (len(errors)))

	for error in errors:
		print(error)
