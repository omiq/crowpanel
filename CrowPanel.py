# Write your code here :-)
# This library CrowPanel E-paper display, based on SSD1683 chips
# CrowPanel 5.79"
# CrowPanel 4.20" (not tested)
#
# Library is based on micropython frameBuffer
#
# V0.1.0 Dec 2025 Initial version
# V0.1.1 Dec 2025 Fixed initialization of screen
#
# Released under the MIT License (MIT).
# Copyright (c) 2025 Ignas Bukys 
# https://www.bukys.eu/components/crowpanel_5_79


from micropython import const
from time import sleep_ms
import framebuf
from ustruct import pack
from io import BytesIO
from machine import SPI, Pin

__version__ = (0, 1, 1)

# Display colour codes
COLOR_WHITE = const(1)
COLOR_BLACK = const(0)

#generic class for chip
class SSD1683(framebuf.FrameBuffer):
    '''Low-level controls for E-Paper chip'''

    # Constants for SSD1608 driver IC
    SET_DRIVER_CONTROL      = const(0x01)
    SET_GATE_VOLTAGE        = const(0x03)
    SET_SOURCE_VOLTAGE      = const(0x04)
    SET_DISPLAY_CONTROL     = const(0x07)
    SET_NON_OVERLAP         = const(0x0B)
    SET_BOOSTER_SOFT_START  = const(0x0C)
    SET_GATE_SCAN_START     = const(0x0F)
    SET_DEEP_SLEEP          = const(0x10)
    SET_DATA_MODE           = const(0x11)
    SET_DATA_MODE_SLAVE     = const(0x91)
    SET_SW_RESET            = const(0x12)
    SET_TEMP_WRITE          = const(0x1A)
    SET_TEMP_READ           = const(0x1B)
    SET_TEMP_CONTROL        = const(0x18)
    SET_TEMP_LOAD           = const(0x1A)
    SET_MASTER_ACTIVATE     = const(0x20)
    SET_DISP_CTRL1          = const(0x21)
    SET_DISP_CTRL2          = const(0x22)
    SET_WRITE_RAM           = const(0x24)
    SET_WRITE_ALTRAM        = const(0x26)
    SET_READ_RAM            = const(0x25)
    SET_VCOM_SENSE          = const(0x2B)
    SET_VCOM_DURATION       = const(0x2C)
    SET_WRITE_VCOM          = const(0x2C)
    SET_READ_OTP            = const(0x2D)
    SET_WRITE_LUT           = const(0x32)
    SET_WRITE_DUMMY         = const(0x3A)
    SET_WRITE_GATELINE      = const(0x3B)
    SET_WRITE_BORDER        = const(0x3C)
    SET_RAMXPOS             = const(0x44)
    SET_RAMYPOS             = const(0x45)
    SET_RAMXCOUNT           = const(0x4E)
    SET_RAMYCOUNT           = const(0x4F)
    SET_WRITE_RAM_SLAVE     = const(0xA4)
    SET_WRITE_ALTRAM_SLAVE  = const(0xA6)
    SET_RAMXPOS_SLAVE       = const(0xC4)
    SET_RAMYPOS_SLAVE       = const(0xC5)
    SET_RAMXCOUNT_SLAVE     = const(0xCE)
    SET_RAMYCOUNT_SLAVE     = const(0xCF)
    SET_NOP                 = const(0xFF)

    # Pins for communication
    LED_PIN = 41
    RESET_PIN = 47
    BUSY_PIN = 48
    DC_PIN = 46
    MOSI_PIN = 11
    SCK_PIN = 12
    CS_PIN = 45
    SCREEN_POWER_PIN = 7

    # Rotation
    ROTATION_0 = const(0)
    ROTATION_90 = const(1)
    ROTATION_180 = const(2)
    ROTATION_270 = const(3)


    def __init__(self, w, h, rotation=ROTATION_0):
        self._init_spi()
        self._init_buffer(w, h, rotation)
        self.FastMode1Init()
        self.HW_RESET()

    def _init_spi(self):
        #Set pin 7 to high level to activate the screen power
        Pin(self.SCREEN_POWER_PIN, Pin.OUT, value=1)

        self.cs = Pin(self.CS_PIN, Pin.OUT)
        self.dc = Pin(self.DC_PIN, Pin.OUT)
        self.rst = Pin(self.RESET_PIN, Pin.OUT)
        self.busy = Pin(self.BUSY_PIN, Pin.IN)

        self.spi = SPI(1,
            baudrate=4_000_000,
            sck=Pin(self.SCK_PIN),
            mosi=Pin(self.MOSI_PIN),
            polarity=0,
            phase=0,
            firstbit=SPI.MSB)

        self.spi.init()
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=1)
        self.rst.init(self.rst.OUT, value=1)
        self.busy.init(self.busy.IN, value=0)


    def _cmd(self, command, data=None):
        '''command and optional 1 byte of data'''
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([command]))
        self.cs(1)
        if data is not None:
            self._data(data)


    def _data(self, data):
        '''one byte of data'''
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([data]))
        self.cs(1)


    def _data_s(self, data):
        '''data in stream of bytes'''
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(pack('B'*len(data), *data))
        self.cs(1)


    def _init_buffer(self, w, h, rotation):
        self._rotation = rotation
        size = w * h // 8
        self.buffer = bytearray(size)

        if self._rotation == self.ROTATION_0 or self._rotation == self.ROTATION_180:
            self.width = w
            self.height = h
        else:
            self.width = w
            self.height = h
        super().__init__(self.buffer, self.width, self.height, framebuf.MONO_HLSB)
        print('Buffer width:{}, height:{}, size:{}'.format(self.width, self.height, size))


    def _wait_until_idle(self):
        while self.busy.value() == 1:
            sleep_ms(10)


    def HW_RESET(self):
        '''Perform Hardware reset'''
        sleep_ms(10)
        self.rst(0)
        sleep_ms(10)
        self.rst(1)
        sleep_ms(10)
        self._wait_until_idle()


    def EPD_Init(self):
        '''Intialize screen by doing Hard and Soft reset. Wait till busy pin low'''
        self.HW_RESET()
        self._wait_until_idle()
        self._cmd(self.SET_SW_RESET)
        self._wait_until_idle()


    def FastMode1Init(self):
        self.EPD_Init()

        self._cmd(self.SET_TEMP_CONTROL, 0x80)       # Read built-in temperature sensor

        self._cmd(self.SET_DISP_CTRL2, 0xB1)         # Load temperature value
        self._cmd(self.SET_MASTER_ACTIVATE)
        self._wait_until_idle()

        self._cmd(self.SET_TEMP_WRITE, 0x64)         # Write to temperature register
        self._data(0x00)

        self._cmd(self.SET_DISP_CTRL2, 0x91)         # Load temperature value
        self._cmd(self.SET_MASTER_ACTIVATE)
        self._wait_until_idle()

        self._cmd(self.SET_WRITE_BORDER, 0x1)        # 0x3 | 0-ry?kus 1-jokio 2-jokio
        self._wait_until_idle()


    def Display_Clear(self, count):
        '''Fill ram and altram of both chips with 0s and 1s'''
        self.SetRAMMP()
        self.SetRAMMA()
        self._cmd(self.SET_WRITE_RAM)
        self._data_s(b'\xFF' * count)
        self.SetRAMMA()
        self._cmd(self.SET_WRITE_ALTRAM)
        self._data_s(b'\x00' * count)
        self.SetRAMSP()
        self.SetRAMSA()
        self._cmd(self.SET_WRITE_RAM_SLAVE)
        self._data_s(b'\xFF' * count)
        self.SetRAMSA()
        self._cmd(self.SET_WRITE_ALTRAM_SLAVE)
        self._data_s(b'\x00' * count)


    def SetRAMMP(self):
        '''Data entry mode for ram primary'''
        self._cmd(self.SET_DATA_MODE, 0x02)      # Data Entry mode setting; 1 ?Y decrement, X increment
        self._cmd(self.SET_RAMXPOS)              # Set Ram X- address Start / End position
        self._data(0x31)                         # XStart, POR = 00h
        self._data(0x00)
        self._cmd(self.SET_RAMYPOS)              # Set Ram Y- address  Start / End position
        self._data(0x00)
        self._data(0x00)
        self._data(0x0f)
        self._data(0x01)


    def SetRAMMA(self):
        '''Data entry mode for altram primary'''
        self._cmd(self.SET_RAMXCOUNT, 0x31)
        self._cmd(self.SET_RAMYCOUNT, 0x00)
        self._data(0x00)


    def SetRAMSP(self):
        '''Data entry mode for ram Slave'''
        self._cmd(self.SET_DATA_MODE_SLAVE, 0x03)
        self._cmd(self.SET_RAMXPOS_SLAVE)
        self._data(0x00)
        self._data(0x31)
        self._cmd(self.SET_RAMYPOS_SLAVE)
        self._data(0x00)                # Set Ram Y- address  Start / End position
        self._data(0x00)
        self._data(0x0f)                # YEnd L
        self._data(0x01)


    def SetRAMSA(self):
        '''Data entry mode for altram Slave'''
        self._cmd(self.SET_RAMXCOUNT_SLAVE, 0x00)
        self._cmd(self.SET_RAMYCOUNT_SLAVE, 0x00)
        self._data(0x00)


    def Update(self):
        self._cmd(self.SET_DISP_CTRL2, 0xF7)
        self._cmd(self.SET_MASTER_ACTIVATE)
        self._wait_until_idle()


    def PartUpdate(self):
        self._cmd(self.SET_DISP_CTRL2, 0xDC)
        self._cmd(self.SET_MASTER_ACTIVATE)
        self._wait_until_idle()


    def FastUpdate(self):
        self._cmd(self.SET_DISP_CTRL2, 0xC7)
        self._cmd(self.SET_MASTER_ACTIVATE)
        self._wait_until_idle()


    def DeepSleep(self, mode=0x01):
        '''Send device to sleep and save power

        To wake up call EPD_Init()

        Parameters
        ----------
        int: mode
            0x00- Normal
            0x01- Mode1
            0x11- Mode2 (without RAM retention)
        '''
        self._cmd(self.SET_DEEP_SLEEP, mode)
        sleep_ms(5)


    def LoadImage(self, PosX, PosY, ImgName, ImgWidth, ImgHeight):
        ''' Load image into frame buffer on predefined possition

        Your file must be Black and White.
        You can use https://javl.github.io/image2cpp/
        Draw mode must be "Horizontal- 1 bit per pixel"
        framebuf.MONO_HLSB

        Parameters
        ----------
        int : Possition X on buffer
        int : Possition Y on buffer
        str : Image location
        int : Image width
        int : Image height

        Raises
        ------
        ValueError
            Sometime buffer construct method return it. I try to choose 2^X images of square dimensions
        '''
        # Create a bytearray to store the image data
        img_data = bytearray(ImgWidth * ImgHeight // 8)

        with open(ImgName, 'rb') as f:
            f.readinto(img_data)

        # Create a FrameBuffer object from the image data
        img_buf = framebuf.FrameBuffer(img_data, ImgWidth, ImgHeight, framebuf.MONO_HLSB)
        self.blit(img_buf, PosX, PosY)


class Screen_579(SSD1683):
    '''device specifics for CrowPanel 5.79" size'''

    # Resolution
    EPD_WIDTH = 792
    EPD_HEIGHT = 272

    def __init__(self):
        super().__init__(self.EPD_WIDTH, self.EPD_HEIGHT)
        self.Prepare((self.EPD_WIDTH+8) * self.EPD_HEIGHT // 8)


    def Prepare(self, count):
        '''Fill RAM and AltRAM of both chips with 0s and 1s
        for proper start'''
        self.SetRAMMP()
        self.SetRAMMA()
        self._cmd(self.SET_WRITE_RAM)
        self._data_s(b'\xFF' * count)
        self.SetRAMMA()
        self._cmd(self.SET_WRITE_ALTRAM)
        self._data_s(b'\x00' * count)
        self.SetRAMSP()
        self.SetRAMSA()
        self._cmd(self.SET_WRITE_RAM_SLAVE)
        self._data_s(b'\xFF' * count)
        self.SetRAMSA()
        self._cmd(self.SET_WRITE_ALTRAM_SLAVE)
        self._data_s(b'\x00' * count)


    def show(self, mode=1):
        '''Show buffer on screen.

        Parameters
        ----------
        mode : int, optional
            1- Fast;
            2- Partial;
            0- Full mode. Slowest but most clear view

        Raises
        ------
        ValueError
            Buffer size is not as expected according to screen dimension
        '''
        if len(self.buffer) != self.EPD_WIDTH * self.EPD_HEIGHT / 8:
            raise ValueError(f"Invalid frame buffer size. Expected {self.EPD_WIDTH * self.EPD_HEIGHT} bytes.")

        # prepare file-like object to work with
        bitmap_buffer = BytesIO(self.buffer)

        while True:
            chunk = bitmap_buffer.read(50)
            if not chunk: break

            self._cmd(self.SET_WRITE_RAM_SLAVE)
            self._data_s(chunk)

            # Simulate "partial data hidden" behavior (optional)
            bitmap_buffer.seek(-1, 1)  # Not recommended for BytesIO, can cause errors
            # on screen intersection, half of byte is invisible. On right screen- 4 MSB's,
            # on right- 4 LSB's. That why need to share same byte between two screens

            # Read the next chunk (if any)
            chunk = bitmap_buffer.read(50)
            if not chunk: break

            self._cmd(self.SET_WRITE_RAM)
            self._data_s(chunk)
        bitmap_buffer.close()

        if mode == 1:
            self.FastUpdate()
        elif mode == 2:
            self.PartUpdate()
        else:
            self.Update()


class Screen_420(SSD1683):
    '''device specifics for CrowPanel 4.2" size'''

    # Resolution
    EPD_HEIGHT = 300
    EPD_WIDTH = 400

    def __init__(self):
        raise NotImplementedError
        '''probably initialization may be different if screen
        orientation differs from 5.79 screen'''
        super().__init__(self.EPD_WIDTH, self.EPD_HEIGHT)
        self.Prepare(self.EPD_WIDTH * self.EPD_HEIGHT // 8)


    def Prepare(self, count):
        '''Fill RAM and AltRAM of chip with 0s and 1s
        for proper start'''
        self.SetRAMMP()
        self.SetRAMMA()
        self._cmd(self.SET_WRITE_RAM)
        self._data_s(b'\xFF' * count)
        self.SetRAMMA()
        self._cmd(self.SET_WRITE_ALTRAM)
        self._data_s(b'\x00' * count)


    def show(self, mode=1):
        '''Show buffer on screen.

        Parameters
        ----------
        mode : int, optional
            1- Fast;
            2- Partial;
            0- Full mode. Slowest but most clear view

        Raises
        ------
        ValueError
            Buffer size is not as expected according to screen dimension
        '''

        if len(self.buffer) != self.EPD_WIDTH * self.EPD_HEIGHT / 8:
            raise ValueError(f"Invalid frame buffer size. Expected {self.EPD_WIDTH * self.EPD_HEIGHT} bytes.")

        self._cmd(self.SET_WRITE_RAM)
        self._data_s(self.buffer)

        if mode == 1:
            self.FastUpdate()
        elif mode == 2:
            self.PartUpdate()
        else:
            self.Update()
