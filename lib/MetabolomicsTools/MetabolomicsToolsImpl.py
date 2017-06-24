# -*- coding: utf-8 -*-
#BEGIN_HEADER
# The header block is where all import statements should live
import os
import uuid
import json
from KBaseReport.KBaseReportClient import KBaseReport
from Workspace.WorkspaceClient import Workspace
from taxaspec.filter import filter_file
from taxaspec import acquire
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
    GIT_COMMIT_HASH = "9137e5b52f3559bc352d7c4943a8512f79b9e2af"

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
        self.workspaceURL = config['workspace-url']
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
        token = ctx['token']
        print("Token: %s" % token)
        ws_client = Workspace(self.workspaceURL, token=token)
        with open('/kb/module/data/Compound_Data.json') as infile:
            comp_data = json.load(infile)
        # acquire metabolic model from the workspace and get inchikeys & names
        try:
            kb_model = ws_client.get_objects(
                [{'name': params['metabolic_model'],
                  'workspace': params['workspace_name']}])[0]
        except Exception as e:
            raise ValueError(
                'Unable to get metabolic model object from workspace: (' +
                params['workspace_name'] + '/' +
                params['metabolic_model'] + ')' + str(e))
        kb_ids = [x['id'].replace('_c0', '')
                  for x in kb_model['data']['modelcompounds']]
        names, inchis = set(), set()
        for cid in kb_ids:
            if cid in comp_data:
                names.update(comp_data[cid].get('names', None))
                inchis.add(comp_data[cid].get('inchikey', None))

        # Acquire Spectral Library
        if params['spectra_source'] == 'MoNA-API':
            spec_file = acquire.from_mona(params['spectra_query'], workspace)
        else:
            spec_file = '/kb/module/data/%s' % params['spectra_source']
            if not os.path.exists(spec_file):
                raise ValueError('%s is not a supported spectra source'
                                 % params['spectra_source'])

        # Filter Spectral Library
        n_in_spectra, n_out_spectra, output_file = filter_file(spec_file, None,
                                                               inchis, names)
        print(n_in_spectra, n_out_spectra)

        # Package report
        report_files = [{'path': workspace + "/" + output_file,
                         'name': output_file,
                         'label': ".".join(output_file.split(".")[1:]),
                         'description': 'Spectral Library filtered with '
                                        'supplied metabolic model'}]
        report_params = {
            'objects_created': [],
            'text_message': 'Acquired %s matching spectra and filtered library'
                            ' to %s spectra which match the %s model' % (
                n_in_spectra, n_out_spectra, params['metabolic_model']),
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
