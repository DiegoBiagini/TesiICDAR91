import bs4
import toc_process_exact
import pickle
import doc_process
import process_references
import dictionary_analysis
import matplotlib.pyplot as plt
import dblp_util
import json
import numpy as np
import toc_learning
import pandas as pd
import util

def main():
    html_path = "../dataset/conference_out_strip.html"
    html=None
    with open(html_path) as fp:
       html = bs4.BeautifulSoup(fp, features="html.parser")
    #toc_learning.create_training_dataset(html)
    toc_process_exact.predict_toc(html)
    return
    eng_dict = dictionary_analysis.load_json_dictionary("../dictionaries/english2.json")

    pages = [bs4.BeautifulSoup(page) for page in pickle.load(open("tempPages", "rb"))]

    print("Pages split")
    min_fsize, max_fsize, avg_fsize = doc_process.get_document_fontsize_stats(pages)

    pages_words = []
    # Take only the upper part of the pages and text with bigger than avg fsize( and record  the fsize and line)
    for n, page in enumerate(pages):
        if n != len(pages) - 1:
            pages_words.append([word[0].lower() for word in
                                doc_process.extract_words_fsize_line_from_page_vertical_region(page, pages[n + 1], 0.3,
                                                                                               avg_fsize - 1)])
        else:
            pages_words.append([word[0].lower() for word in
                                doc_process.extract_words_fsize_line_from_page_vertical_region(page, None, 0.3,
                                                                                               avg_fsize - 1)])
    print("Important information from pages extracted")

    #pages_and_titles = pickle.load(open("tempResults", "rb"))
    #title_pages = toc_process_exact.fix_titles(pages_and_titles, pages_words, eng_dict)
    #print("Titles fixed")
    correct = toc_process_exact.correctICPR1

    title_pages_correct = []
    for i in range(len(correct)):
        title_pages_correct.append(("", correct[i]))

    process_references.find_references(pages, title_pages_correct)

def remove_newlines():
    file_in = "../dataset/other_conferences/ICPR7.html"
    file_out = "../dataset/other_conferences/ICPR7_strip.html"

    with open(file_in, 'r') as f:
        with open(file_out, "w") as f_out:
            for line in f:
                f_out.write(line.strip('\n'))

def to_lowercase(filename):
    f = open(filename, 'r')
    text = f.read()

    lines = ['"' + line +'":1,\n' for line in text.split("\n")]
    with open(filename.replace("txt","json"), 'w') as out:
        out.writelines(lines)

def piechart():
    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    labels = 'Parentesi quadre', 'Elenco numerato', 'Abbreviazione autore'
    sizes = [57, 27, 8]

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%',shadow=False, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.show()

def barchart():
    plt.rcdefaults()
    fig, ax = plt.subplots()

    labels = 'Totali', 'Riconosciuti\n dall\'OCR', 'Con marcatore\n individuati', \
             "Con titoli in inglese \n e leggibili", "Con titolo \n trovato in DBLP", "Estratti \n con successo"
    sizes = [132, 131, 93, 85, 32, 22]
    y_pos = [0, 1, 2, 3, 4, 5]
    plt.title('Suddivisione dei riferimenti', fontsize=20)
    ax.barh(y_pos, sizes, align='center')
    for i, v in enumerate(sizes):
        ax.text(v + 3, i + .25, v, color='blue', fontweight='bold')
    ax.set_yticks(y_pos)
    ax.invert_yaxis()
    ax.set_yticklabels(labels, fontsize=15)
    plt.show()

def print_goodenough_list(path):
    with open(path, "rb") as f:
        goodenough_list = pickle.load(f)
        for el in goodenough_list:
            print(el)

def vbarchart():
    labels = ['Conferenza 1', 'Conferenza 2', "Conferenza 3"]
    greater_than02 = [435, 310,663]
    corrects = [207, 59,85]

    x = np.array([0,1,2])  # the label locations
    width = 0.1  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width, greater_than02, width, label='Con score > 0.2')
    rects2 = ax.bar(x, corrects, width, label='Correttamente identificati')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_title('Riferimenti trovati')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()
    plt.show()

