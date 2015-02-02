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
        if self.fileObject.read(2) == '\xff\xd8': # start of JPEG file
            pass
        else:
            LOGGER.error('JPEG file start mark 0xFFD8 check failed.')

    def tag_com(self, tag):
        # 0xFFFE 注释
        pass

    def tag_app(self, tag):
        # 0xFFE0~0xFFEE APPn
        pass

    def tag_jpg(self, tag):
        # 0xFFF0~0xFFFD JPGn 为扩展保留
        pass

    def tag_jpeg(self, tag):
        # 0xFFC8 JPEG 扩展保留

    def tag_dhp(self, tag):
        # #FFDE 图像层次级数
        pass

    def tag_exp(self, tag):
        # 0xFFDF 展开参考图像

    def tag_dqt(self, tag):
        # 0xFFDB 图像量化表
        pass

    def tag_sof(self, tag):
        # 0xFFC0~0xFFC7 0xFFC9~0xFFCF 图像帧开始
        pass

    def tag_dht(self, tag):
        # 0xFFC4 Huffman表
        pass

    def tag_dnl(self, tag):
        # 0xFFDC 线数


    def tag_dri(self, tag):
        # 0xFFDD 差分编码累计复位间隔
        pass

    def tag_sos(self, tag):
        # 0xFFDA 图像扫描开始
        pass

    def tag_eoi(self, tag):
        # 0xFFD9 图像结束
        pass

    def tag_dac(self, tag):
        # 0xFFCC 算数差分表
        pass

    def tag_res(self, tag):
        # 0xFF02~0xFFBF resverse

    def detect(self):
        self.start()
        return ['','','']