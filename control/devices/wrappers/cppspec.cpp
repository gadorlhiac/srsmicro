#include "cppspec.hpp"
#using "HP2000_wrapper.dll"

optosky::CppSpec::CppSpec()
{
    m_spec = gcnew HP2000_wrapper::HP2000Wrapper();
    _is_open = m_spec->openSpectraMeter();
    if (_is_open == true)
    {
        int init = m_spec->initialize();
        if (init == m_spec->ErrorFlag->THREAD_ERRORFLAG)
        {
            _is_open = false;
            return;
        } else if (init == m_spec->ErrorFlag->GAIT_ERRORFLAG) {
            char text[41] = "Failed to get the current exposure time.";
        } else if (init == m_spec->ErrorFlag->RSCFS_ERRORFLAG) {
            char text[42] = "Failed to get the correction coefficient.";
        } else {
            char text[28] = "Device opened successfully.";
        }
        
        _wavelength = m_spec->getWavelength();
        _exposureTime = 1000;
        _avgs = 5;
        bool flag = m_spec->setAverage(_avgs);
        
    } else {
        char text[27] = "Failed to open the device.";
    }
    return;
}

int optosky::CppSpec::cpp_acquire()
{
    bool flag = m_spec->getSpectrum(_exposureTime);
    while (true)
    {    
        if (flag == 1)
        {
            bool ready = m_spec->getSpectrumDataReadyFlag();
            if (ready == 1)
            {
                _data = m_spec->ReadSpectrum();
                if (_data.valid_flag == 1)
                {
                    _spectrum = _data->array;
                    _spectrum = m_spec->getdata1(_spectrum, 0, true, true, true);
                    m_spec->ClearSpectrumDataReadyFlag();
                    break;
                }
            }        
        }
    }
}
