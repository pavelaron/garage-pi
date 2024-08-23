import network
import sys
import errno
import gc
import machine
import uos as os
import utime as time
import ujson as json
import ubinascii as binascii

from http_handler import HttpHandler
from network import WLAN, AP_IF

cache_filename = 'cache.json'

class ApHandler:
  def __init__(self):
    self._init_ap()

    gc.enable()
    gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
    gc.collect()

  def _get_pwd(self):
    if cache_filename not in os.listdir():
      return 'changeme'

    with open(cache_filename, 'r') as cache:
      data = json.load(cache)
      cache.close()

      return data['password']

  def _init_ap(self):
    uid = machine.unique_id()
    ssid = 'GaragePi-' + binascii.hexlify(uid).decode()[-4:].upper()
    pwd = self._get_pwd()

    ap = WLAN(AP_IF)
    ap.config(essid=ssid, password=pwd)
    ap.active(True)

    status = ap.ifconfig()

    print('Access point active')
    print(status)

    handler = HttpHandler(status[0], cache_filename)
    handler.listen()
