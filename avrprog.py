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

VERSION = "v1.0"

cpuList = [
    {
        'id': 'attiny13',
        'name': 'ATtiny13',
        'signature': [0x1e, 0x90, 0x07, ],
        'flashPageWords': 16,
        'flashPagesCount': 32,
        'eepromSize': 64,
        'fuses': ['fusel', 'fuseh', 'lock', 'cal'],
    }, {
        'id': 'attiny26',
        'name': 'ATtiny26',
        'signature': [0x1e, 0x91, 0x09, ],
        'flashPageWords': 16,
        'flashPagesCount': 64,
        'eepromSize': 128,
        'fuses': ['fusel', 'fuseh', 'lock', 'cal'],
    }, {
        'id': 'atmega48',
        'name': 'ATmega48',
        'signature': [0x1e, 0x92, 0x05, ],
        'flashPageWords': 32,
        'flashPagesCount': 64,
        'eepromSize': 256,
        'fuses': ['fusel', 'fuseh', 'fusee', 'lock', 'cal'],
    }, {
        'id': 'atmega48p',
        'name': 'ATmega48p',
        'signature': [0x1e, 0x92, 0x0a, ],
        'flashPageWords': 32,
        'flashPagesCount': 64,
        'eepromSize': 256,
        'fuses': ['fusel', 'fuseh', 'fusee', 'lock', 'cal'],
    }, {
        'id': 'atmega8',
        'name': 'ATmega8',
        'signature': [0x1e, 0x93, 0x07, ],
        'flashPageWords': 32,
        'flashPagesCount': 128,
        'eepromSize': 512,
        'fuses': ['fusel', 'fuseh', 'lock', 'cal'],
    }, {
        'id': 'atmega88',
        'name': 'ATmega88',
        'signature': [0x1e, 0x93, 0x0a, ],
        'flashPageWords': 32,
        'flashPagesCount': 128,
        'eepromSize': 512,
        'fuses': ['fusel', 'fuseh', 'fusee', 'lock', 'cal'],
    }, {
        'id': 'atmega88p',
        'name': 'ATmega88p',
        'signature': [0x1e, 0x93, 0x0f, ],
        'flashPageWords': 32,
        'flashPagesCount': 128,
        'eepromSize': 512,
        'fuses': ['fusel', 'fuseh', 'fusee', 'lock', 'cal'],
    }, {
        'id': 'atmega16',
        'name': 'ATmega16',
        'signature': [0x1e, 0x94, 0x03, ],
        'flashPageWords': 64,
        'flashPagesCount': 128,
        'eepromSize': 512,
        'fuses': ['fusel', 'fuseh', 'fusee', 'lock', 'cal'],
    }, {
        'id': 'atmega162',
        'name': 'ATmega162',
        'signature': [0x1e, 0x94, 0x04, ],
        'flashPageWords': 64,
        'flashPagesCount': 128,
        'eepromSize': 512,
        'fuses': ['fusel', 'fuseh', 'fusee', 'lock', 'cal'],
    }, {
        'id': 'atmega164a',
        'name': 'ATmega164p',
        'signature': [0x1e, 0x94, 0x0f, ],
        'flashPageWords': 64,
        'flashPagesCount': 128,
        'eepromSize': 512,
        'fuses': ['fusel', 'fuseh', 'fusee', 'lock', 'cal'],
    }, {
        'id': 'atmega164p',
        'name': 'ATmega164p',
        'signature': [0x1e, 0x94, 0x0a, ],
        'flashPageWords': 64,
        'flashPagesCount': 128,
        'eepromSize': 512,
        'fuses': ['fusel', 'fuseh', 'fusee', 'lock', 'cal'],
    }, {
        'id': 'atmega168',
        'name': 'ATmega168',
        'signature': [0x1e, 0x94, 0x06, ],
        'flashPageWords': 64,
        'flashPagesCount': 128,
        'eepromSize': 512,
        'fuses': ['fusel', 'fuseh', 'fusee', 'lock', 'cal'],
    }, {
        'id': 'atmega168p',
        'name': 'ATmega168p',
        'signature': [0x1e, 0x94, 0x0b, ],
        'flashPageWords': 64,
        'flashPagesCount': 128,
        'eepromSize': 512,
        'fuses': ['fusel', 'fuseh', 'fusee', 'lock', 'cal'],
    }, {
        'id': 'atmega32',
        'name': 'ATmega32',
        'signature': [0x1e, 0x95, 0x02, ],
        'flashPageWords': 64,
        'flashPagesCount': 256,
        'eepromSize': 1024,
        'fuses': ['fusel', 'fuseh', 'lock', 'cal'],
    }, {
        'id': 'atmega324p',
        'name': 'ATmega324P',
        'signature': [0x1e, 0x95, 0x08, ],
        'flashPageWords': 64,
        'flashPagesCount': 256,
        'eepromSize': 1024,
        'fuses': ['fusel', 'fuseh', 'fusee', 'lock', 'cal'],
    }, {
        'id': 'atmega324a',
        'name': 'ATmega324A',
        'signature': [0x1e, 0x95, 0x15, ],
        'flashPageWords': 64,
        'flashPagesCount': 256,
        'eepromSize': 1024,
        'fuses': ['fusel', 'fuseh', 'fusee', 'lock', 'cal'],
    }, {
        'id': 'atmega324pa',
        'name': 'ATmega324PA',
        'signature': [0x1e, 0x95, 0x11, ],
        'flashPageWords': 64,
        'flashPagesCount': 256,
        'eepromSize': 1024,
        'fuses': ['fusel', 'fuseh', 'fusee', 'lock', 'cal'],
    }, {
        'id': 'atmega328p',
        'name': 'ATmega328p',
        'signature': [0x1e, 0x95, 0x0f, ],
        'flashPageWords': 64,
        'flashPagesCount': 256,
        'eepromSize': 1024,
        'fuses': ['fusel', 'fuseh', 'fusee', 'lock', 'cal'],
    }, {
        'id': 'atmega64',
        'name': 'ATmega64',
        'signature': [0x1e, 0x96, 0x02, ],
        'flashPageWords': 128,
        'flashPagesCount': 256,
        'eepromSize': 2048,
        'fuses': ['fusel', 'fuseh', 'fusee', 'lock', 'cal'],
    }, {
        'id': 'atmega644',
        'name': 'ATmega644',
        'signature': [0x1e, 0x96, 0x09, ],
        'flashPageWords': 128,
        'flashPagesCount': 256,
        'eepromSize': 2048,
        'fuses': ['fusel', 'fuseh', 'fusee', 'lock', 'cal'],
    }, {
        'id': 'atmega644p',
        'name': 'ATmega644P',
        'signature': [0x1e, 0x96, 0x0A, ],
        'flashPageWords': 128,
        'flashPagesCount': 256,
        'eepromSize': 2048,
        'fuses': ['fusel', 'fuseh', 'fusee', 'lock', 'cal'],
    }, {
        'id': 'atmega128',
        'name': 'ATmega128',
        'signature': [0x1e, 0x97, 0x02, ],
        'flashPageWords': 128,
        'flashPagesCount': 512,
        'eepromSize': 4096,
        'fuses': ['fusel', 'fuseh', 'fusee', 'lock', 'cal'],
    }, {
        'id': 'atmega1284',
        'name': 'ATmega128',
        'signature': [0x1e, 0x97, 0x06, ],
        'flashPageWords': 128,
        'flashPagesCount': 512,
        'eepromSize': 4096,
        'fuses': ['fusel', 'fuseh', 'fusee', 'lock', 'cal'],
    }, {
        'id': 'atmega1284p',
        'name': 'ATmega128',
        'signature': [0x1e, 0x97, 0x05, ],
        'flashPageWords': 128,
        'flashPagesCount': 512,
        'eepromSize': 4096,
        'fuses': ['fusel', 'fuseh', 'fusee', 'lock', 'cal'],
    },
]


