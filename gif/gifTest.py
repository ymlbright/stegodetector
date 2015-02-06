

import unittest
from gif.gifdetector import GIFDetector
from common.fileobject import FileObject
from PIL import Image

class MyTestCase(unittest.TestCase):

    def test_gif1(self):
        detector = GIFDetector(FileObject("1.gif"))

        self.assertEqual(detector.type, "GIF")
        self.assertEqual(detector.version, "89a")

        self.assertEqual(detector.logicScreenWidth, 400)
        self.assertEqual(detector.logicScreenHeight, 400)

        self.assertEqual(detector.globalColorTableFlag, 1)
        self.assertEqual(detector.colorResolution, 7)
        self.assertEqual(detector.sortFlag, 0)
        self.assertEqual(detector.pixel, 7)
        self.assertEqual(detector.backgroundColorIndex, 255)
        self.assertEqual(detector.pixelAspectRatio, 0)

        self.assertEqual(detector.globalColorTable.__len__(), 2**(detector.pixel+1))

        images = detector.get_images()
        for image in images:
            im = Image.new("RGB", (len(image[0]), len(image)))
            for i in range(len(image)):
                for j in range(len(image[i])):
                    im.putpixel((i, j), image[i][j])
            im.save(str(i)+".jpg")


    def test_lzw(self):
        data = [chr(i) for i in [1,1,2,4,3,4,9,5,11,2] ]
        detector = GIFDetector(FileObject("1.gif"))
        res = detector.lzwdecode(data, 2, [0, [1], [2], [3]])
        print res


if __name__ == '__main__':
    unittest.main()
