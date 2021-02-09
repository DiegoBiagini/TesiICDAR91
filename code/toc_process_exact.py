import bs4
import regex

from operator import itemgetter
from doc_process import *
import dictionary_analysis
import toc_learning
import doc_process

correct = [18, 101, 31, 46, 55, 992, 74, 112, 123, 132, 141, 151, 162, 83, 171, 92, 180, 190, 201, 210, 219, 228, 238,
               249, 258, 267, 279, 289, 300, 308, 317, 327, 336, 345, 354, 364, 376, 385, 393, 402, 418, 427, 436, 445,
               509, 518, 527, 535, 544, 553, 561, 455, 570, 464, 473, 578, 587, 596, 482, 605, 491, 500, 613, 622, 631,
               640, 649, 658, 667, 676, 685, 694, 703, 712, 721, 731, 740, 749, 758, 767, 774, 784, 793, 802, 811, 820,
               828, 837, 849, 859, 890, 900, 911, 920, 929, 939, 948, 957, 967, 976, 985]

correctICPR1=[0, 14, 29, 33, 36, 44, 52, 61, 68, 70, 78, 88, 99, 100, 124, 130, 136, 149, 0, 150, 160, 170, 177, 178, 247, 180, 255, 256, 190, 198, 208,
              216, 231, 238, 258, 259, 0, 265, 266, 274, 285, 286, 297, 304, 242, 246, 313, 314, 318, 319, 329, 338, 339, 345, 351, 352, 353, 354,
              367, 385, 386, 400, 401, 407, 417, 418, 424, 427, 434, 444, 445, 456, 464, 473, 474, 475, 496, 503, 505, 537, 545, 546, 547, 561, 552,
              506, 508, 510, 515, 516, 525]

correctICPR2=[59, 0, 38, 429, 384, 26, 323, 374, 481, 0, 547, 0, 492, 22, 335, 0, 571, 392, 544, 345, 0, -1, 34, -1, 171, 300, 168, 0, 0, 152, 147, 551,
              333, 307, 0, 310, 312, 319, 464, 64, 81, 0, 533, 0, 31, 76, 400, 326, 0, 388, 142, 159, 0, 382, 357, 556, 0, 398, 265, 267, 0, 372, 269,
              450, 51, 72, 68, 19, 43, 0, 57, 0, 578, 87, 527, 134, 0, -139, 0, 0, 284, 270, -1, 211, 560, 218, 0, 417, 410, 321, 222, 432, 249, 125, 94,
              0, 118, 0, 102, 104, 106, 317, 0, 173, 178, 185, 558, 512, 190, 231, 0, 239, 0, 0, 242, 425, 254, 257, 226, 0, 437, 111, 0, 340, 280, 0,
              352, 292, 201, 196, 17, 206, -1, 0, 380, 487, -1, 529, 505, -1, 495, 565]

correctICPR4 = [0, 0, 42, 53, 68, 93, 118, 1094, 148, 162, 169, 177, 745, 0, 237, 240, 247, 253, 256, 261, 272,
281, 285, 288, 293, 299, 303, 307, 0, 315, 319, 324, 331, 337, 340, 346, 349, 352, 355, 358, 363, 364,
369, 374, 377, 382, 387, 0, 397, 402, 407, 410, 148, 414, 417, 421, 425, 428, 428, 431, 437, 440, 0,
 449, 455, 461, 464, 468, 472, 475, 480, 487, 495, 498, 503, 506, 511, 517, 520, 525, 532, 535, 541, 544,
 548, 553, 556, 561, 564, 568, 572, 576, 0, 582, 583, 588, 204, 596, 0, 602, 607, 615, 620, 626, 631,
 636, 639, 643, 118, 653, 658, 661, 665, 668, 162, 672, 677, 680, 689, 692, 695, 698, 704, 0, 714, 719,
 724, 0, 730, 733, 738, 93, 209, 746, 749, 754, 758, 763, 766, 773, 0, 777, 0, 787, 790, 109, 796,
 799, 53, 808, 811, 0, 814, 819, 822, 829, 832, 835, 838, 841, 0, 851, 854, 862, 867, 868, 871, 876,
 879, 882, 169, 887, 889, 897, 900, 908, 911, 914, 0, 922, 927, 932, 936, 944, 0, 950, 177, 956, 0,
 961, 968, 971, 977, 980, 0, 986, 991, 0, 1000, 1005, 0, 1015, 1020, 1025, 1031, 0, 1034, 1039,
 1044, 1050, 1055, 1058, 1064, 0, 1069, 1072, 1078, 1081, 0, 1084, 1089, 1094, 1097, 1101, 1107, 1112,
 1115, 1121, 1125, 1130, 178, 1141, 1144, 1150, 1155, 0, 1160, 1162, 0, 1165, 0]

