"""
This file contains functions used to find and elaborate the references found in articles
"""
import bs4
import doc_process
import Levenshtein
import regex
import dictionary_analysis
import util
import json
import dblp_util
import pickle

def find_references(pages, articles):
    """
    :type pages: list[bs4.BeautifulSoup]
    :parameter articles: list of tuples, each tuple contains the name and starting page of the article
    :type articles: list[tuple[str,int]]
    :return:
    """

    # Sort the articles by page
    articles.sort(key=lambda tup: tup[1])
    print(articles)

    references_lines = []
    for i, article in enumerate(articles):
        if i != len(articles) - 1:
            ref_lines = find_reference_section_lines(pages, article[1], articles[i+1][1] - 1)
        else:
            ref_lines = find_reference_section_lines(pages, article[1], len(pages) - 1)
        if len(ref_lines) > 0:
            references_lines.append(ref_lines)
    print("Reference sections found:" + str(len(references_lines)))

    # Find single references
    max_lines_for_reference = 8
    #Counters
    total_ref = 0
    regart1 = 0
    regart2 = 0
    regart3 = 0

    reference_texts = []
    current_ref = []
    article_references = []

    for i, lines_of_article in enumerate(references_lines):
        reg1 = 0
        reg2 = 0
        reg3 = 0

        article_references = []
        for i, line in enumerate(lines_of_article):
            # For the [1],(1) types
            found = regex.search(r"(\[(\d{1,2})\]){d<=1,i<=2}", line)
            if found is not None and found.span()[0] < 5:
                if len(current_ref) != 0:
                    article_references.append("".join(current_ref))
                    total_ref += 1
                    reg1 += 1
                current_ref = [line]
            else:
                # For 1.
                found = regex.search(r"(\d{1,2}\.){i<=2}", line)
                if found is not None and found.span()[0] < 5:
                    if len(current_ref) != 0:
                        article_references.append("".join(current_ref))
                        total_ref += 1
                        reg2 += 1
                    current_ref = [line]
                else:
                    # For [Auth1]
                    found = regex.search(r"(\[(.{,15})\]){d<=1,i<=1}", line)
                    if found is not None and found.span()[0] < 5:
                        if len(current_ref) != 0:
                            article_references.append("".join(current_ref))
                            total_ref += 1
                            reg3 += 1
                        current_ref = [line]
                    else:
                        if len(current_ref) < max_lines_for_reference:
                            current_ref += line

        if reg1 >= reg2 and reg1 >= reg3:
            regart1 += 1
        elif reg2 >= reg1 and reg2 >= reg3:
            regart2 += 1
        else:
            regart3 += 1
        if i != len(references_lines)-1:
            reference_texts.append((lines_of_article, article_references))
    if len(current_ref) != 0:
        article_references.append("".join(current_ref))
        reference_texts.append((references_lines[-1], article_references))

    print(str(total_ref) + "references found total")
    print(str(regart1) + " for first regexp")
    print(str(regart2) + " for second regexp")
    print(str(regart3) + " for third regexp")

    with open("dblp1991.json") as fp:
        dblp = json.load(fp)
    dblp_hashed = dblp_util.dblp_to_hashedlist(dblp)
    print("Size of dblp " + str(len(dblp_hashed)))
    print("Loaded dblp")
    eng_dict = dictionary_analysis.load_json_dictionary("../dictionaries/english2.json")

    goodenough_list = []
    goodenough02 = 0
    goodenough03 = 0
    goodenough04 = 0
    goodenough05 = 0
    goodenough06 = 0

    for art_text_ref in reference_texts:
        for line in art_text_ref[0]:
            print(line)
        print(art_text_ref[1])
        for single_ref in art_text_ref[1]:
            result = find_reference_dblp(single_ref, dblp_hashed, eng_dict)
            if result[0] != "":
                print(result)
                found_title = title_from_key_dblp(result[0], dblp)
                print(found_title)
                if result[1] >= 0.2:
                    goodenough02 += 1
                    #goodenough_list.append((single_ref, found_title))
                if result[1] >= 0.3:
                    goodenough03 += 1
                if result[1] >= 0.4:
                    goodenough04 += 1
                if result[1] >= 0.5:
                    goodenough05 += 1
                if result[1] >= 0.6:
                    goodenough06 += 1
            print("-"*10)
        print("-"*30)

    print(str(goodenough02) + " with score better than 0.2")
    print(str(goodenough03) + " with score better than 0.3")
    print(str(goodenough04) + " with score better than 0.4")
    print(str(goodenough05) + " with score better than 0.5")
    print(str(goodenough06) + " with score better than 0.6")

    with open("goodenoughTemp", "wb") as f:
        pickle.dump(goodenough_list, f)

    correct_ref = manual_check_reference(goodenough_list)
    print("Found " + str(len(correct_ref)) + " correct references")
    for el in correct_ref:
        print(el)

    with open("correct_ref", "wb") as f:
        pickle.dump(correct_ref, f)

def find_reference_section_lines(pages, starting_page, end_page):
    # Extract all lines contained in article
    lines_whole_article = []
    for i in range(starting_page, end_page):
        lines_whole_article += doc_process.extract_lines_from_page(pages[i], raw=True)

    # Find a line containing "References" or "Bibliography"
    starting_ref_line = -1
    for i, line in enumerate(lines_whole_article):
        if Levenshtein.distance(line.lower(), "references") <= 5  or \
                Levenshtein.distance(line.lower(), "bibliography") <= 5:
            starting_ref_line = i
            break

    if starting_ref_line == -1:
        return []
    else:
        if len(lines_whole_article[starting_ref_line + 1:]) > 1000:
            return lines_whole_article[starting_ref_line + 1: starting_ref_line + 1000 +1]
        else:
            return lines_whole_article[starting_ref_line + 1:]

def manual_check_reference(references_titles_tup):
    correct_ref = []
    for tup in references_titles_tup:
        print(str(tup))
        res = input("Ok?[y/n]")
        if res == 'y':
            correct_ref.append(tup)
    return correct_ref


def find_reference_dblp(single_reference, dblp_hashed, eng_dict):
    """
    :return: (key, score, reference text)
    """
    print(single_reference)
    results = dictionary_analysis.find_sentence_from_string(single_reference, eng_dict)
    new_results = []
    for title in results:
        words = title.split()
        new_title = ""
        for word in words:
            w, d = dictionary_analysis.closest_word(word, eng_dict)
            if d < 2:
                new_title += w + " "
            else:
                new_title += word + " "
        new_results.append(new_title.strip())

    best_in_dblp = ("", 0, "")
    for result in new_results:
        # Find the entry in dblp that shares the highest number of bigramwords
        hashed_bigram_title = dblp_util.hashed_biwordgram_from_title(result)
        for art_key in dblp_hashed.keys():
            score = dblp_util.bigramword_score(hashed_bigram_title, dblp_hashed[art_key])
            if score > best_in_dblp[1]:
                best_in_dblp = (art_key, score, result)
    return best_in_dblp

def title_from_key_dblp(key, dblp):
    found_title = ""
    for art_type in dblp["dblp"]:
        for article in dblp["dblp"][art_type]:
            if article["@key"] == key:
                found_title = article["title"]
                if not isinstance(found_title, str):
                    found_title = found_title["#text"]
                break
    return found_title