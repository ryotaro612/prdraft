import blanketml.config as c
import blanketml.file as fi
import blanketml.model.openai as o


def temp():

    config = c.load("./config.toml")
    fewshot = o.read_fewshot(config)

    lora = fi.read_bin_base64("ORA-low-rank-adaptation-of-large-language-models.pdf")
    name = "LORA-low-rank-adaptation-of-large-language-models"
    fewshot.append(
        {
            "content": [
                {
                    "file_data": f"data:application/pdf;base64,{lora}",
                    "type": "input_file",
                    "filename": name + ".pdf",
                },
                {"text": f"{name}.pdfを要約してください。", "type": "input_text"},
            ],
            "role": "user",
        }
    )
    client = o._create_client()

    response = o._generate(
        client,
        input=fewshot,
        instructions=config.insutruction,
        previous_response_id=None,
    )
    return response
