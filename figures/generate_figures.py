#!/usr/bin/env python3
"""
Generate publication-quality figures for the Creative Determinant PDE framework.

All numerics come from the ``cd`` library: residual-validated Picard solvers, discrete
principal eigenvalues, and the canonical field constructors. This script only chooses
parameters and draws. Every solve records its termination reason and branch; a point whose
solve did not converge (branch ``unresolved`` or ``invalid``) is drawn as a hollow red marker
with no line through it and is counted in the per-figure ``FIGURE ...`` summary line.

Outputs are saved next to this file (``figures/``). Run from the repo root:
    uv run python figures/generate_figures.py
"""

from __future__ import annotations

import json
import time
from collections.abc import Sequence
from functools import partial
from pathlib import Path
from typing import NamedTuple

import matplotlib.pyplot as plt
import numpy as np

import cd

# Publication style
plt.rcParams.update(
    {
        "figure.figsize": (8, 5),
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "axes.grid": True,
        "axes.labelsize": 12,
        "axes.titlesize": 14,
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "font.family": "serif",
        "text.usetex": False,  # Set True if LaTeX available
    }
)

OUTPUT_DIR = Path(__file__).parent

# =============================================================================
# Parameters (single source of truth; printed at startup)
# =============================================================================

SOLVER_1D = {"max_iter": 8000, "tol": 1e-10, "damping": 0.5}
SOLVER_2D = {"max_iter": 8000, "tol": 1e-8, "damping": 0.6}
RESIDUAL = {"residual_atol": 1e-8, "residual_rtol": 1e-8}  # acceptance criterion, both solvers
CANONICAL = {"kappa": 0.9, "gamma": 0.9, "c": 10.0, "p": 2.0}  # b0 = kappa * gamma = 0.81
MU_1D = {"center": 0.5, "sigma": 0.12, "amplitude": 1.0}  # center and sigma as fractions of L
CONST_1D = {"L": 1.0, "a": 0.0, "b": 0.8, "c": 10.0, "p": 2.0}  # constant-coefficient problem
CANON_1D = {"L": 1.0, "N": 800, **CANONICAL, "mu": MU_1D}
CANON_2D = {"Lx": 1.0, "Ly": 1.0, **CANONICAL}
BETAS = np.linspace(0.0, 30.0, 61).tolist()
LAMBDAS = np.linspace(0.0, 4.0, 21).tolist()

PARAMETERS = {
    "solver_1d": SOLVER_1D,
    "solver_2d": SOLVER_2D,
    "residual_criterion": RESIDUAL,
    "fig1_eigenvalue_threshold": {"L": 1.0, "N": 600, "b": 0.8, "beta_values": BETAS},
    "fig2_threshold_comparison": {**CONST_1D, "N": 800, "beta_ratios": [0.8, 1.2]},
    "fig3_canonical_closure_sweep": {**CANON_1D, "beta_ratio": 1.2, "lambda_values": LAMBDAS},
    "fig4_2d_presence_field": {
        **CANON_2D,
        "Nx": 100,
        "Ny": 100,
        "mu": {"x0": 0.5, "y0": 0.5, "sigma": 0.20, "amplitude": 0.6},
        "lam": 0.5,
        "beta_ratio": 1.8,
    },
    "fig5_grid_refinement": {**CONST_1D, "beta_ratio": 1.2, "N_values": [100, 200, 400, 800, 1600]},
    "fig6_field_decomposition": {**CANON_1D, "lam": 1.5},
    "fig7_2d_phase_transition": {
        **CANON_2D,
        "Nx": 80,
        "Ny": 80,
        "mu": {"x0": 0.5, "y0": 0.5, "sigma": 0.18, "amplitude": 0.8},
        "lambda_values": [0.3, 1.8],
        "beta_ratio": 1.5,
    },
}

# Points that failed are drawn with this style and never joined by a line.
UNRESOLVED_STYLE = {
    "linestyle": "none",
    "marker": "o",
    "markersize": 9,
    "markerfacecolor": "none",
    "markeredgecolor": "red",
    "markeredgewidth": 1.5,
}
UNRESOLVED_LABEL = "unresolved solve (not a certified solution)"


# =============================================================================
# Bookkeeping helpers
# =============================================================================


