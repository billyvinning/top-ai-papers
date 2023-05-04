from argparse import ArgumentParser
from html.parser import HTMLParser
from io import StringIO

import pandas as pd

N_ALLTIME_PAPERS = 20
N_DECADAL_PAPERS = 5


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def clean_citations(df):
    out_df = df.copy()
    out_df["title"] = out_df.title.apply(lambda x: ", ".join(x))
    out_df["title"] = out_df.title.apply(strip_tags)
    out_df["title"] = out_df.title.apply(lambda x: x.replace("\n", "").strip())
    out_df["ISSN"] = out_df.ISSN.apply(lambda x: x[-1])
    out_df["DOI"] = out_df.DOI.apply(lambda x: f"[{x}](https://doi.org/{x})")

    # out_df['author'] = out_df.author.apply(lambda x: ', '
    # .join(n['family'] for n in x))
    out_df["year"] = out_df.published.apply(lambda x: x["date-parts"][0][0])
    out_df = (
        out_df.sort_values(
            ["year", "is-referenced-by-count"],
            ascending=[True, False],
        )
        .groupby("year")
        .head(5)
    )
    out_df["yearly_ranking"] = (
        out_df.groupby("year")["is-referenced-by-count"]
        .rank(ascending=False)
        .astype(int)
    )
    out_df["decade"] = out_df.year - (out_df.year % 10)
    out_df["decade_ranking"] = (
        out_df.groupby("decade")["is-referenced-by-count"]
        .rank(ascending=False)
        .astype(int)
    )
    out_df["alltime_ranking"] = (
        out_df["is-referenced-by-count"].rank(ascending=False).astype(int)
    )

    out_df = out_df.rename(
        columns={
            "title": "Title",
            "year": "Year",
            "decade": "Decade",
            "yearly_ranking": "Yearly Ranking",
            "decade_ranking": "Decade Ranking",
            "alltime_ranking": "All-Time Ranking",
            "journal": "Journal",
            "is-referenced-by-count": "No. Citations",
        }
    )
    return out_df[
        [
            "Title",
            "DOI",
            "Year",
            "Decade",
            "Journal",
            "Yearly Ranking",
            "Decade Ranking",
            "All-Time Ranking",
            "No. Citations",
        ]
    ]


def tabulate_alltime_rankings(df):
    df = df.sort_values("No. Citations", ascending=False).head(
        N_ALLTIME_PAPERS
    )
    df = df.rename(columns={"All-Time Ranking": "Rank"})
    df = df[["Rank", "No. Citations", "Title", "Journal", "DOI", "Year"]]
    return df.to_markdown(tablefmt="github", index=False)


def tabulate_decadal_rankings(df):
    out = []
    df = df.sort_values(["Decade", "No. Citations"], ascending=False)
    for decade, group_df in df.groupby("Decade"):
        df = group_df.head(N_DECADAL_PAPERS)
        df = df.rename(columns={"Decade Ranking": "Rank"})
        df = df[["Rank", "No. Citations", "Title", "Journal", "DOI"]]
        table = df.to_markdown(tablefmt="github", index=False)
        out.append(f"{decade}'s\n")
        out.append(table)
    return "\n".join(out)


def run(
    citations_data_path,
    input_path,
    output_path,
):
    citation_data = pd.read_csv(
        citations_data_path,
        converters={
            "title": eval,
            "published": eval,
            "ISSN": eval,
            "year": eval,
        },
    )
    citation_data_clean = clean_citations(citation_data)

    with open(input_path, "r") as f:
        template_readme = f.read()

    table_data = f"""
## All-Time Rankings
{tabulate_alltime_rankings(citation_data_clean)}
## Decadal Rankings
{tabulate_decadal_rankings(citation_data_clean)}
    """

    print(table_data)
    formatted_readme = template_readme.format(table_data=table_data)

    with open(output_path, "w") as f:
        f.write(formatted_readme)


def parse_args():
    parser = ArgumentParser(description="Fetch citation data.")
    parser.add_argument("citations_data_path", help="Path to citations data.")
    parser.add_argument(
        "-i",
        "--input-path",
        help="Path to input README (must feature {table_data} placeholder).",
    )
    parser.add_argument("-o", "--output-path", help="Path to output README.")
    return parser.parse_args()


def main():
    args = parse_args()
    return run(
        citations_data_path=args.citations_data_path,
        input_path=args.input_path,
        output_path=args.output_path,
    )


if __name__ == "__main__":
    main()
