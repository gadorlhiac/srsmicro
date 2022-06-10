from .device import Device
from .zurichdaq import ZurichDaq
import zhinst.ziPython as ziPython
from PyQt5.QtCore import QObject, QThread
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import pyqtSlot as Slot

# For simplicity, use the same names as serial devices
# Need _cond_vars
# Need _logs and logs
# Need cmd_result
# Need name, this will be different than the name used by the server API

class ZurichLockin(Device):
    """The base class for the ZI HFL2I lock-in amplifier.

    Uses a separate server for communication through ZI's provided API. For
    simplicity, and reproducibility, ZI API calls are handled behind the scenes,
    so the end user experience mimics using the SerialDevice class.
    """
    data = Signal(object, object)

    def __init__(self, name='Lockin'):
        """! The ZurichLockin base class initializer."""
        super().__init__(name)

        ## @var _devname
        # Actual hardware device name for internal use with the server API
        self._devname: str = ''
        self._cond_vars['dwell'] = 1e-5

    # Lockin discovery and configuration functions
    ############################################################################
    def _open(self):
        """! Run the ZI API discovery routine and attempt to start the lock-in
        amplifier server.
        """
        # It is required to construct an instance of the discovery class
        discovery = ziPython.ziDiscovery()
        devs = discovery.findAll()
        if len(devs) == 0:
            raise(DeviceNotFound('No lockin detected. Is everything plugged in?'))
        else:
            dev = devs[0]
            info = discovery.get(dev)
            port = info['serverport']
            apilevel = info['apilevel']
            self._devname = info['deviceid'].lower()
            self._server = ziPython.ziDAQServer('localhost', port, apilevel)
            self._server.connect()

            # Use external clock
            self._server.set([['/{}/system/extclk'.format(self._devname), 1]])
            self._server.sync()
            self._enable_demod()
            self._configure_sigin()

            # Create ZurichDaq object and the separate thread it runs on
            # The ZurichDaq has a dataAcquisitionModule which also runs on an
            # independent thread. This allows the ZurichDaq to do continuous
            # polling of the dataAcquisitionModule while that in turn polls reads
            # continuously from the physical device itself
            self._daq_thread = QThread()
            self._daq.moveToThread(self._daq_thread)
            self._daq = ZurichDaq(self._server.dataAcquisitionModule(),
                        self._devname, '/{}/demods/0/sample'.format(self._devname))

            # Connect _image_data for relaying information to controller and
            # gui
            self._daq.data.connect(self._image_data)

            # Connect signal/slots for shutdown to thread signal/slots
            # Thread shutdown occurs in the ZurichLockin exit routine below
            self._daq.shutdown.connect(self._daq_thread.quit)
            self._daq.shutdown.connect(self._daq.exit)
            self._daq_thread.finished.connect(self._daq_thread.deleteLater)


    def _enable_demod(self, demod=0, sigin=0, freq=1.028e7, harm=1, tc=3e-6,
                                                    order=4, osc=0, rate=100000):
        """! Enable a demodulator for signal processing.
        @param demod (int) Index of demodulator, [0, 5]. Default: 0
        @param sigin (int) Index of signal input, [0, 5]. Default: 0 (Signal In 1)
        @param freq (float) Demodulation frequency (Hz). Default: 10280000
        @param harm (int) Demodulation harmonic. Default: 1
        @param tc (float) Lock-in time constant in seconds. Default: 3e-6
        @param order (int) Low-pass filter order [1,8]. Default 4 (24 dB/oct slope)
        @param osc (int) Oscillator to use 0 or 1. Default 0
        @param rate (int) Data transfer rate (Hz), may be approximated by LIA. Default: 10000 (>2 samples/pixel at 512 pixels with dwell=tc)
        """
        # Demodulator parameter settings
        parameters = [['/{}/demods/{}/enable'.format(self._devname, demod), 1],
                      ['/{}/demods/{}/adcselect'.format(self._devname, demod), sigin],
                      ['/{}/demods/{}/harmonic'.format(self._devname, demod), harm],
                      ['/{}/demods/{}/timeconstant'.format(self._devname, demod), tc],
                      ['/{}/demods/{}/order'.format(self._devname, demod), order],
                      ['/{}/demods/{}/oscselect'.format(self._devname, demod), 0],
                      ['/{}/demods/{}/rate'.format(self._devname, demod), rate]]

        # Push settings to lock-in
        self._server.set(parameters)
        self._server.sync()

        # Set oscillator parameters
        # Note: documentation may indicate that demods has a frequency parameter
        # but it doesn't. Set it in the oscillator
        parameters = [['/{}/oscs/{}/freq'.format(self._devname, osc), freq]]

        # Push settings to lock-in
        self._server.set(parameters)
        self._server.sync()

        # Update object copy of parameters and logs
        self._cond_vars['demod{}'.format(demod)] = { 'enable' : 1,
                                                     'sigin' : sigin,
                                                     'harmonic' : harm,
                                                     'tc' : tc,
                                                     'order' : order,
                                                     'oscillator' : 0,
                                                     'rate': rate }
        self._cond_vars['osc{}'.format(osc)] ={ 'freq' : freq }

        self._logs += '{} Demodulator {} using:\n'.format(self.current_time, demod)
        for param in self._cond_vars['demod{}'.format(demod)]:
            self._logs += '{}: {}\n'.format(param, self._cond_vars['demod{}'.format(demod)][param])

        self._logs += 'Oscillator {} using:\n'.format(osc)
        self._logs += '{}: {}\n'.format('freq', freq)

    def _configure_sigin(self, sigin=0, ac=1, i50=1, diff=0, range=.01):
        """! Configure signal in parameters.
        @param sigin (int) Index of signal input to configure. Default: 0
        @param ac (int) Whether to enable AC coupling. Default: 1 (Enable)
        @param i50 (int) Whether input impedance is set to 50 ohm. Default: 1 (Yes)
        @param diff (int) Whether using differential input. Default: 0 (No)
        @param range (float) Voltage range of signal in V (0.0001). Default: 0.01
        """
        # Signal input parameter settings
        sig_set = [['/{}/sigins/{}/ac'.format(self._devname, sigin), ac],
                   ['/{}/sigins/{}/imp50'.format(self._devname, sigin), i50],
                   ['/{}/sigins/{}/diff'.format(self._devname, sigin), diff],
                   ['/{}/sigins/{}/range'.format(self._devname, sigin), range]]

        # Push settings to lock-in
        self._server.set(sig_set)
        self._server.sync()

        # Update object copy of parameters and logs
        self._cond_vars['sigin{}'.format(sigin)] = { 'enable' : 1,
                                                     'ac' : ac,
                                                     'imp50' : i50,
                                                     'diff' : diff,
                                                     'range' : range}


        self._logs += '{} Configured input {} using:\n'.format(self.current_time, sigin)
        for param in self._cond_vars['sigin{}'.format(sigin)]:
            self._logs += '{}: {}'.format(param, self._cond_vars['sigin{}'.format(sigin)][param])


    def _configure_sigout(self, sigout=0, on=1, add=0, range=10):
        """! Configure signal out parameters. Defaults to beginning output, so
        should only be called to begin output, or then to disable it afterwards.
        @param sigout (int) Index of signal output to configure. Default: 0
        @param on (int) Toggle signal output on or off. Default: 1 (On)
        @param add (int) Toggle the signal adder on or off. Default: 0 (Off)
        @param range (float) Output range [0.01, 0.1, 1, 10]. Default: 10
        """
        sig_set = [['/{}/sigouts/{}/on'.format(self._devname, sigout), on],
                   ['/{}/sigouts/{}/add'.format(self._devname, sigout), add],
                   ['/{}/sigouts/{}/range'.format(self._devname, sigout), range]]
        self._server.set(sig_set)
        self._server.sync()

    def _get_config(self):
        """! Return current lock-in parameter configuration.
        @todo Define scope of return from tree hierarchy (i.e. which node to start at)
        @todo Parse dictionary to more readable form
        @todo Actually implement above. Add to logs? Or have a separate output?
        """
        pass

    # DAQ management (Imaging)
    ############################################################################
    def start_daq(self):
        self._daq_thread.started.connect(self._daq.start)
        self._daq_thread.start()

    def stop_daq(self):
        self._daq.stop = True

    # def create_daq(self, path: str) -> (QThread, ZurichDaq):
    #     path = '/{}/demods/0/sample.r'
    #     self._daqthread = QThread()
    #     self._daq = self._server.dataAcquisitionModule()
    #     self._daq.moveToThread(_daqthread)
    #     self._daqthread.start()
        # return _daqthread, _daq

    def _image_data(self, data):
        self.data.emit('Image', data)

    # def read_daq():
    #     pass

    @property
    def acquiring(self):
        return not self._daq.finished()

    # On application close
    ############################################################################
    def exit(self):
        self._daq_thread.quit()
        self.close()

    # Polling without DAQ module
    ############################################################################
    def _poll(self, demod, sigin, poll_length=0.05, timeout=500, tc=1e-3):
        """! Poll a demodulator and record the data.

        Args:
            poll_length (float): how long to poll. Units: (s)
            timeout (int): timeout period for response from server. Units (ms)
            tc (float): demodulator time constant with which to poll. Units (s)

        Returns:
            x (np array): demodulator x values over polling period.
            y (np array): demodulator y values over polling period.
            frame (np array): auxilary in 0 values.  Currently configured to olympus frame clock.
            line (np array): auxilary in 1 values. Currently configured to olympus line clock.
        """
        flat_dictionary_key = True
        path = '/%s/DEMODS/0' % (self._name)

        self.server.setDouble('%s/timeconstant' % (path), tc)
        self.server.sync()

        self.server.subscribe(path)
        self.server.sync()

        try:
            data = self.server.poll(poll_length, timeout, 1, flat_dictionary_key)
            if '%s/sample' % (path) in data:
                x = np.array(data['%s/sample' % (path)]['x'])
                y = np.array(data['%s/sample' % (path)]['y'])
                frame = np.array(data['%s/sample' % (path)]['auxin0'])
                line = np.array(data['%s/sample' % (path)]['auxin1'])

            self.last_action = 'Polled for %f s and time constant %f s' \
                                                            % (poll_length, tc)
        except Exception as e:
            self.last_action = 'While polling, encountered error: %s' % (str(e))

        self.server.setDouble('%s/timeconstant' % (path), self._tc)
        self.server.sync()

        return x, y, frame, line

    def _poll_scope(self, channel):
        """Poll the oscilloscope.  Not currently in use."""
        try:
            path = '/%s/scopes/0/wave' % (self._name)
            self.server.subscribe(path)
            self.server.sync()
            poll_length = .05  # [s]
            poll_timeout = 500  # [ms]
            poll_flags = 0
            poll_return_flat_dict = True
            data = self.server.poll(poll_length, poll_timeout, poll_flags, poll_return_flat_dict)
            self._scope = data['/%s/scopes/%i/wave' % (self._name, channel)][0]['wave']
        except Exception as e:
            self.last_action = str(e)

    # Oscilloscope module
    ############################################################################
    @property
    def scope(self):
        """Return the oscilloscope trace."""
        return self._scope

    @property
    def scope_time(self):
        return self._scope_time

    @scope_time.setter
    def scope_time(self, val):
        try:
            if val > 15:
                scope_time = 15
            else:
                scope_time = val
            clockbase = float(self.server.getInt('/%s/clockbase' % (self._name)))
            self.server.set(['/%s/scopes/0/time' % (device), scope_time])
            self.last_action = 'Oscilloscope time set to %i' % (val)
            #desired_t_shot = 10./frequency
            #scope_time = np.ceil(np.max([0, np.log2(clockbase*desired_t_shot/2048.)]))
        except:
            self.last_action = ''

    # Parameter setting/getting
    ############################################################################
    # Property and setter functions for lockin time constant, modulation
    # frequency and sampling rate

    # Lockin time constant
    @property
    def tc(self):
        """Property to return current demodulator time constant."""
        return self._tc

    @tc.setter
    def tc(self, val):
        """
        Time constant setter.

        Args:
            val (float): demodulator time constant. Units (s)
        """
        self.server.setDouble('/%s/DEMODS/0/timeconstant' % (self._name), val)
        self.server.sync()

        self._tc = self.server.getDouble('/%s/DEMODS/0/timeconstant' % (self._name))
        self.last_action = 'Lockin time constant set to %i' % (self._tc)

    # Lockin oscillator frequency
    @property
    def freq(self):
        """Property to return current oscillator frequency."""
        return self._freq

    @freq.setter
    def freq(self, val):
        """
        Oscillator frequency setter.

        Args:
            val (float): oscillator frequency. Units (Hz)
        """
        self.server.setDouble('/%s/oscs/0/freq' % (self._name), val)
        self.server.sync()

        self._freq = self.server.getDouble('/%s/oscs/0/freq' % (self._name))
        self.last_action = 'Oscillator frequency set to %i' % (self._freq)

    # Lockin sampling rate
    @property
    def rate(self):
        """Property to return current sampling rate of demodulated signal."""
        return self._rate

    @rate.setter
    def rate(self, val):
        """
        Sampling rate setter.

        Args:
            val (float): sampling rate of demodulated signal. Units (Sa/s)
        """
        self.server.setDouble('/%s/DEMODS/0/rate' % (self._name), val)
        self.server.sync()

        self._rate = self.server.getDouble('/%s/DEMODS/0/rate' % (self._name))
        self.last_action = 'Lockin sampling rate set to %i' % (self._rate)


    ############################################################################
    # Property and setter functions for signal input/outputs

    # @property
    # def sigin(self):
    #     """Return current signal input channel.  Not in use."""
    #     return self._sigin
    #
    # @sigin.setter
    # def sigin(self, val):
    #     """Set current signal input channel. Not in use."""
    #     self._sigin = val
    #     self.last_action = 'Signal input changed to channel %d.' % (val+1)
    #
    # @property
    # def sigout(self):
    #     """Return current signal output channel.  Not in use."""
    #     return self._sigout
    #
    # @sigout.setter
    # def sigout(self, val):
    #     """Set current signal output channel. Not in use."""
    #     self._sigout = val
    #     self.last_action = 'Signal output changed to channel %d.' % (val+1)

    ############################################################################
    # API errors

    # Flag and API error management
    ############################################################################
    # /dev1292/status/flags

    def _check_api_errors(self):
        """Check if any API errors were found"""
        try:
            e = self.server.getLastError()
            if e != '':
                raise APIError(self._api_error)

        except APIError as e:
            self._api_error = str(msg)
            self.last_action = str(msg)

# Exception error classes
############################################################################
class DeviceNotFound(Exception):
    """Exception class when unable to find Lockin devices connected."""
    def __init__(self, msg):
        """! DeviceNotFound class initializer.
        @param msg (str) Additional message to include.
        """
        self.msg = msg

    def __str__(self):
        """! String representation of the PositionError on print
        @return (str) self.msg
        """
        return self.msg

class APIError(Exception):
    """Exception class for errors due to ZI API"""
    def __init__(self, msg):
        """! APIError class initializer.
        @param msg (str) Additional message to include.
        """
        self.msg = msg

    def __str__(self):
        """! String representation of the PositionError on print
        @return (str) self.msg
        """
        return 'APIError: {}'.format(self.msg)
