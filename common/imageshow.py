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
    def __init__(pic,picArray):
        LOGGER.addHandler(stream_handler)
        pic.picArray = picArray       
       

    def show(pic):
        if len(pic.picArray)==0:
            LOGGER.error("no picture data")
            return
        LOGGER.info("show picture...")
        for pic in pic.picArray:
            img = Image.new("RGBA", (pic.width,pic.height))
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
            img.show()

    def save(pic,name):
        pic.image.save(name)



