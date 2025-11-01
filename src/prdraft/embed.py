import prdraft.args as args
import logging
import git
import itertools
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
import duckdb
import prdraft.pullrequest as pr
import prdraft.repository as r


def run(args: args.PrEmbedArgs) -> int:
    embeddings = HuggingFaceEmbeddings(model_name=args.model)
    repo = git.Repo(args.repository)

    org, repo_name = _determine_repository_id(repo.remotes.origin.url)
    print(org, repo_name)
    with duckdb.connect(args.database) as conn:
        count = 0
        for batch in itertools.batched(
            pr.find_not_embeded_pull_requests(conn, org, repo_name, args.model), 10
        ):
            diff_texts = [
                r.make_diff_summary(repo, pullr.base_sha, pullr.head_sha)
                for pullr in batch
            ]
            diff_embeddings = embeddings.embed_documents(diff_texts)
            pr.save_embedded_pull_request(
                conn,
                org,
                repo_name,
                args.model,
                [
                    pr.EmbeddedPullRequest(
                        pull_request_id=pullr.id, embedded=embedding, text=diff_text
                    )
                    for pullr, diff_text, embedding in zip(
                        batch, diff_texts, diff_embeddings
                    )
                ],
            )
            count += len(batch)
            logging.debug(f"processed {count} pull requests")

    return 0


def _determine_repository_id(git_url: str) -> tuple[str, str]:
    org_name, repo_name = git_url.split(":")[1].split("/")
    return org_name, repo_name[:-4]
