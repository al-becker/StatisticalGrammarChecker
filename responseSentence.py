class ResponseSentence:
    def __init__(self, html_sentence, error_count):
        self.html_sentence = html_sentence
        self.error_count = error_count

    def get_html_sentence(self):
        return self.html_sentence

    def get_error_count(self):
        return self.error_count
