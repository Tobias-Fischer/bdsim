"""
Transfer blocks:

- have inputs and outputs
- have state variables
- are a subclass of ``TransferBlock`` |rarr| ``Block``

"""
# The constructor of each class ``MyClass`` with a ``@block`` decorator becomes a method ``MYCLASS()`` of the BlockDiagram instance.


import numpy as np
import math
from math import sin, cos, atan2, sqrt, pi

import matplotlib.pyplot as plt
import inspect
from spatialmath import base

from bdsim.components import ClockedBlock, block

# ------------------------------------------------------------------------ 


@block
class ZOH(ClockedBlock):

    def __init__(self, clock, *inputs, x0=0, min=None, max=None, **kwargs):
        """
        :param ``*inputs``: Optional incoming connections
        :type ``*inputs``: Block or Plug
        :param x0: Initial state, defaults to 0
        :type x0: array_like, optional
        :param min: Minimum value of state, defaults to None
        :type min: float or array_like, optional
        :param max: Maximum value of state, defaults to None
        :type max: float or array_like, optional
        :param ``**kwargs``: common Block options
        :return: a ZOH block
        :rtype: Integrator instance

        Create a zero-order hold block.

        Output is the input at the previous clock time.  The state can be a scalar or a
        vector, this is given by the type of ``x0``.

        The minimum and maximum values can be:

            - a scalar, in which case the same value applies to every element of 
              the state vector, or
            - a vector, of the same shape as ``x0`` that applies elementwise to
              the state.

        .. note:: If input is not a scalar, ``x0`` must have the shape of the
            input signal.
        """
        self.type = 'sampler'
        super().__init__(nin=1, nout=1, inputs=inputs, clock=clock, **kwargs)

        x0 = base.getvector(x0)
        self._x0 = x0
        self.ndstates = len(x0)
        # print('nstates', self.nstates)

    def output(self, t=None):
        # print('* output, x is ', self._x)
        return [self._x]

    def next(self):
        xnext = np.array(self.inputs)
        return xnext

# ------------------------------------------------------------------------ 


@block
class DIntegrator(ClockedBlock):
    """
    :blockname:`INTEGRATOR`
    
    .. table::
       :align: left
    
    +------------+---------+---------+
    | inputs     | outputs |  states |
    +------------+---------+---------+
    | 1          | 1       | N       |
    +------------+---------+---------+
    | float,     | float,  |         | 
    | A(N,)      | A(N,)   |         |
    +------------+---------+---------+
    """

    def __init__(self, clock, *inputs, x0=0, gain=1.0, min=None, max=None, **kwargs):
        """
        :param ``*inputs``: Optional incoming connections
        :type ``*inputs``: Block or Plug
        :param x0: Initial state, defaults to 0
        :type x0: array_like, optional
        :param min: Minimum value of state, defaults to None
        :type min: float or array_like, optional
        :param max: Maximum value of state, defaults to None
        :type max: float or array_like, optional
        :param ``**kwargs``: common Block options
        :return: an INTEGRATOR block
        :rtype: Integrator instance

        Create an integrator block.

        Output is the time integral of the input.  The state can be a scalar or a
        vector, this is given by the type of ``x0``.

        The minimum and maximum values can be:

            - a scalar, in which case the same value applies to every element of 
              the state vector, or
            - a vector, of the same shape as ``x0`` that applies elementwise to
              the state.
        """
        self.type = 'discrete-integrator'
        super().__init__(nin=1, nout=1, inputs=inputs, clock=clock, **kwargs)

        if isinstance(x0, (int, float)):
            self.ndstates = 1
            if min is None:
                min = -math.inf
            if max is None:
                max = math.inf
                
        else:
            if isinstance(x0, np.ndarray):
                if x0.ndim > 1:
                    raise ValueError('state must be a 1D vector')
            else:
                x0 = base.getvector(x0)

            self.ndstates = x0.shape[0]
            if min is None:
                min = [-math.inf] * self.nstates
            elif len(min) != self.nstates:
                raise ValueError('minimum bound length must match x0')

            if max is None:
                max = [math.inf] * self.nstates
            elif len(max) != self.nstates:
                raise ValueError('maximum bound length must match x0')

        self._x0 = np.r_[x0]
        self.min = np.r_[min]
        self.max = np.r_[max]
        self.gain = gain
        print('nstates', self.nstates)

    def output(self, t=None):
        return [self._x]

    def next(self):
        xnext = self._x + self.gain * self.clock.T * np.array(self.inputs[0])
        return xnext

# ------------------------------------------------------------------------ #


# @block
# class LTI_SS(TransferBlock):
#     """
#     :blockname:`LTI_SS`
    
#     .. table::
#        :align: left
    
#        +------------+---------+---------+
#        | inputs     | outputs |  states |
#        +------------+---------+---------+
#        | 1          | 01      | nc      |
#        +------------+---------+---------+
#        | float,     | float,  |         | 
#        | A(nb,)     | A(nc,)  |         |
#        +------------+---------+---------+
#     """

#     def __init__(self, *inputs, A=None, B=None, C=None, x0=None, verbose=False, **kwargs):
#         r"""
#         :param ``*inputs``: Optional incoming connections
#         :type ``*inputs``: Block or Plug
#         :param N: numerator coefficients, defaults to 1
#         :type N: array_like, optional
#         :param D: denominator coefficients, defaults to [1, 1]
#         :type D: array_like, optional
#         :param x0: initial states, defaults to zero
#         :type x0: array_like, optional
#         :param ``**kwargs``: common Block options
#         :return: A SCOPE block
#         :rtype: LTI_SISO instance

