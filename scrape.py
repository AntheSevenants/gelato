import argparse
import pycurl
import os
import urllib.parse
from io import BytesIO
from tqdm.auto import tqdm

parser = argparse.ArgumentParser(description="Get semantic information about words")

parser.add_argument("url", type=str, help="Path to the advanced search URL")
parser.add_argument("lemmas_path", type=str, help="Path to text file with lemmas, one lemma each line")
parser.add_argument("-o", "--out_dir", type=str, help="Path to the output directory", default="output/")

args = parser.parse_args()

if not os.path.exists(args.lemmas_path):
    raise FileNotFoundError("Lemmas file does not exist")

if not os.path.exists(args.out_dir):
    os.makedirs(args.out_dir, exist_ok=True)

url = args.url

def scrape_word(lemma):
    post_data = {
        "word": lemma,
        "regex": None,
        "pos": "",
        "p_length": "",
        "offset": 0,
        "search_type": "simple"
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

with open(args.lemmas_path, "rt") as reader:
    lemmas = reader.read().split("\n")

for lemma in tqdm(lemmas, desc="Lemmas scraped"):
    lemma = lemma.strip() # you never know
    output_path = f"{args.out_dir}/{lemma}.xml"
    xml_sample = scrape_word(lemma).decode("UTF-8")

    with open(output_path, "wt") as writer:
        writer.write(xml_sample)