class Dbg:
    def __init__(self, verbose=3, gaugeLength=50, useColors=True):
        self.gaugeLength = gaugeLength
        self.loglevel = verbose
        self.useColors = useColors
        self.gaugeStrLen = 0
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

    def setVerbose(self, loglevel):
        self.loglevel = loglevel

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


class SrecException(Exception):
    def __init__(self, msg="SrecException."):
        self.msg = msg

    def __str__(self):
        return self.msg


def readBytesFromSrecFile(fileName, dataBuffer=[]):
    with open(fileName) as srecFile:
        loadSize = 0
        startAddr = None
        for srec in srecFile:
            # Strip some file content
            srec = srec.strip('\n').strip('\r')
            if not srec.startswith('S'):
                raise SrecException('this is not an motorola srec file')
            record = int(srec[1:2])
            bytesCount = int(srec[2:4], 16)
            if bytesCount * 2 + 4 != len(srec):
                raise SrecException('wrong srec line length')
            checkSum = 0x00
            for i in xrange(2, bytesCount * 2 + 4, 2):
                checkSum = (checkSum + int(srec[i:i + 2], 16)) & 0xff
            if checkSum != 0xff:
                raise SrecException('wrong srec checksum')
            addrLen = [2, 2, 3, 4, 0, 2, 0, 4, 3, 2, ][record]
            if addrLen == 0:
                raise SrecException('unknown record: ' + record)
            addr = int(srec[4:(4 + addrLen * 2)], 16)
            bytes = []
            for i in xrange(4 + addrLen * 2, bytesCount * 2 + 2, 2):
                bytes.append(int(srec[i:i + 2], 16))
            if record == 0:
                dbg.info('  srec header: ' + str(bytearray(bytes)), loglevel=3)
            elif record in (1, 2, 3):
                if startAddr is None:
                    startAddr = addr
                if len(dataBuffer) < addr:
                    dataBuffer += [0xff] * (addr - len(dataBuffer))
                dataBuffer[addr:addr + len(bytes)] = bytes
            loadSize += len(bytes)
        dbg.info('  loaded from address: 0x%06x: %s' % (startAddr, byteSize(loadSize, maxMult=10)))
    return dataBuffer


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


