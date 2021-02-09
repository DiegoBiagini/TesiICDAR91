"""
This file contains functions used to load dictionaries from files and use them for various tasks
"""
import json
import Levenshtein
import util

def load_txt_dictionary(path):
    words = []
    with open(path) as f:
        line = f.readline().strip()
        if len(line) > 0:
            words.append(line)
    return words


def load_json_dictionary(path):
    with open(path) as f:
        words_dict = json.load(f)
    return words_dict


def closest_word(word, words_dict):
    """
    :return: return a list containing the closest word(s) and their distance to the original
    :rtype: (list(str), int)
    """
    if word in words_dict:
        return word, 0
    else:
        words = words_dict.keys()
        best_word = [[""], 100]
        for dword in words:
            distance = Levenshtein.distance(word, dword)
            if distance < best_word[1]:
                best_word = [[dword], distance]
            elif distance == best_word[1]:
                best_word[0].append(dword)
        return best_word[0][0], best_word[1]


def sentence_dictionary_confidence(sentence, dictionary, tolerance=0):
    words = sentence.split(" ")
    in_dictionary = 0
    for word in words:
        w, d = closest_word(word, dictionary)
        if d <= tolerance:
            in_dictionary += 1
    return in_dictionary/len(words)


def compile_distance_vector(sentence_list, dictionary):
    """
    :type sentence: list(str)
    :return: list with the distance of each word to a word in the dictionary
    """
    distance_vector = []
    for word in sentence_list:
        distance_vector.append(closest_word(word, dictionary)[1])

    return distance_vector


def find_sentence_from_string(original, dictionary):
    original = util.remove_punctuation2(original.lower())

    #original = divide_title(original, dictionary)
    original = merge_title(original, dictionary)

    original_list = original.split()
    original_list = [w for w in original_list if len(w) > 1]
    d_vector = compile_distance_vector(original_list, dictionary)
    consecutive_1s = 0
    candidates = []
    current_string = ""
    for i, distance in enumerate(d_vector):
        if distance > 1:
            if len(current_string) != 0 and i != len(d_vector) - 1 and d_vector[i+1] == 0:
                current_string += original_list[i] + " "
                consecutive_1s = 0
            else:
                candidates.append(current_string)
                current_string = ""
                consecutive_1s = 0
        elif distance == 0:
            current_string += original_list[i] + " "
            consecutive_1s = 0
        elif distance == 1:
            if consecutive_1s <= 1 and len(original_list[i]) > 3:
                consecutive_1s += 1
                current_string += original_list[i] + " "
            else:
                candidates.append(current_string)
                current_string = ""
                consecutive_1s = 0

    if len(current_string) > 0:
        candidates.append(current_string)
    candidates = [candidate for candidate in candidates if len(candidate.split())> 2]
    return candidates

def merge_title(original, dictionary):
    merged_title = ""
    words = original.split()
    i = 0
    while i < len(words):
        if i == len(words) - 1:
            merged_title += words[i]
            break
        current_word = words[i]
        next_word = words[i + 1]
        # Don't fix uppercase words, they are names
        if (current_word.isupper() and len(current_word) > 1) or (next_word.isupper() and len(next_word) > 1) \
                or len(current_word) + len(next_word) < 3:
            i += 1
            merged_title += current_word + " "
            continue
        current_word = current_word.lower()
        next_word = next_word.lower()
        merged_word = current_word + " " + next_word

        w, current_distance = closest_word(current_word, dictionary)
        w, next_distance = closest_word(next_word, dictionary)
        w, merged_distance = closest_word(merged_word, dictionary)
        if merged_distance < current_distance + next_distance + 1:
            if merged_distance < 2:
                merged_title += w + " "
            else:
                merged_title += current_word + next_word + " "
            i += 2
        else:
            merged_title += current_word + " "
            i += 1
    return merged_title


def divide_title(original, dictionary):
    original_words = original.split()
    split_title = ""
    for word in original_words:
        w, orig_d = closest_word(word, dictionary)
        # (split position, split distance)
        best_split = (0, 100)
        for c in range(1, len(word)):
            w1 = word[:c]
            w2 = word[c:]

            w, d1 = closest_word(w1, dictionary)
            w, d2 = closest_word(w2, dictionary)
            if d1+d2 < orig_d and d1+d2 < best_split[1] and (d1 == 0 or d2 == 0):
                best_split = (c, d1+d2)
        if best_split[0] == 0:
            split_title += word + " "
        else:
            split_title += word[:best_split[0]] + " " + word[best_split[0]:] + " "

    return split_title.strip()
