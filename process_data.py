import json
import argparse
import os
import spacy
import multiprocessing
from joblib import cpu_count
import tqdm
from convert_num_to_word import convert_num_to_word
import pathlib


def is_text(part_type: str):
    return any(
        [
            part_type.startswith("paragraph"),
            part_type.startswith("abstract"),
        ]
    )


def get_argparser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--articles-dir", action="store", type=str, required=True)

    return argparser


def process_batch(batch_id: int, files: list):
    nlp = spacy.load("en_core_web_sm")
    equation_syms = set(["=", "±", "+", "−"])
    for f in files:
        print(f"batch {batch_id}-{f}")
        with open(os.path.join(articles_dir, f)) as f:
            article = json.load(f)
        sentences = []
        
        for doc in article["documents"]:
            for p in doc["passages"]:
                if is_text(p["infons"]["type"]):
                    text_doc = nlp(p["text"])
                    for sent in text_doc.sents:
                        filtered_sent = [
                            token.text.upper()
                            for token in sent
                            if not any([token.is_punct, token.is_space] or token.text == '%' or token.text =='/')
                        ]
                        
                        if set(filtered_sent).intersection(equation_syms):
                            continue
                            
                        len(filtered_sent) > 3 and sentences.append(
                            convert_num_to_word(" ".join(filtered_sent)) + "\n"
                        )

        with open(f"{articles_dir}_processed/{batch_id}.txt", "a") as wf:
            wf.writelines(sentences)


def create_batches(input_list: list, num_batches: int) -> list:
    per_batch, rest = divmod(len(input_list), num_batches)
    result = [
        input_list[i * per_batch : (i + 1) * per_batch] for i in range(num_batches)
    ]
    result[-1].extend(input_list[-rest:])
    return result


if __name__ == "__main__":
    arg_parser = get_argparser()
    args = arg_parser.parse_args()
    articles_dir = args.articles_dir
    _, _, filenames = next(os.walk(articles_dir), (None, None, []))
    num_cpu = cpu_count()
    filename_in_batches = create_batches(filenames, num_cpu)
    jobs = [(batch_id, filename_in_batches[batch_id]) for batch_id in range(num_cpu)]
    pathlib.Path(f"{articles_dir}_processed").mkdir(exist_ok=True)
    with multiprocessing.Pool(cpu_count()) as pool:
        results = list(tqdm.tqdm(pool.starmap(process_batch, jobs), total=len(jobs)))
