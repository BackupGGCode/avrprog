#!/usr/bin/python

# name:    AVR programmer
# desc:    programming tool for Atmel AVR CPU
# author:  (c)2012 Pavel Revak <pavel.revak@gmail.com>
# licence: GPL

# TODO:
# - remove pyserial dependency
# - add support for all avr
# - read intel hexfile format
# - raaf motorola hexfile format
# - save buffer
# - eeprom write
# - eeprom read
# - buffer save

import sys
import serial

VERSION = "v1.0"

cpuList = {
    'atmega8': {
        'name': 'ATmega8',
        'signature': [ 0x1e, 0x93, 0x07, ],
        'flashPageWords': 32,
        'flashPagesCount': 128,
        'eepromSize': 512,
    },
}

class Dbg:
    def __init__(self, verbose = 3, graphLength = 50, useColors = True):
        self.graphLength = graphLength
        self.loglevel = verbose
        self.useColors = useColors
        self.graphStrLen = 0
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
    def log(self, message, loglevel = 3, color = None):
        if loglevel < self.loglevel:
            if self.graphStrLen:
                sys.stderr.write('\n')
                self.graphStrLen = 0
            if self.useColors and color in self.colors.keys():
                sys.stderr.write(self.colors[color] + str(message) + self.colors['normal'] + '\n')
            else:
                sys.stderr.write(str(message) + '\n')
    def graph(self, percentage, loglevel = 2):
        if loglevel < self.loglevel:
            graph = self.graphLength * percentage / 100
            graphStr = '[%s%s] %3d%%' % ('=' * graph, ' ' * (self.graphLength - graph),  percentage)
            sys.stderr.write('\b' * self.graphStrLen + graphStr)
            self.graphStrLen = len(graphStr)
            sys.stderr.flush()
    def msg(self, message, loglevel = 2, color = 'white'):
        self.log(message, loglevel = loglevel, color = color)
    def info(self, message, loglevel = 2, color = 'gray'):
        self.log(message, loglevel = loglevel, color = color)
    def warning(self, message, loglevel = 1, color = 'yellow'):
        self.log(message, loglevel = loglevel, color = color)
    def error(self, message, loglevel = 1, color = 'red'):
        self.log(message, loglevel = loglevel, color = color)

dbg = Dbg()



def readBytesFromFile(fileName, chunkSize = 64):
    with open(fileName, 'rb') as f:
        while True:
            chunk = f.read(chunkSize)
            if not chunk:
                break
            for byte in bytearray(chunk):
                yield byte


def crc16_update(crc, val, poly = 0xa001):
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
    def __init__(self, msg = "AvrProgException."):
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
        ret =  "Device is not ready"
        if not self.lines:
            return ret
        ret += ", received:"
        for line in self.lines:
            ret += "\n  %s" % line
        return ret

class WrongAnswerException(AvrProgException):
    def __init__(self, lines = None, expected = None):
        self.lines = lines
        self.expected = expected
    def __str__(self):
        ret = "Wrong answer from device"
        if self.lines:
            ret += ", received:"
            for line in self.lines:
                ret += "\n  %s" % line
        if self.expected:
            ret += "\nexpected: %s" % expected
        return ret

class NotEnoughtSpaceException(AvrProgException):
    def __init__(self, bufferSize, flashSize):
        self.bufferSize = bufferSize
        self.flashSize = flashSize
    def __str__(self):
        return "Not enought space in memmory, need %d, but %d Bytes only is free." % (self.bufferSize, self.flashSize)