class AvrProgException(Exception):
    def __init__(self, msg="AvrProgException."):
        self.msg = msg

    def __str__(self):
        return self.msg


class NotConnectedException(AvrProgException):
    def __init__(self):
        pass

    def __str__(self):
        return "Not connected."


class NotRespondingException(AvrProgException):
    def __init__(self):
        pass

    def __str__(self):
        return "Device is not responding."


class NotReadyException(AvrProgException):
    def __init__(self, lines):
        self.lines = lines

    def __str__(self):
        ret = "Device is not ready"
        if not self.lines:
            return ret
        ret += ", received:"
        for line in self.lines:
            ret += "\n  %s" % line
        return ret


class WrongAnswerException(AvrProgException):
    def __init__(self, lines=None, expected=None):
        self.lines = lines
        self.expected = expected

    def __str__(self):
        ret = "Wrong answer from device"
        if self.lines:
            ret += ", received:"
            for line in self.lines:
                ret += "\n  %s" % line
        if self.expected:
            ret += "\nexpected: %s" % self.expected
        return ret


class NotEnoughtSpaceException(AvrProgException):
    def __init__(self, bufferSize, flashSize):
        self.bufferSize = bufferSize
        self.flashSize = flashSize

    def __str__(self):
        return "Not enought space in memmory, need %s, but %s only is free." % (byteSize(self.bufferSize), byteSize(self.flashSize))


class BufferIsEmptyException(AvrProgException):
    def __init__(self):
        pass

    def __str__(self):
        return "Buffer is empty."


class NotInBootloaderException(AvrProgException):
    def __init__(self):
        pass

    def __str__(self):
        return "Not in bootloader."


class NotInProgrammerException(AvrProgException):
    def __init__(self):
        pass

    def __str__(self):
        return "Not in programmer."


class UnknownCommandException(AvrProgException):
    def __init__(self, cmd):
        self.cmd = cmd

    def __str__(self):
        return "%s: command not found." % self.cmd


class UnknownCpuException(AvrProgException):
    def __init__(self, signature=[]):
        self.signature = signature

    def __str__(self):
        if self.signature:
            msg = 'UnknownCPU with signature:'
            for byte in self.signature:
                msg += ' 0x%02x' % byte
            msg += '.'
        else:
            msg = 'Error detecting CPU.'
        return msg


class NotExpectedCpuException(AvrProgException):
    def __init__(self, expected, detected):
        self.expected = expected
        self.detected = detected
        pass

    def __str__(self):
        expected = ''
        for cpu in self.expected:
            if expected:
                expected += ' or '
            expected += "'%s'" % cpu
        return "Expected CPU is %s, but detected: \'%s\'." % (expected, self.detected)


class SerialTerminal:
    def __init__(self, port):
        self.ser = None
        self.ser = serial.Serial(port, timeout=1)

    def __del__(self):
        if self.ser and self.ser.isOpen():
            self.ser.close()

    def cmdReceive(self, resultLines=None):
        if not self.ser or not self.ser.isOpen():
            raise NotConnectedException()
        lines = []
        if resultLines:
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
            if resultLines:
                if receivedLines < resultLines:
                    receivedLines += 1
                    dbg.gauge(100 * receivedLines / resultLines)
            dbg.log("<< " + line, color='blue')
            if line == 'ready':
                return lines
            lines.append(line)

    def cmdSend(self, cmd, result=True, disableResultError=False, retry=2, resultLines=None):
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
                return self.cmdReceive(resultLines=resultLines)
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


