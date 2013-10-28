#!/usr/bin/python
# name:    AVR programmer
# desc:    programming tool for Atmel AVR CPU
# author:  (c)2012 Pavel Revak <pavel.revak@gmail.com>
# licence: GPL

# TODO:
# - remove/optional pyserial dependency
# - add support for all avr
# - read intel hexfile format
# - save buffer
# - eeprom write
# - eeprom read
# - eeprom save
# - spi speed option
# - limited support for unknown AVR (flash size will be detected from signature)

import sys
import serial
import unittest

VERSION = "v2.0"

cpuList = [
    {
        'id': 'attiny13',
        'name': 'ATtiny13',
        'signature': (0x1e, 0x90, 0x07),
        'flashPageWords': 16,
        'flashPagesCount': 32,
        'eepromSize': 64,
        'fuses': ('low', 'high', 'lock', 'calib'),
    }, {
        'id': 'attiny26',
        'name': 'ATtiny26',
        'signature': (0x1e, 0x91, 0x09),
        'flashPageWords': 16,
        'flashPagesCount': 64,
        'eepromSize': 128,
        'fuses': ('low', 'high', 'lock', 'calib'),
    }, {
        'id': 'atmega48',
        'name': 'ATmega48',
        'signature': (0x1e, 0x92, 0x05),
        'flashPageWords': 32,
        'flashPagesCount': 64,
        'eepromSize': 256,
        'fuses': ('low', 'high', 'extend', 'lock', 'calib'),
    }, {
        'id': 'atmega48p',
        'name': 'ATmega48p',
        'signature': (0x1e, 0x92, 0x0a),
        'flashPageWords': 32,
        'flashPagesCount': 64,
        'eepromSize': 256,
        'fuses': ('low', 'high', 'extend', 'lock', 'calib'),
    }, {
        'id': 'atmega8',
        'name': 'ATmega8',
        'signature': (0x1e, 0x93, 0x07),
        'flashPageWords': 32,
        'flashPagesCount': 128,
        'eepromSize': 512,
        'fuses': ('low', 'high', 'lock', 'calib'),
    }, {
        'id': 'atmega88',
        'name': 'ATmega88',
        'signature': (0x1e, 0x93, 0x0a),
        'flashPageWords': 32,
        'flashPagesCount': 128,
        'eepromSize': 512,
        'fuses': ('low', 'high', 'extend', 'lock', 'calib'),
    }, {
        'id': 'atmega88p',
        'name': 'ATmega88p',
        'signature': (0x1e, 0x93, 0x0f),
        'flashPageWords': 32,
        'flashPagesCount': 128,
        'eepromSize': 512,
        'fuses': ('low', 'high', 'extend', 'lock', 'calib'),
    }, {
        'id': 'atmega16',
        'name': 'ATmega16',
        'signature': (0x1e, 0x94, 0x03),
        'flashPageWords': 64,
        'flashPagesCount': 128,
        'eepromSize': 512,
        'fuses': ('low', 'high', 'extend', 'lock', 'calib'),
    }, {
        'id': 'atmega162',
        'name': 'ATmega162',
        'signature': (0x1e, 0x94, 0x04),
        'flashPageWords': 64,
        'flashPagesCount': 128,
        'eepromSize': 512,
        'fuses': ('low', 'high', 'extend', 'lock', 'calib'),
    }, {
        'id': 'atmega164a',
        'name': 'atmega164A',
        'signature': (0x1e, 0x94, 0x0f),
        'flashPageWords': 64,
        'flashPagesCount': 128,
        'eepromSize': 512,
        'fuses': ('low', 'high', 'extend', 'lock', 'calib'),
    }, {
        'id': 'atmega164p',
        'name': 'ATmega164p',
        'signature': (0x1e, 0x94, 0x0a),
        'flashPageWords': 64,
        'flashPagesCount': 128,
        'eepromSize': 512,
        'fuses': ('low', 'high', 'extend', 'lock', 'calib'),
    }, {
        'id': 'atmega168',
        'name': 'ATmega168',
        'signature': (0x1e, 0x94, 0x06),
        'flashPageWords': 64,
        'flashPagesCount': 128,
        'eepromSize': 512,
        'fuses': ('low', 'high', 'extend', 'lock', 'calib'),
    }, {
        'id': 'atmega168p',
        'name': 'ATmega168p',
        'signature': (0x1e, 0x94, 0x0b),
        'flashPageWords': 64,
        'flashPagesCount': 128,
        'eepromSize': 512,
        'fuses': ('low', 'high', 'extend', 'lock', 'calib'),
    }, {
        'id': 'atmega32',
        'name': 'ATmega32',
        'signature': (0x1e, 0x95, 0x02),
        'flashPageWords': 64,
        'flashPagesCount': 256,
        'eepromSize': 1024,
        'fuses': ('low', 'high', 'lock', 'calib'),
    }, {
        'id': 'atmega324p',
        'name': 'ATmega324P',
        'signature': (0x1e, 0x95, 0x08),
        'flashPageWords': 64,
        'flashPagesCount': 256,
        'eepromSize': 1024,
        'fuses': ('low', 'high', 'extend', 'lock', 'calib'),
    }, {
        'id': 'atmega324a',
        'name': 'ATmega324A',
        'signature': (0x1e, 0x95, 0x15),
        'flashPageWords': 64,
        'flashPagesCount': 256,
        'eepromSize': 1024,
        'fuses': ('low', 'high', 'extend', 'lock', 'calib'),
    }, {
        'id': 'atmega324pa',
        'name': 'ATmega324PA',
        'signature': (0x1e, 0x95, 0x11),
        'flashPageWords': 64,
        'flashPagesCount': 256,
        'eepromSize': 1024,
        'fuses': ('low', 'high', 'extend', 'lock', 'calib'),
    }, {
        'id': 'atmega328p',
        'name': 'ATmega328p',
        'signature': (0x1e, 0x95, 0x0f),
        'flashPageWords': 64,
        'flashPagesCount': 256,
        'eepromSize': 1024,
        'fuses': ('low', 'high', 'extend', 'lock', 'calib'),
    }, {
        'id': 'atmega64',
        'name': 'ATmega64',
        'signature': (0x1e, 0x96, 0x02),
        'flashPageWords': 128,
        'flashPagesCount': 256,
        'eepromSize': 2048,
        'fuses': ('low', 'high', 'extend', 'lock', 'calib'),
    }, {
        'id': 'atmega644',
        'name': 'ATmega644',
        'signature': (0x1e, 0x96, 0x09),
        'flashPageWords': 128,
        'flashPagesCount': 256,
        'eepromSize': 2048,
        'fuses': ('low', 'high', 'extend', 'lock', 'calib'),
    }, {
        'id': 'atmega644p',
        'name': 'ATmega644P',
        'signature': (0x1e, 0x96, 0x0A),
        'flashPageWords': 128,
        'flashPagesCount': 256,
        'eepromSize': 2048,
        'fuses': ('low', 'high', 'extend', 'lock', 'calib'),
    }, {
        'id': 'atmega128',
        'name': 'ATmega128',
        'signature': (0x1e, 0x97, 0x02),
        'flashPageWords': 128,
        'flashPagesCount': 512,
        'eepromSize': 4096,
        'fuses': ('low', 'high', 'extend', 'lock', 'calib'),
    }, {
        'id': 'atmega1284',
        'name': 'ATmega128',
        'signature': (0x1e, 0x97, 0x06),
        'flashPageWords': 128,
        'flashPagesCount': 512,
        'eepromSize': 4096,
        'fuses': ('low', 'high', 'extend', 'lock', 'calib'),
    }, {
        'id': 'atmega1284p',
        'name': 'ATmega128',
        'signature': (0x1e, 0x97, 0x05),
        'flashPageWords': 128,
        'flashPagesCount': 512,
        'eepromSize': 4096,
        'fuses': ('low', 'high', 'extend', 'lock', 'calib'),
    },
]


