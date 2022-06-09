"""
@brief Useful functions for unit and type conversions e.g. OPO wavelength to
SRS wavenumber or switching between file formats.
"""
import h5py

def calc_omega(w_p, w_s=1040):
    """! Calculate the wavenumber given a pump and Stokes wavelength in nm.
    @param w_p (float) Pump wavelength in nm.
    @param w_s (float) Stokes wavelength in nm. Default is 1040.
    """
    if w_p > w_s:
        omega = (10000000./w_s) - (10000000./w_p)
    else:
        omega = (10000000./w_p) - (10000000./w_s)
    return omega

def logstotext(h5, output):
    """! Produces a readable text file of recorded experimental logs.
    @param h5 (str) Path to the experimental hdf5 file.
    @param output Desired path for the output plain text log file.
    """
    h5file = h5py.File(h5)
    with open(output, 'w') as f:
        text = h5file['logs'][()].decode('utf-8')
        f.write(text)
