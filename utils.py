import dataclasses


@dataclasses.dataclass(frozen=True)
class TestResult:
    """Represent test result dataclass."""
    order: int
    status: str
    comparison: str | None = None
    error_massage: str | None = None
    completed_time: int | None = None
    used_memory: int | None = None


@dataclasses.dataclass(frozen=True)
class TestCase:
    """Represent test case dataclass."""
    code_line: str
    allocated_time: int | None = None
    allocated_memory: int | None = None