class PointRecord(NamedTuple):
    """Outcome of one numerical result that a figure draws (``value`` = maxPhi or λ₁)."""

    label: str
    branch: str
    termination: str
    iters: int = 0
    residual_inf: float = float("nan")
    value: float = float("nan")

    @property
    def resolved(self) -> bool:
        return self.branch in ("zero", "positive", "nonnegative")


def record_solve(label: str, info: dict) -> PointRecord:
    """Build a record from a solver ``info`` dict and print its diagnostics."""
    rec = PointRecord(label, str(info["branch"]), str(info["termination"]), int(info["iters"]))
    rec = rec._replace(residual_inf=float(info["residual_inf"]), value=float(info["maxPhi"]))
    print(
        f"  {label}: branch={rec.branch} termination={rec.termination} "
        f"iters={rec.iters} residual={rec.residual_inf:.2e} maxPhi={rec.value:.4g}"
    )
    return rec


def record_eigenvalue(label: str, compute) -> PointRecord:
    """Evaluate ``compute()`` (a principal eigenvalue); a failed eigensolve is an invalid point."""
    try:
        lam1 = float(compute())
    except RuntimeError as exc:  # eigensolver did not converge
        print(f"  {label}: eigensolver failed ({exc})")
        lam1 = float("nan")
    ok = np.isfinite(lam1)
    return PointRecord(
        label, "positive" if ok else "invalid", "converged" if ok else "nonfinite", value=lam1
    )


def summarize(stem: str, records: Sequence[PointRecord], extra: Sequence[PointRecord] = ()) -> int:
    """Print the machine-readable summary line; return the number of unresolved points.

    ``extra`` holds auxiliary points (eigenvalues drawn beside a sweep) that are not counted in
    the line but still block ``ALL_FIGURES_OK`` if invalid.
    """
    n_bad = sum(not r.resolved for r in records)
    print(
        f"FIGURE {stem}: points={len(records)} converged={len(records) - n_bad} unresolved={n_bad}"
    )
    n_extra = sum(not r.resolved for r in extra)
    if n_extra:
        print(f"  plus {n_extra} invalid auxiliary eigenvalue point(s)")
    return n_bad + n_extra


def save(stem: str) -> None:
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"{stem}.png", dpi=300, bbox_inches="tight")
    plt.savefig(OUTPUT_DIR / f"{stem}.pdf", bbox_inches="tight")
    plt.close()
    print(f"  Saved: {stem}.png/pdf")


def labels(ax, xlabel: str, ylabel: str, title: str, title_size: int = 14) -> None:
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=title_size)


def plot_sweep(ax, xs, records: list[PointRecord], fmt: str, **kwargs) -> None:
    """Line through resolved points only; hollow markers, no line, at unresolved ones.

    NaN gaps break the line at every unresolved point, so no segment ever crosses one.
    An unresolved point with a nonfinite value is drawn at 0 (it carries no value).
    """
    xs = np.asarray(xs, dtype=float)
    ys = np.array([r.value for r in records], dtype=float)
    ok = np.array([r.resolved for r in records], dtype=bool)
    ax.plot(xs, np.where(ok, ys, np.nan), fmt, **kwargs)
    if not ok.all():
        bad_y = np.where(np.isfinite(ys), ys, 0.0)[~ok]
        ax.plot(xs[~ok], bad_y, label=UNRESOLVED_LABEL, **UNRESOLVED_STYLE)


