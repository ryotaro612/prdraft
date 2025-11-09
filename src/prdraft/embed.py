import prdraft.args as args
import logging
import git
import ollama
from transformers import AutoTokenizer
import duckdb
import prdraft.pullrequest as pr
import prdraft.repository as r
import prdraft.tokenizer as tokenizer


def run(args: args.PrEmbedArgs) -> int:
    repo = git.Repo(args.repository)

    org, repo_name = _determine_repository_id(repo.remotes.origin.url)
    with (
        duckdb.connect(args.database) as conn0,
        duckdb.connect(args.database) as conn1,
    ):
        for c in [conn0, conn1]:
            c.execute("load vss")

        count = 0
        for pullreq in pr.find_not_embeded_pull_requests(
            conn0, org, repo_name, args.model
        ):
            if not pullreq.merged:
                continue

            diff_text = pr.make_summary(
                repo,
                pullreq.base_sha,
                pullreq.head_sha,
                tokenizer.Tokenizer(model_name=args.model),
                3500,
            )

            raw_res = ollama.embed(model=args.model, input=diff_text)
            res = raw_res.embeddings

            pr.save_embedded_pull_request(
                conn1,
                org,
                repo_name,
                args.model,
                [
                    pr.EmbeddedPullRequest(
                        pull_request_id=pullreq.id,
                        embedded=res[0],
                        text=diff_text,
                    )
                ],
            )
            count += 1
            logging.debug(f"processed {count} pull requests")

    return 0


def _determine_repository_id(git_url: str) -> tuple[str, str]:
    org_name, repo_name = git_url.split(":")[1].split("/")
    return org_name, repo_name[:-4]
