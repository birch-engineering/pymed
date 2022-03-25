

import sys
import os
from glob import glob


if __name__ == "__main__":
    *rest, article_dirs_file, dest_file = sys.argv
    with open(article_dirs_file) as fs:
        dir_names = [line.rstrip() for line in fs]

    # we don't want duplicate sentences
    sentences = set() 
    for dirname in dir_names:
        processed_dir = f"{dirname}_processed"

        if os.path.isdir(processed_dir) and os.path.exists(processed_dir):
            print(f"process dir... {processed_dir}")
            filenames = glob(f"{processed_dir}/*")
            for filename in filenames:
                with open(filename) as fs:
                    sents_from_file = [line.rstrip() for line in fs]
                    sentences.update(sents_from_file)
    
    with open(dest_file, "w") as fo:
        fo.writelines(map(lambda x: x + "\n", list(sentences)))

    