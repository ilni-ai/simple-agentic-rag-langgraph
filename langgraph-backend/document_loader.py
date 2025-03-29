# document_loader.py
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_documents(file_path="data/info.txt"):
    loader = TextLoader(file_path)
    documents = loader.load()

    # Split into smaller chunks for better embedding & retrieval
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
    return splitter.split_documents(documents)
