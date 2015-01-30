#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-01-27 23:24:08
# @Author  : yml_bright@163.com

import struct
from common.logger import LOGGER, CustomLoggingLevel

class BMPDetector():

	detectSensitive = 1.0

	def __init__(self, fileObject):
		self.fileObject = fileObject
		self.version = struct.unpack('h',self.fileObject.read(2))
		if self.version == 0:
			# ver 1
			self.version = 1
			self.width = struct.unpack('h',self.fileObject.read(2))
			self.height = struct.unpack('h',self.fileObject.read(2))
			self.rowDataLength = struct.unpack('h',self.fileObject.read(2))
			self.channel = int(struct.unpack('b',self.fileObject.read(1)))
			if self.channel != 1:
				LOGGER.log(CustomLoggingLevel.IMAGE_INFO, 'warning: bmpfile channel is NOT 1!')
			self.bitsPerPixel = int(struct.unpack('b',self.fileObject.read(1)))
			self.padding = 32 - self.width * self.bitsPerPixel % 32
			self.rowDataLength = (self.width*self.bitsPerPixel+self.padding)*self.height/8
			LOGGER.log(CustomLoggingLevel.IMAGE_INFO, 'BMP(ver 1): %d*%dpx , channel: %d, fileLength: %db, \
						rowDataLength: %db' % (self.width, self.height, self.channel, self.fileObject.size, 
						self.rowDataLength) )

		elif self.version == 0x4D42:
			# ver 2  3  4
			self.length = struct.unpack('i',self.fileObject.read(4))
			self.fileObject.read(4) # reserved always 0
			bitmapOffset = struct.unpack('h',self.fileObject.read(2))
			bitmapLength = struct.unpack('i',self.fileObject.read(4, bitmapOffset))
			if bitmapLength == 12:
				# ver 2

			elif bitmapLength == 40:
				# ver 3
			elif bitmapLength == 108:
				# ver 4
			else:
				LOGGER.error('Unknown BMP file version.')
		else:
			LOGGER.error('Magic value BM check failed.')

	def rowdata_ver1(self):
		if self.fileObject.size - self.rowDataLength - 10 > 10*(1 - detectSensitive):
			LOGGER.log(CustomLoggingLevel.EXTRA_DATA, 'Some extra data may in end of the file.')
		LOGGER.error('BMP file version 1 is not surported.')

	def detect(self):

		LOGGER.log(CustomLoggingLevel.IMAGE_DEBUG,"BMP型图像调试信息")
		LOGGER.log(CustomLoggingLevel.ASCII_DATA,"连续 ASCII 或 可见字符")
		LOGGER.log(CustomLoggingLevel.OTHER_DATA,"其它数据")
		LOGGER.log(CustomLoggingLevel.EXTRA_DATA,"在文件尾部或中间发现多余数据")
		LOGGER.log(CustomLoggingLevel.STEGO_DATA,"发现隐写数据")
		LOGGER.log(CustomLoggingLevel.IMAGE_INFO,"输出图像基本信息")

		LOGGER.warning("警告信息")
		LOGGER.error("错误信息")
		return ['','','']