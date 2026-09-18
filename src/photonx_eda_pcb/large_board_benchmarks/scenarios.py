from .model import BenchmarkScenario
def standard_scenarios():
    return [
      BenchmarkScenario("1k_objects",24,24,2.0,1),
      BenchmarkScenario("3k_objects",40,40,2.0,1),
      BenchmarkScenario("7k_objects",60,60,2.0,1),
    ]
