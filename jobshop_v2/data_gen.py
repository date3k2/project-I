import numpy as np
from jobshop_v2.validation import checkCycle


class DataGen:
    def __init__(self, n_jobs: int, n_machines: int, n_tasks: int, seed: int = None):
        if seed:
            np.random.seed(seed)
        self.n_jobs = n_jobs
        self.n_machines = n_machines
        self.n_tasks = n_tasks

    def generate(self):
        jobs_data = []
        for _ in range(self.n_jobs):
            num_tasks = np.random.randint(1, self.n_tasks)
            tasks = np.random.choice(self.n_tasks, num_tasks, replace=False)
            # assert len(tasks) == len(set(tasks)), "Duplicate tasks"
            processing_times = np.random.uniform(1, 10, num_tasks).round(2)
            jobs_data.append(list(zip(tasks, processing_times)))

        pre = []
        for job in jobs_data:
            num_pre = np.random.randint(0, len(job))
            tasks = [task for task, _ in job]
            while True:
                pre_in_job = set()
                for _ in range(num_pre):
                    i, j = np.random.choice(tasks, 2, replace=False)
                    if i != j and (j, i) not in pre_in_job:
                        pre_in_job.add((i, j))
                pre_in_job = list(pre_in_job)
                if not checkCycle(pre_in_job):
                    pre.append(list(pre_in_job))
                    break
                # assert checkCycle(pre_in_job), "Cycle in pre"
        capacities = []
        while True:
            capacities = []
            all_tasks_in_machines = set()
            for _ in range(self.n_machines):
                num_cap = np.random.randint(1, self.n_tasks)
                capacities.append(
                    list(np.random.choice(self.n_tasks, num_cap, replace=False))
                )
                all_tasks_in_machines.update(capacities[-1])
            if len(all_tasks_in_machines) == self.n_tasks:
                break
            # assert len(all_tasks_in_machines) == self.n_tasks, "Missing tasks"
        cost = list(np.random.uniform(1, 10, self.n_machines).round(2))
        return jobs_data, pre, capacities, cost
