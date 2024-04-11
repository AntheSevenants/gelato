import argparse
import urllib.parse
import pycurl
import math
import re
import sys
from io import BytesIO
from tqdm.auto import tqdm
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description="Collect all lemmas")

parser.add_argument("url", type=str, help="Path to the advanced search URL")
parser.add_argument("-o", "--out", type=str,
                    help="Output path for lemmas file", default="lemmas_out.txt")
parser.add_argument("-p", "--pos", type=str,
                    help="Filter for a specific pos", default=None)

args = parser.parse_args()

url = args.url


def scrape_page(count, offset, pos=""):
    post_data = {
        "leid": "",
        "display": "",
        "offset": offset,
        "search_type": "advanced",
        "p_length": count,
        "comparison": "",
        "tense": "",
        "grammatical_number": "",
        "wf_writtenform": "",
        "mwe_writtenform": "",
        "mwe_expressiontype": "",
        "l_writtenform": "",
        "mode": "",
        "rf_writtenform": "",
        "variantType": "",
        "comparisonType": "",
        "declinable": "",
        "separability": "",
        "auxiliary": "",
        "pronominalAndGrammaticalGender": "",
        "adverbialUsage": "",
        "position": "",
        "reflexivity": "",
        "polarity": "",
        "valency": "",
        "transitivity": "",
        "part_of_speech": pos,
        "article": "",
        "complementation_complement": "",
        "complementation_preposition": "",
        "constituent": "",
        "function": "",
        "preposition": "",
        "complementizer": "",
        "chronology": "",
        "connotation": "",
        "domain": "",
        "geography": "",
        "register": "",
        "countability": "",
        "reference": "",
        "semantic_type": "",
        "semantic_shift_type": "",
        "semad_semanticType": "",
        "semad_semantic_shift": "",
        "semve_semanticType": "",
        "semve_semanticFeatureSet": "",
        "canonical_phrase": "",
        "canonical_form": "",
        "canonical_expressiontype": "",
        "textual_form": "",
        "textual_phrase": "",
        "gracol_complem": "",
        "lexcol_collocator": "",
        "sem_ex_definition": "",
        "synex_partOfSpeech": "",
        "synsex_lemma": "",
        "relationType": "",
    }

    # Encode the data in the format pycurl expects (e.g., "key1=value1&key2=value2")
    postfields = urllib.parse.urlencode(post_data)

    # Initialize BytesIO object to store response
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(curl.URL, url)
    curl.setopt(curl.POSTFIELDS, postfields)
    curl.setopt(curl.WRITEDATA, buffer)
    curl.perform()

    http_response_code = curl.getinfo(pycurl.HTTP_CODE)
    response_body = buffer.getvalue()

    curl.close()

    return response_body

poses = [ "adjective", "adverb", "noun", "verb", "other" ]
output_path = args.out

if args.pos is not None and args.pos in poses:
    poses = [ args.pos ]
    output_path = f"lemmas_{args.pos}.txt"

lemmas = []

for pos in tqdm(poses, leave=True, desc="Parts of speech"):
    soup = BeautifulSoup(scrape_page(1, 0, pos=pos), "html5lib")

    paginator = soup.find("span", class_="page-status").get_text()
    no_results = re.search(r"from (\d*)", paginator).group(1)
    no_entries = int(no_results)

    tranche_size = 10000
    tranches = math.ceil(no_entries / tranche_size)
    for i in tqdm(range(tranches), desc="Tranches scraped"):
        html = scrape_page(tranche_size, i * tranche_size, pos=pos).decode("UTF-8")
        soup = BeautifulSoup(html, "html5lib")

        lexical_entries_table = soup.find("tbody")
        if lexical_entries_table:
            tr_elements = lexical_entries_table.find_all("tr")
            for tr in tr_elements:
                # Find all <td> elements within each <tr>
                td_elements = tr.find_all("td")
                if len(td_elements) > 1:
                    # Extract text from the second <td> element (= lemma)
                    lemma = td_elements[1].get_text().strip()
                    lemmas.append(lemma)

# Dedupe
lemmas = sorted(list(set(lemmas)))

with open(output_path, "wt") as writer:
    writer.write("\n".join(lemmas))