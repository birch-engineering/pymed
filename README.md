# PyMed with changes made by Ziyuan 


## user the crawler 

scrape clinical data using pymed from pubmed.  
1. choose search term based on [mesh](https://www.ncbi.nlm.nih.gov/mesh), for instance, Radiology
2. for other possible search options, see [build advanced search](https://pubmed.ncbi.nlm.nih.gov/advanced/)
3. crawler first use pymed to query for the list of articles for that search term
4. carwler then uses [BioC API](https://www.ncbi.nlm.nih.gov/research/bionlp/APIs/BioC-PubMed/) to download each article and store them to another directory.


```bash
nohup python pymed/crawler.py --mesh-term="Radiology" &>>LOGS/Radiology.log& 
```

the output is in [BioC json format](http://bioc.sourceforge.net/#:~:text=BioC%20is%20a%20simple%20format,and%20perform%20some%20sample%20processing.)

outputs will be stored to `Radiology` directory, which is created by the script

## process the data

process the scraped data into capitalized plain text format, numbers and signs converted to spoken words. 

see `test/test_convert_num.py` for examples of such conversions


```bash
nohup python pymed/process_data.py --articles-dir=Radiology &>>PLOGS/Radiology.log& 

```

outputs will be stored to `Radiology_processed` directory, which is crated by the script


# PyMed - PubMed Access through Python
PyMed is a Python library that provides access to PubMed through the PubMed API.

## Why this library?
The PubMed API is not very well documented and querying it in a performant way is too complicated and time consuming for researchers. This wrapper provides access to the API in a consistent, readable and performant way.

## Features
This library takes care of the following for you:

- Querying the PubMed database (with the standard PubMed query language)
- Batching of requests for better performance
- Parsing and cleaning of the retrieved articles

## Examples
For full (working) examples have a look at the `examples/` folder in this repository. In essence you only need to import the `PubMed` class, instantiate it, and use it to query:

```python
from pymed import PubMed
pubmed = PubMed(tool="MyTool", email="my@email.address")
results = pubmed.query("Some query", max_results=500)
```

## Notes on the API
The original documentation of the PubMed API can be found here: [PubMed Central](https://www.ncbi.nlm.nih.gov/pmc/tools/developers/). PubMed Central kindly requests you to:

> - Do not make concurrent requests, even at off-peak times; and
> - Include two parameters that help to identify your service or application to our servers
>   * _tool_ should be the name of the application, as a string value with no internal spaces, and
>   * _email_ should be the e-mail address of the maintainer of the tool, and should be a valid e-mail address.

## Notice of Non-Affiliation and Disclaimer 
The author of this library is not affiliated, associated, authorized, endorsed by, or in any way officially connected with PubMed, or any of its subsidiaries or its affiliates. The official PubMed website can be found at https://www.ncbi.nlm.nih.gov/pubmed/.
