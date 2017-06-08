# -*- coding: utf-8 -*-
#BEGIN_HEADER
# The header block is where all import statements should live
import os
import uuid
from KBaseReport.KBaseReportClient import KBaseReport
import taxaspec
#END_HEADER


class MetabolomicsTools:
    '''
    Module Name:
    MetabolomicsTools

    Module Description:
    A KBase module: MetabolomicsTools
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/JamesJeffryes/MetabolomicsTools.git"
    GIT_COMMIT_HASH = "467e29359db2901ab7173c741ff2a78ba7050486"

    #BEGIN_CLASS_HEADER
    # Class variables and functions can be defined in this block
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        
        # Any configuration parameters that are important should be parsed and
        # saved in the constructor.
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']

        #END_CONSTRUCTOR
        pass


    def get_spectra(self, ctx, params):
        """
        :param params: instance of type "GetSpectraParams" -> structure:
           parameter "workspace_name" of String, parameter "metabolic_model"
           of type "model_ref" (A reference to a kbase metabolic model),
           parameter "spectra_source" of String, parameter "spectra_query" of
           String
        :returns: instance of type "SpectraResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN get_spectra

        # Parse/examine the parameters and catch any errors
        print('Validating parameters.')
        for val in ('workspace_name', 'metabolic_model', 'spectra_source',
                    'spectra_query'):
            if val not in params:
                raise ValueError('Parameter %s is not set in input arguments'
                                 % val)

        uuid_string = str(uuid.uuid4())
        workspace = self.shared_folder + "/" + uuid_string
        os.mkdir(workspace)
        # TODO: Figure out how to acqure metabolic model from the workspace and get inchikeys & names from it
        metabolic_model = 'eco'  # allows testing the other functions

        # Acquire Spectral Library
        if params['spectra_source'] == 'MONA':
            spec_file = taxaspec.acquire.from_mona(params['spectra_query'],
                                                   workspace)
        else:
            raise ValueError('%s is not a supported spectra source' % val)

        # Filter Spectral Library
        n_in_spectra, n_out_spectra, output_file = taxaspec.filter.filter_file(
            spec_file, metabolic_model)

        # Package report
        report_files = [{'path': workspace + "/" + output_file,
                         'name': output_file,
                         'label': ".".join(output_file.split(".")[1:]),
                         'description': 'Spectral Library filtered with '
                                        'supplied metabolic model'}]
        report_params = {
            'objects_created': [],
            'text_message': 'Acquired %s matching spectra and filtered library'
                            ' to %s spectra which match the %s model'
                            % (n_in_spectra, n_out_spectra, metabolic_model),
            'file_links': report_files,
            'workspace_name': params['workspace_name'],
            'report_object_name': 'mass_spectra_report_' + uuid_string
        }

        # Construct the output to send back
        report_client = KBaseReport(self.callback_url)
        report_info = report_client.create_extended_report(report_params)
        output = {'report_name': report_info['name'],
                  'report_ref': report_info['ref'],
                  }
        #END get_spectra

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method get_spectra return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
