# -*- coding: utf-8 -*-
# @Date    : 2015-01-27 23:24:08
# @Author  : xieshufang76@gmail.com

import struct
from common.logger import LOGGER, CustomLoggingLevel


class GIFDetector():

    def __init__(self,file_object):
        self.fileObject = file_object
        if file_object.read(3) != 'GIF':
            LOGGER.error("File is not a gif file")
        self.version = file_object.read(3)
        if self.version != '37a'or self.version!='39a':
            LOGGER.error("Invalid version")
        self.logicScreenWidth = file_object.read(2)
        self.logicScreenHeight = file_object.read(2)
        mask = file_object.read(1)
        self.pixel = mask & 0b111
        mask >>= 3
        self.sortFlag = mask & 0b1
        mask >>= 1
        self.colorResolution = mask & 0b111
        mask >>= 3
        self.globalColorTableFlag = mask & 0b1
        self.globalColorTable = [[0, 0, 0]]*(2 ** (self.pixel+1))
        for i in range(len(self.globalColorTable)):
            for j in range(3):  # 0 red 1 green 2 blue
                self.globalColorTable[i][j] = file_object.read(1)
        self.images = []
        while True:
            tag = file_object.read(1)
            if tag != 0b00101100:  # start of a image
                break
            image = {}
            image.xOffset = file_object.read(2)
            image.yOffset = file_object.read(2)
            image.width = file_object.read(2)
            mask = file_object.read(1)
            image.pixel = mask & 0b111
            mask >>= 3
            image.reserved = mask & 0b11
            if image.reserved != 0:
                pass # TODO show warning
            mask >>= 2
            image.sortFlag = mask & 0b1
            mask >>= 1
            image.interlaceFlag = mask & 0b1
            mask >>= 1
            image.localColorTableFlag = mask & 0b1
            if image.localColorTableFlag:
                image.localColorTable = [[0, 0, 0]]*(2 ** (image.pixel+1))
                for i in range(len(image.localColorTable)):
                    for j in range(3):  # 0 red 1 green 2 blue
                        image.localColorTable[i][j] = file_object.read(1)




