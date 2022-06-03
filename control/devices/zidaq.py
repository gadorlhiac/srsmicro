#! /usr/bin/env python

import numpy as np
import time
import zhinst.ziPython as ziPython
import yaml
from AnyQt.QtCore import pyqtSignal, QObject

class APIError(Exception):
    def __init__(self, error):
        self.msg = error

    def __str__(self):
        return self.msg

class ziDAQ(QObject):
    """
    Facilitates control of the ZI HFL2I lockin amplifier.  Uses the server API.
    """
    daqData = pyqtSignal(np.ndarray)
    def __init__(self):
        QObject.__init__(self)
        self._name = ''
        self._scope = []
        self._settings = {}

        self._daq = None

        self._sigin = 0
        self._sigout = 0
        self._scope_time = 1

        self._tc = 0
        self._freq = 0
        self._rate = 0

        try:
            port, apilevel = self._discover()
            self.server = ziPython.ziDAQServer('localhost', port, apilevel)
            self.server.connect()

            msg = self._load_settings()
            self.server.set(self._settings['server'])
            self.server.sync()

            self._get_config()

            self._daq = self.server.dataAcquisitionModule()

            self.last_action = 'Lockin found, %s' % (msg)
        except Exception as e:
            self.last_action = str(e)

    ############################################################################
    # Lockin device discovery functions and settings initiliazation.

    def _discover(self) -> list[int, int]:
        """Run API discovery routines, and return port and apilevel to allow connection"""
        try:
            disc = ziPython.ziDiscovery()
            device = disc.findAll()[0]
            dev_info = disc.get(device)
            port = dev_info['serverport']
            apilevel = dev_info['apilevel']
            self._name = dev_info['deviceid'].lower()
            self.last_action = 'Lock-in found'
            return port, apilevel

        except Exception as e:
            self.last_action = 'Lock-in not found. %s' % (str(e))
            return 8005, 1

    def _load_settings(self) -> str:
        """
        Try to load settings for oscillator/demodulator/server.
        Default settings hard coded if not found.
        """
        try:
            with open('calibration/lockin.yaml') as f:
                tmp = ''
                for line in f:
                    tmp += line
                settings = yaml.load(tmp)
            msg = 'settings loaded'
        except FileNotFoundError as e:
            msg = 'using default settings'
            self._settings['server'] = [['/%s/demods/*/enable' % (self._name), 0],
                                        ['/%s/demods/*/trigger' % (self._name), 0],
                                        ['/%s/sigouts/*/enables/*' % (self._name), 0],
                                        ['/%s/scopes/*/enable' % (self._name), 0],

                                        ['/%s/sigins/%d/ac' % (self._name, self._sigin), 1],
                                        ['/%s/sigins/%d/imp50' % (self._name, self._sigin), 1],
                                        ['/%s/sigins/%d/diff' % (self._name, self._sigin), 0],

                                        ['/%s/demods/0/enable' % (self._name), 1],
                                        ['/%s/demods/0/adcselect' % (self._name), self._sigin],
                                        ['/%s/demods/0/order' % (self._name), 4],
                                        ['/%s/demods/0/timeconstant' % (self._name), 2e-5],
                                        ['/%s/demods/0/rate' % (self._name), 2e5],
                                        ['/%s/demods/0/oscselect' % (self._name), 0],
                                        ['/%s/demods/0/harmonic' % (self._name), 1],
                                        ['/%s/oscs/0/freq' % (self._name), 10280000]]
        finally:
            return msg

    def _get_config(self):
        """
        Get the current lockin oscillator frequency, demodulator time constant
        and sampling rate of the demodulated signal.
        """
        try:
            self._tc = self.server.getDouble('/%s/demods/0/timeconstant' % (self._name))
            self._rate = self.server.getDouble('/%s/demods/0/rate' % (self._name))
            self._freq = self.server.getDouble('/%s/oscs/0/freq' % (self._name))
        except Exception as e:
            self.last_action = str(e)

    ############################################################################
    # Data acquisition module for imaging

    def start_daq(self, imsize, dwell, num_frames=0):
        # imsize (rows, cols)
        path = '/%s/demods/0/sample' % (self._name)
        try:
            self._daq.set(self._settings['daq'])
        except KeyError:
            self._settings['daq'] = [['dataAcquisitionModule/device', self._name],
                                     ['dataAcquisitionModule/type', 1], # edge trigger
                                     ['dataAcquisitionModule/triggernode', '%s.auxin1' % (path)],
                                     ['dataAcquisitionModule/edge', 1], # positive edge
                                     ['dataAcquisitionModule/level', 2.5],
                                     ['dataAcquisitionModule/duration', dwell*imsize[1]],
                                     ['dataAcquisitionModule/delay', 0],

                                     ['dataAcquisitionModule/grid/mode', 2], # linear interpolation
                                     ['dataAcquisitionModule/grid/repetitions', 1],
                                     ['dataAcquisitionModule/grid/rows', imsize[0]],
                                     ['dataAcquisitionModule/grid/cols', imsize[1]],
                                     ['dataAcquisitionModule/grid/direction', 0],

                                     ['dataAcquisitionModule/refreshrate', 200],

                                     ['dataAcquisitionModule/delay', 0],
                                     ['dataAcquisitionModule/holdoff/time', 0],
                                     ['dataAcquisitionModule/holdoff/count', 0]]
            if num_frames:
                self._settings['daq'].append(['dataAcquisitionModule/count', num_frames])
            else:
                self._settings['daq'].append(['dataAcquisitionModule/endless', True])
            self._daq.set(self._settings['daq'])
        finally:
            self._daq.subscribe('%s.r' % (path))
            self._daq.execute()

    def read_daq():
        read = '/%s/demods/0/sample' % (self._name)
        while not self._daq.finished():
            try:
                read = self._daq.read(True)
                data = np.zeros([512, 512])
                # Can return multiple frames, but right now only care about most
                # recent
                num_frames = len(read['%s.r' % (path)])
                for i in range(num_frames):
                    flags = read['%s.r' % (path)][i]['header']['flags']
                    if flags & 1:
                        data = np.array(read['%s.r' % (path)][i]['value'])
                        self.daqData.emit(data)
            except KeyError:
                pass

    @property
    def acquiring(self):
        return not self._daq.finished()

    ############################################################################
    # Polling functions for data retrieval.

    def _poll(self, poll_length=0.05, timeout=500, tc=1e-3):
        """
        Poll the demodulator and record the data.

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
        path = '/%s/demods/0' % (self._name)

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

    ############################################################################
    # API errors

    def _check_api_errors(self):
        """Check if any API errors were found"""
        try:
            e = self.server.getLastError()
            if e != '':
                raise APIError(self._api_error)

        except APIError as e:
            self._api_error = str(msg)
            self.last_action = str(msg)

    @property
    def name(self):
        return self._name

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
        self.server.setDouble('/%s/demods/0/timeconstant' % (self._name), val)
        self.server.sync()

        self._tc = self.server.getDouble('/%s/demods/0/timeconstant' % (self._name))
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
        self.server.setDouble('/%s/demods/0/rate' % (self._name), val)
        self.server.sync()

        self._rate = self.server.getDouble('/%s/demods/0/rate' % (self._name))
        self.last_action = 'Lockin sampling rate set to %i' % (self._rate)


    ############################################################################
    # Property and setter functions for signal input/outputs

    @property
    def sigin(self):
        """Return current signal input channel.  Not in use."""
        return self._sigin

    @sigin.setter
    def sigin(self, val):
        """Set current signal input channel. Not in use."""
        self._sigin = val
        self.last_action = 'Signal input changed to channel %d.' % (val+1)

    @property
    def sigout(self):
        """Return current signal output channel.  Not in use."""
        return self._sigout

    @sigout.setter
    def sigout(self, val):
        """Set current signal output channel. Not in use."""
        self._sigout = val
        self.last_action = 'Signal output changed to channel %d.' % (val+1)

    ############################################################################
    # Oscilloscope properties

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
