#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-01-27 19:58:48
# @Author  : yml_bright@163.com

import os 
import cStringIO
#import magic
from time import localtime, strftime
from logger import LOGGER

class FileObject():
	# init with filepath or bytes
	def __init__(self, stream):
		if os.path.isfile(stream):
			self.fileHandler = open(stream, 'rb')
			stat = os.stat(stream)
			self.accessTime = strftime("%Y-%m-%d %H:%M:%S",localtime(stat.st_atime))
			self.editTime = strftime("%Y-%m-%d %H:%M:%S",localtime(stat.st_mtime))
			self.createTime = strftime("%Y-%m-%d %H:%M:%S",localtime(stat.st_ctime))
			self.size = stat.st_size
		else:
			self.fileHandler = cStringIO.StringIO(stream)
			self.accessTime = "-"
			self.editTime = "-"
			self.createTime = "-"
			self.size = len(stream)

	def __del__(self):
		self.fileHandler.close()

	# read [length] bytes from [start]
	# if [start] is 0, read data from current position
	def read(self, length, start = -1):
		if start < 0 :
			return self.fileHandler.read(length)
		else:
			self.fileHandler.seek(start)
			return self.fileHandler.read(length)

	# return current file pointer
	def cur(self):
		return self.fileHandler.tell()

	# guess file MIME type return an ascii string
	def type(self):
		pass
		#return magic.from_buffer(self.read(1024))

	# get data which are unread and split it by whick are not continuation
	def redundancy(self):
		pass

	def __str__(self):
		return "FileObject(accessTime=%s, editTime=%s, createTime=%s, size=%s, fileHandler=%s)"%(
				self.accessTime, self.editTime, self.createTime, self.size, self.fileHandler)