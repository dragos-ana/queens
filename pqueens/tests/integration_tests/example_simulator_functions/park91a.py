"""Park91a function."""
# pylint: disable=invalid-name


import numpy as np

# x3 and x4 grid
x = np.linspace(0, 1, 4)
x3_vec, x4_vec = np.meshgrid(x, x)
x3_vec = x3_vec.flatten()
x4_vec = x4_vec.flatten()


def unit_bounding(*args):
    """Bounding function.

    This should be avoided...
    """
    args = list(args)
    for i, arg in enumerate(args):
        if arg <= 0:
            args[i] = 0.01
        elif arg >= 1:
            args[i] = 0.99
    return tuple(args)


def x3_x4_grid_eval(park_function, x1, x2, gradient_bool=False, **kwargs):
    """Evaluate a park function on a *x3* and *x4* grid.

    Args:
        park_function (func): Function to be evaluated
        x1 (int): Input parameter 1
        x2 (int): Input parameter 2
        gradient_bool (bool, optional): Switch to return gradient value w.r.t. *x1* and *x2*

    Returns:
        np.ndarray: *park_function* evaluated on the grid
    """
    # Loop over the coordinates
    y_vec = []
    dy_dx1_vec = []
    dy_dx2_vec = []
    if gradient_bool:
        for x3, x4 in zip(x3_vec, x4_vec):
            # Bound the arguments
            args = unit_bounding(x1, x2, x3, x4)
            y, gradient = park_function(*args, gradient_bool=True, **kwargs)
            dy_dx1_vec.append(gradient[0])
            dy_dx2_vec.append(gradient[1])
            y_vec.append(y)
        return np.array(y_vec), (np.array(dy_dx1_vec), np.array(dy_dx2_vec))
    else:
        for x3, x4 in zip(x3_vec, x4_vec):
            # Bound the arguments
            args = unit_bounding(x1, x2, x3, x4)
            y_vec.append(park_function(*args, **kwargs))
        return np.array(y_vec)


def park91a_lofi(x1, x2, x3, x4, **kwargs):
    r"""Low-fidelity Park91a function.

    Simple four-dimensional benchmark function as proposed in [1] to mimic
    a computer model. For the purpose of multi-fidelity simulation, [3]
    defined a corresponding lower fidelity function, which is defined as:

    :math:`f_{lofi}({\bf x})=
    \left[1 + \frac{\sin(x_1)}{10} \right] f_{hifi}({\bf x}) - 2x_1 + x_2^2 + x_3^2 + 0.5`

    The high-fidelity version is defined as is implemented in *park91a_hifi*.

    Args:
        x1 (float):  Input parameter 1 [0,1)
        x2 (float):  Input parameter 2 [0,1)
        x3 (float):  Input parameter 3 [0,1)
        x4 (float):  Input parameter 4 [0,1)

    Returns:
        float: Value of function at parameters

    References:
        [1] Park, J.-S.(1991). Tuning complex computer codes to data and optimal
            designs, Ph.D Thesis

        [2] Cox, D. D., Park, J.-S., & Singer, C. E. (2001). A statistical method
            for tuning a computer code to a data base. Computational Statistics &
            Data Analysis, 37(1), 77-92. http://doi.org/10.1016/S0167-9473(00)00057-8

        [3] Xiong, S., Qian, P., & Wu, C. (2013). Sequential design and analysis of
            high-accuracy and low-accuracy computer codes. Technometrics.
            http://doi.org/10.1080/00401706.2012.723572
    """
    yh = park91a_hifi(x1, x2, x3, x4)
    term1 = (1 + np.sin(x1) / 10) * yh
    term2 = -2 * x1 + x2**2 + x3**2
    y = term1 + term2 + 0.5
    return y


