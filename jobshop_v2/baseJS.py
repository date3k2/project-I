from typing import List, Tuple
import plotly.figure_factory as ff
import datetime
from abc import ABC, abstractmethod


def ToDate(now, mins):
    return (now + datetime.timedelta(minutes=mins)).strftime("%Y-%m-%d %H:%M:%S")


class BaseJS(ABC):
    """
    Base class for Job Shop Scheduling version 2
    """

    def __init__(
        self,
        tasks: List[List[int]],
        orders: List[List[Tuple[int, int]]],
        capacities: dict,
        times: List[int],
    ):
        self.tasks = tasks
        self.orders = orders
        self.capacities = capacities
        self.n_jobs = len(tasks)
        self.times = times

    @abstractmethod
    def solve(self, display, max_time_in_seconds):
        pass

    def plot(self, df):
        """
        Plot the Gantt chart
        """
        sorted_df = sorted(df, key=lambda k: k["Task"])
        fig = ff.create_gantt(
            sorted_df,
            index_col="Machine",
            title=" Gantt Chart",
            show_colorbar=True,
            showgrid_x=True,
            showgrid_y=True,
            group_tasks=True,
        )
        fig.show()
