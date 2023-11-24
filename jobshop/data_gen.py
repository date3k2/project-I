import numpy as np
from typing import List, Tuple


def jobshop_data_gen(
    n_job: int, n_machine: int, seed=None
) -> Tuple[List[List[int]], List[List[int]]]:
    """
    Generate random jobshop data.

    Parameters
    ----------
    n_job : int
        Number of jobs.
    n_machine : int
        Number of machines.
    seed : int, optional
        Random seed.

    Returns
    -------
    durations : List[List[int]]
        Processing times.
    machines : List[List[int]]
        Machine orders.
    """
    if seed is not None:
        np.random.seed(seed)
    durations = np.random.randint(1, 100, size=(n_job, n_machine)).tolist()
    machines = [np.random.permutation(n_machine).tolist() for _ in range(n_job)]
    return durations, machines
