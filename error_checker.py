import config

def get_error(sentence, values):
    sentence = "_START_ " + sentence
    error_values = []

    one_grams = sentence.split()
    two_grams = [one_grams[i] + ' ' + one_grams[i + 1] for i in range(len(one_grams) - 1)]
    three_grams = [one_grams[i] + ' ' + one_grams[i + 1] + ' ' + one_grams[i + 2] for i in range(len(one_grams) - 2)]
    four_grams = [one_grams[i] + ' ' + one_grams[i + 1] + ' ' + one_grams[i + 2] + ' ' + one_grams[i + 3] for i in range(len(one_grams) - 3)]

    token_count = len(one_grams)
    for i in range(1, token_count):
        min_value = min(int(values[one_grams[i]] / config.BACKOFF_THRESHOLD_DIVIDER), 10)

        if token_count > 4 and values[four_grams[i - 3]] > min_value and i > 2:
            error_value = values[four_grams[i - 3]] / values[three_grams[i - 3]]
            error_values.append(error_value)

        elif token_count > 3 and values[three_grams[i - 2]] > min_value and i > 1:
            error_value = config.DAMPENER * values[three_grams[i - 2]] / values[two_grams[i - 2]]
            if i == 2:
                error_value *= (1/config.DAMPENER)
            error_values.append(error_value)

        elif token_count > 2 and values[two_grams[i - 1]] > min_value:
            if i == 1:
                error_value = values[two_grams[i - 1]] / config.START_TOKEN_COUNT
            else:
                error_value = config.DAMPENER * config.DAMPENER * values[two_grams[i - 1]] / values[one_grams[i - 1]]
            error_values.append(error_value)

        else:
            error_value = config.DAMPENER * config.DAMPENER * config.DAMPENER * values[one_grams[i]] / config.ESTIMATED_ONE_GRAM_COUNT
            error_values.append(error_value)

    mistakes = []
    for i in range(len(error_values)):
        if error_values[i] < config.THRESHOLD:
            mistakes.append(i)
    return mistakes