class BufferIsEmpty(AvrProgException):
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
    def __init__(self, signature = []):
        self.signature = signature
    def __str__(self):
        msg = 'Unknown CPU'
        if self.signature:
            msg += ' with signature:'
            for byte in self.signature:
                msg += ' 0x%02x' % byte
        msg += '.'
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
        self.ser = serial.Serial(port, timeout = .5)

    def __del__(self):
        if self.ser and self.ser.isOpen():
            self.ser.close()

    def cmdReceive(self):
        if not self.ser or not self.ser.isOpen():
            raise NotConnectedException()
        lines = []
        while True:
            line = self.ser.readline()
            if line == '':
                if lines:
                    raise NotReadyException(lines)
                raise NotRespondingException()
            line = line.strip()
            if line == '':
                continue
            dbg.log("<< " + line, color = 'blue')
            if line == 'ready':
                return lines
            lines.append(line)


    def cmdSend(self, cmd, result = True, disableResultError = False, retry = 2):
        if not self.ser or not self.ser.isOpen():
            raise NotConnectedException()
        dbg.log(">> " + cmd, color = 'cyan')
        self.ser.flushInput()
        self.ser.write(cmd)
        self.ser.write('\r\n\r\r')
        self.ser.flush()
        if not result:
            return []
        while retry > 0:
            try:
                return self.cmdReceive()
            except NotRespondingException, e:
                self.ser.write('\r\n')
                self.ser.flush()
                if not disableResultError:
                    dbg.warning('retrying', loglevel = 2)
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

        self.buffer = []
        self.bufferSize = 0
        self.bufferCrc16 = 0


    def cmdSend(self, cmd, resultOk = []):
        res = self.term.cmdSend(cmd, disableResultError = bool(resultOk))
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

    def readFile(self, fileName):
        dbg.msg("loading file: %s" % fileName)
        for byte in readBytesFromFile(fileName):
            self.buffer.append(byte)
            self.bufferSize += 1
            self.bufferCrc16 = crc16_update(self.bufferCrc16, byte)

    def signBuffer(self):
        dbg.msg("signing for bootloader")
        if not len(self.buffer):
            raise BufferIsEmpty()
        if not self.isBootloader():
            raise NotInBootloaderException()
        sizeLimit = self.flashSize - 4
        if self.bufferSize > sizeLimit:
            raise NotEnoughtSpaceException(bufferSize = self.bufferSize, flashSize = sizeLimit)
        self.buffer += [0xff] * (sizeLimit - self.bufferSize)
        self.buffer += [self.bufferSize & 0xff, (self.bufferSize >> 8) & 0xff]
        self.buffer += [self.bufferCrc16 & 0xff, (self.bufferCrc16 >> 8) & 0xff]

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
        print line + '   ' * (16 - count) + (' ' if (count < 8) else '')  + ascii + ' ' * (16 - count) + '|'


    def printBuffer(self):
        dbg.msg("buffer hexdump:")
        addr = 0
        lineAddr = addr
        lineData = []
        previousLineAddr = addr
        previousLineData = []
        repeat = False
        for byte in self.buffer:
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
            dbg.info("  space: %d bytes" % (self.flashSize - 4))
            dbg.info("  app: %s" % self.deviceCrcStatus)

    def flash(self):
        dbg.msg("writing flash")
        if not len(self.buffer):
            raise BufferIsEmpty()
        if not self.isProgrammingDevice():
            raise NotInBootloaderException()
        addr = 0
        flashBlock = False
        blocks = []
        for byte in self.buffer:
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
            self.cmdSend(cmd, 'flash ok')
            blocksWrited += 1
            dbg.graph(blocksWrited * 100 / blocksToWrite)


    def reboot(self):
        if self.isKnownDevice():
            dbg.msg("rebooting")
            self.term.cmdSend('reboot', disableResultError = True)
        self.deviceName = ''

    def bootloader(self):
        if not self.isBootloader():
            dbg.msg("restarting in to bootloader")
            self.term.cmdSend('bootloader', disableResultError = True)
        self.deviceName = ''

    def startBootloader(self):
        if self.isBootloader():
            return
        self.bootloader()
        self.hello()
        if not self.isBootloader():
            raise AvrProgException("Can not start bootloader.")

    def setCpu(self, cpu):
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
        for cpuId, attr in cpuList.iteritems():
            if attr['signature'] == signature:
                self.deviceCpu = cpuId
                self.flashPageSize = attr['flashPageWords'] * 2
                self.flashSize = attr['flashPagesCount'] * self.flashPageSize
                dbg.info("  detected cpu: " + attr['name'])
        if not self.deviceCpu:
            raise UnknownCpuException(signature)
        if not cpu or 'auto' in cpu:
            return
        if cpuId not in cpu:
            raise NotExpectedCpuException(expected = cpu, detected = self.deviceCpu)

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
        if not len(self.buffer):
            raise BufferIsEmpty()
        dbg.msg("verifying flash")
        addrFrom = 0
        addrTo = len(self.buffer) - 1
        res = self.term.cmdSend('spi flash read %06x %06x' % (addrFrom, addrTo))
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
                    AvrProgException('CRC8 error')
                if addrFrom != addr:
                    raise AvrProgException('Returned Wrong address')
                for byte in byteList[:-1]:
                    if self.buffer[addrFrom] != byte:
                        raise AvrProgException('Verify error, addr: %06x buffer: %02x flash: %02x' % (addrFrom, self.buffer[addrFrom], byte))
                    addrFrom += 1


    def flashDump(self, addresses = []):
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
        self.buffer = [0xff,] * addrFrom
        res = self.term.cmdSend('spi flash read %06x %06x' % (addrFrom, addrTo))
        for line in res:
            cmd = line.split()
            if cmd[0] == 'data':
                addr = int(cmd[1], 16)
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
                    AvrProgException('CRC8 error')
                self.buffer += byteList[:-1]

    def spiFuse(self, fuseId, val = None):
        res = self.term.cmdSend('spi ' + fuseId + ((' %02x' % val) if val else ''))
        for line in res:
            cmd = line.split()
            if cmd[0] == fuseId:
                return int(cmd[1], 16)

    def fuse(self, fuseId = None, val = None):
        if not fuseId:
            for fuseId in ('fusel', 'fuseh', 'fusee', 'lock', 'cal'):
                print '%5s: 0x%02x' % (fuseId, self.spiFuse(fuseId))
        elif not val and fuseId in  ('fusel', 'fuseh', 'fusee', 'lock', 'cal'):
            print '%5s: 0x%02x' % (fuseId, self.spiFuse(fuseId))
        elif val and fuseId in ('fusel', 'fuseh', 'fusee', 'lock'):
            val = int(val[0], 16)
            if val != self.spiFuse(fuseId, val):
                AvrProgException('Error setting %s to %02x' % (fuseId, val))