class Dbg(object):
    def __init__(self, verbose=3, gaugeLength=50, useColors=True):
        self.gaugeLength = gaugeLength
        self.loglevel = verbose
        self.useColors = useColors
        self.gaugeStrLen = 0
        self.defaultVerbose = True
        self.colors = {
            'gray': '\033[1;90m',
            'red': '\033[1;91m',
            'green': '\033[1;92m',
            'yellow': '\033[1;93m',
            'blue': '\033[1;94m',
            'pink': '\033[1;95m',
            'cyan': '\033[1;96m',
            'silver': '\033[1;97m',
            'white': '\033[1;98m',
            'normal': '\033[0m',
        }

    @property
    def verbose(self):
        return self.loglevel

    @verbose.setter
    def verbose(self, value):
        self.loglevel = value
        self.defaultVerbose = False

    @property
    def isDefaultVerbose(self):
        return self.defaultVerbose

    def log(self, message, loglevel=3, color=None):
        if loglevel < self.loglevel:
            if self.gaugeStrLen:
                sys.stderr.write('\n')
                self.gaugeStrLen = 0
            if self.useColors and color in self.colors.keys():
                sys.stderr.write(self.colors[color] + str(message) + self.colors['normal'] + '\n')
            else:
                sys.stderr.write(str(message) + '\n')

    def gauge(self, percentage, loglevel=2):
        if loglevel < self.loglevel:
            gauge = self.gaugeLength * percentage / 100
            gaugeStr = '[%s%s] %3d%%' % ('=' * gauge, ' ' * (self.gaugeLength - gauge),  percentage)
            sys.stderr.write('\b' * self.gaugeStrLen + gaugeStr)
            self.gaugeStrLen = len(gaugeStr)
            sys.stderr.flush()

    def msg(self, message, loglevel=2, color='white'):
        self.log(message, loglevel=loglevel, color=color)

    def info(self, message, loglevel=2, color='gray'):
        self.log(message, loglevel=loglevel, color=color)

    def warning(self, message, loglevel=1, color='yellow'):
        self.log(message, loglevel=loglevel, color=color)

    def error(self, message, loglevel=1, color='red'):
        self.log(message, loglevel=loglevel, color=color)