correctICPR5 = [26, 38, 41, 45, 49, 53, 57, 60, 65, 68, 71, 74, 78, 82, 86, 90, 93, 98, 103, 112, 118, 122, 125, 134,
    138, 138, 146, 151, 154, 0, 161, 164, 167, 170, 176, 180, 0, 187, 197, 0, 207, 210,
    219, 228, 234, 239, 243, 249, 257, 263, 266, 270, 273, 276, 285, 289, 294, 298, 306, 310, 314,
    320, 324, 329, 333, 342, 345, 350, 354, 357, 361, 364, 367, 372, 376, 382, 385, 394, 0, 398, 407, 410,
    417, 420, 427, 433, 443, 0, 447, 453, 456, 459, 462, 465, 468, 482, 0, 486, 492, 497, 500, 510, 514,
    518, 530, 0, 537, 541, 545, 548, 554, 0, 559, 567, 570, 577, 584, 0, 588, 600, 603, 610,
    614, 628, 631, 636, 642, 650, 655, 664, 671, 677, 683, 688, 691, 694, 697, 702, 709, 720, 725, 729,
    732, 740, 743, 746, 0, 767, 0, 770, 775, 784, 0, 792, 796, 799, 802, 805, 808, 811, 817, 827,
    830, 837, 0, 843, 846, 850, 856, 862, 867, 870, 875, 0, 881, 886, 893, 900, 903, 0, 911, 0,
    914, 922, 925, 0, 938, 0, 943, 946, 950, 956, 961, 974, 978, 0, 984, 988, 994, 1000, 0, 1003,
    1007, 1010, 1013, 1021, 0, 1027, 1030, 1034, 1040, 1043, 1051, 1055, 1060, 0, 1074, 1085, 1091,
    1095, 1101, 1104, 1110, 1113, 1116, 1121, 1129, 0, 1132, 1138, 1146, 0, 1152, 1156, 1160, 1163,
    1168, 1171, 1175, 1178, 1181, 1190, 0, 0, 1198, 1201, 1205, 1211, 0, 1218, 0, 1225, 1229,
    1233, 1238, 1244, 1247, 1251, 1254, 1259, 1263, 1270, 1274, 1283, 1285, 0, 1296, 1303, 1308, 1311,
    1315, 1321, 1324, 1327, 1331, 1355, 1358, 1361, 1367, 1370, 1373, 1378, 1382, 1387]

