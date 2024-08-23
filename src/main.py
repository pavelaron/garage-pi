from machine import reset
from rp2 import bootsel_button

from ap_handler import ApHandler
from logger import Logger

if __name__ == '__main__':
  try:
    ApHandler()
  except KeyboardInterrupt:
    print('Process terminated by user...')
  except Exception as error:
    if bootsel_button() == 0:
      Logger(error)
      reset()
