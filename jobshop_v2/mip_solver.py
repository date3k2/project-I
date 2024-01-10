from ortools.linear_solver import pywraplp
from typing import List, Tuple
from collections import defaultdict
from baseJS import BaseJS, ToDate
from datetime import datetime


class LPJS(BaseJS):
    def __init__(
        self,
        tasks: List[List[int]],
        orders: List[List[Tuple[int, int]]],
        capacities: dict,
        times: List[int]
    ):
        super().__init__(tasks, orders, capacities, times)
        self.model = pywraplp.Solver(
            "JSSP", pywraplp.Solver.SCIP_MIXED_INTEGER_PROGRAMMING
        )

    def addConstraints(self):
        V = 1_000_000
        # Define a dict of start time for each task of each job
        self.start_vars = [defaultdict() for _ in range(self.n_jobs)]
        # Define a dict of tasks including what machine can do the task
        all_tasks = set.union(*[set(i) for i in self.tasks])
        self.task_machines = defaultdict(dict)
        for taskJ in all_tasks:
            for machine in self.capacities:
                for taskM in self.capacities[machine]:
                    if taskJ == taskM:
                        self.task_machines[taskJ][machine] = self.capacities[machine][
                            taskM
                        ]
                        break
        # Define variables for assigning task of each job to each machine
        self.assignment_task = defaultdict(list)
        assignment_machine = defaultdict(list)
        for job in range(self.n_jobs):
            for task in self.tasks[job]:
                self.start_vars[job][task] = self.model.NumVar(
                    0, V, f"start_job_{job}_task_{task}"
                )
                for machine in self.task_machines[task]:
                    decision_var = self.model.BoolVar(
                        f"job_{job}_task_{task}_machine_{machine}"
                    )
                    self.assignment_task[(job, task)].append(
                        (decision_var, machine,
                         self.task_machines[task][machine][1])
                    )
                    assignment_machine[machine].append(
                        (decision_var, job, task))
                self.model.Add(
                    sum(des for des, _,
                        _ in self.assignment_task[(job, task)]) == 1
                )  # Each task must be assigned to one machine

        # Orders constraint
        for job, order in enumerate(self.orders):
            for task1, task2 in order:
                for dec_var, machine, _ in self.assignment_task[(job, task1)]:
                    self.model.Add(
                        self.start_vars[job][task1]
                        + self.task_machines[task1][machine][0]
                        <= self.start_vars[job][task2] + V * (1 - dec_var)
                    )

        # A machine can only perform one task at a time
        precedence = defaultdict()
        for machine in assignment_machine:
            for i, job1, task1 in assignment_machine[machine]:
                for j, job2, task2 in assignment_machine[machine]:
                    if i.name() != j.name():
                        precedence[
                            (machine, job1, task1, job2, task2)
                        ] = self.model.BoolVar(
                            f"machine_{machine}_job_{job1}_task_{task1}_job_{job2}_task_{task2}"
                        )
        for machine in assignment_machine:
            for idx, (i, job1, task1) in enumerate(assignment_machine[machine]):
                for j, job2, task2 in assignment_machine[machine][idx + 1:]:
                    self.model.Add(
                        precedence[(machine, job1, task1, job2, task2)]
                        + precedence[(machine, job2, task2, job1, task1)]
                        == 1
                    )

        for machine in assignment_machine:
            for i, job1, task1 in assignment_machine[machine]:
                for j, job2, task2 in assignment_machine[machine]:
                    if i.name() != j.name():
                        self.model.Add(
                            self.start_vars[job1][task1]
                            + self.task_machines[task1][machine][0]
                            <= self.start_vars[job2][task2]
                            + V
                            * (
                                3
                                - precedence[(machine, job1,
                                              task1, job2, task2)]
                                - i
                                - j
                            )
                        )
        # Minimize cost
        weight = sum(len(i) for i in self.tasks)
        self.model.Minimize(
            sum(
                cost * decision_var
                for job in range(self.n_jobs)
                for task in self.tasks[job]
                for decision_var, _, cost in self.assignment_task[(job, task)]
            )
            # add cost of delay
            + sum(
                self.start_vars[job][task]
                for job in range(self.n_jobs)
                for task in self.tasks[job]
            ) / weight
        )

    def solve(self, display=True, max_time_in_seconds=10):
        self.addConstraints()
        finished_time = 0  # time when all tasks are finished
        print("Vui lòng chờ trong giây lát...\n")
        self.model.set_time_limit(max_time_in_seconds * 1000)
        status = self.model.Solve()
        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            print("Solution for MIP Model:")
            df = []
            # round current time to minute
            current_time = datetime.now().replace(second=0, microsecond=0)
            start_of_batch = 0
            min_times = min(self.times)
            times = [i - min_times for i in self.times]
            for time in range(min_times):
                start_of_batch = finished_time
                for job in range(self.n_jobs):
                    for task in self.tasks[job]:
                        start = (
                            self.start_vars[job][task].solution_value()
                            if self.start_vars[job][task].solution_value() < 1e6
                            else 0
                        )
                        for des, machine, _ in self.assignment_task[(job, task)]:
                            if des.solution_value() == 1:
                                print(
                                    "%d.Job %d task %d starts at %.2f and ends at %.2f on machine %d costs %.2f"
                                    % (
                                        time,
                                        job,
                                        task,
                                        start + start_of_batch,
                                        start +
                                        self.task_machines[task][machine][0] +
                                        start_of_batch,
                                        machine,
                                        self.task_machines[task][machine][1]
                                    )
                                )
                                finished_time = max(
                                    finished_time, start + self.task_machines[task][machine][0] + start_of_batch)
                                df.append(
                                    dict(
                                        Task="Machine %i" % machine,
                                        Start=ToDate(
                                            current_time, start + start_of_batch),
                                        Finish=ToDate(
                                            current_time,
                                            start +
                                            self.task_machines[task][machine][0] +
                                            start_of_batch,
                                        ),
                                        Machine="Task %i" % task,
                                    )
                                )
            for job in range(self.n_jobs):
                for time in range(min_times, min_times + times[job]):
                    start_of_batch = finished_time
                    for task in self.tasks[job]:
                        start = (
                            self.start_vars[job][task].solution_value()
                            if self.start_vars[job][task].solution_value() < 1e6
                            else 0
                        )
                        for des, machine, _ in self.assignment_task[(job, task)]:
                            if des.solution_value() == 1:
                                print(
                                    "%d.Job %d task %d starts at %.2f and ends at %.2f on machine %d costs %.2f"
                                    % (
                                        time,
                                        job,
                                        task,
                                        start_of_batch,
                                        self.task_machines[task][machine][0] +
                                        start_of_batch,
                                        machine,
                                        self.task_machines[task][machine][1]
                                    )
                                )
                                finished_time = max(
                                    finished_time, self.task_machines[task][machine][0] + start_of_batch)
                                df.append(
                                    dict(
                                        Task="Machine %i" % machine,
                                        Start=ToDate(
                                            current_time, start + start_of_batch),
                                        Finish=ToDate(
                                            current_time,
                                            start +
                                            self.task_machines[task][machine][0] +
                                            start_of_batch,
                                        ),
                                        Machine="Task %i" % task,
                                    )
                                )
            print()
            print("Finished time: %.2f" % finished_time)
            print("Total cost: %.2f" % sum(
                cost * decision_var.solution_value() * self.times[job]
                for job in range(self.n_jobs)
                for task in self.tasks[job]
                for decision_var, _, cost in self.assignment_task[(job, task)]
            ))
            if display:
                self.plot(df)
        else:
            print("No solution found.")


