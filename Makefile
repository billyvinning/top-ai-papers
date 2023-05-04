JOURNAL_DATA := scimago_ai_journals.csv
CITATIONS_DATA := papercitations.csv
TABLE_DATA := tabledata.md 
README := README.md
README_FMT := _README.md

all: $(README)


clean:
	rm -f $(JOURNAL_DATA) $(CITATIONS_DATA) $(README)

$(JOURNAL_DATA):
	curl https://www.scimagojr.com/journalrank.php\?category\=1702\&out\=xls -o $(JOURNAL_DATA)


$(CITATIONS_DATA): $(JOURNAL_DATA)
	python src/fetch_citations.py $(JOURNAL_DATA) -o $(CITATIONS_DATA)


$(README): $(CITATIONS_DATA)
	python src/build_readme.py $(CITATIONS_DATA) -i $(README_FMT) -o $(README)
