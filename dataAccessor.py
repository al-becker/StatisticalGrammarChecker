from lxml import html
from numpy.lib.function_base import average
import requests
import re
import database
import config
import model


class DataAccessor:
    def __init__(self, sentence, ngrams, language):
        self.sentence = sentence
        self.ngrams = ngrams
        self.language = language
        self.START_YEAR = config.START_YEAR
        self.END_YEAR = config.END_YEAR

    def get_values(self):
        ngram_values_db = self.__get_ngrams_db()
        ngrams_found_db = list(ngram_values_db)
        ngrams_remain = self.__calculate_remaining_ngrams(ngrams_found_db)
        ngram_values_viewer = self.__get_ngrams_viewer(ngrams_remain)
        return {**ngram_values_db, **ngram_values_viewer}

    def __get_ngrams_db(self):
        values = {}
        records = database.Database.instance().select_rows(
            "SELECT * from ngram_{} where ngram IN {}"
                .format(self.language.value, tuple(self.ngrams)))

        for record in records:
            values[record[0]] = record[1]
        return values

    def __get_ngrams_viewer(self, ngrams_remain):
        corpus = self.get_corpus_id()

        ngram_values = {}
        for ngrams_chunk in self.divide_list_to_chunks_of_length_n(ngrams_remain, 10):
            ngram_values = {**ngram_values, **self.__extract_counts_from_ngram_viewer(corpus, ngrams_chunk)}

        ngram_values = self.__fill_not_found_values(ngrams_remain, ngram_values)
        self.__insert_ngrams_db(ngram_values)
        return ngram_values

    def __extract_counts_from_ngram_viewer(self, corpus, ngrams_chunk):
        page = requests.get(
            'https://books.google.com/ngrams/graph?content={}&year_start={}&year_end={}&corpus={}'.format(
                '%2C'.join(ngrams_chunk), self.START_YEAR, self.END_YEAR, corpus))
        script = html.fromstring(page.content).xpath('//script[preceding::div[@id="chart"]]/text()')
        json_data = re.findall(r'({"ngram".*?})', str(script))
        return self.__extract_values_from_json_data(json_data)

    def __extract_values_from_json_data(self, data):
        values = {}
        for i in range(len(data)):
            timeseries = re.findall(r'(?<="timeseries": \[)([\d.e\-, ]*)', data[i])
            ngram = re.findall(r'(?<="ngram": ")([\w ]*)', data[i])[0]
            relative_values_per_year = [float(i) for i in re.sub(r',', '', timeseries[0]).split()]

            values[ngram] = self.__sum_relative_values_per_year(relative_values_per_year, ngram.count(' '))
        return values

    def __sum_relative_values_per_year(self, relative_values_per_year, n):
        total_counts = []
        if self.language == model.Language.GERMAN:
            total_counts = config.TOTAL_NGRAM_COUNTS_GERMAN
        elif self.language == model.Language.ENGLISH:
            total_counts = config.TOTAL_NGRAM_COUNTS_ENGLISH
        return int(average(relative_values_per_year) / (1 / total_counts[n]))

    def __calculate_remaining_ngrams(self, ngrams_db):
        remaining_ngrams = [ngram for ngram in self.ngrams if ngram not in ngrams_db]
        return remaining_ngrams

    def __insert_ngrams_db(self, values):
        db = database.Database.instance()
        for value in values:
            db.execute("INSERT INTO ngram_{} (ngram,count) VALUES ('{}',{})"
                       .format(self.language.value, value, values[value]))
        db.commit()

    def get_corpus_id(self):
        corpus = 0
        if self.language == model.Language.ENGLISH:
            corpus = 26
        elif self.language == model.Language.GERMAN:
            corpus = 31
        return corpus

    @staticmethod
    def __fill_not_found_values(ngrams_remain, ngram_values):
        for ngram in ngrams_remain:
            if ngram not in ngram_values:
                ngram_values[ngram] = 0
        return ngram_values

    @staticmethod
    def divide_list_to_chunks_of_length_n(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]
