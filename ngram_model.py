import itertools
import config
import dataAccessor


class Ngrams:
    def __init__(self, sentence, language):
        self.sentence = sentence
        self.language = language
        self.ngrams = self.__build_ngrams()
        self.values = dataAccessor.DataAccessor(sentence, self.get_all_ngrams(), language).get_values()

    def get_language(self):
        return self.language

    def get_values(self):
        return self.values

    def get_all_ngrams(self):
        return list(itertools.chain.from_iterable(self.ngrams))

    def get_ngrams(self, n):
        return self.ngrams[n-1]

    def __build_ngrams(self):
        ngrams = []
        tokens = ["_START_"] + self.sentence.get_content().split()
        for i in range(1, config.MAX_NGRAM_SIZE + 1):
            ngrams.append(self.__build_ngrams_size_n(tokens, i))
        return ngrams

    @staticmethod
    def __build_ngrams_size_n(tokens, n):
        ngrams_size_n = []
        for word_position in range(len(tokens) - (n - 1)):
            ngrams_size_n.append(Ngrams.__concatenate_ngram_from_tokens(word_position, n, tokens))
        return ngrams_size_n

    @staticmethod
    def __concatenate_ngram_from_tokens(word_position, n, tokens):
        ngram = tokens[word_position]
        for i in range(1, n):
            ngram += " " + tokens[word_position + i]
        return ngram
