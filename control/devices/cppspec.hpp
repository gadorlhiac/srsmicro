#ifndef SPEC_HPP_INCLUDED
#define SPEC_HPP_INCLUDED

#include <stdlib.h>
#include <cstdio>
#include <conio.h>

namespace optosky
{
    class CppSpec
    {
        public:
            // Methods
            CppSpec();
            int cpp_acquire();
            int cpp_close();

            int cpp_set_exposeTime();
            int cpp_set_averages();

        private:
            // Attributes
            HP2000_wrapper::HP2000Wrapper^ m_spec;
            HP2000_wrapper::Spectrum _data;
            bool _is_open;
            double _wavelength[2048];
            double _spectrum[2048];
            int _exposureTime; // In ms
            int _avgs;
    };
}

#endif
