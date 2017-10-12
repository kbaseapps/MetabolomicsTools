/*
A KBase module: MetabolomicsTools

*/

module MetabolomicsTools {
    typedef int bool;

    /* A reference to a FBAModel, CompoundSet or FBA object */
    typedef string obj_ref;

    typedef structure {
        string workspace_name;
        obj_ref compound_object;
        string spectra_source;
        string spectra_query;
        bool use_inchi;
        bool use_name;
    } GetMonaSpectraParams;

    typedef structure {
        string report_name;
        string report_ref;
    } SpectraResults;

    funcdef get_mona_spectra(GetMonaSpectraParams params)
        returns (SpectraResults output) authentication required;

    typedef structure {
        string workspace_name;
        obj_ref compound_object;
        bool charge;
        list<string> energy_levels;
        bool use_inchi;
        bool use_name;
        bool use_source;
    } GetMineSpectraParams;

    funcdef get_mine_spectra(GetMineSpectraParams params)
        returns (SpectraResults output) authentication required;
};
