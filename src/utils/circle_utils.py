import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, Rectangle
from matplotlib.lines import Line2D
from matplotlib.transforms import Affine2D

# constants
M = 5.97 * 10**(24)
G = 6.67 * 10**(-11)

#computed value (see documentation for equation)
e = (G*M*10**(5))**(1/2) #~10**(-10)

# physical circular orbit solution
radius = e**2 / (M*G)
phi_d = e / radius**2         # angular velocity e / r^2

def get_phi_vals(time):
    return phi_d * np.asarray(time)


class visualize_control():
    def __init__(self, time, phi_vals, radius, state, u_signal, r=0):
        self.time = time
        self.phi_vals = phi_vals
        self.radius = radius
        self.state = state
        self.u_signal = u_signal
        self.r = r
        self.path = "src/visuals/visual_circle"

    def control_graph(self):
        plt.figure()
        plt.plot(self.time, self.u_signal, label="u_signal")
        plt.plot(self.time, self.state[0], label="state")
        plt.plot([self.time[0], self.time[-1]], [self.r, self.r], '--')
        plt.legend(['u_signal', 'state'])
        plt.ylabel("Output")
        plt.xlabel("Time $t$ [sec]")
        plt.title("Baseline controller step response")
        plt.savefig(f"{self.path}/cyclic_control.png")
        plt.close()
        return

    def sattelite_video(self):
        R = self.radius
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(-5 - 1.1 * R, 5 + 1.1 * R)
        ax.set_ylim(-5 - 1.1 * R, 5 + 1.1 * R)
        ax.set_aspect('equal'); ax.grid(True)
        ax.set_title("Satellite Attitude Control & Orbit")

        ax.add_patch(Circle((0, 0), 1.0, color='dodgerblue', alpha=0.7))
        ax.add_patch(Circle((0, 0), R, color='gray', ls='--', fill=False))

        # Satellite artists (defined around the origin, moved via transforms)
        sat_body = Rectangle((-0.2*R, -0.2*R), 0, 0, fc='orange', ec='black', zorder=3)
        panel = Line2D([-0.1*R, 0.1*R], [0, 0], color='cornflowerblue', lw=5,
                       solid_capstyle='round', zorder=2)
        # Ghost showing the desired orientation (theta = 0 -> aligned with orbit frame)
        ghost = Line2D([-0.1*R, 0.1*R], [0, 0], color='green', lw=2, ls=':', zorder=1)
        ax.add_patch(sat_body); ax.add_line(panel); ax.add_line(ghost)

        control_text = ax.text(0.55, 0.90, '', transform=ax.transAxes, fontsize=10,
                               bbox=dict(boxstyle='round', facecolor='white',
                                         edgecolor='gray', alpha=0.8))

        def init():
            control_text.set_text('')
            return sat_body, panel, ghost, control_text

        def animate(i):
            phi = self.phi_vals[i]
            theta = self.state[0, i] 
            x_pos = R * np.cos(phi)
            y_pos = R * np.sin(phi)

            # Attitude = orbit frame angle + control-driven error theta
            actual = Affine2D().rotate(phi + np.pi/2 + theta).translate(x_pos, y_pos) + ax.transData
            desired = Affine2D().rotate(phi + np.pi/2).translate(x_pos, y_pos) + ax.transData

            sat_body.set_transform(actual)
            panel.set_transform(actual)
            ghost.set_transform(desired)

            control_text.set_text(f'u(t) = {self.u_signal[i]: .3f}\n'
                                  f'θ = {np.degrees(theta): .1f}°')
            return sat_body, panel, ghost, control_text

        ani = animation.FuncAnimation(fig, animate, init_func=init,
                                      frames=len(self.time), interval=40, blit=False)

        writer = animation.FFMpegWriter(fps=25, bitrate=2000)
        ani.save(f'{self.path}/satellite_cyclic.mp4', writer=writer)
        plt.close(fig)
        print("Saved satellite_cyclic.mp4")