import json
import argparse
import os
import spacy
import multiprocessing
from joblib import cpu_count
import tqdm
from convert_num_to_word import convert_sent_to_word
import re
import string
from pathlib import Path
from functools import partial

def is_text(part_type: str):
    return any(
        [
            part_type.startswith("paragraph"),
            part_type.startswith("abstract"),
        ]
    )


def get_argparser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--articles-dir", action="store", type=str, required=True, help="the names of the dir that contains the origianl input files.")
    argparser.add_argument("--raw-input", action="store_true", help="if the input is in raw(plain text with numbers and punctuations). defaulted to bioC format(json)")
    argparser.add_argument("--output-part-size", action="store", type=int, default=100000, help="size of the output file in the number of lines")
    argparser.add_argument("--num-jobs", action="store", type=int, default=0, help="default to the min(number of cpu, the number of files to process)")
    return argparser


def process_batch(batch_id: int, files: list):
    nlp = spacy.load("en_core_web_sm")
    equation_syms = set(["=", "±", "+", "−"])
    for file_name in files:
        print(f"batch {batch_id}-{file_name}")
        try:
            with open(os.path.join(articles_dir, file_name)) as f:
                article = json.load(f)
        except ValueError:
            print(f"Error reading file {file_name}, skipping")

        sentences = []
        
        for doc in article["documents"]:
            for p in doc["passages"]:
                if is_text(p["infons"]["type"]):
                    text_doc = nlp(p["text"])
                    for sent in text_doc.sents:
                        filtered_sent = convert_sent_to_word(sent, nlp)
                        
                        if set(filtered_sent).intersection(equation_syms):
                            continue
                            
                        len(filtered_sent) > 3 and sentences.append(
                            " ".join(filtered_sent) + "\n"
                        )

        with open(f"{articles_dir}_processed/{batch_id}.txt", "a") as wf:
            wf.writelines(sentences)

def process_raw_batch(output_part_size: int, batch_id: int, files: list):
    nlp = spacy.load("en_core_web_sm")
    sentences = []
    part_id = 0

    for f in files:
        print(f"batch {batch_id}-{f}")
        
        with (Path(articles_dir) / f).open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                filtered_sent = convert_sent_to_word(line, nlp)

                len(filtered_sent) > 3 and sentences.append(
                    " ".join(filtered_sent) + "\n"
                )

                if len(sentences) == output_part_size :
                    with Path(f"{articles_dir}_processed/{batch_id}_part{part_id}.txt").open("w") as of:
                        of.writelines(sentences)
                    sentences = []
                    part_id +=1

    with Path(f"{articles_dir}_processed/{batch_id}_part{part_id}.txt").open("w") as of:
        of.writelines(sentences)



def create_batches(input_list: list, num_batches: int) -> list:
    per_batch, rest = divmod(len(input_list), num_batches)
    result = [
        input_list[i * per_batch : (i + 1) * per_batch] for i in range(num_batches)
    ]

    rest and result[-1].extend(input_list[-rest:])
    return result


if __name__ == "__main__":
    arg_parser = get_argparser()
    args = arg_parser.parse_args()
    articles_dir = args.articles_dir
    is_raw_input = args.raw_input
    output_part_size = args.output_part_size
    _, _, filenames = next(os.walk(articles_dir), (None, None, []))
    num_batches = min(cpu_count(), len(filenames))
    filename_in_batches = create_batches(filenames, num_batches)
    jobs = [(batch_id, filename_in_batches[batch_id]) for batch_id in range(num_batches)]
    Path(f"{articles_dir}_processed").mkdir(exist_ok=True)
    with multiprocessing.Pool(num_batches) as pool:
        if is_raw_input:
            results = list(tqdm.tqdm(pool.starmap(partial(process_raw_batch, output_part_size),jobs), total=num_batches))       
        else:        
            results = list(tqdm.tqdm(pool.starmap(process_batch, jobs), total=num_batches))
