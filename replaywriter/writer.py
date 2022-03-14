import os

from common import common
from struct import *

def save_btimes2_to_shavit(replay, path):
	sTrack = str()

	if replay.iTrack > 0:
		sTrack = "_%d" % (replay.iTrack)

	sDirectoryPath = path + "replaybot/%d" % (replay.iStyle)
	sPath = sDirectoryPath + "/%s%s.replay" % (replay.sMap, sTrack)

	if not os.path.exists(sDirectoryPath):
		os.makedirs(sDirectoryPath)
		
	with open(sPath, "wb") as file:
		file.write(("%s\n" % (common.Constants.SHAVIT_HEADER_FINAL)).encode("ascii"))
		file.write(("%s\x00" % (replay.sMap)).encode("ascii"))
		file.write(pack("b", replay.iStyle))
		file.write(pack("b", replay.iTrack))
		file.write(pack("i", replay.iPreFrames))
		file.write(pack("i", len(replay.aFrames)))
		file.write(pack("f", replay.fTime))
		file.write(("%s\x00" % (replay.sAuthID)).encode("ascii"))

		for frame in replay.aFrames:
			file.write(pack("f", frame.fOrigin[0]))
			file.write(pack("f", frame.fOrigin[1]))
			file.write(pack("f", frame.fOrigin[2]))
			file.write(pack("f", frame.fAngles[0]))
			file.write(pack("f", frame.fAngles[1]))
			file.write(pack("i", frame.iButtons))
			file.write(pack("i", frame.iFlags))
			file.write(pack("i", frame.iMoveType))

	print("Saved %s." % (sPath))