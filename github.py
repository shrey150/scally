from typing import Dict, Literal, Optional
from dotenv import load_dotenv
from pprint import pprint
from langchain_community.document_loaders.github import GitHubPRLoader
import os
import json

from pydantic import root_validator

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

loader = GitHubPRLoader(
    repo="expressjs/express",
    labels=["5.x"], # TODO this label doesn't work...
    access_token=ACCESS_TOKEN,
)

docs = loader.load()
example_doc = list(filter(lambda x: x.metadata['number'] == 4852, docs))


print(example_doc)

files = loader.get_changed_files(4852)



print(len(files))

files_info = json.dumps(files)

print(files_info)

from git import Repo, GitCommandError
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain_text_splitters import Language
from dotenv import load_dotenv

load_dotenv()

# Clone
try:
    repo_path = "rag_repo"
    repo = Repo.clone_from("https://github.com/shrey150/NetflixGPT", to_path=repo_path)
except GitCommandError:
    pass

# Load
loader = GenericLoader.from_filesystem(
    repo_path,
    glob="**/*",
    suffixes=[".py"],
    exclude=["**/non-utf8-encoding.py"],
    parser=LanguageParser(language=Language.PYTHON, parser_threshold=500),
)
documents = loader.load()
len(documents)

from langchain_text_splitters import RecursiveCharacterTextSplitter

python_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON, chunk_size=2000, chunk_overlap=200
)
texts = python_splitter.split_documents(documents)
len(texts)

print(texts)

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

db = Chroma.from_documents(texts, HuggingFaceEmbeddings())
retriever = db.as_retriever(
    search_type="mmr",  # Also test "similarity"
    search_kwargs={"k": 8},
)

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o")

# First we need a prompt that we can pass into an LLM to generate this search query

prompt = ChatPromptTemplate.from_messages(
    [
        ("placeholder", "{chat_history}"),
        ("user", "{input}"),
        (
            "user",
            "Given the above conversation, generate a search query to look up to get information relevant to the conversation",
        ),
    ]
)

retriever_chain = create_history_aware_retriever(llm, retriever, prompt)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a world-class engineer who has full knowledge of the given codebase. Use the below context in the user's task:\n\n{context}",
        ),
        ("placeholder", "{chat_history}"),
        ("user", "{input}"),
    ]
)
document_chain = create_stuff_documents_chain(llm, prompt)

qa = create_retrieval_chain(retriever_chain, document_chain)



question = (
    "Generate an onboarding guide in Markdown composed of the core principles shown through this pull request." +
    "Focus on the steps the developer took in the context of the entire codebase and explain in enough detail," +
    "such that another engineer could read this onboarding guide, implement the patch, and solve the issue.\n\n" +
    f"Here are the patch notes: {files_info}\n\n" +
    "Onboarding guide:\n```md\n"
)
result = qa.invoke({"input": question})
print(result["answer"])


