from __future__ import annotations

from collections.abc import Iterator


def iter_gerber_statements(text: str) -> Iterator[tuple[int, str]]:
    """Yield RS-274X statements without assuming one command per line.

    Extended parameter blocks are delimited by percent signs and may contain
    internal '*' separators (notably aperture macros). Normal commands are
    terminated by '*'. The returned line number is the physical source line
    where the statement begins, preserving useful provenance/diagnostics.
    """

    i = 0
    line = 1
    n = len(text)

    while i < n:
        while i < n and text[i].isspace():
            if text[i] == "\n":
                line += 1
            i += 1

        if i >= n:
            break

        start_line = line

        if text[i] == "%":
            end = text.find("%", i + 1)
            if end < 0:
                raw = text[i:]
                i = n
            else:
                raw = text[i : end + 1]
                i = end + 1
        else:
            end = text.find("*", i)
            if end < 0:
                raw = text[i:]
                i = n
            else:
                raw = text[i : end + 1]
                i = end + 1

        line += raw.count("\n")
        statement = raw.replace("\r", "").replace("\n", "").strip()
        if statement:
            yield start_line, statement
