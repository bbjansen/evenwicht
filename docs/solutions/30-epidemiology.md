<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 30: Epidemiology & Population Dynamics

**Exercise 30.1.** Logistic growth.

??? success "Solution"

    $r = 0.5$ hr$^{-1}$, $K = 10^6$, $N_0 = 100$.

    The logistic solution is

    $$N(t) = \frac{K}{1 + \left(\frac{K}{N_0} - 1\right)e^{-rt}} = \frac{10^6}{1 + 9999 \cdot e^{-0.5t}}.$$

    **(a)** At $t = 10$: $e^{-5} = 0.006738$. $N(10) = 10^6/(1 + 9999 \times 0.006738) = 10^6/(1 + 67.37) = 10^6/68.37 = 14{,}627$ cells.

    **(b)** Half carrying capacity: $N = K/2 = 500{,}000$. Setting $N(t^*) = K/2$: $1 + 9999 e^{-0.5t^*} = 2$, so $e^{-0.5t^*} = 1/9999$. $t^* = -2\ln(1/9999) = 2\ln(9999) = 2 \times 9.2103 = 18.42$ hours.

    **(c)** $dN/dt = rN(1-N/K)$, maximised when $N = K/2$ (vertex of the quadratic). Maximum rate: $dN/dt|_{\max} = r \cdot K/2 \cdot 1/2 = rK/4 = 0.5 \times 10^6/4 = 125{,}000$ cells/hour, occurring at $t^* = 18.42$ hours.

    $\square$

---

**Exercise 30.2.** SIR model analysis.

??? success "Solution"

    $\beta = 0.4$, $\gamma = 0.2$. $R_0 = \beta/\gamma = 0.4/0.2 = 2.0$.

    Herd immunity threshold: $H = 1 - 1/R_0 = 1 - 1/2 = 0.50$ (50% must be immune).

    With 60% vaccinated (perfectly effective): the effective susceptible fraction is $S_{\text{eff}} = 1 - 0.60 = 0.40$. The effective reproduction number is $R_e = R_0 \times S_{\text{eff}} = 2.0 \times 0.40 = 0.80$.

    Since $R_e = 0.80 < 1$, the disease **cannot spread**. Each infected individual replaces themselves with only 0.80 new infections on average, so an outbreak will die out.

    $\square$

---

**Exercise 30.3.** Disease with $R_0 = 5$, mean infectious period 4 days.

??? success "Solution"

    $\gamma = 1/4 = 0.25$ day$^{-1}$. $\beta = R_0 \cdot \gamma = 5 \times 0.25 = 1.25$ day$^{-1}$.

    In a fully susceptible population ($S \approx N$), early SIR dynamics give exponential growth with rate $\lambda = \beta - \gamma = 1.25 - 0.25 = 1.00$ day$^{-1}$.

    Alternatively, from the SIR linearization: $\lambda = \gamma(R_0 - 1) = 0.25 \times 4 = 1.00$ day$^{-1}$. Consistent.

    Doubling time: $T_d = \ln 2/\lambda = 0.6931/1.00 = 0.693$ days $\approx 16.6$ hours.

    $\square$

---

**Exercise 30.4.** Lotka–Volterra with $\alpha=2$, $\beta=0.5$, $\delta=0.2$, $\gamma=0.8$.

??? success "Solution"

    Equations: $\dot{x} = \alpha x - \beta xy = 2x - 0.5xy$, $\dot{y} = \delta xy - \gamma y = 0.2xy - 0.8y$.

    Coexistence equilibrium: $\dot{x} = 0 \Rightarrow x(\alpha - \beta y) = 0 \Rightarrow y^* = \alpha/\beta = 2/0.5 = 4$. $\dot{y} = 0 \Rightarrow y(\delta x - \gamma) = 0 \Rightarrow x^* = \gamma/\delta = 0.8/0.2 = 4$.

    Equilibrium: $(x^*, y^*) = (4, 4)$.

    The Jacobian at the coexistence equilibrium is:

    $$J = \begin{bmatrix} \alpha - \beta y^* & -\beta x^* \\ \delta y^* & \delta x^* - \gamma \end{bmatrix} = \begin{bmatrix} 0 & -2 \\ 0.8 & 0 \end{bmatrix}.$$

    Eigenvalues: $\lambda^2 = -(-2)(0.8) = -1.6$, so $\lambda = \pm j\sqrt{1.6} = \pm 1.265j$.

    The eigenvalues are purely imaginary, confirming a **centre** (neutrally stable). The period of small oscillations is:

    $$T = \frac{2\pi}{\sqrt{\alpha\gamma}} = \frac{2\pi}{\sqrt{2 \times 0.8}} = \frac{2\pi}{\sqrt{1.6}} = \frac{2\pi}{1.265} = 4.97 \text{ (time units)}.$$

    $\square$

