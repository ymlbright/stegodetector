#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-02-02 10:29:36
# @Author  : yml_bright@163.com


import struct
from common.fileobject import FileObject
from common.logger import LOGGER, CustomLoggingLevel

class JPGDetector():

    detectSensitive = 1.0
    
    def __init__(self, fileObject):
        self.fileObject = fileObject
        self.huffmanTable = []
        self.quantizationTable = []
        self.tagMap = {
            '\xff\x00' :self.tag_none,
            '\xff\xc0' :self.tag_sof0,
            '\xff\xc1' :self.tag_sof,
            '\xff\xc2' :self.tag_sof,
            '\xff\xc3' :self.tag_sof,
            '\xff\xc4' :self.tag_dht,
            '\xff\xc5' :self.tag_sof,
            '\xff\xc6' :self.tag_sof,
            '\xff\xc7' :self.tag_sof,
            '\xff\xc8' :self.tag_jpeg,
            '\xff\xc9' :self.tag_sof,
            '\xff\xca' :self.tag_sof,
            '\xff\xcb' :self.tag_sof,
            '\xff\xcc' :self.tag_dac,
            '\xff\xcd' :self.tag_sof,
            '\xff\xce' :self.tag_sof,
            '\xff\xcf' :self.tag_sof,
            '\xff\xd0' :self.tag_rst,
            '\xff\xd1' :self.tag_rst,
            '\xff\xd2' :self.tag_rst,
            '\xff\xd3' :self.tag_rst,
            '\xff\xd4' :self.tag_rst,
            '\xff\xd5' :self.tag_rst,
            '\xff\xd6' :self.tag_rst,
            '\xff\xd7' :self.tag_rst,
            '\xff\xd8' :self.tag_soi,
            '\xff\xd9' :self.tag_eoi,
            '\xff\xda' :self.tag_sos,
            '\xff\xdb' :self.tag_dqt,
            '\xff\xdc' :self.tag_dnl,
            '\xff\xdd' :self.tag_dri,
            '\xff\xde' :self.tag_dhp,
            '\xff\xdf' :self.tag_exp,
            '\xff\xe0' :self.tag_app0,
            '\xff\xe1' :self.tag_app,
            '\xff\xe2' :self.tag_app,
            '\xff\xe3' :self.tag_app,
            '\xff\xe4' :self.tag_app,
            '\xff\xe5' :self.tag_app,
            '\xff\xe6' :self.tag_app,
            '\xff\xe7' :self.tag_app,
            '\xff\xe8' :self.tag_app,
            '\xff\xe9' :self.tag_app,
            '\xff\xea' :self.tag_app,
            '\xff\xeb' :self.tag_app,
            '\xff\xec' :self.tag_app,
            '\xff\xed' :self.tag_app,
            '\xff\xee' :self.tag_app,
            '\xff\xef' :self.tag_app,
            '\xff\xf0' :self.tag_jpg,
            '\xff\xf1' :self.tag_jpg,
            '\xff\xf2' :self.tag_jpg,
            '\xff\xf3' :self.tag_jpg,
            '\xff\xf4' :self.tag_jpg,
            '\xff\xf5' :self.tag_jpg,
            '\xff\xf6' :self.tag_jpg,
            '\xff\xf7' :self.tag_jpg,
            '\xff\xf8' :self.tag_jpg,
            '\xff\xf9' :self.tag_jpg,
            '\xff\xfa' :self.tag_jpg,
            '\xff\xfb' :self.tag_jpg,
            '\xff\xfc' :self.tag_jpg,
            '\xff\xfd' :self.tag_jpg,
            '\xff\xfe' :self.tag_com,
        }

    def start(self):
        if self.fileObject.read(2) == '\xff\xd8': # start of JPEG file
            pass
        else:
            LOGGER.error('JPEG file start mark 0xFFD8 check failed.')

    def tag_none(self, tag):
        # 0xFF00 means 0xFF in data
        pass

    def tag_com(self, tag):
        # 0xFFFE Comment
        data = []
        d = self.fileObject.read(1)
        while d != '\xff':
            data.append(d)
            d = self.fileObject.read(1)
        LOGGER.log(CustomLoggingLevel.STEGO_DATA, '[0x%x] %s'%(self.fileObject.cur(), ''.join(data)))
        return '\xff' + self.fileObject.read(1)

    def tag_app0(self, tag):
        # 0xFFE0 APP0
        length = self.fileObject.read_uint16()
        magic = self.fileObject.read(5)
        self.version = self.fileObject.read_uint16()
        self.fileObject.read(5)
        self.thumbnailX = self.fileObject.read_uint8()
        self.thumbnailY = self.fileObject.read_uint8()
        self.thumbnail = self.fileObject.read(length-16) # RGB pixel
        return self.find_tag('APP0')

    def tag_app(self, tag):
        # 0xFFE1~0xFFEE Application-specific
        length = self.fileObject.read_uint16()
        data = self.fileObject.read(length-2)
        return self.find_tag('APP%d'%(int(tag)-0xFFE0))

    def tag_jpg(self, tag):
        # 0xFFF0~0xFFFD JPGn extention reserve
        pass

    def tag_jpeg(self, tag):
        # 0xFFC8 JPEG extention reserve
        pass

    def tag_dhp(self, tag):
        # #FFDE Define hierarchical progression
        pass

    def tag_exp(self, tag):
        # 0xFFDF Expand reference image(s)
        pass

    def tag_dqt(self, tag):
        # 0xFFDB Define Quantization Table(s)
        pass

    def tag_sof0(self, tag):
        # 0xFFC0 Start Of Frame 
        length = self.fileObject.read_uint16()
        self.bitsPerPixel = self.fileObject.read_uint8()
        self.height = self.fileObject.read_uint16()
        self.width = self.fileObject.read_uint16()
        if self.fileObject.read(1) != '\x03':
            LOGGER.error('[0x%x] Color type must be YCrCb(0x03) in JFIF.'%self.fileObject.cur())
        self.comp = self.fileObject.read(9)
        return self.find_tag('SOF0')

    def tag_sof(self, tag):
        # 0xFFC1~0xFFC7 0xFFC9~0xFFCF Start Of Frame 
        pass

    def tag_dht(self, tag):
        # 0xFFC4 Define Huffman Table(s)
        length = self.fileObject.read_uint16()
        

    def tag_dnl(self, tag):
        # 0xFFDC Define number of lines
        pass

    def tag_dri(self, tag):
        # 0xFFDD Define Restart Interval
        pass

    def tag_sos(self, tag):
        # 0xFFDA Start Of Scan
        pass

    def tag_eoi(self, tag):
        # 0xFFD9 End Of Image
        pass

    def tag_dac(self, tag):
        # 0xFFCC Define arithmetic conditioning table
        pass

    def tag_rst(self, tag):
        # 0xFFD0~0xFFD7 Restart
        pass

    def tag_res(self, tag):
        # 0xFF02~0xFFBF Reserve
        pass

    def tag_soi(self, tag):
        # 0xFFD0 Start Of Image
        LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '[0x%x] A new file start tag found.'%self.fileObject.cur())

    def tag_unknown(self, tag):
        # unknown tag
        LOGGER.log(CustomLoggingLevel.IMAGE_INFO, '[0x%x] Unknown tag 0x%x found.'%(tag, self.fileObject.cur()))

    def find_tag(self, tagName):
        if self.fileObject.read(1) != '\xFF':
            curPos = '[0x%x]' % self.fileObject.cur()
            LOGGER.error('%s Can\'t find 0xFF in end of %s.'%(curPos, tagName))
            data = []
            d = self.fileObject.read(1)
            while d != '\xFF':
                data.append(d)
                d = self.fileObject.read(1)
            LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '%s %s'%(curPos, ''.join(data)))
        return '\xff' + self.fileObject.read(1)

    def detect(self):
        self.start()
        return ['','','']