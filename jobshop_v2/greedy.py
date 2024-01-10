from typing import List, Tuple
from collections import defaultdict
from baseJS import BaseJS, ToDate
from datetime import datetime


class GreedyJS(BaseJS):
    def __init__(
        self,
        tasks: List[List[int]],
        orders: List[List[Tuple[int, int]]],
        capacities: dict,
        times: List[int],
    ):
        super().__init__(tasks, orders, capacities, times)

    def solve(self, display=True, max_time_in_seconds=0):
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
        self.start_vars = defaultdict(float)
        self.last_end_time = defaultdict(int)
        # Assign with greedy algorithm : Assign task to machine with minimum cost
        for job in range(self.n_jobs):
            for time in range(self.times[job]):
                order = defaultdict(list)
                for task1, task2 in self.orders[job]:
                    order[task1].append(task2)
                for task in self.tasks[job]:
                    self.start_vars[(job, task, time)] = max(
                        self.start_vars[(job, task, time - 1)]
                        + self.task_machines[task][1]
                        if time > 0
                        else 0,
                        self.start_vars[(job, task, time)],
                        self.last_end_time[self.task_machines[task][0]],
                    )
                    for subsequent_task in order[task]:
                        self.start_vars[(job, subsequent_task, time)] = (
                            self.start_vars[(job, task, time)]
                            + self.task_machines[task][1]
                        )
                for task in self.tasks[job]:
                    self.last_end_time[self.task_machines[task][0]] = (
                        self.start_vars[(job, task, time)] + self.task_machines[task][1]
                    )
        print("Solution for greedy algorithm:")
        df = []
        current_time = datetime.now().replace(second=0, microsecond=0)
        finished_time = 0  # time when all tasks are finished
        total_cost = 0
        for job in range(self.n_jobs):
            for time in range(self.times[job]):
                for task in self.tasks[job]:
                    print(
                        "%d.Job %d task %d starts at %.2f and ends at %.2f on machine %d costs %.2f"
                        % (
                            time,
                            job,
                            task,
                            self.start_vars[(job, task, time)],
                            self.start_vars[(job, task, time)]
                            + self.task_machines[task][1],
                            self.task_machines[task][0],
                            self.capacities[self.task_machines[task][0]][task][1],
                        )
                    )
                    total_cost += self.capacities[self.task_machines[task][0]][task][1]
                    finished_time = max(
                        finished_time,
                        self.start_vars[(job, task, time)]
                        + self.task_machines[task][1],
                    )
                    df.append(
                        dict(
                            Task="Machine %i" % self.task_machines[task][0],
                            Start=ToDate(
                                current_time, self.start_vars[(job, task, time)]
                            ),
                            Finish=ToDate(
                                current_time,
                                self.start_vars[(job, task, time)]
                                + self.task_machines[task][1],
                            ),
                            Machine="Task %i" % task,
                        )
                    )
        print("Finished time: %.2f" % finished_time)
        print("Total cost: %.2f" % total_cost)
        print()
        if display:
            self.plot(df)


if __name__ == "__main__":
    tasks = [(1, 17, 2, 3), [1, 26, 3, 7, 5, 6], [1, 24, 3]]
    orders = [
        [(1, 17), (17, 2), (2, 3)],
        [(1, 26), (26, 3), (3, 7), (7, 5)],
        [(1, 24), (24, 3)],
    ]
    times = [50, 6, 10]
    capacities = defaultdict(
        dict,
        {
            1: {18: (6.61, 3.11), 12: (6.1, 2.73), 19: (9.04, 4.25), 17: (3.64, 7.35)},
            2: {32: (6.49, 7.88), 17: (3.98, 2.22)},
            3: {6: (2.85, 5.1)},
            4: {2: (4.34, 1.6)},
            5: {3: (0.28, 1.83), 4: (3.39, 8.33)},
            6: {17: (9.7, 4.35)},
            7: {12: (9.42, 5.49), 19: (2.96, 7.61), 32: (6.18, 4.53), 27: (4.67, 7.27)},
            8: {5: (2.76, 6.22)},
            9: {5: (7.51, 5.6)},
            10: {
                18: (9.59, 1.21),
                12: (1.3, 6.67),
                19: (5.73, 0.66),
                28: (3.76, 4.06),
                29: (3.54, 8.28),
            },
            11: {
                17: (3.72, 3.08),
                28: (0.5, 6.45),
                29: (6.9, 4.95),
                12: (1.94, 6.69),
                26: (7.33, 5.05),
            },
            12: {
                26: (3.34, 0.19),
                27: (6.66, 4.82),
                28: (4.85, 5.65),
                29: (0.66, 1.47),
            },
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
            30: {20: (4.11, 8.26), 21: (9.67, 3.39)},
        },
    )
    greedyjs = GreedyJS(tasks, orders, capacities, times)
    greedyjs.solve(display=False)
