from typing import Dict, Literal, Optional
from dotenv import load_dotenv
from pprint import pprint
import os
import json
from git import Repo, GitCommandError
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from loader import GitHubPRLoader, extract_info
from langchain_text_splitters import Language
from dotenv import load_dotenv
import re

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
URL = "https://github.com/expressjs/express/pull/4852"


def fetch_changed_files(url: str) -> str:
    base_repo, issue_num = extract_info(url)

    loader = GitHubPRLoader(
        repo=base_repo,
        access_token=ACCESS_TOKEN,
    )

    docs = loader.load()
    example_doc = list(filter(lambda x: x.metadata['number'] == 4852, docs))

    files = loader.get_changed_files(issue_num)
    files_info = json.dumps(files)

    return files_info


def get_relevant_code(url: str) -> str:
    base_repo, issue_num = extract_info(url)

    # Clone
    try:
        print('Cloning...')
        repo_path = f"../data/{base_repo}"
        repo = Repo.clone_from(f"https://github.com/{base_repo}", to_path=repo_path)
    except GitCommandError as e:
        print(e)
        pass

    print(os.path.abspath(repo_path))

    # Load
    loader = GenericLoader.from_filesystem(
        path=repo_path,
        glob="**/*",
        suffixes=[".py",".js",".c",".cc",".cpp",".rb",".rs",".go",".ts",".tsx",".jsx",".java"],
        exclude=["**/non-utf8-encoding.py"],
        parser=LanguageParser(language=Language.PYTHON, parser_threshold=500),
    )
    documents = loader.load()
    print(f'Loaded repo {url}.')
    print(len(documents))

    from langchain_text_splitters import RecursiveCharacterTextSplitter

    python_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, chunk_size=2000, chunk_overlap=200
    )

    texts = python_splitter.split_documents(documents)

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

    print('Fetching changed files from PR...')
    files_info = fetch_changed_files(url)
    print('Fetched.')

    question = (
        "Generate an onboarding guide in Markdown composed of the core principles shown through this pull request." +
        "Focus on the steps the developer took in the context of the entire codebase and explain in enough detail," +
        "such that another engineer could read this onboarding guide, implement the patch, and solve the issue.\n\n" +
        f"Here are the patch notes: {files_info}\n\n" +
        "Onboarding guide:\n```md\n"
    )
    print(question)
    result = qa.invoke({"input": question})
    print(f"Answer: {result['answer']}")
    return result["answer"]
