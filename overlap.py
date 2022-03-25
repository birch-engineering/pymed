import sys
from pathlib import Path
import re
from collections import defaultdict

if __name__ == "__main__":
    # corpus file from pubmed scraping corpus, word_cnt_file from transcripts
    *rest, corpus_file, word_cnt_file = sys.argv
    
    word_cnt = defaultdict(int)
    with (Path.cwd()/corpus_file).open() as f:
        for line in f:
            for w in line.split():
                word_cnt[w] += 1
    with (Path.cwd() / word_cnt_file).open() as f:
        line = f.readlines()[0]
    
    start = 0
    cnt_start = re.compile(r"\d+")
    m = cnt_start.search(line, start)
    i = 0
    missed_terms = dict()
    matched_terms = dict()
    
    while m:
        term = line[start:m.start()].strip()
        cnt = int(line[m.start():m.end()])
        start = m.end()
        m = cnt_start.search(line, start)
    
        if term:
            if term in word_cnt:
                matched_terms[term] = cnt
            else:
                missed_terms[term] = cnt
    with open("missed_terms", "w") as f:
        for term in missed_terms:
            f.write(f"{term} {missed_terms[term]}\n")

    with open("matched_terms", "w") as f:
        for term in matched_terms:
            f.write(f"{term} {matched_terms[term]}\n")
    
    print(f"Total words {len(missed_terms) + len(matched_terms)}, missed words {len(missed_terms)}, matched words {len(matched_terms)}")

    
    