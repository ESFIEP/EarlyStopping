import numpy as np

class landweber:
    """ A class to perform estimation using the Landweber iterative method.

    Parameters
    ----------
    input_matrix: array
        nxp design matrix of the linear model.

    output_variable: array
        n-dim vector of the observed data in the linear model.

    true_signal: array or None, default = None 
        d-dim vector
        For simulation purposes only. For simulated data the true signal can be
        included to compute theoretical quantities such as the bias and the mse
        alongside the iterative procedure.

    Attributes
    ----------
    sample_size: int
        Sample size of the linear model
    
    para_size: int
        Parameter size of the linear model

    iter: int
        Current Landweber iteration of the algorithm

    landw_estimate: array
        Landweber estimate at the current iteration for the data given in
        inputMatrix

    residuals: array
        Lists the sequence of the squared residuals between the observed data and
        the Landweber estimator.

    strong_bias2: array
        Only exists if trueSignal was given. Lists the values of the strong squared
        bias up to current Landweber iteration.

    strong_variance: array
        Only exists if trueSignal was given. Lists the values of the strong variance 
        up to current Landweber iteration.

    strong_error: array
        Only exists if trueSignal was given. Lists the values of the strong norm error 
        between the Landweber estimator and the true signal up to
        current Landweber iteration.
    
    weak_bias2: array
        Only exists if trueSignal was given. Lists the values of the weak squared
        bias up to current Landweber iteration.

    weak_variance: array
        Only exists if trueSignal was given. Lists the values of the weak variance 
        up to current Landweber iteration.

    weak_error: array
        Only exists if trueSignal was given. Lists the values of the weak norm error 
        between the Landweber estimator and the true signal up to
        current Landweber iteration.

    """

    def __init__(self, input_matrix, output_variable, true_signal = None):
        self.input_matrix    = input_matrix
        self.output_variable = output_variable
        self.true_signal     = true_signal
 
        # Parameters of the model
        self.sample_size = np.shape(input_matrix)[0]
        self.para_size   = np.shape(input_matrix)[1]

        # Estimation quantities
        self.iter               = 0
        self.landw_estimate     = np.zeros(self.para_size)

        # Residual quantities
        self.__residual_vector = output_variable
        self.residuals         = np.array([np.sum(self.__residual_vector**2)])

        if self.true_signal is not None:
            self.mse = np.array([])
   
#        if self.true_signal is not None:
#            self.__error_vector     = self.output_variable - np.dot(self.input_matrix, self.true_signal) 
#            self.__strong_bias2_vector     = self.true_signal
#            self.__strong_variance_vector  = np.zeros(self.para_size)
#            self.__weak_bias2_vector     = np.dot(self.input_matrix,self.true_signal)
#            self.__weak_variance_vector  = np.zeros(self.sample_size)#

#            self.strong_bias2      = np.array([np.sum(self.__strong_bias2_vector**2)])
#            self.strong_variance   = np.array([0])
#            self.strong_error      = self.strong_bias2

#            self.weak_bias2        = np.array([np.sum(self.__weak_bias2_vector**2)])
#            self.weak_variance     = np.array([0])
#            self.weak_error        = self.weak_bias2

    def landw(self, iter_num = 1):
        """Performs iter_num iterations of the Landweber algorithm"""
        for index in range(iter_num):
            self.__landw_one_iteration()
        
    def __landw_one_iteration(self):
        """Performs one iteration of the Landweber algorithm"""
        
        self.landw_estimate  = self.landw_estimate + np.dot(np.transpose(self.input_matrix),self.output_variable - np.dot(self.input_matrix,self.landw_estimate))

        # Update estimation quantities
        self.__residual_vector  = self.output_variable - np.dot(self.input_matrix,self.landw_estimate)
        new_residuals           = np.sum(self.__residual_vector**2)
        self.residuals          = np.append(self.residuals, new_residuals)
        self.iter             = self.iter + 1

        # Update theoretical quantities
        if self.true_signal is not None:
            self.__update_strong_error()
#            self.__update_strong_bias2()
#            self.__update_strong_variance()
#            self.__update_weak_error()
#            self.__update_weak_bias2()
#            self.__update_weak_variance()
        
    def __update_strong_error(self): 
        new_mse   = np.mean((self.true_signal - self.landw_estimate)**2)
        self.mse = np.append(self.mse, new_mse)

#    def __update_bias2(self, weak_learner):
#        coefficient        = np.dot(self.true_signal, weak_learner) / \
#                             self.sample_size
#        self.__bias2_vector = self.__bias2_vector - coefficient * weak_learner
#        new_bias2           = np.mean(self.__bias2_vector**2)
#        self.bias2         = np.append(self.bias2, new_bias2)

#    def __update_stochastic_error(self, weak_learner):
#        coefficient             = np.dot(self.__error_vector, weak_learner) / \
#                                 self.sample_size
#        self.__stoch_error_vector = self.__stoch_error_vector + \
#                                  coefficient * weak_learner
#        new_stoch_error           = np.mean(self.__stoch_error_vector**2)
#        self.stoch_error         = np.append(self.stoch_error, new_stoch_error)