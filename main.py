# This is a sample Python script.
import json
import os
from openai import OpenAI

from langchain_community.document_loaders import Docx2txtLoader
from openai.types.chat import ChatCompletionMessage

from openai_wrapper import OpenAIWrapper
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    import openai

    client = OpenAI()

    completion = client.chat.completions.create(

        model="gpt-3.5-turbo",

        messages=[

            {"role": "system", "content": "You are a helpful assistant."},

            {"role": "user",
             "content": "give me keywords from the following sentence, exlude RSA, ID-Plus. Does RSA ID-Plus  record copies of online consent"}

        ]
    )
    keyword_search_result = {}
    with open("initial.conf") as conf_file:
        configuration = json.load(conf_file)
    print(completion.choices[0].message)

    for keyword in json.loads(completion.choices[0].message.to_json())['content'].split(":")[1].split(","):
    # for keyword in json.loads(completion.choices[0].message.to_json())['content'].split(":")[1].split(","):
        keyword = keyword.strip()
        keyword = keyword.strip(".")
        print("Searching for" + keyword)
        for subdir, dirs, files in os.walk(configuration["file_path"]):
            for file in files:
                line_number = 0
                with open(configuration["file_path"] + "\\" + file) as idplus_file:
                    for oneline in idplus_file:
                        line_number += 1
                        if keyword in oneline:
                            if keyword not in keyword_search_result.keys():
                                keyword_search_result[keyword] = {
                                    configuration["file_path"] + "\\" + file: [{line_number:oneline}]}
                            else:
                                if configuration["file_path"] + "\\" + file not in keyword_search_result[keyword].keys():
                                    keyword_search_result[keyword][configuration["file_path"] + "\\" + file] = [{line_number:oneline}]
                                else:
                                    keyword_search_result[keyword][configuration["file_path"] + "\\" + file].append({line_number:oneline})
        print(keyword_search_result)

    # with open("initial.conf") as conf_file:
    #     configuration = json.load(conf_file)
    # for subdir, dirs, files in os.walk(configuration["file_path"]):
    #     for file in files:
    #         with open(configuration["file_path"] + "\\" + file) as idplus_file:
    #
    # # loader = Docx2txtLoader(
    # #     "C:\\Users\\vinod.nair\\Desktop\\Delete\\Uni of Melbourne Schedule C Technical requirements Draft 9 with Assignments PS LG Partner.docx")
    # # docs = loader.load()
    # text_splitter = RecursiveCharacterTextSplitter()
    # # documents = text_splitter.split_documents(docs)
    #
    # with open(configuration["file_path"] + "\\" + "Appendix 2-5_IAMTextVersion.txt") as idplus_file:
    #             master_doc = text_splitter.create_documents(idplus_file.readlines())
    #
    # wannabemasterdoc = []
    #
    # for subdir, dirs, files in os.walk(configuration["file_path"]):
    #     for file in files:
    #         with open(configuration["file_path"] + "\\" + file) as idplus_file:
    #             wannabemasterdoc += (text_splitter.create_documents(idplus_file.readlines()))
    #
    # openai_wrapper = OpenAIWrapper(org_id=configuration["openai_conf"]["org_id"],
    #                                api_key=configuration["openai_conf"]["api_key"])
    # openai_wrapper.process_documents(wannabemasterdoc)
    # response = openai_wrapper.ask("Does RSA ID Plus  record copies of online consent? if not why not?")
    #
    # print(response)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
