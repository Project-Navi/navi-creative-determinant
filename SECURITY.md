# Security Policy

## Scope

The Creative Determinant framework is a **research tool** for studying mathematical models of coherence. It is not designed for:

- Production systems handling sensitive data
- Security-critical applications
- Real-time control systems

That said, we take security seriously because this code may be integrated into larger systems.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

**Email:** nelson@projectnavi.ai

**Subject line:** `[SECURITY] Brief description`

**Include:**
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

### What to expect

- **Acknowledgment:** Within 48 hours
- **Initial assessment:** Within 7 days
- **Resolution timeline:** Depends on severity; we'll communicate throughout

### What we commit to

- We will not take legal action against good-faith security researchers
- We will credit you (unless you prefer anonymity) when the fix is released
- We will be transparent about the issue once a fix is available

## Security Considerations

### Numerical Code

The framework performs numerical linear algebra. Potential concerns:

- **Denial of service:** Very large grid sizes could exhaust memory
- **Numerical instability:** Extreme parameter values might cause NaN/Inf

These are not security vulnerabilities per se, but users should validate inputs.

### Dependencies

We depend on:
- NumPy
- SciPy
- Matplotlib

These are widely-used, well-maintained libraries. We recommend keeping them updated.

### No Network Access

The core library makes no network requests. The only I/O is file-based (saving figures, loading data).

## Responsible Use

This framework models aspects of cognition and meaning. While it's purely mathematical, we ask users to consider the ethical implications of any applications they build on top of it.

See the [Ethical Covenant](docs/explanation/ethical-covenant.md) for our voluntary ethical commitments.
