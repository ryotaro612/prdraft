CREATE TABLE pull_request_qwen3_embedding(pull_request_id bigint, diff_text varchar, diff_embedding float[4096], PRIMARY KEY(pull_request_id));
COMMENT ON TABLE pull_request_qwen3_embedding IS 'pull request metadata';
COMMENT ON COLUMN pull_request_qwen3_embedding.pull_request_id IS 'id of pull request';
COMMENT ON COLUMN pull_request_qwen3_embedding.diff_text IS 'diff text of pull request';
COMMENT ON COLUMN pull_request_qwen3_embedding.diff_embedding IS 'diff embedding of pull request';


create table pull_request(id bigint, body varchar, raw json, primary key(id));