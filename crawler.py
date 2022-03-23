from pymed import PubMed
import requests
import json
import argparse
import sys
import pathlib


def get_argparser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--mesh-term", action="store", type=str, required=True)

    return argparser


if __name__ == "__main__":
    arg_parser = get_argparser()
    args = arg_parser.parse_args()
    mesh_term = args.mesh_term
    print(mesh_term)

    # Create a PubMed object that GraphQL can use to query
    # Note that the parameters are not required but kindly requested by PubMed Central
    # https://www.ncbi.nlm.nih.gov/pmc/tools/developers/
    pubmed = PubMed(tool="MyTool", email="my@email.address")

    # Create a GraphQL query in plain text
    query = f"(Free full text[Filter]) AND ({mesh_term}[mesh])"

    print(f"query str: {query} ")

    article_ids = pubmed._getArticleIds(query=query, max_results=500000)

    url = "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMC{}/unicode"

    print(f"total retreived articles: {len(article_ids)}")
    if article_ids:
        curdir = "_".join(mesh_term.split())
        pathlib.Path(f"./{curdir}").mkdir()

    for n, article_id in enumerate(article_ids):

        response = requests.get(url.format(article_id))
        if response.status_code == 200:
            with open(f"{curdir}/{article_id}.json", "w") as output_file:
                json.dump(response.json(), output_file, indent=2)
            print(f"Sucssefully retrieved {n} article {article_id}")
        else:
            print(f"Not Found {n} article {article_id}")
        
