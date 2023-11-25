from typing import List
from ortools.sat.colab import visualization


class JobShopBase:
    def __init__(self, durations: List[List[int]], machines: List[List[int]]):
        self.durations = durations
        self.machines = machines
        self.n_jobs = len(durations)
        self.n_machines = len(durations[0])
        self.horizon = sum(sum(durations, []))
        self.all_jobs = range(self.n_jobs)
        self.all_machines = range(self.n_machines)
        self.makespan = -1
        self.addConstraints()

    def display(self, status: str, starts: List[List[int]], obj: int):
        if obj > 0:
            print(f"{status} : {obj}")
            visualization.DisplayJobshop(
                starts, self.durations, self.machines, self.__class__.__name__
            )
        else:
            print("No solution found !")

    def addConstraints(self):
        pass

    def solve(self, display=False):
        return self.makespan

    def summary(self):
        pass
