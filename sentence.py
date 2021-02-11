import string


class Sentence:
    def __init__(self, user_input):
        content, sentence_end = self.__parse_input(user_input)
        self.content = content
        self.word_count = len(content.split())
        self.sentence_end = sentence_end

    @staticmethod
    def __parse_input(user_input):
        sentence_end = ""
        if user_input[-1:] in string.punctuation:
            sentence_end = user_input[-1:]
        content = ''.join(ch for ch in user_input if ch not in set(string.punctuation))
        return content, sentence_end

    def get_content(self):
        return self.content

    def get_sentence_end(self):
        return self.sentence_end

    def to_string(self):
        return self.content + self.sentence_end

    def get_length(self):
        return len(self.content + self.sentence_end)

    def get_word_count(self):
        return self.word_count
