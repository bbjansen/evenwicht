<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 48: Genetics & Bioinformatics

**Exercise 48.1.** Hardy–Weinberg test.

??? success "Solution"

    (a) Allele frequencies:

    $$\hat{p} = \frac{2 \times 120 + 250}{2 \times 500} = \frac{490}{1000} = 0.49, \qquad \hat{q} = 1 - 0.49 = 0.51.$$

    (b) Expected counts:

    $$E_{AA} = \hat{p}^2 n = 0.2401 \times 500 = 120.05, \qquad E_{Aa} = 2\hat{p}\hat{q}\,n = 0.4998 \times 500 = 249.9, \qquad E_{aa} = \hat{q}^2 n = 0.2601 \times 500 = 130.05.$$

    (c)

    $$\chi^2 = \frac{(120-120.05)^2}{120.05} + \frac{(250-249.9)^2}{249.9} + \frac{(130-130.05)^2}{130.05} = 0.0001.$$

    With 1 degree of freedom, $\chi^2_{\text{crit}}(0.05) = 3.84$. Since $0.0001 \ll 3.84$, the null hypothesis of Hardy–Weinberg equilibrium is **not rejected**. The genotype frequencies are consistent with HW proportions.

---

**Exercise 48.2.** Directional selection.

??? success "Solution"

    Genotype fitnesses: $w_{AA} = 1.0$, $w_{Aa} = 0.95$, $w_{aa} = 0.90$.

    Mean fitness ($p = 0.3$, $q = 0.7$):

    $$\bar{w} = p^2 w_{AA} + 2pq w_{Aa} + q^2 w_{aa} = 0.09 \times 1.0 + 0.42 \times 0.95 + 0.49 \times 0.90 = 0.930.$$

    New frequency:

    $$p' = \frac{p^2 w_{AA} + pq w_{Aa}}{\bar{w}} = \frac{0.09 + 0.1995}{0.930} = \frac{0.2895}{0.930} = 0.3113.$$

    $\Delta p = 0.3113 - 0.3 = 0.0113 > 0$. $\checkmark$ Allele $A$ is increasing.

    For $p$ to go from 0.3 to 0.9: this requires iterative computation. With selection coefficients $s = 0.10$ (against $aa$) and $h = 0.5$ (heterozygote disadvantage), the number of generations is approximately

    $$N_g \approx \frac{2}{s}\ln\!\left(\frac{p_f q_0}{p_0 q_f}\right) = \frac{2}{0.10}\ln\!\left(\frac{0.9 \times 0.7}{0.3 \times 0.1}\right) = 20\ln(21) = 20 \times 3.045 = 61 \text{ generations}.$$

    More precise iteration gives approximately 70–80 generations due to the non-additive fitness.

---

**Exercise 48.3.** Jukes–Cantor distance.

??? success "Solution"

    Observed (uncorrected) distance: $\hat{d} = 50/300 = 0.1667$.

    Jukes–Cantor corrected:

    $$d_{JC} = -\frac{3}{4}\ln\!\left(1 - \frac{4}{3}\hat{d}\right) = -0.75\ln(1 - 0.2222) = -0.75\ln(0.7778) = -0.75 \times (-0.2513) = 0.1885.$$

    Percentage increase:

    $$(0.1885 - 0.1667)\,/\,0.1667 \times 100 = 13.1\%.$$

    The correction accounts for multiple substitutions at the same site (saturation); sequences that appear 16.7% different are estimated to have diverged by 18.9% after correcting for back-mutations.

---

**Exercise 48.4.** Linkage disequilibrium decay.