correctICPR6 = [0, 34, 37, 46, 49, 53, 58, 61, 64, 67, 70, 74, 78, 81, 84, 87, 0, 97, 100, 104, 108, 112, 119, 123, 127, 131, 134, 138, 143, 158, 160, 163, 168, 171, 174, 178, 181, 189, 196, 0, 199, 202,
	0, 209, 211, 215, 219, 0, 241, 0, 247, 251, 0, 253, 259, 262, 265, 272, 276, 280, 284, 0, 296, 299, 302, 307, 311, 314, 318, 323, 326, 330, 334, 337, 340, 344, 351, 354, 358, 362, 366, 371, 374,
	 377, 380, 383, 391, 403, 407, 411, 415, 418, 422, 425, 428, 437, 443, 446, 450, 454, 458, 462, 466, 470, 473, 479, 482, 486, 489, 493, 502, 506,509, 512, 516, 522, 537, 540, 543, 548, 551, 555, 558, 562,
	 565, 569, 573, 576, 580, 583, 0, 589, 601, 604, 608, 0, 613, 616, 620, 623, 626, 629, 0, 637, 0,644, 647, 0, 651, 656, 659, 663, 0, 672, 688, 692, 696, 701, 709, 0, 716, 723, 727, 730, 734,
	 737, 749, 756, 759, 762, 765, 770, 773, 776, 780, 784, 791, 795, 798, 801, 804, 808, 813, 0, 817, 0,  824, 830, 833, 0, 843, 849, 853, 856, 859, 866, 0, 874, 877, 880, 888, 891, 0, 0, 909, 913,
	 921, 923, 926, 929, 932, 936, 943, 952, 955, 958, 962, 976, 979, 984, 987, 991, 995, 998, 1001, 1005, 1016, 1020, 0, 1031, 1035, 1039, 1054, 1057, 1061, 1064, 1067, 1071, 1075, 1078, 1081, 1085, 1088, 1095,
	 1098, 1101, 1103, 1106, 1112, 1115, 1122, 1125, 1133, 1135, 1138, 1141, 1145, 1148, 1152, 1156, 1174, 1177,1180, 1184, 1185, 1186, 1187, 1188, 1189, 1190, 1191, 1192, 1193, 1194, 1195, 1197, 1196, 1198,
	 1199, 1199, 1200, 0, 1202, 1203, 1204, 1205, 1208, 0, 1209, 1210, 1211, 1212, 1214, 0, 1215,1216, 1217, 1219, 0, 1220, 1222, 1223, 1224, 1225, 1226, 1227, 1228, 1229, 1230]

correctICPR7 = [0, 46, 49, 53, 56, 56, 64, 73, 77, 81, 85, 88, 91, 0, 102, 105, 108, 111, 0, 118, 121, 125, 128, 131, 0, 139, 142, 150, 0, 153, 0, 161, 165, 168, 175, 187, 195, 199, 204, 212, 0, 231, 234, 242, 0, 0,
	251,255, 259, 262, 265, 270, 277, 280, 280, 284, 293, 297, 300, 303, 303, 309, 0, 313, 317, 323, 0, 330, 335, 336, 340, 343, 346, 349, 354, 358, 362, 365, 368, 371, 376, 379, 382, 387, 390,
	393, 397, 405, 408, 0, 416, 420,  0, 425, 429, 432, 435, 438, 447, 0, 451, 459, 0, 463, 0, 471, 474, 481, 485, 494, 497, 500,  504, 507, 511, 515, 522, 526, 535, 541, 544, 547, 550, 555, 559, 563, 0, 567, 571, 0,
	 579, 582, 585, 588, 591, 595, 607, 607, 610, 0, 619, 626, 630, 633, 644, 648, 655, 0, 659, 664, 667, 671, 0, 674, 675, 679, 682, 0, 0, 702, 709, 715, 0, 719, 726, 729, 732, 736, 741, 744,
	 750, 757, 0, 765, 768, 775, 778, 792, 796, 0, 807, 0, 810, 817, 0, 832, 839, 842, 846, 849, 853, 861, 864, 865, 868, 871, 874, 877, 880, 881, 883, 884, 887, 890, 896, 899, 902, 903, 0, 904, 907, 914, 915, 921, 921, 922, 926, 932,
	 935, 938, 941, 943, 944, 945, 948, 951, 954, 957, 960, 963, 966, 0, 972, 978, 981, 984, 987, 996, 0, 999, 1002, 1005, 1008, 1011, 1014, 1017,
	 0, 1037, 1043, 1049, 1051, 1054, 1057, 1060, 1063, 1067, 1070, 1073, 1081, 1084, 1088, 1092, 1097, 0,1100, 1104,
	 1116, 1121, 1127, 1131, 1134, 0, 1141, 1151, 1154, 1158, 1161, 1168, 1171, 1184, 1190, 1193, 0, 1197,1205, 1209, 1212, 1215, 1223, 1227, 1229, 1234, 1237, 1240, 1243, 1256, 1264, 1268, 1276, 0, 1283, 1286,
	 0, 1293, 1297,1307, 1311, 1325, 1329, 1333, 1336, 0, 1339, 1345, 1348, 1352, 1355, 1358, 1362, 1365,  1370, 1373, 1376, 1379, 1384, 1388, 1394, 1398]