#         Create a state-space LTI block.

#         Describes the dynamics of a single-input single-output (SISO) linear
#         time invariant (LTI) system described by numerator and denominator
#         polynomial coefficients.

#         Coefficients are given in the order from highest order to zeroth 
#         order, ie. :math:`2s^2 - 4s +3` is ``[2, -4, 3]``.

#         Only proper transfer functions, where order of numerator is less
#         than denominator are allowed.

#         The order of the states in ``x0`` is consistent with controller canonical
#         form.

#         Examples::

#             LTI_SISO(N=[1,2], D=[2, 3, -4])

#         is the transfer function :math:`\frac{s+2}{2s^2+3s-4}`.
#         """
#         #print('in SS constructor')
#         self.type = 'LTI SS'

#         assert A.shape[0] == A.shape[1], 'A must be square'
#         n = A.shape[0]
#         if len(B.shape) == 1:
#             nin = 1
#             B = B.reshape((n, 1))
#         else:
#             nin = B.shape[1]
#         assert B.shape[0] == n, 'B must have same number of rows as A'

#         if len(C.shape) == 1:
#             nout = 1
#             assert C.shape[0] == n, 'C must have same number of columns as A'
#             C = C.reshape((1, n))
#         else:
#             nout = C.shape[0]
#             assert C.shape[1] == n, 'C must have same number of columns as A'

#         super().__init__(nin=nin, nout=nout, inputs=inputs, **kwargs)

#         self.A = A
#         self.B = B
#         self.C = C

#         self.nstates = A.shape[0]

#         if x0 is None:
#             self._x0 = np.zeros((self.nstates,))
#         else:
#             self._x0 = x0

#     def output(self, t=None):
#         return list(self.C @ self._x)

#     def deriv(self):
#         return self.A @ self._x + self.B @ np.array(self.inputs)
# # ------------------------------------------------------------------------ #


# @block
# class LTI_SISO(LTI_SS):
#     """
#     :blockname:`LTI_SISO`
    
#     .. table::
#        :align: left
    
#        +------------+---------+---------+
#        | inputs     | outputs |  states |
#        +------------+---------+---------+
#        | 1          | 1       | n       |
#        +------------+---------+---------+
#        | float      | float   |         | 
#        +------------+---------+---------+
     
#     """

#     def __init__(self, N=1, D=[1, 1], *inputs, x0=None, verbose=False, **kwargs):
#         r"""
#         :param N: numerator coefficients, defaults to 1
#         :type N: array_like, optional
#         :param D: denominator coefficients, defaults to [1, 1]
#         :type D: array_like, optional
#         :param ``*inputs``: Optional incoming connections
#         :type ``*inputs``: Block or Plug
#         :param x0: initial states, defaults to zero
#         :type x0: array_like, optional
#         :param ``**kwargs``: common Block options
#         :return: A SCOPE block
#         :rtype: LTI_SISO instance

#         Create a SISO LTI block.

#         Describes the dynamics of a single-input single-output (SISO) linear
#         time invariant (LTI) system described by numerator and denominator
#         polynomial coefficients.

#         Coefficients are given in the order from highest order to zeroth 
#         order, ie. :math:`2s^2 - 4s +3` is ``[2, -4, 3]``.

#         Only proper transfer functions, where order of numerator is less
#         than denominator are allowed.

#         The order of the states in ``x0`` is consistent with controller canonical
#         form.

#         Examples::

#             LTI_SISO(N=[1, 2], D=[2, 3, -4])

#         is the transfer function :math:`\frac{s+2}{2s^2+3s-4}`.
#         """
#         #print('in SISO constscutor')

#         if not isinstance(N, list):
#             N = [N]
#         if not isinstance(D, list):
#             D = [D]
#         self.N = N
#         self.D = N
#         n = len(D) - 1
#         nn = len(N)
#         if x0 is None:
#             x0 = np.zeros((n,))
#         assert nn <= n, 'direct pass through is not supported'

#         # convert to numpy arrays
#         N = np.r_[np.zeros((len(D) - len(N),)), np.array(N)]
#         D = np.array(D)

#         # normalize the coefficients to obtain
#         #
#         #   b_0 s^n + b_1 s^(n-1) + ... + b_n
#         #   ---------------------------------
#         #   a_0 s^n + a_1 s^(n-1) + ....+ a_n

#         # normalize so leading coefficient of denominator is one
#         D0 = D[0]
#         D = D / D0
#         N = N / D0

#         A = np.eye(len(D) - 1, k=1)  # control canonic (companion matrix) form
#         A[-1, :] = -D[1:]

#         B = np.zeros((n, 1))
#         B[-1] = 1

#         C = (N[1:] - N[0] * D[1:]).reshape((1, n))

#         if verbose:
#             print('A=', A)
#             print('B=', B)
#             print('C=', C)

#         super().__init__(A=A, B=B, C=C, x0=x0, **kwargs)
#         self.type = 'LTI'


# if __name__ == "__main__":

#     import pathlib
#     import os.path

#     exec(open(os.path.join(pathlib.Path(
#         __file__).parent.absolute(), "test_transfers.py")).read())
