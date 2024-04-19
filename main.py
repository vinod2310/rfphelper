# This is a sample Python script.
import json

from langchain_community.document_loaders import Docx2txtLoader
from openai_wrapper import OpenAIWrapper
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    with open("initial.conf") as conf_file:
        configuration = json.load(conf_file)

    loader = Docx2txtLoader(
        "/Users/vinod/Downloads/Uni of Melbourne Schedule C Technical requirements Draft 9 with Assignments PS LG Partner.docx")
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter()
    documents = text_splitter.split_documents(docs)
    openai_wrapper = OpenAIWrapper(org_id=configuration["openai_conf"]["org_id"],
                                   api_key=configuration["openai_conf"]["api_key"])
    openai_wrapper.process_documents(documents)
    response = openai_wrapper.ask({"input": "Does RSA support SSO with social identity?"})

    print(response)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
