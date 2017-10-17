# -*- coding: utf-8 -*-
import unittest
import os  # noqa: F401
import json  # noqa: F401
import time
import requests

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint  # noqa: F401

from biokbase.workspace.client import Workspace as workspaceService
from MetabolomicsTools.MetabolomicsToolsImpl import MetabolomicsTools
from MetabolomicsTools.MetabolomicsToolsServer import MethodContext
from MetabolomicsTools.authclient import KBaseAuth as _KBaseAuth

class MetabolomicsToolsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('MetabolomicsTools'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'MetabolomicsTools',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = workspaceService(cls.wsURL)
        cls.serviceImpl = MetabolomicsTools(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_MetabolomicsTools_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})  # noqa
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx

    def test_get_spectra(self):
        params = {
            'workspace_name': 'jjeffryes:narrative_1497984704461',
            'compound_object': '7601/197',
            'spectra_source': 'MoNA-export-GC-MS.msp',
            'spectra_query': '',
            'use_inchi': 1,
            'use_name': 1,
        }
        result = self.getImpl().get_mona_spectra(self.getContext(), params)
        print('RESULT:')
        pprint(result)
        assert result

    def test_mona_api(self):
        params = {
            'workspace_name': 'jjeffryes:narrative_1497984704461',
            'compound_object': '7601/197',
            'spectra_source': 'MoNA-API',
            'spectra_query': "metaData=q='name==\"collision energy\" and value==\"35%\"'",
            'use_inchi': 1,
            'use_name': 1,
        }
        result = self.getImpl().get_mona_spectra(self.getContext(), params)
        print('RESULT:')
        pprint(result)
        assert result