dbg = Dbg()


def byteSize(val, mult=1024, maxMult=1, prefix=' ', sufix='Bytes', units=['', 'K', 'M', 'G', 'T', ]):
    i = 0
    while val >= (maxMult * mult) and i < len(units) - 1:
        val /= mult
        i += 1
    return "%d%s%s%s" % (val, prefix, units[i], sufix)


def readBytesFromFile(fileName, chunkSize=64):
    with open(fileName, 'rb') as binaryFile:
        while True:
            chunk = binaryFile.read(chunkSize)
            if not chunk:
                break
            for byte in bytearray(chunk):
                yield byte


class IntelHexException(Exception):
    def __init__(self, message="IntelHexException."):
        self.message = message

    def __str__(self):
        return self.message


class IntelHex(object):
    def __init__(self, dataBuffer=None):
        self.dataBuffer = dataBuffer if dataBuffer is not None else []

    def encodeFile(self, fileName):
        raise IntelHexException(
            "Intel hex file format is not supported yet, use motorola srec or binary file instead."
        )


class SrecException(Exception):
    def __init__(self, message="SrecException."):
        self.message = message

    def __str__(self):
        return self.message


class Srec(object):
    def __init__(self, dataBuffer=None):
        self.dataBuffer = dataBuffer if dataBuffer is not None else []
        self.loadSize = 0
        self.startAddr = None
        self.srecHeader = None

    def encodeRecord(self, srec):
        srec = srec.strip('\n').strip('\r')
        if not srec.startswith('S'):
            raise SrecException("This is not an motorola srec file.")
        record = int(srec[1:2])
        # validate length
        bytesCount = int(srec[2:4], 16)
        if bytesCount * 2 + 4 != len(srec):
            raise SrecException("Wrong srec line length.")
        # validate checksum
        checkSum = 0x00
        for i in xrange(2, bytesCount * 2 + 4, 2):
            checkSum = (checkSum + int(srec[i:i + 2], 16)) & 0xff
        if checkSum != 0xff:
            raise SrecException("Wrong srec checksum.")
        # address size
        addrSize = [2, 2, 3, 4, 0, 2, 0, 4, 3, 2, ][record]
        if addrSize == 0:
            raise SrecException("Unknown record: %s." % record)
        addr = int(srec[4:(4 + addrSize * 2)], 16)
        # load bytes
        bytes = []
        for i in xrange(4 + addrSize * 2, bytesCount * 2 + 2, 2):
            bytes.append(int(srec[i:i + 2], 16))
        if record == 0:
            # srec header record
            self.srecHeader = str(bytearray(bytes))
            dbg.info('  srec header: %s.' % self.srecHeader, loglevel=3)
        elif record in (1, 2, 3):
            # data sequence record
            if self.startAddr is None:
                self.startAddr = addr
            if len(self.dataBuffer) < addr:
                self.dataBuffer += [0xff] * (addr - len(self.dataBuffer))
            self.dataBuffer[addr:addr + len(bytes)] = bytes
        elif record == 5:
            # count of records in actual transmition
            # TODO
            pass
        elif record in (7, 8, 9):
            # end of transmition
            # TODO
            pass
        self.loadSize += len(bytes)

    def encodeLines(self, srecLines):
        for srec in srecLines:
            self.encodeRecord(srec)
        if self.startAddr is None:
            raise SrecException("No data section found in srec file.")

    def encodeFile(self, fileName):
        with open(fileName) as srecFile:
            self.encodeLines(srecFile)
        dbg.info('  loaded from address: 0x%06x: %s' % (
            self.startAddr,
            byteSize(self.loadSize, maxMult=10)
        ))