def park91a_hifi(x1, x2, x3, x4, gradient_bool=False, **kwargs):
    r"""High-fidelity Park91a function.

    Simple four-dimensional benchmark function as proposed in [1] to mimic
    a computer model. For the purpose of multi-fidelity simulation, [3]
    defined a corresponding lower fidelity function, which is  implemented
    in *park91a_lofi*.

    The high-fidelity version is defined as:

    :math:`f({\bf x}) =
    \frac{x_1}{2}\left[ \sqrt{1+(x_2+x_3^2)\frac{x_4}{x_1^2}}-1 \right] +(x_1+3x_4)\exp \left[1-\sin(x_3) \right]`

    Args:
        x1 (float): Input parameter 1 [0,1)
        x2 (float): Input parameter 2 [0,1)
        x3 (float): Input parameter 3 [0,1)
        x4 (float): Input parameter 4 [0,1)
        gradient_bool (bool, optional): Switch to return gradient value w.r.t. `x1` and `x2`

    Returns:
        y (float): Value of function at parameters
        dy_dx1 (float): Gradient of the function w.r.t. *x1*
        dy_dx2 (float): Gradient of the function w.r.t. *x2*

    References:
        [1] Park, J.-S.(1991). Tuning complex computer codes to data and optimal
            designs, Ph.D. Thesis

        [2] Cox, D. D., Park, J.-S., & Singer, C. E. (2001). A statistical method
            for tuning a computer code to a database. Computational Statistics &
            Data Analysis, 37(1), 77?92. http://doi.org/10.1016/S0167-9473(00)00057-8

        [3] Xiong, S., Qian, P., & Wu, C. (2013). Sequential design and analysis of
            high-accuracy and low-accuracy computer codes. Technometrics.
            http://doi.org/10.1080/00401706.2012.723572
    """
    term1a = x1 / 2
    term1b = np.sqrt(1 + (x2 + x3**2) * x4 / (x1**2)) - 1
    term1 = term1a * term1b

    term2a = x1 + 3 * x4
    term2b = np.exp(1 + np.sin(x3))
    term2 = term2a * term2b

    y = term1 + term2

    if gradient_bool:
        term1a = x1 / 2
        term1b = np.sqrt(1 + (x2 + x3**2) * x4 / (x1**2)) - 1
        term1 = term1a * term1b

        term2a = x1 + 3 * x4
        term2b = np.exp(1 + np.sin(x3))
        term2 = term2a * term2b

        y = term1 + term2

        # ----
        term1a = x1 / 2
        d_term1a_dx1 = 1 / 2
        term1b = np.sqrt(1 + (x2 + x3**2) * x4 / (x1**2)) - 1
        d_term1b_dx1 = (
            1
            / (2 * np.sqrt(1 + (x2 + x3**2) * x4 / (x1**2)))
            * (-2 * (x2 + x3**2) * x4 * x1 ** (-3))
        )
        term1 = term1a * term1b
        d_term1_dx1 = d_term1a_dx1 * term1b + term1a * d_term1b_dx1

        term2a = x1 + 3 * x4
        d_term2a_dx1 = 1
        term2b = np.exp(1 + np.sin(x3))
        d_term2b_dx1 = 0
        term2 = term2a * term2b
        d_term2_dx1 = d_term2a_dx1 * term2b + term2a * d_term2b_dx1

        dy_dx1 = d_term1_dx1 + d_term2_dx1

        # ----
        term1a = x1 / 2
        d_term1a_dx2 = 0
        term1b = np.sqrt(1 + (x2 + x3**2) * x4 / (x1**2)) - 1
        d_term1b_dx2 = 1 / (2 * np.sqrt(1 + (x2 + x3**2) * x4 / (x1**2))) * x4 / (x1**2)
        term1 = term1a * term1b
        d_term1_dx2 = d_term1a_dx2 * term1b + term1a * d_term1b_dx2

        term2a = x1 + 3 * x4
        term2b = np.exp(1 + np.sin(x3))
        term2 = term2a * term2b
        d_term2_dx2 = 0

        dy_dx2 = d_term1_dx2 + d_term2_dx2

        return y, (dy_dx1, dy_dx2)
    else:
        return y


def park91a_hifi_on_grid(x1, x2, **kwargs):
    r"""High-fidelity Park91a function on *x3* and *x4* grid.

    Args:
        x1 (float): Input parameter 1 [0,1)
        x2 (float): Input parameter 2 [0,1)

    Returns:
        np.ndarray: Value of the function at the parameters
    """
    y = x3_x4_grid_eval(park91a_hifi, x1, x2, **kwargs)
    return y


def park91a_hifi_on_grid_with_gradients(x1, x2, **kwargs):
    r"""High-fidelity Park91a function on *x3* and *x4* grid with gradients.

    Args:
        x1 (float): Input parameter 1 [0,1)
        x2 (float): Input parameter 2 [0,1)

    Returns:
        y (float): Value of function at parameters
        dy_dx1 (float): Gradient of the function w.r.t. *x1*
        dy_dx2 (float): Gradient of the function w.r.t. *x2*

    """
    y, (dy_dx1, dy_dx2) = x3_x4_grid_eval(park91a_hifi, x1, x2, gradient_bool=True, **kwargs)
    return y, (dy_dx1, dy_dx2)


def park91a_lofi_on_grid(x1, x2, **kwargs):
    r"""Low-fidelity Park91a function on fixed *x3* and *x4* grid.

    Args:
        x1 (float): Input parameter 1 [0,1)
        x2 (float): Input parameter 2 [0,1)

    Returns:
        np.ndarray: Value of the function at the parameters
    """
    y = x3_x4_grid_eval(park91a_lofi, x1, x2, **kwargs)
    return y
