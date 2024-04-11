import argparse
from glob import glob
from tqdm.auto import tqdm
import os

parser = argparse.ArgumentParser(description="Combine all XML files into a single lexical database")

parser.add_argument("-i", "--in_dir", type=str, help="Path where all input XML files are stored", default="output/")
parser.add_argument("-o", "--out", type=str, help="Output path for gelato lexical database", default="gelato.le.xml")

args = parser.parse_args()

if not os.path.exists(args.in_dir):
    raise FileNotFoundError("Input directory does not exist")

xml_files = glob(f"{args.in_dir}/*.xml")
if len(xml_files) == 0:
    raise ValueError("No input XML files found in input directory")

last_index = len(xml_files) - 1
footer_els = [ "</Lexicon>", "</LexicalResource>" ]

# Open the final output file
with open(args.out, "wt") as writer:
    # Go over each XML file
    for index, xml_file_path in enumerate(tqdm(xml_files, desc="XML files read")):
        # Open the XML file
        with open(xml_file_path, "rt") as reader:
            for line in reader:
                line_strip = line.strip()
                
                # Only keep if first file
                if line_strip.startswith("<?xml") or line_strip.startswith("<LexicalResource") or line_strip.startswith("<GlobalInformation"):
                    if index == 0:
                        writer.write(line)
                        continue
                    else:
                        continue
                
                # Copy footer structure
                if line_strip in footer_els:
                    if index == last_index:
                        writer.write(line)
                        continue
                else:
                    writer.write(line)
                    continue