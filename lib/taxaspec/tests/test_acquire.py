from taxaspec import acquire
import filecmp
import os
import glob
from subprocess import call

query = 'compound.metaData=q=\'name=="molecular formula" and ' \
            'value=="C47H74O12S"\''


def test_from_mona():
    try:
        file_name = acquire.from_mona(query)
        filecmp.cmp(file_name, "tests/mona_results.msp")
    finally:
        for file in glob.glob('*.msp'):
            os.remove(file)


def test_mona_commandline():
    try:
        rc = call(['python', 'acquire.py', 'mona', query, 'eco'])
        assert not rc
        assert len(glob.glob('*.msp')) == 2
        assert len(glob.glob('*_filtered_by_eco.msp')) == 1

    finally:
        for file in glob.glob('*.msp'):
            os.remove(file)


def test_from_mine():
    try:
        file_name = acquire.from_mine("EcoCycexp2", "", "eco", False,
                                      [[True, 20], [False, 40]])
        filecmp.cmp(file_name, "tests/mine_results.msp")
    finally:
        for file in glob.glob('*.msp'):
            os.remove(file)