def predict_toc(html):
    eng_dict = dictionary_analysis.load_json_dictionary("../dictionaries/english2.json")
    fr_dict = dictionary_analysis.load_json_dictionary("../dictionaries/francais.json")

    # columns = ["page_length", "n_english", "n_french", "page_score", "avg_fsize", "avg_xdistance", "avg_ydistance"]
    columns = ["page_length", "page_score", "avg_fsize", "avg_xdistance", "avg_ydistance"]

    pages = [bs4.BeautifulSoup(page) for page in pickle.load(open("tempPages", "rb"))]
    #pages = doc_process.split_pages(html, save=True)

    print("Pages split")
    toc_pages = find_toc_pages(pages)
    #toc_pages =[14,15,16,17,18,19,20,21,22,23,24,25,27,28,29,30,31,32,33]

    print("Table of contents pages found:", toc_pages)

    min_fsize, max_fsize, avg_fsize = get_document_fontsize_stats(pages)
    print(f"Document font size information: \n min fontsize:{min_fsize} \n max fontsize:{max_fsize} \n "
          f"average fontsize: {avg_fsize}\n")

    # Get all text lines from table of contents
    toc_lines = []
    for page_index in toc_pages:
        toc_lines += extract_lines_from_page(pages[page_index], remove_dot=False, page_number=False, line_tolerance=0)
    for line in toc_lines:
        print(line)
    #ordered_lines = sorted(toc_lines, key=lambda tup:tup[1])
    #toc_lines = [line[0] for line in ordered_lines]

    # Only for ICPR7
    """
    toc_lines_2 = []
    for i, line in enumerate(toc_lines):
        #found = regex.search(r"(p\.\d+){1i+2d+2s<=2}", line)
        found = regex.search(r"(\d+){i<=2}", line)
        # Must be on last characters of line
        if found is not None:
            toc_lines_2.append(line[:found.span()[0]] + found.group(0))
            toc_lines_2.append(line[found.span()[1]:])
        else:
            toc_lines_2.append(line)
    toc_lines = toc_lines_2
    """

    # Find the link pages(lps), in which line they sit and in which position in the line
    lps = []
    for i, line in enumerate(toc_lines):
        found = regex.search(r"(p\.\d+){1i+2d+2s<=2}", line)
        #found = regex.search(r"(\d+){i<=2}", line)
        # Must be on last characters of line
        if found is not None and found.span()[1] > len(line) - 3:
            lps.append((i, found.group(), found.span()))

    print("Article links found")
    print(lps, "\n")

    # Find the candidate link titles
    candidate_titles = find_candidate_titles(lps, toc_lines)
    print("Candidate titles found")
    print(candidate_titles)
    for title in candidate_titles:
        print(title)
    pages_words = []
    # Take only the upper part of the pages and text with bigger than avg fsize( and record  the fsize and line)
    for n, page in enumerate(pages):
        if n != len(pages) - 1:
            pages_words.append([(word[0].lower(), word[1], word[2]) for word in
                                extract_words_fsize_line_from_page_vertical_region(page, pages[n+1], 0.3, avg_fsize - 1)])
        else:
            pages_words.append([(word[0].lower(), word[1],word[2]) for word in
                                extract_words_fsize_line_from_page_vertical_region(page, None, 0.3, avg_fsize-1)])


    print("Important information from pages extracted")

    pages_languages = pickle.load(open("language_stats", "rb"))

    #print("Start compiling training dataset")

    clf, scaler = toc_learning.train_tree(columns)
    print("Model trained")
    chosen_page_and_prob = []
    # Iterate over the articles
    for entries in candidate_titles:

        # Dictionary of the form {page_number : (position_in_best_prob, probabilities, entry, info)}
        page_probabilities_frequencies = {}

        # Iterate over the candidate titles for each article
        for entry in entries:
            # List of tuples (page_number, page_prob)
            pages_prob = []

            # Don't consider words that are shorter than 2 characters
            entry_words = [word.lower() for word in entry.split(" ") if len(word) > 2]
            # Don't consider candidate titles that are too short
            if len(entry_words) < 3:
                continue

            # Start searching in pages after the toc
            for n, page_words in enumerate(pages_words[toc_pages[-1] + 1:]):
                x = toc_learning.compile_single_dataframe(entry, page_words,
                                                          None,
                                                          None, columns)
                #print(clf.predict_proba(scaler.transform(x)))
                prob_hit = clf.predict_proba(scaler.transform(x))[0][1]

                # Record (page_number, page_prob, info)
                pages_prob.append((int(page_words[1][0]), prob_hit, x))

            # Record each time a page is in the top 3
            pages_prob.sort(key=itemgetter(1), reverse=True)
            for n, prob in enumerate(pages_prob[:3]):
                if prob[0] not in page_probabilities_frequencies:
                    page_probabilities_frequencies[prob[0]] = []
                page_probabilities_frequencies[prob[0]].append((n+1, prob[1], entry, prob[2]))

        if len(page_probabilities_frequencies.keys()) == 0:
            continue

        # Get the best scoring title of all candidate titles by taking into account each time it's in the best
        pages_voting_scores = []
        for page in page_probabilities_frequencies.keys():
            vote = 0
            best_title = ("", 0)
            for page_freq in page_probabilities_frequencies[page]:
                vote += page_freq[1]/page_freq[0]

                # Select the title that has the best ratio of english words over all words
                title_confidence = dictionary_analysis.sentence_dictionary_confidence(page_freq[2], eng_dict, tolerance=0)
                if title_confidence >= best_title[1]:
                    best_title = (page_freq[2], title_confidence)
            best_for_page = max(page_probabilities_frequencies[page], key=itemgetter(1))

            pages_voting_scores.append((page, vote, best_title[0], best_for_page[3]))
        best_entry = max(pages_voting_scores, key=itemgetter(1))
        chosen_page_and_prob.append(best_entry)

        print(best_entry)
        print("-" * 20)

    print("Finished analyzing")
    print("Pages found:")
    print([p[0] for p in chosen_page_and_prob])

    print("Correct pages")
    print(correctICPR2)

    with open("tempResults", "wb") as f:
        pickle.dump(chosen_page_and_prob, f)

    corrects = []
    wrongs = []
    i = 0
    train = 0
    ntrain = 0
    test = 0
    correct_train = 0
    correct_test = 0
    for x, y in zip(correctICPR2, chosen_page_and_prob):
        if x < 1:
            i+=1
            continue
        if x != y[0]:
            print(x, y[0], "Wrong", y[1], y[2])
            wrongs.append(y[1])
            if i < ntrain:
                train += 1
            else:
                test += 1
        else:
            print(x, y[0], "Correct", y[1],y[2])
            corrects.append(y[1])
            if i < ntrain:
                train += 1
                correct_train += 1
            else:
                test += 1
                correct_test += 1
        i+=1

    if len(corrects) > 0:
        print("Corrects:", len(corrects),  statistics.mean(corrects))
    if len(wrongs) > 0:
        print("Wrongs:", len(wrongs), statistics.mean(wrongs))
    #print("Training: Found " + str(train) + ", Correct " + str(correct_train) + ", Accuracy :" + str(correct_train/train))
    print("Test: Found " + str(test) + ", Correct " + str(correct_test) + ", Accuracy :" + str(correct_test/test))

    fixed_titles = fix_titles(chosen_page_and_prob, pages_words, eng_dict)
    print(fixed_titles)



