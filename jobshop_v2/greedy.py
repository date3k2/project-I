from typing import List, Tuple
from collections import defaultdict


class GreedyJS:
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

    def solve(self):
        # Define all tasks in the problem
        all_tasks = set.union(*[set(i) for i in self.tasks])
        # Define a dict of tasks including what machine can do the task
        self.task_machines = defaultdict()
        self.min_cost_for_task = defaultdict(lambda: float("inf"))
        for taskJ in all_tasks:
            for machine in self.capacities:
                for taskM in self.capacities[machine]:
                    if taskJ == taskM:
                        if (
                            self.min_cost_for_task[taskJ]
                            > self.capacities[machine][taskM][1]
                        ):
                            self.task_machines[taskJ] = (
                                machine,
                                self.capacities[machine][taskM][0],
                            )
                            self.min_cost_for_task[taskJ] = self.capacities[machine][
                                taskM
                            ][1]

        # Define a dict of start time for each task of each job
        self.start_vars = [defaultdict(int) for _ in range(self.n_jobs)]
        self.last_end_time = defaultdict(int)
        # Assign with greedy algorithm
        for job in range(self.n_jobs):
            order = defaultdict(list)
            for task1, task2 in self.orders[job]:
                order[task1].append(task2)
            for task in self.tasks[job]:
                self.start_vars[job][task] = max(
                    self.start_vars[job][task],
                    self.last_end_time[self.task_machines[task][0]],
                )
                for subsequent_task in order[task]:
                    self.start_vars[job][subsequent_task] = (
                        self.start_vars[job][task] + self.task_machines[task][1]
                    )
            for task in self.tasks[job]:
                self.last_end_time[self.task_machines[task][0]] = (
                    self.start_vars[job][task] + self.task_machines[task][1]
                )
        print("Solution for greedy algorithm:")
        for job in range(self.n_jobs):
            for task in self.tasks[job]:
                print(
                    "Job %d task %d starts at %.2f and ends at %.2f on machine %d"
                    % (
                        job,
                        task,
                        self.start_vars[job][task],
                        self.start_vars[job][task] + self.task_machines[task][1],
                        self.task_machines[task][0],
                    )
                )
        print()
