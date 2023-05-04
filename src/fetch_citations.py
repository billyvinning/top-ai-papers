import json
from argparse import ArgumentParser

import pandas as pd
import requests
import tqdm

N_JOURNALS = 20  # Top N journals to parse papers from.
YEAR_PUBLISHED_RANGE = (
    1990,
    2024,
)  # (Low, High) range of published date years.
N_PAPERS = 5  # Number of papers to parse per journal.


def compile_query(**kwargs):
    out = []
    for k, v in kwargs.items():
        if isinstance(v, dict):
            delim = ":" if k == "filter" else "="
            q = ",".join(f"{kk}{delim}{vv}" for kk, vv in v.items())
        elif isinstance(v, (list, tuple)):
            q = ",".join(v)
        else:
            q = v
        out.append(f"{k}={q}")
    return "&".join(out)


def scrape_journal_selection(issn, year, dry_run=False, **kwargs):
    cursor = "*"
    query = compile_query(
        filter={
            "from-pub-date": year,
            "until-pub-date": year,
        },
        sort="is-referenced-by-count",
        order="desc",
        rows=N_PAPERS,
        **kwargs,
    )
    url = f"https://api.crossref.org/journals/{issn}/works?{query}"
    records = []
    if dry_run:
        print(url)
        return

    while 1:
        response = requests.get(f"{url}&cursor={cursor}")
        assert response.status_code == 200, (url, response.status_code)
        message = json.loads(response.text)["message"]
        items = message["items"]
        if not items:
            break
        records.extend(items)
        break

    return records


def run(journal_data_path, output_path):
    journals_df = pd.read_csv(journal_data_path, sep=";")
    journals_df = journals_df[journals_df["Type"] == "journal"]
    journals_df = journals_df.sort_values("SJR", ascending=False).head(
        N_JOURNALS
    )
    dfs = []
    for row in journals_df.itertuples():
        records = []
        for year in tqdm.trange(*YEAR_PUBLISHED_RANGE):
            year_records = scrape_journal_selection(
                issn=row.Issn.split(",")[-1].strip(),
                select=[
                    "title",
                    "ISSN",
                    "author",
                    "published",
                    "DOI",
                    "is-referenced-by-count",
                ],
                year=year,
            )
            records.extend(year_records)

        df = pd.DataFrame(records)
        df["journal"] = row.Title
        dfs.append(df)

    df = pd.concat(dfs)
    df.to_csv(output_path)


def parse_args():
    parser = ArgumentParser(description="Fetch citation data.")
    parser.add_argument("journal_data_path", help="Path to journal ISSN data.")
    parser.add_argument("-o", "--output-path", help="Path to output data.")
    return parser.parse_args()


def main():
    args = parse_args()
    return run(
        journal_data_path=args.journal_data_path, output_path=args.output_path
    )


if __name__ == "__main__":
    main()