def find_toc_pages(all_pages):
    """
    Find out which pages qualify to be part of the table of contents
    :type all_pages: list[bs4.BeautifulSoup]
    :return: List containing the pages that make up the table of contents
    """
    toc_pages = []

    for n, page in enumerate(all_pages[0:100]):
        text = extract_page_text(page)

        # Search only numbers with 2 or 3 digits, ignoring the first one(it's the page number)
        number_list = [int(n) for n in re.findall(r'\d{2,3}', text)[1:]]

        # Try to extract an ordered list of numbers, by removing numbers that aren't in order
        # (or that cause too much of a gap)
        max_gap = 100

        ordered_list = []
        for number in number_list:
            if len(ordered_list) == 0:
                ordered_list.append(number)
            elif number > ordered_list[-1] and (number - ordered_list[-1]) < max_gap:
                ordered_list.append(number)


        # Calculate distance variance between numbers in page
        distances = []
        distance_stdev = -1

        for i, number in enumerate(ordered_list):
            if i != 0:
                distances.append(number - ordered_list[i-1])

        if len(distances) > 2:
            distance_stdev = statistics.stdev(distances)

        # Take into account only the first 100 pages, which have a number of numbers greater than 10 and a good enough
        # variance between the distances of those numbers
        if len(ordered_list) >= 3 and 0 <= distance_stdev < 15 :
            toc_pages.append(n)

    toc_sequences = []
    last_page = -1
    current_sequence = []
    for page in toc_pages:
        if last_page == -1:
            current_sequence = [page]
        elif last_page == page - 1:
            current_sequence.append(page)
        elif last_page == page - 2:
            current_sequence.append(page - 1)
            current_sequence.append(page)
        else:
            toc_sequences.append(current_sequence)
            current_sequence = [page]
        last_page = page
    if len(current_sequence) > 0:
        toc_sequences.append(current_sequence)
    print(toc_sequences)
    longest_sequence = []
    for seq in toc_sequences:
        if len(longest_sequence) < len(seq):
            longest_sequence = seq
    return longest_sequence


