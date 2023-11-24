import sys

sys.stdin = open("input.txt", "r")
sys.stdout = open("output.txt", "w")
input = sys.stdin.readline

# Input
number_of_jobs = int(input())
times_on_machine_1 = list(map(int, input().split()))
times_on_machine_2 = list(map(int, input().split()))


# Algorithm
def jssp_two_machines(number_of_jobs, times_on_machine_1, times_on_machine_2):
    """
    Solves the Johnson's two-machine scheduling problem for a given set of jobs and their processing times on two machines.

    Args:
    - number_of_jobs (int): The number of jobs to be scheduled.
    - times_on_machine_1 (list): A list of integers representing the processing times of each job on machine 1.
    - times_on_machine_2 (list): A list of integers representing the processing times of each job on machine 2.

    Returns:
    - A tuple containing two elements:
        - The optimal completion time of two-machine scheduling.
        - A list of integers representing the order in which the jobs should be scheduled.
    """

    # Step 1: Apply Johnson's algorithm to determine the order in which the jobs should be scheduled
    job_order_1 = []
    job_order_2 = []
    for i in range(number_of_jobs):
        if times_on_machine_1[i] <= times_on_machine_2[i]:
            job_order_1.append((i + 1, times_on_machine_1[i]))
        else:
            job_order_2.append((i + 1, times_on_machine_2[i]))
    job_order_1.sort(key=lambda x: x[1])
    job_order_2.sort(key=lambda x: -x[1])
    ans = [i for i, _ in job_order_1] + [i for i, _ in job_order_2]

    # Step 2: Calculate the start and finish times for each job on both machines
    start_A = finish_A = start_B = finish_B = 0
    for i in range(number_of_jobs):
        job = ans[i] - 1
        start_A = finish_A
        finish_A = start_A + times_on_machine_1[job]
        start_B = max(finish_A, finish_B)
        finish_B = start_B + times_on_machine_2[job]

    # Return the completion time of the last job on machine 2 and the order in which the jobs should be scheduled
    return finish_B, ans


# Output
if __name__ == "__main__":
    optimal_completion_time, sequence = jssp_two_machines(
        number_of_jobs, times_on_machine_1, times_on_machine_2
    )
    print(f"Optimal completion time: {optimal_completion_time}")
    # Though machine A is scheduled first, the order of machine is always 1 -> 2
    print(f"Job sequence:", *sequence)
