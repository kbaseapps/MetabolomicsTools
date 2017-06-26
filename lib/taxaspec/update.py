"""
Methods for updating taxonomic models
"""
import pymongo
import pickle
import gzip
import sys
from collections import defaultdict


def from_mine(db_name):
    """Import metabolic models from a MINE database and overwrite taxonomy

    :param db_name: Name of MINE database
    :type db_name: str
    :return:
    :rtype:
    """
    print("Updating taxonomy with models from %s database" % db_name)
    client = pymongo.MongoClient()
    db = client[db_name]
    compounds = {}

    def get_comp_data(value, key='DB_links.KEGG'):
        if value not in compounds:
            res = db.compounds.find_one({key: value},
                                        {"Names": 1, "Inchikey": 1, "_id": 0})
            if res:
                compounds[value] = res
            else:
                return None
        return compounds[value]["Names"], compounds[value]["Inchikey"]

    names = defaultdict(set)
    inchikeys = defaultdict(set)
    for model in db.models.find({}, {'Compounds': 1}):
        m_id = model['_id']
        for _id in model['Compounds']:
            data = get_comp_data(_id)
            if data:
                names[m_id].update(data[0])
                inchikeys[m_id].add(data[1])
    with gzip.GzipFile('model_names.pkl.gz', 'wb') as outfile:
        pickle.dump(dict(names), outfile)
    with gzip.GzipFile('model_inchikeys.pkl.gz', 'wb') as outfile:
        pickle.dump(dict(inchikeys), outfile)


if __name__ == "__main__":
    from_mine(sys.argv[1])
    print("Taxonomy updated")