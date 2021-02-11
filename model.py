from enum import Enum
import ngram_model
import string
import sentence
import responseBuilder
import error_checker


class Language(Enum):
    ENGLISH = "en"
    GERMAN = "de"


class Model:

    def __init__(self, user_input, language_string):
        self.sentence = sentence.Sentence(user_input)
        self.ngrams = ngram_model.Ngrams(self.sentence, Language(language_string))
        self.mistake_positions = error_checker.get_mistake_positons(self.ngrams)

    def build_response(self):
        response_builder = responseBuilder.ResponseBuilder(self.ngrams, self.sentence, self.mistake_positions)
        return response_builder.build_response()
