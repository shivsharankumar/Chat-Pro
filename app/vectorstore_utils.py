from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
# from typing import list,Optional
# from langchain_openai import OpenAIEmbeddings
from .config import EURI_API_KEY



def create_faiss_index(texts:list[str])->FAISS:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vectorstore = FAISS.from_texts(texts, embeddings) #convert text to vector
    return vectorstore

def retrieve_relevant_documents(vectorstore:FAISS, query:str, k:int=4)->list[str]:
    return vectorstore.similarity_search(query, k=k)
