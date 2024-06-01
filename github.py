from dotenv import load_dotenv
import os

load_dotenv()

from langchain_community.document_loaders import GitHubIssuesLoader

loader = GitHubIssuesLoader(
    repo="langchain-ai/langchain",
    access_token=os.getenv("ACCESS_TOKEN"),  # delete/comment out this argument if you've set the access token as an env var.
)

docs = loader.load()

print(docs[0].page_content)
print(docs[0].metadata)

