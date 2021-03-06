# database config
DATABASE_NAME = "ngrams"
DATABASE_USERNAME = "postgres"
DATABASE_PASSWORD = "postgres"
DATABASE_HOST = "localhost"
DATABASE_PORT = "5432"
# ngram config
MAX_NGRAM_SIZE = 4
START_YEAR = 2000
END_YEAR = 2020
TOTAL_NGRAM_COUNTS_ENGLISH = [27725227037, 29131577058, 26318878130, 26318878130]
TOTAL_NGRAM_COUNTS_GERMAN = [4173133161, 4390391801, 4173133161, 3955874750]
# error_checker config
DAMPENER = 0.4
THRESHOLD = 0.00008
BACKOFF_THRESHOLD_DIVIDER = 300000
ESTIMATED_ONE_GRAM_COUNT = 50000000
START_TOKEN_COUNT = 100000
# suggestion config
RESULTS_COUNT = 4
