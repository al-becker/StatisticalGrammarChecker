import config


def get_mistake_positons(ngrams):
    error_values = []

    token_count = len(ngrams.get_ngrams(1))
    for word_position in range(1, token_count):
        error_values.append(__calculate_error_likelihood(word_position, ngrams, token_count))

    mistakes = []
    for i in range(len(error_values)):
        if error_values[i] < config.THRESHOLD:
            mistakes.append(i)
    return mistakes


def __calculate_error_likelihood(word_position, ngrams, token_count):
    values = ngrams.get_values()
    min_value = min(int(values[ngrams.get_ngrams(1)[word_position]] / config.BACKOFF_THRESHOLD_DIVIDER), 10)

    if token_count > 4 and values[ngrams.get_ngrams(4)[word_position - 3]] > min_value and word_position > 2:
        error_value = values[ngrams.get_ngrams(4)[word_position - 3]] / values[ngrams.get_ngrams(3)[word_position - 3]]

    elif token_count > 3 and values[ngrams.get_ngrams(3)[word_position - 2]] > min_value and word_position > 1:
        error_value = config.DAMPENER * values[ngrams.get_ngrams(3)[word_position - 2]] / values[ngrams.get_ngrams(2)[word_position - 2]]
        if word_position == 2:
            error_value *= (1 / config.DAMPENER)

    elif token_count > 2 and values[ngrams.get_ngrams(2)[word_position - 1]] > min_value:
        if word_position == 1:
            error_value = values[ngrams.get_ngrams(2)[word_position - 1]] / config.START_TOKEN_COUNT
        else:
            error_value = config.DAMPENER * config.DAMPENER * values[ngrams.get_ngrams(2)[word_position - 1]] / values[
                ngrams.get_ngrams(1)[word_position - 1]]

    else:
        error_value = config.DAMPENER * config.DAMPENER * config.DAMPENER * values[
            ngrams.get_ngrams(1)[word_position]] / config.ESTIMATED_ONE_GRAM_COUNT
    return error_value

