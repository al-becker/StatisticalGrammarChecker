from transformers import pipeline
from error_checker import get_error
from ngram import Ngram
import distance
import string

bert_de = pipeline('fill-mask', model='dbmdz/bert-base-german-uncased', top_k=20)
bert_en = pipeline('fill-mask', model='bert-base-uncased', top_k=20)


# needs a sentence where the wrong word is replaced by a MASK
# example: input: We enjoys [MASK] movies
# returns {'token_strs': ['were', 'are'], 'scores': [0.5045040249824524, 0.4793391227722168]}
def get_correction_suggestions(input_text, mistake, mistake_pos, language, con):
    if duplicated_words(input_text, mistake_pos, mistake):
        return {"token_strs": [""], "scores": [1], "ranks": [1]}
    if language == 'de':
        bert_suggestions = bert_de(input_text)
    else:
        bert_suggestions = bert_en(input_text)
    result = []

    for suggestion in bert_suggestions:
        if suggestion["token_str"] in string.punctuation or suggestion["score"] < 0.003 or mistake == suggestion["token_str"]:
            continue

        word_distance = min(distance.levenshtein(suggestion["token_str"], mistake), len(mistake))
        rank = (((len(mistake) - word_distance) / len(mistake)) * 10) ** 3 * suggestion["score"]
        result.append((rank, suggestion["token_str"], suggestion["score"]))
        result.sort(key=lambda pair: pair[0], reverse=True)
    sorted_results = {"token_strs": [a_tuple[1] for a_tuple in result[:4]],
                      "scores": [a_tuple[2] for a_tuple in result[:4]],
                      "ranks": [a_tuple[0] for a_tuple in result[:4]]}

    i = 0
    while i != len(sorted_results["token_strs"]):
        input_text = input_text.replace("[MASK]", sorted_results["token_strs"][i])
        sentence = Ngram(input_text.strip(string.punctuation), language, con)
        mistakes = get_error(sentence, sentence.values)
        if mistake_pos in mistakes:
            del sorted_results["token_strs"][i]
            del sorted_results["scores"][i]
            del sorted_results["ranks"][i]
        else:
            i += 1

    return sorted_results


def duplicated_words(input_text, mistake_pos, mistake):
    if input_text.split()[mistake_pos - 1] == mistake:
        return True
    return False
