from .base import JobShopBase
from ortools.sat.python import cp_model
from collections import namedtuple
from typing import List


class CPModel(JobShopBase):
    def __init__(self, durations: List[List[int]], machines: List[List[int]]):
        super().__init__(durations, machines)
        self.model = cp_model.CpModel()
        self.starts = None
        self.all_tasks = {}
        self.addConstraints()

    def addConstraints(self):
        task_type = namedtuple("task_type", "start end interval")

        """
        Ràng buộc thời gian bắt đầu và kết thúc của mỗi task.
        Điều kiện : 
            - Thời gian bắt đầu và kết thúc của mỗi task phải thỏa mãn điều kiện : 0 <= start <= end <= horizon
            -  start + duration = end
        """
        for i in self.all_jobs:
            for j in self.all_machines:
                start_var = self.model.NewIntVar(
                    0, self.horizon, "start_%i_%i" % (i, j)
                )
                duration = self.durations[i][j]
                end_var = self.model.NewIntVar(0, self.horizon, "end_%i_%i" % (i, j))
                interval_var = self.model.NewIntervalVar(
                    start_var, duration, end_var, "interval_%i_%i" % (i, j)
                )
                self.all_tasks[(i, j)] = task_type(
                    start=start_var, end=end_var, interval=interval_var
                )

        """
        Ràng buộc mỗi máy chỉ được thực hiện một task tại một thời điểm.
        """
        machine_to_jobs = {}
        for i in self.all_machines:
            machines_jobs = []
            for j in self.all_jobs:
                for k in self.all_machines:
                    if (
                        self.machines[j][k] == i
                    ):  # Tìm tất cả các task cần thực hiện trên máy i
                        machines_jobs.append(self.all_tasks[(j, k)].interval)
            machine_to_jobs[i] = machines_jobs
            # Mỗi máy chỉ được thực hiện một task tại một thời điểm (các khoảng thời gian không được chồng lấn lên nhau)
            self.model.AddNoOverlap(machines_jobs)

        """
        Ràng buộc tuần tự công nghệ: 
            Với mỗi task của job, thời gian bắt đầu của task tiếp theo phải >= thời gian kết thúc của task trước đó.
        """
        for i in self.all_jobs:
            for j in range(0, self.n_machines - 1):
                self.model.Add(
                    self.all_tasks[(i, j + 1)].start >= self.all_tasks[(i, j)].end
                )

        """
        Mục tiêu cần tối ưu:
            Tìm thời gian hoàn thành của job cuối cùng (makespan) là nhỏ nhất.
        """
        self.obj_var = self.model.NewIntVar(0, self.horizon, "makespan")
        self.model.AddMaxEquality(
            self.obj_var,
            [self.all_tasks[(i, self.n_machines - 1)].end for i in self.all_jobs],
        )  # Thời gian lớn nhất để hoàn thành task cuối cùng của tất cả các job chính là thời gian hoàn thành tất cả các jobs (makespan)
        self.model.Minimize(self.obj_var)

    def solve(self, max_time_in_seconds=60.0):
        self.solver = cp_model.CpSolver()
        self.solver.parameters.log_search_progress = True
        self.solver.parameters.max_time_in_seconds = max_time_in_seconds
        status = self.solver.Solve(self.model)
        stt = makespan = None
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            stt = self.solver.StatusName(status)
            makespan = self.solver.ObjectiveValue()
            self.starts = [
                [self.solver.Value(self.all_tasks[(i, j)][0]) for j in self.all_machines]
                for i in self.all_jobs
            ]
        # # Print sequences of jobs assigned to each machine.
        # starts = [
        #     [(starts[i][j], machines[i][j]) for j in all_machines] for i in all_jobs
        # ]
        # starts = [sorted(job, key=lambda x: x[1]) for job in starts]
        # job_sq = []
        # for start in zip(*starts):
        #     start_job = sorted(
        #         [(i, j[0]) for i, j in enumerate(start)], key=lambda x: x[1]
        #     )
        #     job_sq.append([i[0] for i in start_job])
        # print()
        # print("Optimal job sequence: ")
        # for i in job_sq:
        #     print(*i)
        else:
            stt = self.solver.StatusName(status)
            makespan = 0
        self.display(stt, self.starts, makespan)

    def summary(self):
        print("Constraint programming model summary: ")
        print(self.solver.ResponseStats())
        print(self.solver.SolutionInfo())

