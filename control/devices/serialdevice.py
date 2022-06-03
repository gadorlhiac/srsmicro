from serial import Serial
import time

class SerialDevice():
    def __init__(self):
        self._sercom = Serial(timeout=0)

        self._comport = ''
        self._isconnected = False
        self._baudrate = 115200
        self._cmd_result = ''
        self._comtime = 0.1

    def open_com(self):
        try:
            self._sercom.open()
        except:
            pass
    def close_com(self):
        if self._isconnected:
            self._sercom.close()

    def write(self, cmd, waittime):
        self._sercom.write(b'{}\n'.format(cmd))
        time.sleep(waittime)

    def read(self):
        return self._sercom.readline().decode('ascii')

    # Properties for setting values and retrieving result
    ############################################################################
    @property
    def cmd_result(self):
        return self._cmd_result

    @property
    def baudrate(self):
        return self._baudrate

    @baudrate.setter
    def baudrate(self, val):
        self._baudrate = val.split(':')[1][1:]
        self._cmd_result = '{0}'.format(val)

    @property
    def comport(self):
        return self._comport

    @comport.setter
    def comport(self, val):
        self._comport = val.split(':')[1][1:]
        self._cmd_result = '{0}'.format(val)

    @property
    def comtime(self):
        return self._comtime

    @comtime.setter
    def comtime(self):
        self._comtime = val.split(':')[1][1:]
        self._cmd_result = '{0}'.format(val)
