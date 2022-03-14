from enum import auto
from enum import Enum

class Timers(Enum):
	shavit = auto()
	btimes_1_8_3 = auto()
	btimes_2_0 = auto()

class ReplayVersions(Enum):
	Ancient = auto()
	Version2 = auto()
	Final = auto()

class Constants:
	SHAVIT_REPLAY_FORMAT_SUBVERSION = 0x03
	SHAVIT_HEADER_V2 = "{SHAVITREPLAYFORMAT}{V2}"
	SHAVIT_HEADER_FINAL = "%d:{SHAVITREPLAYFORMAT}{FINAL}" % (SHAVIT_REPLAY_FORMAT_SUBVERSION)

	MOVETYPE_WALK = 2
	FL_CLIENT = (1 << 7)
	FL_AIMTARGET = (1 << 16)

class Buttons(Enum):
	IN_ATTACK = (1 << 0)
	IN_JUMP = (1 << 1)
	IN_DUCK = (1 << 2)
	IN_FORWARD = (1 << 3)
	IN_BACK = (1 << 4)
	IN_USE = (1 << 5)
	IN_CANCEL = (1 << 6)
	IN_LEFT = (1 << 7)
	IN_RIGHT = (1 << 8)
	IN_MOVELEFT = (1 << 9)
	IN_MOVERIGHT = (1 << 10)
	IN_ATTACK2 = (1 << 11)
	IN_RUN = (1 << 12)
	IN_RELOAD = (1 << 13)
	IN_ALT1 = (1 << 14)
	IN_ALT2 = (1 << 15)
	IN_SCORE = (1 << 16)
	IN_SPEED = (1 << 17)
	IN_WALK = (1 << 18)
	IN_ZOOM = (1 << 19)
	IN_WEAPON1 = (1 << 20)
	IN_WEAPON2 = (1 << 21)
	IN_BULLRUSH = (1 << 22)
	IN_GRENADE1 = (1 << 23)
	IN_GRENADE2 = (1 << 24)
	IN_ATTACK3 = (1 << 25)

class CReplayFrame:
	fOrigin = [None] * 3
	fAngles = [None] * 2
	iButtons = 0
	iFlags = 0
	iMoveType = 0
	#Uncomment this if you use my modified btimes --- deadwinter
	#iWeapon = 0 

	def __repr__(self):
		aList = []

		for button in Buttons:
			if (self.iButtons & button.value) > 0:
				aList.append("%s" % button.name)

		return "|".join(aList)

	def __init__(self, fOrigin, fAngles, iButtons, iFlags, iMoveType):
		self.fOrigin = fOrigin
		self.fAngles = fAngles
		self.iButtons = iButtons
		self.iFlags = iFlags
		self.iMoveType = iMoveType

	def __copy__(self):
		return type(self)(self.fOrigin, self.fAngles, self.iButtons, self.iFlags, self.iMoveType)

class CReplayShavit:
	iReplayVersion = ReplayVersions.Final
	iSubVersion = Constants.SHAVIT_REPLAY_FORMAT_SUBVERSION
	iStyle = 0
	iTrack = 0
	sMap = str()
	iPreframes = 0
	iFrames = 0
	fTime = 0.0
	sAuthID = str()
	aFrames = []

	def __repr__(self):
		return "%s | %s | %s | %d frames" % (Timers.shavit, self.sMap, self.iReplayVersion, self.iFrames)

class CReplaybTimes2:
	sMap = str()
	iStyle = 0
	iTrack = 0
	bTAS = False
	iPlayerID = -1
	fTime = 0.0
	sAuthID = str()
	aFrames = []
	iPreFrames = 0

	def __repr__(self):
		return "%s | %s | %d frames" % (Timers.btimes_2_0, self.sMap, len(self.aFrames))