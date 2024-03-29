"""!
@brief Definition of ExperimentResult class which manages all data generated,
useful metadata such as experimental parameters, and any log files generated.
"""

import h5py
import os

class ExperimentResult:
    """The class definition of the ExperimentResult object which handles I/O
    of all data, metadata, and experiment logs.
    """
    def __init__(self, path=None, name='experimentresults'):
        """! ExperimentResult class initializer.
        @param path (str) Destination path for output file. If none is provided
        (default) the current working directory will be used.
        @param name (str) Output file name. Default is experimentresults.
        """
        if path != None:
            self._path = path
        else:
            self._path = os.getcwd()

        ## @var file
        # An hdf5 File instance for storing logs and experiment results.

        try:
            self.file = h5py.File('{}/{}.h5'.format(self._path, name), 'a')
        except Exception as e:
            print('Improper path specified. Using current working directory.')
            self._path = os.getcwd()
            self.file = h5py.File('{}/{}.h5'.format(self._path, name), 'a')

        self.file['logs'][()] = ''

    def write_logs(self,  logs):
        """! Write logs to the appropriate dataset in the file."""
        self.file['logs'][()] = logs

    def exit(self):
        """! Shutdown procedure. Properly close the working file."""
        self.file.close()
