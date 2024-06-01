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



# question = (
#     "Generate an onboarding guide in Markdown composed of the core principles shown through this pull request." +
#     "Focus on the steps the developer took in the context of the entire codebase and explain in enough detail," +
#     "such that another engineer could read this onboarding guide, implement the patch, and solve the issue.\n\n" +
#     f"Here are the patch notes: {}"
# )
result = qa.invoke({"input": question})
print(result["answer"])
