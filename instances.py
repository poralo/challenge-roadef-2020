import numpy as np

RESOURCES_STR = 'Resources'
SEASONS_STR = 'Seasons'
INTERVENTIONS_STR = 'Interventions'
EXCLUSIONS_STR = 'Exclusions'
T_STR = 'T'
SCENARIO_NUMBER = 'Scenarios_number'
RESOURCE_CHARGE_STR = 'workload'
TMAX_STR = 'tmax'
DELTA_STR = 'Delta'
MAX_STR = 'max'
MIN_STR = 'min'
RISK_STR = 'risk'
START_STR = 'start'
QUANTILE_STR = "Quantile"
ALPHA_STR = "Alpha"


def get_interventions(instance: dict):
    return instance[INTERVENTIONS_STR]


def get_t_max(instance: dict):
    return instance[T_STR]


def get_resources(instance: dict):
    return instance[RESOURCES_STR]


def get_exclusions(instance: dict):
    return instance[EXCLUSIONS_STR]


def get_seasons(instance: dict):
    return instance[SEASONS_STR]


def get_max_resources(resources: dict, resource_name: str, time: int):
    """Return the maximum available resources at a time"""
    return resources[resource_name][MAX_STR][time]


def get_min_resources(resources: dict, resource_name: str, time: int):
    """Return the minimum resources to be used at a time"""
    return resources[resource_name][MIN_STR][time]


def get_intervention_duration(intervention: dict, time: int):
    """Return the duration time of a given intervention"""
    return intervention[DELTA_STR][time]


def get_intervention_workload(intervention: dict):
    return intervention[RESOURCE_CHARGE_STR]


def get_resource_workload(interventions: dict, resource_name: str, time: int, intervention_name: str, start_time: int):
    resource_workload = interventions[intervention_name][RESOURCE_CHARGE_STR][resource_name]
    return resource_workload[str(time)][str(start_time)]


# Retrieve effective risk distribution given starting times solution
def compute_risk_distribution(interventions: dict, t_max: int, scenario_numbers: list, solution: list):
    """Compute risk distributions for all time steps, given the interventions starting times"""

    # Init risk table
    risk = [scenario_numbers[t] * [0] for t in range(t_max)]

    # Compute for each intervention independently
    for intervention_name, start_time in solution:
        # Retrieve intervention's usefull infos
        intervention = interventions[intervention_name]
        intervention_risk = intervention[RISK_STR]

        start_time_idx = int(start_time) - 1  # index for list getter
        delta = int(intervention[DELTA_STR][start_time_idx])
        for time in range(start_time_idx, start_time_idx + delta):
            try:
                for i, additional_risk in enumerate(intervention_risk[str(time + 1)][str(start_time)]):
                    risk[time][i] += additional_risk
            except:
                # print("Error")
                pass

    return risk


# Compute mean for each period
def compute_mean_risk(risk: list, t_max: int, scenario_numbers: list):
    """Compute mean risk values over each time period"""

    # Init mean risk
    mean_risk = np.zeros(t_max)
    # compute mean
    for t in range(t_max):
        mean_risk[t] = sum(risk[t]) / scenario_numbers[t]

    return mean_risk


# Compute quantile for each period
def compute_quantile(risk: list, t_max: int, scenario_numbers: list, quantile: float):
    """Compute Quantile values over each time period"""

    # Init quantile
    q = np.zeros(t_max)
    for t in range(t_max):
        risk[t].sort()
        q[t] = risk[t][int(np.ceil(scenario_numbers[t] * quantile))-1]

    return q


# Compute both objectives: mean risk and quantile
def compute_objective(instance: dict, solution: list):
    """Compute objectives (mean and expected excess)"""

    # Retrieve usefull infos
    t_max = instance[T_STR]
    scenario_numbers = instance[SCENARIO_NUMBER]
    interventions = instance[INTERVENTIONS_STR]
    quantile = instance[QUANTILE_STR]
    alpha = instance[ALPHA_STR]

    # Retrieve risk final distribution
    risk = compute_risk_distribution(
        interventions, t_max, scenario_numbers, solution)

    # Compute mean risk
    mean_risk = compute_mean_risk(risk, t_max, scenario_numbers)

    # Compute quantile
    quant = compute_quantile(risk, t_max, scenario_numbers, quantile)
    tmp = np.zeros(len(quant))
    obj_2 = np.mean(np.max(np.vstack((quant - mean_risk, tmp)), axis=0))

    return alpha * np.mean(mean_risk) + (1 - alpha) * obj_2
