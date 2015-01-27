#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-01-26 16:36:13
# @Author  : yml_bright@163.com

import sys
import logging
from ansistrm import ColorizingStreamHandler

class CustomLoggingLevel:
	BASIC_DEBUG = 2
	IMAGE_DEBUG = 5
	ASCII_DATA = 42
	OTHER_DATA = 44
	EXTRA_DATA = 45
	STEGO_DATA = 47
	IMAGE_INFO = 50

logging.addLevelName(CustomLoggingLevel.BASIC_DEBUG, "BASIC DEBUG")
logging.addLevelName(CustomLoggingLevel.IMAGE_DEBUG, "IMAGE DEBUG")
logging.addLevelName(CustomLoggingLevel.ASCII_DATA, "ASCII DATA")
logging.addLevelName(CustomLoggingLevel.OTHER_DATA, "OTHER DATA")
logging.addLevelName(CustomLoggingLevel.EXTRA_DATA, "EXTRA DATA")
logging.addLevelName(CustomLoggingLevel.STEGO_DATA, "STEGO DATA")
logging.addLevelName(CustomLoggingLevel.IMAGE_INFO, "IMAGE INFO")

stream_handler = ColorizingStreamHandler(sys.stdout)
stream_handler.level_map[logging.getLevelName("BASIC DEBUG")] = (None, "cyan", False)
stream_handler.level_map[logging.getLevelName("IMAGE DEBUG")] = (None, "magenta", False)

formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s', \
			'%H:%M:%S')    
stream_handler.setFormatter(formatter)


LOGGER = logging.getLogger('StegoDetector')
LOGGER.setLevel(1)
