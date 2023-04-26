"""TODO_doc."""

import numpy as np

from pqueens.randomfields.random_field_gen_KLE import RandomFieldGenKLE


class RandomFieldGenKLE2D(RandomFieldGenKLE):
    """Generator for 2D random fields based on KLE expansion.

    Attributes:
        w_n: TODO_doc
        lambda_n: TODO_doc
        act_energy_frac: TODO_doc
    """

    def __init__(
        self,
        marginal_distribution,
        corr_length,
        energy_frac,
        field_bbox,
        dimension,
        num_ex_term_per_dim,
        num_terms,
    ):
        """TODO_doc.

        Args:
            marginal_distribution: TODO_doc
            corr_length: TODO_doc
            energy_frac: TODO_doc
            field_bbox: TODO_doc
            dimension: TODO_doc
            num_ex_term_per_dim: TODO_doc
            num_terms: TODO_doc
        """
        # call superclass constructor first
        super().__init__(
            marginal_distribution,
            corr_length,
            energy_frac,
            field_bbox,
            dimension,
            num_ex_term_per_dim,
            num_terms,
        )

        w_n = np.zeros((self.m, self.spatial_dim))
        # Compute roots of characteristic function for each dimension
        for i in range(self.spatial_dim):
            w_n[:, i] = self.compute_roots_of_characteristic_equation().ravel()

        # compute factors of denominator
        fac1 = self.corr_length**2 * w_n[:, 0] ** 2 + 1
        fac2 = self.corr_length**2 * w_n[:, 1] ** 2 + 1

        # compute eigenvalues and store in vector
        lambdas_array = 4 * self.corr_length**2 / (np.kron(fac1, fac2))
        lambdas_vec = lambdas_array.reshape(-1, 1)

        # in order to sort the eigenvalues we need to store the corresponding
        # root indeces to access them later when computing the eigenfunctions
        # build up index vector for indexing
        index_dim = np.arange(0, self.m)
        index_dim1_h = np.tile(index_dim, (self.m, 1))
        index_dim1 = index_dim1_h.reshape((-1, 1), order='F')
        index_dim2 = np.tile((index_dim), (1, self.m)).T
        my_w_index = np.hstack((index_dim1, index_dim2))

        # store eigenvalues together with indices
        lambdas_vec = np.hstack((lambdas_vec, my_w_index))

        # sort in ascending order
        lambda_sorted = lambdas_vec[
            lambdas_vec[:, 0].argsort(),
        ]
        # create view with reverse order
        lambda_sorted = lambda_sorted[::-1]

        # truncate and store in class variables
        self.lambda_n = lambda_sorted[0 : self.trunc_thres, :]
        my_index_1 = np.array(lambda_sorted[0 : self.trunc_thres, 2]).astype(int)
        my_index_0 = np.array(lambda_sorted[0 : self.trunc_thres, 1]).astype(int)

        self.w_n = np.zeros((self.trunc_thres, 2))
        self.w_n[:, 1] = w_n[my_index_1, 1]
        self.w_n[:, 0] = w_n[my_index_0, 0]
        #
        retained_energy = np.sum(self.lambda_n[:, 0]) / (self.largest_length**self.spatial_dim)

        if retained_energy < self.des_energy_frac:
            raise RuntimeError(
                'Energy fraction retained by KLE expansion is '
                f' only {retained_energy}, not {self.des_energy_frac}'
            )
        self.act_energy_frac = retained_energy

    def gen_sample_gauss_field(self, loc, phase_angles):
        """Generate sample of standard Gaussian field.

        Compute realization of standard Gaussian field based on passed phase
        angles *phase_angles* and location.

        Arguments:
            loc (np.array):             Locations at which to evaluate generated
                                        field
            phase_angles (np.array):    Realization of standard normal random
                                        phase angles
        Returns:
            np.array: Values of the random field realization at *loc*
        """
        if len(phase_angles) != self.stoch_dim:
            raise RuntimeError(
                'Number of random phase angles does not match ' 'stochastic dimension of the field!'
            )

        if len(loc[0, :]) != 2:
            raise RuntimeError('Location vector must have one dimensions!')

        # use KLE expansion to compute random field values
        coeff = np.array(np.sqrt(self.lambda_n[:, 0]) * np.transpose(phase_angles))
        values = np.dot(
            self.compute_eigen_function_vec(loc, 0) * self.compute_eigen_function_vec(loc, 1),
            coeff.T,
        )

        return values
