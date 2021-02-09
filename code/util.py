import string

def text_to_ngram(text, n):
    return [text[i: i+n] for i in range(len(text)-n+1)]


def ngram_scoring(word1, word2, n):
    tr1 = text_to_ngram(word1, n)
    tr2 = text_to_ngram(word2, n)

    if len(tr1) == 0 or len(tr2) == 0:
        return 0

    common_trigrams = [tr for tr in tr1 if tr in tr2]

    return len(common_trigrams)/(max(len(tr1), len(tr2)))


def get_coordinate_from_style(style_string, coord):
    to_find = " " + coord + ":"
    found = style_string.find(to_find)
    if found == -1:
        return None
    else:
        start = found + len(to_find)

    end = style_string.find("px", start)

    return int(style_string[start:end])


def remove_punctuation(s):
    return s.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation))).encode("utf-8", "ignore").decode()

def remove_punctuation2(s):
    return s.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation))).encode("ascii", "ignore").decode()

