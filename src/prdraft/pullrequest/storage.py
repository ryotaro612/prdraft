from contextlib import contextmanager
import duckdb


@contextmanager
def pull_request_storage(filepath: str):
    with duckdb.connect(filepath) as conn:
        yield _Client(conn)


class _Client:

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self._conn = conn
