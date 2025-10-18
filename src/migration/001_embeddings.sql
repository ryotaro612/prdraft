CREATE TABLE pull_request (pull_request_id UUID, ID bigint, PRIMARY KEY(pull_request_id), UNIQUE (id));

COMMENT ON TABLE pull_request IS 'pull request metadata';
comment on COLUMN pull_request.id IS 'id of pull request';