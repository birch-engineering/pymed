import sys
from pathlib import Path
import re

if __name__ == "__main__":

    _, arpa_file, lexicon_file = sys.argv
    one_gram_flag = False
    with Path(lexicon_file).open("w") as flexicon:
        with Path(arpa_file).open() as farpa:
            for line in farpa:
                if line.startswith("\\1-grams:"):
                    one_gram_flag = True
                    continue
                if line.startswith("\\2-grams:"):
                    break

                if one_gram_flag:
                    if not re.match(r"[-]*[0-9\.]+\t\S+\t*[-]*[0-9\.]*$", line):
                        continue

                    word = line.split("\t")[1]
                    word = word.strip()

                    if word == "<unk>" or word == "<s>" or word == "</s>":
                        continue

                    if not re.match("^[A-Z']+$", word):
                        print("ERROR: invalid word - {w}".format(w=word))
                        continue
                    flexicon.write("{w}\t{s} |\n".format(w=word, s=" ".join(word)))
