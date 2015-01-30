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
        self.version = struct.unpack('h',self.fileObject.read(2))[0]
        if self.version == 0:
            # ver 1
            # read file header
            self.version = 1
            self.width, self.height, self.rowDataLength = struct.unpack('3h',self.fileObject.read(6))
            self.channel = int(struct.unpack('b',self.fileObject.read(1))[0])
            self.bitsPerPixel = int(struct.unpack('b',self.fileObject.read(1))[0])
            self.padding = 32 - self.width * self.bitsPerPixel % 32
            self.rowDataLength = (self.width*self.bitsPerPixel+self.padding)*self.height/8
            LOGGER.log(CustomLoggingLevel.IMAGE_INFO, 'BMP(ver 1): %d*%dpx , channel: %d, fileLength: %d b, rowDataLength: %d b' % 
                        (self.width, self.height, self.channel, self.fileObject.size, self.rowDataLength) )

        elif self.version == 0x4D42:
            # ver 2  3  4
            # read file header
            self.length = struct.unpack('i',self.fileObject.read(4))[0]
            if self.fileObject.read(4) != '\x00\x00\x00\x00': # reserved always 0
                LOGGER.log(CustomLoggingLevel.OTHER_DATA, 'File header reserved options is not 0')
            bitmapOffset = struct.unpack('i',self.fileObject.read(4))[0]

            # read bitmap header
            bitmapHeaderLength = struct.unpack('l',self.fileObject.read(4))[0]
            self.width, self.height, self.channel, self.bitsPerPixel = struct.unpack('2l2h',self.fileObject.read(12))
            if self.bitsPerPixel != 24:
                self.numberOfEntries = 1 << self.bitsPerPixel
            else:
                self.numberOfEntries = 0

            if bitmapHeaderLength == 12:
                # ver 2
                self.version = 2
            elif bitmapHeaderLength == 40:
                # ver 3
                self.version = 3
                self.compressionMethod, self.bitmapLength = struct.unpack('2L',self.fileObject.read(8))
                self.fileObject.read(16) # skip useless header
            elif bitmapHeaderLength == 108:
                # ver 4
                self.version = 4
            else:
                LOGGER.error('Unknown BMP file version.')

            if self.version != 0x4D42:
                # read color palette
                self.colorPalette = []
                for i in range(self.numberOfEntries):
                    t = {}
                    t['B'], t['G'], t['R'], reserved = struct.unpack('4b',self.fileObject.read(4))
                    self.colorPalette.append(t)
                    if reserved != 0:
                        LOGGER.log(CustomLoggingLevel.OTHER_DATA, 'Color palette reserved option is not 0, is 0x%x!',ord(reserved))

                self.rowDataLength = 0
                LOGGER.log(CustomLoggingLevel.IMAGE_INFO, 'BMP(ver %d): %d*%dpx , channel: %d, fileLength: %d b, rowDataLength: - b' % 
                            (self.version, self.width, self.height, self.channel, self.fileObject.size) )
        else:
            LOGGER.error('Magic value BM check failed.')

        if self.channel != 1:
            LOGGER.log(CustomLoggingLevel.IMAGE_INFO, 'Warning: bmpfile channel is NOT 1!')

    def rowdata_ver1(self):
        if self.fileObject.size - self.rowDataLength - 10 > 10*(1 - detectSensitive):
            LOGGER.log(CustomLoggingLevel.EXTRA_DATA, 'Some extra data may in end of the file.')
        LOGGER.error('BMP file version 1 is not surported.')

    def rowdata_ver4(self):
        LOGGER.error('BMP file version 4 is not surported.')

    def rowdata_ver23(self):
        pass

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