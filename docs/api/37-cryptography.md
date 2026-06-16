<!-- Copyright (c) 2025-2026 Bob Jansen <bobjansen@pm.me> -->
<!-- SPDX-License-Identifier: CC-BY-NC-4.0 -->
<!-- See LICENSE for full terms. Commercial licensing available. -->

# Cryptography & Number Theory — API Reference

This is the API reference for the TypeScript implementation of Cryptography & Number Theory. For the mathematical theory, see the corresponding chapter in the main text.

### Module Structure

- `src/crypto/modular.ts` — modular exponentiation, inverse, extended GCD
- `src/crypto/rsa.ts` — RSA key generation, encryption, decryption (CRT-optimised)
- `src/crypto/dh.ts` — Diffie-Hellman key exchange
- `src/crypto/ec.ts` — elliptic curve point addition and scalar multiplication
- `src/crypto/hash.ts` — SHA-256 implementation
- `src/crypto/zkp.ts` — Schnorr zero-knowledge proof

### Data Representation

Cryptographic integers are represented as `bigint` values in TypeScript. Keys, messages and ciphertexts are typically serialised as hexadecimal strings or `Uint8Array` byte buffers. Elliptic curve points are represented as pairs `{ x: bigint, y: bigint }` in affine coordinates or triples `{ X: bigint, Y: bigint, Z: bigint }` in projective coordinates.

### RSA Implementation

```typescript
interface RSAPublicKey {
    n: bigint;
    e: bigint;
}

interface RSAPrivateKey {
    n: bigint;
    d: bigint;
    p: bigint;
    q: bigint;
    dp: bigint;  // d mod (p-1), for CRT optimisation
    dq: bigint;  // d mod (q-1)
    qInv: bigint; // q^{-1} mod p
}

function generateRSAKeys(bits: number): { pub: RSAPublicKey; priv: RSAPrivateKey } {
    const p = generatePrime(bits / 2);
    const q = generatePrime(bits / 2);
    const n = p * q;
    const phi = (p - 1n) * (q - 1n);
    const e = 65537n; // Standard public exponent
    const d = modInverse(e, phi);
    return {
        pub: { n, e },
        priv: { n, d, p, q, dp: d % (p - 1n), dq: d % (q - 1n), qInv: modInverse(q, p) }
    };
}

function rsaEncrypt(m: bigint, pub: RSAPublicKey): bigint {
    return modPow(m, pub.e, pub.n);
}

function rsaDecrypt(c: bigint, priv: RSAPrivateKey): bigint {
    // CRT-optimized decryption
    const m1 = modPow(c, priv.dp, priv.p);
    const m2 = modPow(c, priv.dq, priv.q);
    const h = (priv.qInv * ((m1 - m2 + priv.p) % priv.p)) % priv.p;
    return m2 + h * priv.q;
}
```

### Elliptic Curve Implementation

```typescript
interface ECPoint {
    x: bigint;
    y: bigint;
}

interface ECCurve {
    a: bigint;
    b: bigint;
    p: bigint;    // Field prime
    n: bigint;    // Group order
    G: ECPoint;   // Generator point
}

function ecAdd(P: ECPoint | null, Q: ECPoint | null, curve: ECCurve): ECPoint | null {
    if (P === null) return Q;
    if (Q === null) return P;
    if (P.x === Q.x && P.y === (curve.p - Q.y) % curve.p) return null; // P + (-P) = O

    let lambda: bigint;
    if (P.x === Q.x && P.y === Q.y) {
        // Point doubling
        lambda = (3n * P.x * P.x + curve.a) * modInverse(2n * P.y, curve.p) % curve.p;
    } else {
        // Point addition
        lambda = (Q.y - P.y) * modInverse((Q.x - P.x + curve.p) % curve.p, curve.p) % curve.p;
    }
    lambda = (lambda + curve.p) % curve.p;

    const x3 = (lambda * lambda - P.x - Q.x) % curve.p;
    const y3 = (lambda * (P.x - x3) - P.y) % curve.p;
    return { x: (x3 + curve.p) % curve.p, y: (y3 + curve.p) % curve.p };
}

function ecMul(k: bigint, P: ECPoint, curve: ECCurve): ECPoint | null {
    // Double-and-add scalar multiplication
    let result: ECPoint | null = null;
    let addend: ECPoint | null = P;
    while (k > 0n) {
        if (k & 1n) result = ecAdd(result, addend, curve);
        addend = ecAdd(addend, addend, curve);
        k >>= 1n;
    }
    return result;
}
```

### API Preview

```typescript
import { modPow, modInverse, extGcd } from 'evenwicht/crypto/modular';
import { generateRSAKeys, rsaEncrypt, rsaDecrypt } from 'evenwicht/crypto/rsa';
import { diffieHellman } from 'evenwicht/crypto/dh';
import { ecAdd, ecMul, ecPoint } from 'evenwicht/crypto/ec';
import { sha256 } from 'evenwicht/crypto/hash';
import { schnorrProve, schnorrVerify } from 'evenwicht/crypto/zkp';
```

### Error Handling

- `modInverse` throws if the modular inverse does not exist (inputs are not coprime).
- `generateRSAKeys` requires `bits >= 512`; throws for smaller values.
- `rsaEncrypt` throws if the message $m$ exceeds $n$.
- `ecAdd` returns `null` for the point at infinity (identity element).
- `ecMul` with `k = 0` returns `null` (point at infinity).

