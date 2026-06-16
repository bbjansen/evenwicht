<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Chapter 37: Cryptography & Number Theory

**Exercise 37.1.** Compute $\gcd(252, 198)$ using the Euclidean algorithm. Then find integers $s$ and $t$ such that $252s + 198t = \gcd(252, 198)$.

??? success "Solution"

    Apply the Euclidean algorithm:

    $$\begin{aligned}
    252 &= 1 \times 198 + 54, \\
    198 &= 3 \times 54 + 36, \\
    54 &= 1 \times 36 + 18, \\
    36 &= 2 \times 18 + 0.
    \end{aligned}$$

    The last nonzero remainder is $\gcd(252, 198) = 18$.

    Back-substitution to find the Bézout coefficients:

    $$\begin{aligned}
    18 &= 54 - 1 \times 36, \\
    18 &= 54 - 1 \times (198 - 3 \times 54) = 4 \times 54 - 198, \\
    18 &= 4 \times (252 - 198) - 198 = 4 \times 252 - 5 \times 198.
    \end{aligned}$$

    So $s = 4$ and $t = -5$.

    Verification: $4 \times 252 + (-5) \times 198 = 1008 - 990 = 18$.

    $\square$

---

**Exercise 37.2.** Compute $\varphi(100)$, $\varphi(97)$ and $\varphi(84)$.

??? success "Solution"

    For $\varphi(100)$: $100 = 2^2 \times 5^2$. Using the formula $\varphi(p^k) = p^{k-1}(p-1)$ and multiplicativity:

    $$\varphi(100) = \varphi(2^2)\varphi(5^2) = 2^1(2-1) \times 5^1(5-1) = 2 \times 20 = 40.$$

    For $\varphi(97)$: $97$ is prime, so $\varphi(97) = 97 - 1 = 96$.

    For $\varphi(84)$: $84 = 2^2 \times 3 \times 7$.

    $$\varphi(84) = \varphi(2^2)\varphi(3)\varphi(7) = 2(1) \times 2 \times 6 = 24.$$

    $\square$

---

**Exercise 37.3.** Compute $7^{222} \bmod 11$.

??? success "Solution"

    By Fermat's little theorem, $7^{10} \equiv 1 \pmod{11}$ since $11$ is prime and $\gcd(7, 11) = 1$.

    Divide the exponent by 10: $222 = 22 \times 10 + 2$.

    Therefore:

    $$7^{222} = (7^{10})^{22} \times 7^2 \equiv 1^{22} \times 49 \equiv 49 \pmod{11}.$$

    Now $49 = 4 \times 11 + 5$, so $49 \equiv 5 \pmod{11}$.

    $$7^{222} \equiv 5 \pmod{11}.$$

    $\square$

---

**Exercise 37.4.** Construct an RSA system with $p = 11$, $q = 13$, $e = 7$. Compute $d$, encrypt $m = 9$ and verify decryption.

??? success "Solution"

    Step 1: $n = 11 \times 13 = 143$.

    Step 2: $\varphi(n) = 10 \times 12 = 120$.

    Step 3: Verify $\gcd(7, 120) = 1$. Since $120 = 17 \times 7 + 1$, it follows that $\gcd(7, 120) = 1$.

    Step 4: Compute $d = 7^{-1} \bmod 120$. Apply the extended Euclidean algorithm:

    $$\begin{aligned}
    120 &= 17 \times 7 + 1, \\
    7 &= 7 \times 1 + 0.
    \end{aligned}$$

    Back-substituting: $1 = 120 - 17 \times 7$, so $(-17) \times 7 \equiv 1 \pmod{120}$, giving $d = 120 - 17 = 103$.

    Verification: $7 \times 103 = 721 = 6 \times 120 + 1$. Confirmed.

    Step 5: Encrypt $m = 9$: $c = 9^7 \bmod 143$.

    Using repeated squaring:
    - $9^1 = 9$
    - $9^2 = 81$
    - $9^4 \equiv 81^2 = 6561 \equiv 6561 - 45 \times 143 = 6561 - 6435 = 126 \pmod{143}$
    - $9^7 = 9^4 \times 9^2 \times 9^1 \equiv 126 \times 81 \times 9 \pmod{143}$

    Compute $126 \times 81 = 10206$. $10206 \bmod 143$: $10206 / 143 \approx 71.37$, so $10206 - 71 \times 143 = 10206 - 10153 = 53$.

    Then $53 \times 9 = 477$. $477 \bmod 143$: $477 - 3 \times 143 = 477 - 429 = 48$.

    So $c = 48$.

    Step 6: Decrypt $c = 48$: $m = 48^{103} \bmod 143$.

    By correctness of RSA, $c^d \equiv m^{ed} \equiv m \pmod{n}$ since $ed = 7 \times 103 = 721 = 1 + 6 \times 120 = 1 + 6\varphi(n)$.

    Decryption therefore recovers $m = 9$.

    $\square$

