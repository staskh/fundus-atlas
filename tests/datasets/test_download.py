# ABOUTME: Tests for the chunked, resumable download every fetcher uses for large archives.
# ABOUTME: The transport is faked; what is tested is resuming, retrying and knowing when to stop.

import pytest

from datasets.utils import archives


class Server:
    """A range server that can be told to misbehave, standing in for a real one that does."""

    def __init__(self, payload, stall_after=None, fail_times=0):
        self.payload = payload
        self.stall_after = stall_after
        self.fail_times = fail_times
        self.requests = []

    def __call__(self, url, start, end):
        self.requests.append((start, end))
        if self.fail_times > 0:
            self.fail_times -= 1
            raise OSError("connection reset")
        chunk = self.payload[start : end + 1]
        if self.stall_after is not None and start >= self.stall_after:
            return b""
        return chunk

    def size(self, url):
        return len(self.payload)


def test_a_file_arrives_whole(tmp_path):
    server = Server(b"x" * 1000)
    archives.download("u", tmp_path / "f.bin", fetch=server, size_of=server.size, chunk=256)
    assert (tmp_path / "f.bin").read_bytes() == server.payload


def test_it_asks_for_the_file_in_chunks_rather_than_one_long_connection(tmp_path):
    server = Server(b"x" * 1000)
    archives.download("u", tmp_path / "f.bin", fetch=server, size_of=server.size, chunk=256)
    assert len(server.requests) == 4
    assert server.requests[0] == (0, 255)


def test_it_resumes_from_what_is_already_on_disk(tmp_path):
    server = Server(b"abcdefghij" * 100)
    partial = tmp_path / "f.bin"
    partial.write_bytes(server.payload[:600])
    archives.download("u", partial, fetch=server, size_of=server.size, chunk=200)
    assert partial.read_bytes() == server.payload
    assert server.requests[0][0] == 600


def test_a_complete_file_is_not_downloaded_again(tmp_path):
    server = Server(b"x" * 1000)
    done = tmp_path / "f.bin"
    done.write_bytes(server.payload)
    archives.download("u", done, fetch=server, size_of=server.size, chunk=256)
    assert server.requests == []


def test_a_dropped_connection_is_retried_rather_than_losing_the_download(tmp_path):
    server = Server(b"x" * 500, fail_times=2)
    archives.download(
        "u", tmp_path / "f.bin", fetch=server, size_of=server.size, chunk=256, pause=0
    )
    assert (tmp_path / "f.bin").read_bytes() == server.payload


def test_a_server_that_goes_quiet_is_given_up_on_rather_than_waited_for(tmp_path):
    # The failure that prompted this: a long connection to figshare accepted, then delivered
    # nothing for as long as it was left alone.
    server = Server(b"x" * 1000, stall_after=512)
    with pytest.raises(OSError, match="stopped sending"):
        archives.download(
            "u", tmp_path / "f.bin", fetch=server, size_of=server.size, chunk=256, pause=0
        )
    assert (tmp_path / "f.bin").stat().st_size == 512


def test_a_file_larger_than_the_one_it_claims_to_be_is_refused(tmp_path):
    # How this was found: a stray retry loop was appending to the same file as the downloader, and
    # the archive grew a third of a gigabyte past its real size while both processes called it
    # progress. A file that is too big is corrupt, and resuming from its end is meaningless.
    server = Server(b"x" * 1000)
    too_big = tmp_path / "f.bin"
    too_big.write_bytes(b"x" * 1500)
    with pytest.raises(ValueError, match="larger than"):
        archives.download("u", too_big, fetch=server, size_of=server.size)


def test_a_server_that_sends_more_than_it_was_asked_for_is_refused(tmp_path):
    class Overrunning(Server):
        def __call__(self, url, start, end):
            return self.payload[start:] * 2

    server = Overrunning(b"x" * 100)
    with pytest.raises(ValueError, match="more than"):
        archives.download(
            "u", tmp_path / "f.bin", fetch=server, size_of=server.size, chunk=50, pause=0
        )


def test_a_short_piece_is_continued_from_rather_than_treated_as_the_end(tmp_path):
    class Truncating(Server):
        def __call__(self, url, start, end):
            return self.payload[start : end + 1][:10]

    server = Truncating(b"abcdefghij" * 10)
    archives.download(
        "u", tmp_path / "f.bin", fetch=server, size_of=server.size, chunk=50, pause=0
    )
    assert (tmp_path / "f.bin").read_bytes() == server.payload
