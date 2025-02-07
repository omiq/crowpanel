
import time
time.sleep(1)
# short sleep to CTRL+C if something goes wrong

# Wifi
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("WIFI", "WIFIPASSWORD")

# Wait for connect
max_wait = 10
# wait for connection
while max_wait > 0:
    """
        0   STAT_IDLE -- no connection and no activity,
        1   STAT_CONNECTING -- connecting in progress,
        -3  STAT_WRONG_PASSWORD -- failed due to incorrect password,
        -2  STAT_NO_AP_FOUND -- failed because no access point replied,
        -1  STAT_CONNECT_FAIL -- failed due to other problems,
        3   STAT_GOT_IP -- connection successful.
    """
    if wlan.status() < 0 or wlan.status() >= 3:
        # connection successful
        break
    max_wait -= 1
    print('waiting for connection... ' + str(max_wait))
    utime.sleep(1)
    
# check connection
if wlan.status() < 0:
    # No connection
    raise RuntimeError('network connection failed')
    exit(1)
else:
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