### Dependencies

- No external module dependencies; all cryptographic primitives use `bigint` arithmetic
- The `modPow` function uses binary exponentiation for efficiency

### Usage Examples

```typescript
import { modPow, modInverse, generateRSAKeys, rsaEncrypt, rsaDecrypt } from 'evenwicht/crypto';
import { ecAdd, ecMul } from 'evenwicht/crypto/ec';

// Modular arithmetic
modPow(2n, 10n, 1000n);     // 1024n % 1000n = 24n
modInverse(3n, 7n);          // 5n (since 3*5 = 15 ≡ 1 mod 7)

// RSA encryption/decryption
const { pub, priv } = generateRSAKeys(2048);
const ciphertext = rsaEncrypt(42n, pub);
const plaintext = rsaDecrypt(ciphertext, priv);  // 42n

// Elliptic curve point doubling
const P = { x: 5n, y: 1n };
const curve = { a: 2n, b: 3n, p: 97n, n: 100n, G: P };
const P2 = ecAdd(P, P, curve);  // 2P
```

### Connections

This chapter draws on Chapter 13 (probability for birthday attacks, security definitions and randomised protocols), Chapter 28 (entropy for perfect secrecy and randomness requirements) and Chapter 9 (matrix structure in lattice problems). It connects forward to network security applications, blockchain consensus mechanisms, secure multi-party computation and post-quantum cryptography.

- **Probability Theory** (Chapter 13): Security definitions are inherently probabilistic. A scheme is "secure" if the advantage of any efficient adversary (the probability of distinguishing ciphertext from random minus $1/2$) is negligible. The birthday bound (Theorem 37.25) is a direct application of the collision probability formula from combinatorial probability. The soundness of zero-knowledge proofs relies on bounding the probability that a cheating prover succeeds.

- **Information Theory** (Chapter 28): Shannon's definition of perfect secrecy ($I(M; C) = 0$) is a direct application of mutual information. The impossibility theorem (Theorem 37.33) connects key length to message entropy. Min-entropy (Definition 37.27) refines Shannon entropy for worst-case security analysis. The entropy of a key source determines the effective security level regardless of nominal key size.

- **Matrices** (Chapter 9): Lattice-based cryptography (a leading post-quantum candidate) relies on the hardness of problems involving integer matrices, such as the Shortest Vector Problem (SVP) and Learning With Errors (LWE). Linear feedback shift registers, used in stream ciphers, are characterised by companion matrices whose eigenvalues determine the period of the output sequence.



### What Is Implemented vs. Documented Only

- [x] Modular exponentiation, modular inverse and extended GCD
- [x] RSA key generation, encryption and CRT-optimised decryption
- [x] Diffie–Hellman key exchange
- [x] Elliptic curve point addition and scalar multiplication (affine coordinates)
- [x] SHA-256 hash function
- [x] Schnorr zero-knowledge proof (prove and verify)
- [ ] AES or other symmetric-key encryption (out of scope; the chapter focuses on public-key and number-theoretic primitives)
- [ ] Elliptic curve point multiplication in projective coordinates for side-channel resistance (documented; deferred)
- [ ] Probabilistic primality testing (Miller–Rabin) as a standalone export (used internally by RSA key generation; not separately exposed)
- [ ] Post-quantum cryptographic schemes such as lattice-based encryption (out of scope)
- [ ] Digital signature schemes beyond Schnorr (e.g., ECDSA) (deferred)

---


### Implementation Context

**Bigint arithmetic throughout.** All cryptographic operations use JavaScript's native `bigint` type. Modular exponentiation uses the square-and-multiply algorithm ($O(\log e)$ modular multiplications), and modular inverse uses the extended Euclidean algorithm. No external big-number library is required, though Montgomery multiplication would improve performance for production-grade key sizes.

**CRT-optimised RSA decryption.** The private key stores precomputed CRT components ($d_p$, $d_q$, $q^{-1} \bmod p$), reducing decryption from one exponentiation modulo $n$ to two half-size exponentiations. This provides roughly a 4x speedup for 2048-bit keys.

**Affine coordinates for elliptic curves.** Point addition and scalar multiplication operate in affine coordinates, requiring one modular inversion per addition. Projective coordinates (documented but deferred) would replace inversions with multiplications, yielding a 3-4x speedup for scalar multiplication. The current affine implementation is suitable for educational use but not for performance-critical applications.

**Timing side-channel exposure.** The `modPow` implementation branches on each bit of the exponent, making execution time depend on the secret key. This is acceptable for a mathematical library but unsuitable for production cryptography, which requires constant-time implementations.

**Primality testing.** RSA key generation uses the Miller–Rabin test with 20 rounds internally, giving a false-positive probability below $4^{-20} \approx 10^{-12}$. The test is not exported as a standalone function.

**Testing strategy.** RSA round-trip tests verify that $\text{decrypt}(\text{encrypt}(m)) = m$ for small and large messages. EC tests verify the group law ($P + O = P$, $P + (-P) = O$, associativity) on known curves. Modular arithmetic tests use Fermat's little theorem ($a^{p-1} \equiv 1$) and known GCD values as reference checks.
