# -*- coding: utf-8 -*-
# @Date    : 2015-01-27 23:24:08
# @Author  : xieshufang76@gmail.com

# http://www.w3.org/Graphics/GIF/spec-gif89a.txt


from common.logger import LOGGER, CustomLoggingLevel
from common.rowdata import RowData
from common.fileobject import FileObject

import logging


class Image():
    def __init__(self):
        pass


class CodeReader():
    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.mask = 1

    def read(self, length):
        ans = 0
        for i in xrange(length):
            tmp = 0 if ord(self.data[self.pos]) & self.mask == 0 else 1
            ans += tmp * (2 ** i)
            self.mask *= 2
            if self.mask == 2 ** 8:
                self.mask = 1
                self.pos += 1
        return ans


class GIFDetector():
    def __init__(self, file_object):
        LOGGER.addHandler(logging.StreamHandler())
        self.fileObject = file_object
        if file_object.read(3) != 'GIF':
            LOGGER.error("File is not a gif file")
        self.type = "GIF"
        self.version = file_object.read(3)
        if self.version != '87a' and self.version != '89a':
            LOGGER.log(CustomLoggingLevel.OTHER_DATA, "Invalid version")
        else:
            LOGGER.log(CustomLoggingLevel.BASIC_DEBUG, "version is " + self.version)
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
        # self.globalColorTable = [[0, 0, 0]] * (2 ** (self.pixel + 1))
        if self.globalColorTableFlag:
            self.globalColorTable = [[0, 0, 0] for _ in range(2 ** (self.pixel + 1))]
        else:
            self.globalColorTable = []

        LOGGER.info("global table size is %d" % len(self.globalColorTable))

        for i in range(len(self.globalColorTable)):

            for j in range(3):  # 0 red 1 green 2 blue
                self.globalColorTable[i][j] = file_object.read_uint8()
        self.images = []
        image = {}
        while True:
            tag = file_object.read_uint8()

            if tag == 0x3b:

                break  # end of gif

            if tag == 0x2c:  # start of a image descriptor
                # LOGGER.info("image descriptor")
                image["xOffset"] = file_object.read_uint16()
                image["yOffset"] = file_object.read_uint16()

                image["width"] = file_object.read_uint16()
                image["height"] = file_object.read_uint16()

                if image["xOffset"] + image["width"] > self.logicScreenWidth or \
                                        image["yOffset"] + image["height"] > self.logicScreenHeight:
                    LOGGER.log(CustomLoggingLevel.OTHER_DATA,
                               "some part out of logic screen at image %d" % len(self.images) + 1)

                mask = file_object.read_uint8()
                image["pixel"] = mask & 0b111
                mask >>= 3
                image["reserved"] = mask & 0b11
                if image["reserved"] != 0:
                    LOGGER.log(CustomLoggingLevel.OTHER_DATA,
                               "[0x%x] reserved data should be 0" % self.fileObject.cur())
                mask >>= 2
                image["sortFlag"] = mask & 0b1
                mask >>= 1
                image["interlaceFlag"] = mask & 0b1
                mask >>= 1
                image["localColorTableFlag"] = mask & 0b1
                if image["localColorTableFlag"]:
                    image["localColorTable"] = [[0, 0, 0] for _ in xrange((2 ** (image["pixel"] + 1)))]
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
                    # not required to take any action.
                    # 1 -   Do not dispose. The graphic is to be left
                    # in place.
                    # 2 -   Restore to background color. The area used by the
                    #           graphic must be restored to the background color.
                    #     3 -   Restore to previous. The decoder is required to
                    #           restore the area overwritten by the graphic with
                    #           what was there prior to rendering the graphic.
                    #  4-7 -    To be defined.
                    control["delayTime"] = file_object.read_uint16()
                    control["TransparentColorIndex"] = file_object.read_uint8()
                    terminator = file_object.read_uint8()
                    if terminator != 0:
                        LOGGER.log(CustomLoggingLevel.OTHER_DATA,
                                   "[0x%x] terminator in block Graphic Control Extension is not 0"
                                   % self.fileObject.cur())
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
                    LOGGER.log(CustomLoggingLevel.ASCII_DATA, image["comment"])
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
                        LOGGER.log(CustomLoggingLevel.OTHER_DATA, "text already in image")
                    image["text"] = text
                    LOGGER.log(CustomLoggingLevel.ASCII_DATA, image["text"])
                elif sub_tag == 0xFF:  # Application Extension.
                    LOGGER.info("Application Extension.")
                    block_size = file_object.read_uint8()
                    if block_size != 11:
                        LOGGER.log(CustomLoggingLevel.OTHER_DATA,
                                   "[0x%x] block size is not 11 in application extension" % self.fileObject.cur())
                    application = {"identifier": file_object.read(8), "authenticationCode": file_object.read(3)}
                    data_size = file_object.read_uint8()
                    application["data"] = file_object.read(data_size)

                    if "application" in image:
                        LOGGER.log(CustomLoggingLevel.OTHER_DATA, "application Extension already in image")

                    image["application"] = application
                    terminator = file_object.read_uint8()
                    if terminator != 0:
                        LOGGER.log(CustomLoggingLevel.OTHER_DATA, "terminator is not 0 in Application Extension")
                else:
                    LOGGER.log(CustomLoggingLevel.OTHER_DATA, "[0x%x] unknown extension at" % self.fileObject.cur())
            else:  # DATA
                # LOGGER.info("DATA")

                image["LZWMinimumCodeSize"] = tag

                image["data"] = []
                while True:
                    data_size = file_object.read_uint8()

                    if data_size == 0:
                        break
                    data = file_object.read(data_size)
                    image["data"] += data
                self.images.append(image)
                if len(image["data"]) != image["width"] * image["height"]:
                    LOGGER.log(CustomLoggingLevel.OTHER_DATA, "image %d has wrong width or height " % len(self.images))
                image = {}

    @staticmethod
    def build_lzw_table(size):
        table = dict((i, [i]) for i in xrange(size))
        table[size] = size  # cc
        table[size + 1] = size + 1  # end
        return table

    def lzw_decode(self, data, lzw_size):
        # http://stackoverflow.com/questions/6834388/basic-lzw-compression-help-in-python

        dictionary = self.build_lzw_table(2 ** lzw_size)
        reader = CodeReader(data)
        code_length = lzw_size + 1
        result = []
        pre_code = 0
        clear_code = 2 ** lzw_size
        end_code = clear_code + 1
        while True:
            if len(dictionary) == 2 ** code_length and code_length < 12:
                code_length += 1
                # print "new code_length ", code_length
            code = reader.read(code_length)
            if code == clear_code:  # cc
                # LOGGER.debug("clear code")
                dictionary = self.build_lzw_table(2 ** lzw_size)
                code_length = lzw_size + 1
            elif code == end_code:  # end
                # LOGGER.debug("end code find")
                break
            elif code in dictionary:
                result += dictionary[code]
                if pre_code != clear_code and pre_code != end_code:
                    k = dictionary[code][0]
                    dictionary[len(dictionary)] = dictionary[pre_code] + [k]
            else:
                k = dictionary[pre_code][0]
                tmp = dictionary[pre_code][:]
                tmp.append(k)
                result += tmp
                dictionary[len(dictionary)] = tmp
            pre_code = code
        return result

    def get_images(self):
        result = []
        for image in self.images:
            print len(image["data"])

            color_table = self.globalColorTable
            if "localColorTableFlag" in image and image["localColorTableFlag"] == 1:
                color_table = image["localColorTable"]
            data = self.lzw_decode(image["data"], image["LZWMinimumCodeSize"])
            w = image["width"]
            h = image["height"]
            cur = Image()
            cur.w = w
            cur.h = h
            cur.data = [color_table[i] for i in data]
            result.append(cur)
        return result

    def detect(self):
        for d in self.fileObject.redundancy():
            self.showextradata(d['data'], d['start'])
        return [RowData(image.data, 3, image.w, image.h) for image in self.get_images()]

    def showextradata(self, data, location):
        if len(data) > 128:
            tmpFileObject = FileObject(data)
            LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '[0x%x] %s' % (location, tmpFileObject.type()) )
        else:
            LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '[0x%x] > %s' % (location, data) )
