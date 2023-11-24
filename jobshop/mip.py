from typing import List
from .base import JobShopBase
from ortools.linear_solver import pywraplp


class MIPModel(JobShopBase):
    def __init__(self, durations: List[List[int]], machines: List[List[int]]):
        super().__init__(durations, machines)
        self.model = pywraplp.Solver(
            "JSSP", pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING
        )
        self.starts = {}
        self.addConstraints()

    def addConstraints(self):
        """
        Khởi tạo biến bắt đầu thời gian thực hiện mỗi task trên mỗi máy, là các biến nguyên không âm.
        """
        for i in self.all_jobs:
            for j in self.all_machines:
                self.starts[(i, j)] = self.model.IntVar(
                    0, self.horizon, "start_%i_%i" % (i, j)
                )

        """
        Ràng buộc các task phải được thực hiện tuần tự.
        """
        for i in self.all_jobs:
            for j in range(self.n_machines - 1):
                self.model.Add(
                    self.starts[(i, j)] + self.durations[i][j]
                    <= self.starts[(i, j + 1)]
                )

        """
        Ràng buộc mỗi máy chỉ thực hiện một task tại một thời điểm.
        """
        # Tìm tập các task được thực hiện trên mỗi máy.
        machine_to_jobs = {}
        for i in self.all_machines:
            machines_jobs = []
            for j in self.all_jobs:
                for k in self.all_machines:
                    if self.machines[j][k] == i:
                        machines_jobs.append((j, k))
            machine_to_jobs[i] = machines_jobs
        # Tạo biến nhị phân để chỉ ra task nào được thực hiện trước task nào trên mỗi máy.
        precedence = {}
        for i in self.all_machines:
            for j in machine_to_jobs[i]:
                for k in machine_to_jobs[i]:
                    if j[0] != k[0]:
                        precedence[(j, k)] = self.model.BoolVar(
                            "precedence_%i(%i)_%i(%i)" % (j + k)
                        )
        # Ràng buộc 2 task liên tiếp trên mỗi máy phải được thực hiện tuần tự (tổng các biến nhị phân = 1).
        for i in self.all_machines:
            for j in range(len(machine_to_jobs[i]) - 1):
                for k in range(j + 1, len(machine_to_jobs[i])):
                    self.model.Add(
                        precedence[(machine_to_jobs[i][j], machine_to_jobs[i][k])]
                        + precedence[(machine_to_jobs[i][k], machine_to_jobs[i][j])]
                        == 1
                    )
        # Với mỗi task thực hiện trước, gán ràng buộc về thời gian để các task không bị trùng thời gian.
        V = 1_000_000
        for i in self.all_machines:
            for j in machine_to_jobs[i]:
                for k in machine_to_jobs[i]:
                    if j[0] != k[0]:
                        self.model.Add(
                            self.starts[j] + self.durations[j[0]][j[1]]
                            <= self.starts[k] + V * (1 - precedence[(j, k)])
                        )
        """
        Khởi tạo biến mục tiêu và ràng buộc.
        """
        obj_var = self.model.IntVar(0, self.horizon, "makespan")
        for i in self.all_jobs:
            self.model.Add(
                obj_var
                >= self.starts[(i, self.n_machines - 1)]
                + self.durations[i][self.n_machines - 1]
            )
        self.model.Minimize(obj_var)

    def solve(self, max_time_in_seconds=60):
        self.model.set_time_limit(max_time_in_seconds * 1000)
        status = self.model.Solve()
        makespan = None
        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            makespan = self.model.Objective().Value()
            start = [[0] * self.n_machines for _ in self.all_jobs]
            for i in self.all_jobs:
                for j in self.all_machines:
                    start[i][j] = self.starts[(i, j)].solution_value()
        else:
            makespan = 0
        if status == pywraplp.Solver.OPTIMAL:
            status = "OPTIMAL"
        elif status == pywraplp.Solver.FEASIBLE:
            status = "FEASIBLE"
        self.display(status, start, makespan)

    def summary(self):
        print("Mixed Integer Programming (MIP) model summary:")
        print(self.model.NumConstraints(), "constraints")
        print(self.model.NumVariables(), "variables")
        print(self.model.WallTime(), "ms")
