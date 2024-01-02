from ortools.linear_solver import pywraplp
from typing import List, Tuple
from collections import defaultdict
import plotly.figure_factory as ff
import datetime


def ToDate(now, mins):
    return (now + datetime.timedelta(minutes=mins)).strftime("%Y-%m-%d %H:%M:%S")


class LPJS:
    def __init__(
        self,
        tasks: List[List[int]],
        orders: List[List[Tuple[int, int]]],
        capacities: dict,
    ):
        self.tasks = tasks
        self.orders = orders
        self.capacities = capacities
        self.n_jobs = len(tasks)
        self.model = pywraplp.Solver(
            "JSSP", pywraplp.Solver.SCIP_MIXED_INTEGER_PROGRAMMING
        )

    def addConstraints(self):
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
        V = 1_000_000
        self.assignment_task = defaultdict(list)
        assignment_machine = defaultdict(list)
        for job in range(self.n_jobs):
            for task in self.tasks[job]:
                self.start_vars[job][task] = self.model.NumVar(
                    0, self.model.infinity(), f"start_job_{job}_task_{task}"
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
                            f"machine_{machine}_job_{job1}_task_{
                                task1}_job_{job2}_task_{task2}"
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
        self.model.Minimize(
            sum(
                cost * decision_var
                for job in range(self.n_jobs)
                for task in self.tasks[job]
                for decision_var, _, cost in self.assignment_task[(job, task)]
            )
        )

    def solve(self, display=True):
        self.addConstraints()
        status = self.model.Solve()
        if status == pywraplp.Solver.OPTIMAL:
            print("Solution:")
            print("Objective value = ", self.model.Objective().Value())
            df = []
            # round current time to minute
            current_time = datetime.datetime.now().replace(second=0, microsecond=0)
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
                                "Job %d task %d starts at %.2f and ends at %.2f on machine %d"
                                % (
                                    job,
                                    task,
                                    start,
                                    start +
                                    self.task_machines[task][machine][0],
                                    machine
                                )
                            )
                            df.append(
                                dict(
                                    Task="Machine %i" % machine,
                                    Start=ToDate(current_time, start),
                                    Finish=ToDate(
                                        current_time,
                                        start +
                                        self.task_machines[task][machine][0],
                                    ),
                                    Machine="Task %i" % task,
                                )
                            )
            if display:
                sorted_df = sorted(df, key=lambda k: k["Task"])
                fig = ff.create_gantt(
                    sorted_df,
                    index_col="Machine",
                    title=" Gantt Chart",
                    show_colorbar=True,
                    showgrid_x=True,
                    showgrid_y=True,
                    group_tasks=True,
                )
                fig.show()
