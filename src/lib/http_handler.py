import uos as os
import ujson as json

from micropython import const
from network import WLAN
from machine import Pin, Timer
from phew import server, template

button = Pin(6, Pin.OUT)
btn_timer = Timer(-1)

DOMAIN = const('garage.pi')
CACHE_FILENAME = const('cache.json')

async def render_root():
  pwd_set = CACHE_FILENAME in os.listdir()
  html_path = 'index' if pwd_set else 'setup'

  return await template.render_template(html_path + '.html')

def serve_root_file(filename):
  if not server.file_exists(filename):
    return 'Not Found', 404

  return server.serve_file(filename)

class HttpHandler:
  def listen(self):
    server.run()
    print('Listening for requests...')

  @server.route('/', methods=['GET'])
  def root(request):
    return await render_root()

  @server.route('/save-pwd', methods=['POST'])
  def save_pwd(request):
    body = request.data
    keys = body.keys()

    if 'password' not in keys:
      return 'Bad request', 400

    with open(CACHE_FILENAME, 'w+') as cache:
      cache.write(json.dumps(body))
      cache.close()

    return 'Created', 201

  @server.route('/pressed', methods=['GET'])
  def pressed(request):
    button.value(1)
    btn_timer.init(
      period=1000,
      mode=Timer.ONE_SHOT,
      callback=lambda t:button.value(0)
    )

    return 'OK', 200

  @server.route('/log', methods=['GET'])
  def log(request):
    return serve_root_file('log.txt')

  @server.route('/log-backup', methods=['GET'])
  def log_backup(request):
    return serve_root_file('log-backup.txt')

  @server.route('/ncsi.txt', methods=['GET'])
  def hotspot_windows_ncsi(request):
    return '', 200

  @server.route('/connecttest.txt', methods=['GET'])
  def hotspot_windows_connecttest(request):
    return '', 200

  @server.route('/redirect', methods=['GET'])
  def hotspot_windows_redirect(request):
    return server.redirect(f'http://{DOMAIN}/', 302)

  @server.route('/generate_204', methods=['GET'])
  def hotspot_android_redirect(request):
    return server.redirect(f'http://{DOMAIN}/', 302)

  @server.route('/hotspot-detect.html', methods=['GET'])
  def hotspot_apple(request):
    return await render_root()

  @server.catchall()
  def catch_all(request):
    path = request.path
    host = request.headers['host']

    if host != DOMAIN:
      return server.redirect(f'http://{DOMAIN}/')
    elif path.startswith('/static/'):
      if not server.file_exists(path):
        return 'Not Found', 404

      return server.serve_file(path)
