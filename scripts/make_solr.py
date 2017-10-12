from ast import literal_eval
import json
import sys
"""
    Makes a JSON for indexing in SOLR
"""


def parse_msp(fp, id_translation=None):
    txt = open(fp).read()
    s_dict = {}
    for spec_txt in txt.split("\n\n"):
        spec = {'search_name': [], 'msp': spec_txt, 'Inchikey': ""}
        for line in spec_txt.split("\n"):
            sp_line = line.split(': ', 1)
            if sp_line[0] in {'Inchikey', 'Energy', 'Generation', '_id'}:
                spec[sp_line[0]] = sp_line[1].strip()
            elif sp_line[0] in {'Name', 'Synonym'}:
                spec['search_name'] = sp_line[1].strip().lower().translate(
                    str.maketrans("", "", '_ ()[]{}<>-+,'))
            elif sp_line[0] == "Sources" and id_translation:
                sources = literal_eval(sp_line[1])
                spec['Sources'] = list(set([id_translation.get(
                    x['Compound'], "") for x in sources]))
        s_dict[spec['Inchikey']] = spec
    return s_dict

if __name__ == "__main__":
    spec_dict = {}
    id_dict = {}
    for file_path in sys.argv[2:]:
        first_pass = parse_msp(file_path)
        for record in first_pass.values():
            id_dict[record['_id']] = record['Inchikey']
        spec_dict.update(parse_msp(file_path, id_dict))
    json.dump(list(spec_dict.values()), open(sys.argv[1], 'w'), indent=2)
