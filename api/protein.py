from Bio import Entrez
from collections import namedtuple

ProteinMatch = namedtuple("ProteinMatch", "location feature_location protein_id")


def contains_location(feature, location, length):
    interval = feature["GBFeature_intervals"][0]
    start = int(interval["GBInterval_from"])
    end = int(interval["GBInterval_to"])
    # when the location is a complement, start > end so use min and max to ensure I'm checking
    # whether the sequence is in the range correctly
    lower = min(start, end)
    upper = max(start, end)
    return location <= upper and location + length - 1 >= lower


def get_protein_id(quals):
    for qual in quals:
        if qual["GBQualifier_name"] == "protein_id":
            return qual["GBQualifier_value"]
    return None


def fetch_protein_data(protein):
    with Entrez.efetch(db="nuccore", id=protein, rettype="gb", retmode="xml") as handle:
        return Entrez.read(handle)


def search_protein(protein, query):
    record = fetch_protein_data(protein)
    seq = record[0]["GBSeq_sequence"]

    location = seq.find(query)
    if location == -1:
        return None
    # ncbi locations seem to start at index 1, so adjust our location value to follow suit
    location = location + 1

    features = record[0]["GBSeq_feature-table"]
    feature_location = None
    protein_id = None

    for feature in features:
        if feature["GBFeature_key"] != "CDS":
            continue

        if contains_location(feature, location, len(query)):
            feature_location = feature["GBFeature_location"]
            protein_id = get_protein_id(feature["GBFeature_quals"])
            break

    return ProteinMatch(location, feature_location, protein_id)