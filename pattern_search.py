from openai import OpenAI
import json
import os

from openai_wrapper import OpenAIWrapper


class PatternSearch:

    def search_for_a_keyword(self, keyword, file_path):
        print("Searching for" + keyword)
        keyword_search_result = {}
        for subdir, dirs, files in os.walk(file_path):
            for file in files:
                line_number = 0
                with open(file_path + "\\" + file) as idplus_file:
                    for oneline in idplus_file:
                        line_number += 1
                        if keyword in oneline:
                            if keyword not in keyword_search_result.keys():
                                keyword_search_result[keyword] = {
                                    file_path + "\\" + file: [{line_number: oneline}]}
                            else:
                                if file_path + "\\" + file not in keyword_search_result[keyword].keys():
                                    keyword_search_result[keyword][file_path + "\\" + file] = [
                                        {line_number: oneline}]
                                else:
                                    keyword_search_result[keyword][file_path + "\\" + file].append(
                                        {line_number: oneline})
        return keyword_search_result

    # returns a set {file-name: {line#of_occurance#1: the content of the line}}
    def search_occurrences_of_keywords(self, openai_wrapper, sentence, filepath):
        keywords = openai_wrapper.extract_keywords(sentence)
        print("Looking for keywords" + str(keywords))
        keyword_search_result = {}
        for keyword in keywords:
            keyword_search_result.update(self.search_for_a_keyword(keyword, filepath))
        print(keyword_search_result)
        return keyword_search_result