class TestSrec(unittest.TestCase):

    def setUp(self):
        self.srec = Srec()

    def testEncodeSrecLinesWrongFileFile(self):
        with self.assertRaises(SrecException) as context:
            self.srec.encodeLines(['abc'])
        self.assertEqual(context.exception.message, "This is not an motorola srec file.")

    def testEncodeSrecLongLine(self):
        with self.assertRaises(SrecException) as context:
            self.srec.encodeLines(['S0050000616263D3'])
        self.assertEqual(context.exception.message, "Wrong srec line length.")

    def testEncodeSrecShortLine(self):
        with self.assertRaises(SrecException) as context:
            self.srec.encodeLines(['S0070000616263D3'])
        self.assertEqual(context.exception.message, "Wrong srec line length.")

    def testEncodeSrecLinesNoDataSectionInSrecFile(self):
        with self.assertRaises(SrecException) as context:
            self.srec.encodeLines(['S0060000616263D3'])
        self.assertEqual(context.exception.message, "No data section found in srec file.")

    def testEncodeSrecWrongChecksum(self):
        with self.assertRaises(SrecException) as context:
            self.srec.encodeLines(['S006000061626300'])
        self.assertEqual(context.exception.message, "Wrong srec checksum.")

    def testEncodeSrecUnknownRecord(self):
        with self.assertRaises(SrecException) as context:
            self.srec.encodeLines(['S4060000616263D3'])
        self.assertEqual(context.exception.message, "Unknown record: 4.")

    def testEncodeSrecLoad16BitAddress(self):
        self.srec.encodeLines(['S1060000616263D3'])
        self.assertEqual(self.srec.dataBuffer, [0x61, 0x62, 0x63])

    def testEncodeSrecLoad24BitAddress(self):
        self.srec.encodeLines(['S207000000616263D2'])
        self.assertEqual(self.srec.dataBuffer, [0x61, 0x62, 0x63])

    def testEncodeSrecLoad32BitAddress(self):
        self.srec.encodeLines(['S30800000000616263D1'])
        self.assertEqual(self.srec.dataBuffer, [0x61, 0x62, 0x63])

    def testEncodeSrecLoadNoZeroAddress(self):
        self.srec.encodeLines(['S1060004616263CF'])
        self.assertEqual(self.srec.dataBuffer, [0xff, 0xff, 0xff, 0xff, 0x61, 0x62, 0x63])

    def testEncodeSrecLoadAppendToBuffer(self):
        self.srec = Srec([0x01, 0x02, 0x03])
        self.srec.encodeLines(['S1060004616263CF'])
        self.assertEqual(self.srec.dataBuffer, [0x01, 0x02, 0x03, 0xff, 0x61, 0x62, 0x63])


def crc16_update(crc, val, poly=0xa001):
    crc ^= (val & 0x00ff)
    i = 0
    while (i < 8):
        if (crc & 1):
            crc = (crc >> 1) ^ poly
        else:
            crc = (crc >> 1)
        i += 1
    return crc & 0xffff


def structuredString(data, indent='  ', actualIndent='\n'):
    if isinstance(data, list):
        return ''.join([structuredString(d, indent, actualIndent + indent) for d in data])
    return actualIndent + str(data)


class AvrProgException(Exception):
    def __init__(self, message=None, messages=None):
        self.message = message
        self.messages = messages

    def __str__(self):
        message = self.__class__.__name__
        if hasattr(self, 'message') and self.message:
            message += ": %s" % self.message
        if hasattr(self, 'messages') and self.messages:
            message += structuredString(self.messages)
        return message


class UnexpectedAnswerException(AvrProgException):
    def __init__(self, command, receivedLines, expectedLines):
        self.command = command
        self.receivedLines = receivedLines
        self.expectedLines = expectedLines

    @property
    def message(self):
        return "in answer to command: '%s'" % self.command

    @property
    def messages(self):
        return [
            "received:",
            self.receivedLines,
            "expected:",
            self.expectedLines,
        ]


class NotConnectedException(AvrProgException):
    @property
    def message(self):
        return "Not connected."


class NotRespondingException(AvrProgException):
    @property
    def message(self):
        return "Device is not responding."


class NotReadyException(AvrProgException):
    def __init__(self, lines):
        self.lines = lines

    @property
    def message(self):
        return "Device is not ready"

    @property
    def messages(self):
        return [
            'received:',
            self.lines
        ]

class NotEnoughtSpaceException(AvrProgException):
    def __init__(self, bufferSize, flashSize):
        self.bufferSize = bufferSize
        self.flashSize = flashSize

    @property
    def message(self):
        return "Not enought space in memmory, need %s, but %s only is free." % (
            byteSize(self.bufferSize),
            byteSize(self.flashSize)
        )


class BufferEmptyException(AvrProgException):
    @property
    def message(self):
        return "Buffer is empty."


class NotInBootloaderException(AvrProgException):
    @property
    def message(self):
        return "Not in bootloader."


class NotInProgrammerException(AvrProgException):
    @property
    def message(self):
        return "Not in programmer."


class UnknownCommandException(AvrProgException):
    def __init__(self, cmd):
        self.cmd = cmd

    @property
    def message(self):
        return "Unknown command '%s'." % self.message


