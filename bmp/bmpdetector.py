#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-01-27 23:24:08
# @Author  : yml_bright@163.com

from common.logger import LOGGER, CustomLoggingLevel


class BMPDetector():
    def __init__(self, fileObject):
        self.fileObject = fileObject

    def detect(self):
        LOGGER.log(CustomLoggingLevel.IMAGE_DEBUG, "BMP型图像调试信息")
        LOGGER.log(CustomLoggingLevel.ASCII_DATA, "连续 ASCII 或 可见字符")
        LOGGER.log(CustomLoggingLevel.OTHER_DATA, "其它数据")
        LOGGER.log(CustomLoggingLevel.EXTRA_DATA, "在文件尾部或中间发现多余数据")
        LOGGER.log(CustomLoggingLevel.STEGO_DATA, "发现隐写数据")
        LOGGER.log(CustomLoggingLevel.IMAGE_INFO, "输出图像基本信息")

        LOGGER.warning("警告信息")
        LOGGER.error("错误信息")
        return ['', '', '']