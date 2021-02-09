"""
This file contains functions used to learn features used to estimate whether a page is the one a candidate title belongs
to
"""
import pandas as pd

from sklearn import preprocessing
import sklearn
from operator import itemgetter
import random
import toc_process_exact
from doc_process import *
from sklearn import linear_model
from sklearn import naive_bayes
from sklearn import neural_network
from sklearn import ensemble
import regex
import doc_process

def compile_single_dataframe(candidate_title, page_words, n_eng, n_fr, columns=None):
    """
    Extract parameters to learn on in a single page
    :type candidate_title: str
    :type page: list[(str,int,int)]
    :rtype:pd.Dataframe
    """
    entry_words = [word.lower() for word in candidate_title.split(" ") if len(word) > 2]

    #(word_position, word_score, (actual_word, actual_word_fsize, line_number))
    best_words = []
    already_checked_words = []

    for entry_word in entry_words:
        entry_word_scores = []

        for n, page_word in enumerate(page_words):
            if page_word not in already_checked_words:
                entry_word_scores.append((n, util.ngram_scoring(entry_word, page_word[0], 3), page_word))

        # Find the word with the best score
        if len(entry_word_scores) == 0:
            best_words.append((-1, 0, ("", 0, -100)))
        else:
            best_page_word_score = max(entry_word_scores, key=itemgetter(1))
            best_words.append(best_page_word_score)
            already_checked_words.append(best_page_word_score[2])

    # Find average distance between subsequent best scoring words in the page
    xdistances = []
    ydistances = []
    for i, score_pos in enumerate(best_words):
        if i != len(best_words) - 1:
            xdistance = abs(best_words[i][0] - best_words[i + 1][0])
            ydistance = abs(best_words[i][2][2] - best_words[i + 1][2][2])

            xdistances.append(xdistance)
            ydistances.append(ydistance)

    df = pd.DataFrame({
        "page_length": pd.Series(len(page_words)),
        "n_english": pd.Series(n_eng),
        "n_french": pd.Series(n_fr),
        "page_score": pd.Series(statistics.mean([word[1] for word in best_words])),
        "avg_fsize": pd.Series(statistics.mean([word[2][1] for word in best_words])),
        "avg_xdistance": pd.Series(statistics.mean(xdistances)),
        "avg_ydistance": pd.Series(statistics.mean(ydistances))
    })
    if columns is not None:
        df = df[columns]
    return df


def compile_training_dataset(entries, pages_words, correct_pages, starting_page, pages_languages):
    columns = ["page_length", "n_english", "n_french", "page_score", "avg_fsize", "avg_xdistance", "avg_ydistance"]
    X = pd.DataFrame(columns=columns)
    y_list = []
    c = 0
    for i,entry in enumerate(entries):
        if correct_pages[i] == 0:
            continue
        else:
            c += 1
        for candidate_title in entry:

            title_words = [word.lower() for word in candidate_title.split(" ") if len(word) > 2]
            # Don't consider candidate titles that are too short
            if len(title_words) < 3:
                continue

            # Add the correct page
            X = X.append(compile_single_dataframe(candidate_title, pages_words[correct_pages[i]],
                                                  None, None))
            y_list.append(1)

            # Add 200 other random pages
            possible_pages = list(range(starting_page-1, len(pages_words)))
            possible_pages.remove(correct_pages[i])
            for page in random.sample(possible_pages, 200):
                X = X.append(compile_single_dataframe(candidate_title, pages_words[page],
                                                      None, None))
                y_list.append(0)
    print(c)
    y = pd.Series(y_list)
    return X, y


def create_training_dataset(html):

    toc_pages = [6,7,8,9]
    print("Table of contents pages found:", toc_pages)

    pages = doc_process.split_pages(html, save=True)

    print("Pages split")

    min_fsize, max_fsize, avg_fsize = get_document_fontsize_stats(pages)
    print(f"Document font size information: \n min fontsize:{min_fsize} \n max fontsize:{max_fsize} \n "
          f"average fontsize: {avg_fsize}\n")

    # Get all text lines from table of contents
    toc_lines = []
    for page_index in toc_pages:
        toc_lines += extract_lines_from_page(pages[page_index], remove_dot=False, page_number=False)

    #ordered_lines = sorted(toc_lines, key=lambda tup:tup[1])
    #toc_lines = [line[0] for line in ordered_lines]

    # Find the link pages(lps), in which line they sit and in which position in the line
    lps = []
    for i, line in enumerate(toc_lines):
        #found = regex.search(r"(p\.\d+){1i+2d+2s<=2}", line)
        found = regex.search(r"(\d+){i<=2}", line)
        # Must be on last characters of line
        if found is not None and found.span()[1] > len(line) - 3:
            lps.append((i, found.group(), found.span()))

    # Find the candidate link titles
    candidate_titles = toc_process_exact.find_candidate_titles_2(lps, toc_lines)

    print("Candidate titles found")
    print(candidate_titles, "\n")

    pages_words = []

    # Take only the upper part of the pages and text with bigger than avg fsize( and record  the fsize and line)
    for n, page in enumerate(pages):
        if n != len(pages) - 1:
            pages_words.append([(word[0].lower(), word[1], word[2]) for word in
                                extract_words_fsize_line_from_page_vertical_region(page, pages[n + 1], 0.3,
                                                                                   avg_fsize - 1)])
        else:
            pages_words.append([(word[0].lower(), word[1], word[2]) for word in
                                extract_words_fsize_line_from_page_vertical_region(page, None, 0.3, avg_fsize - 1)])

    print("Important information from pages extracted")
    print("Analyzed languages stats,  start compiling training dataset")

    correct = toc_process_exact.correctICPR1

    X, y = compile_training_dataset(candidate_titles[:43], pages_words, correct[:43], toc_pages[-1] + 1, None)
    X.to_pickle("dataset_X_73")
    y.to_pickle("dataset_y_73")
    print(X)
    print(y)


def train_tree(columns=None):
    X = pd.read_pickle("dataset_X_73_2")
    y = pd.read_pickle("dataset_y_73_2")
    if columns is not None:
        X = X[columns]

    scaler = preprocessing.MinMaxScaler()
    X = scaler.fit_transform(X)
    #clf = linear_model.LogisticRegression()
    #clf = sklearn.svm.SVC(kernel="linear", probability=True)
    #clf = sklearn.svm.SVC(probability=True)
    #clf = ensemble.BaggingClassifier(n_estimators=100)
    #clf = ensemble.AdaBoostClassifier()
    #clf = ensemble.RandomForestClassifier(max_depth=5)
    #clf = naive_bayes.GaussianNB()
    clf = sklearn.naive_bayes.MultinomialNB()
    #clf = sklearn.naive_bayes.ComplementNB()
    #clf = neural_network.MLPClassifier(hidden_layer_sizes=(5,))
    print("MultinomialNB")

    clf.fit(X, y)
    return clf, scaler


