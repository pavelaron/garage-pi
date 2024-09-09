import network
import sys
import errno
import gc
import machine
import asyncio
import uos as os
import utime as time
import ujson as json
import ubinascii as binascii

from micropython import const
from machine import WDT, Timer
from network import WLAN, AP_IF
from phew import access_point, dns
from http_handler import HttpHandler

CACHE_FILENAME = const('cache.json')

class ApHandler:
  def __init__(self):
    gc.enable()
    gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
    gc.collect()

    self._init_ap()

  def _get_pwd(self):
    if CACHE_FILENAME not in os.listdir():
      return 'changeme'

    with open(CACHE_FILENAME, 'r') as cache:
      data = json.load(cache)
      cache.close()

      return data['password']

  def _wdt_init(self):
    wdt = WDT(timeout=5000)
    wdt.feed()

    wdt_timer = Timer(-1)
    wdt_timer.init(
      period=2000,
      callback=lambda t:self._check_connection(wdt)
    )

  def _check_connection(self, wdt):
    if self._ap.active():
      wdt.feed()

  def _init_ap(self):
    uid = machine.unique_id()
    ssid = 'GaragePi-' + binascii.hexlify(uid).decode()[-4:].upper()
    pwd = self._get_pwd()

    self._ap = access_point(ssid, pwd)
    status = self._ap.ifconfig()

    print('Access point active')
    print(status)

    self._wdt_init()
    dns.run_catchall(status[0])

    handler = HttpHandler()
    handler.listen()
