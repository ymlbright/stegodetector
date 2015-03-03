    # -*- coding: utf-8 -*-
# @Date    : 2015-08-08 
# @Author  : m3d1t10n@163.com

import struct
import zlib
import math
from PIL import Image
import cStringIO
try:
    from common.fileobject import FileObject
    from common.logger import *
    from common.imageshow import ImageShow
    from common.rowdata import RowData
except:
    import sys
    sys.path.append("..")
    from common.fileobject import FileObject
    from common.logger import *
    from common.imageshow import ImageShow
    from common.rowdata import RowData



class PngDetector():
    def __init__(self,fileObject):
        self.fileObject = fileObject
        LOGGER.addHandler(stream_handler)
        self.headerInfo = {}


    def isPng(self,fileObject):
        if fileObject.read(8)!='\x89\x50\x4e\x47\x0d\x0a\x1a\x0a':
            LOGGER.error('not a png file')
        else:
            LOGGER.info('find png start mark')


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


    def getChunkInfo(self,fileObject):
        chunkInfo = {}
        try:
            chunkInfo['length'] = struct.unpack('!I',self.fileObject.read(4))[0]
            chunkInfo['name'] = self.fileObject.read(4)
            chunkInfo['data'] = self.fileObject.read(chunkInfo['length'])
            chunkInfo['crc'] = hex(struct.unpack('!I',self.fileObject.read(4))[0])
        except:
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

    def parseChunk(self):
        chunk = self.getChunkInfo(self.fileObject)
        self.data = ''
        chunk_count = {'IHDR':0, "IDAT":0, "IEND":0}
        while chunk:
            # LOGGER.info(chunk)
            if chunk['name']=='\x49\x48\x44\x52':#'IHDR'
             
                chunk_count['IHDR'] += 1
                self.get_ihdr_info(chunk['data'])
            
            if chunk['name']=='\x49\x44\x41\x54':#'IDAT'
                #LOGGER.info('png IDAT chunk detected')
                chunk_count['IDAT'] += 1
                self.data +=  chunk['data']

            if chunk['name']=='\x49\x45\x4e\x44':#'IEND'
                #LOGGER.info('png IEND chunk detected')
                chunk_count['IEND'] += 1

            if chunk['name'] == '':
                pass
            chunk = self.getChunkInfo(self.fileObject)

        #print the chunk info
        for idx,name in enumerate(chunk_count):

            LOGGER.info('detect png %s chunk %d times' %(name,chunk_count[name]))
            if name=='IHDR':
                LOGGER.info('PNG Image Header Info:\n' + str(self.headerInfo))
    def getPicPixels(self):
        decData = self.decompress( cStringIO.StringIO(self.data))
        self.calcBytesPerPixel()
        return self.ifilter(decData)

    def detect(self):
        self.isPng(self.fileObject)
        self.parseChunk()
        data_mtx = self.getPicPixels()
        
        return  self.result(data_mtx)

       

         


if __name__ == '__main__':
    png = PngDetector(FileObject('../pic/png4.png'))
    show = ImageShow(png.detect())
    show.show()
    # show.show()
    # img = Image.open("test.png")
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
    
    
    
