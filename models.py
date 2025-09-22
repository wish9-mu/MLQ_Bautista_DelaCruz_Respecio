from dataclasses import dataclass, field

# ---------- Defaults ----------
DEFAULT_PROCESSES = [
    ("P1",  1, 20, 3),
    ("P2",  3, 10, 2),
    ("P3",  5,  2, 1),
    ("P4",  8,  7, 2),
    ("P5", 11, 15, 3),
    ("P6", 15,  8, 2),
    ("P7", 20,  4, 1),
]
DEFAULT_RR_QUANTUM = 3
DEFAULT_DEMOTE_UNITS = 6       # cumulative CPU at level before demotion
DEFAULT_AGING_UNITS  = 5


# ---------- Data ----------
@dataclass
class Proc:
    pid: str
    arrival: int
    burst: int
    priority: int          # 1..3 (1 highest)
    remaining: int = field(init=False)
    queue: int = field(init=False)         # 0..2 (0 highest)
    ran_in_level: int = field(default=0)   # CPU consumed since entering current level
    first_start: int = field(default=None)
    completion: int = field(default=None)
    waiting_time: int = field(default=0)
    last_ready_t: int = field(default=None)

    def __post_init__(self):
        self.remaining = self.burst
        self.queue = max(0, min(2, self.priority - 1))