def check_results():
    results = [259, 36, 42, 53, 68, 93, 118, 1094, 148, 162, 169, 177, 209, 173, 237, 240, 292, 253, 376, 261, 272, 281, 285, 288, 293, 299, 303, 307, 51, 315, 319, 42, 331, 337, 340, 346, 349, 352, 355, 358, 36, 364, 369, 374, 381, 382, 387, 1157, 397, 402, 407, 410, 148, 414, 417, 421, 425, 428, 428, 431, 437, 440, 440, 449, 346, 461, 464, 468, 472, 475, 480, 487, 495, 498, 503, 506, 511, 517, 520, 528, 532, 535, 541, 544, 548, 553, 556, 561, 564, 568, 572, 576, 579, 68, 583, 588, 204, 596, 596, 602, 607, 615, 620, 626, 631, 636, 639, 643, 123, 653, 658, 661, 665, 668, 162, 672, 677, 680, 689, 694, 695, 698, 704, 704, 714, 719, 724, 724, 730, 733, 738, 93, 209, 748, 749, 749, 758, 763, 766, 773, 773, 777, 777, 787, 790, 109, 796, 799, 53, 808, 811, 811, 814, 1186, 822, 829, 832, 835, 838, 841, 841, 851, 854, 862, 862, 868, 871, 876, 879, 882, 169, 887, 889, 897, 900, 908, 911, 914, 919, 922, 927, 932, 936, 944, 944, 950, 177, 956, 963, 961, 968, 971, 977, 980, 980, 986, 991, 991, 1000, 1005, 1099, 1015, 1020, 1064, 1031, 1031, 1034, 1039, 1044, 1050, 1055, 1055, 1064, 1064, 1034, 1075, 1078, 1081, 1084, 1084, 1089, 1094, 406, 1101, 1107, 1112, 1115, 1121, 1125, 1130, 178, 1136, 1144, 1150, 1155, 1161, 1160, 1162, 1165, 1165, 1169]

    print(results)
    print(len(results))
    print(toc_process_exact.correctICPR4)
    print(len(toc_process_exact.correctICPR4))
    corrects = []
    wrongs = []
    i = 0
    train = 0
    ntrain = 0
    test = 0
    correct_train = 0
    correct_test = 0
    for x, y in zip(toc_process_exact.correctICPR4, results):
        if x < 1:
            i += 1
            continue
        if x != y:
            print(x, y, "Wrong")
            if i < ntrain:
                train += 1
            else:
                test += 1
        else:
            print(x, y, "Correct")
            if i < ntrain:
                train += 1
                correct_train += 1
            else:
                test += 1
                correct_test += 1
        i += 1

    if len(corrects) > 0:
        print("Corrects:", len(corrects))
    if len(wrongs) > 0:
        print("Wrongs:", len(wrongs))
    print("Test: Found " + str(test) + ", Correct " + str(correct_test) + ", Accuracy :" + str(correct_test / test))

def plot_dblp_by_year():
    dblp_count = {2018: 358119, 1994: 43451, 1993: 39307, 1991: 29822, 1989: 22092, 1995: 45876, 1990: 26609, 1988: 19156,
                  1979: 6297, 1992: 33816, 1987: 16456, 1981: 8092, 1986: 15303, 1999: 67533, 1980: 7338, 1973: 3845,
                  1978: 6076, 1974: 4412, 1975: 4629, 1998: 60892, 1996: 49866, 2001: 81425, 2000: 76637, 1997: 54734,
                  2002: 92540, 2003: 108680, 2004: 130948, 2006: 170437, 2012: 258319, 1971: 2663, 1972: 3328, 2011: 245212,
                  1969: 1939, 2019: 390874, 2008: 199291, 2010: 224197, 2007: 186926, 2015: 295104, 2013: 275159,
                  2014: 285286, 2016: 305117, 2009: 218812, 2017: 326871, 2005: 152921, 1985: 12915, 1976: 5111,
                  1983: 10295, 1977: 5521, 1984: 11791, 1982: 9285, 1970: 2015, 1960: 491, 1967: 1589, 1962: 1030, 1964: 906,
                  1965: 1082, 1961: 721, 1966: 1276, 1968: 2044, 1963: 916, 1941: 13, 1939: 18, 1943: 8, 1936: 12, 1942: 13,
                  1940: 10, 1956: 228, 1938: 11, 1944: 5, 1948: 41, 1958: 313, 1949: 52, 1952: 34, 1951: 21, 1946: 31, 1950: 26,
                  1953: 114, 1955: 159, 1959: 531, 1954: 169, 1947: 10, 1937: 15, 1945: 9, 1957: 249}
    dblp_count_pre2000 = { year: dblp_count[year] for year in dblp_count.keys() if year <= 2000 and year >= 1950}
    years = sorted(dblp_count_pre2000.keys())
    min_year = years[0]
    max_year = years[-1]
    npubs = [dblp_count_pre2000[year] for year in years]
    print(npubs)
    total_pubs = []
    for i,year in enumerate(years):
        articles = 0
        for j in range(0,i+1):
            articles += dblp_count_pre2000[years[j]]
        total_pubs.append(articles)

    fig, ax = plt.subplots()
    ax.bar(years, total_pubs)
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_title('Numero di articoli presenti in DBLP per anno')
    ax.set_xticks([y for y in years if y == min_year or y == max_year or y%10 == 0])
    ax.legend()

    fig.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
    #print_goodenough_list("goodenoughTemp")

