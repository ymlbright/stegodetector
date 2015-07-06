#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-01-27 21:53:05
# @Author  : yml_bright@163.com

import os, re
from optparse import OptionParser
from common.fileobject import FileObject
from common.fastscan import fastscan
from common.logger import *
from common.imageshow import ImageShow
from common.ascdetect import asc_detect
from bmp.bmpdetector import BMPDetector
from gif.gifdetector import GIFDetector
from jpg.jpgdetector import JPGDetector
from png.pngdetector import PNGDetector

import Image

class StegoDetector():
    # # the file to detected
    # filePath = ''

    # # report output level to stdout
    # reportLevel = 1

    # # write all log to a specified file
    # logPath = False

    # # params used in LSB and etc.
    # detectSensitive = 1.0

    # # the type of file to detected
    # fileType = ''

    # # only scan magic mark by stego software
    # fastMod = False

    # # wether turn on ASCII detect
    # asciiDetect = False
    # asciiDetectLength = 10

    mimeMap = {
        'png' : PNGDetector,
        'bmp': BMPDetector,
        'jpg': JPGDetector,
        'gif': GIFDetector
        }
    defaultValue = {
        'reportLevel': 1,
        'logPath': False,
        'detectSensitive': 1.0,
        'fileType': '',
        'fastMod': False,
        'asciiDetect': False,
        'asciiDetectLength': 10,
        'ignoreError': False
    }

    # init detect params
    def __init__(self, filePath='', reportLevel=1, logPath=False, detectSensitive=1.0, fileType='', fastMod=False, asciiDetect = False, asciiDetectLength=10, ignoreError=False, args=None):
        if args:
            for key in args:
                if args[key]:
                    setattr(self, key, args[key])
                else:
                    setattr(self, key, self.defaultValue[key])
        else:
            self.filePath = filePath
            self.reportLevel = reportLevel
            self.logPath = logPath
            self.fileType = fileType
            self.fastMod = fastMod
            self.asciiDetect = asciiDetect
            self.detectSensitive = detectSensitive
            self.asciiDetectLength = asciiDetectLength
            self.ignoreError = ignoreError

    def image_type(self, string):
        if re.compile(r'jpeg', re.I).findall(string):
            return 'jpg'
        elif re.compile(r'png', re.I).findall(string):
            return 'png'
        elif re.compile(r'bmp', re.I).findall(string):
            return 'bmp'
        elif re.compile(r'png', re.I).findall(string):
            return 'git'
        else:
            return 'none'

    # start to detect a image file
    def start(self):
        stream_handler.setLevel(self.reportLevel)
        errorHandler.ignoreError = self.ignoreError
        LOGGER.addHandler(stream_handler)
        LOGGER.addHandler(errorHandler)

        self.fileOject =  FileObject(self.filePath)
        regType = self.image_type(self.fileOject.type())
        # print self.fileOject
        # LOGGER.log(CustomLoggingLevel.BASIC_DEBUG,"common 内和主框架调试信息")

        if self.fileType == '':
            self.fileType = regType
        elif self.fileType != regType:
            # if has different fileType ask user to choose one
            print "Given file type is %s, but recognized type is %s. Use %s?(Y/n)" % ( self.fileType, regType, regType),
            while 1:
                inString = raw_input(':')
                if inString == '':
                    self.fileType = regType
                    break
                elif inString == 'n' or inString == 'N':
                    break
                else:
                    print "Please input Y or N."

        fastscan(self.fileOject, self.fileType)

        if self.asciiDetect:
            asc_detect(self.filePath, self.asciiDetectLength)

        if not self.fastMod:
            imgDetector = self.mimeMap[self.fileType](self.fileOject)
            imageShow = ImageShow(imgDetector.detect())
            imageShow.show()
            # [[rowData, bitsPerPixel, channel, width, height] , ... ]
            # a = imgDetector.detect()[0]
            # # return
            # x = Image.new('RGB',(a.width, a.height),(0,0,0))
            # index = 0
            # for j in range(a.height):
            #     for i in range(a.width):
            #         r = a.rowData[index][0]
            #         g = a.rowData[index][1]
            #         b = a.rowData[index][2]
            #         x.putpixel((i,j),(r,g,b))
            #         index += 1
            # x.save('save.bmp', 'BMP')
            # do some check on rowdata

usage = "usage: stegodetector.py [-tqavl] -f FILE "  
parser = OptionParser(usage=usage) 

parser.add_option("-f", "--file", help="file to be detected", metavar="FILE",
                  action="store", type="string", dest="filePath")
parser.add_option("-t", "--type", help="specific the file type", metavar="TYPE",
                  action="store", type="string", dest="fileType")
parser.add_option("-q", help="turn on quick detect mode",
                  action="store_true", dest="fastMod")
parser.add_option("-a", help="turn on ascii detect",
                  action="store_true", dest="asciiDetect")
parser.add_option("-i", help="continue when error occured",
                  action="store_true", dest="ignoreError")
parser.add_option("-v", "--verbose", help="log level", metavar="LEVEL",
                  action="store", type="int", dest="reportLevel")
parser.add_option("-l", "--logfile", help="file to save detect log", metavar="FILE",
                  action="store", type="string", dest="logPath")
(options, args) = parser.parse_args()

if not options.filePath:
    print "Please specific a file to detect."
    exit(0)
else:
    args = {
        'filePath': options.filePath,
        'fileType': options.fileType,
        'fastMod': options.fastMod,
        'asciiDetect': options.asciiDetect,
        'reportLevel': options.reportLevel,
        'logPath': options.logPath,
        'ignoreError': options.ignoreError
    }
    if not options.fileType:
        args['fileType'] = options.filePath[options.filePath.rfind('.')+1:]
    detector = StegoDetector(args = args)
    detector.start()
    


