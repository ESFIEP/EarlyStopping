import unittest
import numpy as np
import EarlyStopping as es

class Test_landweber(unittest.TestCase):
    """Tests for the landweber algorithm"""

    def setUp(self):
        self.para_size = 50
        self.iteration = 100
        self.tol = 10**(-7)
        #supersmooth signal
        self.indices = np.arange(self.para_size)+1
        self.X = np.diag(1/(np.sqrt(self.indices)))
        self.f = 5*np.exp(-0.1*self.indices)
        self.Y = self.X @ self.f
        self.alg = es.Landweber(self.X, self.Y, true_signal = self.f, true_noise_level = 1)
        self.alg.iterate(self.iteration)
        
    def test_elementary_estimation(self):
        identity_matrix = np.eye(self.para_size)
        f = np.random.normal(0, 1, self.para_size)
        Y = identity_matrix @ f
        alg = es.Landweber(identity_matrix, Y)
        alg.iterate(self.iteration)
        beta = alg.landweber_estimate

        for i in range(len(beta)):
            deviation = np.abs(beta[i] - f[i])
            self.assertTrue(deviation < self.tol)

    def test_monotonicity_residuals(self):
        
        for m in range((self.alg.iteration - 1)):
            self.assertTrue(self.alg.residuals[m] >= self.alg.residuals[(m + 1)])

    def test_monotonicity_of_bias_and_variance(self):

        for i in range((self.alg.iteration - 1)):
            if self.alg.strong_bias2[i] >= self.tol:
                self.assertTrue(self.alg.strong_bias2[i] >= self.alg.strong_bias2[(i + 1)])
                self.assertTrue(self.alg.strong_variance[i] <= self.alg.strong_variance[(i + 1)])
                self.assertTrue(self.alg.weak_bias2[i] >= self.alg.weak_bias2[(i + 1)])
                self.assertTrue(self.alg.weak_variance[i] <= self.alg.weak_variance[(i + 1)])              


 #Running the tests
if __name__ == '__main__':
    unittest.main()

