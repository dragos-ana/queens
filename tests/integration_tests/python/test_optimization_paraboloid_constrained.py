"""TODO_doc."""

import numpy as np
import pytest

from queens.distributions.free import FreeVariable
from queens.drivers.function_driver import FunctionDriver
from queens.interfaces.job_interface import JobInterface
from queens.iterators.optimization_iterator import OptimizationIterator
from queens.main import run_iterator
from queens.models.simulation_model import SimulationModel
from queens.parameters.parameters import Parameters
from queens.schedulers.local_scheduler import LocalScheduler
from queens.utils.io_utils import load_result


@pytest.fixture(name="algorithm", params=["COBYLA", "SLSQP"])
def fixture_algorithm(request):
    """TODO_doc."""
    return request.param


def test_optimization_paraboloid_constrained(algorithm, global_settings):
    """Test different solution algorithms in optimization iterator.

    COBYLA: constrained but unbounded

    SLSQP:  constrained and bounded
    """
    # Parameters
    x1 = FreeVariable(dimension=1)
    x2 = FreeVariable(dimension=1)
    parameters = Parameters(x1=x1, x2=x2)

    # Setup iterator
    driver = FunctionDriver(function="paraboloid")
    scheduler = LocalScheduler(experiment_name=global_settings.experiment_name)
    interface = JobInterface(parameters=parameters, scheduler=scheduler, driver=driver)
    model = SimulationModel(interface=interface)
    iterator = OptimizationIterator(
        initial_guess=[2.0, 0.0],
        algorithm=algorithm,
        result_description={"write_results": True, "plot_results": True},
        bounds=[[0.0, 0.0], float("inf")],
        constraints={
            "cons1": {"type": "ineq", "fun": "lambda x:  x[0] - 2 * x[1] + 2"},
            "cons2": {"type": "ineq", "fun": "lambda x: -x[0] - 2 * x[1] + 6"},
            "cons3": {"type": "ineq", "fun": "lambda x: -x[0] + 2 * x[1] + 2"},
        },
        model=model,
        parameters=parameters,
        global_settings=global_settings,
    )

    # Actual analysis
    run_iterator(iterator, global_settings=global_settings)

    # Load results
    results = load_result(global_settings.result_file(".pickle"))

    np.testing.assert_allclose(results.x, np.array([+1.4, +1.7]), rtol=1.0e-4)
    np.testing.assert_allclose(results.fun, np.array(+0.8), atol=1.0e-07)
