import pandas as pd
from .cp import CPModel
from .mip import MIPModel
import os
from .utils import get_data
from collections import defaultdict


def benchmark(dataset_path: str, model_name: str, time_limit: int, num_instance: int):
    bench = defaultdict(list)
    for file in os.listdir(dataset_path)[:num_instance]:
        model = None
        bench["Instance"].append(file.split(".")[0].title())
        durations, machines = get_data(os.path.join(dataset_path, file))
        if model_name == "CP-SAT":
            model = CPModel(durations, machines)
        elif model_name == "MIP":
            model = MIPModel(durations, machines)
        else:
            raise ValueError("model must be 'cp' or 'mip'")
        makespan = model.solve(time_limit)
        bench[f"Makespan ({model_name})"].append(makespan)
    return pd.DataFrame(bench)
