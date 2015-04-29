## Manual for building AVR programmer ##

### Options in connection to computer ###

  * Serial port
  * USB serial driver (FTDI, ..)
  * Bluetooth serial port (SPP)

only attach RxD and TxD to serial port

use voltage level converters if you use different voltages on serial (bluetooth), AVR and programmed device

### SPI for ISP programming ###

connect signals:
|  **avrprog** | **programmed device** |
|:-------------|:----------------------|
|  MOSI | MISO |
|  MISO | MOSI |
|  SCK | SCK |
|  PORTB2 | RESET |

![http://wiki.avrprog.googlecode.com/git/avrprog-schematic.png](http://wiki.avrprog.googlecode.com/git/avrprog-schematic.png)

![http://wiki.avrprog.googlecode.com/git-history/master/avrprog-photo3.jpg](http://wiki.avrprog.googlecode.com/git-history/master/avrprog-photo3.jpg) ![http://wiki.avrprog.googlecode.com/git-history/master/avrprog-photo1.jpg](http://wiki.avrprog.googlecode.com/git-history/master/avrprog-photo1.jpg)