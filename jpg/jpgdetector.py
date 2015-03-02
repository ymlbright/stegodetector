#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-02-02 10:29:36
# @Author  : yml_bright@163.com

import struct
from common.fileobject import FileObject
from common.logger import LOGGER, CustomLoggingLevel
from jpgenum import *
class JPGDetector():

    def __init__(self, fileObject):
        self.fileObject = fileObject
        self.version = 0
        self.channel = 3
        self.huffmanTable = {}
        self.huffmanTableCount = 0
        self.quantizationTable = {}
        self.colorQuantization = {}
        self.scanQuantization = {}
        self.scanFlag = False
        self.scanData = ''
        self.restartInterval = 0
        self.bitStreamStart = 0
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
            '\xff\xe1' :self.tag_app1,
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
            tag = self.fileObject.read(2)
            while self.scanFlag == False and tag != None:
                try:
                    tag = self.tagMap[tag](tag)
                except KeyError:
                    tag = self.tag_unknown(tag)
            LOGGER.log(CustomLoggingLevel.IMAGE_INFO, 'JPEG (ver %d.%d): %d*%dpx , channel: %d, fileLength: 0x%x b.' % 
                        (self.version>>8, self.version&0xff, self.width, self.height, self.channel, self.fileObject.size) )
        else:
            LOGGER.error('JPEG file start mark 0xFFD8 check failed.')

    def tag_none(self, tag):
        # 0xFF00 means 0xFF in scan data
        pass

    def tag_com(self, tag):
        # 0xFFFE Comment
        return self.reserve_tag()

    def tag_app0(self, tag):
        # 0xFFE0 APP0
        length = self.read_uint16()
        magic = self.fileObject.read(5)
        if magic != 'JFIF\x00':
            LOGGER.warning('[0x%x] Unbale to process magic %s in APP0.'%(self.fileObject.cur(), magic))
        self.version = self.read_uint16()
        self.fileObject.read(5)
        self.thumbnailX = self.fileObject.read_uint8()
        self.thumbnailY = self.fileObject.read_uint8()
        self.thumbnail = self.fileObject.read(length-16) # RGB pixel
        return self.find_tag('APP0')

    def tag_app1(self, tag):
        backCurPos = self.fileObject.cur()
        length = self.read_uint16()
        magic = self.fileObject.read(6)
        if magic != 'Exif\x00\x00':
            LOGGER.warning('[0x%x] Unbale to process magic %s in APP1.'%(self.fileObject.cur(), magic))
        self.read_tiff(length - 8, 'Exif')
        self.fileObject.change_cur(backCurPos+length)
        return self.find_tag('APP1')

    def tag_app(self, tag):
        # 0xFFE1~0xFFEE Application-specific
        appID = int(tag)-0xFFE0
        length = self.read_uint16() - 2
        data = self.fileObject.read(length)
        if not appID in [1, 2, 13 ,14]:
            LOGGER.log(CustomLoggingLevel.OTHER_DATA, '[0x%x] Tag APP%d found.'%(self.fileObject.cur() - length, appID))
        else:
            LOGGER.log(CustomLoggingLevel.OTHER_DATA, '[0x%x] Tag APP%d found, this tag usually not used in file.'%(self.fileObject.cur() - length, appID))
        return self.find_tag('APP%d'%appID)

    def tag_jpg(self, tag):
        # 0xFFF0~0xFFFD JPGn extention reserve
        return self.reserve_tag()

    def tag_jpeg(self, tag):
        # 0xFFC8 JPEG extention reserve
        return self.reserve_tag()

    def tag_dhp(self, tag):
        # #FFDE Define hierarchical progression
        self.unsupported_tag('0xffde', 'DHP')

    def tag_exp(self, tag):
        # 0xFFDF Expand reference image(s)
        self.unsupported_tag('0xffdf', 'EXP')

    def tag_dqt(self, tag):
        # 0xFFDB Define Quantization Table(s)
        length = self.read_uint16() - 2
        while length>0:
            firstBit = self.fileObject.read_uint8()
            tableID = firstBit & 0xf
            tableLength = (firstBit >> 4 + 1) * 64
            self.quantizationTable[tableID] = self.fileObject.read(tableLength)
            length -= tableLength + 1
        return self.find_tag('DQT')

    def tag_sof0(self, tag):
        # 0xFFC0 Start Of Frame 
        length = self.read_uint16()
        self.encodeType = 'sof0'
        self.bitsPerPixel = self.fileObject.read_uint8()
        self.height = self.read_uint16()
        self.width = self.read_uint16()
        if self.fileObject.read(1) != '\x03':
            LOGGER.error('[0x%x] Color type must be YCrCb(0x03) in JFIF.'%self.fileObject.cur())
        comp = self.fileObject.read(9)
        for i in range(3):
            self.colorQuantization[ord(comp[3*i])] = {'Horz' :ord(comp[3*i+1])>>4, 'Vert' :ord(comp[3*i+1])&0xf, 'TableID' :ord(comp[3*i+2])}
        return self.find_tag('SOF0')

    def tag_sof(self, tag):
        # 0xFFC1~0xFFC7 0xFFC9~0xFFCF Start Of Frame 
        length = self.read_uint16()
        self.encodeType = 'sofx'
        self.bitsPerPixel = self.fileObject.read_uint8()
        self.height = self.read_uint16()
        self.width = self.read_uint16()
        if self.fileObject.read(1) != '\x03':
            LOGGER.error('[0x%x] Color type must be YCrCb(0x03) in JFIF.'%self.fileObject.cur())
        comp = self.fileObject.read(9)
        return self.find_tag('SOFx')

    def tag_dht(self, tag):
        # 0xFFC4 Define Huffman Table(s)
        length = self.read_uint16() - 2
        while length>0:
            tableIDByte = self.fileObject.read_uint8()
            tableID = (tableIDByte>>4)+(tableIDByte&0xf)
            if tableID<4:
                length -= self.huffmantree_decode(tableID)+1
            else:
                LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '[0x%x] Unknown part of huffman table'%(self.fileObject.cur()-1))
                self.fileObject.read(length) # skip unknown part
                break
        return self.find_tag('DHT')

    def huffmantree_decode(self, tableID):
        bitCount = []
        powerLength = 0
        self.huffmanTableCount += 1
        if self.huffmanTableCount>4:
            self.log(CustomLoggingLevel.IMAGE_INFO, 'Extra huffman table(DHT) found in jpg file.')
        for i in range(16):
            bitCount.append(ord(self.fileObject.read(1)))
            powerLength += bitCount[i]
        bitPower = self.fileObject.read(powerLength)
        huffmanTree = {}
        powerPos = 0
        lastBit = 0
        for i in range(16):
            if bitCount[i] == 0:
                if lastBit < 2**i:
                    lastBit = lastBit << 1
                continue
            while bitCount[i]>0:
                if i>1 and lastBit < 2**i:
                    lastBit = lastBit << 1
                huffmanTree[lastBit] = bitPower[powerPos]
                lastBit += 1
                powerPos += 1
                bitCount[i] -= 1
        self.huffmanTable[tableID] = huffmanTree
        return powerLength+16

    def tag_dnl(self, tag):
        # 0xFFDC Define number of lines
        self.unsupported_tag('0xffdc', 'DNL')

    def tag_dri(self, tag):
        # 0xFFDD Define Restart Interval
        length = self.read_uint16() - 2
        curPos = '[0x%x]' % self.fileObject.cur()
        self.restartInterval = self.read_uint16()
        if length != 2:
            LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '%s> %s'%(curPos, self.fileObject.read(length-2)))
        return self.find_tag('DRI')

    def tag_sos(self, tag):
        # 0xFFDA Start Of Scan
        self.scanFlag = True
        length = self.read_uint16() - 2
        if self.fileObject.read(1) != '\x03':
            LOGGER.error('[0x%x] Color type must be YCrCb(0x03) in JFIF.'%self.fileObject.cur())
        comp = self.fileObject.read(3)
        for i in range(3):
            self.scanQuantization[i] = {'AC' :ord(comp[i])>>4, 'DC' :ord(comp[i])&0xf}
        self.scanSs = self.fileObject.read(1)
        self.scanSe = self.fileObject.read(1)
        self.scanAh = ord(self.fileObject.read(1))
        self.scanAl = self.scanAh & 0xf
        self.scanAh = self.scanAh >> 4

    def tag_eoi(self, tag):
        # 0xFFD9 End Of Image
        self.scanFlag = False

    def tag_dac(self, tag):
        # 0xFFCC Define arithmetic conditioning table
        self.unsupported_tag('0xffcc', 'DAC')

    def tag_rst(self, tag):
        # 0xFFD0~0xFFD7 Restart
        if self.scanFlag == False:
            self.unexpected_tag(tag, 'RST')
        else:
            pass

    def tag_res(self, tag):
        # 0xFF02~0xFFBF Reserve
        return self.reserve_tag()

    def tag_soi(self, tag):
        # 0xFFD0 Start Of Image
        LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '[0x%x] A new file start tag found.'%self.fileObject.cur())

    def tag_unknown(self, tag):
        # unknown tag
        LOGGER.log(CustomLoggingLevel.IMAGE_INFO, '[0x%x] Unknown tag 0x%s found.'%(self.fileObject.cur(), tag.encode('hex')))

    def read_uint16(self, start=-1):
        high = ord(self.fileObject.read(1, start))<<8
        low = ord(self.fileObject.read(1))
        return high + low

    def read_uint32(self, start=-1):
        bit1 = ord(self.fileObject.read(1, start))<<24
        bit2 = ord(self.fileObject.read(1))<<16
        bit3 = ord(self.fileObject.read(1))<<8
        bit4 = ord(self.fileObject.read(1))
        return bit1 + bit2 + bit3 + bit4

    def read_tiff(self, length, tagName):
        tiffStartPos = self.fileObject.cur()
        if self.fileObject.read(2) == 'II':
            p_read_uint16 = self.fileObject.read_uint16
            p_read_uint32 = self.fileObject.read_uint32
        else:
            p_read_uint16 = self.read_uint16
            p_read_uint32 = self.read_uint32
        if p_read_uint16() != 0x2a:
            LOGGER.warning('[0x%x] TIFF data format magic check failed.'%tiffStartPos)
        dirEntryPos = p_read_uint32()
        self.read_tiff_ifd(tiffStartPos, p_read_uint16, p_read_uint32, dirEntryPos, tagName)

    def read_tiff_ifd(self, tiffStartPos, p_read_uint16, p_read_uint32, dirEntryPos, tagName):
        dirCount = 0
        while dirEntryPos != 0:
            entryCount = p_read_uint16(tiffStartPos+dirEntryPos)
            LOGGER.log(CustomLoggingLevel.IMAGE_DEBUG, '[%s] Tiff data start at 0x%x, directory index: %d, start at: 0x%x, entry count: %d.'%(tagName, tiffStartPos, dirCount,dirEntryPos, entryCount))
            for i in range(entryCount):
                try:
                    dirTag = p_read_uint16(tiffStartPos+dirEntryPos+2+12*i)
                    dataFormat = p_read_uint16()
                    nComponent = p_read_uint32()
                    dataLength = nComponent*tiffEnumDataTypeLength[dataFormat]
                    if dataLength > 4:
                        dataStartPos = p_read_uint32()
                        data = self.fileObject.read(dataLength, tiffStartPos+dataStartPos)
                    else:
                        data = self.fileObject.read(4)

                    if dirTag == 0x8769:
                        self.read_tiff_ifd(tiffStartPos, p_read_uint16, p_read_uint32, 
                                            p_read_uint32(tiffStartPos+dirEntryPos+10+12*i),
                                            'SubExif')
                    elif dirTag == 0xa005:
                        self.read_tiff_ifd(tiffStartPos, p_read_uint16, p_read_uint32, 
                                            p_read_uint32(tiffStartPos+dirEntryPos+10+12*i),
                                            'ExifInteroperability')

                    if dataFormat == 2:
                        LOGGER.log(CustomLoggingLevel.IMAGE_INFO, '[%s - %s](string)> %s'%(tagName, exifEnumTag[dirTag], data.replace('\x00', '')))
                    else:
                        LOGGER.log(CustomLoggingLevel.IMAGE_INFO, '[%s - %s](%s)> Hex:%s'%(tagName, exifEnumTag[dirTag], tiffEnumDataType[dataFormat], data.encode('hex')))
                except KeyError or IndexError:
                    LOGGER.error('[0x%x] Unable to decode dataformat or entrytag in tiff data, tagName: %s, dirTag: 0x%x, dataFormat: 0x%x, directory: %d/%d.'%(self.fileObject.cur(), tagName, dirTag, dataFormat, i, entryCount))
            dirCount += 1
            dirEntryPos = p_read_uint32(tiffStartPos+dirEntryPos+2+12*entryCount)

    def find_tag(self, tagName):
        if self.fileObject.read(1) != '\xFF':
            curPos = '[0x%x]' % self.fileObject.cur()
            LOGGER.error('%s Can\'t find 0xFF in end of %s.'%(curPos, tagName))
            data = []
            d = self.fileObject.read(1)
            while d != '\xFF':
                data.append(d)
                d = self.fileObject.read(1)
            LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '%s> %s'%(curPos, ''.join(data)))
        return '\xff' + self.fileObject.read(1)

    def reserve_tag(self):
        curPos = '[0x%x]' % self.fileObject.cur()
        length = self.read_uint16() - 2
        data = self.fileObject.read(length)
        LOGGER.log(CustomLoggingLevel.STEGO_DATA, '%s> %s'%(curPos, data))
        return self.find_tag('RESERVED TAG')

    def unsupported_tag(self, tag, tagName):
        self.warning('[0x%x] tag %s(%s) is unsupported.'%(self.fileObject.cur(), tagName, tag.encode('hex')))
        length = self.read_uint16() - 2
        self.fileObject.read(length)
        return self.find_tag(tagName)

    def unexpected_tag(self, tag, tagName):
        length = self.read_uint16()
        LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '[0x%x] tag %s(%s) appears unexpected, length: %d.'%(self.fileObject.cur()-2, tagName, tag.encode('hex'), length))
        self.fileObject.read(length-2)

    def showextradata(self, data, location):
        length = len(data)
        if length > 128:
            tmpFileObject = FileObject(data)
            LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '[0x%x] length: %x, type: %s'%(location, length, tmpFileObject.type()) )
        else:
            LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '[0x%x] > %s'%(location, data) )

    # decode scan data of sof0
    def decode_scandata(self):
        # init decode varible
        huffmanTableY_DC = self.huffmanTable[self.scanQuantization[0]['DC']]
        huffmanTableY_AC = self.huffmanTable[2+self.scanQuantization[0]['AC']]
        huffmanTableCr_DC = self.huffmanTable[self.scanQuantization[1]['DC']]
        huffmanTableCr_AC = self.huffmanTable[2+self.scanQuantization[1]['AC']]
        huffmanTableCb_DC = self.huffmanTable[self.scanQuantization[2]['DC']]
        huffmanTableCb_AC = self.huffmanTable[2+self.scanQuantization[2]['AC']]
        quantizationTableY = self.quantizationTable[self.colorQuantization[1]['TableID']]
        quantizationTableCr = self.quantizationTable[self.colorQuantization[2]['TableID']]
        quantizationTableCb = self.quantizationTable[self.colorQuantization[3]['TableID']]
        horzY = self.colorQuantization[1]['Horz']
        horzCr = self.colorQuantization[2]['Horz']
        horzCb = self.colorQuantization[3]['Horz']
        vertY = self.colorQuantization[1]['Vert'] 
        vertCr = self.colorQuantization[2]['Vert']
        vertCb = self.colorQuantization[3]['Vert']
        hmax = max([horzY, horzCr, horzCb])
        vmax = max([vertY, vertCr, vertCb])
        self.baseY = 0
        self.baseCr = 0
        self.BaseCb = 0
        mcuData = []

        with open('scandata.bin','wb') as f:
            f.write(self.fileObject.read(self.fileObject.size - self.fileObject.cur()))

        # try to use C++ to decode ....

        # self.streamBuffer = []
        # LOGGER.log(CustomLoggingLevel.IMAGE_DEBUG, 'Start to decode scan data.')
        # while self.scanFlag == True:
        #     # read Y data
        #     d = 0
        #     for i in range(1,17):
        #         if self.read_bitstream(i) in huffmanTableY_DC.keys():
        #             d = self.read_bitstream(i, False)
        #             break
        #     # read DC part
        #     dataLength = ord(huffmanTableY_DC[d])&0xf
        #     d = self.read_bitstream(dataLength, False) # need to decode
        #     if self.baseY == 0:
        #         self.baseY = d
        #     else:
        #         self.baseY += d
        #     dataY = [self.baseY for i in range(64)]
        #     # read AC part
        #     dataYIndex = 0
        #     for i in range(63):
        #         dataYIndex += 1
        #         for i in range(1,17):
        #             if self.read_bitstream(i) in huffmanTableY_AC.keys():
        #                 d = self.read_bitstream(i, False)
        #                 break
        #         dataLength = ord(huffmanTableY_DC[d])&0xf
        #         if dataLength == 0:
        #             break
        #         else:
        #             d = self.read_bitstream(dataLength, False) # need to decode
        #             skipLength = 0
        #             dataYIndex += skipLength
        #             dataY[dataYIndex] = self.baseY + d
        #     mcuData.append([dataY, 0 , 0])

        # return ''

    # def read_bitstream(self, bitLength, checkFlag = True): 
    #     if bitLength == 0:
    #         return 0
    #     while self.bitStreamStart > 7:
    #         self.streamBuffer.remove(self.streamBuffer[0])
    #         self.bitStreamStart -= 8
    #     expendLength = len(self.streamBuffer)*8 - self.bitStreamStart - bitLength
    #     while expendLength < 0:
    #         d = self.fileObject.read(1)
    #         if d == '\xff':
    #             n = self.fileObject.read(1)
    #             tag = d + n
    #             if n == '\x00':
    #                 self.streamBuffer.append(ord(d))
    #                 expendLength += 8
    #             elif n == '\xd9':
    #                 self.tag_eoi(tag)
    #             elif '\xd0' <= n <= '\xf7':
    #                 if checkFlag == False:
    #                     self.baseY = 0
    #                     self.baseCr = 0
    #                     self.BaseCb = 0
    #                 # self.tag_rst(tag)
    #             else:
    #                 self.unexpected_tag(tag, '?')
    #         else:
    #             self.streamBuffer.append(ord(d))
    #             expendLength += 8
    #     bitNewStart = self.bitStreamStart + bitLength
    #     if self.bitStreamStart + bitLength > 8:
    #         ret = self.streamBuffer[0] & myBitStreamMaskR[8-self.bitStreamStart]
    #         bitLength -= 8 - self.bitStreamStart
    #     else:
    #         ret = ((self.streamBuffer[0] & myBitStreamMaskL[self.bitStreamStart+bitLength]) >> (8 - self.bitStreamStart - bitLength)) & myBitStreamMaskR[bitLength]
    #         bitLength = 0
    #     streamIndex = 1
    #     while bitLength >= 8:
    #         ret = ret << 8
    #         ret += self.streamBuffer[streamIndex]
    #         streamIndex += 1
    #         bitLength -= 8
    #     if bitLength > 0 :
    #         ret = ret << bitLength
    #         ret += self.streamBuffer[streamIndex] & myBitStreamMaskL[bitLength]
    #     if checkFlag == False:
    #         self.bitStreamStart = bitNewStart
    #     return ret

    # def clean_bitstream_remainder(self):
    #     remainder = self.streamBuffer[0] & myBitStreamMaskR[8-self.bitStreamStart]
    #     if remainder != 0 and remainder != myBitStreamMaskR[8-self.bitStreamStart]:
    #         LOGGER.log(CustomLoggingLevel.EXTRA_DATA, 'Scandata remainder is not equal, is %s'%bin(remainder))
    #     self.streamBuffer.remove(self.streamBuffer[0])
    #     self.bitStreamStart = 0

    def read_scandata(self):
        curPos = self.fileObject.cur()
        LOGGER.log(CustomLoggingLevel.IMAGE_DEBUG, 'Start to read scan data.')
        scanDataLength = 0
        d = self.fileObject.read(1)
        while self.scanFlag == True:
            if d == '\xff':
                n = self.fileObject.read(1)
                if n == '\xd9':
                    self.tag_eoi('\xff\xd9')
                else:
                    scanDataLength += 2
            else:
                scanDataLength += 1
            d = self.fileObject.read(1)
        LOGGER.log(CustomLoggingLevel.IMAGE_INFO, 'Scan data start at 0x%x, length: 0x%x.'%(curPos, scanDataLength))

    def detect(self):
        self.start()
        rowData = ''
        if self.encodeType == 'sof0':
            rowData = self.decode_scandata()
        else:
            self.read_scandata()

        for d in self.fileObject.redundancy():
            self.showextradata(d['data'], d['start'])
        return rowData, self.channel*8, self.channel

# how does RST tag works?
# how to decode sof0 scan data
