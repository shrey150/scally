from dotenv import load_dotenv
from pprint import pprint
from langchain_community.document_loaders import GitHubIssuesLoader
import os

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

loader = GitHubIssuesLoader(
    repo="expressjs/express",
    labels=["good first contribution"], # TODO this label doesn't work...
    access_token=ACCESS_TOKEN,
)

docs = loader.load()

pprint(docs)

