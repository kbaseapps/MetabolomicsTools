# -*- coding: utf-8 -*-
#BEGIN_HEADER
# The header block is where all import statements should live
import os
import uuid
import json
import shutil
from KBaseReport.KBaseReportClient import KBaseReport
from Workspace.WorkspaceClient import Workspace
from taxaspec.filter import filter_file
from taxaspec import acquire
import zipfile
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
    VERSION = "1.0.0"
    GIT_URL = "git@github.com:JamesJeffryes/MetabolomicsTools.git"
    GIT_COMMIT_HASH = "c76fc0898314fad8a852c976f5d6d0ca5082fcf0"

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


    def get_mona_spectra(self, ctx, params):
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
        #BEGIN get_mona_spectra
        # Parse/examine the parameters and catch any errors
        print('Validating parameters.')
        for val in ('workspace_name', 'metabolic_model', 'spectra_source',
                    'spectra_query'):
            if val not in params:
                raise ValueError('Parameter %s is not set in input arguments'
                                 % val)

        uuid_string = str(uuid.uuid4())
        scratch = self.shared_folder + "/" + uuid_string
        os.mkdir(scratch)
        token = ctx['token']
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
            spec_file = acquire.from_mona(params['spectra_query'],
                                          '/kb/module/data/')
        else:
            spec_file = '/kb/module/data/%s' % params['spectra_source']
            try:
                z = zipfile.ZipFile(spec_file + ".zip")
                z.extractall('/kb/module/data/')
            except ValueError:
                raise ValueError('%s is not a supported spectra source'
                                 % params['spectra_source'])

        # Filter Spectral Library
        n_in_spectra, n_out_spectra, output_file = filter_file(spec_file, None,
                                                               inchis, names)
        print(n_in_spectra, n_out_spectra)
        if not n_out_spectra:
            raise RuntimeError("No matching spectra found")

        new_path = "%s/%s%s.msp" % (scratch, os.path.basename(output_file)[:-8],
                                    params['metabolic_model'])
        shutil.move(output_file, new_path)

        # Package report
        report_files = [{'path': new_path,
                         'name': os.path.basename(new_path),
                         'label': os.path.basename(new_path),
                         'description': 'Spectral Library filtered with '
                                        'supplied metabolic model'}]
        report_params = {
            'objects_created': [],
            'message': 'Acquired %s matching spectra and filtered library to '
                       '%s spectra which match the %s model' % (
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
        #END get_mona_spectra

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method get_mona_spectra return value ' +
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
