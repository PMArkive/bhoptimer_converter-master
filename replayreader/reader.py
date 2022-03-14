import copy
import os

from common import common
from struct import *

def read_null_terminated_string(file):
	return str().join(iter(lambda: file.read(1).decode("ascii"), '\x00'))

def read_shavit_final(file, replay):
	if replay.iSubVersion >= 0x03:
		replay.sMap = read_null_terminated_string(file)
		replay.iStyle = unpack("b", file.read(1))[0]
		replay.iTrack = unpack("b", file.read(1))[0]
		replay.iPreframes = unpack("i", file.read(4))[0]
	
	replay.iFrames = unpack("i", file.read(4))[0]
	replay.fTime = round(unpack("f", file.read(4))[0], 3)
	replay.sAuthID = read_null_terminated_string(file)

	for i in range(replay.iFrames):
		fOrigin = [None] * 3
		fOrigin[0] = unpack("f", file.read(4))[0]
		fOrigin[1] = unpack("f", file.read(4))[0]
		fOrigin[2] = unpack("f", file.read(4))[0]

		fAngles = [None] * 2
		fAngles[0] = unpack("f", file.read(4))[0]
		fAngles[1] = unpack("f", file.read(4))[0]

		iButtons = unpack("i", file.read(4))[0]
		iMoveType = common.Constants.MOVETYPE_WALK
		iFlags = (common.Constants.FL_CLIENT|common.Constants.FL_AIMTARGET)

		if replay.iSubVersion >= 0x02:
			iFlags = unpack("i", file.read(4))[0]
			iMoveType = unpack("i", file.read(4))[0]

		pFrame = common.CReplayFrame(fOrigin, fAngles, iButtons, iFlags, iMoveType)
		replay.aFrames.append(copy.copy(pFrame))
		del pFrame

def read_shavit_v2(file, replay):
	raise Exception("shavit v2 reader unimplemented")

def read_shavit_ancient(file, replay):
	raise Exception("shavit ancient reader unimplemented")

def read_shavit_general(file, version):
	pReplay = common.CReplayShavit()

	if not version == common.ReplayVersions.Ancient:
		sHeader = file.readline().decode("utf-8").rstrip().split(':', 1)
		
		if version == common.ReplayVersions.Version2:
			pReplay.iFrames = int(sHeader[0])
			read_shavit_v2(file, pReplay)

		else:
			pReplay.iSubVersion = int(sHeader[0])
			read_shavit_final(file, pReplay)

	# ancient replays
	else:
		read_shavit_ancient(file, pReplay)

	return pReplay

def read_btimes2(file):
	pReplay = common.CReplaybTimes2()

	sFileName = os.path.splitext(file.name)[0].rsplit("_", 3)

	pReplay.sMap = sFileName[0].rsplit("/")[-1]
	pReplay.iTrack = int(sFileName[1])
	pReplay.iStyle = int(sFileName[2])
	pReplay.bTAS = bool(int(sFileName[3]))

	pReplay.iPlayerID = unpack("i", file.read(4))[0]
	pReplay.fTime = round(unpack("f", file.read(4))[0], 3)

	# pReplay.sAuthID = need to be done manually

	iHits = 0

	while not iHits == 2:
		aData = file.read(4)

		if not aData:
			break

		fOrigin = [None] * 3
		fOrigin[0] = unpack("f", aData)[0]
		fOrigin[1] = unpack("f", file.read(4))[0]
		fOrigin[2] = unpack("f", file.read(4))[0]

		fAngles = [None] * 2
		fAngles[0] = unpack("f", file.read(4))[0]
		fAngles[1] = unpack("f", file.read(4))[0]

		iButtons = unpack("i", file.read(4))[0]
		iMoveType = common.Constants.MOVETYPE_WALK
		iFlags = (common.Constants.FL_CLIENT|common.Constants.FL_AIMTARGET)
		# Uncomment them if you use my modified btimes --- deadwinter
		#iMoveType = unpack("i", file.read(4))[0]
		#iFlags = unpack("i", file.read(4))[0]
		#iWeapon = unpack("i", file.read(4))[0]

		if (iButtons & common.Buttons.IN_BULLRUSH.value) > 0:
			iHits += 1

		if iHits < 1:
			pReplay.iPreFrames += 1

		if iHits < 2:
			pFrame = common.CReplayFrame(fOrigin, fAngles, iButtons, iFlags, iMoveType)
			pReplay.aFrames.append(copy.copy(pFrame))
			del pFrame


	return pReplay

def read_btimes1_8_3(file):
	pReplay = common.CReplaybTimes2()

	sFileName = os.path.splitext(file.name)[0].rsplit("_", 2)

	pReplay.sMap = sFileName[0].rsplit("/")[-1]
	pReplay.iTrack = int(sFileName[1])
	pReplay.iStyle = int(sFileName[2])

	sHeader = file.readline().rstrip().split('|', 1)
	pReplay.iPlayerID = int(sHeader[0])
	pReplay.fTime = float(sHeader[1])

	for line in file:
		sLine = line.rstrip().rsplit("|", 5)

		iMoveType = common.Constants.MOVETYPE_WALK
		iFlags = (common.Constants.FL_CLIENT|common.Constants.FL_AIMTARGET)

		fOrigin = [None] * 3
		fOrigin[0] = float(sLine[0])
		fOrigin[1] = float(sLine[1])
		fOrigin[2] = float(sLine[2])

		fAngles = [None] * 2
		fAngles[0] = float(sLine[3])
		fAngles[1] = float(sLine[4])

		iButtons = int(sLine[5])
		iMoveType = common.Constants.MOVETYPE_WALK
		iFlags = (common.Constants.FL_CLIENT|common.Constants.FL_AIMTARGET)

		pFrame = common.CReplayFrame(fOrigin,
									fAngles,
									iButtons,
									iFlags,
									iMoveType)

		pReplay.aFrames.append(copy.copy(pFrame))
		del pFrame

	return pReplay

# Reads a replay and returns a replay object.
# See the `common` module for possible replay types.
def read_replay(path, timer, version = None, mode = "rb"):
	with open(path, mode) as file:
		if timer == common.Timers.shavit:
			return read_shavit_general(file, version)

		elif timer == common.Timers.btimes_2_0:
			return read_btimes2(file)

		elif timer == common.Timers.btimes_1_8_3:
			return read_btimes1_8_3(file)

	return None