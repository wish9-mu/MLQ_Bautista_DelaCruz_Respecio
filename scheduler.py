from collections import deque
from typing import List, Tuple, Dict, Any

from models import Proc


class MLFQSimulator:
    def __init__(self, rr_quantum: int, demote_units: int, aging_units: int, preempt_on_arrival: bool = True):
        self.quanta = [rr_quantum, rr_quantum, rr_quantum]
        self.demote_units = demote_units
        self.aging_units = aging_units
        self.preempt_on_arrival = preempt_on_arrival

    def simulate(self, processes: List[Tuple[str, int, int, int]]):
        procs: Dict[str, Proc] = {pid: Proc(pid, at, bt, pr) for pid, at, bt, pr in processes}
        arrivals = sorted(processes, key=lambda x: x[1])
        arr_idx, t = 0, 0

        ready = [deque() for _ in range(3)]
        timeline: List[Tuple[int, int, str, int]] = []  # (start, end, pid, q)

        def enqueue(p: Proc, qlevel=None, now=0):
            if qlevel is None:
                qlevel = p.queue
            p.queue = qlevel
            ready[qlevel].append(p.pid)
            p.last_ready_t = now

        def add_new_arrivals(now):
            nonlocal arr_idx
            while arr_idx < len(arrivals) and arrivals[arr_idx][1] <= now:
                pid, at, bt, pr = arrivals[arr_idx]
                enqueue(procs[pid], qlevel=max(0, min(2, pr - 1)), now=at)
                arr_idx += 1

        def highest_nonempty_queue():
            for qi in range(3):
                if ready[qi]:
                    return qi
            return None

        def age_ready(now):
            if self.aging_units <= 0:
                return
            for q in (1, 2):
                newdq = deque()
                while ready[q]:
                    pid = ready[q].popleft()
                    p = procs[pid]
                    waited = 0 if p.last_ready_t is None else (now - p.last_ready_t)
                    if waited >= self.aging_units and p.queue > 0:
                        p.queue -= 1
                        p.ran_in_level = 0
                        ready[p.queue].append(pid)
                        p.last_ready_t = now
                    else:
                        newdq.append(pid)
                ready[q] = newdq

        add_new_arrivals(0)

        while any(p.remaining > 0 for p in procs.values()):
            if not any(ready):
                if arr_idx < len(arrivals):
                    t = arrivals[arr_idx][1]
                    add_new_arrivals(t)
                    continue
                break

            q = highest_nonempty_queue()
            pid = ready[q].popleft()
            p = procs[pid]

            if p.last_ready_t is not None:
                p.waiting_time += t - p.last_ready_t
                p.last_ready_t = None
            if p.first_start is None:
                p.first_start = t

            quantum = self.quanta[q]
            run_start = t
            remaining_quantum = quantum
            preempted = False

            while remaining_quantum > 0 and p.remaining > 0:
                natural_end = t + min(remaining_quantum, p.remaining)
                delta = natural_end - t

                if arr_idx < len(arrivals):
                    next_at = arrivals[arr_idx][1]
                    if next_at < natural_end:
                        delta = next_at - t

                t += delta
                p.remaining -= delta
                p.ran_in_level += delta

                add_new_arrivals(t)
                age_ready(t)

                hi_q = highest_nonempty_queue()
                if self.preempt_on_arrival and hi_q is not None and hi_q < q and p.remaining > 0:
                    timeline.append((run_start, t, pid, q))
                    enqueue(p, qlevel=q, now=t)
                    preempted = True
                    break

                remaining_quantum -= delta

            if preempted:
                continue

            timeline.append((run_start, t, pid, q))

            if p.remaining == 0:
                p.completion = t
                p.ran_in_level = 0
            else:
                new_q = q
                if self.demote_units > 0 and p.ran_in_level >= self.demote_units and q < 2:
                    new_q = q + 1
                    p.ran_in_level = 0

                enqueue(p, qlevel=new_q, now=t)

        rows: List[Dict[str, Any]] = []
        for pid in sorted(procs, key=lambda s: int(s[1:]) if s[1:].isdigit() else s):
            p = procs[pid]
            rows.append({
                "PID": pid,
                "Arrival": p.arrival,
                "Burst": p.burst,
                "Priority": p.priority,
                "FirstStart": p.first_start,
                "Completion": p.completion,
                "Turnaround": None if p.completion is None else p.completion - p.arrival,
                "Waiting": p.waiting_time,
                "Response": None if p.first_start is None else p.first_start - p.arrival
            })

        return timeline, rows


