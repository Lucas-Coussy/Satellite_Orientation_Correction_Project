import numpy as np
import control as ct
import matplotlib.pyplot as plt
from utils.ellipse_utils import M, G, e, s, p, ecc
from utils.ellipse_utils import radius, phi_dot, phi_sec
from utils.ellipse_utils import get_phi_vals

from utils.ellipse_utils import visualize_control

#to see this system definition go see documentation
A = np.array([[0,1],[0,0]])
B = np.array([0,1])
C = np.array([1,0])
sys = ct.ss(A, B, C, 0, name='sys')

print(sys)

Q = np.eye(sys.nstates)
R = np.eye(sys.ninputs)

#get optimal K for control function
K, _, _ = ct.lqr(sys, Q, R)
B = B.reshape(2,1)

print('K: '+str(K))
print(K.shape, B.shape)

kr = (-1 / (C @ np.linalg.inv(A - B @ K) @ B))
print('k_r: '+str(kr))

#compute closed loop control
A_cl = A - B @ K
B_cl = B * kr
clsys = ct.ss(A_cl, B_cl, C, 0)
print(clsys)

#get temporal interval
Tf = 50
tvec = np.linspace(0, Tf, 700)

#define initial condition
X_0 = np.array([0, phi_dot(0)])

#get solution of lqr control
time, output, state = ct.input_output_response(clsys, tvec, X0=X_0, return_x=True)

# get phi value integrated over time with euler method
phi_vals = get_phi_vals(time)

orbit = [radius(phi) for phi in phi_vals]
sma = max(orbit)
print("semi-major axis :", sma, " km")

#by adding the observed phi_sec of the sattelite to the value of control, 
#we correct the rotation of the sattelite due to the elliptic orbite compared to a cyclic one
#(cyclic one have a null phi_second term)
u_signal = -K @ abs((state + np.pi) % (2*np.pi) - np.pi) + phi_sec(phi_vals) 
u_signal = u_signal.flatten() 

#print("speed min/max:", speed.min(), speed.max())   

vs = visualize_control(time, phi_vals, orbit, sma, state, u_signal)
vs.control_graph()
vs.sattelite_video()
