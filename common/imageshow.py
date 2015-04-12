from PIL import Image
import webbrowser
import os
try:
    from common.fileobject import FileObject
    from common.logger import *
except:
    import sys
    sys.path.append("..")
    from common.fileobject import FileObject
    from common.logger import *


class ImageShow():
    def __init__(self,picArray):
        LOGGER.addHandler(stream_handler)
        self.picArray = picArray
        self.index = 0
        self.outputPath = 'output'
    def checkOutputPath(self,name):
        if os.path.exists(name):
            return 
        else :
            os.mkdir(name)


       

    def show(self,order='all'):
        if len(self.picArray)==0:
            LOGGER.error("no picture data")
            return
        self.checkOutputPath(self.outputPath)
        LOGGER.info("Showing picture...")
        for pic in self.picArray:
            img = Image.new("RGBA", (pic.width,pic.height),'white')
            pix = img.load()
            if pic.channel == 4 : #RGBA
                for y in range(0,pic.height):
                    for x in range(0,pic.width):
                        pos = x * pic.channel
                        pix[x,y] = (pic.rowData[y*pic.width+x][0],pic.rowData[y*pic.width+x][1],pic.rowData[y*pic.width+x][2],pic.rowData[y*pic.width+x][3])
            elif pic.channel ==3 : #RGB
                for y in range(0,pic.height):
                    for x in range(0,pic.width):
                        pos = x * pic.channel
                        pix[x,y] = (pic.rowData[y*pic.width+x][0],pic.rowData[y*pic.width+x][1],pic.rowData[y*pic.width+x][2])
            elif pic.channel == 1: #L
                for y in range(0,pic.height):
                    for x in range(0,pic.width):
                        pos = x * pic.channel
                        value = pic.rowData[y*pic.width+x][0]
                        pix[x,y] = (value,value,value)
            if pic.channel > 1:
                orderList = order.split(',')
                for tmpOrder in orderList:
                    if len(tmpOrder)>pic.channel:
                        LOGGER.error("Img only has %d channels and you wan't to show %d"%(pic.channel,len(tmpOrder)))
                galletyData = self.splitGallery(img, pic.channel)
                self.showGallery(galletyData,order)
            else:
                tmpSaveName = self.outputPath +'\\'+'tmp'+str(self.index)+'.png'
                img.save(tmpSaveName)
                webbrowser.open(tmpSaveName)
            self.index += 1
            # img.save(self.outputPath +'\\'+'tmp'+str(self.index)+'.png')
            # webbrowser.open(self.outputPath +'\\'+'tmp'+str(self.index)+'.png')
            # self.index += 1
    def openAndShow(self,filename):
        webbrowser.open(filename)

    def splitGallery(self,img,channel):
        
        if channel == 4:
            rgba = img.split()
            return (rgba,'rgba')
        elif channel == 3:
            r,g,b,a = img.split()
            return ((r,g,b),'rgb')

    def showGallery(self,gallery,showOrder):
        galleryIndex = {'r':0,'g':1,'b':2,'a':3}
        length = gallery[0][0].size[0]*gallery[0][0].size[1]
        chunkData = [0]*length
        alphaChunkData = [255]*length
        chunkImg = Image.new("L", gallery[0][0].size)
        chunkImg.putdata(chunkData)
       

        orderList = showOrder.split(",")
        for order in orderList:
            if order == 'all':
                # print gallery[1],gallery[0]
                im = Image.merge(gallery[1].upper(), gallery[0])
                tmpSaveName = self.outputPath +'\\'+'tmp'+str(self.index)+'_all.png'
                im = im.convert("RGB")
                im.save(tmpSaveName)
                self.openAndShow(tmpSaveName)
            else:
                for imgpass in order:
                    galleryData ={'r':chunkImg,'g':chunkImg,'b':chunkImg}
                    if imgpass in galleryIndex:
                        if imgpass!='a':
                            tmpSaveName = self.outputPath +'\\'+'tmp'+str(self.index)+'_'+str(imgpass)+'.png'
                            # print imgpass,galleryIndex[imgpass]
                            # gallery[0][galleryIndex[imgpass]].save(tmpSaveName)
                            galleryData[imgpass] = gallery[0][galleryIndex[imgpass]]
                            im = Image.merge("RGB", (galleryData['r'],galleryData['g'],galleryData['b']))
                            # im = gallery[0][galleryIndex[imgpass]].convert("RGBA")
                            im.save(tmpSaveName)
                            self.openAndShow(tmpSaveName)
                        else:
                            tmpSaveName = self.outputPath +'\\'+'tmp'+str(self.index)+'_'+str(imgpass)+'.png'
                            gallery[0][galleryIndex[imgpass]].save(tmpSaveName)
                            self.openAndShow(tmpSaveName)
                    else:
                        LOGGER.error("Order %s not in %s"%(imgpass,gallery[1]))

    def save(self,name):
        if len(self.picArray)==0:
            LOGGER.error("no picture data")
            return
        self.checkOutputPath(self.outputPath)
        LOGGER.info("Save picture...")
        for pic in self.picArray:
            img = Image.new("RGBA", (pic.width,pic.height),'white')
            pix = img.load()
            if pic.channel == 4 : #RGBA
                for y in range(0,pic.height):
                    for x in range(0,pic.width):
                        pos = x * pic.channel
                        pix[x,y] = (pic.rowData[y*pic.width+x][0],pic.rowData[y*pic.width+x][1],pic.rowData[y*pic.width+x][2],pic.rowData[y*pic.width+x][3])
            elif pic.channel ==3 : #RGB
                for y in range(0,pic.height):
                    for x in range(0,pic.width):
                        pos = x * pic.channel
                        pix[x,y] = (pic.rowData[y*pic.width+x][0],pic.rowData[y*pic.width+x][1],pic.rowData[y*pic.width+x][2])
            elif pic.channel == 1: #L
                for y in range(0,pic.height):
                    for x in range(0,pic.width):
                        pos = x * pic.channel
                        value = pic.rowData[y*pic.width+x][0]
                        pix[x,y] = (value,value,value)
            img.save(self.outputPath +'\\' + name+str(self.index)+'.png')
            self.index += 1



