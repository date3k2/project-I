from ortools.linear_solver import pywraplp
from typing import List, Tuple
from collections import defaultdict
import plotly.figure_factory as ff
import datetime


def ToDate(now, mins):
    return (now + datetime.timedelta(minutes=mins)).strftime("%Y-%m-%d %H:%M:%S")


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

    def assign(self):
        V = 1_000_000
        # Define all tasks in the problem
        all_tasks = set.union(*[set(i) for i in self.tasks])
        # Define a dict of tasks including what machine can do the task
        self.task_machines = defaultdict()
        self.min_cost_for_task = defaultdict(lambda: float("inf"))
        for taskJ in all_tasks:
            for machine in self.capacities:
                for taskM in self.capacities[machine]:
                    if taskJ == taskM:
                        if self.min_cost_for_task[taskJ] > self.capacities[machine][taskM][1]:
                            self.task_machines[taskJ] = machine
                            self.min_cost_for_task[taskJ] = self.capacities[machine][taskM][1]

    def solve(self, display=True):
        pass