if __name__ == "__main__":
    tasks = [(1, 17, 2, 3), [1, 26, 3, 7, 5, 6], [1, 24, 3]]
    orders = [
        [(1, 17), (17, 2), (2, 3)],
        [(1, 26), (26, 3), (3, 7), (7, 5)],
        [(1, 24), (24, 3)],
    ]
    times = [50, 6, 10]
    capacities = defaultdict(dict,
                             {1: {18: (6.61, 3.11),
                                  12: (6.1, 2.73),
                                  19: (9.04, 4.25),
                                  17: (3.64, 7.35)},
                                 2: {32: (6.49, 7.88), 17: (3.98, 2.22)},
                                 3: {6: (2.85, 5.1)},
                                 4: {2: (4.34, 1.6)},
                                 5: {3: (0.28, 1.83), 4: (3.39, 8.33)},
                                 6: {17: (9.7, 4.35)},
                                 7: {12: (9.42, 5.49),
                                     19: (2.96, 7.61),
                                     32: (6.18, 4.53),
                                     27: (4.67, 7.27)},
                                 8: {5: (2.76, 6.22)},
                                 9: {5: (7.51, 5.6)},
                                 10: {18: (9.59, 1.21),
                                      12: (1.3, 6.67),
                                      19: (5.73, 0.66),
                                      28: (3.76, 4.06),
                                      29: (3.54, 8.28)},
                                 11: {17: (3.72, 3.08),
                                      28: (0.5, 6.45),
                                      29: (6.9, 4.95),
                                      12: (1.94, 6.69),
                                      26: (7.33, 5.05)},
                                 12: {26: (3.34, 0.19),
                                      27: (6.66, 4.82),
                                      28: (4.85, 5.65),
                                      29: (0.66, 1.47)},
                                 13: {12: (6.16, 6.83), 28: (6.35, 4.78), 17: (3.45, 5.27)},
                                 14: {13: (3.11, 6.26), 20: (6.05, 4.34), 21: (5.1, 0.74)},
                                 15: {24: (5.45, 5.35), 25: (0.44, 7.32)},
                                 16: {24: (2.23, 8.07), 30: (3.76, 1.98), 31: (4.92, 9.68)},
                                 17: {14: (5.24, 9.53), 15: (9.7, 2.86), 16: (9.01, 1.15)},
                                 18: {24: (9.16, 2.51), 30: (0.82, 5.94), 31: (2.69, 4.23)},
                                 19: {22: (0.78, 2.74), 23: (9.2, 1.46)},
                                 20: {10: (0.46, 3.95)},
                                 21: {11: (1.92, 8.74)},
                                 22: {7: (5.0, 4.29)},
                                 23: {9: (4.8, 3.64)},
                                 24: {8: (6.11, 3.29)},
                                 25: {1: (2.16, 1.76)},
                                 26: {1: (4.03, 5.15)},
                                 27: {7: (6.59, 0.77)},
                                 28: {7: (3.29, 9.94)},
                                 29: {14: (0.24, 6.68), 15: (3.93, 2.08)},
                                 30: {20: (4.11, 8.26), 21: (9.67, 3.39)}})
    lpjs = LPJS(tasks, orders, capacities, times)
    lpjs.solve(display=False)
