from lxml import html
from numpy.lib.function_base import average
import requests
import re


class Ngram:
    def __init__(self, language, db_connection, sentence):
        self.language = language
        self.START_YEAR = 2000
        self.END_YEAR = 2020
        self.sentence = sentence
        self.db_connection = db_connection
        self.ngrams = self.build_ngrams()
        self.values = self.get_ngram_counts()

    def get_ngram_counts(self):
        db_cur = self.db_connection.cursor()
        ngram_values_db, ngrams_remain = self.get_ngrams_db(db_cur)
        ngram_values_viewer = self.get_ngrams_viewer(ngrams_remain)
        self.insert_ngrams_db(ngram_values_viewer, db_cur)
        db_cur.close()

        return self.sum_values({**ngram_values_db, **ngram_values_viewer})

    def build_ngrams(self):
        sentence = "_START_ " + self.sentence
        tokens = sentence.split()
        ngrams = tokens.copy()
        for i in range(len(tokens) - 1):
            ngrams.append(tokens[i] + ' ' + tokens[i + 1])
        for i in range(len(tokens) - 2):
            ngrams.append(tokens[i] + ' ' + tokens[i + 1] + ' ' + tokens[i + 2])
        for i in range(len(tokens) - 3):
            ngrams.append(tokens[i] + ' ' + tokens[i + 1] + ' ' + tokens[i + 2] + ' ' + tokens[i + 3])
        return ngrams

    @staticmethod
    def divide_list_to_chunks_of_length_n(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def get_ngrams_db(self, db_cur):
        values = {}
        ngrams_found_in_db = []
        for ngram in self.ngrams:
            db_cur.execute(
                "SELECT * from ngram_{} where ngram = '{}' and year >= {} and year <= {}".format(self.language, ngram,
                                                                                                 self.START_YEAR,
                                                                                                 self.END_YEAR))
            data = db_cur.fetchall()
            if data:
                counts = []
                for row in data:
                    counts.append(row[1])
                values[data[0][0]] = counts
                if len(data) == self.END_YEAR - self.START_YEAR:
                    ngrams_found_in_db.append(ngram)
        return values, [ngram for ngram in self.ngrams if ngram not in ngrams_found_in_db]

    def get_ngrams_viewer(self, ngrams):
        values = {}
        corpus = 0
        if self.language == 'en':
            corpus = 26
        elif self.language == "de":
            corpus = 31
        for ngrams_chunk in self.divide_list_to_chunks_of_length_n(ngrams, 10):
            page = requests.get(
                'https://books.google.com/ngrams/graph?content={}&year_start={}&year_end={}&corpus={}'.format(
                    '%2C'.join(ngrams_chunk), self.START_YEAR, self.END_YEAR, corpus))
            script = html.fromstring(page.content).xpath('//script[preceding::div[@id="chart"]]/text()')
            data = re.findall(r'({"ngram".*?})', str(script))

            for i in range(len(data)):
                timeseries = re.findall(r'(?<="timeseries": \[)([\d.e\-, ]*)', data[i])
                ngram = re.findall(r'(?<="ngram": ")([\w ]*)', data[i])
                values[ngram[0]] = [float(i) for i in re.sub(r',', '', timeseries[0]).split()]

        for ngram in ngrams:
            if ngram not in values:
                values[ngram] = [0] * (self.END_YEAR - self.START_YEAR)
        return values

    def insert_ngrams_db(self, values, db_cur):
        for value in values:
            year = self.START_YEAR
            for count in values[value]:
                db_cur.execute(
                    "INSERT INTO ngram_{} (ngram,count,year) VALUES ('{}',{},{})".format(self.language, value, count, year))
                year = year + 1

        self.db_connection.commit()

    def sum_values(self, values):
        total_counts = []
        if self.language == "de":
            total_counts = [
                4173133161,
                4390391801,
                4173133161,
                3955874750
            ]
        elif self.language == "en":
            total_counts = [
                27725227037,
                29131577058,
                26318878130,
                26318878130
            ]
        summed_values = {}
        for value in values:
            count = average(values[value])
            # numbers are average ngram counts of 1,2,3 and 4 grams
            # identical numbers probably wrong
            if value.count(' ') == 0:
                count = count / (1 / total_counts[0])
            elif value.count(' ') == 1:
                count = count / (1 / total_counts[1])
            elif value.count(' ') == 2:
                count = count / (1 / total_counts[2])
            elif value.count(' ') == 3:
                count = count / (1 / total_counts[3])
            summed_values[value] = int(count)
        return summed_values
