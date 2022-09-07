"""!
@brief Definition of the ZurichLockin class for interaction with the Zurich

Instruments HF2LI lock-in amplifier as well as custom exception classes APIError
and DeviceNotFoundError for zhinst API errors.

Classes:
ZurichLockin
DeviceNotFoundError
APIError
"""

from .device import Device
from .zurichdaq import ZurichDaq
# from srsmicro.utilities.conversions import load_zi_yaml
import zhinst.ziPython as ziPython
from PyQt5.QtCore import QObject, QThread
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import pyqtSlot as Slot
import yaml

# For simplicity, use the same names as serial devices
# Need _cond_vars
# Need _logs and logs
# Need cmd_result
# Need name, this will be different than the name used by the server API

# _cond_vars is a list of list as opposed to

class ZurichLockin(Device):
    """! The base class for interacting with the ZI HF2LI lock-in amplifier.

    Uses a separate server for communication through ZI's provided API. For
    simplicity, and reproducibility, ZI API calls are handled behind the scenes,
    so the end user experience mimics using the SerialDevice class.

    Properties:
    -----------

    Methods:
    --------
    """
    data = Signal(object, object)

    def __init__(self, name='Lockin'):
        """! The ZurichLockin base class initializer."""
        super().__init__(name)

        ## @var _devname
        # Actual hardware device name for internal use with the server API
        self._devname: str = ''
        # self._cond_vars_list, self._cond_vars = load_zi_yaml('srsmicro/control/devices/configuration/ziconfig.yaml')
        self._load_variables()
        # self._cond_vars['dwell'] = 1e-5
        self.state.emit(self.name, self._cond_vars)

    # Loading, lock-in discovery and configuration functions
    ############################################################################
    def _load_variables(self):
        """! Load in the parameter hierarchy from the included configuration
        file. One copy is loaded into a list-of-lists format which can be passed
        directly to ZI API objects for setting parameters. A separate copy is
        converted to a dictionary which matches the format used by other devices
        for accessing parameters. The config file is also used by ZI gui element.
        """
        ## @var _cond_vars_list
        # (list[list]) All possible ZI parameters in list of list format. Each
        # list is of the format [str, int/float/long] where the first entry is a
        # parameter path, and the second is a parameter setting.

        ## @var _cond_vars
        # (dict[str]:int/float/long) _cond_vars_list converted to dictionary
        # format for easier parameter accession and to match the format used by
        # other devices.
        with open('srsmicro/control/devices/configuration/ziconfig.yaml', 'r') as f:
            self._cond_vars_list = yaml.unsafe_load(f)
        self._cond_vars = {}
        for i in range(len(self._cond_vars_list)):
            tmp = self._cond_vars_list[i]
            self._cond_vars[tmp[0]] = tmp[1]
        # print(self._cond_vars)
    def _open(self):
        """! Run the ZI API discovery routine and attempt to start the lock-in
        amplifier server.
        """
        # It is required to construct an instance of the discovery class
        discovery = ziPython.ziDiscovery()
        devs = discovery.findAll()
        if len(devs) == 0:
            raise(DeviceNotFoundError('No lockin detected. Is everything plugged in?'))
        else:
            dev = devs[0]
            info = discovery.get(dev)
            port = info['serverport']
            apilevel = info['apilevel']
            self._devname = info['deviceid'].lower()
            self._server = ziPython.ziDAQServer('localhost', port, apilevel)
            self._server.connect()

            # print([[key, self._cond_vars[key]] for key in self._cond_vars])
            self._server.set([[key, self._cond_vars[key]] for key in self._cond_vars])
            # self._server.set(self._cond_vars_list)
            # # Use external clock
            # self._server.set([['/{}/system/extclk'.format(self._devname), 1]])
            # self._server.sync()
            self._enable_demod()
            # self._configure_sigin()

            # Create ZurichDaq object and the separate thread it runs on
            # The ZurichDaq has a dataAcquisitionModule which also runs on an
            # independent thread. This allows the ZurichDaq to do continuous
            # polling of the dataAcquisitionModule while that in turn reads
            # continuously from the physical device itself
            self._daq_thread = QThread()
            self._daq = ZurichDaq(self._server.dataAcquisitionModule(),
                        self._devname, f'/{self._devname}/demods/0/sample')
            self._daq.moveToThread(self._daq_thread)

            # Connect _image_data for relaying information to controller and
            # gui
            self._daq.data.connect(self._image_data)

            # Connect signal/slots for shutdown to thread signal/slots
            # Thread shutdown occurs in the ZurichLockin exit routine below
            self._daq.shutdown.connect(self._daq_thread.quit)
            self._daq.shutdown.connect(self._daq.exit)
            self._daq_thread.finished.connect(self._daq_thread.deleteLater)


    def _enable_demod(self, demod: int = 0, sigin: int = 0, freq: float = 1.028e7,
                            harm: int = 1, tc: float = 3e-6, order: int = 4,
                            osc: int = 0, rate: int = 100000):
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

        # Can try some clever comprehensions
        # dem = 'demods/{}'.format(demod)
        # values = {'range': range, 'rate': rate, 'adcselect': sigin, 'order': order,
        #           'harmonic':harm, 'timeconstant':tc}
        # parameters = [[key, self._cond_vars[key]] for key in self._cond_vars if dem in key]
        # for p in parameters:

        # Push settings to lock-in
        self._server.set(parameters)
        self._server.sync()

        # Set oscillator parameters
        # Note: documentation may indicate that demods has a frequency parameter
        # but it doesn't. Set it in the oscillator
        parameters = [[f'/{self._devname}/oscs/{osc}/freq', freq]]

        # Push settings to lock-in
        self._server.set(parameters)
        self._server.sync()

        # Update object copy of parameters and logs
        self._cond_vars[f'demod{demod}'] = { 'enable' : 1,
                                             'sigin' : sigin,
                                             'harmonic' : harm,
                                             'tc' : tc,
                                             'order' : order,
                                             'oscillator' : 0,
                                             'rate': rate }

        self._cond_vars[f'osc{osc}'] = { 'freq' : freq }

        log = f'Demodulator {demod} using:\n'
        for param in self._cond_vars[f'demod{demod}']:
            # self._logs += '{}: {}\n'.format(param, self._cond_vars['demod{}'.format(demod)][param])
            log += f'\t{param}: {self._cond_vars[f"demod{demod}"][param]}\n'

        log += f'Oscillator {osc} using:\n'
        log += f'\tfreq: {freq}\n'
        self.log(log)

    def _configure_sigin(self, sigin: int = 0, ac: int = 1, imp50: int = 1,
                                             diff: int = 0, range: float = .01):
        """! Configure signal in parameters.
        @param sigin (int) Index of signal input to configure. Default: 0
        @param ac (int) Whether to enable AC coupling. Default: 1 (Enable)
        @param imp50 (int) Whether input impedance is set to 50 ohm. Default: 1 (Yes)
        @param diff (int) Whether using differential input. Default: 0 (No)
        @param range (float) Voltage range of signal in V (0.0001). Default: 0.01
        """
        # Signal input parameter settings
        sig_set = [[f'/{self._devname}/sigins/{sigin}/ac', ac],
                   [f'/{self._devname}/sigins/{sigin}/imp50', imp50],
                   [f'/{self._devname}/sigins/{sigin}/diff', diff],
                   [f'/{self._devname}/sigins/{sigin}/range', range]]

        # Push settings to lock-in
        self._server.set(sig_set)
        self._server.sync()

        # Update object copy of parameters and logs
        self._cond_vars[f'sigin{sigin}'] = { 'enable' : 1,
                                             'ac' : ac,
                                             'imp50' : imp50,
                                             'diff' : diff,
                                             'range' : range}


        log = f'Configured input {sigin} using:\n'
        for param in self._cond_vars[f'sigin{sigin}']:
            # log += '{}: {}'.format(param, self._cond_vars['sigin{}'.format(sigin)][param])
            log += f'\t{param}: {self._cond_vars[f"sigin{sigin}"][param]}\n'
        self.log(log)


    def _configure_sigout(self, sigout: int = 0, on: int = 1, add: int = 0,
                                                              range: int = 10):
        """! Configure signal out parameters. Defaults to beginning output, so
        should only be called to begin output, or then to disable it afterwards.
        @param sigout (int) Index of signal output to configure. Default: 0
        @param on (int) Toggle signal output on or off. Default: 1 (On)
        @param add (int) Toggle the signal adder on or off. Default: 0 (Off)
        @param range (float) Output range [0.01, 0.1, 1, 10]. Default: 10
        """
        sig_set = [[f'/{self._devname}/sigouts/{sigout}/on', on],
                   [f'/{self._devname}/sigouts/{sigout}/add', add],
                   [f'/{self._devname}/sigouts/{sigout}/range', range]]
        self._server.set(sig_set)
        self._server.sync()

    def _get_config(self):
        """! Return current lock-in parameter configuration.
        @todo Define scope of return from tree hierarchy (i.e. which node to start at)
        @todo Parse dictionary to more readable form
        @todo Actually implement above. Add to logs? Or have a separate output?
        """
        pass

    def parse_cmd(self, param, val):
        if param == 'freq_osc0':
            parameters = [[f'/{self._devname}/oscs/0/freq', float(val)]]

        elif param == 'freq_osc1':
            parameters = [[f'/{self._devname}/oscs/1/freq', float(val)]]

        # Push settings to lock-in
        self._server.set(parameters)
        self._server.sync()

    # DAQ management (Imaging)
    ############################################################################
    def start_daq(self):
        self._daq_thread.started.connect(self._daq.start)
        self._daq_thread.start()

    def stop_daq(self):
        self._daq.stop = True

    def _image_data(self, data):
        self.data.emit('Image', data)

    # On application close
    ############################################################################
    def exit(self):
        print('........Closing DAQ thread.')
        try:
            self._daq_thread.quit()
            self._server.disconnect()
        except AttributeError as err:
            print('............DAQ never opened.')
        finally:
            print('')
        print('........Closing ZI server.')
        self.close()

    # Polling without DAQ module
    ############################################################################
    def _poll(self, demod: int, sigin, poll_length = 0.05, timeout=500, tc=1e-3):
        """! Poll a demodulator and record the data. Used to take spectra.
        @param demod (int)

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

        # Need to flush before subscribing

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
            self._api_error = str(e)
            self.last_action = str(e)

# Exception error classes
############################################################################
class DeviceNotFoundError(Exception):
    """! Exception class when unable to find Lockin devices connected."""
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
    """! Exception class for errors due to ZI API"""
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