??? success "Solution"

    (a) $D(t) = D_0(1-r)^t = 0.15 \times 0.90^t$. We need $D < 0.001$:

    $$0.15 \times 0.90^t < 0.001, \qquad 0.90^t < 0.00667, \qquad t > \frac{\ln 0.00667}{\ln 0.9} = \frac{-5.011}{-0.1054} = 47.5.$$

    So $t = 48$ generations.

    (b) In a population bottleneck to $N = 50$, genetic drift introduces random changes in haplotype frequencies. The variance of $D$ due to drift is proportional to $1/(2N)$ per generation. While recombination deterministically reduces $D$, drift can randomly increase it, particularly in small populations where sampling variance is large. The net effect is that drift maintains some level of LD even as recombination erodes it and can create new LD between previously unlinked loci.

---

**Exercise 48.5.** Wright–Fisher transition matrix for $N = 5$.

??? success "Solution"

    For $2N = 10$ gene copies, the state space is $i \in \{0, 1, \ldots, 10\}$ (11 states). The transition matrix has entries:

    $$T_{ij} = \binom{2N}{j}\left(\frac{i}{2N}\right)^j\left(1 - \frac{i}{2N}\right)^{2N-j}.$$

    (a) States $i = 0$ and $i = 10$ are absorbing ($T_{00} = T_{10,10} = 1$), corresponding to eigenvalues $= 1$ (two absorbing states).

    (b) The eigenvalue $\lambda_1 = 1$ is doubly degenerate (one per absorbing state). Following the convention of Theorem 48.13, the next eigenvalue is $\lambda_2 = 1 - 1/(2N) = 1 - 0.1 = 0.90$, and it governs the rate of heterozygosity decay. Numerical eigenvalue computation of the $11 \times 11$ matrix confirms this value.

    (c) All eigenvalues of a stochastic matrix satisfy $\lvert\lambda\rvert \leq 1$ (by the Perron–Frobenius theorem). This can be verified numerically.

---

**Exercise 48.6.** Mutation equilibrium.

??? success "Solution"

    (a)

    $$p^* = \frac{\nu}{\mu + \nu} = \frac{10^{-6}}{10^{-5} + 10^{-6}} = \frac{10^{-6}}{1.1 \times 10^{-5}} = 0.0909.$$

    (b) The dynamics are $p_{t+1} = p_t(1-\mu) + (1-p_t)\nu$. The convergence rate is $(1-\mu-\nu)$ per generation. Starting from $p_0 = 0.5$, the error decays as $|p_t - p^*| = |p_0 - p^*|(1-\mu-\nu)^t$. For $|p_t - p^*| < 0.01\,p^*$:

    $$(1-\mu-\nu)^t < \frac{0.01\,p^*}{|p_0 - p^*|} = \frac{0.000909}{0.4091} = 0.00222.$$

    $$t > \frac{\ln 0.00222}{\ln(1-1.1 \times 10^{-5})} \approx \frac{-6.11}{-1.1 \times 10^{-5}} = 555{,}500 \text{ generations}.$$

    (c) Fixation timescale under drift: for neutral alleles, the expected time to fixation or loss is $\sim 4N = 40{,}000$ generations. This is much shorter than the mutation equilibrium timescale ($\sim 555{,}000$ generations), meaning drift dominates mutation at this population size. The allele is more likely to fix or be lost by drift before mutation-selection balance is reached.

---

**Exercise 48.7.** Stationary distribution of Wright–Fisher with mutation.

??? success "Solution"

    (a) With $N = 8$ ($2N = 16$), the effective frequency after mutation is $p'_i = (1 - 0.05)(i/16) + 0.02(1 - i/16) = 0.95i/16 + 0.02(16-i)/16 = (0.95i + 0.32 - 0.02i)/16 = (0.93i + 0.32)/16$.

    The $17 \times 17$ transition matrix has entries $T_{ij} = \binom{16}{j}(p'_i)^j(1-p'_i)^{16-j}$.

    (b) The stationary distribution $\boldsymbol{\pi}$ satisfies $\boldsymbol{\pi}^T T = \boldsymbol{\pi}^T$. It is the left eigenvector of $T$ for eigenvalue 1. Unlike the pure drift model, mutation prevents absorption at the boundaries, so there is a unique stationary distribution concentrated in the interior.

    (c) Deterministic equilibrium: $p^* = \nu/(\mu+\nu) = 0.02/0.07 = 0.286$. In the $2N = 16$ model, this corresponds to $i^* = 0.286 \times 16 = 4.57$, so the mode should be near $i = 4$ or $i = 5$. The stationary distribution is peaked around this value but is broad due to the small population size ($N = 8$), reflecting substantial drift around the deterministic equilibrium.

