#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2015-02-02 10:29:36
# @Author  : yml_bright@163.com

import struct
from common.fileobject import FileObject
from common.logger import LOGGER, CustomLoggingLevel

class JPGDetector():

    exifEnumTag = {
        0x0001 : 'InteropIndex',
        0x0002 : 'InteropVersion',
        0x00fe : 'SubfileType',
        0x00ff : 'OldSubfileType',
        0x0100 : 'ImageWidth',
        0x0101 : 'ImageHeight',
        0x0102 : 'BitsPerSample',
        0x0103 : 'Compression',
        0x0106 : 'PhotometricInterpretation',
        0x0107 : 'Thresholding',
        0x0108 : 'CellWidth',
        0x0109 : 'CellLength',
        0x010a : 'FillOrder',
        0x010d : 'DocumentName',
        0x010e : 'ImageDescription',
        0x010f : 'Make',
        0x0110 : 'Model',
        0x0111 : 'StripOffsets',
        0x0112 : 'Orientation',
        0x0115 : 'SamplesPerPixel',
        0x0116 : 'RowsPerStrip',
        0x0117 : 'StripByteCounts',
        0x0118 : 'MinSampleValue',
        0x0119 : 'MaxSampleValue',
        0x011a : 'XResolution',
        0x011b : 'YResolution',
        0x011c : 'PlanarConfiguration',
        0x011d : 'PageName',
        0x011e : 'XPosition',
        0x011f : 'YPosition',
        0x0120 : 'FreeOffsets',
        0x0121 : 'FreeByteCounts',
        0x0122 : 'GrayResponseUnit',
        0x0123 : 'GrayResponseCurve',
        0x0124 : 'T4Options',
        0x0125 : 'T6Options',
        0x0128 : 'ResolutionUnit',
        0x0129 : 'PageNumber',
        0x012c : 'ColorResponseUnit',
        0x012d : 'TransferFunction',
        0x0131 : 'Software',
        0x0132 : 'ModifyDate',
        0x013b : 'Artist',
        0x013c : 'HostComputer',
        0x013d : 'Predictor',
        0x013e : 'WhitePoint',
        0x013f : 'PrimaryChromaticities',
        0x0140 : 'ColorMap',
        0x0141 : 'HalftoneHints',
        0x0142 : 'TileWidth',
        0x0143 : 'TileLength',
        0x0144 : 'TileOffsets',
        0x0145 : 'TileByteCounts',
        0x0146 : 'BadFaxLines',
        0x0147 : 'CleanFaxData',
        0x0148 : 'ConsecutiveBadFaxLines',
        0x014a : 'SubIFD',
        0x014c : 'InkSet',
        0x014d : 'InkNames',
        0x014e : 'NumberofInks',
        0x0150 : 'DotRange',
        0x0151 : 'TargetPrinter',
        0x0152 : 'ExtraSamples',
        0x0153 : 'SampleFormat',
        0x0154 : 'SMinSampleValue',
        0x0155 : 'SMaxSampleValue',
        0x0156 : 'TransferRange',
        0x0157 : 'ClipPath',
        0x0158 : 'XClipPathUnits',
        0x0159 : 'YClipPathUnits',
        0x015a : 'Indexed',
        0x015b : 'JPEGTables',
        0x015f : 'OPIProxy',
        0x0190 : 'GlobalParametersIFD',
        0x0191 : 'ProfileType',
        0x0192 : 'FaxProfile',
        0x0193 : 'CodingMethods',
        0x0194 : 'VersionYear',
        0x0195 : 'ModeNumber',
        0x01b1 : 'Decode',
        0x01b2 : 'DefaultImageColor',
        0x0200 : 'JPEGProc',
        0x0201 : 'ThumbnailOffset',
        0x0202 : 'ThumbnailLength',
        0x0203 : 'JPEGRestartInterval',
        0x0205 : 'JPEGLosslessPredictors',
        0x0206 : 'JPEGPointTransforms',
        0x0207 : 'JPEGQTables',
        0x0208 : 'JPEGDCTables',
        0x0209 : 'JPEGACTables',
        0x0211 : 'YCbCrCoefficients',
        0x0212 : 'YCbCrSubSampling',
        0x0213 : 'YCbCrPositioning',
        0x0214 : 'ReferenceBlackWhite',
        0x022f : 'StripRowCounts',
        0x02bc : 'ApplicationNotes',
        0x1000 : 'RelatedImageFileFormat',
        0x1001 : 'RelatedImageWidth',
        0x1002 : 'RelatedImageLength',
        0x800d : 'ImageID',
        0x80a4 : 'WangAnnotation',
        0x80e3 : 'Matteing',
        0x80e4 : 'DataType',
        0x80e5 : 'ImageDepth',
        0x80e6 : 'TileDepth',
        0x827d : 'Model2',
        0x828d : 'CFARepeatPatternDim',
        0x828e : 'CFAPattern2',
        0x828f : 'BatteryLevel',
        0x8298 : 'Copyright',
        0x829a : 'ExposureTime',
        0x829d : 'FNumber',
        0x830e : 'PixelScale',
        0x83bb : 'IPTC_NAA',
        0x8474 : 'IntergraphPacketData',
        0x847f : 'IntergraphFlagRegisters',
        0x8480 : 'IntergraphMatrix',
        0x8482 : 'ModelTiePoint',
        0x84e0 : 'Site',
        0x84e1 : 'ColorSequence',
        0x84e2 : 'IT8Header',
        0x84e3 : 'RasterPadding',
        0x84e4 : 'BitsPerRunLength',
        0x84e5 : 'BitsPerExtendedRunLength',
        0x84e6 : 'ColorTable',
        0x84e7 : 'ImageColorIndicator',
        0x84e8 : 'BackgroundColorIndicator',
        0x84e9 : 'ImageColorValue',
        0x84ea : 'BackgroundColorValue',
        0x84eb : 'PixelIntensityRange',
        0x84ec : 'TransparencyIndicator',
        0x84ed : 'ColorCharacterization',
        0x84ee : 'HCUsage',
        0x8568 : 'IPTC_NAA2',
        0x85d8 : 'ModelTransform',
        0x8649 : 'PhotoshopSettings',
        0x8769 : 'ExifOffset',
        0x8773 : 'ICC_Profile',
        0x87ac : 'ImageLayer',
        0x87af : 'GeoTiffDirectory',
        0x87b0 : 'GeoTiffDoubleParams',
        0x87b1 : 'GeoTiffAsciiParams',
        0x8822 : 'ExposureProgram',
        0x8824 : 'SpectralSensitivity',
        0x8825 : 'GPSInfo',
        0x8827 : 'ISO',
        0x8828 : 'OptoElectricConvFactor',
        0x8829 : 'Interlace',
        0x882a : 'TimeZoneOffset',
        0x882b : 'SelfTimerMode',
        0x885c : 'FaxRecvParams',
        0x885d : 'FaxSubAddress',
        0x885e : 'FaxRecvTime',
        0x9000 : 'ExifVersion',
        0x9003 : 'DateTimeOriginal',
        0x9004 : 'CreateDate',
        0x9101 : 'ComponentsConfiguration',
        0x9102 : 'CompressedBitsPerPixel',
        0x9201 : 'ShutterSpeedValue',
        0x9202 : 'ApertureValue',
        0x9203 : 'BrightnessValue',
        0x9204 : 'ExposureCompensation',
        0x9205 : 'MaxApertureValue',
        0x9206 : 'SubjectDistance',
        0x9207 : 'MeteringMode',
        0x9208 : 'LightSource',
        0x9209 : 'Flash',
        0x920a : 'FocalLength',
        0x920b : 'FlashEnergy',
        0x920c : 'SpatialFrequencyResponse',
        0x920d : 'Noise',
        0x920e : 'FocalPlaneXResolution',
        0x920f : 'FocalPlaneYResolution',
        0x9210 : 'FocalPlaneResolutionUnit',
        0x9211 : 'ImageNumber',
        0x9212 : 'SecurityClassification',
        0x9213 : 'ImageHistory',
        0x9214 : 'SubjectLocation',
        0x9215 : 'ExposureIndex',
        0x9216 : 'TIFF_EPStandardID',
        0x9217 : 'SensingMethod',
        0x923f : 'StoNits',
        0x927c : 'MakerNote',
        0x9286 : 'UserComment',
        0x9290 : 'SubSecTime',
        0x9291 : 'SubSecTimeOriginal',
        0x9292 : 'SubSecTimeDigitized',
        0x935c : 'ImageSourceData',
        0x9c9b : 'XPTitle',
        0x9c9c : 'XPComment',
        0x9c9d : 'XPAuthor',
        0x9c9e : 'XPKeywords',
        0x9c9f : 'XPSubject',
        0xa000 : 'FlashpixVersion',
        0xa001 : 'ColorSpace',
        0xa002 : 'ExifImageWidth',
        0xa003 : 'ExifImageLength',
        0xa004 : 'RelatedSoundFile',
        0xa005 : 'ExifInteroperabilityOffset',
        0xa20b : 'FlashEnergy2',
        0xa20c : 'SpatialFrequencyResponse2',
        0xa20d : 'Noise2',
        0xa20e : 'FocalPlaneXResolution2',
        0xa20f : 'FocalPlaneYResolution2',
        0xa210 : 'FocalPlaneResolutionUnit2',
        0xa211 : 'ImageNumber2',
        0xa212 : 'SecurityClassification2',
        0xa213 : 'ImageHistory2',
        0xa214 : 'SubjectLocation2',
        0xa215 : 'ExposureIndex2',
        0xa216 : 'TIFF_EPStandardID2',
        0xa217 : 'SensingMethod2',
        0xa300 : 'FileSource',
        0xa301 : 'SceneType',
        0xa302 : 'CFAPattern',
        0xa401 : 'CustomRendered',
        0xa402 : 'ExposureMode',
        0xa403 : 'WhiteBalance',
        0xa404 : 'DigitalZoomRatio',
        0xa405 : 'FocalLengthIn35mmFormat',
        0xa406 : 'SceneCaptureType',
        0xa407 : 'GainControl',
        0xa408 : 'Contrast',
        0xa409 : 'Saturation',
        0xa40a : 'Sharpness',
        0xa40b : 'DeviceSettingDescription',
        0xa40c : 'SubjectDistanceRange',
        0xa420 : 'ImageUniqueID',
        0xa480 : 'GDALMetadata',
        0xa481 : 'GDALNoData',
        0xa500 : 'Gamma',
        0xc350 : 'FilmProductCode',
        0xc351 : 'ImageSourceEK',
        0xc352 : 'CaptureConditionsPAR',
        0xc353 : 'CameraOwner',
        0xc354 : 'SerialNumber',
        0xc355 : 'UserSelectGroupTitle',
        0xc356 : 'DealerIDNumber',
        0xc357 : 'CaptureDeviceFID',
        0xc358 : 'EnvelopeNumber',
        0xc359 : 'FrameNumber',
        0xc35a : 'FilmCategory',
        0xc35b : 'FilmGencode',
        0xc35c : 'ModelAndVersion',
        0xc35d : 'FilmSize',
        0xc35e : 'SBA_RGBShifts',
        0xc35f : 'SBAInputImageColorspace',
        0xc360 : 'SBAInputImageBitDepth',
        0xc361 : 'SBAExposureRecord',
        0xc362 : 'UserAdjSBA_RGBShifts',
        0xc363 : 'ImageRotationStatus',
        0xc364 : 'RollGuidElements',
        0xc365 : 'MetadataNumber',
        0xc366 : 'EditTagArray',
        0xc367 : 'Magnification',
        0xc36c : 'NativeXResolution',
        0xc36d : 'NativeYResolution',
        0xc36e : 'KodakEffectsIFD',
        0xc36f : 'KodakBordersIFD',
        0xc37a : 'NativeResolutionUnit',
        0xc418 : 'SourceImageDirectory',
        0xc419 : 'SourceImageFileName',
        0xc41a : 'SourceImageVolumeName',
        0xc427 : 'OceScanjobDesc',
        0xc428 : 'OceApplicationSelector',
        0xc429 : 'OceIDNumber',
        0xc42a : 'OceImageLogic',
        0xc44f : 'Annotations',
        0xc46c : 'PrintQuality',
        0xc46e : 'ImagePrintStatus',
        0xc4a5 : 'PrintIM',
        0xc612 : 'DNGVersion',
        0xc613 : 'DNGBackwardVersion',
        0xc614 : 'UniqueCameraModel',
        0xc615 : 'LocalizedCameraModel',
        0xc616 : 'CFAPlaneColor',
        0xc617 : 'CFALayout',
        0xc618 : 'LinearizationTable',
        0xc619 : 'BlackLevelRepeatDim',
        0xc61a : 'BlackLevel',
        0xc61b : 'BlackLevelDeltaH',
        0xc61c : 'BlackLevelDeltaV',
        0xc61d : 'WhiteLevel',
        0xc61e : 'DefaultScale',
        0xc61f : 'DefaultCropOrigin',
        0xc620 : 'DefaultCropSize',
        0xc621 : 'ColorMatrix1',
        0xc622 : 'ColorMatrix2',
        0xc623 : 'CameraCalibration1',
        0xc624 : 'CameraCalibration2',
        0xc625 : 'ReductionMatrix1',
        0xc626 : 'ReductionMatrix2',
        0xc627 : 'AnalogBalance',
        0xc628 : 'AsShotNeutral',
        0xc629 : 'AsShotWhiteXY',
        0xc62a : 'BaselineExposure',
        0xc62b : 'BaselineNoise',
        0xc62c : 'BaselineSharpness',
        0xc62d : 'BayerGreenSplit',
        0xc62e : 'LinearResponseLimit',
        0xc62f : 'DNGCameraSerialNumber',
        0xc630 : 'DNGLensInfo',
        0xc631 : 'ChromaBlurRadius',
        0xc632 : 'AntiAliasStrength',
        0xc633 : 'ShadowScale',
        0xc634 : 'DNGPrivateData',
        0xc635 : 'MakerNoteSafety',
        0xc65a : 'CalibrationIlluminant1',
        0xc65b : 'CalibrationIlluminant2',
        0xc65c : 'BestQualityScale',
        0xc660 : 'AliasLayerMetadata',
        0xfde8 : 'OwnerName',
        0xfde9 : 'SerialNumber2',
        0xfdea : 'Lens',
        0xfe4c : 'RawFile',
        0xfe4d : 'Converter',
        0xfe4e : 'WhiteBalance2',
        0xfe51 : 'Exposure',
        0xfe52 : 'Shadows',
        0xfe53 : 'Brightness',
        0xfe54 : 'Contrast2',
        0xfe55 : 'Saturation2',
        0xfe56 : 'Sharpness2',
        0xfe57 : 'Smoothness',
        0xfe58 : 'MoireFilter',
    }

    tiffEnumDataTypeLength = [0, 1, 1, 2, 4, 8, 1, 1, 2, 4, 8, 4, 4]
    tiffEnumDataType = ['', 'ubyte', 'string', 'ushort', 'ulong', 'urational', 'byte', 'undefined', 'short', 'long', 'rational', 'float', 'double']
    
    def __init__(self, fileObject):
        self.fileObject = fileObject
        self.version = 0
        self.channel = 3
        self.huffmanTable = {}
        self.huffmanTableCount = 0
        self.quantizationTable = {}
        self.colorQuantization = {}
        self.scanQuantization = {}
        self.scanFlag = False
        self.scanData = ''
        self.restartInterval = 0
        self.tagMap = {
            '\xff\x00' :self.tag_none,
            '\xff\xc0' :self.tag_sof0,
            '\xff\xc1' :self.tag_sof,
            '\xff\xc2' :self.tag_sof,
            '\xff\xc3' :self.tag_sof,
            '\xff\xc4' :self.tag_dht,
            '\xff\xc5' :self.tag_sof,
            '\xff\xc6' :self.tag_sof,
            '\xff\xc7' :self.tag_sof,
            '\xff\xc8' :self.tag_jpeg,
            '\xff\xc9' :self.tag_sof,
            '\xff\xca' :self.tag_sof,
            '\xff\xcb' :self.tag_sof,
            '\xff\xcc' :self.tag_dac,
            '\xff\xcd' :self.tag_sof,
            '\xff\xce' :self.tag_sof,
            '\xff\xcf' :self.tag_sof,
            '\xff\xd0' :self.tag_rst,
            '\xff\xd1' :self.tag_rst,
            '\xff\xd2' :self.tag_rst,
            '\xff\xd3' :self.tag_rst,
            '\xff\xd4' :self.tag_rst,
            '\xff\xd5' :self.tag_rst,
            '\xff\xd6' :self.tag_rst,
            '\xff\xd7' :self.tag_rst,
            '\xff\xd8' :self.tag_soi,
            '\xff\xd9' :self.tag_eoi,
            '\xff\xda' :self.tag_sos,
            '\xff\xdb' :self.tag_dqt,
            '\xff\xdc' :self.tag_dnl,
            '\xff\xdd' :self.tag_dri,
            '\xff\xde' :self.tag_dhp,
            '\xff\xdf' :self.tag_exp,
            '\xff\xe0' :self.tag_app0,
            '\xff\xe1' :self.tag_app1,
            '\xff\xe2' :self.tag_app,
            '\xff\xe3' :self.tag_app,
            '\xff\xe4' :self.tag_app,
            '\xff\xe5' :self.tag_app,
            '\xff\xe6' :self.tag_app,
            '\xff\xe7' :self.tag_app,
            '\xff\xe8' :self.tag_app,
            '\xff\xe9' :self.tag_app,
            '\xff\xea' :self.tag_app,
            '\xff\xeb' :self.tag_app,
            '\xff\xec' :self.tag_app,
            '\xff\xed' :self.tag_app,
            '\xff\xee' :self.tag_app,
            '\xff\xef' :self.tag_app,
            '\xff\xf0' :self.tag_jpg,
            '\xff\xf1' :self.tag_jpg,
            '\xff\xf2' :self.tag_jpg,
            '\xff\xf3' :self.tag_jpg,
            '\xff\xf4' :self.tag_jpg,
            '\xff\xf5' :self.tag_jpg,
            '\xff\xf6' :self.tag_jpg,
            '\xff\xf7' :self.tag_jpg,
            '\xff\xf8' :self.tag_jpg,
            '\xff\xf9' :self.tag_jpg,
            '\xff\xfa' :self.tag_jpg,
            '\xff\xfb' :self.tag_jpg,
            '\xff\xfc' :self.tag_jpg,
            '\xff\xfd' :self.tag_jpg,
            '\xff\xfe' :self.tag_com,
        }

    def start(self):
        if self.fileObject.read(2) == '\xff\xd8': # start of JPEG file
            tag = self.fileObject.read(2)
            while self.scanFlag == False and tag != None:
                try:
                    tag = self.tagMap[tag](tag)
                except KeyError:
                    tag = self.tag_unknown(tag)
            data = []
            LOGGER.log(CustomLoggingLevel.IMAGE_DEBUG, 'Start to read scan data.')
            d = self.fileObject.read(1)
            while self.scanFlag == True:
                if d == '\xff':
                    n = self.fileObject.read(1)
                    tag = d + n
                    if n == '\x00':
                        data.append(d)
                    elif n == '\xd9':
                        self.tag_eoi(tag)
                    elif '\xd0' <= n <= '\xf7':
                        self.tag_rst(tag)
                    else:
                        self.unexpected_tag(tag, '?')
                else:
                    data.append(d)
                d = self.fileObject.read(1)
            self.scanData = ''.join(data)
            LOGGER.log(CustomLoggingLevel.IMAGE_INFO, 'JPEG (ver %d.%d): %d*%dpx , channel: %d, fileLength: 0x%x b, scanDataLength: 0x%x b' % 
                        (self.version>>8, self.version&0xff, self.width, self.height, self.channel, self.fileObject.size, len(self.scanData)) )
        else:
            LOGGER.error('JPEG file start mark 0xFFD8 check failed.')

    def tag_none(self, tag):
        # 0xFF00 means 0xFF in scan data
        pass

    def tag_com(self, tag):
        # 0xFFFE Comment
        return self.reserve_tag()

    def tag_app0(self, tag):
        # 0xFFE0 APP0
        length = self.read_uint16()
        magic = self.fileObject.read(5)
        if magic != 'JFIF\x00':
            LOGGER.warning('[0x%x] Unbale to process magic %s in APP0.'%(self.fileObject.cur(), magic))
        self.version = self.read_uint16()
        self.fileObject.read(5)
        self.thumbnailX = self.fileObject.read_uint8()
        self.thumbnailY = self.fileObject.read_uint8()
        self.thumbnail = self.fileObject.read(length-16) # RGB pixel
        return self.find_tag('APP0')

    def tag_app1(self, tag):
        backCurPos = self.fileObject.cur()
        length = self.read_uint16()
        magic = self.fileObject.read(6)
        if magic != 'Exif\x00\x00':
            LOGGER.warning('[0x%x] Unbale to process magic %s in APP1.'%(self.fileObject.cur(), magic))
        self.read_tiff(length - 8, 'Exif')
        self.fileObject.change_cur(backCurPos+length)
        return self.find_tag('APP1')

    def tag_app(self, tag):
        # 0xFFE1~0xFFEE Application-specific
        appID = int(tag)-0xFFE0
        length = self.read_uint16() - 2
        data = self.fileObject.read(length)
        if not appID in [1, 2, 13 ,14]:
            LOGGER.log(CustomLoggingLevel.OTHER_DATA, '[0x%x] Tag APP%d found.'%(self.fileObject.cur() - length, appID))
        else:
            LOGGER.log(CustomLoggingLevel.OTHER_DATA, '[0x%x] Tag APP%d found, this tag usually not used in file.'%(self.fileObject.cur() - length, appID))
        return self.find_tag('APP%d'%appID)

    def tag_jpg(self, tag):
        # 0xFFF0~0xFFFD JPGn extention reserve
        return self.reserve_tag()

    def tag_jpeg(self, tag):
        # 0xFFC8 JPEG extention reserve
        return self.reserve_tag()

    def tag_dhp(self, tag):
        # #FFDE Define hierarchical progression
        self.unsupported_tag('0xffde', 'DHP')

    def tag_exp(self, tag):
        # 0xFFDF Expand reference image(s)
        self.unsupported_tag('0xffdf', 'EXP')

    def tag_dqt(self, tag):
        # 0xFFDB Define Quantization Table(s)
        length = self.read_uint16() - 2
        while length>0:
            firstBit = self.fileObject.read_uint8()
            tableID = firstBit & 0xf
            tableLength = (firstBit >> 4 + 1) * 64
            self.quantizationTable[tableID] = self.fileObject.read(tableLength)
            length -= tableLength + 1
        return self.find_tag('DQT')

    def tag_sof0(self, tag):
        # 0xFFC0 Start Of Frame 
        length = self.read_uint16()
        self.encodeType = 'sof0'
        self.bitsPerPixel = self.fileObject.read_uint8()
        self.height = self.read_uint16()
        self.width = self.read_uint16()
        if self.fileObject.read(1) != '\x03':
            LOGGER.error('[0x%x] Color type must be YCrCb(0x03) in JFIF.'%self.fileObject.cur())
        comp = self.fileObject.read(9)
        for i in range(3):
            self.colorQuantization[ord(comp[3*i])] = {'Horz' :ord(comp[3*i+1])>>4, 'Vert' :ord(comp[3*i+1])&0xf, 'Table' :ord(comp[3*i+2])}
        return self.find_tag('SOF0')

    def tag_sof(self, tag):
        # 0xFFC1~0xFFC7 0xFFC9~0xFFCF Start Of Frame 
        length = self.read_uint16()
        self.encodeType = 'sofx'
        self.bitsPerPixel = self.fileObject.read_uint8()
        self.height = self.read_uint16()
        self.width = self.read_uint16()
        if self.fileObject.read(1) != '\x03':
            LOGGER.error('[0x%x] Color type must be YCrCb(0x03) in JFIF.'%self.fileObject.cur())
        comp = self.fileObject.read(9)
        return self.find_tag('SOFx')

    def tag_dht(self, tag):
        # 0xFFC4 Define Huffman Table(s)
        length = self.read_uint16() - 2
        while length>0:
            tableIDByte = self.fileObject.read_uint8()
            tableID = (tableIDByte>>4)+(tableIDByte&0xf)
            if tableID<4:
                length -= self.huffmantree_decode(tableID)+1
            else:
                LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '[0x%x] Unknown part of huffman table'%(self.fileObject.cur()-1))
                self.fileObject.read(length) # skip unknown part
                break
        return self.find_tag('DHT')

    def huffmantree_decode(self, tableID):
        bitCount = []
        powerLength = 0
        self.huffmanTableCount += 1
        if self.huffmanTableCount>4:
            self.log(CustomLoggingLevel.IMAGE_INFO, 'Extra huffman table(DHT) found in jpg file.')
        for i in range(16):
            bitCount.append(ord(self.fileObject.read(1)))
            powerLength += bitCount[i]
        bitPower = self.fileObject.read(powerLength)
        huffmanTree = {}
        powerPos = 0
        lastBit = 0
        for i in range(16):
            if bitCount[i] == 0:
                if lastBit < 2**i:
                    lastBit = lastBit << 1
                continue
            while bitCount[i]>0:
                if i>1 and lastBit < 2**i:
                    lastBit = lastBit << 1
                huffmanTree[lastBit] = bitPower[powerPos]
                lastBit += 1
                powerPos += 1
                bitCount[i] -= 1
        self.huffmanTable[tableID] = huffmanTree
        return powerLength+16

    def tag_dnl(self, tag):
        # 0xFFDC Define number of lines
        self.unsupported_tag('0xffdc', 'DNL')

    def tag_dri(self, tag):
        # 0xFFDD Define Restart Interval
        length = self.read_uint16() - 2
        curPos = '[0x%x]' % self.fileObject.cur()
        self.restartInterval = self.read_uint16()
        if length != 2:
            LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '%s> %s'%(curPos, self.fileObject.read(length-2)))
        return self.find_tag('DRI')

    def tag_sos(self, tag):
        # 0xFFDA Start Of Scan
        self.scanFlag = True
        length = self.read_uint16() - 2
        if self.fileObject.read(1) != '\x03':
            LOGGER.error('[0x%x] Color type must be YCrCb(0x03) in JFIF.'%self.fileObject.cur())
        comp = self.fileObject.read(3)
        for i in range(3):
            self.scanQuantization[i] = {'AC' :ord(comp[i])>>4, 'DC' :ord(comp[i])&0xf}
        self.scanSs = self.fileObject.read(1)
        self.scanSe = self.fileObject.read(1)
        self.scanAh = ord(self.fileObject.read(1))
        self.scanAl = self.scanAh & 0xf
        self.scanAh = self.scanAh >> 4

    def tag_eoi(self, tag):
        # 0xFFD9 End Of Image
        self.scanFlag = False

    def tag_dac(self, tag):
        # 0xFFCC Define arithmetic conditioning table
        self.unsupported_tag('0xffcc', 'DAC')

    def tag_rst(self, tag):
        # 0xFFD0~0xFFD7 Restart
        if self.scanFlag == False:
            self.unexpected_tag(tag, 'RST')
        else:
            pass

    def tag_res(self, tag):
        # 0xFF02~0xFFBF Reserve
        return self.reserve_tag()

    def tag_soi(self, tag):
        # 0xFFD0 Start Of Image
        LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '[0x%x] A new file start tag found.'%self.fileObject.cur())

    def tag_unknown(self, tag):
        # unknown tag
        LOGGER.log(CustomLoggingLevel.IMAGE_INFO, '[0x%x] Unknown tag 0x%s found.'%(self.fileObject.cur(), tag.encode('hex')))

    def read_uint16(self, start=-1):
        high = ord(self.fileObject.read(1, start))<<8
        low = ord(self.fileObject.read(1))
        return high + low

    def read_uint32(self, start=-1):
        bit1 = ord(self.fileObject.read(1, start))<<24
        bit2 = ord(self.fileObject.read(1))<<16
        bit3 = ord(self.fileObject.read(1))<<8
        bit4 = ord(self.fileObject.read(1))
        return bit1 + bit2 + bit3 + bit4

    def read_tiff(self, length, tagName):
        tiffStartPos = self.fileObject.cur()
        if self.fileObject.read(2) == 'II':
            p_read_uint16 = self.fileObject.read_uint16
            p_read_uint32 = self.fileObject.read_uint32
        else:
            p_read_uint16 = self.read_uint16
            p_read_uint32 = self.read_uint32
        if p_read_uint16() != 0x2a:
            LOGGER.warning('[0x%x] TIFF data format magic check failed.'%tiffStartPos)
        dirEntryPos = p_read_uint32()
        self.read_tiff_ifd(tiffStartPos, p_read_uint16, p_read_uint32, dirEntryPos, tagName)

    def read_tiff_ifd(self, tiffStartPos, p_read_uint16, p_read_uint32, dirEntryPos, tagName):
        dirCount = 0
        while dirEntryPos != 0:
            entryCount = p_read_uint16(tiffStartPos+dirEntryPos)
            LOGGER.log(CustomLoggingLevel.IMAGE_DEBUG, '[%s] Tiff data start at 0x%x, directory index: %d, start at: 0x%x, entry count: %d.'%(tagName, tiffStartPos, dirCount,dirEntryPos, entryCount))
            for i in range(entryCount):
                try:
                    dirTag = p_read_uint16(tiffStartPos+dirEntryPos+2+12*i)
                    dataFormat = p_read_uint16()
                    nComponent = p_read_uint32()
                    dataLength = nComponent*self.tiffEnumDataTypeLength[dataFormat]
                    if dataLength > 4:
                        dataStartPos = p_read_uint32()
                        data = self.fileObject.read(dataLength, tiffStartPos+dataStartPos)
                    else:
                        data = self.fileObject.read(4)

                    if dirTag == 0x8769:
                        self.read_tiff_ifd(tiffStartPos, p_read_uint16, p_read_uint32, 
                                            p_read_uint32(tiffStartPos+dirEntryPos+10+12*i),
                                            'SubExif')
                    elif dirTag == 0xa005:
                        self.read_tiff_ifd(tiffStartPos, p_read_uint16, p_read_uint32, 
                                            p_read_uint32(tiffStartPos+dirEntryPos+10+12*i),
                                            'ExifInteroperability')

                    if dataFormat == 2:
                        LOGGER.log(CustomLoggingLevel.IMAGE_INFO, '[%s - %s](string)> %s'%(tagName, self.exifEnumTag[dirTag], data.replace('\x00', '')))
                    else:
                        LOGGER.log(CustomLoggingLevel.IMAGE_INFO, '[%s - %s](%s)> Hex:%s'%(tagName, self.exifEnumTag[dirTag], self.tiffEnumDataType[dataFormat], data.encode('hex')))
                except KeyError or IndexError:
                    LOGGER.error('[0x%x] Unable to decode dataformat or entrytag in tiff data, tagName: %s, dirTag: 0x%x, dataFormat: 0x%x, directory: %d/%d.'%(self.fileObject.cur(), tagName, dirTag, dataFormat, i, entryCount))
            dirCount += 1
            dirEntryPos = p_read_uint32(tiffStartPos+dirEntryPos+2+12*entryCount)

    def find_tag(self, tagName):
        if self.fileObject.read(1) != '\xFF':
            curPos = '[0x%x]' % self.fileObject.cur()
            LOGGER.error('%s Can\'t find 0xFF in end of %s.'%(curPos, tagName))
            data = []
            d = self.fileObject.read(1)
            while d != '\xFF':
                data.append(d)
                d = self.fileObject.read(1)
            LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '%s> %s'%(curPos, ''.join(data)))
        return '\xff' + self.fileObject.read(1)

    def reserve_tag(self):
        curPos = '[0x%x]' % self.fileObject.cur()
        length = self.read_uint16() - 2
        data = self.fileObject.read(length)
        LOGGER.log(CustomLoggingLevel.STEGO_DATA, '%s> %s'%(curPos, data))
        return self.find_tag('RESERVED TAG')

    def unsupported_tag(self, tag, tagName):
        self.warning('[0x%x] tag %s(%s) is unsupported.'%(self.fileObject.cur(), tagName, tag.encode('hex')))
        length = self.read_uint16() - 2
        self.fileObject.read(length)
        return self.find_tag(tagName)

    def unexpected_tag(self, tag, tagName):
        length = self.read_uint16()
        LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '[0x%x] tag %s(%s) appears unexpected, length: %d.'%(self.fileObject.cur()-2, tagName, tag.encode('hex'), length))
        self.fileObject.read(length-2)

    def showextradata(self, data, location):
        length = len(data)
        if length > 128:
            tmpFileObject = FileObject(data)
            LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '[0x%x] length: %x, type: %s'%(location, length, tmpFileObject.type()) )
        else:
            LOGGER.log(CustomLoggingLevel.EXTRA_DATA, '[0x%x] > %s'%(location, data) )

    def decode(self):
        # decode scan data of sof0
        return ''

    def detect(self):
        self.start()
        rowData = ''
        if self.encodeType == 'sof0':
            rowData = self.decode()
        else:
            LOGGER.warning('Only SOF0 is supported, scan data will not be decoded.')

        for d in self.fileObject.redundancy():
            self.showextradata(d['data'], d['start'])
        return rowData, self.channel*8, self.channel

# how does RST tag works?
# how to decode sof0 scan data
