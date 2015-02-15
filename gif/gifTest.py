

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

    def test_gif0(self):
        detector = GIFDetector(FileObject("0.gif"))
        images = detector.get_images()
        cnt = 0
        for image in images:
            self.assertEqual(image.w * image.h, len(image.data))
            im = Image.new("RGB", (image.w, image.h))

            im.putdata([(x[0], x[1], x[2]) for x in image.data])
            im.save("%d.jpg" % cnt)
            cnt += 1

    # def test_lzw(self):
    #     detector = GIFDetector(FileObject("1.gif"))
    #     data = ['T', 'O', 'B', 'E', 'O', 'R', 'N', 'O', 'T', 256, 258, 260, 265, 259, 261, 263]
    #     decoded = detector.lzwdecode(data, 8)
    #     self.assertEqual(decoded, [ord(c) for c in "TOBEORNOTTOBEORTOBEORNOT"])

if __name__ == '__main__':
    unittest.main()
