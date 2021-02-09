"""
This file contains functions used to extract data from the whole document or from single pages
pdfminer has to be used with -Y exact for these functions to work correctly
"""
import util
import re
import statistics
import bs4
import string
import pickle
import dictionary_analysis


def get_document_fontsize_stats(pages):
    """
    Get the minimum, maximum and average fontsize of all pages

    :param pages: list[bs4.BeautifulSoup]
    :return: (min,max,avg)
    :rtype: (float,float,float)
    """
    avg = []
    max_size = 0
    min_size = 100

    size_frequency_dict = {}

    for page in pages:
        for tag in page.children:
            if hasattr(tag, "style"):
                if tag.name == "span":
                    fsize = util.get_coordinate_from_style(tag['style'], "font-size")
                    if fsize is not None and fsize != 0:
                        if fsize in size_frequency_dict:
                            size_frequency_dict[fsize] += 1
                        else:
                            size_frequency_dict[fsize] = 1

                        avg.append(fsize)

    # For a fontsize to be relevant in the min-max it has to occur at least 1k times
    for key in sorted(size_frequency_dict):
        if size_frequency_dict[key] >= 1000:
            min_size = key
            break

    for key in sorted(size_frequency_dict, reverse=True):
        if size_frequency_dict[key] >= 1000:
            max_size = key
            break

    return min_size, max_size, statistics.mean(avg)


def split_pages(html, save=False):
    """
    Split the whole document into a list of single pages

    :param html: Raw BeautifulSoup
    :type html: bs4.BeautifulSoup
    :param save: whether to save the result to file
    :return: list of BeautifulSoup elements , each entry is a page
    """
    # The start of a page is defined by a div containing an a tag with the text Page <page number>
    all_page_divs = [a.parent for a in html.find_all("a", {"name": True})]

    page_list = []
    for i, single_div in enumerate(all_page_divs):
        page = str(single_div)
        # Find the first element that is at the start of the next page
        next_page_first_element = all_page_divs[i+1] if i+1 < len(all_page_divs) else None

        for tag in single_div.next_siblings:
            if tag == next_page_first_element:
                break
            else:
                page += str(tag)

        page_list.append(bs4.BeautifulSoup(page, features="html.parser"))

    if save is True:
        savepath = "tempPages"
        string_pages = []
        for page in page_list:
            string_pages.append(str(page))
        with open(savepath, "wb") as f:
            pickle.dump(string_pages, f)
    return page_list


def extract_lines_from_page(page, remove_dot=True, raw=False, page_number=True, line_tolerance = 0):
    """
    Get all the lines from a page

    :type page: bs4.BeautifulSoup
    :param remove_dot: whether to remove dots from the page or not
    :return: list of lines in the page
    :rtype: list[str]
    """
    to_remove = string.punctuation
    if remove_dot is False:
        to_remove = to_remove.replace('.', '')

    lines = ""
    last_top = 0

    for tag in page.children:
        if tag.name == "span" or tag.name == "div":
            tag_top = util.get_coordinate_from_style(str(tag), "top")
            tag_size = util.get_coordinate_from_style(str(tag), "font-size")
            if tag_size == None:
                tag_size = 0

            # If the top coordinate of the tag is the same as the last one put them on the same line
            if tag_top <= last_top + line_tolerance*tag_size:
                if tag_top != last_top:
                    lines += " "
                lines += "".join(tag.strings)
            else:
                lines += "\n" + "".join(tag.strings)

            last_top = tag_top

    if raw is False:
        lines = lines.translate(str.maketrans(to_remove, ' '*len(to_remove))).encode("ascii", "ignore").decode()

    # Remove multiple newlines and spaces
    lines = re.sub(r'\n+', '\n', lines)
    lines = re.sub(r'  +', ' ', lines)

    lines = lines.split("\n")
    lines = [line.strip() for line in lines if not len(line.strip()) == 0]
    if raw is True or page_number is False:
        lines = lines[1:]
    return lines

