from dataclasses import dataclass


@dataclass(frozen=True)
class ParseLimits:
    max_lines: int = 1_000_000
    max_line_length: int = 65_536
    max_apertures: int = 100_000
    max_objects: int = 5_000_000
    max_aperture_macros: int = 100_000
    max_tools: int = 100_000

    def check_line(self, line: str, number: int) -> None:
        if number > self.max_lines:
            raise ValueError("input exceeds maximum line count")
        if len(line) > self.max_line_length:
            raise ValueError("input line exceeds maximum length")

    def check_text(self, text: str) -> None:
        """Validate physical line count/length without materializing split lines."""
        start = 0
        number = 1
        length = len(text)
        while start < length:
            end = text.find("\n", start)
            if end < 0:
                line = text[start:]
                if line.endswith("\r"):
                    line = line[:-1]
                self.check_line(line, number)
                return

            line = text[start:end]
            if line.endswith("\r"):
                line = line[:-1]
            self.check_line(line, number)
            number += 1
            start = end + 1

    def check_apertures(self, count: int) -> None:
        if count > self.max_apertures:
            raise ValueError("input exceeds maximum aperture count")

    def check_aperture_macros(self, count: int) -> None:
        if count > self.max_aperture_macros:
            raise ValueError("input exceeds maximum aperture-macro count")

    def check_tools(self, count: int) -> None:
        if count > self.max_tools:
            raise ValueError("input exceeds maximum tool count")

    def check_objects(self, count: int) -> None:
        if count > self.max_objects:
            raise ValueError("input exceeds maximum object count")
