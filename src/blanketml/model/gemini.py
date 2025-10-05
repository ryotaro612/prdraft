from google import genai
from google.genai import chats
from google.genai.types import GenerateContentResponse, Part, Blob
import typing


def create_chat() -> chats.Chat:
    client = genai.Client()
    return client.chats.create(model="gemini-2.0-flash")


class Example(typing.TypedDict):
    ja: str
    paper_path: str


def fewshot(
    chat: chats.Chat, paper_path: str, examples: list[Example], system_instruction: str
) -> GenerateContentResponse:

    parts = []
    for example in examples:
        with open(example["paper_path"], "rb") as f:
            paper_content = f.read()
            parts.append(
                Part(inline_data=Blob(data=paper_content, mime_type="application/pdf"))
            )
        with open(example["ja"], "r", encoding="utf-8") as f:
            print(Part(text=f.read()))
            parts.append(Part(text=f.read()))

    with open(paper_path, "rb") as f:
        paper_content = f.read()
        parts.append(
            Part(inline_data=Blob(data=paper_content, mime_type="application/pdf"))
        )
    return chat.send_message(parts, {"system_instruction": system_instruction})
