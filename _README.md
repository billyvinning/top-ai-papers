# top-ai-papers

This repository is intended as a resource that aggregates the most-cited papers published within the most-influential Artificial Intelligence (AI) journals. The results are tabulated lower in this `README`; provided are all-time rankings and decadal rankings from {year_lower} to {year_upper}. The most-influential AI journals considered are those according to [SCImago's](https://www.scimagojr.com/) SCImago Journal Rank (SJR) indicator; the number of citations are provided by [Crossref](https://www.crossref.org/).

# Rankings

{table_data}

# Building

This section provides instructions for running the scraper. Only Python version `3.10.10` has been tested.`curl` must also be available in order to fetch the journal data. To install the dependencies for the scraper, first run `pip install -r requirements.txt`. To run the scraper and add the results to the `README.md`, run:
    
    make clean && make

# License

This project is subject to the GPLv3 license. Please refer to `COPYING.rst` for the details.


