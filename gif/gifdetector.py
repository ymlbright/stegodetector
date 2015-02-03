# -*- coding: utf-8 -*-
# @Date    : 2015-01-27 23:24:08
# @Author  : xieshufang76@gmail.com

# http://www.w3.org/Graphics/GIF/spec-gif89a.txt

import struct
from common.logger import LOGGER, CustomLoggingLevel
import logging

class GIFDetector():
    def __init__(self, file_object):
        LOGGER.addHandler(logging.StreamHandler())
        self.fileObject = file_object
        if file_object.read(3) != 'GIF':
            LOGGER.error("File is not a gif file")
        self.type = "GIF"
        self.version = file_object.read(3)
        if self.version != '87a' and self.version != '89a':
            LOGGER.error("Invalid version")
        else:
            LOGGER.info("version is "+self.version)
        self.logicScreenWidth = file_object.read_uint16()
        self.logicScreenHeight = file_object.read_uint16()
        mask = file_object.read_uint8()
        self.pixel = mask & 0b111
        mask >>= 3
        self.sortFlag = mask & 0b1
        mask >>= 1
        self.colorResolution = mask & 0b111
        mask >>= 3
        self.globalColorTableFlag = mask & 0b1
        if self.version == "89a":
            self.backgroundColorIndex = file_object.read_uint8()
            self.pixelAspectRatio = file_object.read_uint8()
        self.globalColorTable = [[0, 0, 0]] * (2 ** (self.pixel + 1))
        LOGGER.info("global table size is %d" % len(self.globalColorTable))
        for i in range(len(self.globalColorTable)):
            for j in range(3):  # 0 red 1 green 2 blue
                self.globalColorTable[i][j] = file_object.read_uint8()
        self.images = []
        image = {}
        while True:
            tag = file_object.read_uint8()

            if tag == 59:
                break  # end of gif

            if tag == 0b00101100:  # start of a image descriptor
                LOGGER.info("image descriptor")
                image["xOffset"] = file_object.read_uint16()
                image["yOffset"] = file_object.read_uint16()
                image["width"] = file_object.read_uint16()
                image["height"] = file_object.read_uint16()
                mask = file_object.read_uint8()
                image["pixel"] = mask & 0b111
                mask >>= 3
                image["reserved"] = mask & 0b11
                if image["reserved"] != 0:
                    LOGGER.warning("reserved data should be 0")
                mask >>= 2
                image["sortFlag"] = mask & 0b1
                mask >>= 1
                image["interlaceFlag"] = mask & 0b1
                mask >>= 1
                image["localColorTableFlag"] = mask & 0b1
                if image["localColorTableFlag"]:
                    image["localColorTable"] = [[0, 0, 0]] * (2 ** (image["pixel"] + 1))
                    for i in range(len(image["localColorTable"])):
                        for j in range(3):  # 0 red 1 green 2 blue
                            image["localColorTable"][i][j] = file_object.read_uint8()
            elif tag == 0x21:  # Graphic Control Extension.
                if self.version != "89a":
                    LOGGER.warning("not version 89a but has extension segment.")
                sub_tag = file_object.read_uint8()
                if sub_tag == 0xF9:  # Graphic Control Extension.
                    LOGGER.info("Graphic Control Extension")
                    block_size = file_object.read_uint8()
                    if block_size != 4:
                        LOGGER.warning("block size is not 4 in Graphic Control Extension")
                    control = {}
                    mask = file_object.read_uint8()
                    control["transparentFlag"] = mask & 0b1
                    mask >>= 1
                    control["userInputFlag"] = mask & 0b1
                    mask >>= 1
                    control["disposalMethod"] = mask & 0b111
                    # 0 -   No disposal specified. The decoder is
                    #           not required to take any action.
                    #     1 -   Do not dispose. The graphic is to be left
                    #           in place.
                    #     2 -   Restore to background color. The area used by the
                    #           graphic must be restored to the background color.
                    #     3 -   Restore to previous. The decoder is required to
                    #           restore the area overwritten by the graphic with
                    #           what was there prior to rendering the graphic.
                    #  4-7 -    To be defined.
                    control["delayTime"] = file_object.read_uint16()
                    control["TransparentColorIndex"] = file_object.read_uint8()
                    terminator = file_object.read_uint8()
                    if terminator != 0:
                        LOGGER.w("terminator in block Graphic Control Extension is not 0")
                    image["control"] = control
                elif sub_tag == 0xFE:  # Comment Extension.
                    LOGGER.info("Comment Extension.")
                    if "comment" not in image:
                        image["comment"] = ""
                    while True:
                        tmp = file_object.read(1)
                        if tmp == '\0':
                            break
                        image["comment"] += tmp
                elif sub_tag == 0x01:  # plain text Extension
                    LOGGER.info("plain text Extension")
                    block_size = file_object.read_uint8()
                    if block_size != 12:
                        LOGGER.warning("block size is not 12 in plain text")
                    text = {"gridLeftPosition": file_object.read_uint16(), "gridTopPosition": file_object.read_uint16(),
                            "textGridWidth": file_object.read_uint16(), "textGridHeight": file_object.read_uint16(),
                            "characterCellWidth": file_object.read_uint8(),
                            "characterCellHeight": file_object.read_uint8(),
                            "textForegroundColorIndex": file_object.read_uint8(),
                            "textBackgroundColorIndex": file_object.read_uint8(), "data": ""}
                    while True:
                        tmp = file_object.read(1)
                        if tmp == '\0':
                            break
                        text["data"] += tmp
                    if "text" in image:
                        LOGGER.warning("text already in image")
                    image["text"] = text
                elif sub_tag == 0xFF:  # Application Extension.
                    LOGGER.info("Application Extension.")
                    block_size = file_object.read_uint8()
                    if block_size != 11:
                        LOGGER.warning("block size is not 11 in application extension")
                    application = {"identifier": file_object.read(8), "authenticationCode": file_object.read(3)}
                    data_size = file_object.read_uint8()
                    application["data"] = file_object.read(data_size)

                    if "application" in image:
                        LOGGER.warning("application Extension already in image")

                    image["application"] = application
                    terminator = file_object.read_uint8()
                    if terminator != 0:
                        LOGGER.warning("terminator is not 0 in Application Extension")

                else:
                    LOGGER.warning("unknown extension")
            else:  # DATA
                LOGGER.info("DATA")

                image["LZWMinimumCodeSize"] = tag

                image["data"] = []
                while True:
                    data_size = file_object.read_uint8()

                    if data_size == 0:
                        break
                    data = file_object.read(data_size)
                    image["data"].append(data)
                self.images.append(image)
                image = {}

    def intLZWTable(self,size):
        table = [0]*(2**size+2)
        for i in range(2**size):
            table[i] = [i]
        table[2**size] = "CC"
        table[2*size+1] = "EOI"
        return table

    def lzwdecode(self, data, lzw_size):
        output = []
        lzwtable = self.intLZWTable(lzw_size)
        code = data[0]
        output.append(code)
        for i in range(1, len(data)):
            code = data[i]

            if code < len(lzwtable):
                output += lzwtable[code]
                k = lzwtable[code][0]
                tmp = lzwtable[data[i-1]]
                tmp += [k]
                lzwtable.append(tmp)
            else:
                k = lzwtable[data[i-1]][0]
                out = lzwtable[data[i-1]] + [k]
                output += out
                lzwtable.append(out)
        return output


    # def detect(self):
    #     data = []
    #     for image in self.images:
    #         colorTable = self.globalColorTable
    #         if image["localColorTableFlag"] == 1:
    #             colorTable = image["localColorTable"]
    #         w = image["width"]
    #         h = image["height"]
    #         currentData = [[(0, 0, 0)] * w] * h
    #         lzwtable = self.intLZWTable(image["LZWMinimumCodeSize"])
    #         decoded = []
    #         code = image["data"][0]
    #         decoded.append(code)
    #         for i in range(1, len(image["data"])):
    #             code = image["data"][i]
    #             if code in lzwtable:
    #                 decoded += code
    #                 k = lzwtable[code]
    #                 lzwtable.append([image["data"][i-1],])



