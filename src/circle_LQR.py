import numpy as np
import control as ct
from utils.circle_utils import M, G, e, radius, phi_d, radius
from utils.circle_utils import get_phi_vals
from utils.circle_utils import visualize_control

print("radius :", radius, "; phi_d :", phi_d)

# to see this system definition go see documentation
A = np.array([[0, 1], [0, 0]])
B = np.array([0, 1])
C = np.array([1, 0])
sys = ct.ss(A, B, C, 0, name='sys')

print(sys)

Q = np.eye(sys.nstates)
R = np.eye(sys.ninputs)

# get optimal K for control function
K, _, _ = ct.lqr(sys, Q, R)
B = B.reshape(2, 1)

print('K: ' + str(K))
print(K.shape, B.shape)

# feedforward gain to track the reference
kr = (-1 / (C @ np.linalg.inv(A - B @ K) @ B))
print('k_r: ' + str(kr))

# closed loop system
A_cl = A - B @ K
B_cl = B * kr
clsys = ct.ss(A_cl, B_cl, C, 0)
print(clsys)

# reference and temporal interval
r = 0
Tf = 50
tvec = np.linspace(0, Tf, 700)
U = r * np.ones_like(tvec)

# initial condition
X_0 = np.array([0, phi_d])

time, output, state = ct.input_output_response(clsys, tvec, U, X0=X_0, return_x=True)

# control signal (1D for plotting)
u_signal = -K @ state + kr * U
u_signal = u_signal.flatten()

# angle on the circular orbit (constant angular velocity)
phi_vals = get_phi_vals(time)
#print(phi_vals)

vs = visualize_control(time, phi_vals, radius, state, u_signal, r)
vs.control_graph()
vs.sattelite_video()