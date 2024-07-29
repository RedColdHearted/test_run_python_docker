import dataclasses


@dataclasses.dataclass(frozen=True)
class TestResult:
    order: int
    status: str
    result: str | None = None
    error_massage: str | None = None
    completed_time: int | None = None
    used_memory: int | None = None
