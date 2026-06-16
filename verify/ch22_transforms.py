# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 22: Transforms & Spectral Analysis — verification."""

import math
import numpy as np
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(22, "Transforms & Spectral Analysis")

    # ===================================================================
    # LAYER 1: Symbolic — key identities and formulas
    # ===================================================================

    ch.add(SymbolicCheck(
        label="Orthogonality of roots of unity: sum e^{2pi i(k-k')n/N} = N*delta",
        section="5",
        identity=lambda: _orthogonality_identity(),
        note="F4.12",
    ))

    ch.add(SymbolicCheck(
        label="DFT of constant: X_0 = cN, X_k = 0 for k>0",
        section="5",
        identity=lambda: _dft_constant(),
        note="Exercise 22.1 / F4.1",
    ))

    ch.add(SymbolicCheck(
        label="Parseval's theorem: sum |x_n|^2 = (1/N) sum |X_k|^2",
        section="5",
        identity=lambda: _parsevals_theorem(),
        note="F4.4",
    ))

    ch.add(SymbolicCheck(
        label="DFT matrix is symmetric: W_{kn} = W_{nk}",
        section="4",
        identity=lambda: _dft_matrix_symmetric(),
        note="Definition 3.1 remark",
    ))

    ch.add(SymbolicCheck(
        label="Inverse DFT recovers signal (symbolic N=4)",
        section="4",
        identity=lambda: _idft_recovers_signal(),
        note="Definition 3.2",
    ))

    # ===================================================================
    # LAYER 2: Numerical — worked examples
    # ===================================================================

    # --- Example 1: DFT of pure sine wave (N=8, freq=1) ---
    N = 8
    x_sine = np.array([math.sin(2 * math.pi * n / N) for n in range(N)])
    X_sine = np.fft.fft(x_sine)

    # Verify sample values from the table in Example 1
    ch.add(NumericCheck(
        label="Ex 1: x_0 = sin(0) = 0",
        section="9.1",
        stated=0.0,
        computed=x_sine[0],
        tolerance=1e-12,
    ))
    ch.add(NumericCheck(
        label="Ex 1: x_1 = sin(pi/4) = sqrt(2)/2",
        section="9.1",
        stated=math.sqrt(2) / 2,
        computed=x_sine[1],
        tolerance=1e-12,
    ))
    ch.add(NumericCheck(
        label="Ex 1: x_2 = sin(pi/2) = 1",
        section="9.1",
        stated=1.0,
        computed=x_sine[2],
        tolerance=1e-12,
    ))
    ch.add(NumericCheck(
        label="Ex 1: x_4 = sin(pi) = 0",
        section="9.1",
        stated=0.0,
        computed=x_sine[4],
        tolerance=1e-12,
    ))
    ch.add(NumericCheck(
        label="Ex 1: x_6 = sin(3pi/2) = -1",
        section="9.1",
        stated=-1.0,
        computed=x_sine[6],
        tolerance=1e-12,
    ))

    # X_1 should be -4i (Re=0, Im=-4)
    ch.add(NumericCheck(
        label="Ex 1: |X_1| = 4 (N/2) for unit sine",
        section="9.1",
        stated=4.0,
        computed=abs(X_sine[1]),
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Ex 1: Re(X_1) = 0",
        section="9.1",
        stated=0.0,
        computed=X_sine[1].real,
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Ex 1: Im(X_1) = -4",
        section="9.1",
        stated=-4.0,
        computed=X_sine[1].imag,
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Ex 1: |X_7| = 4 (conjugate mirror)",
        section="9.1",
        stated=4.0,
        computed=abs(X_sine[7]),
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Ex 1: Re(X_7) = 0",
        section="9.1",
        stated=0.0,
        computed=X_sine[7].real,
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Ex 1: Im(X_7) = +4 (conjugate of X_1)",
        section="9.1",
        stated=4.0,
        computed=X_sine[7].imag,
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Ex 1: arg(X_1) = -pi/2 (sine phase)",
        section="9.1",
        stated=-math.pi / 2,
        computed=np.angle(X_sine[1]),
        tolerance=1e-10,
        note="Sine = cosine shifted by -pi/2",
    ))
    # All other bins should be zero
    for k in [0, 2, 3, 4, 5, 6]:
        ch.add(NumericCheck(
            label=f"Ex 1: |X_{k}| = 0 for sine",
            section="9.1",
            stated=0.0,
            computed=abs(X_sine[k]),
            tolerance=1e-10,
        ))

    # --- Example 2: DFT of [1, 2, 3, 4] ---
    x_ex2 = np.array([1, 2, 3, 4], dtype=float)
    X_ex2 = np.fft.fft(x_ex2)

    ch.add(NumericCheck(
        label="Ex 2: X_0 = 10",
        section="9.2",
        stated=10.0,
        computed=X_ex2[0].real,
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Ex 2: Re(X_1) = -2",
        section="9.2",
        stated=-2.0,
        computed=X_ex2[1].real,
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Ex 2: Im(X_1) = 2",
        section="9.2",
        stated=2.0,
        computed=X_ex2[1].imag,
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Ex 2: X_2 = -2 (real)",
        section="9.2",
        stated=-2.0,
        computed=X_ex2[2].real,
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Ex 2: Im(X_2) = 0",
        section="9.2",
        stated=0.0,
        computed=X_ex2[2].imag,
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Ex 2: Re(X_3) = -2",
        section="9.2",
        stated=-2.0,
        computed=X_ex2[3].real,
        tolerance=1e-10,
    ))
    ch.add(NumericCheck(
        label="Ex 2: Im(X_3) = -2",
        section="9.2",
        stated=-2.0,
        computed=X_ex2[3].imag,
        tolerance=1e-10,
    ))

    # --- Example 2 FFT butterfly intermediate values (Theorem 3.5) ---
    # Even samples: a = (x_0, x_2) = (1, 3), odd: b = (x_1, x_3) = (2, 4)
    # A_0 = 1+3 = 4, A_1 = 1-3 = -2
    # B_0 = 2+4 = 6, B_1 = 2-4 = -2
    ch.add(NumericCheck(
        label="Ex 2 FFT: A_0 = x_0 + x_2 = 1+3 = 4",
        section="9.2",
        stated=4.0,
        computed=1.0 + 3.0,
        tolerance=1e-12,
        note="Even-indexed 2-pt DFT",
    ))
    ch.add(NumericCheck(
        label="Ex 2 FFT: A_1 = x_0 - x_2 = 1-3 = -2",
        section="9.2",
        stated=-2.0,
        computed=1.0 - 3.0,
        tolerance=1e-12,
    ))
    ch.add(NumericCheck(
        label="Ex 2 FFT: B_0 = x_1 + x_3 = 2+4 = 6",
        section="9.2",
        stated=6.0,
        computed=2.0 + 4.0,
        tolerance=1e-12,
        note="Odd-indexed 2-pt DFT",
    ))
    ch.add(NumericCheck(
        label="Ex 2 FFT: B_1 = x_1 - x_3 = 2-4 = -2",
        section="9.2",
        stated=-2.0,
        computed=2.0 - 4.0,
        tolerance=1e-12,
    ))

    # Twiddle factors: omega_4^0 = 1, omega_4^1 = e^{-i*pi/2} = -i
    tw0_re = math.cos(0)     # 1
    tw0_im = -math.sin(0)    # 0
    tw1_re = math.cos(math.pi / 2)   # 0
    tw1_im = -math.sin(math.pi / 2)  # -1
    ch.add(NumericCheck(
        label="Ex 2 FFT: twiddle w4^0 Re = 1",
        section="9.2",
        stated=1.0,
        computed=tw0_re,
        tolerance=1e-12,
        note="Twiddle factor",
    ))
    ch.add(NumericCheck(
        label="Ex 2 FFT: twiddle w4^0 Im = 0",
        section="9.2",
        stated=0.0,
        computed=tw0_im,
        tolerance=1e-12,
    ))
    ch.add(NumericCheck(
        label="Ex 2 FFT: twiddle w4^1 Re = 0 (cos(pi/2))",
        section="9.2",
        stated=0.0,
        computed=tw1_re,
        tolerance=1e-12,
    ))
    ch.add(NumericCheck(
        label="Ex 2 FFT: twiddle w4^1 Im = -1 (-sin(pi/2))",
        section="9.2",
        stated=-1.0,
        computed=tw1_im,
        tolerance=1e-12,
    ))

    # Butterfly outputs:
    # X_0 = A_0 + w4^0*B_0 = 4 + 1*6 = 10
    # X_1 = A_1 + w4^1*B_1 = -2 + (-i)*(-2) = -2 + 2i
    # X_2 = A_0 - w4^0*B_0 = 4 - 6 = -2
    # X_3 = A_1 - w4^1*B_1 = -2 - 2i
    A0, A1 = 4.0, -2.0
    B0, B1 = 6.0, -2.0

    ch.add(NumericCheck(
        label="Ex 2 FFT butterfly: X_0 = A_0 + w^0*B_0 = 4+6 = 10",
        section="9.2",
        stated=10.0,
        computed=A0 + tw0_re * B0,
        tolerance=1e-12,
        note="F4.5: upper butterfly",
    ))
    ch.add(NumericCheck(
        label="Ex 2 FFT butterfly: X_2 = A_0 - w^0*B_0 = 4-6 = -2",
        section="9.2",
        stated=-2.0,
        computed=A0 - tw0_re * B0,
        tolerance=1e-12,
        note="F4.6: lower butterfly",
    ))
    # X_1 = A_1 + w4^1*B_1: (-2) + (-i)*(-2) = -2 + 2i
    # w4^1 * B_1 (complex): (0 - i)*(-2) = (0*(-2) - (-1)*(-2)) + i*(0*(-2) + (-1)*(-2))... wait
    # Actually w4^1 = -i, B_1 = -2 (real). So w4^1 * B_1 = (-i)*(-2) = 2i => Re=0, Im=2
    tB1_re = tw1_re * B1 - tw1_im * 0  # B_1 is real
    tB1_im = tw1_im * B1 + tw1_re * 0
    ch.add(NumericCheck(
        label="Ex 2 FFT butterfly: Re(w^1*B_1) = 0",
        section="9.2",
        stated=0.0,
        computed=tB1_re,
        tolerance=1e-12,
    ))
    ch.add(NumericCheck(
        label="Ex 2 FFT butterfly: Im(w^1*B_1) = 2",
        section="9.2",
        stated=2.0,
        computed=tB1_im,
        tolerance=1e-12,
    ))
    ch.add(NumericCheck(
        label="Ex 2 FFT butterfly: Re(X_1) = A_1 + Re(w^1*B_1) = -2+0 = -2",
        section="9.2",
        stated=-2.0,
        computed=A1 + tB1_re,
        tolerance=1e-12,
    ))
    ch.add(NumericCheck(
        label="Ex 2 FFT butterfly: Im(X_1) = 0 + Im(w^1*B_1) = 2",
        section="9.2",
        stated=2.0,
        computed=0.0 + tB1_im,
        tolerance=1e-12,
    ))
    ch.add(NumericCheck(
        label="Ex 2 FFT butterfly: Re(X_3) = A_1 - Re(w^1*B_1) = -2-0 = -2",
        section="9.2",
        stated=-2.0,
        computed=A1 - tB1_re,
        tolerance=1e-12,
    ))
    ch.add(NumericCheck(
        label="Ex 2 FFT butterfly: Im(X_3) = 0 - Im(w^1*B_1) = -2",
        section="9.2",
        stated=-2.0,
        computed=0.0 - tB1_im,
        tolerance=1e-12,
    ))

    # --- Example 4: Periodogram of two-cosine signal ---
    N4 = 64
    x_ex4 = np.array([
        3 * math.cos(2 * math.pi * 5 * n / 64) + math.cos(2 * math.pi * 12 * n / 64)
        for n in range(N4)
    ])
    X_ex4 = np.fft.fft(x_ex4)
    P_ex4 = np.abs(X_ex4) ** 2 / N4

    # Expected: P_5 = 3^2 * 64/4 = 144
    ch.add(NumericCheck(
        label="Ex 4: P_5 = 144 (periodogram at bin 5)",
        section="9.4",
        stated=144.0,
        computed=P_ex4[5],
        tolerance=1e-8,
    ))

    # Expected: P_12 = 1^2 * 64/4 = 16
    ch.add(NumericCheck(
        label="Ex 4: P_12 = 16 (periodogram at bin 12)",
        section="9.4",
        stated=16.0,
        computed=P_ex4[12],
        tolerance=1e-8,
    ))

    # Conjugate mirror periodogram values
    ch.add(NumericCheck(
        label="Ex 4: P_59 = 144 (mirror of bin 5, N-5=59)",
        section="9.4",
        stated=144.0,
        computed=P_ex4[59],
        tolerance=1e-8,
        note="Conjugate symmetry mirror",
    ))
    ch.add(NumericCheck(
        label="Ex 4: P_52 = 16 (mirror of bin 12, N-12=52)",
        section="9.4",
        stated=16.0,
        computed=P_ex4[52],
        tolerance=1e-8,
        note="Conjugate symmetry mirror",
    ))

    # All other bins should be zero (check a few)
    for k in [0, 1, 2, 3, 4, 6, 7, 8, 10, 11, 13, 16, 32]:
        ch.add(NumericCheck(
            label=f"Ex 4: P_{k} = 0 (no signal at bin {k})",
            section="9.4",
            stated=0.0,
            computed=P_ex4[k],
            tolerance=1e-8,
        ))

    # DFT magnitudes: |X_5| = 3*N/2 = 96, |X_12| = N/2 = 32
    ch.add(NumericCheck(
        label="Ex 4: |X_5| = 96",
        section="9.4",
        stated=96.0,
        computed=abs(X_ex4[5]),
        tolerance=1e-8,
    ))
    ch.add(NumericCheck(
        label="Ex 4: |X_12| = 32",
        section="9.4",
        stated=32.0,
        computed=abs(X_ex4[12]),
        tolerance=1e-8,
    ))

    # Amplitude ratio in magnitude spectrum: |X_5|/|X_12| = 3
    ch.add(NumericCheck(
        label="Ex 4: |X_5|/|X_12| = 3 (amplitude ratio)",
        section="9.4",
        stated=3.0,
        computed=abs(X_ex4[5]) / abs(X_ex4[12]),
        tolerance=1e-10,
        note="3:1 amplitude in time => 3:1 in magnitude spectrum",
    ))

    # Power ratio: P_5/P_12 = 9 (power ~ amplitude^2)
    ch.add(NumericCheck(
        label="Ex 4: P_5/P_12 = 9 (power ratio = amplitude ratio squared)",
        section="9.4",
        stated=9.0,
        computed=P_ex4[5] / P_ex4[12],
        tolerance=1e-10,
        note="Power proportional to A^2",
    ))

    # --- Parseval verification for the two-cosine signal ---
    time_energy_ex4 = np.sum(x_ex4 ** 2)
    freq_energy_ex4 = np.sum(np.abs(X_ex4) ** 2) / N4
    ch.add(NumericCheck(
        label="Ex 4: Parseval: time_energy = freq_energy for 2-cosine",
        section="9.4",
        stated=time_energy_ex4,
        computed=freq_energy_ex4,
        tolerance=1e-10,
        note="F4.4 applied to Example 4 signal",
    ))

    # Expected total energy: for cos signals of amplitude A in N samples,
    # energy = A^2 * N/2. Total = 3^2*64/2 + 1^2*64/2 = 288 + 32 = 320
    ch.add(NumericCheck(
        label="Ex 4: total energy = 3^2*N/2 + 1^2*N/2 = 320",
        section="9.4",
        stated=320.0,
        computed=time_energy_ex4,
        tolerance=1e-8,
        note="Energy of sum of cosines",
    ))

    # --- Parseval for x=[1,2,3,4] ---
    time_e2 = np.sum(x_ex2 ** 2)  # 1+4+9+16 = 30
    freq_e2 = np.sum(np.abs(X_ex2) ** 2) / 4
    ch.add(NumericCheck(
        label="Parseval [1,2,3,4]: time energy = 30",
        section="5",
        stated=30.0,
        computed=time_e2,
        tolerance=1e-12,
        note="F4.4",
    ))
    ch.add(NumericCheck(
        label="Parseval [1,2,3,4]: freq energy = 30",
        section="5",
        stated=30.0,
        computed=freq_e2,
        tolerance=1e-10,
        note="F4.4",
    ))

    # --- Parseval for the sine signal ---
    time_e_sine = np.sum(x_sine ** 2)  # N/2 = 4 for unit sine
    freq_e_sine = np.sum(np.abs(X_sine) ** 2) / N
    ch.add(NumericCheck(
        label="Parseval sine: time energy = N/2 = 4",
        section="5",
        stated=4.0,
        computed=time_e_sine,
        tolerance=1e-10,
        note="F4.4 on unit sine",
    ))
    ch.add(NumericCheck(
        label="Parseval sine: freq energy = 4",
        section="5",
        stated=4.0,
        computed=freq_e_sine,
        tolerance=1e-10,
    ))

    # --- Frequency resolution and Nyquist ---
    fs = 32
    N_ex3 = 32
    delta_f = fs / N_ex3
    ch.add(NumericCheck(
        label="Ex 3: frequency resolution Delta_f = 1 Hz",
        section="9.3",
        stated=1.0,
        computed=delta_f,
        tolerance=1e-12,
    ))

    f_nyquist = fs / 2.0
    ch.add(NumericCheck(
        label="Ex 3: Nyquist frequency = 16 Hz",
        section="9.3",
        stated=16.0,
        computed=f_nyquist,
        tolerance=1e-12,
    ))

    # f_0 = 3 Hz falls on bin k=3
    ch.add(NumericCheck(
        label="Ex 3: sine at 3 Hz maps to bin k=3 (k = f/Delta_f)",
        section="9.3",
        stated=3.0,
        computed=3.0 / delta_f,
        tolerance=1e-12,
        note="Bin index = frequency / resolution",
    ))

    # Expected sine peak power: N/4 = 8
    ch.add(NumericCheck(
        label="Ex 3: expected sine peak P_3 ~ N/4 = 8",
        section="9.3",
        stated=8.0,
        computed=N_ex3 / 4.0,
        tolerance=1e-12,
        note="Unit-amplitude sine: |X_k|^2/N = (N/2)^2/N = N/4",
    ))

    # --- Exercise 22.5 frequency resolution ---
    N_ex5 = 256
    fs_ex5 = 1000
    delta_f_ex5 = fs_ex5 / N_ex5
    ch.add(NumericCheck(
        label="Ex 22.5: Delta_f = 1000/256 ~ 3.906 Hz",
        section="11",
        stated=1000.0 / 256.0,
        computed=delta_f_ex5,
        tolerance=1e-12,
        note="Exercise 22.5",
    ))
    ch.add(NumericCheck(
        label="Ex 22.5: Nyquist = 500 Hz",
        section="11",
        stated=500.0,
        computed=fs_ex5 / 2.0,
        tolerance=1e-12,
    ))
    # 440 Hz bin: k = 440/3.90625 ~ 112.64
    ch.add(NumericCheck(
        label="Ex 22.5: 440 Hz maps to bin k ~ 112.64",
        section="11",
        stated=440.0 / delta_f_ex5,
        computed=440.0 * N_ex5 / fs_ex5,
        tolerance=1e-10,
        note="Non-integer bin => spectral leakage",
    ))

    # --- Windowing effect verification ---
    # Hann window coefficients
    N_win = 8
    hann = np.array([0.5 * (1 - math.cos(2 * math.pi * n / (N_win - 1))) for n in range(N_win)])
    ch.add(NumericCheck(
        label="Hann window: w_0 = 0",
        section="4",
        stated=0.0,
        computed=hann[0],
        tolerance=1e-12,
        note="Remark 3.9",
    ))
    ch.add(NumericCheck(
        label="Hann window: w_{N-1} = 0",
        section="4",
        stated=0.0,
        computed=hann[N_win - 1],
        tolerance=1e-12,
    ))
    # For even N, max is at (N-1)/2 which falls between indices; indices 3 and 4 are symmetric
    ch.add(NumericCheck(
        label="Hann window: w_3 = w_4 (symmetric around center)",
        section="4",
        stated=hann[3],
        computed=hann[4],
        tolerance=1e-12,
        note="Symmetric window for even N",
    ))

    # Hamming window coefficients
    hamming = np.array([0.54 - 0.46 * math.cos(2 * math.pi * n / (N_win - 1)) for n in range(N_win)])
    ch.add(NumericCheck(
        label="Hamming window: w_0 = 0.08",
        section="4",
        stated=0.08,
        computed=hamming[0],
        tolerance=1e-10,
        note="Remark 3.9: 0.54 - 0.46 = 0.08",
    ))
    ch.add(NumericCheck(
        label="Hamming window: w_3 = w_4 (symmetric)",
        section="4",
        stated=hamming[3],
        computed=hamming[4],
        tolerance=1e-12,
    ))

    # --- Windowed vs unwindowed leakage comparison ---
    # Non-integer frequency to demonstrate leakage
    N_leak = 64
    x_leak = np.array([math.sin(2 * math.pi * 5.5 * n / N_leak) for n in range(N_leak)])
    X_leak_rect = np.fft.fft(x_leak)
    P_leak_rect = np.abs(X_leak_rect) ** 2 / N_leak

    hann_leak = np.array([0.5 * (1 - math.cos(2 * math.pi * n / (N_leak - 1))) for n in range(N_leak)])
    X_leak_hann = np.fft.fft(x_leak * hann_leak)
    P_leak_hann = np.abs(X_leak_hann) ** 2 / N_leak

    ch.add(StructuralCheck(
        label="Windowing reduces far-bin leakage for non-integer freq",
        section="4",
        predicate=lambda: _windowing_reduces_leakage(P_leak_rect, P_leak_hann),
        note="Remark 3.9: Hann reduces sidelobes",
    ))

    # --- DFT of [1, 0, -1, 0] (from section 8 API) ---
    x_api = np.array([1, 0, -1, 0], dtype=float)
    X_api = np.fft.fft(x_api)
    ch.add(NumericCheck(
        label="API example: DFT([1,0,-1,0]) X_0 = 0",
        section="8",
        stated=0.0,
        computed=X_api[0].real,
        tolerance=1e-12,
    ))
    ch.add(NumericCheck(
        label="API example: DFT([1,0,-1,0]) X_1 = 2",
        section="8",
        stated=2.0,
        computed=X_api[1].real,
        tolerance=1e-12,
    ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    ch.add(StructuralCheck(
        label="DFT invertibility: IDFT(DFT(x)) = x",
        section="5",
        predicate=lambda: _dft_invertibility(),
        note="DFT and IDFT are exact inverses",
    ))

    ch.add(StructuralCheck(
        label="Parseval's theorem holds numerically for random signal",
        section="5",
        predicate=lambda: _parsevals_numeric(),
        note="F4.4: energy conservation",
    ))

    ch.add(StructuralCheck(
        label="Convolution theorem: DFT(circ_conv(x,y)) = DFT(x)*DFT(y)",
        section="5",
        predicate=lambda: _convolution_theorem_numeric(),
        note="F4.3",
    ))

    ch.add(StructuralCheck(
        label="Real signal has conjugate-symmetric DFT: X_{N-k} = conj(X_k)",
        section="5",
        predicate=lambda: _conjugate_symmetry(),
        note="Property of real-valued signals",
    ))

    ch.add(StructuralCheck(
        label="Circular shift property: shift by m multiplies by exp(-2pi i km/N)",
        section="5",
        predicate=lambda: _circular_shift_property(),
        note="F4.10",
    ))

    ch.add(StructuralCheck(
        label="DFT linearity: DFT(ax+by) = a*DFT(x) + b*DFT(y)",
        section="4",
        predicate=lambda: _dft_linearity(),
        note="Theorem 3.3(a)",
    ))

    ch.add(StructuralCheck(
        label="Modulation property: e^{2pi inm/N} x_n shifts spectrum by m",
        section="4",
        predicate=lambda: _modulation_property(),
        note="Theorem 3.3(d) / F4.11",
    ))

    ch.add(StructuralCheck(
        label="FFT speedup ratio vs naive: N^2 / (N log2 N) for N=2^20",
        section="4",
        predicate=lambda: _fft_speedup_ratio(),
        note="Theorem 3.5 complexity comparison",
    ))

    ch.add(StructuralCheck(
        label="Parseval on multiple signal types (constant, ramp, random)",
        section="5",
        predicate=lambda: _parsevals_multiple_signals(),
        note="F4.4 universality",
    ))

    # ===================================================================
    # EXERCISE VERIFICATION CHECKS (Section 11)
    # ===================================================================

    # --- Exercise 22.1: DFT of constant signal x_n = c ---
    # X_0 = cN, X_k = 0 for k>0 (already verified symbolically, add numeric)
    c_val = 3.0
    N_const = 8
    x_const = np.full(N_const, c_val)
    X_const = np.fft.fft(x_const)
    ch.add(NumericCheck(
        label="Ex 22.1: X_0 = c*N = 3*8 = 24",
        section="11",
        stated=24.0,
        computed=float(X_const[0].real),
        tolerance=1e-10,
        note="Exercise 22.1",
    ))
    for k in range(1, N_const):
        ch.add(NumericCheck(
            label=f"Ex 22.1: X_{k} = 0 for constant signal",
            section="11",
            stated=0.0,
            computed=float(abs(X_const[k])),
            tolerance=1e-10,
            note="Exercise 22.1",
        ))

    # --- Exercise 22.2: DFT of cos(2*pi*k0*n/N) ---
    # For k0=2, N=8: X_{k0}=N/2=4, X_{N-k0}=N/2=4, rest 0
    k0_ex2 = 2
    N_ex22 = 8
    x_cos = np.array([math.cos(2*math.pi*k0_ex2*n_/N_ex22) for n_ in range(N_ex22)])
    X_cos = np.fft.fft(x_cos)
    ch.add(NumericCheck(
        label="Ex 22.2: |X_{k0}| = N/2 = 4",
        section="11",
        stated=4.0,
        computed=float(abs(X_cos[k0_ex2])),
        tolerance=1e-10,
        note="Exercise 22.2: cosine at bin k0=2",
    ))
    ch.add(NumericCheck(
        label="Ex 22.2: |X_{N-k0}| = N/2 = 4",
        section="11",
        stated=4.0,
        computed=float(abs(X_cos[N_ex22-k0_ex2])),
        tolerance=1e-10,
        note="Exercise 22.2: conjugate mirror",
    ))
    # Cosine has real DFT (both X_{k0} and X_{N-k0} are real positive)
    ch.add(NumericCheck(
        label="Ex 22.2: Re(X_{k0}) = N/2 = 4 (cosine => real)",
        section="11",
        stated=4.0,
        computed=float(X_cos[k0_ex2].real),
        tolerance=1e-10,
        note="Exercise 22.2: cos has 0 phase",
    ))
    ch.add(NumericCheck(
        label="Ex 22.2: Im(X_{k0}) ~ 0",
        section="11",
        stated=0.0,
        computed=float(abs(X_cos[k0_ex2].imag)),
        tolerance=1e-10,
        note="Exercise 22.2",
    ))

    # --- Exercise 22.4: Circular convolution via frequency domain ---
    # x=(1,0,0,0), y=(1,1,1,1)
    x_ex4 = np.array([1.0, 0.0, 0.0, 0.0])
    y_ex4 = np.array([1.0, 1.0, 1.0, 1.0])
    # Circular convolution of delta with constant = constant
    z_freq = np.fft.ifft(np.fft.fft(x_ex4) * np.fft.fft(y_ex4)).real
    ch.add(NumericCheck(
        label="Ex 22.4: circ_conv(delta, const) = (1,1,1,1) at n=0",
        section="11",
        stated=1.0,
        computed=float(z_freq[0]),
        tolerance=1e-10,
        note="Exercise 22.4",
    ))
    ch.add(NumericCheck(
        label="Ex 22.4: circ_conv(delta, const) = (1,1,1,1) at n=1",
        section="11",
        stated=1.0,
        computed=float(z_freq[1]),
        tolerance=1e-10,
        note="Exercise 22.4",
    ))
    ch.add(NumericCheck(
        label="Ex 22.4: circ_conv(delta, const) = (1,1,1,1) at n=2",
        section="11",
        stated=1.0,
        computed=float(z_freq[2]),
        tolerance=1e-10,
        note="Exercise 22.4",
    ))
    ch.add(NumericCheck(
        label="Ex 22.4: circ_conv(delta, const) = (1,1,1,1) at n=3",
        section="11",
        stated=1.0,
        computed=float(z_freq[3]),
        tolerance=1e-10,
        note="Exercise 22.4",
    ))

    # --- Exercise 22.5: Frequency resolution and Nyquist ---
    # N=256, fs=1000
    # Delta_f = 1000/256 ~ 3.90625 Hz
    # Nyquist = 500 Hz
    # 440 Hz bin = 440/3.90625 ~ 112.64 (non-integer => leakage)
    # N=512: Delta_f = 1000/512 ~ 1.953 Hz, bin = 440/1.953 ~ 225.28
    ch.add(NumericCheck(
        label="Ex 22.5: N=512 Delta_f = 1000/512 ~ 1.953 Hz",
        section="11",
        stated=1000.0/512.0,
        computed=lambda: 1000.0 / 512.0,
        tolerance=1e-12,
        note="Exercise 22.5: doubling N halves freq resolution",
    ))
    ch.add(NumericCheck(
        label="Ex 22.5: N=512 440Hz bin ~ 225.28",
        section="11",
        stated=440.0 * 512.0 / 1000.0,
        computed=lambda: 440.0 / (1000.0/512.0),
        tolerance=1e-10,
        note="Exercise 22.5: still non-integer bin",
    ))

    # --- Exercise 22.7: Spectral leakage at non-integer frequency ---
    # f=3.5/16, N=16 => energy leaks into bins 3 and 4
    N_ex7 = 16
    x_ex7 = np.array([math.sin(2*math.pi*3.5*n_/N_ex7) for n_ in range(N_ex7)])
    P_ex7 = np.abs(np.fft.fft(x_ex7))**2 / N_ex7
    # Bins 3 and 4 should have most power
    ch.add(StructuralCheck(
        label="Ex 22.7: bins 3,4 have most power (spectral leakage)",
        section="11",
        predicate=lambda: (
            P_ex7[3] > P_ex7[1] and P_ex7[4] > P_ex7[1],
            f"P[3]={P_ex7[3]:.4f}, P[4]={P_ex7[4]:.4f}, P[1]={P_ex7[1]:.4f}"
        ),
        note="Exercise 22.7",
    ))
    # Hann windowed version
    hann_ex7 = np.array([0.5*(1-math.cos(2*math.pi*n_/(N_ex7-1))) for n_ in range(N_ex7)])
    P_ex7_hann = np.abs(np.fft.fft(x_ex7 * hann_ex7))**2 / N_ex7
    # Hann should reduce far-bin leakage
    far_rect = sum(P_ex7[k] for k in range(6, N_ex7//2))
    far_hann = sum(P_ex7_hann[k] for k in range(6, N_ex7//2))
    ch.add(StructuralCheck(
        label="Ex 22.7: Hann reduces far-bin leakage",
        section="11",
        predicate=lambda: (
            far_hann < far_rect,
            f"Hann far={far_hann:.6f} >= rect far={far_rect:.6f}"
        ),
        note="Exercise 22.7: windowing effect",
    ))

    # --- Exercise 22.8: Z-transform of a^n u_n ---
    # X(z) = 1/(1-a*z^{-1}) for |z|>|a|
    # On unit circle: X(e^{iw}) = 1/(1-a*e^{-iw})
    # |X(e^{iw})| for a=0.9: low-pass filter
    # At w=0: |X|=1/(1-0.9)=10, at w=pi: |X|=1/(1+0.9)=1/1.9~0.526
    a_ex8 = 0.9
    ch.add(NumericCheck(
        label="Ex 22.8: |X(e^{i*0})| = 1/(1-0.9) = 10 (DC gain)",
        section="11",
        stated=10.0,
        computed=lambda: 1.0 / (1 - 0.9),
        tolerance=1e-10,
        note="Exercise 22.8: maximum at DC",
    ))
    ch.add(NumericCheck(
        label="Ex 22.8: |X(e^{i*pi})| = 1/(1+0.9) ~ 0.526 (Nyquist)",
        section="11",
        stated=1.0/1.9,
        computed=lambda: 1.0 / abs(1 - 0.9*(-1)),  # e^{-i*pi} = -1
        tolerance=1e-10,
        note="Exercise 22.8: minimum at Nyquist => low-pass",
    ))
    ch.add(StructuralCheck(
        label="Ex 22.8: low-pass filter (DC gain > Nyquist gain)",
        section="11",
        predicate=lambda: (
            10.0 > 1.0/1.9,
            "DC gain not larger than Nyquist gain"
        ),
        note="Exercise 22.8",
    ))

    # --- Exercise 22.3: Circular shift property proof (numerical verification) ---
    # DFT of shifted signal = DFT(x) * exp(-2*pi*i*k*m/N)
    ch.add(StructuralCheck(
        label="Ex 22.3: circular shift property for multiple shift amounts",
        section="11",
        predicate=lambda: _ex223_shift_property(),
        note="Exercise 22.3: prove circular shift property",
    ))

    # --- Exercise 22.6: IDFT via forward DFT procedure ---
    # IDFT(X) = (1/N) * conj(DFT(conj(X)))
    ch.add(StructuralCheck(
        label="Ex 22.6: IDFT via forward DFT: conj(DFT(conj(X)))/N = IDFT(X)",
        section="11",
        predicate=lambda: _ex226_idft_via_fft(),
        note="Exercise 22.6: implement IDFT using forward DFT",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION — Named algorithms from Section 6
    # ===================================================================

    # --- Naive DFT O(N^2) ---
    def _algo_naive_dft():
        """Implement naive DFT and verify against numpy.fft.fft."""
        def naive_dft(x):
            N = len(x)
            X = [0j] * N
            for k in range(N):
                for n in range(N):
                    angle = 2 * math.pi * k * n / N
                    X[k] += x[n] * (math.cos(angle) - 1j * math.sin(angle))
            return X

        x = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
        our_dft = naive_dft(x)
        np_dft = np.fft.fft(x)
        for k in range(len(x)):
            if abs(our_dft[k] - np_dft[k]) > 1e-8:
                return (False, f"DFT[{k}] = {our_dft[k]}, numpy = {np_dft[k]}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Naive DFT: O(N^2) implementation matches numpy.fft.fft for N=8",
        section="6",
        predicate=_algo_naive_dft,
        note="DFT algorithm verified",
    ))

    # --- FFT Cooley-Tukey Radix-2 ---
    def _algo_fft_butterfly():
        """Implement radix-2 FFT and verify against numpy."""
        def fft_recursive(x):
            N = len(x)
            if N <= 1:
                return [complex(v) for v in x]
            even = fft_recursive(x[0::2])
            odd = fft_recursive(x[1::2])
            M = N // 2
            result = [0j] * N
            for k in range(M):
                twiddle = complex(math.cos(-2 * math.pi * k / N),
                                  math.sin(-2 * math.pi * k / N))
                result[k] = even[k] + twiddle * odd[k]        # Butterfly upper
                result[k + M] = even[k] - twiddle * odd[k]    # Butterfly lower
            return result

        x = [1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0]  # N=8 (power of 2)
        our_fft = fft_recursive(x)
        np_fft = np.fft.fft(x)
        for k in range(len(x)):
            if abs(our_fft[k] - np_fft[k]) > 1e-10:
                return (False, f"FFT[{k}] = {our_fft[k]}, numpy = {np_fft[k]}")

        # Verify Parseval's theorem: sum|x_n|^2 = (1/N)*sum|X_k|^2
        energy_time = sum(abs(v) ** 2 for v in x)
        energy_freq = sum(abs(v) ** 2 for v in our_fft) / len(x)
        if abs(energy_time - energy_freq) > 1e-10:
            return (False, f"Parseval: time={energy_time}, freq={energy_freq}")

        return (True, "")

    ch.add(StructuralCheck(
        label="FFT Butterfly: Radix-2 Cooley-Tukey matches numpy and satisfies Parseval",
        section="6",
        predicate=_algo_fft_butterfly,
        note="FFT butterfly algorithm verified",
    ))

    # --- Remark 3.6: Zero-padding interpolates DFT (finer freq grid) ---
    def _remark_3_6_zero_padding():
        """Verify zero-padding gives finer frequency grid but same spectral shape."""
        x = np.array([1, 2, 3, 4, 3, 2, 1, 0], dtype=float)
        N = len(x)
        X_orig = np.fft.fft(x)
        # Zero-pad to next power of 2 * 4 = 32
        N_padded = 32
        x_padded = np.zeros(N_padded)
        x_padded[:N] = x
        X_padded = np.fft.fft(x_padded)
        # At the original frequency bins, values should match (scaled)
        # DFT of padded at index k corresponds to freq k/N_padded
        # DFT of orig at index j corresponds to freq j/N
        # Matching: k/N_padded = j/N => k = j * N_padded/N = j*4
        for j in range(N):
            k = j * (N_padded // N)
            ratio = abs(X_padded[k]) / max(abs(X_orig[j]), 1e-15)
            if abs(X_orig[j]) > 1e-10 and abs(ratio - 1.0) > 0.01:
                return (False, f"Freq bin {j}: |X_pad|={abs(X_padded[k])}, |X_orig|={abs(X_orig[j])}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.6: Zero-padding interpolates DFT onto finer frequency grid",
        section="3.6",
        predicate=_remark_3_6_zero_padding,
        note="Remark 3.6: radix-2 and zero-padding",
    ))

    # --- Remark 3.12: Z-transform is discrete analog of Laplace ---
    def _remark_3_12_z_laplace():
        """Verify z = e^{s*dt}: Z-transform on unit circle = DFT."""
        dt = 0.01
        x = np.array([1.0, 0.5, 0.25, 0.125])  # geometric sequence
        N = len(x)
        # Z-transform at z = e^{j*omega*dt} for omega on unit circle
        freqs = np.linspace(0, 2*np.pi, N, endpoint=False)
        Z_vals = np.zeros(N, dtype=complex)
        for k, omega in enumerate(freqs):
            z = np.exp(1j * omega)
            Z_vals[k] = sum(x[n] * z**(-n) for n in range(N))
        # Should match DFT
        X_dft = np.fft.fft(x)
        if not np.allclose(Z_vals, X_dft, atol=1e-10):
            return (False, f"Z-transform on unit circle != DFT")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.12: Z-transform on unit circle equals DFT",
        section="3.12",
        predicate=_remark_3_12_z_laplace,
        note="Remark 3.12: continuous-discrete Laplace/Z correspondence",
    ))

    return ch


# -------------------------------------------------------------------
# Symbolic helpers
# -------------------------------------------------------------------

def _orthogonality_identity():
    """Verify orthogonality: sum_{n=0}^{N-1} e^{2pi i(k-k')n/N} = N if k=k', 0 otherwise."""
    import sympy
    N = 6
    # Case k = k' (should sum to N)
    total_same = sum(sympy.exp(2 * sympy.pi * sympy.I * 0 * n / N) for n in range(N))
    # Case k != k' (should sum to 0)
    total_diff = sum(sympy.exp(2 * sympy.pi * sympy.I * 1 * n / N) for n in range(N))
    return sympy.Eq(sympy.simplify(total_same), N) and sympy.Eq(sympy.simplify(total_diff), 0)


def _dft_constant():
    """DFT of constant c: X_0 = cN, X_k = 0 for k>0."""
    import sympy
    N = 4
    c = sympy.Symbol('c')
    # X_0 = sum c * e^0 = cN
    X0 = sum(c * sympy.exp(-2 * sympy.pi * sympy.I * 0 * n / N) for n in range(N))
    # X_1 = sum c * e^{-2pi i n/N}
    X1 = sum(c * sympy.exp(-2 * sympy.pi * sympy.I * 1 * n / N) for n in range(N))
    ok0 = sympy.simplify(X0) == c * N
    ok1 = sympy.simplify(X1) == 0
    return ok0 and ok1


def _parsevals_theorem():
    """Verify Parseval's for x = [1, 2, 3, 4]."""
    import sympy
    x = [1, 2, 3, 4]
    N = len(x)
    time_energy = sum(v ** 2 for v in x)
    # Compute DFT symbolically
    X = []
    for k in range(N):
        Xk = sum(x[n] * sympy.exp(-2 * sympy.pi * sympy.I * k * n / N) for n in range(N))
        X.append(sympy.simplify(Xk))
    freq_energy = sum(abs(Xk) ** 2 for Xk in X) / N
    return sympy.Eq(sympy.nsimplify(sympy.simplify(sympy.Abs(freq_energy))), time_energy)


def _dft_matrix_symmetric():
    """DFT matrix W is symmetric: W_{kn} = W_{nk}."""
    import sympy
    N = 4
    for k in range(N):
        for n in range(N):
            wkn = sympy.exp(-2 * sympy.pi * sympy.I * k * n / N)
            wnk = sympy.exp(-2 * sympy.pi * sympy.I * n * k / N)
            if sympy.simplify(wkn - wnk) != 0:
                return False
    return True


def _idft_recovers_signal():
    """Verify IDFT(DFT(x)) = x symbolically for N=4."""
    import sympy
    N = 4
    x = [sympy.Rational(1), sympy.Rational(2), sympy.Rational(3), sympy.Rational(4)]
    # Forward DFT
    X = []
    for k in range(N):
        Xk = sum(x[n] * sympy.exp(-2 * sympy.pi * sympy.I * k * n / N) for n in range(N))
        X.append(sympy.simplify(Xk))
    # Inverse DFT
    x_rec = []
    for n in range(N):
        xn = sum(X[k] * sympy.exp(2 * sympy.pi * sympy.I * k * n / N) for k in range(N)) / N
        x_rec.append(sympy.simplify(xn))
    for n in range(N):
        if sympy.simplify(x_rec[n] - x[n]) != 0:
            return False
    return True


# -------------------------------------------------------------------
# Structural helpers
# -------------------------------------------------------------------

def _dft_invertibility():
    """IDFT(DFT(x)) = x for a test signal."""
    x = np.array([1.5, -2.3, 4.1, 0.7, -1.2, 3.3, -0.5, 2.8])
    X = np.fft.fft(x)
    x_recovered = np.fft.ifft(X).real
    if not np.allclose(x, x_recovered, atol=1e-12):
        return False, f"Max error: {np.max(np.abs(x - x_recovered)):.2e}"
    return True, ""


def _parsevals_numeric():
    """sum |x_n|^2 = (1/N) sum |X_k|^2 for a random signal."""
    rng = np.random.default_rng(42)
    x = rng.standard_normal(64)
    X = np.fft.fft(x)
    time_energy = np.sum(x ** 2)
    freq_energy = np.sum(np.abs(X) ** 2) / len(x)
    if not np.isclose(time_energy, freq_energy, rtol=1e-10):
        return False, f"Time energy={time_energy:.6f}, Freq energy={freq_energy:.6f}"
    return True, ""


def _convolution_theorem_numeric():
    """Circular convolution via time domain matches pointwise product in freq domain."""
    N = 8
    x = np.array([1, 2, 3, 4, 0, 0, 0, 0], dtype=float)
    y = np.array([1, 1, 0, 0, 0, 0, 0, 0], dtype=float)

    # Circular convolution via DFT
    X = np.fft.fft(x)
    Y = np.fft.fft(y)
    z_freq = np.fft.ifft(X * Y).real

    # Direct circular convolution
    z_time = np.zeros(N)
    for n in range(N):
        for m in range(N):
            z_time[n] += x[m] * y[(n - m) % N]

    if not np.allclose(z_freq, z_time, atol=1e-10):
        return False, f"Max error: {np.max(np.abs(z_freq - z_time)):.2e}"
    return True, ""


def _conjugate_symmetry():
    """For real signal, X_{N-k} = conj(X_k)."""
    x = np.array([1, 3, 5, 7, 2, 4, 6, 8], dtype=float)
    X = np.fft.fft(x)
    N = len(x)
    for k in range(1, N // 2):
        if not np.isclose(X[N - k], np.conj(X[k]), atol=1e-12):
            return False, f"X[{N-k}] = {X[N-k]}, conj(X[{k}]) = {np.conj(X[k])}"
    return True, ""


def _circular_shift_property():
    """Shifting by m multiplies DFT by e^{-2pi i km/N}."""
    x = np.array([1, 2, 3, 4, 5, 6, 7, 8], dtype=float)
    N = len(x)
    m = 2
    x_shifted = np.roll(x, m)  # circular shift by m
    X = np.fft.fft(x)
    X_shifted = np.fft.fft(x_shifted)
    for k in range(N):
        phase = np.exp(-2j * np.pi * k * m / N)
        expected = X[k] * phase
        if not np.isclose(X_shifted[k], expected, atol=1e-10):
            return False, f"At k={k}: shifted={X_shifted[k]:.4f}, expected={expected:.4f}"
    return True, ""


def _dft_linearity():
    """DFT(ax+by) = a*DFT(x) + b*DFT(y)."""
    x = np.array([1, -1, 2, -2, 3, -3, 4, -4], dtype=float)
    y = np.array([0.5, 1.5, -0.5, 2.5, 1.0, -1.0, 0.0, 3.0], dtype=float)
    a, b = 2.7, -1.3
    X = np.fft.fft(x)
    Y = np.fft.fft(y)
    XY_combined = np.fft.fft(a * x + b * y)
    expected = a * X + b * Y
    if not np.allclose(XY_combined, expected, atol=1e-10):
        return False, f"Max error: {np.max(np.abs(XY_combined - expected)):.2e}"
    return True, ""


def _modulation_property():
    """Modulation: multiplying by e^{2pi inm/N} shifts spectrum by m bins."""
    N = 8
    x = np.array([1, 2, 3, 4, 5, 6, 7, 8], dtype=float)
    m = 3
    X = np.fft.fft(x)
    # Modulate: y_n = x_n * e^{2pi i n m / N}
    y = x * np.exp(2j * np.pi * np.arange(N) * m / N)
    Y = np.fft.fft(y)
    # Y_k should equal X_{(k-m) mod N}
    for k in range(N):
        expected = X[(k - m) % N]
        if not np.isclose(Y[k], expected, atol=1e-10):
            return False, f"At k={k}: Y[k]={Y[k]:.4f}, expected X[{(k-m)%N}]={expected:.4f}"
    return True, ""


def _fft_speedup_ratio():
    """Verify the stated speedup: for N=2^20, ratio ~ 50000."""
    N = 2 ** 20
    naive_ops = N ** 2
    fft_ops = N * math.log2(N)
    ratio = naive_ops / fft_ops
    # Chapter states "a factor of 50,000"
    if not (45000 < ratio < 55000):
        return False, f"Speedup ratio = {ratio:.0f}, expected ~50000"
    return True, ""


def _windowing_reduces_leakage(P_rect, P_hann):
    """Verify that Hann windowing reduces far-bin leakage."""
    # For a signal at freq 5.5/64, energy should be near bins 5 and 6
    # Far bins (e.g., k=10..30) should have less power with Hann
    far_power_rect = np.sum(P_rect[10:30])
    far_power_hann = np.sum(P_hann[10:30])
    if not (far_power_hann < far_power_rect):
        return False, f"Hann far-bin power {far_power_hann:.4f} >= rect {far_power_rect:.4f}"
    return True, ""


def _parsevals_multiple_signals():
    """Parseval holds for constant, ramp, and random signals."""
    signals = {
        "constant": np.ones(32) * 5.0,
        "ramp": np.arange(32, dtype=float),
        "random": np.random.default_rng(123).standard_normal(32),
    }
    for name, x in signals.items():
        X = np.fft.fft(x)
        te = np.sum(x ** 2)
        fe = np.sum(np.abs(X) ** 2) / len(x)
        if not np.isclose(te, fe, rtol=1e-10):
            return False, f"{name}: time={te:.6f} != freq={fe:.6f}"
    return True, ""


def _ex223_shift_property():
    """Exercise 22.3: Circular shift property for multiple signals and shifts."""
    rng = np.random.default_rng(42)
    for N in [8, 16, 32]:
        x = rng.standard_normal(N)
        X = np.fft.fft(x)
        for m in range(N):
            x_shifted = np.roll(x, m)
            X_shifted = np.fft.fft(x_shifted)
            for k in range(N):
                phase = np.exp(-2j * np.pi * k * m / N)
                expected = X[k] * phase
                if not np.isclose(X_shifted[k], expected, atol=1e-10):
                    return False, f"N={N}, m={m}, k={k}: got {X_shifted[k]:.6f}, expected {expected:.6f}"
    return True, ""


def _ex226_idft_via_fft():
    """Exercise 22.6: IDFT via forward DFT: x = conj(DFT(conj(X)))/N."""
    test_signals = [
        np.array([1, 2, 3, 4], dtype=complex),
        np.array([1, -1, 1, -1, 2, -2, 3, -3], dtype=complex),
        np.random.default_rng(99).standard_normal(16) + 0j,
    ]
    for x in test_signals:
        X = np.fft.fft(x)
        N = len(X)
        # IDFT via forward DFT: conj(DFT(conj(X))) / N
        x_recovered = np.conj(np.fft.fft(np.conj(X))) / N
        if not np.allclose(x, x_recovered, atol=1e-12):
            return False, f"Max error: {np.max(np.abs(x - x_recovered)):.2e}"
    return True, ""
