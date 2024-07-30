import dataclasses
import abc

# TODO: protocol or abc
class Language:


@dataclasses.dataclass(frozen=True)
class TestResult:
    order: int
    status: str
    result: str | None = None
    error_massage: str | None = None
    completed_time: int | None = None
    used_memory: int | None = None


@dataclasses.dataclass(frozen=True)
class TestCase:
    code_line: str
    language: Language
    allocated_time: int | None = None
    allocated_memory: int | None = None
