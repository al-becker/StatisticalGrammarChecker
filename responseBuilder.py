from flask import jsonify
import responseSentence
import bert


class ResponseBuilder:
    def __init__(self, ngrams, sentence, mistake_positions):
        self.ngrams = ngrams
        self.input_sentence = sentence
        self.response_sentence = self.__build_response_sentence(mistake_positions)
        self.debug_box = self.__build_debug_box()

    def build_response(self):
        return self.__build_json()

    def __build_json(self):
        data = {"content": self.response_sentence.get_html_sentence(),
                "errorcount": self.response_sentence.get_error_count(),
                "ngramcounts": self.debug_box,
                "tokencount": self.input_sentence.get_length(),
                "wordcount": self.input_sentence.get_word_count()}
        return jsonify(data)

    def __build_debug_box(self):
        values = self.ngrams.get_values()
        debug_values_html = ["<span>" + i + " : " + str(values[i]) + "</span>" for i in values]
        return "".join(debug_values_html)

    def __build_response_sentence(self, mistake_positions):
        html_tokens = self.ngrams.get_ngrams(1)[1:].copy()
        for mistake_position in mistake_positions:
            bert_model = bert.BERT.instance()
            suggestions = bert_model.get_correction_suggestion(self.input_sentence, mistake_position, self.ngrams)
            html_tokens[mistake_position] = self.__generate_suggestion_box(mistake_position, suggestions)
        html_sentence = " ".join(html_tokens) + self.input_sentence.get_sentence_end()
        return responseSentence.ResponseSentence(html_sentence, mistake_positions)

    def __generate_suggestion_box(self, mistake_position, suggestions):
        return '<mark id="' + str(mistake_position) + '" ' + \
               'suggestions="' + " ".join(suggestions["token_strs"]) + '" ' + \
               'scores="' + " ".join(['{:.3f}'.format(x) for x in suggestions["scores"]]) + '" ' \
               'ranks="' + " ".join(['{:.3f}'.format(x) for x in suggestions["ranks"]]) + '">' + \
               self.ngrams.get_ngrams(1)[mistake_position + 1] + '</mark>'