try:
    avrProg = AvrProg()
    for arg in sys.argv[1:]:
        arg = arg.split(':')
        cmd = arg[0]
        arg = arg[1:]
        if cmd == 'help':
            print "avrprog - avr programmer"
            print "commands:"
            print "  help\n    print this help"
            print "  verbose:<loglevel>\n    set loglevel (0 == no output, 4 = print everything)"
            print "  load:<file>\n    load file in to buffer"
            print "  buffer\n    print content of buffer"
            print "  port:<serialport>\n    connect to serial port"
            print "  bootloader\n    try to start bootloader"
            print "  reboot\n    reboot device"
            print "  sign\n    sign content of buffer (use this for flashing from bootloader)"
            print "  flash\n    write buffer to flash"
        elif cmd == 'about':
            print "avrprog %s (c)2012 pavel.revak@gmail.com" % VERSION
        elif cmd == 'verbose':
            dbg.setVerbose(int(arg[0]))
        elif cmd == 'load':
            avrProg.readFile(arg[0])
        elif cmd == 'buffer':
            avrProg.printBuffer()
        elif cmd =='port':
            avrProg.connect(arg[0])
            avrProg.hello()
        elif cmd =='bootloader':
            avrProg.startBootloader()
        elif cmd =='reboot':
            avrProg.reboot()
        elif cmd =='cpu':
            avrProg.setCpu(arg[0:])
        elif cmd =='sign':
            avrProg.signBuffer()
        elif cmd =='flash':
            avrProg.flash()
        elif cmd =='flashdump':
            avrProg.flashDump(arg[0:])
        elif cmd =='flashverify':
            avrProg.flashVerify()
        elif cmd =='erase':
            avrProg.erase()
        elif cmd == 'fuses':
            avrProg.fuse()
        elif cmd == 'fusel':
            avrProg.fuse('fusel', arg[0:])
        elif cmd == 'fuseh':
            avrProg.fuse('fuseh', arg[0:])
        elif cmd == 'fusee':
            avrProg.fuse('fusee', arg[0:])
        else:
            raise UnknownCommandException(cmd)
    if avrProg.isProgrammer() and avrProg.deviceCpu:
        avrProg.spiDisable()
    dbg.msg("done.")
except (IOError, serial.serialutil.SerialException, AvrProgException), e:
    dbg.error(e)
except (KeyboardInterrupt), e:
    dbg.error('interrupted by keyboard')


