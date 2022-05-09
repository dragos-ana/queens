"""Beta Distribution."""
import numpy as np
import scipy.linalg
import scipy.stats

from .distributions import Distribution


class BetaDistribution(Distribution):
    """Beta distribution.

    A generalized one dim beta distribution based on scipy stats. The generalized beta
    distribution has a lower bound and an upper bound.
    The parameters :math:`a` and :math:`b` determine the shape of the distribution within
    these bounds.

    Attributes:
        a (float): Shape parameter of the beta distribution, must be > 0
        b (float): Shape parameter of the beta distribution, must be > 0
        lower_bound (float): The lower bound of the beta distribution
        upper_bound (float): The upper bound of the beta distribution
    """

    def __init__(self, lower_bound, upper_bound, a, b, scipy_beta):
        """Initialize Beta distribution."""
        self.a = a
        self.b = b
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.scipy_beta = scipy_beta
        super().__init__(mean=self.scipy_beta.mean(), covariance=self.scipy_beta.var(), dimension=1)

    @classmethod
    def from_config_create_distribution(cls, distribution_options):
        """Create beta distribution object from parameter dictionary.

        Args:
            distribution_options (dict):     Dictionary with distribution description

        Returns:
            distribution: BetaDistribution object
        """
        lower_bound = np.array(distribution_options['lower_bound']).reshape(-1)
        upper_bound = np.array(distribution_options['upper_bound']).reshape(-1)
        a = distribution_options['a']
        b = distribution_options['b']

        super().check_positivity({'a': a, 'b': b})
        super().check_bounds(lower_bound, upper_bound)

        scale = upper_bound - lower_bound
        scipy_beta = scipy.stats.beta(scale=scale, loc=lower_bound, a=a, b=b)
        return cls(
            lower_bound=lower_bound, upper_bound=upper_bound, a=a, b=b, scipy_beta=scipy_beta
        )

    def cdf(self, x):
        """Cumulative distribution function."""
        return self.scipy_beta.cdf(x)

    def draw(self, num_draws=1):
        """Draw samples."""
        return self.scipy_beta.rvs(size=num_draws)

    def logpdf(self, x):
        """Log of the probability density function."""
        return self.scipy_beta.logpdf(x)

    def pdf(self, x):
        """Probability density function."""
        return self.scipy_beta.pdf(x)

    def ppf(self, q):
        """Percent point function (inverse of cdf — percentiles)."""
        return self.scipy_beta.ppf(q)
