import numpy as np

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, Rectangle, Ellipse, FancyArrowPatch
from matplotlib.lines import Line2D
from matplotlib.transforms import Affine2D

# constants
M = 5.97 * 10**(24)
G = 6.67 * 10**(-11)

#computed value (see documentation for equation)
# e = (G*M*10**(7))**(1/2) #~10**(10) plus réaliste en terme d'axe semi majeur et mineur
e = (G*M*10**(5))**(1/2) #~10**(9) meilleur pour la visualisation
s = G*M/(2*e**2)

#compute constant p and ecc of elliptic solution function
p   = e**2 / (G*M)
ecc = s * e**2 / (G*M)

#get semi radius of ellipse
a = p / (1 - ecc**2)
b = p / np.sqrt(1 - ecc**2)

def radius(phi):
    return 1/(s*np.cos(phi) + G*M/e**2)

def phi_dot(phi):
    return e/radius(phi)**2 

def phi_sec(phi):
    return -2*e*phi_dot(phi)*s*np.sin(phi)*(s*np.cos(phi) + G*M/e**2)

# def get_phi_vals(time):
#     """
#     Compute phi_vals for a list of time value recursively by applying euler method.
#     Beware to take recursion limit into account.
#     """
#     if all(time == [0]):
#         return [0]
#     else:
#         phi_vals = get_phi_vals(time[0:-1])
#         return phi_vals + [(phi_vals[-1] + phi_dot(phi_vals[-1])*(time[-1]-time[-2])) % (2*np.pi)]


def get_phi_vals(time):
    """
    Compute phi_vals for a list of time value by applying euler method.
    """
    phi = np.zeros(len(time))
    for k in range(1, len(time)):
        phi[k] = (phi[k-1] + phi_dot(phi[k-1])*(time[k]-time[k-1])) % (2*np.pi)
    return phi

def get_speed(phi_vals, orbit, h = 1e-6):
    #get phi_value list
    phi_arr = np.array(phi_vals)
    #compute dr/dphi approximation
    dr_dphi = np.array([(radius(f + h) - radius(f - h)) / (2*h) for f in phi_arr])
    #get radius list
    r_arr   = np.array(orbit)
    #get phi_dots list
    pdot    = np.array([phi_dot(f) for f in phi_arr])
    # velocity = phi_dot * ( r' * e_r + r * e_phi ); see documentation for formula
    vx = pdot * (dr_dphi*np.cos(phi_arr) - r_arr*np.sin(phi_arr))
    vy = pdot * (dr_dphi*np.sin(phi_arr) + r_arr*np.cos(phi_arr))
    speed = np.hypot(vx, vy)
    return vx, vy, speed

class visualize_control():
    def __init__(self, time, phi_vals, orbit, sma, state, u_signal):
        self.time = time  
        self.phi_vals = phi_vals  
        self.orbit = orbit
        self.sma = sma
        self.state = state
        self.u_signal = u_signal
        self.path = "src/visuals/visual_ellipse"

        #scale based on max_speed
        vx, vy, speed = get_speed(self.phi_vals, self.orbit)
        scale = 0.3 * self.sma / speed.max()      # longest arrow = 30% of sma
        self.vx = vx * scale
        self.vy = vy * scale

    def control_graph(self):
        plt.plot(self.time, phi_sec(self.phi_vals), label="phi_sec")
        plt.plot(self.time, abs((self.state[0] + np.pi) % (2*np.pi) - np.pi), label="state")
        plt.plot(self.time, self.u_signal, label="u_signal")
        plt.legend(['phi_sec', 'state', 'u_signal'])
        plt.ylabel("Output")
        plt.xlabel("Time $t$ [sec]")
        plt.title("Baseline controller step response")
        plt.savefig(f"{self.path}/ellipse_control.png")
        return

    def sattelite_video(self):
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(-1 -1.1*self.sma, 1 + 1.1*self.sma); ax.set_ylim(-1 -1.1*self.sma, 1 + 1.1*self.sma)
        ax.set_aspect('equal'); ax.grid(True)
        ax.set_title("Satellite Attitude Control & Orbit")

        ax.add_patch(Circle((0, 0), 0.2*a, color='dodgerblue', alpha=0.7))

        orbit_patch = Ellipse(xy=(-a*ecc, 0),      # center, not focus
                            width=2*a,           # full length, hence 2a
                            height=2*b,          # full length, hence 2b
                            angle=0,
                            edgecolor='red', facecolor='none', lw=2)
        ax.add_patch(orbit_patch)

        # Satellite artists (defined around the origin, moved via transforms)
        panel    = Line2D([-0.1*a, 0.1*a], [0, 0], color='cornflowerblue', lw=5,
                        solid_capstyle='round', zorder=2)
        # Ghost showing the desired orientation (theta = 0 -> aligned with orbit frame)
        ghost    = Line2D([-0.1*a, 0.1*a], [0, 0], color='green', lw=2, ls=':', zorder=1)
        ax.add_line(panel); ax.add_line(ghost)

        tangent = FancyArrowPatch((0, 0), (1, 1), arrowstyle='-|>',
                                mutation_scale=15, color='purple', lw=2, zorder=4)
        ax.add_patch(tangent)

        control_text = ax.text(0.55, 0.90, '', transform=ax.transAxes, fontsize=10,
                            bbox=dict(boxstyle='round', facecolor='white',
                                        edgecolor='gray', alpha=0.8))

        def init():
            control_text.set_text('')
            return panel, ghost, tangent, control_text

        def animate(i):
            phi   = self.phi_vals[i]
            rad   = self.orbit[i]
            theta = self.state[0, i] % 2*np.pi
            x_pos = rad * np.cos(phi)
            y_pos = rad * np.sin(phi)

            # if i == 0:
            #     print("x : ", radius(0) * np.cos(0), "y : ", radius(0) * np.sin(0))
            #     print("x : ", radius(-np.pi) * np.cos(-np.pi), "y : ", radius(-np.pi) * np.sin(-np.pi))
            #     print("x : ", radius(np.pi/2) * np.cos(np.pi/2), "y : ", radius(np.pi/2) * np.sin(np.pi/2))
            #     print("x : ", radius(-np.pi/2) * np.cos(-np.pi/2), "y : ", radius(-np.pi/2) * np.sin(-np.pi/2))

            # Attitude = orbit frame angle + control-driven error theta
            actual  = Affine2D().rotate(phi + np.pi/2 + theta).translate(x_pos, y_pos) + ax.transData
            desired = Affine2D().rotate(phi + np.pi/2).translate(x_pos, y_pos) + ax.transData

            # update speed vector
            tangent.set_positions((x_pos, y_pos), (x_pos + self.vx[i], y_pos + self.vy[i]))    

            panel.set_transform(actual)
            ghost.set_transform(desired)

            control_text.set_text(f'u(t) = {self.u_signal[i]: .3f}\n'
                                f'θ = {np.degrees(theta): .1f}°')
            return panel, ghost, tangent, control_text

        ani = animation.FuncAnimation(fig, animate, init_func=init,
                                    frames=len(self.phi_vals), interval=40, blit=False)

        writer = animation.FFMpegWriter(fps=25, bitrate=2000)
        # ani.save(f'{self.path}/satellite_elliptic.mp4', writer=writer)
        ani.save(f'{self.path}/satellite_elliptic.gif', writer=writer)
        print("Saved satellite_elliptic.gif")
