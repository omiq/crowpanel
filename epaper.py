
import time
time.sleep(1)
# short sleep to CTRL+C if something goes wrong

import CrowPanel as eink

# Instantiate a Screen
screen = eink.Screen_579()

# Test another font
# bassed on https://github.com/peterhinch/micropython-font-to-py/tree/master
#from writer import Writer
#import freesans20
#wri = Writer(screen, freesans20)

# prepare framebuffer
screen.fill(eink.COLOR_WHITE)#

#screen.LoadImage(30, 10, 'Images/CrowPanel_64_32.bin', 64, 32)
#Writer.set_textpos(screen, 130, 15)
#wri.printstring('CrowPanel ESP32 5.79" E-paper Display with 272*792 Resolution', True)

#diagonal line, to confirm correct display between 2 screens
screen.line(50, 50, 750, 222, eink.COLOR_BLACK)
screen.text("diagonal line, to confirm correct", 280, 115, eink.COLOR_BLACK)
screen.text("display between 2 screens", 295, 135, eink.COLOR_BLACK)

# Draw arc
screen.text("Draw ARC from two semi-ellipses", 30, 180, eink.COLOR_BLACK)
screen.ellipse(130,170, 50, 50, eink.COLOR_BLACK, True, 3)
screen.ellipse(130,175, 50, 50, eink.COLOR_WHITE, True, 3)

#screen.LoadImage(600, 50, 'Images/houseImg128.bin', 128, 128)
screen.text("Load BW image", 615, 50, eink.COLOR_BLACK)

#Writer.set_textpos(screen, 280, 250)
#wri.printstring('Inverted Color of another font')

#Load buffer to screen and display
screen.show()