class AvrProg:
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

    def cmdSend(self, cmd, resultOk=[], resultLines=None):
        res = self.term.cmdSend(cmd, disableResultError=bool(resultOk), resultLines=resultLines)
        statusOk = False
        error = ""
        for line in res:
            if line in resultOk:
                statusOk = True
            else:
                if error:
                    error += ', '
                error += line
        if not statusOk and resultOk:
            raise AvrProgException("'%s'' error, received: %s" % (cmd, error))
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
            readBytesFromSrecFile(fileName, self.dataBuffer)
        elif fileName.endswith('.hex'):
            raise AvrProgException('Intel hex file is not supported yet, use motorola srec file instead or binary')
        else:
            self.dataBufer = []
            for byte in readBytesFromFile(fileName):
                self.dataBuffer.append(byte)

    def clearBuffer(self):
        self.dataBuffer = []

    def signBuffer(self):
        dbg.msg("signing for bootloader")
        if not len(self.dataBuffer):
            raise BufferIsEmptyException()
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
        print(line + '   ' * (16 - count) + (' ' if (count <= 8) else '') + ascii + ' ' * (16 - count) + '|')

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
                        print("*")
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
        res = self.term.cmdSend('hello')
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
            raise WrongAnswerException(res)
        dbg.info("  device: %s" % self.deviceName)
        if self.deviceCpu:
            dbg.info("  cpu: %s" % self.deviceCpu)
        if self.isBootloader():
            dbg.info("  space: %s" % byteSize(self.flashSize - 4, maxMult=100))
            dbg.info("  app: %s" % self.deviceCrcStatus)

    def flash(self):
        dbg.msg("writing flash")
        if not len(self.dataBuffer):
            raise BufferIsEmptyException()
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
                cmd = "spi flash write %04x %06x " % (self.flashPageSize, block['addr'])
            else:
                raise NotInBootloaderException()
            crc = 0
            for byte in block['data']:
                cmd += "%02x" % byte
                crc ^= byte
            cmd += "%02x" % crc
            self.cmdSend(cmd, ['flash ok'])
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

    def startBootloader(self):
        if self.isBootloader():
            return
        self.bootloader()
        self.hello()
        if not self.isBootloader():
            raise AvrProgException("Can not start bootloader.")

    def setCpu(self, cpu):
        dbg.msg("detecting CPU")
        if not self.isProgrammer():
            raise NotInProgrammerException()
        self.deviceCpu = ''
        res = self.term.cmdSend('spi enable', ['spi enable ok'])
        signature = []
        for line in res:
            cmd = line.split()
            if cmd[0] == 'signature':
                for sig in cmd[1:]:
                    signature.append(int(sig, 16))
        for attr in cpuList:
            if attr['signature'] == signature:
                self.deviceCpu = attr['id']
                self.flashPageSize = attr['flashPageWords'] * 2
                self.flashSize = attr['flashPagesCount'] * self.flashPageSize
                self.eepromSize = attr['eepromSize']
                self.fuses = attr['fuses']
                dbg.info("  detected cpu: " + attr['name'])
                break
        if not self.deviceCpu:
            raise UnknownCpuException(signature)
        dbg.info("  flash size: %s" % byteSize(self.flashSize - 4))
        if not cpu or 'auto' in cpu:
            return
        if self.deviceCpu not in cpu:
            raise NotExpectedCpuException(expected=cpu, detected=self.deviceCpu)

    def erase(self):
        if not self.isProgrammer():
            raise NotInProgrammerException()
        dbg.msg("erasing chip")
        self.cmdSend('spi erase', ['erase ok'])

    def spiDisable(self):
        if not self.isProgrammer():
            raise NotInProgrammerException()
        self.cmdSend('spi disable', ['spi disable ok'])

    def flashVerify(self):
        if not self.isProgrammer():
            raise NotInProgrammerException()
        if not len(self.dataBuffer):
            raise BufferIsEmptyException()
        dbg.msg("verifying flash")
        addrFrom = 0
        addrTo = len(self.dataBuffer) - 1
        res = self.term.cmdSend('spi flash read %06x %06x' % (addrFrom, addrTo), resultLines=(addrTo - addrFrom) / 32)
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
                    raise AvrProgException('CRC8 error')
                if addrFrom != addr:
                    raise AvrProgException('Returned Wrong address')
                for byte in byteList[:-1]:
                    if self.dataBuffer[addrFrom] != byte:
                        raise AvrProgException('Verify error, addr: %06x dataBuffer: %02x flash: %02x' % (addrFrom, self.dataBuffer[addrFrom], byte))
                    addrFrom += 1

    def flashDownload(self, addresses=[]):
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
        res = self.term.cmdSend('spi flash read %06x %06x' % (addrFrom, addrTo), resultLines=(addrTo - addrFrom) / 32)
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
                    raise AvrProgException('CRC8 error')
                self.dataBuffer += byteList[:-1]

    def spiFuse(self, fuseId, val=None):
        res = self.term.cmdSend('spi ' + fuseId + ((' %02x' % val) if val else ''))
        for line in res:
            cmd = line.split()
            if cmd[0] == fuseId:
                return int(cmd[1], 16)

    def fuse(self, params):
        if len(params) > 0:
            # first param is fuseId
            fuseId = params[0]
            # test if fuseId is correct
            if fuseId not in self.fuses:
                raise AvrProgException('Wrong fuse: %s' % fuseId)
            if len(params) > 1:
                # second param can by hex number for set fuse
                val = int(params[1], 16)
                # we can set only these fuses..
                if fuseId not in ('fusel', 'fuseh', 'fusee', 'lock'):
                    raise AvrProgException('Can not write fuse: %s' % fuseId)
                dbg.msg("writing %s: 0x%02x" % (fuseId, val))
                # store fuse and test if fuse is stored correctly
                if val != self.spiFuse(fuseId, val):
                    raise AvrProgException('Error setting fuse: %s to %02x' % (fuseId, val))
            else:
                # print the fuse
                print('%5s: 0x%02x' % (fuseId, self.spiFuse(fuseId)))
        else:
            # read and print all cnown fuses
            for fuseId in self.fuses:
                print('%5s: 0x%02x' % (fuseId, self.spiFuse(fuseId)))

    def printCpuList(self):
        print("{:^12} {:^12} {:^12}".format('cpu', 'flash', 'eeprom'))
        for attr in cpuList:
            print("{:<12} {:>12} {:>12}".format(attr['id'], byteSize(2 * attr['flashPageWords'] * attr['flashPagesCount']), byteSize(attr['eepromSize'])))


