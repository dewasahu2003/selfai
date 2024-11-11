from .base import BaseCrawler
from db.documents import RepositoryDoc
from aws_lambda_powertools import Logger
from tempfile import mkdtemp
import os
import subprocess
import shutil

logger = Logger(service="selfai/crawler/github")


class GithubCrawler(BaseCrawler):
    "crawl github repositories, it does not need to scroll so using BaseCrawler"
    model = RepositoryDoc

    def __init__(self, ignore=(".git", ".toml", ".lock", ".png")) -> None:
        super().__init__()
        self._ignore = ignore

    def extract(self, link: str, **kwargs) -> None:
        """extract repository information"""
        logger.info(f"extractig github repo {link}")
        repo_name = link.rstrip("/").split("/")[-1]
        local_temp = mkdtemp()

        try:
            os.chdir(local_temp)
            subprocess.run(["git", "clone", link])
            repo_path = os.path.join(local_temp, os.listdir(local_temp)[0])

            tree = {}
            for root, dirs, files in os.walk(repo_path):
                dir = root.replace(repo_path, "").lstrip("/")
                if dir.startswith(self._ignore):
                    continue
                for file in files:
                    if file.endswith(self._ignore):
                        continue
                    file_path = os.path.join(dir, file)
                    with open(os.path.join(root, file), "r", errors="ignore") as f:
                        tree[file_path] = f.read().replace(" ", "")

            instance = self.model(
                name=repo_name, link=link, content=tree, owner_id=kwargs.get("user")
            )
            instance.save()
        except Exception:
            raise
        finally:
            shutil.rmtree(local_temp)
        logger.info(f"extracted github repo {link}")
