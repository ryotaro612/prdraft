""" """

import typing as t
import blanketml.config as conf
import blanketml.file as fi
import blanketml.markdown as md
from openai import OpenAI


def _create_client() -> OpenAI:
    return OpenAI()


def _generate(
    client: OpenAI, input, instructions: str | None, previous_response_id: str | None
):
    """
    Note that Consider making instructions previous state mutually exclusive.
    """
    response = client.responses.create(
        model="gpt-4.1",
        input=input,
        instructions=instructions,
        previous_response_id=previous_response_id,
    )
    return response


def read_fewshot(config: conf.Config):
    fewshot = []
    for name, post in config.posts.items():
        summary = md.remove_front_matter(fi.read_file(post.ja))
        paper_bin = fi.read_bin_base64(post.paper)
        fewshot.append(
            {
                "content": [
                    {
                        "file_data": f"data:application/pdf;base64,{paper_bin}",
                        "type": "input_file",
                        "filename": name + ".pdf",
                    },
                    {"text": f"{name}.pdfを要約してください。", "type": "input_text"},
                ],
                "role": "user",
            }
        )
        fewshot.append(
            {
                "content": [
                    {"text": summary, "type": "output_text"},
                ],
                "role": "assistant",
            }
        )

    return fewshot
