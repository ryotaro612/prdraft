import prdraft.args as args
import logging
import git
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from transformers import AutoTokenizer
import duckdb
import prdraft.pullrequest as pr
import prdraft.repository as r


def run(args: args.PrEmbedArgs) -> int:
    embeddings = HuggingFaceEmbeddings(model_name=args.model)
    repo = git.Repo(args.repository)
    tokenizer = AutoTokenizer.from_pretrained(args.model)

    org, repo_name = _determine_repository_id(repo.remotes.origin.url)
    with duckdb.connect(args.database) as conn:
        conn.execute("load vss")

        count = 0
        for pullreq in pr.find_not_embeded_pull_requests(
            conn, org, repo_name, args.model
        ):
            if not pullreq.merged:
                continue

            diff_text = pr.make_summary(
                repo, pullreq.base_sha, pullreq.head_sha, _Tokenizer(tokenizer), 4000
            )
            print(diff_text)

            # diff_embeddings = embeddings.embed_documents([diff_text])[0]
            # pr.save_embedded_pull_request(
            #     conn,
            #     org,
            #     repo_name,
            #     args.model,
            #     [
            #         pr.EmbeddedPullRequest(
            #             pull_request_id=pullreq.id,
            #             embedded=diff_embeddings,
            #             text=diff_text,
            #         )
            #     ],
            # )
            count += 1
            logging.debug(f"processed {count} pull requests")

    return 0


def _determine_repository_id(git_url: str) -> tuple[str, str]:
    org_name, repo_name = git_url.split(":")[1].split("/")
    return org_name, repo_name[:-4]


class _Tokenizer:

    def __init__(self, inner):
        self._inner = inner

    def count_tokens(self, text: str) -> int:
        return len(self._inner(text)["input_ids"])
