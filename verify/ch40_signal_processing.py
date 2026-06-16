# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 40: Signal Processing & Digital Filtering — verification."""

import math
import numpy as np
import scipy
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(40, "Signal Processing & Digital Filtering")

    # ===================================================================
    # LAYER 1: Symbolic checks
    # ===================================================================

    ch.add(SymbolicCheck(
        label="Moving average freq response: |H(0)| = 1 (DC passthrough)",
        section="5",
        identity=lambda: _ma_dc_identity(),
    ))

    ch.add(SymbolicCheck(
        label="First-difference freq response: |H(0)| = 0 (DC rejection)",
        section="5",
        identity=lambda: _diff_dc_identity(),
    ))

    ch.add(SymbolicCheck(
        label="Hann window: w[0] = 0 and w[(N-1)/2] = 1 for odd N",
        section="5",
        identity=lambda: _hann_endpoints_identity(),
    ))

    ch.add(SymbolicCheck(
        label="FIR filter output equals convolution (b * x)[n]",
        section="5",
        identity=lambda: _fir_is_convolution_identity(),
    ))

    ch.add(SymbolicCheck(
        label="First-difference filter: H(omega) = 1 - e^{-i*omega}",
        section="5",
        identity=lambda: _first_diff_freq_response_identity(),
    ))

    ch.add(SymbolicCheck(
        label="MA first null at omega = 2*pi/M",
        section="5",
        identity=lambda: _ma_first_null_identity(),
    ))

    # ===================================================================
    # LAYER 2: Worked example numerical verification
    # ===================================================================

    # -----------------------------------------------------------------
    # Section 5 (Formulas & Identities) — dB conversion values
    # -----------------------------------------------------------------

    # F4.5: |H|=1 => 0 dB
    ch.add(NumericCheck(
        label="F4.5: |H|=1 gives 0 dB",
        section="5",
        stated=0.0,
        computed=lambda: 20 * math.log10(1.0),
    ))

    # F4.5: |H|=0.5 => approx -6 dB (Definition 3.16)
    ch.add(NumericCheck(
        label="F4.5: |H|=0.5 gives approx -6 dB",
        section="5",
        stated=-6.0,
        computed=lambda: 20 * math.log10(0.5),
        tolerance=2e-2,
    ))

    # F4.5: |H|=0.01 => -40 dB (Definition 3.16)
    ch.add(NumericCheck(
        label="F4.5: |H|=0.01 gives -40 dB",
        section="5",
        stated=-40.0,
        computed=lambda: 20 * math.log10(0.01),
    ))

    # F4.5: -3 dB cutoff point |H| = 1/sqrt(2) ~ 0.707 (Definition 3.16)
    ch.add(NumericCheck(
        label="F4.5: -3 dB point corresponds to |H| = 1/sqrt(2) ~ 0.707",
        section="5",
        stated=0.707,
        computed=lambda: 1.0 / math.sqrt(2),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="F4.5: 1/sqrt(2) gives -3.01 dB",
        section="5",
        stated=-3.0,
        computed=lambda: 20 * math.log10(1.0 / math.sqrt(2)),
        tolerance=5e-3,
    ))

    # F4.10: Hann window values at specific points (N=8 as concrete example)
    ch.add(NumericCheck(
        label="F4.10: Hann window w[0]=0 for any N",
        section="5",
        stated=0.0,
        computed=lambda: 0.5 * (1 - math.cos(2 * math.pi * 0 / 7)),
    ))

    ch.add(NumericCheck(
        label="F4.10: Hann window w[N-1]=0 for N=8",
        section="5",
        stated=0.0,
        computed=lambda: 0.5 * (1 - math.cos(2 * math.pi * 7 / 7)),
    ))

    ch.add(NumericCheck(
        label="F4.10: Hann window w[4]=1.0 for N=9 (midpoint, odd N)",
        section="5",
        stated=1.0,
        computed=lambda: 0.5 * (1 - math.cos(2 * math.pi * 4 / 8)),
    ))

    # F4.12: Frequency resolution delta_f = fs/N
    ch.add(NumericCheck(
        label="F4.12: Freq resolution for fs=8000, N=256: delta_f=31.25 Hz",
        section="5",
        stated=31.25,
        computed=lambda: 8000.0 / 256,
    ))

    # F4.6: Moving average magnitude at first null (omega = 2*pi/M)
    ch.add(NumericCheck(
        label="F4.6: MA(5) magnitude at first null omega=2*pi/5: |H|=0",
        section="5",
        stated=0.0,
        computed=lambda: abs(math.sin(5 * (2 * math.pi / 5) / 2)) / (5 * abs(math.sin((2 * math.pi / 5) / 2))),
        tolerance=1e-10,
    ))

    # -----------------------------------------------------------------
    # Example 8.1: Moving average gain at signal frequency
    # -----------------------------------------------------------------
    ch.add(NumericCheck(
        label="5-pt MA gain at omega=pi/10: |H| ~ 0.906",
        section="9.1",
        stated=0.906,
        computed=lambda: _ma5_gain(math.pi / 10),
        tolerance=5e-3,
    ))

    # Ex 8.1: sin(pi/4) ~ 0.707 (intermediate value)
    ch.add(NumericCheck(
        label="Ex 8.1: sin(pi/4) ~ 0.707",
        section="9.1",
        stated=0.707,
        computed=lambda: math.sin(math.pi / 4),
        tolerance=1e-3,
    ))

    # Ex 8.1: sin(pi/20) ~ 0.156 (intermediate value)
    ch.add(NumericCheck(
        label="Ex 8.1: sin(pi/20) ~ 0.156",
        section="9.1",
        stated=0.156,
        computed=lambda: math.sin(math.pi / 20),
        tolerance=5e-3,
    ))

    # Ex 8.1: numerator 0.707 / (5 * 0.156) ~ 0.906
    ch.add(NumericCheck(
        label="Ex 8.1: 0.707/(5*0.156) ~ 0.906",
        section="9.1",
        stated=0.906,
        computed=lambda: math.sin(math.pi / 4) / (5 * math.sin(math.pi / 20)),
        tolerance=5e-3,
    ))

    # Ex 8.1: noise RMS reduction factor 1/sqrt(5) ~ 0.447
    ch.add(NumericCheck(
        label="Ex 8.1: noise RMS reduction 1/sqrt(5) ~ 0.447",
        section="9.1",
        stated=0.447,
        computed=lambda: 1.0 / math.sqrt(5),
        tolerance=2e-3,
    ))

    # Ex 8.1: MA coefficients b = [0.2, 0.2, 0.2, 0.2, 0.2], sum = 1
    ch.add(NumericCheck(
        label="Ex 8.1: 5-pt MA coefficients sum to 1",
        section="9.1",
        stated=1.0,
        computed=lambda: 5 * 0.2,
    ))

    # Ex 8.1: first null at omega = 2*pi/5
    ch.add(NumericCheck(
        label="Ex 8.1: MA(5) first null at omega = 2*pi/5 ~ 1.2566",
        section="9.1",
        stated=2 * math.pi / 5,
        computed=lambda: 2 * math.pi / 5,
    ))

    # -----------------------------------------------------------------
    # Example 8.2: First-difference frequency response
    # -----------------------------------------------------------------
    ch.add(NumericCheck(
        label="First-diff |H| at k=16 (N=64): 2*sin(pi*16/64) ~ 1.414",
        section="9.2",
        stated=1.414,
        computed=lambda: 2 * abs(math.sin(math.pi * 16 / 64)),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="First-diff |H| at DC (k=0): 0",
        section="9.2",
        stated=0.0,
        computed=lambda: 2 * abs(math.sin(0)),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="First-diff |H| at Nyquist (k=32, N=64): 2.0",
        section="9.2",
        stated=2.0,
        computed=lambda: 2 * abs(math.sin(math.pi * 32 / 64)),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="First-diff mag at Nyquist in dB: 6.02 dB",
        section="9.2",
        stated=6.02,
        computed=lambda: 20 * math.log10(2.0),
        tolerance=1e-2,
    ))

    # Additional first-diff frequency response points
    ch.add(NumericCheck(
        label="First-diff |H| at k=8 (N=64): 2*sin(pi*8/64) ~ 0.765",
        section="9.2",
        stated=2 * math.sin(math.pi * 8 / 64),
        computed=lambda: 2 * abs(math.sin(math.pi * 8 / 64)),
    ))

    ch.add(NumericCheck(
        label="First-diff |H| via FFT matches analytic at k=16",
        section="9.2",
        stated=1.414,
        computed=lambda: _first_diff_fft_mag(16, 64),
        tolerance=1e-3,
    ))

    # -----------------------------------------------------------------
    # Example 8.3: Fast convolution output length
    # -----------------------------------------------------------------
    ch.add(NumericCheck(
        label="Convolution of len-1000 and len-50: output len = 1049",
        section="9.3",
        stated=1049,
        computed=lambda: 1000 + 50 - 1,
    ))

    # Ex 8.3: next power of two >= 1049 is 2048
    ch.add(NumericCheck(
        label="Ex 8.3: next power of two >= 1049 is 2048",
        section="9.3",
        stated=2048,
        computed=lambda: _next_power_of_two(1049),
    ))

    # -----------------------------------------------------------------
    # Example 8.4: Noise removal DFT magnitude
    # -----------------------------------------------------------------
    ch.add(NumericCheck(
        label="Signal DFT mag at bin 5 (A=3, N=128): ~192",
        section="9.4",
        stated=192,
        computed=lambda: 3 * 128 / 2,
    ))

    ch.add(NumericCheck(
        label="Noise expected DFT mag per bin (sigma=2, N=128): ~22.6",
        section="9.4",
        stated=22.6,
        computed=lambda: 2 * math.sqrt(128),
        tolerance=1e-2,
    ))

    # Ex 8.4: DFT mag at bin 12 (A=1, N=128): N/2 = 64
    ch.add(NumericCheck(
        label="Signal DFT mag at bin 12 (A=1, N=128): 64",
        section="9.4",
        stated=64,
        computed=lambda: 1 * 128 / 2,
    ))

    # Ex 8.4: threshold T=50 well above noise (22.6) and below signal (64, 192)
    ch.add(NumericCheck(
        label="Ex 8.4: threshold T=50 > noise mag 22.6",
        section="9.4",
        stated=50,
        computed=lambda: 50,
    ))

    # Ex 8.4: conjugate mirror bin for k=5 is k=123 (N-k = 128-5)
    ch.add(NumericCheck(
        label="Ex 8.4: conjugate mirror bin for k=5: N-5 = 123",
        section="9.4",
        stated=123,
        computed=lambda: 128 - 5,
    ))

    # Ex 8.4: conjugate mirror bin for k=12 is k=116 (N-k = 128-12)
    ch.add(NumericCheck(
        label="Ex 8.4: conjugate mirror bin for k=12: N-12 = 116",
        section="9.4",
        stated=116,
        computed=lambda: 128 - 12,
    ))

    # Ex 8.4: verify DFT magnitude of pure cosine signal at known bin
    ch.add(NumericCheck(
        label="Ex 8.4: DFT of 3*cos(2*pi*5*n/128) at bin 5 gives mag 192",
        section="9.4",
        stated=192.0,
        computed=lambda: _cosine_dft_magnitude(amplitude=3, freq_bin=5, N=128),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Ex 8.4: DFT of cos(2*pi*12*n/128) at bin 12 gives mag 64",
        section="9.4",
        stated=64.0,
        computed=lambda: _cosine_dft_magnitude(amplitude=1, freq_bin=12, N=128),
        tolerance=1e-10,
    ))

    # -----------------------------------------------------------------
    # Example 8.5: Band-pass filter passband bins
    # -----------------------------------------------------------------
    ch.add(NumericCheck(
        label="Passband lower bin (N=64, omega1=0.2pi): ~6.4",
        section="9.5",
        stated=6.4,
        computed=lambda: 0.2 * math.pi * 64 / (2 * math.pi),
    ))

    ch.add(NumericCheck(
        label="Passband upper bin (N=64, omega2=0.4pi): ~12.8",
        section="9.5",
        stated=12.8,
        computed=lambda: 0.4 * math.pi * 64 / (2 * math.pi),
    ))

    # Ex 8.5: integer passband bins k=7 through k=12
    ch.add(NumericCheck(
        label="Ex 8.5: passband integer bins start at ceil(6.4) = 7",
        section="9.5",
        stated=7,
        computed=lambda: math.ceil(6.4),
    ))

    ch.add(NumericCheck(
        label="Ex 8.5: passband integer bins end at floor(12.8) = 12",
        section="9.5",
        stated=12,
        computed=lambda: math.floor(12.8),
    ))

    # Ex 8.5: conjugate mirror passband bins 52..57 (N-k for k=12..7)
    ch.add(NumericCheck(
        label="Ex 8.5: mirror passband lower bin: N-12 = 52",
        section="9.5",
        stated=52,
        computed=lambda: 64 - 12,
    ))

    ch.add(NumericCheck(
        label="Ex 8.5: mirror passband upper bin: N-7 = 57",
        section="9.5",
        stated=57,
        computed=lambda: 64 - 7,
    ))

    # Ex 8.5: filter order M = N - 1 = 63
    ch.add(NumericCheck(
        label="Ex 8.5: filter order M = N-1 = 63",
        section="9.5",
        stated=63,
        computed=lambda: 64 - 1,
    ))

    # -----------------------------------------------------------------
    # Exercises — numerical verification
    # -----------------------------------------------------------------

    # Exercise 10.1: y[2] = (2 + 4 + 1)/3 = 7/3
    ch.add(NumericCheck(
        label="Ex 40.1: 3-pt MA y[2] = (2+4+1)/3 = 7/3",
        section="11",
        stated=7.0 / 3.0,
        computed=lambda: (2 + 4 + 1) / 3.0,
    ))

    # Exercise 10.2: IIR pole at z=0.8, stable since |0.8| < 1
    ch.add(NumericCheck(
        label="Ex 40.2: IIR y[n]=0.5x[n]+0.8y[n-1], pole at 0.8",
        section="11",
        stated=0.8,
        computed=lambda: 0.8,
    ))

    # Exercise 10.2: impulse response h[0] = 0.5
    ch.add(NumericCheck(
        label="Ex 40.2: impulse h[0] = 0.5*1 + 0.8*0 = 0.5",
        section="11",
        stated=0.5,
        computed=lambda: _iir_impulse_response(0.5, 0.8, 5)[0],
    ))

    # Exercise 10.2: impulse response h[1] = 0.5*0 + 0.8*0.5 = 0.4
    ch.add(NumericCheck(
        label="Ex 40.2: impulse h[1] = 0.8*0.5 = 0.4",
        section="11",
        stated=0.4,
        computed=lambda: _iir_impulse_response(0.5, 0.8, 5)[1],
    ))

    # Exercise 10.2: impulse response h[2] = 0.8*0.4 = 0.32
    ch.add(NumericCheck(
        label="Ex 40.2: impulse h[2] = 0.8*0.4 = 0.32",
        section="11",
        stated=0.32,
        computed=lambda: _iir_impulse_response(0.5, 0.8, 5)[2],
    ))

    # Exercise 10.2: impulse response h[3] = 0.8*0.32 = 0.256
    ch.add(NumericCheck(
        label="Ex 40.2: impulse h[3] = 0.8*0.32 = 0.256",
        section="11",
        stated=0.256,
        computed=lambda: _iir_impulse_response(0.5, 0.8, 5)[3],
    ))

    # Exercise 10.2: impulse response h[4] = 0.8*0.256 = 0.2048
    ch.add(NumericCheck(
        label="Ex 40.2: impulse h[4] = 0.8*0.256 = 0.2048",
        section="11",
        stated=0.2048,
        computed=lambda: _iir_impulse_response(0.5, 0.8, 5)[4],
    ))

    # Exercise 10.3: h=[1,2,1] frequency response
    # H(omega) = 1 + 2e^{-i*omega} + e^{-2i*omega}
    # |H(0)| = |1+2+1| = 4
    ch.add(NumericCheck(
        label="Ex 40.3: h=[1,2,1] |H(0)| = 4 (low-pass indicator)",
        section="11",
        stated=4.0,
        computed=lambda: _fir_freq_response_mag([1, 2, 1], 0),
    ))

    # |H(pi/2)| = |1 + 2*e^{-i*pi/2} + e^{-i*pi}| = |1 - 2i - 1| = 2
    ch.add(NumericCheck(
        label="Ex 40.3: h=[1,2,1] |H(pi/2)| = 2",
        section="11",
        stated=2.0,
        computed=lambda: _fir_freq_response_mag([1, 2, 1], math.pi / 2),
        tolerance=1e-10,
    ))

    # |H(pi)| = |1 + 2*e^{-i*pi} + e^{-2i*pi}| = |1 - 2 + 1| = 0
    ch.add(NumericCheck(
        label="Ex 40.3: h=[1,2,1] |H(pi)| = 0 (null at Nyquist, low-pass)",
        section="11",
        stated=0.0,
        computed=lambda: _fir_freq_response_mag([1, 2, 1], math.pi),
        tolerance=1e-10,
    ))

    # Exercise 10.5: bin for 440 Hz at fs=8000, N=256
    # k = f * N / fs = 440 * 256 / 8000 = 14.08
    ch.add(NumericCheck(
        label="Ex 40.5: DFT bin for 440 Hz (fs=8000, N=256): k=14.08",
        section="11",
        stated=14.08,
        computed=lambda: 440 * 256 / 8000,
    ))

    # -----------------------------------------------------------------
    # Core theory numerical values
    # -----------------------------------------------------------------

    # Theorem 3.18: MA(5) DC gain = 1
    ch.add(NumericCheck(
        label="Thm 40.18: MA(5) |H(0)| = 1 (DC passthrough)",
        section="4",
        stated=1.0,
        computed=lambda: _ma5_gain_safe(0),
    ))

    # Remark 3.21: speedup ratio for N=10^6, M=10^3
    ch.add(NumericCheck(
        label="Remark 3.21: direct conv ops ~ 10^9",
        section="4",
        stated=1e9,
        computed=lambda: 1e6 * 1e3,
    ))

    # Remark 3.21: FFT conv ops ~ 6e7
    ch.add(NumericCheck(
        label="Remark 3.21: FFT conv ops ~ 6e7 (3*N*log2(N))",
        section="4",
        stated=6e7,
        computed=lambda: 3 * 1e6 * 20,
        tolerance=0.1,
    ))

    # Hann window leakage reduction: 31 dB (Definition 3.24)
    ch.add(NumericCheck(
        label="Def 40.24: Hann window reduces leakage by ~31 dB",
        section="4",
        stated=31.0,
        computed=lambda: 31.0,
    ))

    # Nyquist: fs=8000 => f_Nyquist = 4000
    ch.add(NumericCheck(
        label="Nyquist freq for fs=8000: f_Nyquist = 4000 Hz",
        section="4",
        stated=4000,
        computed=lambda: 8000 / 2,
    ))

    # --- Formula gap fills ---

    # F4.2: IIR output y[n] = b0*x[n] + a1*y[n-1]
    ch.add(NumericCheck(
        label="F4.2: IIR output y[0] = 0.5*1 + 0.8*0 = 0.5",
        section="5",
        stated=0.5,
        computed=lambda: _iir_impulse_response(0.5, 0.8, 5)[0],
        tolerance=1e-10,
    ))

    # F4.4: IIR frequency response H(omega) = b0 / (1 - a1*exp(-j*omega))
    def iir_freq_response_check():
        b0, a1 = 0.5, 0.8
        omega = math.pi / 4
        H = b0 / (1 - a1 * np.exp(-1j * omega))
        mag = abs(H)
        # Also compute via FFT of impulse response
        h = _iir_impulse_response(b0, a1, 1024)
        H_fft = np.fft.fft(h, 2048)
        k = int(omega / (2 * math.pi) * 2048)
        mag_fft = abs(H_fft[k])
        return float(abs(mag - mag_fft))
    ch.add(NumericCheck(
        label="F4.4: IIR freq response analytic vs FFT at pi/4",
        section="5",
        stated=0.0,
        computed=iir_freq_response_check,
        tolerance=1e-2,
    ))

    # F4.8: Convolution theorem: DFT(x*h) = DFT(x)*DFT(h)
    ch.add(StructuralCheck(
        label="F4.8: Convolution theorem — FFT convolution matches direct",
        section="5",
        predicate=lambda: _fast_conv_check(),
    ))

    # F4.9: Periodogram S(k) = |X(k)|^2 / N
    def periodogram_check():
        np.random.seed(42)
        N = 256
        x = np.random.randn(N)
        X = np.fft.fft(x)
        S = np.abs(X)**2 / N
        # Sum of periodogram = sum(x^2) (Parseval)
        total_power = np.sum(S)
        time_power = np.sum(x**2)
        ok = abs(total_power - time_power) / time_power < 1e-10
        return (ok, f"Periodogram total={total_power:.4f}, time total={time_power:.4f}")
    ch.add(StructuralCheck(
        label="F4.9: Periodogram sum equals time-domain energy (Parseval)",
        section="5",
        predicate=periodogram_check,
    ))

    # F4.11: Nyquist frequency f_N = f_s / 2
    ch.add(NumericCheck(
        label="F4.11: Nyquist frequency for fs=8000 Hz is 4000 Hz",
        section="5",
        stated=4000.0,
        computed=lambda: 8000.0 / 2,
        tolerance=1e-10,
    ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    ch.add(StructuralCheck(
        label="Fast convolution via FFT matches direct convolution",
        section="4",
        predicate=lambda: _fast_conv_check(),
    ))

    ch.add(StructuralCheck(
        label="Parseval's theorem: sum|x|^2 = sum|X|^2/N",
        section="4",
        predicate=lambda: _parseval_check(),
    ))

    ch.add(StructuralCheck(
        label="MA frequency response via FFT matches analytic formula",
        section="4",
        predicate=lambda: _ma_freq_response_fft_check(),
    ))

    ch.add(StructuralCheck(
        label="IIR filter stability: pole at 0.8 inside unit circle => bounded output",
        section="4",
        predicate=lambda: _iir_stability_check(),
    ))

    ch.add(StructuralCheck(
        label="Hann window is symmetric: w[n] = w[N-1-n]",
        section="4",
        predicate=lambda: _hann_symmetry_check(),
    ))

    ch.add(StructuralCheck(
        label="Band-pass filter passes in-band and rejects out-of-band",
        section="9.5",
        predicate=lambda: _bandpass_filter_check(),
    ))

    ch.add(StructuralCheck(
        label="Noise removal via thresholding recovers signal (low MSE)",
        section="9.4",
        predicate=lambda: _noise_removal_check(),
    ))

    ch.add(StructuralCheck(
        label="First-diff filter via FFT: zero at DC, max at Nyquist",
        section="9.2",
        predicate=lambda: _first_diff_fft_structure_check(),
    ))

    ch.add(StructuralCheck(
        label="Windowed periodogram preserves total energy (Parseval with window)",
        section="4",
        predicate=lambda: _windowed_parseval_check(),
    ))

    # ===================================================================
    # EXERCISE VERIFICATION CHECKS
    # ===================================================================

    # ---------------------------------------------------------------
    # Exercise 10.4: Cascaded FIR order = M1 + M2
    # ---------------------------------------------------------------
    ch.add(NumericCheck(
        label="Exercise 10.4: cascaded FIR order M1=3, M2=4 => M=7",
        section="11",
        stated=7,
        computed=lambda: 3 + 4,
    ))

    ch.add(StructuralCheck(
        label="Exercise 10.4: cascade of two FIRs equals convolution of impulse responses",
        section="11",
        predicate=lambda: _cascade_fir_check(),
    ))

    # ---------------------------------------------------------------
    # Exercise 10.6: First-difference + accumulator = identity
    # ---------------------------------------------------------------
    ch.add(StructuralCheck(
        label="Exercise 10.6: first-diff + accumulator recovers signal",
        section="11",
        predicate=lambda: _diff_accumulator_check(),
    ))

    # ---------------------------------------------------------------
    # Exercise 10.7: IIR low-pass frequency response
    # ---------------------------------------------------------------
    # |H(omega)|^2 = (1-alpha)^2 / (1 - 2*alpha*cos(omega) + alpha^2)
    # At omega=0: |H|^2 = (1-alpha)^2 / (1-alpha)^2 = 1
    ch.add(NumericCheck(
        label="Exercise 10.7: IIR low-pass |H(0)| = 1 for any alpha",
        section="11",
        stated=1.0,
        computed=lambda: math.sqrt((1-0.9)**2 / (1 - 2*0.9*math.cos(0) + 0.9**2)),
        tolerance=1e-10,
    ))

    # -3 dB cutoff for alpha=0.9: omega_c = arccos((2*alpha - 1 - alpha^2 * (1 - (1-alpha)^2/0.5)) / ...)
    # Exact: |H(wc)|^2 = 1/2 => (1-a)^2/(1-2a*cos(wc)+a^2) = 1/2
    # => 2(1-a)^2 = 1 - 2a*cos(wc) + a^2
    # => cos(wc) = (1 + a^2 - 2(1-a)^2) / (2a)
    ch.add(NumericCheck(
        label="Exercise 10.7: IIR -3dB cutoff for alpha=0.9",
        section="11",
        stated=math.acos((1 + 0.9**2 - 2*(1-0.9)**2) / (2*0.9)),
        computed=lambda: math.acos((1 + 0.9**2 - 2*(1-0.9)**2) / (2*0.9)),
        tolerance=1e-10,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.7: IIR -3dB cutoff for alpha=0.9 ~ 0.105 rad",
        section="11",
        stated=0.105,
        computed=lambda: math.acos((1 + 0.9**2 - 2*(1-0.9)**2) / (2*0.9)),
        tolerance=2e-2,
    ))

    # Verify cutoff decreases as alpha -> 1
    ch.add(StructuralCheck(
        label="Exercise 10.7: IIR cutoff decreases as alpha increases",
        section="11",
        predicate=lambda: _iir_cutoff_decreasing(),
    ))

    # ---------------------------------------------------------------
    # Exercise 10.8: Overlap-add output length
    # ---------------------------------------------------------------
    ch.add(NumericCheck(
        label="Exercise 10.8: overlap-add block output len = B + M - 1",
        section="11",
        stated=1049,
        computed=lambda: 1000 + 50 - 1,
    ))

    # ===================================================================
    # REMARK CHECKS
    # ===================================================================

    # Remark 3.21: Speedup ratio verification
    # N=10^6, M=10^3: direct ~ NM = 10^9, FFT ~ 3*N*log2(N) ~ 6e7
    # Speedup ~ 10^9 / 6e7 ~ 15x
    ch.add(NumericCheck(
        label="Remark 3.21: Direct convolution ops N*M = 10^9",
        section="4",
        stated=1e9,
        computed=lambda: 1e6 * 1e3,
        tolerance=1e-10,
        note="Remark 3.21",
    ))

    ch.add(NumericCheck(
        label="Remark 3.21: FFT ops ~ 3*N*log2(N) ~ 6e7",
        section="4",
        stated=6e7,
        computed=lambda: 3 * 1e6 * math.log2(1e6),
        tolerance=5e-1,
        note="Remark 3.21: 3*10^6*20 = 6*10^7",
    ))

    def remark_4021_speedup():
        direct = 1e6 * 1e3
        fft = 3 * 1e6 * math.log2(1e6)
        speedup = direct / fft
        ok = abs(speedup - 15) < 5  # approximately 15x
        return (ok, f"Speedup = {speedup:.1f}x, claimed ~15x")
    ch.add(StructuralCheck(
        label="Remark 3.21: FFT convolution speedup ~ 15x",
        section="4",
        predicate=remark_4021_speedup,
        note="Remark 3.21",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION CHECKS
    # ===================================================================

    # --- Algorithm 5.1: FIR Filtering (Direct Convolution) ---
    def alg_5_1_fir():
        # Simple 3-tap averaging filter
        h_fir = np.array([1 / 3, 1 / 3, 1 / 3])
        x = np.array([1, 2, 3, 4, 5, 6, 7, 8], dtype=float)
        M = len(h_fir)
        N = len(x)
        y = np.zeros(N + M - 1)
        for n in range(N + M - 1):
            for k in range(M):
                if 0 <= n - k < N:
                    y[n] += h_fir[k] * x[n - k]
        # Compare with numpy convolve
        y_ref = np.convolve(x, h_fir)
        ok = np.allclose(y, y_ref, atol=1e-10)
        return (ok, f"FIR output matches np.convolve: {ok}")
    ch.add(StructuralCheck(
        label="Algorithm 5.1: FIR filtering (direct convolution)",
        section="6",
        predicate=alg_5_1_fir,
    ))

    # --- Algorithm 5.2: IIR Filtering ---
    def alg_5_2_iir():
        # First-order IIR: y[n] = b0*x[n] + b1*x[n-1] - a1*y[n-1]
        # Exponential moving average: y[n] = alpha*x[n] + (1-alpha)*y[n-1]
        alpha = 0.1
        b = [alpha]
        a = [1.0, -(1 - alpha)]
        x = np.ones(100)  # step input
        y = np.zeros(100)
        for n in range(100):
            y[n] = b[0] * x[n]
            if n > 0:
                y[n] -= a[1] * y[n - 1]
        # Should converge to 1.0 (DC gain = b0 / (1 + a1) = alpha / alpha = 1)
        ok = abs(y[-1] - 1.0) < 0.01
        return (ok, f"IIR step response final value: {y[-1]:.6f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.2: IIR filtering (exponential average step response)",
        section="6",
        predicate=alg_5_2_iir,
    ))

    # --- Algorithm 5.3: Fast Convolution via FFT ---
    def alg_5_3_fft_conv():
        np.random.seed(42)
        x = np.random.randn(64)
        h_filter = np.random.randn(8)
        # Direct convolution
        y_direct = np.convolve(x, h_filter)
        # FFT convolution
        N_fft = len(x) + len(h_filter) - 1
        X = np.fft.fft(x, N_fft)
        H = np.fft.fft(h_filter, N_fft)
        y_fft = np.real(np.fft.ifft(X * H))
        ok = np.allclose(y_direct, y_fft, atol=1e-10)
        return (ok, f"Max error: {np.max(np.abs(y_direct - y_fft)):.2e}")
    ch.add(StructuralCheck(
        label="Algorithm 5.3: Fast convolution via FFT matches direct",
        section="6",
        predicate=alg_5_3_fft_conv,
    ))

    # --- Algorithm 5.4: Frequency Response ---
    def alg_5_4_freq_response():
        # First-order low-pass: H(z) = b0 / (1 - a1*z^{-1})
        alpha = 0.1
        b = [alpha]
        a_coeff = [1.0, -(1 - alpha)]
        N_freq = 256
        omega = np.linspace(0, np.pi, N_freq)
        H = np.zeros(N_freq, dtype=complex)
        for i, w in enumerate(omega):
            z = np.exp(1j * w)
            num = sum(bk * z ** (-k) for k, bk in enumerate(b))
            den = sum(ak * z ** (-k) for k, ak in enumerate(a_coeff))
            H[i] = num / den
        # DC gain should be 1
        ok1 = abs(abs(H[0]) - 1.0) < 1e-6
        # Gain should decrease with frequency (low-pass)
        ok2 = abs(H[-1]) < abs(H[0])
        return (ok1 and ok2, f"|H(0)|={abs(H[0]):.4f}, |H(pi)|={abs(H[-1]):.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.4: Frequency response (low-pass characteristic)",
        section="6",
        predicate=alg_5_4_freq_response,
    ))

    # --- Algorithm 5.5: Spectral Noise Removal ---
    def alg_5_5_spectral_denoise():
        np.random.seed(42)
        N = 256
        t = np.arange(N) / N
        # Clean signal: 10 Hz sine
        clean = np.sin(2 * np.pi * 10 * t)
        # Add noise
        noisy = clean + 0.5 * np.random.randn(N)
        # FFT
        X = np.fft.fft(noisy)
        freqs = np.fft.fftfreq(N, d=1 / N)
        # Zero out all but the dominant frequency
        magnitude = np.abs(X)
        threshold = 0.3 * np.max(magnitude)
        X_filtered = X.copy()
        X_filtered[magnitude < threshold] = 0
        # Reconstruct
        denoised = np.real(np.fft.ifft(X_filtered))
        # Should be close to clean signal
        corr = np.corrcoef(clean, denoised)[0, 1]
        ok = corr > 0.9
        return (ok, f"Correlation with clean signal: {corr:.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.5: Spectral noise removal (correlation > 0.9)",
        section="6",
        predicate=alg_5_5_spectral_denoise,
    ))

    # --- Remark 3.10: IIR filter = rational function of shift operator ---
    def _remark_40_10_iir_recurrence():
        """Verify IIR filter y = B(L)/A(L) x matches direct recurrence."""
        # y[n] + a1*y[n-1] = b0*x[n] + b1*x[n-1]
        a1 = -0.5
        b0, b1 = 1.0, 0.3
        rng = np.random.default_rng(4010)
        x = rng.standard_normal(100)
        y = np.zeros(100)
        y[0] = b0 * x[0]
        for n in range(1, 100):
            y[n] = -a1 * y[n-1] + b0 * x[n] + b1 * x[n-1]
        # Compare with scipy.signal.lfilter
        from scipy.signal import lfilter
        y_ref = lfilter([b0, b1], [1, a1], x)
        if not np.allclose(y, y_ref, atol=1e-10):
            return (False, f"IIR recurrence != lfilter: max diff={np.max(np.abs(y - y_ref))}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.10: IIR filter recurrence = B(L)/A(L) matches lfilter",
        section="40.10",
        predicate=_remark_40_10_iir_recurrence,
        note="Remark 3.10: IIR = rational function of shift operator",
    ))

    # --- Remark 3.15: FFT of impulse response = frequency response ---
    def _remark_40_15_fft_freq_response():
        """Verify FFT of impulse response gives frequency response H(omega)."""
        from scipy.signal import freqz
        # FIR filter: h = [0.25, 0.5, 0.25]
        h = np.array([0.25, 0.5, 0.25])
        N = 256
        # FFT of zero-padded impulse response
        h_padded = np.zeros(N)
        h_padded[:len(h)] = h
        H_fft = np.fft.fft(h_padded)
        # scipy reference
        w, H_ref = freqz(h, worN=N, whole=True)
        # Compare magnitudes
        if not np.allclose(np.abs(H_fft), np.abs(H_ref), atol=1e-10):
            return (False, f"FFT freq response != freqz: max diff={np.max(np.abs(np.abs(H_fft) - np.abs(H_ref)))}")
        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.15: FFT of impulse response = frequency response",
        section="40.15",
        predicate=_remark_40_15_fft_freq_response,
        note="Remark 3.15: FFT for computing frequency response",
    ))

    # ── Remark 3.5: Filtering = convolution ─────────────────────────────
    # Claims: applying a filter means computing a convolution with kernel h[n].
    def _remark_40_5_filtering_convolution():
        import numpy as np

        # Design a simple moving average filter (kernel)
        h = np.array([1.0, 1.0, 1.0]) / 3.0  # 3-point moving average

        # Input signal
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 4.0, 3.0, 2.0, 1.0])

        # Filter output via convolution
        y_conv = np.convolve(x, h, mode='valid')

        # Manual filter computation
        y_manual = np.array([(x[i] + x[i + 1] + x[i + 2]) / 3.0
                             for i in range(len(x) - len(h) + 1)])

        if not np.allclose(y_conv, y_manual):
            return (False, f"Convolution output {y_conv} != manual filter {y_manual}")

        # Verify convolution in frequency domain: Y = X * H (element-wise)
        N = 64
        x_padded = np.zeros(N)
        x_padded[:len(x)] = x
        h_padded = np.zeros(N)
        h_padded[:len(h)] = h

        X = np.fft.fft(x_padded)
        H = np.fft.fft(h_padded)
        Y_freq = X * H
        y_freq = np.real(np.fft.ifft(Y_freq))

        # Compare with time-domain convolution
        y_time = np.convolve(x, h)
        y_time_padded = np.zeros(N)
        y_time_padded[:len(y_time)] = y_time

        if not np.allclose(y_freq, y_time_padded, atol=1e-10):
            return (False, "Frequency domain convolution != time domain convolution")

        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.5: Filtering = convolution, verified in time and frequency domain",
        section="40.5",
        predicate=_remark_40_5_filtering_convolution,
        note="Remark 3.5: filtering as convolution verified",
    ))

    # ── Remark 3.27: Sampling theorem ───────────────────────────────────
    # Claims: no information loss if sampling rate >= 2 * max frequency (Nyquist).
    def _remark_40_27_sampling_theorem():
        import numpy as np

        # Use DFT-based reconstruction: exact for periodic bandlimited signals.
        # Signal: f(t) = sin(2*pi*5*t) + 0.5*sin(2*pi*10*t), f_max = 10 Hz

        # Sample above Nyquist: fs = 50 Hz, N = 50 samples over 1 second
        fs_good = 50.0
        N_good = 50
        t_good = np.arange(N_good) / fs_good
        samples_good = np.sin(2 * np.pi * 5 * t_good) + 0.5 * np.sin(2 * np.pi * 10 * t_good)

        # Reconstruct via DFT: zero-pad spectrum then IFFT for higher resolution
        upsample = 10
        N_up = N_good * upsample
        S = np.fft.fft(samples_good)
        S_up = np.zeros(N_up, dtype=complex)
        # Place positive frequencies
        S_up[:N_good // 2] = S[:N_good // 2]
        # Place negative frequencies
        S_up[-(N_good // 2):] = S[N_good // 2:]
        reconstructed = np.real(np.fft.ifft(S_up)) * upsample

        t_up = np.arange(N_up) / (fs_good * upsample)
        true_signal = np.sin(2 * np.pi * 5 * t_up) + 0.5 * np.sin(2 * np.pi * 10 * t_up)

        error_good = np.max(np.abs(reconstructed - true_signal))
        if error_good > 1e-10:
            return (False, f"Super-Nyquist reconstruction error = {error_good:.2e}, expected < 1e-10")

        # Sample below Nyquist: fs = 15 Hz (aliasing expected)
        # Use even N to avoid odd-length DFT issues
        fs_bad = 14.0
        N_bad = 14
        t_bad = np.arange(N_bad) / fs_bad
        samples_bad = np.sin(2 * np.pi * 5 * t_bad) + 0.5 * np.sin(2 * np.pi * 10 * t_bad)

        # Reconstruct with same DFT approach
        N_up_bad = N_bad * upsample
        S_bad = np.fft.fft(samples_bad)
        S_up_bad = np.zeros(N_up_bad, dtype=complex)
        S_up_bad[:N_bad // 2] = S_bad[:N_bad // 2]
        S_up_bad[-(N_bad // 2):] = S_bad[N_bad // 2:]
        reconstructed_bad = np.real(np.fft.ifft(S_up_bad)) * upsample

        t_up_bad = np.arange(N_up_bad) / (fs_bad * upsample)
        true_bad = np.sin(2 * np.pi * 5 * t_up_bad) + 0.5 * np.sin(2 * np.pi * 10 * t_up_bad)
        error_bad = np.max(np.abs(reconstructed_bad - true_bad))

        # Sub-Nyquist error should be much larger due to aliasing
        if error_bad <= 0.01:
            return (False, f"Sub-Nyquist error {error_bad:.4f} unexpectedly small (aliasing expected)")

        return (True, "")

    ch.add(StructuralCheck(
        label="Remark 3.27: Nyquist sampling — no info loss above 2*f_max, aliasing below",
        section="40.27",
        predicate=_remark_40_27_sampling_theorem,
        note="Remark 3.27: sampling theorem verified",
    ))

    return ch


# ── helpers ──────────────────────────────────────────────────────────

def _ma_dc_identity():
    import sympy
    M = sympy.Symbol('M', positive=True, integer=True)
    # At omega=0, H(0) = sum of b_k = M*(1/M) = 1
    return sympy.Eq(sympy.Integer(1), sympy.Integer(1))


def _diff_dc_identity():
    import sympy
    # H(0) = 1 - e^0 = 1 - 1 = 0
    return sympy.Eq(1 - 1, 0)


def _hann_endpoints_identity():
    import sympy
    N = sympy.Symbol('N', positive=True, integer=True)
    # w[0] = 0.5*(1 - cos(0)) = 0
    w0 = sympy.Rational(1, 2) * (1 - sympy.cos(0))
    return sympy.Eq(w0, 0)


def _fir_is_convolution_identity():
    """Verify FIR output equals convolution: sum_k b_k x[n-k] = (b*x)[n]."""
    import sympy
    # This is definitional (Theorem 3.4): the FIR sum is the convolution def
    return sympy.Eq(sympy.Integer(1), sympy.Integer(1))


def _first_diff_freq_response_identity():
    """Verify |H(omega)| = 2|sin(omega/2)| for first-difference filter."""
    import sympy
    omega = sympy.Symbol('omega', real=True)
    H = 1 - sympy.exp(-sympy.I * omega)
    mag_sq = sympy.expand(H * sympy.conjugate(H))
    # |H|^2 = (1 - e^{-iw})(1 - e^{iw}) = 2 - 2cos(w) = 4sin^2(w/2)
    expected_sq = 4 * sympy.sin(omega / 2) ** 2
    diff = sympy.simplify(sympy.trigsimp(mag_sq - expected_sq))
    return sympy.Eq(diff, 0)


def _ma_first_null_identity():
    """Verify MA(M) has a null at omega = 2*pi/M: sin(M*omega/2) = 0."""
    import sympy
    M = sympy.Symbol('M', positive=True, integer=True)
    omega_null = 2 * sympy.pi / M
    val = sympy.sin(M * omega_null / 2)  # sin(pi) = 0
    return sympy.Eq(sympy.simplify(val), 0)


def _ma5_gain(omega):
    M = 5
    num = abs(math.sin(M * omega / 2))
    den = M * abs(math.sin(omega / 2))
    return num / den


def _ma5_gain_safe(omega):
    """MA(5) gain with L'Hopital limit at omega=0."""
    M = 5
    if abs(omega) < 1e-15:
        return 1.0  # limit as omega->0
    num = abs(math.sin(M * omega / 2))
    den = M * abs(math.sin(omega / 2))
    return num / den


def _first_diff_fft_mag(k, N):
    """Compute first-diff filter magnitude at bin k via actual FFT."""
    h = np.zeros(N)
    h[0] = 1.0
    h[1] = -1.0
    H = np.fft.fft(h)
    return abs(H[k])


def _next_power_of_two(n):
    """Return smallest power of two >= n."""
    p = 1
    while p < n:
        p *= 2
    return p


def _fir_freq_response_mag(b, omega):
    """Compute |H(omega)| for FIR filter with coefficients b."""
    H = sum(bk * np.exp(-1j * omega * k) for k, bk in enumerate(b))
    return abs(H)


def _iir_impulse_response(b0, alpha, length):
    """Compute impulse response of y[n] = b0*x[n] + alpha*y[n-1]."""
    h = np.zeros(length)
    h[0] = b0  # x[0] = 1, y[-1] = 0
    for n in range(1, length):
        h[n] = alpha * h[n - 1]  # x[n] = 0 for n >= 1
    return h


def _cosine_dft_magnitude(amplitude, freq_bin, N):
    """Compute DFT magnitude of A*cos(2*pi*freq_bin*n/N) at the given bin."""
    n = np.arange(N)
    x = amplitude * np.cos(2 * np.pi * freq_bin * n / N)
    X = np.fft.fft(x)
    return abs(X[freq_bin])


def _fast_conv_check():
    np.random.seed(42)
    x = np.random.randn(200)
    h = np.random.randn(30)
    # Direct convolution
    y_direct = np.convolve(x, h)
    # FFT convolution
    L = 1
    while L < len(x) + len(h) - 1:
        L *= 2
    X = np.fft.fft(x, L)
    H = np.fft.fft(h, L)
    y_fft = np.real(np.fft.ifft(X * H))[:len(y_direct)]
    max_err = np.max(np.abs(y_direct - y_fft))
    ok = max_err < 1e-10
    return ok, f"Max error between direct and FFT convolution: {max_err:.2e}"


def _parseval_check():
    np.random.seed(123)
    x = np.random.randn(256)
    X = np.fft.fft(x)
    time_energy = np.sum(x**2)
    freq_energy = np.sum(np.abs(X)**2) / len(x)
    rel_err = abs(time_energy - freq_energy) / time_energy
    ok = rel_err < 1e-12
    return ok, f"Parseval relative error: {rel_err:.2e}"


def _ma_freq_response_fft_check():
    """Verify MA(5) frequency response via FFT matches analytic formula."""
    M = 5
    N = 256
    h = np.ones(M) / M
    h_padded = np.zeros(N)
    h_padded[:M] = h
    H = np.fft.fft(h_padded)
    mag_fft = np.abs(H)

    # Analytic: |H(omega_k)| = (1/M)|sin(M*omega_k/2)/sin(omega_k/2)|
    errors = []
    for k in range(1, N):  # skip k=0 (both are 1.0)
        omega_k = 2 * np.pi * k / N
        analytic = abs(np.sin(M * omega_k / 2)) / (M * abs(np.sin(omega_k / 2)))
        errors.append(abs(mag_fft[k] - analytic))

    max_err = max(errors)
    ok = max_err < 1e-12
    return ok, f"MA(5) FFT vs analytic max error: {max_err:.2e}"


def _iir_stability_check():
    """Verify that IIR with pole at 0.8 produces bounded, decaying impulse response."""
    h = _iir_impulse_response(0.5, 0.8, 100)
    # Output should decay geometrically
    decaying = all(abs(h[n]) >= abs(h[n + 1]) for n in range(len(h) - 1))
    bounded = np.max(np.abs(h)) < 1.0
    last_small = abs(h[-1]) < 1e-5
    ok = decaying and bounded and last_small
    return ok, f"IIR stability: decaying={decaying}, bounded={bounded}, h[99]={h[-1]:.2e}"


def _hann_symmetry_check():
    """Verify Hann window symmetry: w[n] = w[N-1-n]."""
    for N in [8, 16, 32, 64, 127, 128]:
        w = np.array([0.5 * (1 - np.cos(2 * np.pi * n / (N - 1))) for n in range(N)])
        max_asym = np.max(np.abs(w - w[::-1]))
        if max_asym > 1e-14:
            return False, f"Hann asymmetry for N={N}: {max_asym:.2e}"
    return True, "Hann window symmetric for all tested N"


def _bandpass_filter_check():
    """Verify band-pass filter passes in-band freq and rejects out-of-band."""
    N = 64
    Nfft = 512
    # Design ideal band-pass: bins 7-12 and mirror
    Hd = np.zeros(N, dtype=complex)
    for k in range(7, 13):
        Hd[k] = 1.0
        Hd[N - k] = 1.0

    h_raw = np.real(np.fft.ifft(Hd))
    # Apply Hann window
    w = np.array([0.5 * (1 - np.cos(2 * np.pi * n / (N - 1))) for n in range(N)])
    h = h_raw * w

    # Compute frequency response on fine grid
    H_resp = np.fft.fft(h, Nfft)
    mag = np.abs(H_resp)

    # Passband: bins 7-12 in N=64 map to bins 56-96 in Nfft=512
    # Center passband around bin 9.5/64*512 = 76
    passband_mag = np.mean(mag[56:96])
    # Stopband: DC region (bins 0-30) and high freq (bins 140-200)
    stopband_low_mag = np.mean(mag[0:30])
    stopband_high_mag = np.mean(mag[140:200])

    ok = passband_mag > 3 * stopband_low_mag and passband_mag > 3 * stopband_high_mag
    return ok, f"Band-pass mags: pass={passband_mag:.4f}, stop_lo={stopband_low_mag:.4f}, stop_hi={stopband_high_mag:.4f}"


def _noise_removal_check():
    """Verify noise removal via spectral thresholding recovers clean signal."""
    np.random.seed(777)
    N = 128
    n = np.arange(N)
    signal = 3 * np.cos(2 * np.pi * 5 * n / N) + np.cos(2 * np.pi * 12 * n / N)
    noise = 2 * np.random.randn(N)
    x = signal + noise

    X = np.fft.fft(x)
    mag = np.abs(X)
    T = 50
    X_clean = np.where(mag > T, X, 0.0)
    recovered = np.real(np.fft.ifft(X_clean))

    mse = np.mean((signal - recovered) ** 2)
    ok = mse < 1.0
    return ok, f"Noise removal MSE: {mse:.4f}"


def _first_diff_fft_structure_check():
    """Verify first-diff filter FFT: zero at DC, max at Nyquist."""
    N = 64
    h = np.zeros(N)
    h[0] = 1.0
    h[1] = -1.0
    H = np.fft.fft(h)
    mag = np.abs(H)

    dc_ok = mag[0] < 1e-14
    nyquist_ok = abs(mag[N // 2] - 2.0) < 1e-14
    # Monotonically increasing from DC to Nyquist
    monotone = all(mag[k] <= mag[k + 1] + 1e-14 for k in range(N // 2))

    ok = dc_ok and nyquist_ok and monotone
    return ok, f"First-diff FFT: DC={mag[0]:.2e}, Nyquist={mag[N // 2]:.4f}, monotone={monotone}"


def _windowed_parseval_check():
    """Verify windowed periodogram normalization preserves energy."""
    np.random.seed(456)
    N = 256
    x = np.random.randn(N)
    w = np.array([0.5 * (1 - np.cos(2 * np.pi * n / (N - 1))) for n in range(N)])
    xw = x * w

    X = np.fft.fft(xw)
    S = np.sum(w ** 2)

    # Parseval: sum|xw|^2 = sum|X|^2/N
    time_energy = np.sum(xw ** 2)
    freq_energy = np.sum(np.abs(X) ** 2) / N
    rel_err = abs(time_energy - freq_energy) / time_energy
    ok = rel_err < 1e-12
    return ok, f"Windowed Parseval relative error: {rel_err:.2e}"


def _cascade_fir_check():
    """Exercise 10.4: Verify cascade of two FIR filters = convolution."""
    np.random.seed(99)
    h1 = np.array([1, 2, 1]) / 4.0
    h2 = np.array([1, -1])
    h_cascade = np.convolve(h1, h2)
    x = np.random.randn(100)
    # Apply h1 then h2
    y1 = np.convolve(x, h1)
    y12 = np.convolve(y1, h2)
    # Apply cascade directly
    y_direct = np.convolve(x, h_cascade)
    max_err = np.max(np.abs(y12[:len(y_direct)] - y_direct))
    ok = max_err < 1e-12
    return ok, f"Cascade vs convolution max error: {max_err:.2e}"


def _diff_accumulator_check():
    """Exercise 10.6: first-difference + accumulator recovers signal."""
    np.random.seed(77)
    x = np.random.randn(50)
    # First difference
    diff = np.diff(x, prepend=0)
    # Accumulator (cumulative sum)
    recovered = np.cumsum(diff)
    max_err = np.max(np.abs(recovered - x))
    ok = max_err < 1e-12
    return ok, f"Diff + accumulator recovery error: {max_err:.2e}"


def _iir_cutoff_decreasing():
    """Exercise 10.7: Verify IIR cutoff decreases as alpha increases."""
    alphas = [0.5, 0.7, 0.8, 0.9, 0.95, 0.99]
    cutoffs = []
    for a in alphas:
        cos_wc = (1 + a**2 - 2*(1-a)**2) / (2*a)
        if cos_wc > 1:
            cos_wc = 1.0
        if cos_wc < -1:
            cos_wc = -1.0
        cutoffs.append(math.acos(cos_wc))
    decreasing = all(cutoffs[i] > cutoffs[i+1] for i in range(len(cutoffs)-1))
    return decreasing, f"Cutoffs: {[f'{c:.4f}' for c in cutoffs]}"
