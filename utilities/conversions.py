"""
@brief Useful functions for unit and type conversions, e.g. OPO wavelength to
SRS wavenumber, switching between file formats, and loading configuration files.
"""
import h5py
import yaml

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

def load_zi_yaml(self, path):
    """! Load in the parameter hierarchy from the included configuration
    file. One copy is loaded into a list-of-lists format which can be passed
    directly to ZI API objects for setting parameters. A separate copy is
    converted to a dictionary which matches the format used by other devices
    for accessing parameters. The config file is used by the actual device
    control object as well as GUI elements.
    @return cond_vars_list (list[list]) All possible ZI parameters in list of
    list format. Each list is of the form [str, int/float/long] where the first
    entry is a parameter path, and the second its setting.
    @return cond_vars (dict[str]) The above list converted to a dictionary for
    easier parameter accession and to match the format used by other devices.
    """
    with open(path, 'r') as f:
        cond_vars_list = yaml.unsafe_load(f)
    cond_vars = {}
    for i in range(len(cond_vars_list)):
        tmp = cond_vars_list[i]
        cond_vars[tmp[0]] = tmp[1]

    return cond_vars_list, cond_vars
