import sys

from machine import reset
from rp2 import bootsel_button
from phew import logging
from ap_handler import ApHandler

if __name__ == '__main__':
  try:
    ApHandler()
  except KeyboardInterrupt:
    print('Process terminated by user...')
  except Exception as error:
    sys.print_exception(error)
    print(error)
    logging.error(error)
    if bootsel_button() == 0:
      reset()
