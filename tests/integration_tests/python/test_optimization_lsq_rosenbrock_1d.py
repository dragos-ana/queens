#
# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (c) 2024-2025, QUEENS contributors.
#
# This file is part of QUEENS.
#
# QUEENS is free software: you can redistribute it and/or modify it under the terms of the GNU
# Lesser General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version. QUEENS is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details. You
# should have received a copy of the GNU Lesser General Public License along with QUEENS. If not,
# see <https://www.gnu.org/licenses/>.
#
"""Integration test for the Optimization iterator.

This test analyzes the special case of 1 unknown but 2 residuals.
"""

import numpy as np

from queens.distributions.free_variable import FreeVariable
from queens.drivers.function import Function
from queens.iterators.least_squares import LeastSquares
from queens.main import run_iterator
from queens.models.simulation import Simulation
from queens.parameters.parameters import Parameters
from queens.schedulers.pool import Pool
from queens.utils.io import load_result


def test_optimization_lsq_rosenbrock_1d(global_settings):
    """Test special case for optimization iterator with the least squares.

    Special case: 1 unknown but 2 residuals.
    """
    # Parameters
    x1 = FreeVariable(dimension=1)
    parameters = Parameters(x1=x1)

    # Setup iterator
    driver = Function(parameters=parameters, function="rosenbrock60_residual_1d")
    scheduler = Pool(experiment_name=global_settings.experiment_name)
    model = Simulation(scheduler=scheduler, driver=driver)
    iterator = LeastSquares(
        algorithm="trf",
        initial_guess=[3.0],
        result_description={"write_results": True},
        bounds=[float("-inf"), float("inf")],
        model=model,
        parameters=parameters,
        global_settings=global_settings,
    )

    # Actual analysis
    run_iterator(iterator, global_settings=global_settings)

    # Load results
    results = load_result(global_settings.result_file(".pickle"))

    np.testing.assert_allclose(results.x, np.array([+1.0]))
    np.testing.assert_allclose(results.fun, np.array([+0.0, +0.0]))
