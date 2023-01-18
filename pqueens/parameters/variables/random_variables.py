"""Random Variables module."""


class RandomVariable:
    """RandomVariable class.

    Attributes:
        distribution (Distribution): Underlying distribution of random variable.
        dimension (int): Dimension of the random variable.
        lower_bound (list, int): Lower bound of the random variable.
        upper_bound (list, int): Upper bound of the random variable.
        data_type (str): Specifies the data type of the random variable ("INT" or "FLOAT").
    """

    def __init__(self, distribution, dimension, lower_bound, upper_bound):
        """Initialize random variable object.

        Args:
            distribution (Distribution): Underlying distribution of random variable
            dimension (int): Dimension of the random variable
            lower_bound (list, int): Lower bound of the random variable
            upper_bound (list, int): Upper bound of the random variable
        """
        self.distribution = distribution
        self.dimension = dimension
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def draw_samples(self, num_samples):
        """Draw samples from the random variable.

        Args:
            num_samples: TODO_doc
        Returns:
            samples (np.ndarray): Drawn samples
        """
        return self.distribution.draw(num_samples).reshape(-1, self.dimension)