---

**Exercise 30.5.** Derive the final size equation.

??? success "Solution"

    In the SIR model, dividing $dS/dt = -\beta SI$ by $dR/dt = \gamma I$ gives:

    $$\frac{dS}{dR} = -\frac{\beta S}{\gamma} = -R_0 \frac{S}{N}.$$

    Integrating from $t=0$ to $t=\infty$: $S_\infty - S_0 = -\frac{R_0}{N}\int_0^{R_\infty} S\,dR$. Since $dS/dR$ depends only on $S$, the equation can be integrated:

    $$\int_{S_0}^{S_\infty}\frac{dS}{S} = -\frac{R_0}{N}\int_0^{R_\infty}dR,$$

    giving $\ln(S_\infty/S_0) = -R_0 R_\infty/N$. Since the epidemic ends with $I_\infty = 0$ and $S + I + R = N$, $R_\infty = N - S_\infty$. Thus:

    $$\ln\left(\frac{S_0}{S_\infty}\right) = R_0\frac{S_0 - S_\infty}{N}.$$

    $\square$

    For $R_0 = 3$, $S_0 = N$: $\ln(N/S_\infty) = 3(1 - S_\infty/N)$. Let $s = S_\infty/N$: $-\ln s = 3(1-s)$, i.e., $\ln s + 3(1-s) = 0$. Solving numerically (Newton's method with $s_0 = 0.1$): $s \approx 0.0595$.

    Fraction ultimately infected: $1 - s = 1 - 0.0595 = 0.9405 = 94.1\%$.

---

**Exercise 30.6.** SIR with vital dynamics stability analysis.

??? success "Solution"

    With births and deaths at rate $\mu$: $\dot{S} = \mu N - \beta SI - \mu S$, $\dot{I} = \beta SI - \gamma I - \mu I$, $\dot{R} = \gamma I - \mu R$.

    Disease-free equilibrium (DFE): $I^* = 0$, $R^* = 0$, $S^* = N$.

    Jacobian at DFE (considering $S$, $I$ subsystem with $S + I + R = N$):

    $$J_{\text{DFE}} = \begin{bmatrix} -\mu & -\beta N \\ 0 & \beta N - (\gamma + \mu) \end{bmatrix}.$$

    Eigenvalues: $\lambda_1 = -\mu < 0$ and $\lambda_2 = \beta N - (\gamma + \mu) = (\gamma + \mu)(R_0 - 1)$ where $R_0 = \beta N/(\gamma + \mu)$.

    When $R_0 > 1$: $\lambda_2 > 0$, so the DFE is **unstable**. $\checkmark$

    The endemic equilibrium $S^{**} = N/R_0$, $I^{**} = \mu(R_0-1)/\beta$. Computing the Jacobian at this point and evaluating the eigenvalues shows that the trace is $-\mu R_0 < 0$ and determinant is $\mu(\gamma+\mu)(R_0-1) > 0$ when $R_0 > 1$, confirming both eigenvalues have negative real parts. The endemic equilibrium is **locally stable** when $R_0 > 1$. $\square$

---

**Exercise 30.7.** Estimating growth rate from case data.

??? success "Solution"

    Daily new cases: $[12, 15, 18, 23, 29, 37, 45, 57, 72, 91]$ for $k = 1, \ldots, 10$.

    $\ln(c_k)$: $[2.485, 2.708, 2.890, 3.135, 3.367, 3.611, 3.807, 4.043, 4.277, 4.511]$.

    Linear regression of $\ln(c_k)$ on $k$: slope $= \hat{\lambda}$, intercept $= \hat{a}$.

    Using the formulas: $\bar{k} = 5.5$, $\overline{\ln c} = 3.483$, $\sum(k_i - \bar{k})(\ln c_i - \overline{\ln c}) = 18.617$, $\sum(k_i - \bar{k})^2 = 82.5$.

    $\hat{\lambda} = 18.617/82.5 = 0.226$ per day. Doubling time: $\ln 2/0.226 = 3.07$ days.

    **SIR estimate of $R_0$:** $R_0 = 1 + \lambda/\gamma = 1 + 0.226 \times 5 = 2.13$.

    **SEIR estimate of $R_0$:** With latent period $1/\sigma = 3$ days ($\sigma = 1/3$), $R_0 = (1 + \lambda/\gamma)(1 + \lambda/\sigma) = (1 + 0.226 \times 5)(1 + 0.226 \times 3) = 2.13 \times 1.678 = 3.57$.

    The SEIR estimate is higher because the latent period slows the observable exponential growth relative to the true transmission rate; accounting for this delay reveals a higher $R_0$.

    $\square$

---

**Exercise 30.8.** SEIR with vital dynamics: next-generation matrix and endemic equilibrium.

??? success "Solution"

    **(a)** DFE: Setting all derivatives to zero with $I=0$, $E=0$: $S^* = N$, $E^* = 0$, $I^* = 0$, $R^* = 0$.

    **(b)** The infected compartments are $E$ and $I$. The next-generation matrix $K = FV^{-1}$ where $F$ (new infections) and $V$ (transitions) are:

    $$F = \begin{bmatrix} 0 & \beta N \\ 0 & 0 \end{bmatrix}, \quad V = \begin{bmatrix} \sigma + \mu & 0 \\ -\sigma & \gamma + \mu \end{bmatrix}.$$

    $$V^{-1} = \frac{1}{(\sigma+\mu)(\gamma+\mu)}\begin{bmatrix} \gamma+\mu & 0 \\ \sigma & \sigma+\mu \end{bmatrix}.$$

    $$K = FV^{-1} = \begin{bmatrix} \frac{\beta N \sigma}{(\sigma+\mu)(\gamma+\mu)} & \frac{\beta N(\sigma+\mu)}{(\sigma+\mu)(\gamma+\mu)} \\ 0 & 0 \end{bmatrix}.$$

    $R_0 = \rho(K) = \frac{\beta\sigma N}{(\sigma+\mu)(\gamma+\mu)}$. $\square$

    **(c)** At the endemic equilibrium: $S^{**} = N/R_0$, $E^{**} = \frac{\mu(R_0-1)}{\beta}$, $I^{**} = \frac{\sigma\mu(R_0-1)}{\beta(\gamma+\mu)}$.

    **(d)** Using $R = N - S - E - I$ to reduce the system to three equations in $(S, E, I)$, the Jacobian at the endemic equilibrium $(S^{**}, E^{**}, I^{**})$ is

    $$J = \begin{bmatrix} -\beta I^{**} - \mu & 0 & -\beta S^{**} \\ \beta I^{**} & -(\sigma+\mu) & \beta S^{**} \\ 0 & \sigma & -(\gamma+\mu) \end{bmatrix}.$$

    Substituting $\beta S^{**} = (\sigma+\mu)(\gamma+\mu)/(\sigma) \cdot (1/N) \cdot N = (\sigma+\mu)(\gamma+\mu)/\sigma$ (from the endemic equilibrium condition) and $\beta I^{**} = \mu(R_0 - 1)$, the characteristic polynomial is cubic. The Routh–Hurwitz conditions guarantee stability (negative real parts) when $R_0 > 1$, but the discriminant condition for complex eigenvalues (oscillatory approach to equilibrium) depends on all parameter ratios and does not reduce to a simple closed-form threshold. For typical parameter values of endemic diseases such as measles ($R_0 \approx 15$, $\mu \approx 1/70$ yr$^{-1}$, $1/\sigma \approx 8$ days, $1/\gamma \approx 7$ days), numerical eigenvalue computation confirms complex eigenvalues with negative real parts, producing the observed multiannual epidemic cycles.

---