def plot_curve(ax, x, Phi, rec: PointRecord, label: str, **kwargs) -> None:
    """A 1D field: solid line if resolved, sparse hollow markers (no line) otherwise."""
    if rec.resolved:
        ax.plot(x, Phi, label=label, **kwargs)
        return
    style = {**UNRESOLVED_STYLE, "markevery": max(1, len(x) // 40)}
    ax.plot(x, np.nan_to_num(Phi), label=f"{label} — UNRESOLVED ({rec.termination})", **style)


def draw_field(ax, X, Y, Phi, rec: PointRecord, title: str, levels: int):
    """Heatmap of a 2D field; an unresolved field is flagged in the title and gets no contours."""
    extent = [0, X.max(), 0, Y.max()]
    im = ax.imshow(np.nan_to_num(Phi), origin="lower", extent=extent, cmap="viridis")
    if not rec.resolved:
        ax.set_title(f"UNRESOLVED ({rec.termination}): {title}", fontsize=11, color="red")
    else:
        ax.set_title(title, fontsize=13)
        if np.all(np.isfinite(Phi)) and Phi.max() > 1e-6:  # contours only where there is structure
            ax.contour(X, Y, Phi, levels=levels, colors="white", linewidths=0.8, alpha=0.7)
    ax.set_xlabel("$x$", fontsize=12)
    ax.set_ylabel("$y$", fontsize=12)
    return im


def solve_2d_canonical(P: dict, lam: float, beta: float, label: str):
    """Build the canonical 2D fields for one contradiction cost, solve, and check the residual.

    ``a`` is passed as the full (Ny+2, Nx+2) grid array and ``c`` as a scalar; the solver takes
    the gain ``beta`` and the interior viability field so that ``q = beta * b``.
    """
    Lx, Ly, Nx, Ny, m = P["Lx"], P["Ly"], P["Nx"], P["Ny"], P["mu"]
    X, Y = np.meshgrid(np.linspace(0, Lx, Nx + 2), np.linspace(0, Ly, Ny + 2))
    mu = np.clip(cd.gaussian_bump_2d(X, Y, m["x0"], m["y0"], m["sigma"], m["amplitude"]), 0.0, 1.0)
    b = cd.viability_canonical(P["kappa"], P["gamma"], mu, lam)
    a = cd.creative_drive(P["kappa"], P["gamma"], mu)
    args = (Lx, Ly, Nx, Ny, a, beta, P["c"])
    _, _, Phi, info = cd.solve_2d_picard(
        *args, p=P["p"], b_field=b[1:-1, 1:-1], **SOLVER_2D, **RESIDUAL
    )
    rec = record_solve(label, info)
    res_inf = float("nan")
    if np.all(np.isfinite(Phi)):
        c_full = np.full(Phi.shape, P["c"])
        hx, hy = Lx / (Nx + 1), Ly / (Ny + 1)
        res_inf = float(np.max(np.abs(cd.residual_2d(Phi, a, beta * b, c_full, P["p"], hx, hy))))
    print(f"    residual_2d ||R||_inf = {res_inf:.3e}")
    return X, Y, b, Phi, rec


def mu_1d(P: dict, x: np.ndarray) -> np.ndarray:
    m = P["mu"]
    bump = cd.gaussian_bump_1d(x, m["center"] * P["L"], m["sigma"] * P["L"], m["amplitude"])
    return np.clip(bump, 0.0, 1.0)


# =============================================================================
# Figure 1: Eigenvalue threshold crossing (1D linear theory)
# =============================================================================


def fig1_eigenvalue_threshold() -> int:
    stem = "fig1_eigenvalue_threshold"
    print("Generating Figure 1: Eigenvalue threshold crossing...")
    P = PARAMETERS[stem]
    L, N, b = P["L"], P["N"], P["b"]
    beta_values = np.array(P["beta_values"])
    beta_star = cd.viability_threshold_1d(L, b)

    records = [
        record_eigenvalue(f"beta={beta:.2f}", partial(cd.principal_eigenvalue_1d, N, L, beta * b))
        for beta in beta_values
    ]
    lam_ana = (np.pi / L) ** 2 - beta_values * b

    fig, ax = plt.subplots(figsize=(8, 5))
    plot_sweep(ax, beta_values, records, "o", markersize=4, label="Numerical (FD)", alpha=0.7)
    ax.plot(
        beta_values, lam_ana, "-", linewidth=2, label=r"Analytic: $\lambda_1 = (\pi/L)^2 - \beta b$"
    )
    ax.axhline(0.0, color="k", linewidth=1)
    ax.axvline(
        beta_star, color="r", linestyle="--", linewidth=1.5, label=rf"$\beta^* = {beta_star:.2f}$"
    )
    regions = (
        (1, "blue", r"$\lambda_1 > 0$: zero branch (exact for $a \equiv 0$, Prop. 3.19)"),
        (-1, "green", r"$\lambda_1 < 0$: positive branch (Thm 3.16)"),
    )
    for sign, color, label in regions:
        ax.fill_between(
            beta_values,
            lam_ana,
            0,
            where=(sign * lam_ana > 0),
            alpha=0.15,
            color=color,
            label=label,
        )
    labels(
        ax,
        r"$\beta$ (viability gain)",
        r"$\lambda_1(-\Delta - \beta b)$",
        "Viability Threshold: When Support Exceeds Dissipation",
    )
    ax.legend(loc="upper right")
    ax.set_xlim(0, 30)
    ax.set_ylim(-15, 12)
    save(stem)
    return summarize(stem, records)


# =============================================================================
# Figure 2: Below vs above threshold comparison (1D nonlinear)
# =============================================================================


def fig2_threshold_comparison() -> int:
    stem = "fig2_threshold_comparison"
    print("Generating Figure 2: Below/above threshold comparison...")
    P = PARAMETERS[stem]
    L, N, a, b, c, p = P["L"], P["N"], P["a"], P["b"], P["c"], P["p"]
    beta_star = cd.viability_threshold_1d(L, b)

    fig, ax = plt.subplots(figsize=(8, 5))
    records = []
    cases = zip(P["beta_ratios"], ("steelblue", "forestgreen"), ("Below", "Above"), (".2g", ".3f"))
    for ratio, color, word, fmt in cases:
        beta_b = ratio * beta_star * b
        x, Phi, info = cd.solve_1d_picard(
            L, N, a=a, beta_b=beta_b, c=c, p=p, **SOLVER_1D, **RESIDUAL
        )
        rec = record_solve(f"{word.lower()} threshold beta={ratio}*beta_star", info)
        records.append(rec)
        label = rf"{word} threshold: $\beta = {ratio}\beta^*$ (max = {rec.value:{fmt}})"
        plot_curve(ax, x, Phi, rec, label, linewidth=2, color=color)

    labels(
        ax,
        r"$x$",
        r"$\Phi(x)$ (presence field)",
        "Presence Emergence: Nontrivial Equilibrium Above Viability Threshold",
    )
    ax.legend(loc="upper right")
    ax.set_xlim(0, 1)
    save(stem)
    return summarize(stem, records)


# =============================================================================
# Figure 3: Canonical closure sweep (presence collapse under contradiction)
# =============================================================================


def fig3_canonical_closure_sweep() -> int:
    stem = "fig3_canonical_closure_sweep"
    print("Generating Figure 3: Canonical closure sweep...")
    P = PARAMETERS[stem]
    L, N, c, p, kappa, gamma = P["L"], P["N"], P["c"], P["p"], P["kappa"], P["gamma"]
    x = np.linspace(0, L, N + 2)
    mu = mu_1d(P, x)
    a_x = cd.creative_drive(kappa, gamma, mu)
    beta = P["beta_ratio"] * cd.viability_threshold_1d(L, kappa * gamma)
    lam_values = np.array(P["lambda_values"])

    records, eig_records = [], []
    for lam in lam_values:
        q = beta * cd.viability_canonical(kappa, gamma, mu, lam)
        _, _, info = cd.solve_1d_picard(L, N, a=a_x, beta_b=q, c=c, p=p, **SOLVER_1D, **RESIDUAL)
        records.append(record_solve(f"lambda={lam:.2f}", info))
        eig = partial(cd.principal_eigenvalue_1d_spatial, N, L, q)
        eig_records.append(record_eigenvalue(f"lambda={lam:.2f}", eig))
    lam1 = np.nan_to_num(np.array([r.value for r in eig_records]))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Left: presence vs contradiction cost (line only through certified points)
    plot_sweep(
        ax1, lam_values, records, "ko-", markersize=6, linewidth=2, label=r"converged $\max\Phi$"
    )
    labels(
        ax1,
        r"$\lambda$ (contradiction cost)",
        r"$\max_x \Phi(x)$",
        "Presence Collapse Under Contradiction",
    )
    ax1.axhline(0, color="gray", linestyle="--", linewidth=0.8)
    if not all(r.resolved for r in records):
        ax1.legend()

    # Right: eigenvalue indicator
    plot_sweep(ax2, lam_values, eig_records, "bo-", markersize=6, linewidth=2)
    ax2.axhline(0.0, color="k", linewidth=1)
    for sign, color, label in (
        (-1, "green", r"$\lambda_1 < 0$: positive branch guaranteed (Thm 3.16)"),
        (1, "red", r"$\lambda_1 \geq 0$: no guarantee (sufficient condition only)"),
    ):
        ax2.fill_between(
            lam_values, lam1, 0, where=(sign * lam1 > 0), alpha=0.2, color=color, label=label
        )
    labels(
        ax2,
        r"$\lambda$ (contradiction cost)",
        r"$\lambda_1(-\Delta - \beta b(\cdot))$",
        "Eigenvalue Indicator Under Canonical Closure",
    )
    ax2.legend()
    save(stem)
    return summarize(stem, records, extra=eig_records)


# =============================================================================
# Figure 4: 2D presence field heatmap (hero figure)
# =============================================================================


def fig4_2d_presence_field() -> int:
    stem = "fig4_2d_presence_field"
    print("Generating Figure 4: 2D presence field...")
    P = PARAMETERS[stem]
    b0 = P["kappa"] * P["gamma"]
    beta = P["beta_ratio"] * cd.viability_threshold_2d(P["Lx"], P["Ly"], b0)
    X, Y, b, Phi, rec = solve_2d_canonical(P, P["lam"], beta, f"lambda={P['lam']}")
    print(
        f"  Parameters: b0={b0:.3f}, lam={P['lam']}, beta={beta:.2f}, b_min={b.min():.3f}, b_max={b.max():.3f}"
    )

    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    extent = [0, P["Lx"], 0, P["Ly"]]
    im0 = axs[0].imshow(b, origin="lower", extent=extent, cmap="RdYlGn", vmin=0.0, vmax=1.0)
    labels(axs[0], "$x$", "$y$", r"Viability Field $b(x,y) = \kappa\gamma - \lambda\mu(x,y)$", 13)
    plt.colorbar(im0, ax=axs[0], fraction=0.046, pad=0.04).set_label("Viability", fontsize=10)

    im1 = draw_field(axs[1], X, Y, Phi, rec, r"Presence Field $\Phi(x,y)$ — V1′ Equilibrium", 10)
    plt.colorbar(im1, ax=axs[1], fraction=0.046, pad=0.04).set_label(
        "Presence intensity", fontsize=10
    )
    save(stem)
    return summarize(stem, [rec])


# =============================================================================
# Figure 5: Grid refinement convergence (numerical rigor)
# =============================================================================


def fig5_grid_refinement() -> int:
    stem = "fig5_grid_refinement"
    print("Generating Figure 5: Grid refinement convergence...")
    P = PARAMETERS[stem]
    L, a, b, c, p = P["L"], P["a"], P["b"], P["c"], P["p"]
    beta_b = P["beta_ratio"] * cd.viability_threshold_1d(L, b) * b
    Ns = np.array(P["N_values"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    records, residuals = [], []
    for N in Ns:
        x, Phi, info = cd.solve_1d_picard(
            L, int(N), a=a, beta_b=beta_b, c=c, p=p, **SOLVER_1D, **RESIDUAL
        )
        rec = record_solve(f"N={N}", info)
        records.append(rec)
        res_inf = float("nan")
        if np.all(np.isfinite(Phi)):
            res_inf = float(np.max(np.abs(cd.residual_1d(x, Phi, a, beta_b, c, p))))
        residuals.append(res_inf)
        plot_curve(ax1, x, Phi, rec, rf"$N={N}$", linewidth=1.5)

    labels(ax1, r"$x$", r"$\Phi(x)$", "Solution Convergence Under Grid Refinement")
    ax1.legend()

    # Right: discretization error of max Phi against the finest grid, log-log, with an O(h^2)
    # reference. The discrete residual is drawn as a separate series: it sits at the solver
    # tolerance on every grid and does not decay with h, so it is not a convergence measure.
    ref, coarse, N_coarse = records[-1], records[:-1], Ns[:-1]
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    if ref.resolved:
        errs = [r._replace(value=abs(r.value - ref.value)) for r in coarse]
        err_label = rf"$|\max\Phi_N - \max\Phi_{{{Ns[-1]}}}|$ (discretization error)"
        plot_sweep(ax2, N_coarse, errs, "ko-", markersize=8, linewidth=2, label=err_label)
        anchors = [(N, e.value) for N, e in zip(N_coarse, errs) if e.resolved and e.value > 0]
        if anchors:
            N0, e0 = anchors[0]
            reference = e0 * ((N0 + 1) / (N_coarse + 1)) ** 2
            ax2.loglog(N_coarse, reference, "r--", linewidth=1.5, label=r"$O(h^2)$ reference")
    else:
        msg = f"reference grid N={Ns[-1]} unresolved:\nno discretization error available"
        ax2.text(0.5, 0.6, msg, ha="center", va="center", transform=ax2.transAxes, color="red")
    res_label = r"discrete residual $\|R_h\|_\infty$ (solver tolerance; does not decay)"
    ax2.loglog(Ns, residuals, "s:", color="gray", markersize=7, linewidth=1.2, label=res_label)
    labels(ax2, "Grid points $N$", "Magnitude", "Discretization error of max Phi (second order)")
    ax2.legend(loc="center left", bbox_to_anchor=(0.0, 0.35), fontsize=9)  # empty band
    save(stem)
    return summarize(stem, records)


# =============================================================================
# Figure 6: Contradiction field visualization (1D)
# =============================================================================


def fig6_field_decomposition() -> int:
    stem = "fig6_field_decomposition"
    print("Generating Figure 6: Field decomposition visualization...")
    P = PARAMETERS[stem]
    kappa, gamma = P["kappa"], P["gamma"]
    x = np.linspace(0, P["L"], P["N"] + 2)
    mu = mu_1d(P, x)
    b_x = cd.viability_canonical(kappa, gamma, mu, P["lam"])
    a_x = cd.creative_drive(kappa, gamma, mu)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(
        x,
        np.full_like(x, kappa * gamma),
        "k--",
        linewidth=1.5,
        label=r"$\kappa\gamma$ (care × coherence)",
    )
    ax.plot(x, mu, "r-", linewidth=2, label=r"$\mu(x)$ (contradiction field)")
    ax.plot(x, b_x, "g-", linewidth=2, label=r"$b(x) = \kappa\gamma - \lambda\mu(x)$ (viability)")
    ax.plot(x, a_x, "b-", linewidth=2, label=r"$a(x) = \kappa\gamma\mu(x)$ (creative drive)")
    ax.axhline(0, color="gray", linestyle=":", linewidth=0.8)
    ax.fill_between(
        x, 0, b_x, where=(b_x < 0), alpha=0.2, color="red", label="Negative viability region"
    )
    labels(ax, r"$x$", "Field intensity", "Canonical Closure: Field Decomposition")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.6, 1.1)
    save(stem)
    return summarize(stem, [])  # pure field plot: no solves


# =============================================================================
# Figure 7: 2D Phase Transition (viable vs non-viable comparison)
# =============================================================================


def fig7_2d_phase_transition() -> int:
    stem = "fig7_2d_phase_transition"
    print("Generating Figure 7: 2D phase transition comparison...")
    P = PARAMETERS[stem]
    beta = P["beta_ratio"] * cd.viability_threshold_2d(P["Lx"], P["Ly"], P["kappa"] * P["gamma"])
    lam_low, lam_high = P["lambda_values"]
    X, Y, _, Phi_low, rec_low = solve_2d_canonical(P, lam_low, beta, f"low lambda={lam_low}")
    _, _, _, Phi_high, rec_high = solve_2d_canonical(P, lam_high, beta, f"high lambda={lam_high}")

    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    title_low = rf"Viable: $\lambda = {lam_low}$ (max $\Phi$ = {rec_low.value:.3f})"
    title_high = rf"Collapsed: $\lambda = {lam_high}$ (max $\Phi$ = {rec_high.value:.2e})"
    im0 = draw_field(axs[0], X, Y, Phi_low, rec_low, title_low, 8)
    plt.colorbar(im0, ax=axs[0], fraction=0.046, pad=0.04)
    im1 = draw_field(axs[1], X, Y, Phi_high, rec_high, title_high, 8)
    plt.colorbar(im1, ax=axs[1], fraction=0.046, pad=0.04)
    plt.suptitle(
        "2D Phase Transition: Presence Collapse Under Excess Contradiction", fontsize=14, y=1.02
    )
    save(stem)
    return summarize(stem, [rec_low, rec_high])


# =============================================================================
# Main
# =============================================================================

FIGURES = (
    fig1_eigenvalue_threshold,
    fig2_threshold_comparison,
    fig3_canonical_closure_sweep,
    fig4_2d_presence_field,
    fig5_grid_refinement,
    fig6_field_decomposition,
    fig7_2d_phase_transition,
)


def main() -> None:
    print("=" * 60)
    print("Creative Determinant PDE Framework — Figure Generation")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"cd version: {cd.__version__}")
    print("PARAMETERS = " + json.dumps(PARAMETERS, indent=2))
    print()

    t0 = time.perf_counter()
    unresolved = sum(make() for make in FIGURES)
    elapsed = time.perf_counter() - t0

    print()
    print("=" * 60)
    print(f"All figures generated in {elapsed:.1f} s")
    print("ALL_FIGURES_OK" if unresolved == 0 else "FIGURES_WITH_UNRESOLVED_POINTS")
    print("=" * 60)


if __name__ == "__main__":
    main()
