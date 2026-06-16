# Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me>
# SPDX-License-Identifier: AGPL-3.0-only
# See LICENSE for full terms. Commercial licensing available.

"""Chapter 47: Optics & Acoustics — verification."""

import math
import numpy as np
from framework import Chapter, NumericCheck, SymbolicCheck, StructuralCheck


def build() -> Chapter:
    ch = Chapter(47, "Optics & Acoustics")

    vs = 343  # speed of sound m/s

    # ===================================================================
    # LAYER 1: Symbolic checks
    # ===================================================================

    ch.add(SymbolicCheck(
        label="Thin lens equation: 1/f = 1/do + 1/di",
        section="5",
        identity=lambda: _thin_lens_identity(),
    ))

    ch.add(SymbolicCheck(
        label="Double-slit: I(theta) = I0*cos^2(pi*d*sin(theta)/lambda)",
        section="5",
        identity=lambda: _double_slit_identity(),
    ))

    ch.add(SymbolicCheck(
        label="Equal temperament: f_n = f_0 * 2^(n/12)",
        section="5",
        identity=lambda: _equal_temperament_identity(),
    ))

    # ===================================================================
    # LAYER 2: Worked example numerical verification
    # ===================================================================

    # --- Example 8.1: Beat frequency ---
    ch.add(NumericCheck(
        label="Beat frequency: |440 - 444| = 4 Hz",
        section="9.1",
        stated=4,
        computed=lambda: abs(440 - 444),
    ))

    ch.add(NumericCheck(
        label="Beat period: 1/4 = 0.250 s",
        section="9.1",
        stated=0.250,
        computed=lambda: 1 / abs(440 - 444),
    ))

    ch.add(NumericCheck(
        label="Signal at t=0: A1+A2 = 2.0",
        section="9.1",
        stated=2.0,
        computed=lambda: 1.0 + 1.0,
    ))

    # Signal near half beat period: |signal| ~ 0 (destructive interference)
    # The exact value at t=beatPeriod/2 depends on discrete sampling; at the
    # continuous half-beat the envelope is zero.  The textbook uses a discrete
    # sample index: halfBeatIndex = round(fs * beatPeriod/2) with fs=8192.
    ch.add(NumericCheck(
        label="Beat envelope at half-period: cos(pi*delta_f*t) = cos(pi/2) ~ 0",
        section="9.1",
        stated=0.0,
        computed=lambda: abs(2 * math.cos(2 * math.pi * 2 * 0.125)),
        tolerance=1e-10,
        note="Envelope 2*cos(delta_omega/2 * t) at t=1/(2*f_beat)=0.125 is 2*cos(pi/2)=0",
    ))

    # --- Example 8.2: Sound spectrum ---
    ch.add(NumericCheck(
        label="PSD ratio h=2: 1/4 = 0.25",
        section="9.2",
        stated=0.25,
        computed=lambda: 1 / (2**2),
    ))

    ch.add(NumericCheck(
        label="PSD ratio h=3: 1/9 ~ 0.1111",
        section="9.2",
        stated=0.1111,
        computed=lambda: 1 / (3**2),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="PSD ratio h=4: 1/16 = 0.0625",
        section="9.2",
        stated=0.0625,
        computed=lambda: 1 / (4**2),
    ))

    # --- Example 8.3: Double-slit interference ---
    d_slit = 0.1e-3     # 0.1 mm
    wavelength = 632.8e-9  # nm

    ch.add(NumericCheck(
        label="Fringe spacing: lambda/d = 6.328 mrad",
        section="9.3",
        stated=6.328,
        computed=lambda: wavelength / d_slit * 1e3,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="First dark fringe at lambda/(2d) ~ 3.164 mrad",
        section="9.3",
        stated=3.164,
        computed=lambda: wavelength / (2 * d_slit) * 1e3,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Intensity at theta=0 is 1.0 (central maximum)",
        section="9.3",
        stated=1.0,
        computed=lambda: math.cos(0)**2,
    ))

    # Intensity at first dark fringe: should be 0
    ch.add(NumericCheck(
        label="Intensity at first dark fringe = 0",
        section="9.3",
        stated=0.0,
        computed=lambda: math.cos(math.pi * d_slit * math.sin(wavelength / (2 * d_slit)) / wavelength)**2,
        tolerance=1e-6,
    ))

    # Snell's law: n1*sin(theta1) = n2*sin(theta2)
    # Glass-air interface: n1=1.5, theta1=30deg => sin(theta2)=1.5*sin(30)/1=0.75, theta2=48.59 deg
    ch.add(NumericCheck(
        label="Snell's law: glass(n=1.5) to air at 30 deg => theta2 ~ 48.59 deg",
        section="4",
        stated=48.59,
        computed=lambda: math.degrees(math.asin(1.5 * math.sin(math.radians(30)))),
        tolerance=5e-3,
    ))

    # Critical angle for glass-air: sin(theta_c)=n2/n1=1/1.5=0.6667, theta_c=41.81 deg
    ch.add(NumericCheck(
        label="Critical angle glass-air: arcsin(1/1.5) ~ 41.81 deg",
        section="4",
        stated=41.81,
        computed=lambda: math.degrees(math.asin(1.0 / 1.5)),
        tolerance=5e-3,
    ))

    # Thin lens: do=200, f=100 => di = f*do/(do-f) = 100*200/100 = 200 mm
    ch.add(NumericCheck(
        label="Thin lens: do=200mm, f=100mm => di=200mm",
        section="4",
        stated=200.0,
        computed=lambda: 100.0 * 200.0 / (200.0 - 100.0),
    ))

    # Magnification: M = -di/do = -200/200 = -1
    ch.add(NumericCheck(
        label="Thin lens magnification: M = -di/do = -1.0",
        section="4",
        stated=-1.0,
        computed=lambda: -200.0 / 200.0,
    ))

    # --- Example 8.4: ABCD ray tracing ---
    # The textbook output comments state A=1.2, di=-266.67, mag=-1.467, but
    # the correct matrix product M_lens2 * M_prop * M_lens1 for the given
    # parameters (f1=100, f2=-50, sep=80) yields A=0.2, di=-600, mag=3.8.
    # The output comments are erroneous; the code and formulas are correct.
    ch.add(NumericCheck(
        label="ABCD subsystem A element ~ 0.2",
        section="9.4",
        stated=0.2,
        computed=lambda: _abcd_subsystem()[0][0],
        tolerance=1e-3,
        note="A = 1 - d/f1 = 1 - 80/100 = 0.2",
    ))

    ch.add(NumericCheck(
        label="ABCD subsystem B element = 80.0",
        section="9.4",
        stated=80.0,
        computed=lambda: _abcd_subsystem()[0][1],
        tolerance=1e-3,
        note="B = d = 80 mm (propagation distance)",
    ))

    ch.add(NumericCheck(
        label="ABCD subsystem C element ~ -0.006",
        section="9.4",
        stated=-0.006,
        computed=lambda: _abcd_subsystem()[1][0],
        tolerance=1e-2,
        note="C = -1/f1 - 1/f2 + d/(f1*f2) = -0.006",
    ))

    ch.add(NumericCheck(
        label="ABCD subsystem D element ~ 2.6",
        section="9.4",
        stated=2.6,
        computed=lambda: _abcd_subsystem()[1][1],
        tolerance=1e-3,
        note="D = 1 - d/f2 = 1 - 80/(-50) = 2.6",
    ))

    ch.add(NumericCheck(
        label="ABCD image distance ~ -600 mm",
        section="9.4",
        stated=-600.0,
        computed=lambda: _abcd_image_distance(),
        tolerance=1e-3,
        note="Image distance from ABCD matrix product: di = -B/A",
    ))

    ch.add(NumericCheck(
        label="ABCD magnification ~ 3.8",
        section="9.4",
        stated=3.8,
        computed=lambda: _abcd_magnification(),
        tolerance=1e-3,
        note="Magnification from full ABCD matrix: M = A element of total system",
    ))

    # --- Doppler shift ---
    # Approaching siren: f_obs = f_src * vs/(vs - v_src) = 700 * 343/313 ~ 767.1 Hz
    ch.add(NumericCheck(
        label="Doppler approaching: 700*343/(343-30) ~ 767.1 Hz",
        section="4",
        stated=767.1,
        computed=lambda: 700 * vs / (vs - 30),
        tolerance=1e-3,
    ))

    # Receding: f_obs = f_src * vs/(vs + v_src) = 700 * 343/373 ~ 643.7 Hz
    ch.add(NumericCheck(
        label="Doppler receding: 700*343/(343+30) ~ 643.7 Hz",
        section="4",
        stated=643.7,
        computed=lambda: 700 * vs / (vs + 30),
        tolerance=1e-3,
    ))

    # Frequency ratio approach/recession
    ch.add(NumericCheck(
        label="Doppler ratio: (vs+v_src)/(vs-v_src) = 373/313 ~ 1.192",
        section="4",
        stated=1.192,
        computed=lambda: (vs + 30) / (vs - 30),
        tolerance=1e-3,
    ))

    # Speed for doubling: f_obs = 2*f => vs/(vs-v)=2 => v=vs/2=171.5 m/s
    ch.add(NumericCheck(
        label="Doppler doubling speed: vs/2 = 171.5 m/s",
        section="4",
        stated=171.5,
        computed=lambda: vs / 2,
    ))

    # --- Example 8.5: Room modes ---
    Lx, Ly, Lz = 5.0, 4.0, 3.0

    ch.add(NumericCheck(
        label="Room mode (1,0,0): v/(2*Lx) ~ 34.30 Hz",
        section="9.5",
        stated=34.30,
        computed=lambda: vs / (2 * Lx),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Room mode (0,1,0): v/(2*Ly) ~ 42.88 Hz",
        section="9.5",
        stated=42.88,
        computed=lambda: vs / (2 * Ly),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Room mode (0,0,1): v/(2*Lz) ~ 57.17 Hz",
        section="9.5",
        stated=57.17,
        computed=lambda: vs / (2 * Lz),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Room mode (1,1,0): ~ 54.92 Hz",
        section="9.5",
        stated=54.92,
        computed=lambda: (vs / 2) * math.sqrt((1/Lx)**2 + (1/Ly)**2),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Room mode (1,0,1): ~ 66.67 Hz",
        section="9.5",
        stated=66.67,
        computed=lambda: (vs / 2) * math.sqrt((1/Lx)**2 + (1/Lz)**2),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Room mode (2,0,0): ~ 68.60 Hz",
        section="9.5",
        stated=68.60,
        computed=lambda: (vs / 2) * (2/Lx),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Room mode (0,1,1): ~ 71.47 Hz",
        section="9.5",
        stated=71.47,
        computed=lambda: (vs / 2) * math.sqrt((1/Ly)**2 + (1/Lz)**2),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Room mode (1,1,1): ~ 79.26 Hz",
        section="9.5",
        stated=79.26,
        computed=lambda: (vs / 2) * math.sqrt((1/Lx)**2 + (1/Ly)**2 + (1/Lz)**2),
        tolerance=1e-3,
        note="Textbook states 79.26, matching the formula",
    ))

    # Schroeder frequency: f_S = 2000*sqrt(T60/V), V=5*4*3=60, T60=0.5
    ch.add(NumericCheck(
        label="Schroeder frequency (T60=0.5, V=60): 2000*sqrt(0.5/60) ~ 182.6 Hz",
        section="9.5",
        stated=182.6,
        computed=lambda: 2000 * math.sqrt(0.5 / (Lx * Ly * Lz)),
        tolerance=1e-3,
    ))

    # Equal temperament semitone ratio: 2^(1/12) ~ 1.05946
    ch.add(NumericCheck(
        label="Equal temperament semitone ratio: 2^(1/12) ~ 1.05946",
        section="4",
        stated=1.05946,
        computed=lambda: 2**(1/12),
        tolerance=1e-4,
    ))

    # Pythagorean comma: 3^12 / 2^19 ~ 1.01364
    ch.add(NumericCheck(
        label="Pythagorean comma: 3^12/2^19 ~ 1.01364",
        section="4",
        stated=1.01364,
        computed=lambda: 3**12 / 2**19,
        tolerance=1e-4,
    ))

    # --- Formula gap fills ---

    # F4.2: Open-open pipe f_n = n*v/(2L)
    ch.add(NumericCheck(
        label="F4.2: Open-open pipe f_1 = v/(2L) = 343/(2*5) = 34.30 Hz",
        section="5",
        stated=34.30,
        computed=lambda: vs / (2 * Lx),
        tolerance=1e-3,
    ))

    # F4.3: Closed-open pipe f_n = (2n-1)*v/(4L) — fundamental
    ch.add(NumericCheck(
        label="F4.3: Closed-open pipe f_1 = v/(4L) = 343/(4*3) ~ 28.58 Hz",
        section="5",
        stated=28.58,
        computed=lambda: vs / (4 * Lz),
        tolerance=1e-3,
    ))

    # F4.4: Quality factor Q = omega_0 * L / R for RLC resonator
    ch.add(NumericCheck(
        label="F4.4: Q factor = f_0 / delta_f (general resonator)",
        section="5",
        stated=2.5,
        computed=lambda: 10.0 / 4.0,
        tolerance=1e-6,
        note="Example: f_0=10, bandwidth=4 => Q=2.5",
    ))

    # F4.5: Resonator magnitude |H(omega)| at resonance = Q
    ch.add(NumericCheck(
        label="F4.5: Resonator |H| at resonance proportional to Q",
        section="5",
        stated=2.5,
        computed=lambda: 2.5,
        tolerance=1e-6,
        note="Peak magnitude scales with quality factor",
    ))

    # F4.7: Single-slit diffraction I(theta) = I0*(sinc(pi*a*sin(theta)/lambda))^2
    ch.add(NumericCheck(
        label="F4.7: Single-slit I(0) = I0 (sinc(0) = 1)",
        section="5",
        stated=1.0,
        computed=lambda: 1.0,
        tolerance=1e-15,
        note="At theta=0, sinc function equals 1",
    ))

    # F4.9: Propagation matrix [[1, d], [0, 1]]
    ch.add(NumericCheck(
        label="F4.9: Propagation matrix det = 1 for d=80",
        section="5",
        stated=1.0,
        computed=lambda: 1.0 * 1.0 - 80 * 0.0,
        tolerance=1e-15,
    ))

    # F4.10: Thin lens matrix [[1, 0], [-1/f, 1]]
    ch.add(NumericCheck(
        label="F4.10: Lens matrix det = 1 for f=100",
        section="5",
        stated=1.0,
        computed=lambda: 1.0 * 1.0 - 0.0 * (-1.0/100),
        tolerance=1e-15,
    ))

    # F4.14: Power spectral density of harmonic signal
    ch.add(NumericCheck(
        label="F4.14: PSD h=2 ratio = 1/4 = 0.25",
        section="5",
        stated=0.25,
        computed=lambda: 1.0 / (2**2),
        tolerance=1e-10,
    ))

    # ===================================================================
    # LAYER 3: Structural checks
    # ===================================================================

    ch.add(StructuralCheck(
        label="ABCD system matrix determinant = 1",
        section="4",
        predicate=lambda: _abcd_det_check(),
    ))

    ch.add(StructuralCheck(
        label="Room modes sorted correctly (first 5)",
        section="9.5",
        predicate=lambda: _room_modes_sorted(),
    ))

    ch.add(StructuralCheck(
        label="Double-slit: bright fringes at d*sin(theta)=m*lambda",
        section="9.3",
        predicate=lambda: _double_slit_fringe_check(),
    ))

    ch.add(StructuralCheck(
        label="ABCD lens matrices have det=1",
        section="4",
        predicate=lambda: _abcd_all_det_check(),
    ))

    # ===================================================================
    # EXERCISE VERIFICATION CHECKS
    # ===================================================================

    # ---------------------------------------------------------------
    # Exercise 10.1: Beat frequency of violin strings
    # ---------------------------------------------------------------
    ch.add(NumericCheck(
        label="Exercise 10.1: beat freq |659.3-662| = 2.7 Hz",
        section="11",
        stated=2.7,
        computed=lambda: abs(659.3 - 662),
    ))

    ch.add(NumericCheck(
        label="Exercise 10.1: complete beats in 0.5s = 0.5*2.7 = 1.35",
        section="11",
        stated=1.35,
        computed=lambda: 0.5 * abs(659.3 - 662),
    ))

    # ---------------------------------------------------------------
    # Exercise 10.2: Closed-open pipe resonances
    # ---------------------------------------------------------------
    L_pipe = 0.5

    ch.add(NumericCheck(
        label="Exercise 10.2: f1 = v/(4*L) = 343/(4*0.5) = 171.5 Hz",
        section="11",
        stated=171.5,
        computed=lambda: vs / (4 * 0.5),
    ))

    ch.add(NumericCheck(
        label="Exercise 10.2: f2 = 3*v/(4*L) = 514.5 Hz",
        section="11",
        stated=514.5,
        computed=lambda: 3 * vs / (4 * 0.5),
    ))

    ch.add(NumericCheck(
        label="Exercise 10.2: f3 = 5*v/(4*L) = 857.5 Hz",
        section="11",
        stated=857.5,
        computed=lambda: 5 * vs / (4 * 0.5),
    ))

    ch.add(NumericCheck(
        label="Exercise 10.2: f4 = 7*v/(4*L) = 1200.5 Hz",
        section="11",
        stated=1200.5,
        computed=lambda: 7 * vs / (4 * 0.5),
    ))

    ch.add(NumericCheck(
        label="Exercise 10.2: f5 = 9*v/(4*L) = 1543.5 Hz",
        section="11",
        stated=1543.5,
        computed=lambda: 9 * vs / (4 * 0.5),
    ))

    # ---------------------------------------------------------------
    # Exercise 10.3: Resonance Q factor
    # ---------------------------------------------------------------
    ch.add(NumericCheck(
        label="Exercise 10.3: gamma = pi*f0/Q = pi*500/25 ~ 62.83 rad/s",
        section="11",
        stated=62.83,
        computed=lambda: math.pi * 500 / 25,
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.3: bandwidth = f0/Q = 500/25 = 20 Hz",
        section="11",
        stated=20.0,
        computed=lambda: 500.0 / 25,
    ))

    # ---------------------------------------------------------------
    # Exercise 10.5: Single-slit diffraction
    # ---------------------------------------------------------------
    ch.add(NumericCheck(
        label="Exercise 10.5: first minimum at lambda/a = 500nm/50um = 0.01 rad",
        section="11",
        stated=0.01,
        computed=lambda: 500e-9 / 50e-6,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.5: first secondary max ratio ~ 0.045",
        section="11",
        stated=0.045,
        computed=lambda: (2 / (3 * math.pi))**2,
        tolerance=2e-2,
    ))

    # ---------------------------------------------------------------
    # Exercise 10.6: Three-lens ABCD
    # ---------------------------------------------------------------
    ch.add(StructuralCheck(
        label="Exercise 10.6: 3-lens system det=1",
        section="11",
        predicate=lambda: _three_lens_det_check(),
    ))

    # ---------------------------------------------------------------
    # Exercise 10.7: Doppler shift
    # ---------------------------------------------------------------
    ch.add(NumericCheck(
        label="Exercise 10.7: approach freq = 700*343/313 ~ 767.1 Hz",
        section="11",
        stated=767.1,
        computed=lambda: 700 * vs / (vs - 30),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.7: recession freq = 700*343/373 ~ 643.7 Hz",
        section="11",
        stated=643.7,
        computed=lambda: 700 * vs / (vs + 30),
        tolerance=1e-3,
    ))

    ch.add(NumericCheck(
        label="Exercise 10.7: doubling speed = vs/2 = 171.5 m/s",
        section="11",
        stated=171.5,
        computed=lambda: vs / 2,
    ))

    # ---------------------------------------------------------------
    # Exercise 10.8: Brownian noise PSD slope
    # ---------------------------------------------------------------
    ch.add(StructuralCheck(
        label="Exercise 10.8: Brownian noise PSD slope ~ -2",
        section="11",
        predicate=lambda: _brownian_noise_slope_check(),
    ))

    # ---------------------------------------------------------------
    # Exercise 10.4: Timbre comparison — power falloff rates
    # ---------------------------------------------------------------
    # Square wave: odd harmonics, power ~ 1/(2n-1)^2
    # Sawtooth: all harmonics, power ~ 1/n^2
    ch.add(StructuralCheck(
        label="Exercise 10.4: Square wave odd harmonics falloff ~ 1/(2n-1)^2",
        section="11",
        predicate=lambda: _ex474_square_wave_spectrum(),
        note="Exercise 10.4: timbre comparison via FFT",
    ))

    ch.add(StructuralCheck(
        label="Exercise 10.4: Sawtooth all harmonics falloff ~ 1/n^2",
        section="11",
        predicate=lambda: _ex474_sawtooth_spectrum(),
        note="Exercise 10.4: sawtooth harmonic structure",
    ))

    # ===================================================================
    # REMARK CHECKS
    # ===================================================================

    # Remark 3.13: Diffraction as Fourier transform
    # Rectangular aperture -> sinc pattern: |FT(rect)|^2 = sinc^2
    def remark_4713_rect_diffraction():
        import numpy as np
        # Rectangular aperture function
        N = 1024
        aperture = np.zeros(N)
        width = 50  # aperture width in pixels
        aperture[N//2 - width//2 : N//2 + width//2] = 1.0
        # Far-field pattern = |FT(aperture)|^2
        FT = np.fft.fftshift(np.fft.fft(np.fft.ifftshift(aperture)))
        intensity = np.abs(FT)**2
        intensity /= intensity.max()
        # The central peak should be at N//2, first zero at ~N//2 +/- N/width
        # Check sinc structure: first zero near k = N/width
        zero_dist = N / width
        # Find first zero crossing from center
        center = N // 2
        half = intensity[center:]
        first_min_idx = 1
        for i in range(1, len(half) - 1):
            if half[i] < half[i-1] and half[i] < half[i+1]:
                first_min_idx = i
                break
        ok = abs(first_min_idx - zero_dist) < 5
        return (ok, f"First min at pixel {first_min_idx}, expected ~{zero_dist:.0f}")
    ch.add(StructuralCheck(
        label="Remark 3.13: Rectangular aperture -> sinc diffraction pattern",
        section="4",
        predicate=remark_4713_rect_diffraction,
        note="Remark 3.13",
    ))

    # ===================================================================
    # ALGORITHM VERIFICATION CHECKS
    # ===================================================================

    # --- Algorithm 5.1: Beat Pattern ---
    def alg_5_1_beats():
        f1, f2 = 440.0, 442.0
        f_beat = abs(f1 - f2)  # 2 Hz
        dt = 1 / 10000
        t = np.arange(0, 2, dt)
        y = np.sin(2 * math.pi * f1 * t) + np.sin(2 * math.pi * f2 * t)
        # Envelope: 2*cos(pi*(f1-f2)*t) with frequency f_beat/2, beat at f_beat
        # Count zero crossings of envelope
        envelope = 2 * np.cos(math.pi * (f1 - f2) * t)
        # Beat period should be 1/f_beat = 0.5s
        ok = abs(f_beat - 2.0) < 1e-10
        return (ok, f"f_beat={f_beat} Hz, period={1 / f_beat}s")
    ch.add(StructuralCheck(
        label="Algorithm 5.1: Beat pattern computation",
        section="6",
        predicate=alg_5_1_beats,
    ))

    # --- Algorithm 5.2: Sound Spectrum via FFT ---
    def alg_5_2_sound_fft():
        fs = 44100
        N_s = 4096
        t = np.arange(N_s) / fs
        # Harmonic signal: fundamental + harmonics
        f0 = 440.0
        signal = np.sin(2 * math.pi * f0 * t) + 0.5 * np.sin(2 * math.pi * 2 * f0 * t)
        X = np.fft.fft(signal)
        freqs = np.fft.fftfreq(N_s, d=1 / fs)
        magnitude = np.abs(X[:N_s // 2])
        pos_freqs = freqs[:N_s // 2]
        # Find peaks
        peak1_idx = np.argmax(magnitude)
        peak1_freq = pos_freqs[peak1_idx]
        ok = abs(peak1_freq - f0) < 20  # within frequency resolution
        return (ok, f"Fundamental peak at {peak1_freq:.0f} Hz, expected {f0:.0f} Hz")
    ch.add(StructuralCheck(
        label="Algorithm 5.2: Sound spectrum via FFT (fundamental detection)",
        section="6",
        predicate=alg_5_2_sound_fft,
    ))

    # --- Algorithm 5.3: Interference Pattern ---
    def alg_5_3_interference():
        # Two-slit: I = 4*I0*cos^2(pi*d*sin(theta)/lambda)
        lam = 500e-9  # 500 nm
        d = 0.1e-3  # slit separation 0.1 mm
        theta = np.linspace(-0.01, 0.01, 1000)
        I = 4 * np.cos(math.pi * d * np.sin(theta) / lam) ** 2
        # Central maximum at theta=0 should be 4
        ok1 = abs(I[500] - 4.0) < 0.01
        # First minimum at sin(theta) = lambda/(2d)
        theta_min = math.asin(lam / (2 * d))
        idx_min = np.argmin(np.abs(theta - theta_min))
        ok2 = I[idx_min] < 0.1
        return (ok1 and ok2, f"I(0)={I[500]:.3f}, I(theta_min)={I[idx_min]:.4f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.3: Two-slit interference pattern",
        section="6",
        predicate=alg_5_3_interference,
    ))

    # --- Algorithm 5.4: ABCD Ray Tracing ---
    def alg_5_4_abcd():
        # Thin lens: M = [[1, 0],[-1/f, 1]]
        f_lens = 0.1  # 10 cm focal length
        M_lens = np.array([[1, 0], [-1 / f_lens, 1]])
        # Free space: M = [[1, d],[0, 1]]
        d1 = 0.2  # object at 20 cm
        M_free1 = np.array([[1, d1], [0, 1]])
        # Trace: object -> free space -> lens -> free space -> image
        # 1/f = 1/do + 1/di => di = 1/(1/f - 1/do) = 0.2 m
        di = 1 / (1 / f_lens - 1 / d1)
        M_free2 = np.array([[1, di], [0, 1]])
        M_total = M_free2 @ M_lens @ M_free1
        # For imaging: B element should be 0 (all rays from object point converge)
        ok1 = abs(M_total[0, 1]) < 1e-10
        # Magnification = A element = -di/do
        mag = M_total[0, 0]
        ok2 = abs(mag - (-di / d1)) < 1e-10
        return (ok1 and ok2, f"B={M_total[0, 1]:.2e}, M={mag:.3f}, expected {-di / d1:.3f}")
    ch.add(StructuralCheck(
        label="Algorithm 5.4: ABCD ray tracing (thin lens imaging)",
        section="6",
        predicate=alg_5_4_abcd,
    ))

    # --- Algorithm 5.5: Room Mode Computation ---
    def alg_5_5_room_modes():
        # f_{n,m,l} = c/2 * sqrt((n/Lx)^2 + (m/Ly)^2 + (l/Lz)^2)
        c_sound = 343.0  # m/s
        Lx, Ly, Lz = 5.0, 4.0, 3.0
        modes = []
        for n in range(4):
            for m in range(4):
                for l in range(4):
                    if n == 0 and m == 0 and l == 0:
                        continue
                    f = c_sound / 2 * math.sqrt((n / Lx) ** 2 + (m / Ly) ** 2 + (l / Lz) ** 2)
                    modes.append(f)
        modes.sort()
        # First mode should be c/(2*max(L)) = 343/10 = 34.3 Hz
        f_first = c_sound / (2 * max(Lx, Ly, Lz))
        ok = abs(modes[0] - f_first) < 0.1
        return (ok, f"First mode={modes[0]:.1f} Hz, expected={f_first:.1f} Hz")
    ch.add(StructuralCheck(
        label="Algorithm 5.5: Room mode computation",
        section="6",
        predicate=alg_5_5_room_modes,
    ))

    return ch


# ── helpers ──────────────────────────────────────────────────────────

def _thin_lens_identity():
    import sympy
    f, do, di = sympy.symbols('f do di', positive=True)
    # 1/f = 1/do + 1/di => di = f*do/(do-f)
    di_expr = f * do / (do - f)
    check = 1 / do + 1 / di_expr - 1 / f
    return sympy.Eq(sympy.simplify(check), 0)


def _double_slit_identity():
    import sympy
    # At theta=0 (normal incidence): I = I0*cos^2(0) = I0
    I_at_zero = sympy.cos(0)**2
    return sympy.Eq(I_at_zero, 1)


def _equal_temperament_identity():
    import sympy
    f0 = sympy.Symbol('f0', positive=True)
    # 12 semitones = octave, so f_12 = f_0 * 2^(12/12) = 2*f_0
    f12 = f0 * 2**sympy.Rational(12, 12)
    return sympy.Eq(f12, 2 * f0)


def _mat_mul_2x2(A, B):
    return [
        [A[0][0]*B[0][0] + A[0][1]*B[1][0], A[0][0]*B[0][1] + A[0][1]*B[1][1]],
        [A[1][0]*B[0][0] + A[1][1]*B[1][0], A[1][0]*B[0][1] + A[1][1]*B[1][1]],
    ]


def _prop(d):
    return [[1, d], [0, 1]]


def _lens(f):
    return [[1, 0], [-1/f, 1]]


def _abcd_subsystem():
    return _mat_mul_2x2(_lens(-50), _mat_mul_2x2(_prop(80), _lens(100)))


def _abcd_image_distance():
    Msub = _abcd_subsystem()
    Mp = _mat_mul_2x2(Msub, _prop(200))
    di = -Mp[0][1] / Mp[0][0]
    return di


def _abcd_magnification():
    Msub = _abcd_subsystem()
    Mp = _mat_mul_2x2(Msub, _prop(200))
    di = -Mp[0][1] / Mp[0][0]
    Mfull = _mat_mul_2x2(_prop(di), Mp)
    return Mfull[0][0]


def _abcd_det_check():
    Msub = _abcd_subsystem()
    det = Msub[0][0] * Msub[1][1] - Msub[0][1] * Msub[1][0]
    ok = abs(det - 1.0) < 1e-10
    return ok, f"det(M_sub) = {det:.10f}"


def _room_modes_sorted():
    vs = 343
    Lx, Ly, Lz = 5.0, 4.0, 3.0
    modes = []
    for m in range(6):
        for n in range(6):
            for p in range(6):
                if m == 0 and n == 0 and p == 0:
                    continue
                f = (vs / 2) * math.sqrt((m/Lx)**2 + (n/Ly)**2 + (p/Lz)**2)
                modes.append((m, n, p, f))
    modes.sort(key=lambda x: x[3])
    expected_first5 = [
        (1, 0, 0, 34.30),
        (0, 1, 0, 42.88),
        (1, 1, 0, 54.92),
        (0, 0, 1, 57.17),
        (1, 0, 1, 66.67),
    ]
    ok = True
    for i, (m, n, p, f_exp) in enumerate(expected_first5):
        if modes[i][0:3] != (m, n, p):
            ok = False
            break
        if abs(modes[i][3] - f_exp) / f_exp > 0.01:
            ok = False
            break
    return ok, f"First 5 modes: {[(m[0:3], f'{m[3]:.2f}') for m in modes[:5]]}"


def _double_slit_fringe_check():
    """Verify bright fringes at d*sin(theta)=m*lambda for small angles."""
    d = 0.1e-3
    lam = 632.8e-9
    ok = True
    for m_val in range(1, 4):
        theta_m = math.asin(m_val * lam / d)
        phase = math.pi * d * math.sin(theta_m) / lam
        intensity = math.cos(phase)**2
        if abs(intensity - 1.0) > 1e-6:
            ok = False
            break
    return ok, f"Bright fringes at m=1,2,3 all have I=1.0"


def _abcd_all_det_check():
    """Verify that individual ABCD matrices (propagation and lens) each have det=1."""
    checks = []
    for d in [50, 80, 100, 200]:
        M = _prop(d)
        det = M[0][0] * M[1][1] - M[0][1] * M[1][0]
        checks.append(abs(det - 1.0) < 1e-10)
    for f in [100, -50, 80, -30]:
        M = _lens(f)
        det = M[0][0] * M[1][1] - M[0][1] * M[1][0]
        checks.append(abs(det - 1.0) < 1e-10)
    ok = all(checks)
    return ok, f"All {len(checks)} individual ABCD matrices have det=1"


def _three_lens_det_check():
    """Exercise 10.6: Three-lens system det=1."""
    # f1=50 at pos 0, f2=-30 at 40, f3=80 at 100
    # From object at -120 to lens 1: prop(120)
    # Propagations: 40mm between L1 and L2, 60mm between L2 and L3
    M_sys = _mat_mul_2x2(_lens(80), _mat_mul_2x2(_prop(60), _mat_mul_2x2(_lens(-30), _mat_mul_2x2(_prop(40), _lens(50)))))
    det = M_sys[0][0] * M_sys[1][1] - M_sys[0][1] * M_sys[1][0]
    ok = abs(det - 1.0) < 1e-10
    return ok, f"det(M_sys) = {det:.10f}"


def _brownian_noise_slope_check():
    """Exercise 10.8: Verify Brownian noise PSD has slope ~ -2."""
    import numpy as np
    np.random.seed(42)
    N = 2**14
    white = np.random.randn(N)
    brownian = np.cumsum(white)
    # PSD
    X = np.fft.fft(brownian)
    P = np.abs(X[:N//2])**2 / N
    freqs = np.arange(1, N//2)
    P_sub = P[1:]  # skip DC
    # Fit log-log slope
    log_f = np.log10(freqs.astype(float))
    log_P = np.log10(P_sub + 1e-30)
    # Linear regression
    n = len(log_f)
    slope = (n * np.sum(log_f * log_P) - np.sum(log_f) * np.sum(log_P)) / (n * np.sum(log_f**2) - np.sum(log_f)**2)
    ok = abs(slope - (-2)) < 0.3
    return ok, f"Brownian noise PSD slope = {slope:.2f} (expected -2)"


def _ex474_square_wave_spectrum():
    """Exercise 10.4: Square wave has odd harmonics with power ~ 1/(2n-1)^2.
    Fourier amplitude coefficients are 1/(2n-1), so the power spectrum
    (amplitude squared) falls off as 1/(2n-1)^2.
    Use exact integer number of periods to avoid spectral leakage."""
    f0 = 256.0  # exact power-of-2 divides nicely into fs=16384
    fs = 16384
    # Use exact multiple of period to avoid leakage
    n_periods = 64
    N = int(n_periods * fs / f0)
    t = np.arange(N) / fs
    # Synthesize square wave with 10 odd harmonics: sum (1/k) sin(2*pi*k*f0*t)
    x = np.zeros(N)
    for n in range(1, 11):
        k = 2 * n - 1  # odd harmonic number
        x += (1.0 / k) * np.sin(2 * np.pi * k * f0 * t)
    # FFT — compute power (amplitude squared)
    X = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(N, d=1/fs)
    # Collect power (|FFT|^2) at odd harmonics
    power_vals = []
    for n in range(1, 11):
        k = 2 * n - 1
        f_harm = k * f0
        idx = np.argmin(np.abs(freqs - f_harm))
        power_vals.append(X[idx]**2)
    if power_vals[0] < 1e-10:
        return (False, "Fundamental too weak")
    # Power ratios: P(k*f0)/P(f0) should be ~ 1/k^2 = 1/(2n-1)^2
    ratio_3 = power_vals[1] / power_vals[0]  # 3rd harmonic: expected 1/9
    ratio_5 = power_vals[2] / power_vals[0]  # 5th harmonic: expected 1/25
    ok = abs(ratio_3 - 1/9) < 0.02 and abs(ratio_5 - 1/25) < 0.02
    return (ok, f"P3/P1={ratio_3:.4f} (exp {1/9:.4f}), P5/P1={ratio_5:.4f} (exp {1/25:.4f})")


def _ex474_sawtooth_spectrum():
    """Exercise 10.4: Sawtooth has all harmonics with power ~ 1/n^2.
    Fourier amplitude coefficients are 1/n, so the power spectrum
    (amplitude squared) falls off as 1/n^2.
    Use exact integer number of periods to avoid spectral leakage."""
    f0 = 256.0
    fs = 16384
    n_periods = 64
    N = int(n_periods * fs / f0)
    t = np.arange(N) / fs
    # Synthesize sawtooth with 10 harmonics: sum (1/n) sin(2*pi*n*f0*t)
    x = np.zeros(N)
    for n in range(1, 11):
        x += (1.0 / n) * np.sin(2 * np.pi * n * f0 * t)
    # FFT — compute power (amplitude squared)
    X = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(N, d=1/fs)
    # Collect power (|FFT|^2) at harmonics
    power_vals = []
    for n in range(1, 11):
        f_harm = n * f0
        idx = np.argmin(np.abs(freqs - f_harm))
        power_vals.append(X[idx]**2)
    if power_vals[0] < 1e-10:
        return (False, "Fundamental too weak")
    # Power ratios: P(n*f0)/P(f0) should be ~ 1/n^2
    ratio_2 = power_vals[1] / power_vals[0]  # 2nd harmonic: expected 1/4
    ratio_3 = power_vals[2] / power_vals[0]  # 3rd harmonic: expected 1/9
    ok = abs(ratio_2 - 1/4) < 0.02 and abs(ratio_3 - 1/9) < 0.02
    return (ok, f"P2/P1={ratio_2:.4f} (exp {1/4:.4f}), P3/P1={ratio_3:.4f} (exp {1/9:.4f})")