def find_candidate_titles(lps, toc_lines):
    candidate_titles = []
    for i, link in enumerate(lps):
        titles_for_link = []
        current_line = link[0]
        titles_for_link.append(util.remove_punctuation(toc_lines[current_line][:link[2][0]]).strip())
        while current_line > lps[i-1][0] + 1 or (i == 0 and current_line > 0):
            current_line -= 1
            current_line_text = util.remove_punctuation(toc_lines[current_line]).strip()
            if len(current_line_text) > 0:
                titles_for_link.append((current_line_text + " " + titles_for_link[-1]))

        # Discard short titles
        titles_for_link = [re.sub(r'  +', ' ', title) for title in titles_for_link if len(title) > 0]
        candidate_titles.append(titles_for_link)

    return candidate_titles

def find_candidate_titles_2(lps, toc_lines):
    # For the second kind of documents, where the number is in the first/second line
    candidate_titles = []
    for i, link in enumerate(lps):

        titles_for_link = []
        current_line = link[0] if link[0] > 0 else 0

        next_line = lps[i+1][0] if i != len(lps)-1 else len(toc_lines)
        while current_line < next_line:
            current_line_text = util.remove_punctuation(toc_lines[current_line]).strip()

            found = regex.search(r"(\d+){i<=2}", current_line_text)
            if found is not None and found.span()[1] > len(current_line_text) - 3:
                current_line_text = current_line_text[:found.span()[0]] + current_line_text[found.span()[1]:]

            if len(current_line_text) > 0:
                if len(titles_for_link) == 0:
                    titles_for_link.append(current_line_text)
                else:
                    titles_for_link.append((titles_for_link[-1] + " " + current_line_text))
            current_line += 1

        # Discard short titles
        titles_for_link = [re.sub(r'  +', ' ', title) for title in titles_for_link if len(title) > 0]
        candidate_titles.append(titles_for_link)

    return candidate_titles

