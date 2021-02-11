from transformers import pipeline
import ngram_model
from singleton import Singleton
import error_checker
import distance
import string
import model
import config
import sentence


@Singleton
class BERT:
    def __init__(self):
        self.bert_de = pipeline('fill-mask', model='dbmdz/bert-base-german-uncased', top_k=20)
        self.bert_en = pipeline('fill-mask', model='bert-base-uncased', top_k=20)

    def get_correction_suggestion(self, incorrect_sentence, mistake_position, ngrams):
        words = ngrams.get_ngrams(1)[1:]
        mistake = words[mistake_position]
        masked_words = words.copy()
        masked_words[mistake_position] = '[MASK]'
        masked_sentence = " ".join(masked_words) + incorrect_sentence.get_sentence_end()

        if self.__is_duplicated_word_error(words, mistake_position):
            return {"token_strs": [""], "scores": [1], "ranks": [1]}

        bert_suggestions = self.__get_suggestions(masked_sentence, ngrams.get_language())
        results = self.__create_results(bert_suggestions, mistake)
        top_results = self.__build_top_results(results)
        top_results = self.__check_top_results(masked_sentence, mistake_position, ngrams, top_results)
        return top_results

    def __get_suggestions(self, masked_sentence, language):
        if language == model.Language:
            bert_suggestions = self.bert_de(masked_sentence)
        else:
            bert_suggestions = self.bert_en(masked_sentence)
        return bert_suggestions

    @staticmethod
    def __build_top_results(results):
        results.sort(key=lambda pair: pair[0], reverse=True)
        top_results = {"ranks": [a_tuple[0] for a_tuple in results[:config.RESULTS_COUNT]],
                       "token_strs": [a_tuple[1] for a_tuple in results[:config.RESULTS_COUNT]],
                       "scores": [a_tuple[2] for a_tuple in results[:config.RESULTS_COUNT]]}
        return top_results

    @staticmethod
    def __check_top_results(masked_sentence, mistake_position, ngrams, top_results):
        i = 0
        while i != len(top_results["token_strs"]):
            suggestion_sentence = masked_sentence.replace("[MASK]", top_results["token_strs"][i])
            suggestion_ngrams = ngram_model.Ngrams(sentence.Sentence(suggestion_sentence), ngrams.language)
            suggestion_mistake_positions = error_checker.get_mistake_positons(suggestion_ngrams)
            if mistake_position in suggestion_mistake_positions:
                del top_results["token_strs"][i]
                del top_results["scores"][i]
                del top_results["ranks"][i]
            else:
                i += 1
        return top_results

    @staticmethod
    def __create_results(bert_suggestions, mistake):
        result = []
        for suggestion in bert_suggestions:
            if suggestion["token_str"] in string.punctuation or suggestion["score"] < 0.003 or \
                    mistake == suggestion["token_str"]:
                continue

            word_distance = min(distance.levenshtein(suggestion["token_str"], mistake), len(mistake))
            rank = (((len(mistake) - word_distance) / len(mistake)) * 10) ** 3 * suggestion["score"]
            result.append((rank, suggestion["token_str"], suggestion["score"]))
        return result

    @staticmethod
    def __is_duplicated_word_error(one_grams, mistake_position):
        if one_grams[mistake_position - 1] == one_grams[mistake_position]:
            return True
        return False
