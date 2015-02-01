

import unittest
from gif.gifdetector import GIFDetector
from common.fileobject import FileObject

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



if __name__ == '__main__':
    unittest.main()
