from flask import Flask, render_template, request, redirect, url_for, flash
from collections import deque
import copy

app = Flask(__name__)
app.secret_key = "secure_key_123"


class Process:
    pid_counter = 1

    def __init__(self, arrival, burst):
        self.pid = f"P{Process.pid_counter}"
        self.arrival = int(arrival)
        self.burst = int(burst)
        self.reset()
        Process.pid_counter += 1

    def reset(self):
        self.remaining = self.burst
        self.last_executed = self.arrival


default_processes = [Process(3, 4), Process(5, 3), Process(2, 1), Process(6, 7)]
processes = [p for p in default_processes]


def reset_pids():
    Process.pid_counter = 1
    for i, p in enumerate(processes, 1):
        p.pid = f"P{i}"
        p.reset()


def fcfs_schedule(procs):
    # Create deep copies to avoid modifying original processes
    sorted_procs = sorted(
        [copy.deepcopy(p) for p in procs], key=lambda p: (p.arrival, int(p.pid[1:]))
    )
    time = 0
    gantt = []
    waiting_times = []

    for p in sorted_procs:
        if time < p.arrival:
            time = p.arrival
        start = time
        end = time + p.burst
        gantt.append({"pid": p.pid, "start": start, "end": end})
        waiting_times.append(start - p.arrival)
        time = end

    turnaround = [wt + p.burst for wt, p in zip(waiting_times, sorted_procs)]
    return gantt, waiting_times, turnaround


def rr_schedule(procs, quantum):
    # Create deep copies to avoid modifying original processes
    sorted_procs = sorted(
        [copy.deepcopy(p) for p in procs], key=lambda p: (p.arrival, int(p.pid[1:]))
    )
    for p in sorted_procs:
        p.reset()  # Ensure all processes start fresh

    queue = deque()
    time = 0
    gantt = []
    completion_times = {p.pid: 0 for p in sorted_procs}
    i = 0

    # Initialize queue with processes arriving at time 0
    while i < len(sorted_procs) and sorted_procs[i].arrival <= time:
        queue.append(sorted_procs[i])
        i += 1

    # Handle case when no processes arrive at time 0
    if not queue and i < len(sorted_procs):
        time = sorted_procs[i].arrival
        while i < len(sorted_procs) and sorted_procs[i].arrival <= time:
            queue.append(sorted_procs[i])
            i += 1

    while queue or i < len(sorted_procs):
        # If queue is empty but more processes will arrive
        if not queue and i < len(sorted_procs):
            time = sorted_procs[i].arrival
            while i < len(sorted_procs) and sorted_procs[i].arrival <= time:
                queue.append(sorted_procs[i])
                i += 1
            continue

        current = queue.popleft()

        if current.remaining <= 0:
            continue

        exec_time = min(quantum, current.remaining)
        start = time
        end = time + exec_time

        # Record execution in gantt chart
        gantt.append({"pid": current.pid, "start": start, "end": end})

        # Update process state
        current.remaining -= exec_time
        current.last_executed = end
        time = end

        # If process completes, record completion time
        if current.remaining <= 0:
            completion_times[current.pid] = time

        # Add newly arrived processes
        while i < len(sorted_procs) and sorted_procs[i].arrival <= time:
            queue.append(sorted_procs[i])
            i += 1

        # Re-add to queue if remaining time
        if current.remaining > 0:
            queue.append(current)

    # Calculate waiting and turnaround times
    waiting_times = []
    turnaround_times = []

    for p in sorted_procs:
        turnaround = completion_times[p.pid] - p.arrival
        waiting = turnaround - p.burst
        waiting_times.append(waiting)
        turnaround_times.append(turnaround)

    return gantt, waiting_times, turnaround_times


@app.route("/", methods=["GET", "POST"])
def index():
    global processes
    algorithm = request.args.get("algorithm", "fcfs")
    quantum = int(request.args.get("quantum", 2))

    if request.method == "POST":
        if "add_process" in request.form:
            try:
                arrival = request.form.get("arrival", "0")
                burst = request.form.get("burst", "1")

                arrival = int(arrival) if arrival else 0
                burst = int(burst) if burst else 1

                if arrival < 0 or burst < 1:
                    raise ValueError("Invalid input values")

                processes.append(Process(arrival, burst))
                reset_pids()

            except Exception as e:
                flash(f"Error: {str(e)}", "error")
            return redirect(url_for("index", algorithm=algorithm, quantum=quantum))

        elif "run_algorithm" in request.form:
            try:
                if not processes:
                    processes = [copy.deepcopy(p) for p in default_processes]
                    reset_pids()

                algorithm = request.form.get("algorithm", "fcfs")
                quantum = int(request.form.get("quantum", 2))

                if algorithm == "fcfs":
                    gantt, waiting, turnaround = fcfs_schedule(processes)
                else:
                    if quantum < 1:
                        quantum = 1
                        flash("Quantum set to minimum value (1)", "info")
                    gantt, waiting, turnaround = rr_schedule(processes, quantum)

                total_time = gantt[-1]["end"] if gantt else 0
                time_points = sorted(
                    {point for seg in gantt for point in [seg["start"], seg["end"]]}
                )

                return render_template(
                    "index.html",
                    processes=processes,
                    algorithm=algorithm,
                    quantum=quantum,
                    gantt=gantt,
                    time_points=time_points,
                    avg_wait=round(sum(waiting) / len(waiting), 2) if waiting else 0,
                    avg_turn=(
                        round(sum(turnaround) / len(turnaround), 2) if turnaround else 0
                    ),
                    total_time=total_time,
                )

            except Exception as e:
                flash(f"Scheduling error: {str(e)}", "error")
                return redirect(url_for("index", algorithm=algorithm, quantum=quantum))

    return render_template(
        "index.html", processes=processes, algorithm=algorithm, quantum=quantum
    )


@app.route("/reset", methods=["POST"])
def reset():
    global processes
    Process.pid_counter = 1
    processes = [Process(p.arrival, p.burst) for p in default_processes]
    reset_pids()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
