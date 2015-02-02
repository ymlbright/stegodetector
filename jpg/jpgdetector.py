#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-02-02 10:29:36
# @Author  : yml_bright@163.com


import struct
from common.fileobject import FileObject
from common.logger import LOGGER, CustomLoggingLevel

class JPGDetector():

    detectSensitive = 1.0

    def __init__(self, fileObject):
        self.fileObject = fileObject

    def start(self):
        pass

    def detect(self):
        self.start()
        return ['','','']