def fix_titles(page_and_titles, pages_words, eng_dict):
    article_page_title = []
    for article in page_and_titles:
        orig_title = article[2]
        print(orig_title)
        page = article[0]

        # Remove the big title things
        matches = [m for m in regex.finditer("(?<!\S)\d(?!\S)", orig_title)]
        if len(matches) > 0:
            orig_title = orig_title[matches[-1].end(0):]
        reduced_title = orig_title.strip()

        merged_title = dictionary_analysis.merge_title(reduced_title, eng_dict)

        # Search for the word with the best score in the corresponding page
        final_title = ""
        for title_word in merged_title.split(" "):
            if title_word.isupper():
                final_title += title_word + " "
                continue
            title_word = title_word.lower()

            best_word = title_word
            best_score = 0
            for page_word in pages_words[page]:
                score = util.ngram_scoring(title_word, page_word, 3)
                if score > best_score:
                    best_word = page_word
                    best_score = score

            fixed_word_from_title, d1 = dictionary_analysis.closest_word(title_word, eng_dict)
            fixed_word_from_page, d2 = dictionary_analysis.closest_word(best_word, eng_dict)
            chosen_word = ""
            if title_word == best_word:
                chosen_word = title_word
            else:
                chosen_word, d = (fixed_word_from_page, d2) if d2 < d1 else (fixed_word_from_title, d1)

                if d > 1:
                    chosen_word = title_word
            final_title += chosen_word + " "

        print(final_title.strip())
        article_page_title.append((final_title.strip(), page))

    return article_page_title


###############################################################################################################
def extract_toc_content(html):
    pages = [bs4.BeautifulSoup(page) for page in pickle.load(open("bs_splitpages","rb"))]
    print("Pages split")
    toc_pages = find_toc_pages(pages)
    print("Table of contents pages found:", toc_pages)

    min_fsize, max_fsize, avg_fsize = get_document_fontsize_stats(pages)
    print(f"Document font size information: \n min fontsize:{min_fsize} \n max fontsize:{max_fsize} \n "
          f"average fontsize: {avg_fsize}\n")

    # Get all text lines from table of contents
    toc_lines = []
    for page_index in toc_pages:
        toc_lines += extract_lines_from_page(pages[page_index], remove_dot=False)

    # Find the link pages(lps), in which line they sit and in which position in the line
    lps = []
    for i, line in enumerate(toc_lines):
        found = regex.search(r"(p\.\d+){1i+2d+2s<=2}", line)
        if found is not None:
            lps.append((i, found.group(), found.span()))
    print("Article links found")
    print(lps, "\n")

    # Find the candidate link titles
    candidate_titles = find_candidate_titles(lps, toc_lines)
    print("Candidate titles found")
    print(candidate_titles, "\n")

    pages_words = []
    # Take only the upper part of the pages and text with bigger than avg fsize( and record  the fsize and line)
    for n, page in enumerate(pages):
        if n != len(pages) - 1:
            pages_words.append([(word[0].lower(), word[1], word[2]) for word in
                                extract_words_fsize_line_from_page_vertical_region(page, pages[n+1], 0.3, avg_fsize - 1)])
        else:
            pages_words.append([(word[0].lower(), word[1],word[2]) for word in
                                extract_words_fsize_line_from_page_vertical_region(page, None, 0.3, avg_fsize-1)])
    print("Important information from pages extracted, start title-page matching")

    pages_scores = find_target_pages(candidate_titles, pages_words, toc_pages, min_fsize, max_fsize, avg_fsize)

    print("Finished analyzing")
    print("Pages found:")
    print([p[0] for p in pages_scores])

    print("Correct pages")
    print(correct)

    corrects = []
    wrongs = []
    for x, y in zip(correct, pages_scores):
        if x != y[0]:
            print(x, y[0], "Wrong", y[1])
            wrongs.append(y[1])
        else:
            print(x, y[0], "Correct", y[1])
            corrects.append(y[1])

    if len(corrects) > 0:
        print("Corrects:", len(corrects),  statistics.mean(corrects))
    if len(wrongs) > 0:
        print("Wrongs:", len(wrongs), statistics.mean(wrongs))


