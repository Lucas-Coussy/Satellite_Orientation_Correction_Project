# On LQR 

LQR systems are composed of three variables, $u$ which is the control applied to our system, $x$ which represent the state of our system and $\dot{x}$ which is the derivative of our state.

Mathematically, $x$ is a functions of $\mathbb{R}_{+} \rightarrow \mathbb{R}^n$ and $u$ a function of $\mathbb{R}_{+} \rightarrow \mathbb{R}^m$ and $\dot{x} = \frac{dx}{dt}$ which by definition is 

$$
\begin{equation*} 

\frac{dx}{dt} = 
\begin{pmatrix}
\frac{dx_1}{dt} \\
\frac{dx_2}{dt} \\
\vdots \\
\frac{dx_n}{dt} \\
\end{pmatrix}

\end{equation*}
$$

Then, an hypothesis is made on $\dot{x}$ being a function of $u$ and $x$ and being linear in respect to them, thus  $\dot{x}$ can be written :

$$ 
\begin{equation} 
\dot{x} = A x + B u 
\end{equation}
$$ 

where $A \in \mathbb{M}_{n,n}$ and $B \in \mathbb{M}_{n,m}$.

Then the **LQR** define this quantity :

$$ 
\begin{equation} 
J = \int_{0}^{\infty} x^{T}Qx + u^{T}Ru \, dt
\end{equation}
$$

Where $Q$ and $R$ are symetrical definit semi positive matrices (i.e $Q = Q^{T}$, $R = R^{T}$ and $Q \succeq 0$, $R \succeq 0$).

The objectiv of LQR is to solve the following equation :

$$
\begin{equation} 
\inf_{u} J = \int_{0}^{\infty} x^{T}Qx + u^{T}Ru \, dt \quad \textit{with} \quad \forall t \in \mathbb{R}_{+}, \, \dot{x}(t) = A x(t) + B u(t) 

\end{equation} 
$$

To find such a $u$, the approach is to solve the Hamilton Jacobi Equation of our equation above, for this, an approach is to turn HJB into a Riccati equation and solve that form as in this [course](https://underactuated.mit.edu/lqr.html).

# Of our particular case