---

**Exercise 37.5.** Diffie–Hellman with $p = 467$, $g = 2$, $a = 153$, $b = 294$.

??? success "Solution"

    The computation proceeds via modular exponentiation (square-and-multiply):

    $A = 2^{153} \bmod 467$. Since $153 = 10011001_2$, successive squaring yields $A = 2^{153} \bmod 467$.

    Verification by the `modPow` algorithm confirms:

    $A = g^a \bmod p = 2^{153} \bmod 467 = 29$.

    $B = g^b \bmod p = 2^{294} \bmod 467 = 196$.

    Shared secret (Alice): $s = B^a \bmod p = 196^{153} \bmod 467 = 206$.

    Shared secret (Bob): $s = A^b \bmod p = 29^{294} \bmod 467 = 206$.

    Both parties compute $s = 206$.

    An eavesdropper observes $g = 2$, $p = 467$, $A = 29$, $B = 196$ but must solve $2^a \equiv 29 \pmod{467}$ to recover $a = 153$, which is computationally hard for large primes.

    $\square$

---

**Exercise 37.6.** Birthday collision analysis for a 32-bit hash.

??? success "Solution"

    The hash space has $M = 2^{32} \approx 4.295 \times 10^9$ possible outputs.

    Number of files for 50% collision probability:

    $$k \approx 1.177 \times 2^{n/2} = 1.177 \times 2^{16} = 1.177 \times 65536 \approx 77{,}163.$$

    Approximately 77,000 files are needed before a collision becomes likely.

    For 10,000 files, the collision probability is:

    $$P \approx 1 - e^{-k^2/(2 \cdot 2^n)} = 1 - e^{-10000^2/(2 \times 2^{32})} = 1 - e^{-10^8 / 8.59 \times 10^9} = 1 - e^{-0.01164} \approx 0.01157.$$

    The collision probability is approximately $1.16\%$. A 32-bit hash is far too short for serious deduplication at scale; by about 77,000 files the probability of a false match exceeds 50%.

    $\square$

---

**Exercise 37.7.** Prove that knowing $\varphi(n)$ and $n = pq$ allows efficient factorisation.

??? success "Solution"

    From $n = pq$ and $\varphi(n) = (p-1)(q-1) = pq - p - q + 1 = n - (p+q) + 1$, it is possible to compute:

    $$p + q = n - \varphi(n) + 1.$$

    Let $S = p + q = n - \varphi(n) + 1$ and $P = pq = n$. Then $p$ and $q$ are roots of the quadratic:

    $$x^2 - Sx + P = 0.$$

    By the quadratic formula:

    $$p, q = \frac{S \pm \sqrt{S^2 - 4P}}{2}.$$

    Since $p$ and $q$ are distinct primes, $S^2 - 4P = (p+q)^2 - 4pq = (p-q)^2 > 0$, so the discriminant is a perfect square and the roots are real and distinct. Computing $S$, $P$ and the square root are all efficient operations. Knowing $n$ and $\varphi(n)$ therefore yields $p$ and $q$ in $O((\log n)^2)$ bit operations.

    $\square$

---

**Exercise 37.8.** Schnorr protocol nonce reuse.

??? success "Solution"

    **Why fresh $r$ is needed:** If the prover reuses the same $r$ (and hence the same commitment $a = g^r$) for two different challenges $e_1$ and $e_2$, they produce responses $z_1 = r + e_1 x \bmod q$ and $z_2 = r + e_2 x \bmod q$. A dishonest verifier who obtains both transcripts can subtract:

    $$z_1 - z_2 = (e_1 - e_2)x \bmod q.$$

    Since $q$ is prime and $e_1 \neq e_2$, $(e_1 - e_2)$ is invertible mod $q$, so:

    $$x = (z_1 - z_2)(e_1 - e_2)^{-1} \bmod q.$$

    The secret $x$ is completely revealed.

    **Explicit computation:** Given $g = 3$, $p = 17$, $q = 8$, $x = 5$, $r = 2$, $e_1 = 3$, $e_2 = 6$:

    $z_1 = r + e_1 x \bmod q = 2 + 3 \times 5 \bmod 8 = 17 \bmod 8 = 1$.

    $z_2 = r + e_2 x \bmod q = 2 + 6 \times 5 \bmod 8 = 32 \bmod 8 = 0$.

    Extract $x$: $z_1 - z_2 = 1 - 0 = 1$. $e_1 - e_2 = 3 - 6 = -3 \equiv 5 \pmod{8}$.

    We need $5^{-1} \bmod 8$: $5 \times 5 = 25 \equiv 1 \pmod{8}$, so $5^{-1} = 5$.

    $x = 1 \times 5 \bmod 8 = 5$.

    This correctly recovers the secret $x = 5$, demonstrating the fatal consequence of nonce reuse.

    $\square$

---
