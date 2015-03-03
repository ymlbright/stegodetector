#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-01-27 23:24:08
# @Author  : yml_bright@163.com

import struct
from common.fileobject import FileObject
from common.logger import LOGGER, CustomLoggingLevel
from common.rowdata import RowData
class BMPDetector():

    detectSensitive = 1.0

    def __init__(self, fileObject):
        self.fileObject = fileObject

    def start(self):
        self.version = struct.unpack('h',self.fileObject.read(2))[0]
        if self.version == 0:
            # ver 1
            # read file header
            self.version = 1
            self.width, self.height, self.rowDataLength = struct.unpack('3h',self.fileObject.read(6))
            self.channel = ord(struct.unpack('b',self.fileObject.read(1))[0])
            self.bitsPerPixel = ord(struct.unpack('b',self.fileObject.read(1))[0])
            self.headerLength = 10

        elif self.version == 0x4D42:
            # ver 2  3  4
            # read file header
            self.length = struct.unpack('i',self.fileObject.read(4))[0]
            if self.fileObject.read(4) != '\x00\x00\x00\x00': # reserved always 0
                LOGGER.log(CustomLoggingLevel.OTHER_DATA, '[0x%x] File header reserved options is not 0'%(self.fileObject.cur()-4))
            bitmapOffset = struct.unpack('i',self.fileObject.read(4))[0]

            # read bitmap header
            bitmapHeaderLength = struct.unpack('l',self.fileObject.read(4))[0]
            
            if bitmapHeaderLength == 12:
                # ver 2
                self.version = 2
                self.width, self.height, self.channel, self.bitsPerPixel = struct.unpack('4h',self.fileObject.read(8))
                self.headerLength = 26
            elif bitmapHeaderLength == 40:
                # ver 3
                self.version = 3
                self.width, self.height, self.channel, self.bitsPerPixel = struct.unpack('2l2h',self.fileObject.read(12))
                self.compressionMethod, self.bitmapLength = struct.unpack('2L',self.fileObject.read(8))
                self.fileObject.read(16) # skip useless header
                self.headerLength = 53
            elif bitmapHeaderLength == 108:
                # ver 4
                self.version = 4
            else:
                LOGGER.error('[0x%x] Unknown BMP file version.'%(self.fileObject.cur()-4))

            if self.version != 0x4D42:
                # calculate number of entries
                if self.bitsPerPixel < 24:
                    self.numberOfEntries = 1 << self.bitsPerPixel
                else:
                    self.numberOfEntries = 0

                # read color palette
                self.colorPalette = []
                if self.version ==  3 and self.compressionMethod == 3:
                    self.fileObject.read(12*self.numberOfEntries)
                else:
                    for i in range(self.numberOfEntries):
                        self.headerLength += 4
                        t = self.fileObject.read(4)
                        self.colorPalette.append(t[2]+t[1]+t[0]+t[3])
                        if t[3] != '\x00':
                            LOGGER.log(CustomLoggingLevel.OTHER_DATA, '[0x%x] Color palette reserved option(alpha channel) is not 0, is 0x%x!'%(self.fileObject.cur()-4, ord(t[3])))
        else:
            LOGGER.error('Magic value BM check failed.')

        self.padding = self.width * self.bitsPerPixel % 32
        if self.padding != 0:
            self.padding = 32 - self.padding 
        self.rowDataLength = (self.width*self.bitsPerPixel+self.padding)*self.height/8
        LOGGER.log(CustomLoggingLevel.IMAGE_INFO, 'BMP(ver %d): %d*%dpx , channel: %d, fileLength: 0x%x(0x%x) b, headerLength: %d b, rowDataLength: %d b' % 
                    (self.version, self.width, self.height, self.channel, self.fileObject.size, self.headerLength+self.rowDataLength, self.headerLength, self.rowDataLength) )

        if self.channel != 1:
            LOGGER.log(CustomLoggingLevel.IMAGE_INFO, 'Warning: bmpfile channel is NOT 1!')

    # read bitmap for  ver 1
    def rowdata_ver1(self):
        if self.fileObject.size - self.rowDataLength - 10 > 10*(1 - detectSensitive):
            LOGGER.log(CustomLoggingLevel.EXTRA_DATA, 'Some extra data may in end of the file.')
        LOGGER.error('BMP file version 1 is not surported.')

    # read bitmap for  ver 4
    def rowdata_ver4(self):
        LOGGER.error('BMP file version 4 is not surported.')

    # read bitmap for  ver 2 and ver 3
    def rowdata_ver23(self):
        rowData = []
        if self.compressionMethod != 0:
            # decompress bitmap data according to compression method
            if self.bitmapLength == 0:
                LOGGER.warning('BitmapLength shouldn\'t be 0 in bitmap header! There may have some extra data in end of the file.')
                tdata = self.fileObject.read(self.fileObject.size - self.headerLength)
            else:
                tdata = self.fileObject.read(self.bitmapLength)
            # decompress
            data = []
            if self.compressionMethod == 1:
                specialFlag = -1
                for i in range(len(tdata)):
                    if specialFlag < 0:
                        if specialFlag == -1:
                            if tdata[i] == '\x00':
                                pass # end of line
                            elif tdata == '\x01':
                                break # end of RLE data
                            elif tdata[i] == '\x02':
                                data.append('\x00'*(ord(tdata[i+1])+self.width*ord(tdata[i+2]))*self.bitsPerPixel/8)
                            else:
                                specialFlag = ord(tdata[i]) + 1
                        specialFlag -= 1
                        if specialFlag == -3:
                            specialFlag = 0
                    elif specialFlag == 0:
                        if tdata[i] == '\x00':
                            specialFlag = -1
                    elif specialFlag > 1:
                        data.append(tdata[i])
                        specialFlag -= 1
                    else:
                        specialFlag -= 1
                if i < len(tdata) - 1:
                    self.showextradata(tdata[i:len(tdata)-1], self.headerLength + i)
                data = ''.join(data)
            elif self.compressionMethod == 2:
                LOGGER.error('Compress method RLE4 of BMP file version 3 is not surported.')
                return
            elif self.compressionMethod == 3:
                LOGGER.error('Compress method using RGB mask of BMP file version 3 is not surported.')
                return
        else:
            data = self.fileObject.read(self.rowDataLength)

        if self.compressionMethod ==0 and self.bitmapLength !=0:
            LOGGER.warning('BitmapLength should be 0 in bitmap header! Image pixel may be processed with wrong compress method!')
        if self.bitsPerPixel in [1, 4, 8, 24, 32]:
            # return row data from stream 
            if self.bitsPerPixel == 24:
                self.channel = 3
            else:
                self.channel = 4
            return self.decode_rgb_data(data)
        else:
            LOGGER.error('BMP file bits per pixel is not in (1, 4, 8, 24, 32).')

    # decode rgb data
    def decode_rgb_data(self, data):
        rowData = []
        mask = {1 :0b1, 4 :0b1111, 8 :0b11111111 }
        lineLength = self.width * self.bitsPerPixel
        if lineLength % 8 != 0:
            lineLength = lineLength / 8 + 1
        else:
            lineLength /= 8
        if lineLength % 4 != 0:
            lineLength = (lineLength / 4 + 1)*4
        index = 0
        for j in range(self.height):
            lineData = []
            if self.bitsPerPixel >= 24:
                for i in range(self.width):
                    if self.bitsPerPixel == 32:
                        lineData.append([ord(data[index+2]), ord(data[index+1]), ord(data[index]), ord(data[index+3])])
                        index += 4
                    else: # 24
                        lineData.append([ord(data[index+2]), ord(data[index+1]), ord(data[index])])
                        index += 3
            else:
                # decode rowdata from color palette
                kmax = 8/self.bitsPerPixel
                i = 0
                while i != -1:
                    d = ord(data[index])
                    index += 1
                    for k in range(kmax-1, -1, -1):
                        if i < self.width:
                            colorPalette = self.colorPalette[ (d>>(k*self.bitsPerPixel)) & mask[self.bitsPerPixel] ]
                            lineData.append([ord(colorPalette[0]), ord(colorPalette[1]), ord(colorPalette[2]), ord(colorPalette[3])])
                            i += 1
                        else:
                            i = -1
            rowData = lineData + rowData
            appendData = data[index:(j+1)*lineLength]
            for c in appendData:
                if c != '\x00' and c != '\xff':
                    LOGGER.log(CustomLoggingLevel.OTHER_DATA, '[0x%x]Unsual append data: 0x%s'%(self.headerLength+index, appendData.encode('hex')))
                    break
            index = (j+1)*lineLength
        return rowData

    def showextradata(self, data, location):
        if len(data) > 128:
            tmpFileObject = FileObject(data)
            LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '[0x%x] %s'%(location, tmpFileObject.type()) )
        else:
            LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '[0x%x] > %s'%(location, data) )
    
    def detect(self):
        self.start()
        rowData = ''
        if self.version == 1:
            rowData = self.rowdata_ver1()
        elif self.version in [2, 3]:
            rowData = self.rowdata_ver23()
        elif self.version == 4:
            rowData = self.rowdata_ver4()
        for d in self.fileObject.redundancy():
            self.showextradata(d['data'], d['start'])
        return [RowData(rowData, self.channel, self.width, self.height)]

        # LOGGER.log(CustomLoggingLevel.IMAGE_DEBUG,"BMP型图像调试信息")
        # LOGGER.log(CustomLoggingLevel.ASCII_DATA,"连续 ASCII 或 可见字符")
        # LOGGER.log(CustomLoggingLevel.OTHER_DATA,"其它数据")
        # LOGGER.log(CustomLoggingLevel.EXTRA_DATA,"在文件尾部或中间发现多余数据")
        # LOGGER.log(CustomLoggingLevel.STEGO_DATA,"发现隐写数据")
        # LOGGER.log(CustomLoggingLevel.IMAGE_INFO,"输出图像基本信息")

        # LOGGER.warning("警告信息")
        # LOGGER.error("错误信息")