def find_target_pages(candidate_titles, pages_words, toc_pages, min_fsize, max_fsize, avg_fsize):
    """
    Find the best scoring page for each article candidate titles

    :param candidate_titles: each element in the list is a list of candidate titles for each article
    :type candidate_titles: list[list[str]]
    :param toc_pages: list that contains the indexes of the toc pages
    :type toc_pages: list[int]
    :param pages_words: each entry of the list is the list of words in that page(with associated fsize)
    :type pages_words: list[list[tuple[str,int]]]
    :type min_fsize: float
    :type max_fsize: float
    :type avg_fsize: float
    :return: list best page and score for each article
    :rtype: list[tuple[int,float]]
    """
    chosen_page_and_score = []
    # Iterate over the articles
    for entries in candidate_titles:
        print(entries)

        # List of tuples (entry, page_number, score)
        entry_best_page_score = []

        # Iterate over the candidate titles for each article
        for entry in entries:
            # List of tuples (page_number, page_score)
            pages_score = []

            # Dont' consider words that are shorter than 2 characters
            entry_words = [word.lower() for word in entry.split(" ") if len(word) > 2]

            # Don't consider candidate titles that are too short
            if len(entry_words) < 3:
                continue

            # Start searching in pages after the toc
            for page_words in pages_words[toc_pages[-1] + 1:]:
                # List of tuples ( word_position, word_score, (actual_word, actual_word_fsize, line_number))
                # record the word that had the best ngram score for a single word in the candidate title
                best_words = []

                # Record which words in the page were chosen as best for any word in the ctitle
                already_checked_words = []

                # Iterate over words in candidate title
                for entry_word in entry_words:
                    # List of tuples, contains the score of each word in the page with regard to the current word in the
                    # candidate title
                    # (word_position, word_score, (actual_word, actual_word_fsize, line_number)
                    entry_word_scores = []

                    # Iterate over words in page
                    for n, page_word in enumerate(page_words):
                        if page_word not in already_checked_words:
                            entry_word_scores.append((n, util.ngram_scoring(entry_word, page_word[0], 3), page_word))

                    # Find the word with the best score
                    if len(entry_word_scores) == 0:
                        best_words.append((-1, 0, ("None", 0, -100)))
                    else:
                        best_page_word_score = max(entry_word_scores, key=itemgetter(1))
                        best_words.append(best_page_word_score)
                        already_checked_words.append(best_page_word_score[2])

                # Find average distance between subsequent best scoring words in the page
                distances = []
                for i, score_pos in enumerate(best_words):
                    if i != len(best_words) - 1:
                        distance = abs(best_words[i][0] - best_words[i + 1][0])
                        #distance = abs(best_words[i][2][2] - best_words[i + 1][2][2])
                        distances.append(distance)
                #positions = [word[0] for word in best_words]
                #pos_stddev = statistics.stdev(positions)
                # Total score: take into account word score(word[1]), word font-size(importance)
                # And finally mean distance between words
                page_score = sum([word[1] * fsize_importance(word[2][1], min_fsize, max_fsize, avg_fsize)
                                  for word in best_words]) / (len(entry_words))
                page_score = word_closeness_decay(statistics.mean(distances)) * page_score
                #page_score = word_closeness_decay(pos_stddev) * page_score

                # Record (page_number, page_score, mean_distance)
                pages_score.append(
                    #(int(page_words[1][0]), page_score, pos_stddev))
                    (int(page_words[1][0]), page_score, statistics.mean(distances)))

            # Get the best page for the candidate titles
            pages_score.sort(key=itemgetter(1),reverse=True)
            print(pages_score[:5])
            best_score = max(pages_score, key=itemgetter(1))

            entry_best_page_score.append((entry, best_score[0], best_score[1], best_score[2]))

        # Get the best scoring title of all candidate titles
        best_entry = max(entry_best_page_score, key=itemgetter(2))

        chosen_page_and_score.append((best_entry[1], best_entry[2]))

        print(best_entry)
        print("-" * 20)
    return chosen_page_and_score


