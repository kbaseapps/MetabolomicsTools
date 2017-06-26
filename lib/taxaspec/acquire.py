"""
Methods for acquiring mass spectra from public libraries
"""
import requests
from taxaspec import filter
import sys
import json as _json
import random
import datetime


def from_mona(query, save_path='./'):
    """
    Pull mass spectra stored in the MoNA(http://mona.fiehnlab.ucdavis.edu)
        database in MSP format
    :param query: A valid RSQL query string. It can be helpful to test the
        query on the mona website to ensure proper formatting
    :type query: str
    :param save_path: The desired location to save the downloaded file
    :type query: str
    :return: The path to the generated MSP file
    :rtype: str
    """
    endpoint = "http://mona.fiehnlab.ucdavis.edu/rest/spectra/search?query="
    r = requests.get(endpoint+query, headers={"Accept": "text/msp"})
    if not r.status_code == 200:
        raise RuntimeError("Mona query failed with status code %s"
                           % r.status_code)
    filename = "mona_%s.msp" % datetime.datetime.now()
    with open(save_path + filename, "w") as outfile:
        outfile.write(r.text)
    return save_path + filename


class ServerError(Exception):

    def __init__(self, name, code, message, data=None, error=None):
        self.name = name
        self.code = code
        self.message = '' if message is None else message
        self.data = data or error or ''
        # data = JSON RPC 2.0, error = 1.1

    def __str__(self):
        return self.name + ': ' + str(self.code) + '. ' + self.message + \
            '\n' + self.data


def from_mine(db, mongo_query, parent_filter, putative, spec_type):
    url = 'http://bio-data-1.mcs.anl.gov/services/mine-database'
    arg_hash = {'method': 'mineDatabaseServices.spectra_download',
                'params': [db, mongo_query, parent_filter, putative, spec_type],
                'version': '1.1',
                'id': str(random.random())[2:]
                }
    _CT = 'content-type'
    _AJ = 'application/json'
    ret = requests.post(url, data=_json.dumps(arg_hash))
    if ret.status_code == requests.codes.server_error:
        if _CT in ret.headers and ret.headers[_CT] == _AJ:
            err = _json.loads(ret.text)
            if 'error' in err:
                raise ServerError(**err['error'])
            else:
                raise ServerError('Unknown', 0, ret.text)
        else:
            raise ServerError('Unknown', 0, ret.text)
    if ret.status_code != requests.codes.OK:
        ret.raise_for_status()
    resp = _json.loads(ret.text)
    if 'result' not in resp:
        raise ServerError('Unknown', 0,
                          'An unknown server error occurred')
    filename = "mine_%s.msp" % datetime.datetime.now()
    with open(filename, "w") as outfile:
        outfile.write(resp['result'][0])
    return filename


if __name__ == "__main__":
    if sys.argv[1] == 'mona':
        print("Querying MoNA")
        mona_file = from_mona(sys.argv[2])
        if len(sys.argv) == 4:
            filter.filter_file(mona_file, sys.argv[3])
    else:
        raise ValueError('Unsupported data source %s' % sys.argv[1])