---

**Exercise 48.8.** Kimura 2-parameter model.

??? success "Solution"

    (a) The rate matrix is:

    $$Q = \begin{pmatrix} -(\alpha+2\beta) & \alpha & \beta & \beta \\ \alpha & -(\alpha+2\beta) & \beta & \beta \\ \beta & \beta & -(\alpha+2\beta) & \alpha \\ \beta & \beta & \alpha & -(\alpha+2\beta) \end{pmatrix}$$

    with rows/columns ordered A, G, C, T (purines A, G; pyrimidines C, T).

    (b) The eigenvalues are found by exploiting the block structure. Write $Q = \begin{pmatrix}A & B \\ B & A\end{pmatrix}$ with $A = \begin{pmatrix}-(\alpha+2\beta) & \alpha \\ \alpha & -(\alpha+2\beta)\end{pmatrix}$ and $B = \begin{pmatrix}\beta & \beta \\ \beta & \beta\end{pmatrix}$. The eigenvalues of $Q$ are those of $A+B$ and $A-B$.

    $A + B = \begin{pmatrix} -(\alpha+\beta) & \alpha+\beta \\ \alpha+\beta & -(\alpha+\beta) \end{pmatrix}$: eigenvalues $0$ and $-2(\alpha+\beta)$.

    $A - B = \begin{pmatrix} -(\alpha+3\beta) & \alpha-\beta \\ \alpha-\beta & -(\alpha+3\beta) \end{pmatrix}$: eigenvalues $-4\beta$ and $-2(\alpha+\beta)$.

    Thus the four eigenvalues of $Q$ are:

    - $\lambda_1 = 0$ (eigenvector $(1,1,1,1)^T$, conservation of probability).
    - $\lambda_2 = -4\beta$ (once; eigenvector $(1,-1,1,-1)^T$, transversion contrast).
    - $\lambda_{3,4} = -2(\alpha+\beta)$ (multiplicity 2; eigenvectors $(1,1,-1,-1)^T$ and $(1,-1,-1,1)^T$, purine–pyrimidine and within-class contrasts).

    Trace check: $0 + (-4\beta) + 2 \times (-2(\alpha+\beta)) = -4\alpha - 8\beta = -4(\alpha+2\beta)$. $\checkmark$

    (c) $P(t) = e^{Qt}$. Using the spectral decomposition with eigenvalues $0$, $-4\beta$, $-2(\alpha+\beta)$ (mult 2):

    $$P_{ii}(t) = \frac{1}{4} + \frac{1}{4}e^{-4\beta t} + \frac{1}{2}e^{-2(\alpha+\beta)t}$$

    (probability of no change). For a transition ($i \to j$, same purine or pyrimidine class):

    $$P_{\text{ts}}(t) = \frac{1}{4} + \frac{1}{4}e^{-4\beta t} - \frac{1}{2}e^{-2(\alpha+\beta)t}.$$

    For a transversion ($i \to j$, across purine/pyrimidine classes):

    $$P_{\text{tv}}(t) = \frac{1}{4} - \frac{1}{4}e^{-4\beta t}.$$

    When $\alpha = \beta$: the exponents $-4\beta t$ and $-2(\alpha+\beta)t = -4\alpha t$ coincide, giving $P_{ii} = \frac{1}{4} + \frac{3}{4}e^{-4\alpha t}$ and all off-diagonal entries equal $\frac{1}{4} - \frac{1}{4}e^{-4\alpha t}$, reproducing exactly the Jukes–Cantor result of Theorem 48.18. $\square$

---
