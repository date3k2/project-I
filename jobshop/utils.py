def get_data(filename: str = "input.txt"):
    with open(filename, "r") as f:
        n_job, n_machine = map(int, f.readline().split())
        durations = [list(map(int, f.readline().split())) for _ in range(n_job)]
        _ = f.readline()
        machines = [
            list(map(lambda x: int(x) - 1, f.readline().split())) for _ in range(n_job)
        ]
    return durations, machines