def extract_lines_ycoord_from_page(page, remove_dot=True, raw=False, page_number=True, line_tolerance = 0):
    """
    Get all the lines and their y position from a page

    :type page: bs4.BeautifulSoup
    :param remove_dot: whether to remove dots from the page or not
    :return: list of lines in the page
    :rtype: list[tuple(str,int)]
    """
    to_remove = string.punctuation
    if remove_dot is False:
        to_remove = to_remove.replace('.', '')

    lines = []
    current_line = ""
    last_top = 0

    for tag in page.children:
        if tag.name == "span" or tag.name == "div":
            tag_top = util.get_coordinate_from_style(str(tag), "top")
            tag_size = util.get_coordinate_from_style(str(tag), "font-size")
            if tag_size == None:
                tag_size = 0

            # If the top coordinate of the tag is the same as the last one put them on the same line
            if tag_top <= last_top + line_tolerance*tag_size:
                if tag_top != last_top:
                    current_line += " "
                current_line += "".join(tag.strings)
            else:
                lines.append((current_line, last_top))
                current_line = "".join(tag.strings)

            last_top = tag_top
    if current_line != "":
        lines.append((current_line, last_top))
    if raw is False:
        lines = [(line[0].translate(str.maketrans(to_remove, ' '*len(to_remove))).encode("ascii", "ignore").decode(),line[1]) for line in lines]

    # Remove multiple  spaces
    lines = [(re.sub(r'  +', ' ', line[0]), line[1]) for line in lines]

    lines = [(line[0].strip(),line[1]) for line in lines if not len(line[0].strip()) == 0]
    if raw is True or page_number is False:
        lines = lines[1:]
    return lines


def extract_words_from_page(page):
    """
    Get all the words from a page

    :type page: bs4.BeautifulSoup
    :return: list of words in the page
    :rtype: list[str]
    """
    return extract_page_text(page).split(" ")


def extract_page_text(page):
    """
    Get page content
    :type page: bs4.BeautifulSoup
    :rtype: str
    """
    return " ".join(extract_lines_from_page(page))


def extract_words_from_page_vertical_region(page, next_page, region, min_fsize=-1, min_len=2):
    """
    Exctract words from the top portion of the page whose font size is big enough
    :type page: bs4.BeautifulSoup
    :type next_page: bs4.BeautifulSoup or None
    :param region: portion of the page to extract(between 0 and 1=all)
    :type region: float
    :param min_fsize: minimum font size of a word to be extracted
    :type min_fsize: float
    :param min_len: minimum lenght of a word to be extracted
    :type min_len: int
    :rtype: list[str]
    """
    # Find start of current page and next page
    page_top = util.get_coordinate_from_style(page.contents[0]['style'], 'top')
    default_page_size = 1000
    if next_page is None:
        # Last pages are badly formatted anyway, just take an approximation
        next_page_top = page_top + default_page_size
    else:
        next_page_top = util.get_coordinate_from_style(next_page.contents[0]['style'], 'top')

    current_line = ""
    last_top = 0
    words = []

    for tag in page.children:
        if hasattr(tag, "style"):
            if tag.name == "div" or tag.name == "span":

                # Check font size
                tag_fsize = util.get_coordinate_from_style(tag['style'], "font-size")
                if tag_fsize is None or tag_fsize >= min_fsize or tag_fsize == 0:

                    # Check position in page
                    tag_top = util.get_coordinate_from_style(tag['style'], 'top')
                    if tag_top is not None:
                        if tag_top < region*(next_page_top - page_top) + page_top:
                            if tag_top == last_top:
                                current_line += util.remove_punctuation("".join(tag.strings))
                            else:
                                # Remove multiple newlines and spaces
                                current_line = re.sub(r'\n+', ' ', current_line)
                                current_line = re.sub(r'  +', ' ', current_line)
                                single_words = current_line.split(" ")
                                single_words = [word for word in single_words if not len(word) < min_len]

                                if len(single_words) > 0:
                                    words += single_words
                                current_line = util.remove_punctuation("".join(tag.strings))
                            last_top = tag_top

    if len(current_line) > 0:
        current_line = re.sub(r'\n+', ' ', current_line)
        current_line = re.sub(r'  +', ' ', current_line)
        single_words = current_line.split(" ")
        single_words = [word for word in single_words if not len(word) < min_len]

        if len(single_words) > 0:
            words += single_words

    return words


