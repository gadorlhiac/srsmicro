"""
@brief Useful functions for unit and type conversions e.g. OPO wavelength to
SRS wavenumber or switching between file formats.
"""
import h5py

def logstotext(h5, output):
    h5file = h5py.File(h5)
    with open(output, 'w') as f:
        text = h5file['logs'][()].decode('utf-8')
        f.write(text)
