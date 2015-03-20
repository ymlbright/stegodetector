    # -*- coding: utf-8 -*-
# @Date    : 2015-08-08 
# @Author  : m3d1t10n@163.com

import struct
import zlib
import math
from PIL import Image
import cStringIO
import sys
import ctypes
try:
    from common.fileobject import FileObject
    from common.logger import *
    from common.imageshow import ImageShow
    from common.rowdata import RowData
except:
    sys.path.append("..")
    from common.fileobject import FileObject
    from common.logger import *
    from common.imageshow import ImageShow
    from common.rowdata import RowData




class PNGDetector():
    def __init__(self,fileObject):
        self.fileObject = fileObject
        self.streamCur = 0
        LOGGER.addHandler(stream_handler)
        errorHandler.ignoreError = False
        LOGGER.addHandler(errorHandler)
        self.headerInfo = {}
        self.FILE_END = 3
        self.FILE_LEGAL = 2
        self.FILE_OVER = 1
        self.chunk_count = {"IHDR":0,"IDAT":0,"PLTE":0,"IEND":0,"tRNS":0,"cHRM":0,"sRGB":0,"iCCP":0,"gAMA":0,"sBIT":0,"tEXt":0,"iTXt":0,"zTXt":0,"bKGD":0,"hIST":0,"pHYs":0,"sPLT":0,"tIME":0}
        self.ImageExtraInfoLogCount = 0
        self.ImageExtraDataStart = 0
        self.ImageExtraDataEnd = 0
        self.HasExtraData = False
        # self.iterlaceTable = [[1,6,4,6,2,6,4,6],
        #                       [7,7,7,7,7,7,7,7],
        #                       [5,6,5,6,5,6,5,6],
        #                       [7,7,7,7,7,7,7,7],
        #                       [3,6,4,6,3,6,4,6],
        #                       [7,7,7,7,7,7,7,7],
        #                       [5,6,5,6,5,6,5,6],
        #                       [7,7,7,7,7,7,7,7]
        #                     ]
        self._adam7 = ((0, 0, 8, 8),
                       (4, 0, 8, 8),
                       (0, 4, 4, 8),
                       (2, 0, 4, 4),
                       (0, 2, 2, 4),
                       (1, 0, 2, 2),
                       (0, 1, 1, 2))


    def deinterlace(self, raw):
        """
        Read raw pixel data, undo filters, deinterlace, and flatten.
        Return in flat row flat pixel format.
        """

        # print >> sys.stderr, ("Reading interlaced, w=%s, r=%s, planes=%s," +
        #     " bpp=%s") % (self.width, self.height, self.planes, self.bps)
        
        flt_list = [self.ifilter0, self.ifilter1, self.ifilter2, self.ifilter3, self.ifilter4]
        # Values per row (of the target image)
        vpr = self.width * self.bpp

        # Make a result array, and make it big enough.  Interleaving
        # writes to the output array randomly (well, not quite), so the
        # entire output array must be in memory.
        # fmt = 'BH'[self.bitdepth > 8]
        # a = array(fmt, [0]*vpr*self.height)
        source_offset = 0

        # after = [[0]*vpr] * self.height
        after = []
        for i in range(self.height):
            after.append([0]*vpr)
     
        for xstart, ystart, xstep, ystep in self._adam7:
            
            if xstart >= self.width:
                continue
           
            # Pixels per row (reduced pass image)
            ppr = int(math.ceil((self.width-xstart)/float(xstep)))
            row_size = int(math.ceil(self.bpp * ppr))
            recon = [0] * row_size
            for y in range(ystart, self.height, ystep):
                filter_type = raw[source_offset]
                source_offset += 1
                scanline  = [ord(b) for b in  raw[source_offset:source_offset+row_size]]
                source_offset += row_size
                recon = flt_list[ord(filter_type)](scanline,recon,self.bpp)
                if xstep == 1 and xstart==0:
                    after[y][0:vpr] = recon[0:vpr]
                else:
                    reconIndex = 0
                    for xpos in range(xstart,self.width,xstep):
                        after[y][xpos*self.bpp:xpos*self.bpp+self.bpp] = recon[reconIndex*self.bpp:reconIndex*self.bpp+self.bpp]
                        reconIndex += 1
      
        return after

    def checkInterlaceMethod1(self,data):
        totalSum = 0
        for xstart,ystart,xstep,ystep in self._adam7:
            passPixels = math.ceil((self.width-xstart)/float(xstep))
            rowBytes = passPixels * self.bpp + 1
            t_sum = 0
            for y in range(ystart,self.height,ystep):
                t_sum += rowBytes 
            totalSum += t_sum
        if totalSum < len(data):
            self.checkFileType(totalSum, data[totalSum:len(data)])

    def checkIterlaceMethod0(self,data):
        totalSum = (self.width * self.bpp + 1) * self.height
        if totalSum < len(data):
            self.checkFileType(totalSum, data[totalSum:len(data)])

    def checkFileType(self,curStream,data):
        if len(data) <= 128:
            LOGGER.log(CustomLoggingLevel.EXTRA_DATA, 'In IDAT decompress data at [0x%.8x] %s'%(curStream,data) )
        else:
            tmpFileObject = FileObject(data)
            LOGGER.log(CustomLoggingLevel.EXTRA_DATA, 'In IDAT decompress data at [0x%.8x] %s'%(curStream, tmpFileObject.type()) )


    def isPng(self,fileObject):
        if fileObject.read(8)!='\x89\x50\x4e\x47\x0d\x0a\x1a\x0a':
            LOGGER.log(CustomLoggingLevel.IMAGE_INFO,'Not a png file')
        else:
            LOGGER.info('Find png start mark')
        self.streamCur = self.fileObject.cur()


    def get_ihdr_info(self,data):
        result = struct.unpack('!IIBBBBB', data)
        # struct{
        #   int32 width;
        #   int32 height;
        #   uint8 bit_depth;
        #   uint8 color_type;
        #   uint8 compression_method;
        #   uint8 filter_method;
        #   uint8 interlace_method;
        # }
        prop = ['width', 'height', 'bit depth', \
                'color type', 'compression method', \
                'filter method', 'interlace method']
        for index, item in enumerate(prop):
            self.headerInfo[item] = result[index]
        self.width = self.headerInfo['width']
        self.height = self.headerInfo['height']


    def checkChunkIsValid(self,chunkInfo):
        names  =  self.chunk_count.keys()
        if chunkInfo['name'] not in names:
            LOGGER.log(CustomLoggingLevel.IMAGE_INFO,'Chunk name %s isn\'t a valid chunk name,At 0x%.8x'%(chunkInfo['name'],self.streamCur+4) )
            return False
        else:
            self.chunk_count[chunkInfo['name']] += 1
        crc = ctypes.c_uint(zlib.crc32(chunkInfo['name']+chunkInfo['data'])).value
        # print hex(int(crc)),chunkInfo['crc']
        if hex(int(crc)) != chunkInfo['crc']:
            LOGGER.log(CustomLoggingLevel.IMAGE_INFO,'Not a valid crc value:%s at 0x%.8x'%(chunkInfo['crc'],self.streamCur+8+len(chunkInfo['data'])))
        if self.HasExtraData:
             LOGGER.log(CustomLoggingLevel.EXTRA_DATA,"Extra data at 0x%.8x - 0x%.8x"%(self.ImageExtraDataStart-4,self.ImageExtraDataEnd-4))
        self.HasExtraData = False
        return True

    def checkReadValid(self,length):
        if self.fileObject.size == self.fileObject.cur():
            return self.FILE_END
        elif self.fileObject.size >= self.fileObject.cur() + length:
            return self.FILE_LEGAL
        else:
            self.HasExtraData = True
            raise IOError('Wrong chunk length  start at 0x%.8x'%(self.fileObject.cur()-4))


    def getChunkInfo(self):
        chunkInfo = {}
        try:
            self.checkReadValid(4)
            chunkInfo['length'] = struct.unpack('!I',self.fileObject.read(4))[0]
            self.checkReadValid(chunkInfo['length'])

            self.checkReadValid(4)
            chunkInfo['name'] = self.fileObject.read(4)
            
            # self.checkReadValid(chunkInfo['length'])
            chunkInfo['data'] = self.fileObject.read(chunkInfo['length'])

            self.checkReadValid(4)
            chunkInfo['crc'] = hex(struct.unpack('!I',self.fileObject.read(4))[0])
            if not self.checkChunkIsValid(chunkInfo):
                self.streamCur += 1
                self.fileObject.change_cur(self.streamCur)
                return self.getChunkInfo()
            else:
                self.streamCur = self.fileObject.cur()
                return chunkInfo

        except IOError,e:

            if self.ImageExtraInfoLogCount == 0:
                LOGGER.log(CustomLoggingLevel.EXTRA_DATA,e)
                self.ImageExtraInfoLogCount += 1
            if self.ImageExtraDataStart == 0:
                self.ImageExtraDataStart = self.fileObject.cur()
            elif self.ImageExtraDataEnd == 0:
                self.ImageExtraDataEnd = self.fileObject.cur() 
            else:
                if self.fileObject.cur()-self.ImageExtraDataEnd==1:
                    self.ImageExtraDataEnd += 1
                else:
                    self.ImageExtraDataEnd = 0
                    self.ImageExtraDataStart = 0
                    self.ImageExtraInfoLogCount = 0
            if self.fileObject.size >= self.streamCur :
                self.streamCur += 1
                self.fileObject.change_cur(self.streamCur)
                return self.getChunkInfo()
        except struct.error,e:
            pass
        except Exception,e:
            pass
        return chunkInfo


    def ifilter0(self,before, upper,bpp):
        '''Type 0: No filter'''
        return before


    def ifilter1(self,before, upper,bpp):
        '''Type 1: Inverse Sub filter'''
        N = len(before)
        after = [0] * N
        after[0:bpp] = before[0:bpp]
        for k in range(bpp, N):
            after[k] = (before[k] + after[k-bpp]) % 0x0100
        return after


    def ifilter2(self,before, upper,bpp):
        '''Type 2: Inverse Up filter'''
        N = len(before)
        after = [0] * N
        for k in range(N):
            after[k] = (before[k] + upper[k]) % 0x0100
        return after


    def ifilter3(self,before, upper,bpp):
        '''Type 3: Inverse Average filter'''
        N = len(before)
        after = [0] * N
        for k in range(bpp):
            after[k] = (before[k] + upper[k] / 2) % 0x0100 # integer div
        for k in range(bpp, N):
            after[k] = (before[k] + (after[k-bpp] + upper[k]) / 2) % 0x0100
        return after


    def ifilter4(self,before, upper, bpp):
        '''Type 4: Inverse Paeth filter'''
        def predictor(a, b, c):
            '''a = left, b = above, c = upper left'''
            p = a + b -c
            pa = abs(p - a)
            pb = abs(p - b)
            pc = abs(p - c)
            if pa <= pb and pa <= pc:
                return a
            elif pb <= pc:
                return b
            else:
                return c
        N = len(before)
        after = [0] * N
        for k in range(bpp):
            after[k] = (before[k] + upper[k]) % 0x0100
        for k in range(bpp, N):
            after[k] = (before[k] + predictor(after[k-bpp], upper[k], upper[k-bpp])) % 0x0100
        return after


    def ifilter(self,before):
        width = self.headerInfo['width']
        height = self.headerInfo['height']
        bit_depth = self.headerInfo['bit depth']
        num_items = {0:1, 2:3, 3:1, 4:2, 6:4}
        width = int(math.ceil(width * bit_depth * num_items[self.headerInfo['color type']] / 8.0))
        after = []
        flt_type = [0] * height
        flt_list = [self.ifilter0, self.ifilter1, self.ifilter2, self.ifilter3, self.ifilter4]
        for k in range(height):
            after.append([ord(b) for b in before[(k*(width+1)+1):((k+1)*(width+1))]])
            flt_type[k] = ord(before[k * (width+1)])
        # print flt_type
        after[0]= flt_list[flt_type[0]](after[0], [0] * width, self.bpp)
        for k in range(1, height):
            after[k] = flt_list[flt_type[k]](after[k], after[k-1], self.bpp)
        return after


    def calcBytesPerPixel(self):
        '''PNG image type |  Colour type | Allowed bit depths | Interpretation
               Greyscale  |     0        | 1, 2, 4, 8, 16     | Each pixel is a greyscale sample
              Truecolour  |     2        |      8, 16         | Each pixel is an R,G,B triple
            Indexed-colour|     3        |    1 , 2, 4, 8     |Each pixel is a palette index; a PLTE chunk shall appear.
    Greyscale with alpha  |     4        |       8, 16        | Each pixel is a greyscale sample followed by an alpha sample.
    Truecolour with alpha |     6        |       8, 16        |Each pixel is an R,G,B triple followed by an alpha sample.'''
        num_enum = { 0:1, 2:3, 3:1, 4:2, 6:4}

        # mode = { 0:"L", 2:"RGB", 3:"P", 4:"LA", 6:"RGBA"}
        bytes = math.ceil(self.headerInfo['bit depth'] / 8.0 * num_enum[self.headerInfo['color type']])
        self.bpp = int(bytes)
        # self.mode = mode[self.headerInfo['color type']]
        return int(bytes)


    def splitByte(self,byte,width):
        mask = 2**width - 1
        li = []
        for k in range(8/width):
            li.append(byte & mask)
            byte >>= width
        li.reverse()
        return li


    def bytes2pixels(self,mtx, bit_depth, img_width):
        if bit_depth < 8:
            for idx, line in enumerate(mtx):
                pixels = []
                for B in line:
                    pixels.extend(self.split_byte(B, bit_depth))
                pixels = pixels[:img_width]
                mtx[idx] = pixels
        if bit_depth == 16:
           for idx, line in enumerate(mtx):
                pixels = []
                for k in range(img_width):
                    pixels.append(line[2*k]*2**8 + line[2*k+1])
                mtx[idx] = pixels
        return mtx

    def decompress(self,f):
        out = open('output/zip.dat','w')
        out.write(f.getvalue())
        out.close()

        z = zlib.decompressobj()
        t=''
        while True:
            buf = z.unconsumed_tail
            if buf == "":
                buf = f.read(8192)
                if buf == "":
                    break
            got = z.decompress(buf)
            if got == "":
                break
            t += got
        return t


    def result(self,data):
        rData  = []
        for y in range(self.height):
            for x in range(self.width):
                pix = []
                for i in range(self.bpp):
                    pix.append(data[y][x*self.bpp+i])
                rData.append(pix)
        return [RowData(rData, self.bpp, self.width, self.height)]

    def checkRedundancy(self):
        if self.fileObject.size - self.fileObject.cur() > 128:
            curStream = self.fileObject.cur()
            data = self.fileObject.read(self.fileObject.size - self.fileObject.cur())
            tmpFileObject = FileObject(data)
            LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '[0x%x] ,filetype is %s'%(curStream, tmpFileObject.type()) )
            
        elif self.fileObject.size-self.fileObject.cur()>0:
            curStream = self.fileObject.cur()
            data = self.fileObject.read(self.fileObject.size - self.fileObject.cur())
            LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '[0x%x] ,data is  %s'%(curStream, data) )
            
    def parseChunk(self):
        chunk = self.getChunkInfo()
        self.data = ''
        #self.chunk_count = {'IHDR':0, "IDAT":0, "IEND":0}
        while chunk:

            # LOGGER.info(chunk)
            if chunk['name']=='\x49\x48\x44\x52':#'IHDR'
             
               # self.chunk_count['IHDR'] += 1
                self.get_ihdr_info(chunk['data'])
            
            if chunk['name']=='\x49\x44\x41\x54':#'IDAT'
                #LOGGER.info('png IDAT chunk detected')
                #self.chunk_count['IDAT'] += 1
                self.data +=  chunk['data']
            if chunk['name']=='IEND':
                self.checkRedundancy()


            chunk = self.getChunkInfo()

        #print the chunk info
        for idx,name in enumerate(self.chunk_count):
            if self.chunk_count[name] > 0:
                LOGGER.info('Detect png %s chunk %d times' %(name,self.chunk_count[name]))
            if name=='IHDR':
                LOGGER.info('PNG Image Header Info:\n' + str(self.headerInfo))
    def getPicPixels(self):
        # print len(self.data)
        decData = self.decompress(cStringIO.StringIO(self.data))
        # f = open('data.dat','w')
        # f.write(decData[0x280bf6:len(decData)])
        # f.close()
        #self.testShow(decDatab)
        # print len(decData)

        self.calcBytesPerPixel()
        if self.headerInfo['interlace method'] == 0 :
            self.checkIterlaceMethod0(decData)
            return self.ifilter(decData)
        else :
            self.checkInterlaceMethod1(decData)
            return self.deinterlace(decData)

    def detect(self):
        self.isPng(self.fileObject)
        self.parseChunk()
        data_mtx = self.getPicPixels()
        # f = open('test1.dat','w')
        # f.write(data_mtx)
        # f.close()
        return  self.result(data_mtx)


if __name__ == '__main__':
    png = PNGDetector(FileObject('../pic/steg.png'))
    # png = PNGDetector(FileObject('../pic/png2.png'))
    show = ImageShow(png.detect())
    # f = open('test2.dat')
    show.show()
    # show.show()
    # img = Image.open("../pic/png7.png")
    # print img
    # width,height = img.size
    # pix = img.load()
    # f = open("test1.dat",'w')
    # l = []
    # for y in range(height):
    #     tmpL = []
    #     for x in range(width):
    #         for i in range(4):
    #             tmpL.append(pix[x,y][i])
    #     l.append(tmpL)

    # f.write(str(l))
    # f.close()
    
    
    