def extract_words_fsize_from_page_vertical_region(page, next_page, region, min_fsize=-1, min_len=2):
    """
    Exctract words and their fontsize from the top portion of the page whose font size is big enough
    :type page: bs4.BeautifulSoup
    :type next_page: bs4.BeautifulSoup or None
    :param region: portion of the page to extract(between 0 and 1=all)
    :type region: float
    :param min_fsize: minimum font size of a word to be extracted
    :type min_fsize: float
    :param min_len: minimum lenght of a word to be extracted
    :type min_len: int
    :rtype: list[(str,int)]
    """
    # Find start of current page and next page
    page_top = util.get_coordinate_from_style(page.contents[0]['style'], 'top')
    default_page_size = 1000
    if next_page is None:
        # Last pages are badly formatted anyway, just take an approximation
        next_page_top = page_top + default_page_size
    else:
        next_page_top = util.get_coordinate_from_style(next_page.contents[0]['style'], 'top')

    current_line = ""
    words_fsize = []
    last_top = 0
    tag_fsize = min_fsize

    for tag in page.children:
        if hasattr(tag, "style"):
            if tag.name == "div" or tag.name == "span":

                # Check font size
                tag_fsize = util.get_coordinate_from_style(tag['style'], "font-size")
                if tag_fsize is None or tag_fsize == 0:
                    tag_fsize = min_fsize
                if tag_fsize >= min_fsize:

                    # Check position in page
                    tag_top = util.get_coordinate_from_style(tag['style'], 'top')
                    if tag_top is not None:
                        if tag_top < region*(next_page_top - page_top) + page_top:

                            if tag_top == last_top:
                                current_line += util.remove_punctuation("".join(tag.strings))
                            else:
                                # Remove multiple newlines and spaces
                                current_line = re.sub(r'\n+', ' ', current_line)
                                current_line = re.sub(r'  +', ' ', current_line)
                                single_words = current_line.split(" ")
                                single_words = [word for word in single_words if not len(word) < min_len]

                                if len(single_words) > 0:
                                    words_fsize += [(word, tag_fsize) for word in single_words]
                                current_line = util.remove_punctuation("".join(tag.strings))
                            last_top = tag_top

    if len(current_line) > 0:
        current_line = re.sub(r'\n+', ' ', current_line)
        current_line = re.sub(r'  +', ' ', current_line)
        single_words = current_line.split(" ")
        single_words = [word for word in single_words if not len(word) < min_len]

        if len(single_words) > 0:
            words_fsize += [(word, tag_fsize) for word in single_words]

    return words_fsize


def extract_words_fsize_line_from_page_vertical_region(page, next_page, region, min_fsize=-1, min_len=2):
    """
    Exctract words, their fontsize and the line in which they sit from the top portion of the page whose font size is
    big enough
    :type page: bs4.BeautifulSoup
    :type next_page: bs4.BeautifulSoup or None
    :param region: portion of the page to extract(between 0 and 1=all)
    :type region: float
    :param min_fsize: minimum font size of a word to be extracted
    :type min_fsize: float
    :param min_len: minimum lenght of a word to be extracted
    :type min_len: int
    :rtype: list[(str,int,int)]
    """
    # Find start of current page and next page
    page_top = util.get_coordinate_from_style(page.contents[0]['style'], 'top')
    default_page_size = 1000
    if next_page is None:
        # Last pages are badly formatted anyway, just take an approximation
        next_page_top = page_top + default_page_size
    else:
        next_page_top = util.get_coordinate_from_style(next_page.contents[0]['style'], 'top')

    current_line = ""
    words_fsize = []
    last_top = 0
    tag_fsize = min_fsize
    line_number = 0
    for tag in page.children:
        if hasattr(tag, "style"):
            if tag.name == "div" or tag.name == "span":

                # Check font size
                tag_fsize = util.get_coordinate_from_style(tag['style'], "font-size")
                if tag_fsize is None or tag_fsize == 0:
                    tag_fsize = min_fsize
                if tag_fsize >= min_fsize:
                    # Check position in page
                    tag_top = util.get_coordinate_from_style(tag['style'], 'top')
                    if tag_top is not None:
                        if tag_top < region*(next_page_top - page_top) + page_top:

                            if tag_top == last_top:
                                current_line += util.remove_punctuation("".join(tag.strings))
                            else:
                                # Remove multiple newlines and spaces
                                current_line = re.sub(r'\n+', ' ', current_line)
                                current_line = re.sub(r'  +', ' ', current_line)
                                single_words = current_line.split(" ")
                                single_words = [word for word in single_words if not len(word) < min_len]

                                if len(single_words) > 0:
                                    words_fsize += [(word, tag_fsize, line_number) for word in single_words]
                                line_number += 1
                                current_line = util.remove_punctuation("".join(tag.strings))
                            last_top = tag_top

    if len(current_line) > 0:
        current_line = re.sub(r'\n+', ' ', current_line)
        current_line = re.sub(r'  +', ' ', current_line)
        single_words = current_line.split(" ")
        single_words = [word for word in single_words if not len(word) < min_len]

        if len(single_words) > 0:
            words_fsize += [(word, tag_fsize, line_number) for word in single_words]

    return words_fsize


def count_pages_languages(pages_words, eng_dict, fr_dict):
    # Count how many words are english and french in each page
    # [(n_eng1,n_fr1), (n_eng2, n_fr2), ...]
    pages_languages = []
    for page_words in pages_words:
        # Find how many words are english and how many are french
        n_eng = 0
        n_fr = 0
        for word in page_words:
            eng_w, eng_d = dictionary_analysis.closest_word(word[0], eng_dict)
            fr_w, fr_d = dictionary_analysis.closest_word(word[0], fr_dict)
            if eng_d < fr_d:
                n_eng += 1
            elif fr_d < eng_d:
                n_fr += 1
            else:
                n_fr += 1
                n_eng += 1
        pages_languages.append((n_eng, n_fr))
    return pages_languages