#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-01-27 21:53:05
# @Author  : yml_bright@163.com

import os
from common.fileobject import FileObject
from common.fastscan import fastscan
from common.logger import *
from bmp.bmpdetector import BMPDetector
from gif.gifdetector import GIFDetector
from jpg.jpgdetector import JPGDetector
import Image

class StegoDetector():
    # the file to detected
    filePath = ''

    # report output level to stdout
    reportLevel = 1

    # write all log to a specified file
    logPath = False

    # params used in LSB and etc.
    detectSensitive = 1.0

    # the type of file to detected
    fileType = ''

    # only scan magic mark by stego software
    fastMod = False

    mimeMap = {
        # 'png' : PNGDetector,
        'bmp': BMPDetector,
        'jpg': JPGDetector,
        'gif': GIFDetector
        }

    # init detect params
    def __init__(self, filePath='', reportLevel=1, logPath=False, detectSensitive=1.0, fileType='', fastMod=False):
        self.filePath = filePath
        self.reportLevel = reportLevel
        self.logPath = logPath
        self.detectSensitive = detectSensitive
        self.fileType = fileType
        self.fastMod = fastMod

    # start to detect a image file
    def start(self):
        stream_handler.setLevel(self.reportLevel)
        errorHandler.ignoreError = False
        LOGGER.addHandler(stream_handler)
        LOGGER.addHandler(errorHandler)

        self.fileOject =  FileObject(self.filePath)

        # print self.fileOject
        # LOGGER.log(CustomLoggingLevel.BASIC_DEBUG,"common 内和主框架调试信息")

        if self.fileType == '':
            self.fileType = self.fileOject.type
        else:
            # if has different fileType ask user to choose one
            pass

        fastscan(self.filePath, self.fileType)

        if not self.fastMod:
            imgDetector = self.mimeMap[self.fileType](self.fileOject)
            # [[rowData, bitsPerPixel, channel, width, height] , ... ]
            a = imgDetector.detect()[0]
            x = Image.new('RGB',(a.width, a.height),(255,255,255))

            index = 0
            for j in range(a.height):
                for i in range(a.width):
                    r = a.rowData[index][0]
                    g = a.rowData[index][1]
                    b = a.rowData[index][2]
                    x.putpixel((i,j),(r,g,b))
                    index += 1

            x.save('save.bmp','bmp')
            
            # do some check on rowdata

t = StegoDetector(filePath='test4.jpg', fileType='jpg')
t.start()


