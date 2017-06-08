/*
A KBase module: MetabolomicsTools

*/

module MetabolomicsTools {
    /* A mass spectral library in MSP format */
    typedef string mspSpectraLibrary;

    /* A reference to a kbase metabolic model */
    typedef string model_ref;

    /* A peak as tuple of mass/charge ratio and intensity  */
	typedef tuple<float mz, float intensity> peak;

    typedef structure {
        string workspace_name;
        model_ref metabolic_model;
        string spectra_source;
        string spectra_query;
    } GetSpectraParams;

    typedef structure {
        string report_name;
        string report_ref;
    } SpectraResults;

    funcdef get_spectra(GetSpectraParams params)
        returns (SpectraResults output) authentication required;
};
