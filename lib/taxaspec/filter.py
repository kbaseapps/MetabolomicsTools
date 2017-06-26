"""
Methods for filtering mass spectra based on taxonomy
"""
# TODO: Should just use directory search to find models to speed filter time
import pickle
import difflib
import re
import sys
import gzip


def get_model(model_id):
    """
    Return sets of Inchikeys and names associated with the model id
    :param model_id: the name of the metabolic model
    :type model_id: str
    :return:
    :rtype: tuple(set, set)
    """
    def get_set(file):
        with gzip.GzipFile(file, 'rb') as infile:
            set_dict = pickle.load(infile)
        try:
            return set_dict[model_id]
        except KeyError:
            options = difflib.get_close_matches(model_id, set_dict.keys())
            raise ValueError('%s does not match any valid models. Did you '
                             'mean any of these: %s'
                             % (model_id, ", ".join(options)))

    return get_set('model_inchikeys.pkl.gz'), get_set('model_names.pkl.gz')


def select_quant_ions(spec, n_ions=3, min_sep=2, graylist_penalty=500,
                      blacklist={'73', '147', '148', '149', '207'},
                      graylist=set(list(range(100)) + [221, 281, 295, 355, 429])):
    # Return a list of ions that are not on the blacklist sorted by intensity
    ion_list = []
    for x in re.findall("\(\s*(\d+)\s+(\d+)\)", spec):
        # skip all blacklisted ions
        if x[0] in blacklist:
            continue
        # subtract the graylist penalty from any ion in the graylist
        ion_list.append((int(x[1])-int(int(x[0]) in graylist)*graylist_penalty,
                         int(x[0])))
    ion_list.sort(reverse=True)
    quant_ions = set()
    while len(quant_ions) < n_ions and ion_list:
        ion = ion_list.pop(0)
        # If the candidate ion is at least min_sep from any existing quant ion,
        # add it to the quant ion list
        if not any([abs(x - ion[1]) <= min_sep for x in quant_ions]):
            quant_ions.add(ion[1])
    return quant_ions


def filter_file(infile, model=None, inchikeys=None, names=None):
    """
    Filters a mass spectra library to only compounds that exist in a
    specific organism's metabolic model
    :param infile: The path to the file to be filtered
    :type infile: str
    :param model: The id of a model to use for filtering (e.g. 'eco'). This
        will override inchikeys and names parameters
    :type model: str
    :param inchikeys: If a spectrum matches any of these inchikeys it will be 
        retained
    :type inchikeys: set
    :param names: If a spectrum matches any of these names it will be retained
    :type names: set
    :return: The number of input spectra in the file and number of spectra
    remaining after filtering
    :rtype: tuple(int, int)
    """
    def spec_gen(file):
        # This should probably be converted to a generator to be resilient
        # against really big spec libraries
        raw = open(file, 'r').read()
        sep_list = ["\n\n\n", "\n\n", "END IONS\n\nBEGIN IONS\n"]
        sep = max(sep_list, key=lambda x: raw.count(x, 0, 10000))
        for spec in raw.split(sep):
            yield spec+sep

    if not any((model, inchikeys, names)):
        raise ValueError("No filtering criteria supplied")

    if infile[-4:] not in {'.msp', '.mgf', '.msl'}:
        raise ValueError("%s is not a valid input file. Use MSP, MGF or MSL "
                         "formats" % infile)
    # Trigger file not found error quickly if applicable
    open(infile)

    if model:
        inchikeys, names = get_model(model)
    outname = "%s_filtered_by_%s.%s" % (infile[:-4], model, infile[-3:])
    outfile = open(outname, "w")
    in_spec, out_spec = 0, 0
    for spec in spec_gen(infile):
        in_spec += 1
        inchikey = re.search("[A-Z]{14}-[A-Z]{10}-[A-Z]", spec)
        if inchikey:
            inchikey = inchikey.group(0)
        n_patt = "(Synon: METB N: |Name: |Synonym:)(\S+)"
        spec_names = set([x[1] for x in re.findall(n_patt, spec) if x])
        ri = re.search('"retention index=(\w+)"', spec)
        if ri:
            spec = spec.replace("\nFormula:", "\nRI: %s\nFormula:" %
                                ri.group(1))

        # Currently only works with MSL format
        if '\nQUANTIFICATION:' in spec:
            ion_list = select_quant_ions(spec)
            # Expects qualification line to exist, may need to be refactored
            spec = spec.replace("\nQUANTIFICATION:\n", "\nQUANTIFICATION: %s\n"
                                % " ".join([str(x) for x in ion_list]))
        if spec_names & names or inchikey in inchikeys:
            out_spec += 1
            outfile.write(spec)
    outfile.close()
    return in_spec, out_spec, outname

if __name__ == "__main__":
    inspec, outspec, outfile = filter_file(sys.argv[1], sys.argv[2])
    print("Filtered %s spectra down to %s based on the %s model"
          % (inspec, outspec, sys.argv[2]))