class UnknownCpuException(AvrProgException):
    def __init__(self, signature):
        self.signature = signature

    @property
    def message(self):
        if not self.signature:
            return "Error detecting CPU."
        return 'Unknown CPU with signature: %s.' % ' '.join(
            ['0x%02x' % byte for byte in self.signature]
        )


class NotExpectedCpuException(AvrProgException):
    def __init__(self, expected, detected):
        self.expected = expected
        self.detected = detected

    @property
    def message(self):
        return "Detected CPU is %s but expected is %s." % (
            self.detected,
            ' or '.join(self.expected)
        )


class SerialTerminal(object):
    def __init__(self, port):
        self.ser = None
        self.ser = serial.Serial(port, timeout=1)

    def __del__(self):
        if self.ser and self.ser.isOpen():
            self.ser.close()

    def cmdReceive(self, expectedLinesCount=None):
        if not self.ser or not self.ser.isOpen():
            raise NotConnectedException()
        lines = []
        if expectedLinesCount:
            receivedLines = 0
        while True:
            line = self.ser.readline()
            if line == '':
                if lines:
                    raise NotReadyException(lines)
                raise NotRespondingException()
            line = line.strip()
            if line == '':
                continue
            if expectedLinesCount:
                if receivedLines < expectedLinesCount:
                    receivedLines += 1
                    dbg.gauge(100 * receivedLines / expectedLinesCount)
            dbg.log("<< " + line, color='blue')
            if line == 'ready':
                return lines
            lines.append(line)

    def cmdSend(self, cmd, result=True, disableResultError=False, retry=2, expectedLinesCount=None):
        if not self.ser or not self.ser.isOpen():
            raise NotConnectedException()
        dbg.log(">> " + cmd, color='cyan')
        self.ser.flushInput()
        self.ser.write(cmd)
        self.ser.write('\r\n\r\r')
        self.ser.flush()
        if not result:
            return []
        while retry > 0:
            try:
                return self.cmdReceive(expectedLinesCount=expectedLinesCount)
            except NotRespondingException, e:
                self.ser.write('\r\n')
                self.ser.flush()
                if not disableResultError:
                    dbg.warning('retrying', loglevel=2)
            except NotReadyException, e:
                if not disableResultError:
                    raise e
            retry -= 1
        if disableResultError:
            return None
        raise NotRespondingException()


