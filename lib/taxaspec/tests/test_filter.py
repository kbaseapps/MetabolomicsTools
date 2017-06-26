from taxaspec import filter
from nose.tools import raises
import os
spec1 = """ (  73  900) (  76   30) (  77   30) (  78    8) 
(  87   13) (  88    8) (  89    8) (  90    4) (  91   51) 
(  92    8) (  93   21) (  94    8) (  95  900) (  99    4) 
( 101   30) ( 102   34) ( 104   17) ( 105   21) ( 108    4) 
( 109    4) ( 111    8) ( 115   55) ( 116   13) ( 117    4) 
( 118   17) ( 119   21) ( 121   17) ( 123    8) ( 127   13) 
( 131   59) ( 132   13) ( 133  190) ( 134   21) ( 135   46) 
( 136    8) ( 137    4) ( 139   13) ( 141   21) ( 142    8) 
( 143   68) ( 144   13) ( 145   13) ( 146    8) ( 150   30) 
( 151   97) ( 152    8) ( 153    8) ( 155    4) ( 156   17) 
( 157    4) ( 159    8) ( 161   34) ( 162    4) ( 165   13) 
( 166   21) ( 167  194) ( 168   30) ( 169    8) ( 170    4) 
( 173    4) ( 175   51) ( 176   13) ( 177   13) ( 181   21) 
( 182   25) ( 183   55) ( 184    8) ( 185    8) ( 187    4) 
( 190    8) ( 191   76) ( 192   42) ( 193   63) ( 194    8) 
( 195   13) ( 201    4) ( 203  101) ( 207  900) ( 209    8) 
( 210    4) ( 211    8) ( 213    4) ( 214    4) ( 215   25) 
( 216   13) ( 219 1000) ( 220  900) ( 221  186) ( 222   30) 
( 223   30) ( 224    8) ( 225   17) ( 226    4) ( 227    4) 
( 229    8) ( 230   42) ( 231   13) ( 232    4) ( 233    4) 
( 236  152) ( 237   42) ( 238    8) ( 239  186) ( 240   51) 
( 241   21) ( 242    8) ( 243   21) ( 244    8) ( 245   13) 
( 246    4) ( 247    4) ( 249   21) ( 250    4) ( 251    4) 
( 254    8) ( 255  662) ( 256  169) ( 257  148) ( 258   34) 
( 259   13) ( 260    4) ( 261    4) ( 267   30) ( 268    8) 
( 269   13) ( 272    4) ( 273    4) ( 275    4) ( 276    4) 
( 282    8) ( 283   34) ( 284   17) ( 285   17) ( 287    4) 
( 293   76) ( 294   21) ( 295   13) ( 299   13) ( 300    4) 
( 308    4) ( 309  118) ( 310   38) ( 311   13) ( 313   21) 
( 314    4) ( 315    4) ( 326    4) ( 329   13) ( 330    4) 
( 331   21) ( 333   30) ( 334   21) ( 335    4) ( 336    4) 
( 338    4) ( 339    4) ( 340   17) ( 341   13) ( 342    4) 
( 344   38) ( 345  781) ( 346  312) ( 347  139) ( 348   30) 
( 349    4) ( 357    8) ( 358    8) ( 370    4) ( 371    8) 
( 372   80) ( 373   30) ( 374   13) ( 375    4) ( 382    8) 
( 383    8) ( 389    4) ( 390    4) ( 393    4) ( 394    4) 
"""


def test_get_model():
    inchikeys, names = filter.get_model('eco')
    assert len(inchikeys) == 1084
    assert "NWQWQKUXRJYXFH-UHFFFAOYSA-N" in inchikeys
    assert len(names) == 3420
    assert "Glucose" in names


@raises(ValueError)
def test_missing_model():
    filter.get_model("bacillus")


def test_select_quant_ions():
    assert filter.select_quant_ions(spec1) == {219, 345, 255}


def test_filter_msp_file():
    try:
        spec_in, spec_out = filter.filter_file('tests/test.msp', 'eco')
        assert spec_in == 76
        assert spec_out == 1
        assert os.path.exists("tests/test_filtered_by_eco.msp")
    finally:
        os.remove("tests/test_filtered_by_eco.msp")


def test_msl_file():
    try:
        spec_in, spec_out = filter.filter_file('tests/test.msl', 'eco')
        assert spec_in == 3
        assert spec_out == 1
        assert os.path.exists("tests/test_filtered_by_eco.msl")
    finally:
        os.remove("tests/test_filtered_by_eco.msl")


@raises(ValueError)
def test_filter_bad_input_file():
    filter.filter_file('tests/test_filter.py', 'eco')


@raises(FileNotFoundError)
def test_filter_missing_input_file():
    filter.filter_file('fake.msp', 'eco')
