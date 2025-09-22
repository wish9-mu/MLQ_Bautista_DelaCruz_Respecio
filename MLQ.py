from models import DEFAULT_PROCESSES, DEFAULT_RR_QUANTUM, DEFAULT_DEMOTE_UNITS, DEFAULT_AGING_UNITS
from io_utils import read_line, read_int_or_default, read_yes_no_default
from scheduler import MLFQSimulator


def main():
    print("=== MLFQ Simulator (defaults on empty input) ===\n")

    n_str = read_line("How many processes? (Enter for defaults: 7) ").strip()
    if n_str == "":
        processes = DEFAULT_PROCESSES[:]
        print("Using default processes.\n")
    else:
        try:
            n = int(n_str)
        except ValueError:
            n = len(DEFAULT_PROCESSES)
            print(f"Invalid number; using defaults: {n}")
        processes = []
        print("\nEnter process details. Press Enter to accept shown defaults (if any).")
        for i in range(1, n + 1):
            pid = f"P{i}"
            d = DEFAULT_PROCESSES[i-1] if i-1 < len(DEFAULT_PROCESSES) else None
            at = read_int_or_default(
                f"  {pid} arrival time [{d[1]}]: " if d else f"  {pid} arrival time: ",
                default=(d[1] if d else 0), min_val=0)
            bt = read_int_or_default(
                f"  {pid} burst time [{d[2]}]: " if d else f"  {pid} burst time: ",
                default=(d[2] if d else 1), min_val=1)
            pr = read_int_or_default(
                f"  {pid} priority 1-3 [{d[3]}]: " if d else f"  {pid} priority 1-3: ",
                default=(d[3] if d else 3), min_val=1, max_val=3)
            processes.append((pid, at, bt, pr))
        print()

    rrq = read_int_or_default(
        f"Round Robin quantum for Q0/Q1/Q2 [default {DEFAULT_RR_QUANTUM}]: ",
        default=DEFAULT_RR_QUANTUM, min_val=1)

    demote_units = read_int_or_default(
        f"Decrease lower priority after this many CPU units at a level [default {DEFAULT_DEMOTE_UNITS}]: ",
        default=DEFAULT_DEMOTE_UNITS, min_val=1)

    aging_units = read_int_or_default(
        f"Increase priority (aging) after this many waiting units [default {DEFAULT_AGING_UNITS}]: ",
        default=DEFAULT_AGING_UNITS, min_val=0)

    preempt = read_yes_no_default("Preempt when higher-priority work arrives?", default=True)

    print("\nSimulating...\n")
    sim = MLFQSimulator(rr_quantum=rrq, demote_units=demote_units, aging_units=aging_units, preempt_on_arrival=preempt)
    timeline, rows = sim.simulate(processes)

    print("Gantt Timeline (start-end:PID@Q):")
    print(" | ".join(f"{s}-{e}:{pid}@Q{q}" for (s, e, pid, q) in timeline) or "(empty)")

    print("\nPer-Process Metrics:")
    header = ["PID", "Arrival", "Burst", "Priority", "FirstStart", "Completion", "Turnaround", "Waiting", "Response"]
    print(" | ".join(f"{h:>11}" for h in header))
    for r in rows:
        print(" | ".join(f"{str(r[h]):>11}" for h in header))

    finished = [r for r in rows if r["Completion"] is not None]
    if finished:
        avg_wait = sum(r["Waiting"] for r in finished) / len(finished)
        avg_tt = sum(r["Turnaround"] for r in finished) / len(finished)
        avg_resp = sum(r["Response"] for r in finished) / len(finished)
        makespan = max(r["Completion"] for r in finished) - min(r["Arrival"] for r in finished)
        total_burst = sum(r["Burst"] for r in finished)
        util = (total_burst / makespan) * 100 if makespan else 100.0
        print(f"\nAverages → Waiting: {avg_wait:.2f}, Turnaround: {avg_tt:.2f}, Response: {avg_resp:.2f}")
        print(f"CPU Utilization: {util:.2f}%")


if __name__ == "__main__":
    main()
