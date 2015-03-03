from PIL import Image
try:
    from common.fileobject import FileObject
    from common.logger import *
except:
    import sys
    sys.path.append("..")
    from common.fileobject import FileObject
    from common.logger import *


class ImageShow():
    def __init__(self,,director=0):
        self.width = width
        self.height = height 
        self.bpp = bpp
        LOGGER.addHandler(stream_handler)
        self.data = data
        self.director = director
       

    def show(self):
        if len(self.data)==0:
            LOGGER.error("no picture data")
            return
        for pic in self.data:





        if self.mode=="RGBA":
            self.image = Image.new("RGBA", (width,height))
            pix = self.image.load()
            for y in range(0,self.height):
                for x in range(0,self.width):
                    pos = x * self.bpp
                    pix[x,y] = (self.data[y*self.width+pos],self.data[y*self.width+pos+1],self.data[y*self.width+pos+2],self.data[y*self.width+pos+3])
            
        elif self.mode=="RGB":
            self.image = Image.new("RGB", (width,height))
            pix = self.image.load()
            for y in range(0,self.height):
                for x in range(0,self.width):
                    pos = x * self.bpp
                    pix[x,y] = (self.data[y*self.width+pos],self.data[y*self.width+pos+1],self.data[y*self.width+pos+2])
            
        elif self.mode=="L":
            self.image = Image.new("L", (width,height))
            pix = self.image.load()
            for y in range(0,self.height):
                for x in range(0,self.width):
                    pix[x,y] = (self.data[y*self.width+x],self.data[y*self.width+x],self.data[y*self.width+x])
        elif self.mode=="P":
            pass
        self.image.show()

    def save(self,name):
        self.image.save(name)



