
import time
time.sleep(1)
# short sleep to CTRL+C if something goes wrong

# Wifi
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("WIFI", "WIFIPASSWORD")

# How many retries?
retries = 60

# wait for connection
while retries > 0:

    print('waiting for connection... ' + str(retries))
    time.sleep(4)
    if wlan.status() == 1010: 
        # connection successful on ESP32, other devices return different codes!
        break
    retries -= 1

    
# connection successful
print('wlan connected')
status = wlan.ifconfig()
print('IP address: ' + status[0])
print('subnet mask: ' + status[1])
print('gateway: ' + status[2])
print('DNS server: ' + status[3])

# E-Paper display
import CrowPanel as eink

# Instantiate a Screen
screen = eink.Screen_579()

# prepare framebuffer
screen.fill(eink.COLOR_WHITE)

# Get current IP address
ip_address = status[0]

# Output message
screen.text("WiFi Connected", 30, 80, eink.COLOR_BLACK)
screen.text("IP address: " + ip_address, 30, 100, eink.COLOR_BLACK)


#Load buffer to screen and display
screen.show()

