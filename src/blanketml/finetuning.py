import sys
import logging
import json
import base64
import csv


if __name__ == "__main__":
    source_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(source_file) as s_f, open(output_file, "w") as o_f:
        reader = csv.DictReader(s_f)
        for i, record in enumerate(reader):
            with open(record["paper_path"], "rb") as pdf:
                pdf_bytes = pdf.read()
                encoded_pdf = base64.b64encode(pdf_bytes).decode()

            with open(record["md_path"]) as md_f:
                lines = md_f.readlines()

            idx = [i for i, line in enumerate(lines) if line.startswith("---")]
            if len(idx) < 2:
                logging.warning("Markdown file does not have front matter.")

            md = "".join(lines[idx[1] + 1 :])

            messages = [
                {
                    "role": "developer",
                    "content": "以下の方針でPDF形式の論文を要約してください。\n- 文末は常体\n- 箇条書きを避ける\n- 見出しを控える\n- 重要な数式とその解説を含める",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "text": "論文を要約してください。要約をブログに記載したいです。",
                            "type": "text",
                        },
                        {"type": "text", "file": {"file_data": encoded_pdf}},
                    ],
                },
                {"role": "assistant", "content": md},
            ]
            line = json.dumps({"messages": messages}, ensure_ascii=False)
            if i:
                o_f.write("\n")
            o_f.write(line)
