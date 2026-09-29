# Security Policy

## Scope

The Creative Determinant framework is a **research tool** for studying mathematical models of coherence. Do not use it in:

- Production systems handling sensitive data
- Security-critical applications
- Real-time control systems

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| main    | :white_check_mark: |

## Reporting a Vulnerability

Report a vulnerability by email:

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

Neither is treated as a vulnerability; bound grid sizes and parameters in calling code.

### Dependencies

We depend on:
- NumPy
- SciPy
- Matplotlib

Keep them up to date.

### No Network Access

The core library (`src/cd`) makes no network requests and does no file I/O; it computes on in-memory arrays. Files are written only by the figure script and the notebook, which save their own outputs.

## Responsible Use

This framework models aspects of cognition and meaning. Consider the ethical implications of applications built on it.

See the [Ethical Covenant](https://docs.projectnavi.ai/navi-creative-determinant/explanation/ethical-covenant/) for our voluntary ethical commitments.
