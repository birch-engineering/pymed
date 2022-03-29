import sys


def prune_duplicate(*filenames) -> list:
    sentences = set()
    for file in filenames:
        with open(file) as f:
            sentences.update([line.strip() for line in f])
    return list(sentences)


if __name__ == "__main__":
    prog, *files = sys.argv

    for sent in prune_duplicate(*files):
        print(sent)
