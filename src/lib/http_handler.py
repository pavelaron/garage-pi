import network
import errno
import uos as os
import ure as re
import usocket as socket
import ujson as json

from network import WLAN
from machine import Pin, Timer, WDT

types_map = {
  'css'  : 'text/css',
  'gif'  : 'image/gif',
  'html' : 'text/html',
  'jpg'  : 'image/jpeg',
  'js'   : 'application/javascript',
  'json' : 'application/json',
  'png'  : 'image/png',
  'txt'  : 'text/plain',
}

http = {
  'ok'            : 'HTTP/1.0 200 OK\r\n',
  'bad_request'   : 'HTTP/1.0 400 Bad request\r\n',
  'not_found'     : 'HTTP/1.0 404 Not Found\r\n',
}

button = Pin(6, Pin.OUT)

class HttpHandler:
  def __init__(self, ip, cache_filename):
    self._ip = ip
    self._connection = socket.socket()
    self._completed_setup = cache_filename in os.listdir()

    self._cache_filename = cache_filename
    self._btn_timer = Timer(-1)

  def _open_socket(self):
    address = (self._ip, 80)
    self._connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self._connection.bind(address)
    self._connection.listen(5)

  def listen(self):
    print('Listening for requests...')

    self._open_socket()
    self._wdt_init()

    while True:
      client = self._connection.accept()[0]

      self._router(client)
      client.close()

  def _wdt_init(self):
    wdt = WDT(timeout=5000)
    wdt.feed()

    wdt_timer = Timer(-1)
    wdt_timer.init(
      period=2000,
      callback=lambda t:self._check_connection(wdt)
    )

  def _check_connection(self, wdt):
    connection = str(self._connection).lower()
    if re.search(r'state=[1-3]', connection):
      wdt.feed()

  def _handle_button(self):
    button.value(1)
    self._btn_timer.init(
      period=1000,
      mode=Timer.ONE_SHOT,
      callback=lambda t:button.value(0)
    )

  def _router(self, client):
    request = client.recv(1024)
    lines = request.splitlines()

    if not lines:
      client.send(http['bad_request'])
      return

    route = lines[0]

    if re.search('/save-pwd', route):
      body = json.loads(lines[-1].decode('utf-8'))
      keys = body.keys()

      if 'password' not in keys:
        client.send(http['bad_request'])
        return

      with open(self._cache_filename, 'w') as cache:
        cache.write(json.dumps(body))
        cache.close()

      client.send(http['ok'])
    elif re.search('/pressed', route):
      self._handle_button()
      client.send(http['ok'])
    elif re.search(r'/static/\S+', route):
      client.send(http['ok'])
      path = re.search(r'static/\w+\.?\S*', route)
      filename = path.group(0).decode('utf-8')

      ext = filename.split('.')[-1]
      content_type = types_map[ext] if ext in types_map \
                      else 'application/octet-stream'

      client.send('Content-Type: ' + content_type + '\r\n')
      client.send('Content-Length: ' + str(os.stat(filename)[6]) + '\r\n\r\n')

      self._send_file(filename, client)
    elif re.search(r'/log', route):
      self._send_file('log.txt', client)
    elif re.search(r'/log-backup', route):
      self._send_file('log-backup.txt', client)
    else:
      client.send(http['ok'])
      client.send('Content-Type: text/html; charset=UTF-8\r\n\r\n')
      self._root(client)

  def _root(self, client):
    html_path = 'index' if self._completed_setup else 'setup'
    self._send_file(html_path + '.html', client)

  def _send_file(self, filename, client):
    try:
      with open(filename, 'rb') as f:
          while True:
            data = f.read(1024)
            if not data:
              break
            client.sendall(data)

          f.close()
          client.send('\r\n')
    except OSError as exc:
      if exc.errno != errno.ENOENT:
        raise

      client.send(http['not_found'])
