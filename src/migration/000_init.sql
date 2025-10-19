CREATE TABLE pull_request_qwen3_embedding(pull_request_id, embedding , PRIMARY KEY(pull_request_id));
COMMENT ON TABLE pull_request IS 'pull request metadata';
COMMENT ON COLUMN pull_request.id IS 'id of pull request';