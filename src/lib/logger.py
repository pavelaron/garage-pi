import utime as time
import uio as io
import uos as os
import sys

class Logger:
  def __init__(self, error):
    self._logfile = 'log.txt'
    self._logfile_backup = 'log-backup.txt'

    try:
      self._log(error)
    except Exception as exception:
      print(exception)

  def _log(self, error):
    self._cleanup()

    now = time.localtime()
    stamp = '[{}-{:02d}-{:02d}, {:02d}:{:02d}:{:02d}]'.format(*now)

    with open(self._logfile, 'a') as log:
      if error is not Exception:
        log.write('{}:\n{}\n\n'.format(stamp, str(error)))
      else:
        buf = io.StringIO()
        sys.print_exception(error, buf)

        log.write('{}:\n{}\n\n'.format(stamp, buf.getvalue()))

      log.close()

  def _cleanup(self):
    files = os.listdir()

    if self._logfile not in files:
      return

    size = os.stat(self._logfile)[6]
    if size < 5 * 1024:
      return

    if self._logfile_backup in files:
      os.remove(self._logfile_backup)

    os.rename(self._logfile, self._logfile_backup)