avrProg = AvrProg()
try:
    for arg in sys.argv[1:]:
        arg = arg.split(':')
        cmd = arg[0]
        arg = arg[1:]
        if cmd == 'help':
            print("avrprog - avr programmer")
            print("commands:")
            print("  help\n    print this help")
            print("  verbose:<loglevel>\n    set loglevel (0 == no output, 4 = print everything)")
            print("  clear\n    clear buffer")
            print("  load:<file>\n    load file in to buffer")
            print("  buffer\n    print content of buffer")
            print("  port:<serialport>\n    connect to serial port")
            print("  bootloader\n    try to start bootloader")
            print("  reboot\n    reboot device")
            print("  sign\n    sign content of buffer (use this for flashing from bootloader)")
            print("  cpu[:<cpuid>]\n    connect to CPU, and detect it (if cpuid not match, programmer exit with error)")
            print("  erase\n    chip erase, cause erase flash, eeprom and lockbits")
            print("  flash\n    write buffer to flash")
            print("  download\n    read flash to buffer")
            print("  verify\n    verify flash with buffer")
            print("  fuse[:<fuseid>[:<value>]]\n    read fuse(s) or write fuse. value is in hex")
        elif cmd == 'about':
            print("avrprog %s (c)2012 pavel.revak@gmail.com" % VERSION)
        elif cmd == 'cpulist':
            avrProg.printCpuList()
        elif cmd == 'verbose':
            dbg.setVerbose(int(arg[0]))
        elif cmd == 'clear':
            avrProg.clearBuffer()
        elif cmd == 'load':
            avrProg.readFile(arg[0])
        elif cmd == 'buffer':
            avrProg.printBuffer()
        elif cmd == 'port':
            avrProg.connect(arg[0])
        elif cmd == 'bootloader':
            avrProg.startBootloader()
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
        else:
            raise UnknownCommandException(cmd)
    if avrProg.isProgrammer() and avrProg.deviceCpu:
        avrProg.spiDisable()
    dbg.msg("done.")
except (IOError, serial.serialutil.SerialException, AvrProgException), e:
    dbg.error(e)
except (KeyboardInterrupt), e:
    dbg.error('interrupted by keyboard')
