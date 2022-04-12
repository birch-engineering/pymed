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
from concurrent.futures import ThreadPoolExecutor, wait


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
    argparser.add_argument("--additional-processing", action="store_const", const=True, default=False, help="if set, program will only process files that don't exist in the output dir.")
    return argparser

def process_file(file_path: str, is_additional_processing = False, is_dump_only = False):
    articles_dir, filename = os.path.split(file_path)
    output_file_path = f"{articles_dir}_processed/{filename}.txt"
    if is_additional_processing and os.path.exists(output_file_path):
        return
    try:
        with open(file_path) as f:
            article = json.load(f)
    except ValueError:
        print(f"Error reading file {file_name}, skipping")
        return
    sentences = []
    
    for doc in tqdm.tqdm(article["documents"]):
        for p in doc["passages"]:
            if is_text(p["infons"]["type"]):
                text_doc = nlp(p["text"])
                for sent in text_doc.sents:

                    if is_dump_only:
                        sentences.append(sent.text + "\n")
                        continue
                    filtered_sent = convert_sent_to_word(sent.text)
                        
                    len(filtered_sent) > 3 and sentences.append(
                        " ".join(filtered_sent) + "\n"
                    )

    with open(output_file_path, "w") as wf:
        wf.writelines(sentences)

def process_raw_file(file_path, is_additional_processing = False):
    articles_dir, filename = os.path.split(file_path)
    sentences = []
    file_size = Path(file_path).stat().st_size
    output_file_path = f"{articles_dir}_processed/{filename}.txt"
    if is_additional_processing and os.path.exists(output_file_path):
        # output file alread generated before, skip
        return
    with tqdm.tqdm(total=file_size) as pbar:
        with (Path(file_path)).open() as f:
            for line in f:
                line_length = len(line)
                line = line.strip()
                if not line:
                    pbar.update(line_length)
                    continue
                filtered_sent = convert_sent_to_word(line)

                len(filtered_sent) > 3 and sentences.append(
                    " ".join(filtered_sent) + "\n"
                )

                pbar.update(line_length)
    with Path(output_file_path).open("w") as of:
        of.writelines(sentences)


def process_lines(batch_id, chunk_start, chunk_end, input_file, output_part_size = 100000):
    sentences = []
    part_id = 0
    input_file_name = os.path.basename(input_file)

    
    with open(input_file) as fi:
        with tqdm.tqdm(total=chunk_end - chunk_start) as pbar:
            fi.seek(chunk_start)
            while fi.tell() < chunk_end:
                line = fi.readline().strip()
            
                if not line:
                    continue
                filtered_sent = convert_sent_to_word(line)
                len(filtered_sent) > 3 and sentences.append(
                            " ".join(filtered_sent) + "\n")

                if len(sentences) == output_part_size :
                    with Path(f"{input_file}_processed/{input_file_name}_worker{batch_id}_part{part_id}.txt").open("w") as of:
                        of.writelines(sentences)
                    sentences = []
                    part_id +=1

                pbar.update(fi.tell() - chunk_start - pbar.n)

    with Path(f"{input_file}_processed/{input_file_name}_worker{batch_id}_part{part_id}.txt").open("w") as of:
        of.writelines(sentences)
    



def create_batches(input_list: list, num_batches: int) -> list:
    per_batch, rest = divmod(len(input_list), num_batches)

    def batch_gen(start, end):
        i = start
        while i < end and i < len(input_list):
            yield input_list[i]
            i += 1

    return [batch_gen(i * per_batch, (i + 1)*per_batch) for i in range(num_batches)]


def process_data(args):
    is_raw_input = args.raw_input
    output_part_size = args.output_part_size
    num_batches = args.num_jobs or cpu_count()
    is_dump_only = args.dump_only
    is_additional_processing = args.additional_processing

    # only need one of those two options for input, either a dir or an input file
    input_file = args.input_file
    articles_dir = args.articles_dir
    if articles_dir:
        global nlp
        nlp = spacy.load("en_core_web_sm")
        
        _, _, filenames = next(os.walk(articles_dir), (None, None, []))
        
        if not filenames:
            print(f"{articles_dir} doesn't contain any file to process!")
            sys.exit(1)
        filenames = [os.path.join(articles_dir, filename) for filename in filenames]

        Path(f"{articles_dir}_processed").mkdir(exist_ok=True)
        print(f"Create output dir {articles_dir}_processed, total number of input files {len(filenames)}")

        with ThreadPoolExecutor() as executor:
            if is_raw_input:
                results = executor.map(partial(process_raw_file, is_additional_processing=is_additional_processing), filenames)
                
            else:        
                results = executor.map(partial(process_file, is_additional_processing=is_additional_processing, is_dump_only = is_dump_only), filenames)
                
                
    elif input_file:


        chunk_args = []
        batch_cnt = 0
        with open(input_file) as fh:
            # dont read the entire file as it might exhaust the entire memory
            file_size = Path(input_file).stat().st_size
            chunk_size = file_size//num_batches
            # Arguments for each chunk (eg. [('input.txt', 0, 32), ('input.txt', 32, 64)])
            chunk_start = 0
            while chunk_start < file_size:
                chunk_end = min(chunk_start + chunk_size, file_size)
                # make sure the chunk ends at the beginning of the next line
                while chunk_end < file_size:
                    fh.seek(chunk_end)
                    if fh.read(1) == '\n':
                        chunk_end += 1
                        break
                    chunk_end += 1
                chunk_args.append((batch_cnt, chunk_start, chunk_end))
                batch_cnt += 1
                chunk_start = chunk_end
        Path(f"{input_file}_processed").mkdir(exist_ok=True)
        print(f"Create output dir {input_file}_processed ...")
        with multiprocessing.Pool(num_batches) as pool:
            pool.starmap(partial(process_lines, input_file = input_file, output_part_size = output_part_size), chunk_args)
    else:
        print("Please specify either the input file(raw format) or the input file directory.")

if __name__ == "__main__":
    arg_parser = get_argparser()
    args = arg_parser.parse_args()

    process_data(args)