import sys
import random
from utils import *
from instances import *


DELTA_STR = 'Delta'
TMAX_STR = 'tmax'


def check_exclusion(exclusions: dict, interventions: dict, seasons, intervention_name: str, start_time: int, solution: list):
    for exclusion in exclusions.values():
        # Retrieve exclusion infos
        [intervention_1_name, intervention_2_name, season] = exclusion

        if intervention_1_name == intervention_name:
            intervention_1 = interventions[intervention_1_name]
            for name, start_time_to_check in solution:
                if name == intervention_2_name:
                    intervention_2 = interventions[intervention_2_name]
                    intervention_1_delta = int(
                        intervention_1[DELTA_STR][start_time - 1])  # get index in list
                    intervention_2_delta = int(
                        intervention_2[DELTA_STR][start_time_to_check - 1])  # get index in list

                    # Check overlaps for each time step of the season
                    for time_str in seasons[season]:
                        time = int(time_str)
                        if (start_time <= time < start_time + intervention_1_delta) and (start_time_to_check <= time < start_time_to_check + intervention_2_delta):
                            return False

        elif intervention_2_name == intervention_name:
            intervention_1 = interventions[intervention_2_name]
            for name, start_time_to_check in solution:
                if name == intervention_1_name:
                    intervention_2 = interventions[intervention_1_name]
                    intervention_1_delta = int(
                        intervention_1[DELTA_STR][start_time - 1])  # get index in list
                    intervention_2_delta = int(
                        intervention_2[DELTA_STR][start_time_to_check - 1])  # get index in list

                    # Check overlaps for each time step of the season
                    for time_str in seasons[season]:
                        time = int(time_str)
                        if (start_time <= time < start_time + intervention_1_delta) and (start_time_to_check <= time < start_time_to_check + intervention_2_delta):
                            return False

    return True


def get_starting_times(t_max: int):
    starting_time = list(range(1, t_max + 1))
    random.shuffle(starting_time)
    return starting_time


def compute(instance: dict):
    best_objective = -1
    best_solution = []
    n_try = 100
    for i in range(n_try):
        solution = []

        # Retrieve usefull infos
        interventions = get_interventions(instance)
        t_max = get_t_max(instance)
        resources = get_resources(instance)
        exclusions = get_exclusions(instance)
        seasons = get_seasons(instance)

        # Init resource usage dictionnary for each resource and time
        resources_usage = {}
        for resource_name in resources.keys():
            resources_usage[resource_name] = [0 for _ in range(t_max)]

        # Loop on all interventions
        for intervention_name, intervention in interventions.items():

            # Test a list of starting time for the intervention
            starting_times = get_starting_times(t_max)
            for start_time in starting_times:
                start_time_idx = start_time - 1  # index of list starts at 0
                is_workload_validate = True

                # compute effective worload
                intervention_workload = get_intervention_workload(intervention)
                intervention_delta = get_intervention_duration(
                    intervention, start_time_idx)
                for resource_name, intervention_resource_workload in intervention_workload.items():
                    for time in range(start_time_idx, int(start_time_idx + intervention_delta)):
                        # null values are not available
                        if str(time + 1) in intervention_resource_workload and str(start_time) in intervention_resource_workload[str(time + 1)]:
                            resource_usage_day = resources_usage[resource_name][time] + \
                                intervention_resource_workload[str(
                                    time + 1)][str(start_time)]
                            if resource_usage_day > get_max_resources(resources, resource_name, time):
                                # We can't do the intervention because it exerced the max workload
                                is_workload_validate = False
                                break

                    # If we can do the intervention this day, we add the necessary ressources to the usage
                    # Else we try another day
                    if is_workload_validate == False:
                        break
                    else:
                        for time in range(start_time_idx, int(start_time_idx + intervention_delta)):
                            # null values are not available
                            if str(time + 1) in intervention_resource_workload and str(start_time) in intervention_resource_workload[str(time + 1)]:
                                resources_usage[resource_name][time] += \
                                    intervention_resource_workload[str(
                                        time + 1)][str(start_time)]

                is_exclusion_validate = check_exclusion(
                    exclusions,
                    interventions,
                    seasons,
                    intervention_name,
                    start_time,
                    solution)  # Check exclusions constraints
                if is_workload_validate and is_exclusion_validate:
                    solution.append((intervention_name, start_time))
                    break

        objective = compute_objective(instance, solution)
        print(f"Try number {i} -- objective = {objective}")

        if best_objective < 0:  # Init the objective
            best_objective = objective
            best_solution = solution
        elif objective < best_objective:
            best_objective = objective
            best_solution = solution

    export_solution(best_solution, solution_file)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('ERROR: expecting 2 argument: paths to instance and solution filename')
        sys.exit(1)
    else:
        instance_file = sys.argv[1]
        solution_file = sys.argv[2]
        instance = read_json(instance_file)

    compute(instance)
