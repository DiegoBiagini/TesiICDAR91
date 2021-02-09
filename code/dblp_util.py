"""
This file contains functions used to elaborate the content of the dblp DB
"""
import util
from collections import deque
import xmltodict
import json
import hashlib


def articles_before(all_records, starting_year):
    new_all_records = all_records.copy()
    for record_type in all_records["dblp"].keys():
        queue = deque()
        for entry in all_records["dblp"][record_type]:
            if "year" in entry:
                year = 2020
                if isinstance(entry['year'], list):
                    int_years = [int(year) for year in entry["year"]]
                    year = min(int_years)
                else:
                    year = int(entry['year'])
                if year <= starting_year:
                    queue.append(entry)

        new_all_records['dblp'][record_type][:] = list(queue)

    with open('dblp1991.json', 'w') as f:
        json.dump(new_all_records, f)


def xml_to_json(path):
    with open(path) as fd:
        doc = xmltodict.parse(fd.read())
    with open('dblp.json', 'w') as f:
        json.dump(doc, f, indent=4, sort_keys=True)


def dblp_to_hashedlist(dblp):
    hashed_dict = {}
    for record_type in dblp["dblp"].keys():
        for entry in dblp["dblp"][record_type]:
            if not isinstance(entry["title"], str):
                hashed_dict[entry["@key"]] = hashed_biwordgram_from_title(entry["title"]["#text"])
            else:
                hashed_dict[entry["@key"]] = hashed_biwordgram_from_title(entry["title"])

    return hashed_dict

def hashed_biwordgram_from_title(title):
    title = util.remove_punctuation(title).lower()
    words = title.split()
    hashed_words = [int(hashlib.sha256(word.encode('utf-8')).hexdigest(), 16) % 10**8 for word in words]
    bigram_words = []
    for i, word in enumerate(hashed_words):
        if i != len(words) - 1:
            bigram_words.append([hashed_words[i], hashed_words[i+1]])
    return bigram_words


def bigramword_score(t1, t2):
    if len(t1) == 0 or len(t2) == 0:
        return 0

    common_biwords = [bw for bw in t1 if bw in t2]

    return len(common_biwords)/(max(len(t1), len(t2)))


def count_dblp(dblp):
    # {Year:Number}
    results = {}

    for record_type in dblp["dblp"].keys():
        for entry in dblp["dblp"][record_type]:
            if "year" in entry:
                year = 2020
                if isinstance(entry['year'], list):
                    int_years = [int(year) for year in entry["year"]]
                    year = min(int_years)
                else:
                    year = int(entry['year'])
                if not year in results:
                    results[year] = 1
                else:
                    results[year] += 1

    return results