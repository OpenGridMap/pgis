class LoadEstimator:
    def __init__(self):
        pass

    @staticmethod
    def estimate_load(population):
        # German per head power consumption in kWh according to statista (for the year 2015)
        per_head_power_consumption = 7.381
        load_per_head = (per_head_power_consumption * 1000) / (365 * 24)
        total_load = population * load_per_head
        return total_load
