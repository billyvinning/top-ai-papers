JOURNAL_DATA_FNAME := scimago_ai_journals.csv

clean:
	rm -f $(JOURNAL_DATA_FNAME)

$(JOURNAL_DATA_FNAME):
	curl https://www.scimagojr.com/journalrank.php\?category\=1702\&out\=xls -o $(JOURNAL_DATA_FNAME)

