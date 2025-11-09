import logging
import ollama


class Tokenizer:

    def __init__(self, model_name: str):
        self._model_name = model_name

    def count_tokens(self, text: str) -> int:
        # truncate: If true, truncate inputs that exceed the context window. If false, returns an error.
        # https://docs.ollama.com/api/embed
        logging.debug(f"Counting tokens for text of length {len(text)}")
        try:
            count = ollama.embed(
                model=self._model_name, input=text, truncate=False
            ).prompt_eval_count
            if isinstance(count, int):
                return count
        except Exception as e:
            logging.debug(f"Error counting tokens: {e}")

        return 10000000