class AvrProg(object):
    def __init__(self):
        self.term = None

        self.deviceName = ''
        self.deviceCpu = ''
        self.deviceVersion = ''
        self.deviceCrcStatus = ''
        self.deviceFlashMagic = 0x4321

        self.flashSize = 0
        self.flashPageSize = 0
        self.eepromSize = 0
        self.fuses = []

        self.dataBuffer = []

    def cmdSend(self, cmd, expectedLines=list(), expectedLinesCount=None):
        if not self.term:
            raise NotConnectedException()
        res = self.term.cmdSend(
            cmd,
            disableResultError=bool(expectedLines),
            expectedLinesCount=expectedLinesCount
        )
        statusOk = not expectedLines
        for line in res:
            if line in expectedLines:
                statusOk = True
        if not statusOk:
            raise UnexpectedAnswerException(cmd, res, expectedLines)
        return res

    def connect(self, port):
        dbg.msg("openning port: %s" % port)
        self.term = SerialTerminal(port)
        self.hello()

    def getDeviceName(self):
        return self.deviceName

    def isBootloader(self):
        return self.deviceName == 'avrboot'

    def isProgrammer(self):
        return self.deviceName == 'avrprog'

    def isKnownDevice(self):
        return self.deviceName in ('avrprog', 'avrboot')

    def isProgrammingDevice(self):
        return self.deviceName in ('avrprog', 'avrboot')

    def readFile(self, fileName=""):
        dbg.msg("loading file: %s" % fileName)
        if fileName.endswith('.srec'):
            srecFile = Srec(self.dataBuffer)
            srecFile.encodeFile(fileName)
        elif fileName.endswith('.hex'):
            hexFile = IntelHex(self.dataBuffer)
            hexFile.encodeFile(fileName)
        elif fileName.endswith('.bin'):
            self.dataBuffer = []
            for byte in readBytesFromFile(fileName):
                self.dataBuffer.append(byte)
        else:
            raise AvrProgException("Unsupported file format '%s'." % fileName.split('.')[-1])

    def clearBuffer(self):
        self.dataBuffer = []

    def signBuffer(self):
        dbg.msg("signing for bootloader")
        if not len(self.dataBuffer):
            raise BufferEmptyException()
        if not self.isBootloader():
            raise NotInBootloaderException()
        sizeLimit = self.flashSize - 4
        bufferSize = len(self.dataBuffer)
        if bufferSize > sizeLimit:
            raise NotEnoughtSpaceException(bufferSize=bufferSize, flashSize=sizeLimit)
        bufferCrc16 = 0
        for byte in self.dataBuffer:
            bufferCrc16 = crc16_update(bufferCrc16, byte)
        self.dataBuffer += [0xff] * (sizeLimit - bufferSize)
        self.dataBuffer += [bufferSize & 0xff, (bufferSize >> 8) & 0xff]
        self.dataBuffer += [bufferCrc16 & 0xff, (bufferCrc16 >> 8) & 0xff]

    def printHexLine(self, addr, data):
        if not data:
            return
        line = '%06x' % addr
        ascii = '  |'
        count = 0
        for byte in data:
            if count % 8 == 0:
                line += ' '
            count += 1
            line += ' %02x' % byte
            ascii += ('%c' % byte) if 0x20 <= byte < 0x7f else '.'
        line += '   ' * (16 - count)
        line += ' ' if (count <= 8) else ''
        line += ascii
        line += ' ' * (16 - count)
        line += '|'
        print line

    def printBuffer(self):
        dbg.msg("buffer hexdump:")
        addr = 0
        lineAddr = addr
        lineData = []
        previousLineAddr = addr
        previousLineData = []
        repeat = False
        for byte in self.dataBuffer:
            lineData.append(byte)
            addr += 1
            if addr % 16 == 0:
                if lineData == previousLineData:
                    if not repeat:
                        print "*"
                        repeat = True
                else:
                    repeat = False
                    self.printHexLine(lineAddr, lineData)
                previousLineData = lineData
                lineData = []
                previousLineAddr = lineAddr
                lineAddr = addr
        if repeat:
            self.printHexLine(previousLineAddr, previousLineData)
        self.printHexLine(lineAddr, lineData)

    def hello(self):
        self.deviceName = ''
        self.deviceCpu = ''
        self.deviceVersion = ''
        self.deviceCrcStatus = ''
        hello = False
        res = self.cmdSend('hello')
        for line in res:
            cmd = line.split()
            if cmd[0] == 'hello':
                hello = True
            elif cmd[0] == 'device':
                self.deviceName = cmd[1]
                if len(cmd) >= 3:
                    self.deviceVersion = cmd[2]
            elif cmd[0] == 'cpu':
                self.deviceCpu = cmd[1]
            elif cmd[0] == 'bootaddr':
                self.flashSize = int(cmd[1])
            elif cmd[0] == 'pagesize':
                self.flashPageSize = int(cmd[1])
            elif cmd[0] == 'magic':
                self.deviceFlashMagic = int(cmd[1])
            elif cmd[0] == 'crc':
                self.deviceCrcStatus = cmd[1]
        if not hello or not self.deviceName:
            raise UnexpectedAnswerException('hello', res)
        dbg.info("  device: %s" % self.deviceName)
        if self.deviceCpu:
            dbg.info("  cpu: %s" % self.deviceCpu)
        if self.isBootloader():
            dbg.info("  space: %s" % byteSize(self.flashSize - 4, maxMult=100))
            dbg.info("  app: %s" % self.deviceCrcStatus)

    def flash(self):
        dbg.msg("writing flash")
        if not len(self.dataBuffer):
            raise BufferEmptyException()
        if not self.isProgrammingDevice():
            raise NotInBootloaderException()
        addr = 0
        flashBlock = False
        blocks = []
        for byte in self.dataBuffer:
            if addr % self.flashPageSize == 0:
                block = {
                    'addr': addr,
                    'data': [],
                }
            block['data'].append(byte)
            if byte != 0xff:
                flashBlock = True
            addr += 1
            if addr % self.flashPageSize == 0:
                if flashBlock:
                    blocks.append(block)
                    flashBlock = False
        if flashBlock:
            blocks.append(block)
        blocksToWrite = len(blocks)
        blocksWrited = 0
        for block in blocks:
            if self.isBootloader():
                cmd = "flash %04x %04x " % (block['addr'], self.deviceFlashMagic)
            elif self.isProgrammer():
                cmd = "avr flash write %02x %06x " % (self.flashPageSize / 2, block['addr'])
            else:
                raise NotInBootloaderException()
            crc = 0
            for byte in block['data']:
                cmd += "%02x" % byte
                crc ^= byte
            cmd += "%02x" % crc
            self.cmdSend(cmd, ['avr flash write done', 'flash ok'])
            blocksWrited += 1
            dbg.gauge(blocksWrited * 100 / blocksToWrite)

    def reboot(self):
        if self.isKnownDevice():
            dbg.msg("rebooting")
            self.term.cmdSend('reboot', disableResultError=True)
        self.deviceName = ''

    def bootloader(self):
        if not self.isBootloader():
            dbg.msg("restarting in to bootloader")
            self.term.cmdSend('bootloader', disableResultError=True)
        self.deviceName = ''

    def startBootloader(self, cpu):
        if not self.isBootloader():
            self.bootloader()
            self.hello()
        if not self.isBootloader():
            raise AvrProgException("Can not start bootloader.")
        if not cpu or 'auto' in cpu:
            return
        if self.deviceCpu not in cpu:
            raise NotExpectedCpuException(expected=cpu, detected=self.deviceCpu)

    def setCpu(self, cpu):
        dbg.msg("detecting CPU")
        if not self.isProgrammer():
            self.reboot()
            self.hello()
            if not self.isProgrammer():
                raise NotInProgrammerException()
        self.deviceCpu = ''
        res = self.cmdSend('avr connect', ['avr connected'])
        signature = []
        for line in res:
            cmd = line.split()
            if cmd[0] == 'signature':
                for sig in cmd[1:]:
                    signature.append(int(sig, 16))
        for attr in cpuList:
            if list(attr['signature']) == signature:
                self.deviceCpu = attr['id']
                self.flashPageSize = attr['flashPageWords'] * 2
                self.flashSize = attr['flashPagesCount'] * self.flashPageSize
                self.eepromSize = attr['eepromSize']
                self.fuses = attr['fuses']
                dbg.info("  detected cpu: " + attr['name'])
                break
        if not self.deviceCpu:
            raise UnknownCpuException(signature)
        dbg.info("  flash size: %s" % byteSize(self.flashSize))
        dbg.info("  eeprom size: %s" % byteSize(self.eepromSize))
        if not cpu or 'auto' in cpu:
            return
        if self.deviceCpu not in cpu:
            raise NotExpectedCpuException(expected=cpu, detected=self.deviceCpu)

    def erase(self):
        if not self.isProgrammer():
            raise NotInProgrammerException()
        dbg.msg("erasing chip")
        self.cmdSend('avr flash erase', ['avr flash erase done'])

    def avrDisable(self):
        if not self.isProgrammer():
            raise NotInProgrammerException()
        self.cmdSend('avr disconnect', ['avr disconnected'])

    def flashVerify(self):
        if not self.isProgrammer():
            raise NotInProgrammerException()
        if not len(self.dataBuffer):
            raise BufferEmptyException()
        dbg.msg("verifying flash")
        addrFrom = 0
        addrTo = len(self.dataBuffer) - 1
        res = self.cmdSend(
            'avr flash read %06x %06x' % (addrFrom, addrTo),
            expectedLinesCount=(addrTo - addrFrom) / 32
        )
        for line in res:
            cmd = line.split()
            if cmd[0] == 'data':
                addr = int(cmd[1], 16)
                byteList = []
                byteStr = ''
                crc8 = 0x00
                for h in cmd[2]:
                    if not byteStr:
                        byteStr = h
                    else:
                        byteStr += h
                        byteStr = int(byteStr, 16)
                        crc8 ^= byteStr
                        byteList.append(byteStr)
                        byteStr = ''
                if crc8:
                    raise AvrProgException("CRC8 error")
                if addrFrom != addr:
                    raise AvrProgException("Returned Wrong address")
                for byte in byteList[:-1]:
                    if self.dataBuffer[addrFrom] != byte:
                        raise AvrProgException(
                            "Verify error, addr: %06x dataBuffer: %02x flash: %02x" % (
                                addrFrom,
                                self.dataBuffer[addrFrom],
                                byte
                            )
                        )
                    addrFrom += 1

    def flashDownload(self, addresses=list()):
        if not self.isProgrammer():
            raise NotInProgrammerException()
        dbg.msg("reading flash")
        addrFrom = 0
        addrTo = self.flashSize - 1
        if len(addresses) > 0:
            addrTo = int(addresses[0], 16)
        elif len(addresses) > 1:
            addrFrom = int(addresses[0], 16)
            addrTo = int(addresses[1], 16)
        self.dataBuffer = [0xff, ] * addrFrom
        res = self.cmdSend(
            'avr flash read %06x %06x' % (addrFrom, addrTo),
            expectedLinesCount=(addrTo - addrFrom) / 32
        )
        for line in res:
            cmd = line.split()
            if cmd[0] == 'data':
                # addr = int(cmd[1], 16)
                byteList = []
                byte = ''
                crc8 = 0x00
                for h in cmd[2]:
                    if not byte:
                        byte = h
                    else:
                        byte += h
                        byte = int(byte, 16)
                        crc8 ^= byte
                        byteList.append(byte)
                        byte = ''
                if crc8:
                    raise AvrProgException("CRC8 error")
                self.dataBuffer += byteList[:-1]

    def avrFuse(self, fuseId, val=None):
        cmd = 'avr fuse %s' % fuseId
        if val:
            cmd += ' %02x' % val
        res = self.cmdSend(cmd)
        for line in res:
            cmd = line.split()
            if cmd[1] == fuseId:
                return int(cmd[2], 16)
        raise AvrProgException("Error reading fuse %s" % fuseId)

    def fuse(self, params):
        if not params:
            # read and print all cnown fuses
            for fuseId in self.fuses:
                print "%5s: 0x%02x" % (fuseId, self.avrFuse(fuseId))
            return
        # first param is fuseId
        fuseId = params[0]
        # test if fuseId is correct
        if fuseId not in self.fuses:
            raise AvrProgException("Wrong fuse: %s" % fuseId)
        if len(params) > 1:
            # second param can by hex number for set fuse
            val = int(params[1], 16)
            # we can write only these fuses..
            if fuseId not in ('low', 'high', 'extend', 'lock'):
                raise AvrProgException("Can not write fuse '%s'" % fuseId)
            dbg.msg("writing %s: 0x%02x" % (fuseId, val))
            # store fuse and test if fuse is stored correctly
            if val != self.avrFuse(fuseId, val):
                raise AvrProgException("Error setting fuse '%s' to %02x" % (fuseId, val))
        else:
            # print the fuse
            print '%5s: 0x%02x' % (fuseId, self.avrFuse(fuseId))

    def printCpuList(self):
        print "{:^12} {:^12} {:^12}".format('cpu', 'flash', 'eeprom')
        for attr in cpuList:
            print "{:<12} {:>12} {:>12}".format(
                attr['id'],
                byteSize(2 * attr['flashPageWords'] * attr['flashPagesCount']),
                byteSize(attr['eepromSize'])
            )


