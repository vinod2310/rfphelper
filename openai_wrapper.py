from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_openai import OpenAIEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS


class OpenAIWrapper:

    def __init__(self, org_id, api_key):
        self.retrieval_chain = None
        self.vector = None
        self.org_id = org_id
        self.api_key = api_key
        llm = ChatOpenAI(
            organization="org-fSxyjoh12x4jAMTN665PsHs2",
            api_key="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")

        prompt = ChatPromptTemplate.from_template("""Answer the following question based only on the provided context:
                                <context>
                                {context}
                                </context>
                                Question: {input}""")

        self.document_chain = create_stuff_documents_chain(llm, prompt)
        self.embeddings = OpenAIEmbeddings()

    def process_documents(self, documents):
        self.vector = FAISS.from_documents(documents, self.embeddings)
        retriever = self.vector.as_retriever()
        self.retrieval_chain = create_retrieval_chain(retriever, self.document_chain)

    def ask(self, question):
        response = self.retrieval_chain.invoke({"input": question})
        return response["answer"]
