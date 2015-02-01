# -*- coding: utf-8 -*-
# @Date    : 2015-01-27 23:24:08
# @Author  : xieshufang76@gmail.com

# http://www.w3.org/Graphics/GIF/spec-gif89a.txt

import struct
from common.logger import LOGGER, CustomLoggingLevel


class GIFDetector():
    def __init__(self, file_object):
        self.fileObject = file_object
        if file_object.read(3) != 'GIF':
            LOGGER.error("File is not a gif file")
        self.type = "GIF"
        self.version = file_object.read(3)
        if self.version != '37a' or self.version != '39a':
            LOGGER.error("Invalid version")
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
        for i in range(len(self.globalColorTable)):
            for j in range(3):  # 0 red 1 green 2 blue
                self.globalColorTable[i][j] = file_object.read_uint8()
        self.images = []
        self.control = []
        while True:
            tag = file_object.read_uint8()
            if tag == 59:
                break  # end of gif

            if tag == 0b00101100:  # start of a image
                image = {}
                image.xOffset = file_object.read_uint16()
                image.yOffset = file_object.read_uint16()
                image.width = file_object.read_uint16()
                mask = file_object.read_uint8()
                image.pixel = mask & 0b111
                mask >>= 3
                image.reserved = mask & 0b11
                if image.reserved != 0:
                    pass  # TODO show warning
                mask >>= 2
                image.sortFlag = mask & 0b1
                mask >>= 1
                image.interlaceFlag = mask & 0b1
                mask >>= 1
                image.localColorTableFlag = mask & 0b1
                if image.localColorTableFlag:
                    image.localColorTable = [[0, 0, 0]] * (2 ** (image.pixel + 1))
                    for i in range(len(image.localColorTable)):
                        for j in range(3):  # 0 red 1 green 2 blue
                            image.localColorTable[i][j] = file_object.read_uint8()
                self.images.append(image)

            elif tag == 0x21:  # Graphic Control Extension.
                if self.version != "89a":
                    LOGGER.warning("not version 89a but has extension segment.")
                sub_tag = file_object.read_uint8()
                if sub_tag == 0xF9:  # Graphic Control Extension.
                    block_size = file_object.read_uint8()
                    if block_size != 4:
                        LOGGER.warning("block size is not 4 in Graphic Control Extension")
                    control = {}
                    mask = file_object.read_uint8()
                    control.transparentFlag = mask & 0b1
                    mask >>= 1
                    control.userInputFlag = mask & 0b1
                    mask >>= 1
                    control.disposalMethod = mask & 0b111
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
                    control.delayTime = file_object.read_uint8()
                    control.TransparentColorIndex = file_object.read_uint8()
                    terminator = file_object.read_uint8()
                    if terminator != 0:
                        LOGGER.w("terminator in block Graphic Control Extension is not 0")
                    self.control.append(control)
                elif sub_tag == 0xFE: # Comment Extension.
                    pass
                elif sub_tag == 0x01: # plain text Extension
                    pass
                elif sub_tag == 0xFF: # Application Extension.
                    pass
                else:
                    LOGGER.warning("unknown extension")
            else:  # TODO　analysis image data
                pass
