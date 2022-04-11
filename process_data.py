import json
import argparse
import os, sys
import spacy
import multiprocessing
from joblib import cpu_count
import tqdm
from convert_num_to_word import convert_sent_to_word
import re, mmap
import string
from pathlib import Path
from functools import partial
from concurrent.futures import ThreadPoolExecutor


def is_text(part_type: str):
    return any(
        [
            part_type.startswith("paragraph"),
            part_type.startswith("abstract"),
        ]
    )


def get_argparser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--articles-dir", action="store", type=str, help="the names of the dir that contains the origianl input files.")
    argparser.add_argument("--input-file", action="store", type=str, help="name of the input file, it only takes one big input")
    argparser.add_argument("--raw-input", action="store_true", help="if the input is in raw(plain text with numbers and punctuations). defaulted to bioC format(json)")
    argparser.add_argument("--output-part-size", action="store", type=int, default=100000, help="size of the output file in the number of lines, defaulted to 10K")
    argparser.add_argument("--num-jobs", action="store", type=int, default=0, help="default to the min(number of cpu, the number of files to process)")
    argparser.add_argument("--dump-only", action="store_const", const=True, default=False, help="if set, then it only dumps those articles, without processing text.")
    return argparser

def process_file(file_name: str):
    try:
        with open(os.path.join(articles_dir, file_name)) as f:
            article = json.load(f)
    except ValueError:
        print(f"Error reading file {file_name}, skipping")
        return False

    sentences = []
    for doc in tqdm.tqdm(article["documents"]):
        for p in doc["passages"]:
            if is_text(p["infons"]["type"]):
                text_doc = nlp(p["text"])
                for sent in text_doc.sents:

                    if dump_only:
                        sentences.append(sent.text + "\n")
                        continue
                    filtered_sent = convert_sent_to_word(sent.text)
                        
                    len(filtered_sent) > 3 and sentences.append(
                        " ".join(filtered_sent) + "\n"
                    )

    with open(f"{articles_dir}_processed/{file_name}.txt", "a") as wf:
        wf.writelines(sentences)
    return True

def process_raw_file(file_name):
    sentences = []
    part_id = 0
    file_size = Path(file_name).stat().st_size
    with tqdm(total=file_size) as pbar:
        with (Path(file_name)).open() as f:
            for line in f:
                line_length = len(line)
                line = line.strip()
                if not line:
                    continue
                filtered_sent = convert_sent_to_word(line)

                len(filtered_sent) > 3 and sentences.append(
                    " ".join(filtered_sent) + "\n"
                )

                if len(sentences) == output_part_size :
                    with Path(f"{articles_dir}_processed/{file_name}_part{part_id}.txt").open("w") as of:
                        of.writelines(sentences)
                    sentences = []
                    part_id +=1
                
                pbar.update(line_length)


def process_lines(batch_id: int, lines_idx):
    print(f"batch {batch_id} ...")
    sentences = []
    part_id = 0
    for idx in lines_idx:
        line = all_lines[idx]
        if not line:
            continue
        filtered_sent = convert_sent_to_word(line)
        len(filtered_sent) > 3 and sentences.append(
                    " ".join(filtered_sent) + "\n")

        if len(sentences) == output_part_size :
            with Path(f"{input_file}_processed/{batch_id}_part{part_id}.txt").open("w") as of:
                of.writelines(sentences)
            sentences = []
            part_id +=1

    with Path(f"{input_file}_processed/{batch_id}_part{part_id}.txt").open("w") as of:
        of.writelines(sentences)
    



def create_batches(input_list: list, num_batches: int) -> list:
    per_batch, rest = divmod(len(input_list), num_batches)

    def batch_gen(start, end):
        i = start
        while i < end and i < len(input_list):
            yield input_list[i]
            i += 1

    return [batch_gen(i * per_batch, (i + 1)*per_batch) for i in range(num_batches)]


if __name__ == "__main__":
    arg_parser = get_argparser()
    args = arg_parser.parse_args()
    articles_dir = args.articles_dir
    is_raw_input = args.raw_input
    output_part_size = args.output_part_size
    num_jobs = args.num_jobs
    num_batches = num_jobs or cpu_count()
    dump_only = args.dump_only

    if args.articles_dir:
        articles_dir = args.articles_dir
        nlp = spacy.load("en_core_web_sm")
        _, _, filenames = next(os.walk(articles_dir), (None, None, []))

        if not filenames:
            print(f"{articles_dir} doesn't contain any file to process!")
            sys.exit(1)
        filenames = [os.path.join(articles_dir, filename) for filename in filenames]

        Path(f"{articles_dir}_processed").mkdir(exist_ok=True)
        with ThreadPoolExecutor() as executor:
            if is_raw_input:
                executor.map(process_raw_file, filenames)
            else:        
                executor.map(process_file, filenames)
    elif args.input_file:
        input_file = args.input_file
        all_lines = []
        chunk_args = []
        with open(input_file) as fh:
            # dont read the entire file as it might exhaust the entire memory
            file_size = Path(input_file).stat().st_size
            chunk_size = file_size//num_batches
            # Arguments for each chunk (eg. [('input.txt', 0, 32), ('input.txt', 32, 64)])
            chunk_start = 0
            while chunk_start < file_size:
                chunk_end = chunk_start + chunk_size
                # make sure the chunk ends at the beginning of the next line
                while chunk_end < file_size:
                    f.seek(chunk_end)
                    if f.read(1) == '\n':
                        chunk_end += 1
                        break
                    chunk_end += 1
    
                chunk_args.append((input_file, chunk_start, chunk_end))
                chunk_start = chunk_end
        Path(f"{input_file}_processed").mkdir(exist_ok=True)
        
        with multiprocessing.Pool(num_batches) as pool:
            pool.starmap(process_lines, chunk_args)
    else:
        print("Please specify either the input file(raw format) or the input file directory.")