class TestAvrProg(unittest.TestCase):

    def setUp(self):
        pass

    # def test_numbers_3_4(self):
    #     self.assertEqual(3 * 4, 12)

    # def test_strings_a_3(self):
    #     self.assertEqual('a' * 3, 'aaa')

avrProg = AvrProg()
try:
    for arg in sys.argv[1:]:
        arg = arg.split(':')
        cmd = arg[0]
        arg = arg[1:]
        if cmd == 'help':
            print "avrprog - avr programmer"
            print "commands:"
            print "  help\n    print this help"
            print "  verbose:<loglevel>\n    set loglevel (0 == no output, 4 = print everything)"
            print "  clear\n    clear buffer"
            print "  load:<file>\n    load file in to buffer"
            print "  buffer\n    print content of buffer"
            print "  port:<serialport>\n    connect to serial port"
            print "  bootloader\n    try to start bootloader"
            print "  reboot\n    reboot device"
            print "  sign\n    sign content of buffer (use this for flashing from bootloader)"
            print "  cpu[:<cpuid>]\n    connect to CPU, and detect it (optional validation)"
            print "  erase\n    chip erase, cause erase flash, eeprom and lockbits"
            print "  flash\n    write buffer to flash"
            print "  download\n    read flash to buffer"
            print "  verify\n    verify flash with buffer"
            print "  fuse[:<fuseid>[:<value>]]\n    read fuse(s) or write fuse. value is in hex"
        elif cmd == 'about':
            print "avrprog %s (c)2012-2013 pavel.revak@gmail.com" % VERSION
        elif cmd == 'cpulist':
            avrProg.printCpuList()
        elif cmd == 'verbose':
            dbg.verbose = int(arg[0])
        elif cmd == 'clear':
            avrProg.clearBuffer()
        elif cmd == 'load':
            avrProg.readFile(arg[0])
        elif cmd == 'buffer':
            avrProg.printBuffer()
        elif cmd == 'port':
            avrProg.connect(arg[0])
        elif cmd == 'bootloader':
            avrProg.startBootloader(arg[0:])
        elif cmd == 'reboot':
            avrProg.reboot()
        elif cmd == 'sign':
            avrProg.signBuffer()
        elif cmd == 'cpu':
            avrProg.setCpu(arg[0:])
        elif cmd == 'erase':
            avrProg.erase()
        elif cmd == 'flash':
            avrProg.flash()
        elif cmd == 'download':
            avrProg.flashDownload(arg[0:])
        elif cmd == 'verify':
            avrProg.flashVerify()
        elif cmd == 'fuse':
            avrProg.fuse(arg[0:])
        elif cmd == 'test':
            if dbg.isDefaultVerbose:
                dbg.verbose = 0
            unittest.main(argv=[sys.argv[0]] + arg[0:])
        else:
            raise UnknownCommandException(cmd)
    if avrProg.isProgrammer() and avrProg.deviceCpu:
        avrProg.avrDisable()
    dbg.msg("done.")
except (
    IOError,
    serial.serialutil.SerialException,
    AvrProgException,
    UnexpectedAnswerException,
    SrecException,
    IntelHexException
) as e:
    dbg.error(e)
except (KeyboardInterrupt), e:
    dbg.error("interrupted by keyboard")
