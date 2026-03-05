#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Nelson Spence
"""
Generate publication-quality figures for the Creative Determinant PDE framework.

Outputs saved to navi-creative-determinant/figures/
Run from repo root: python figures/generate_figures.py
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from scipy.sparse import diags, kron, eye
from scipy.sparse.linalg import eigsh, spsolve
from scipy.integrate import solve_bvp

# Publication style
plt.rcParams.update({
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
})

OUTPUT_DIR = Path(__file__).parent


# =============================================================================
# Utilities
# =============================================================================

def laplacian_1d_dirichlet(N, L):
    """Sparse matrix for -d²/dx² on (0,L) with Dirichlet BC, N interior points."""
    h = L / (N + 1)
    main = 2.0 * np.ones(N) / h**2
    off = -1.0 * np.ones(N - 1) / h**2
    A = diags([off, main, off], offsets=[-1, 0, 1], format="csr")
    return A, h


def principal_eigenvalue_Lb_1d_const(N, L, beta_b):
    """Principal eigenvalue of (-d²/dx²) - (beta_b) I on (0,L), Dirichlet."""
    A, _ = laplacian_1d_dirichlet(N, L)
    M = A - beta_b * diags([np.ones(N)], [0], format="csr")
    lam, _ = eigsh(M, k=1, which="SA")
    return float(lam[0])


def principal_eigenvalue_Lb_1d_spatial(N, L, beta_b_full):
    """Principal eigenvalue of (-d²/dx²) - diag(beta*b(x)) on interior nodes."""
    A, _ = laplacian_1d_dirichlet(N, L)
    bb_int = beta_b_full[1:-1]
    M = A - diags([bb_int], [0], format="csr")
    lam, _ = eigsh(M, k=1, which="SA")
    return float(lam[0])


def gaussian_bump_1d(x, center, sigma, amplitude=1.0):
    return amplitude * np.exp(-0.5 * ((x - center) / sigma) ** 2)


def gaussian_bump_2d(X, Y, cx, cy, sigma, amplitude=1.0):
    return amplitude * np.exp(-((X - cx) ** 2 + (Y - cy) ** 2) / (2 * sigma**2))


def solve_V1prime_1d_picard(L, N, a, beta_b, c, p=2.0, max_iter=8000, tol=1e-10, damping=0.5):
    """Solve -Phi'' = a|Phi'| + (beta_b)Phi - c Phi^p with Dirichlet BC."""
    A, h = laplacian_1d_dirichlet(N, L)
    x = np.linspace(0, L, N + 2)
    Phi = 0.1 * np.sin(np.pi * x / L)
    Phi_int = Phi[1:-1].copy()

    def grad_abs(Phi_full):
        d = (Phi_full[2:] - Phi_full[:-2]) / (2 * h)
        return np.abs(d)

    for it in range(max_iter):
        Phi_full = np.zeros(N + 2)
        Phi_full[1:-1] = Phi_int
        gabs = grad_abs(Phi_full)
        rhs = a * gabs + beta_b * Phi_int - c * np.maximum(Phi_int, 0.0) ** p
        Phi_new = spsolve(A, rhs)
        Phi_next = (1 - damping) * Phi_int + damping * Phi_new
        Phi_next = np.maximum(Phi_next, 0.0)
        err = np.linalg.norm(Phi_next - Phi_int, ord=np.inf)
        Phi_int = Phi_next
        if err < tol:
            break

    Phi = np.zeros(N + 2)
    Phi[1:-1] = Phi_int
    return x, Phi, {"iters": it + 1, "inf_err": float(err), "maxPhi": float(Phi.max())}


def solve_V1prime_1d_picard_spatial(L, N, a_x, beta_b_x, c_x, p=2.0, max_iter=10000, tol=1e-10, damping=0.5):
    """Solve with spatially-varying coefficients."""
    A, h = laplacian_1d_dirichlet(N, L)
    x = np.linspace(0, L, N + 2)
    a_int = a_x[1:-1]
    bb_int = beta_b_x[1:-1]
    c_int = c_x[1:-1]

    Phi = 0.1 * np.sin(np.pi * x / L)
    Phi_int = Phi[1:-1].copy()

    def grad_abs(Phi_full):
        d = (Phi_full[2:] - Phi_full[:-2]) / (2 * h)
        return np.abs(d)

    for it in range(max_iter):
        Phi_full = np.zeros(N + 2)
        Phi_full[1:-1] = Phi_int
        gabs = grad_abs(Phi_full)
        rhs = a_int * gabs + bb_int * Phi_int - c_int * np.maximum(Phi_int, 0.0) ** p
        Phi_new = spsolve(A, rhs)
        Phi_next = (1 - damping) * Phi_int + damping * Phi_new
        Phi_next = np.maximum(Phi_next, 0.0)
        err = np.linalg.norm(Phi_next - Phi_int, ord=np.inf)
        Phi_int = Phi_next
        if err < tol:
            break

    Phi = np.zeros(N + 2)
    Phi[1:-1] = Phi_int
    return x, Phi, {"iters": it + 1, "inf_err": float(err), "maxPhi": float(Phi.max())}


def laplacian_2d_dirichlet(Nx, Ny, Lx, Ly):
    """Sparse matrix for -Δ on (0,Lx)x(0,Ly) with Dirichlet BC."""
    hx = Lx / (Nx + 1)
    hy = Ly / (Ny + 1)
    Ax = diags([-np.ones(Nx - 1), 2 * np.ones(Nx), -np.ones(Nx - 1)], [-1, 0, 1], format="csr") / hx**2
    Ay = diags([-np.ones(Ny - 1), 2 * np.ones(Ny), -np.ones(Ny - 1)], [-1, 0, 1], format="csr") / hy**2
    Ix = eye(Nx, format="csr")
    Iy = eye(Ny, format="csr")
    A = kron(Iy, Ax) + kron(Ay, Ix)
    return A, hx, hy


def gradmag_2d(Phi, hx, hy):
    dPhidx = (Phi[1:-1, 2:] - Phi[1:-1, :-2]) / (2 * hx)
    dPhidy = (Phi[2:, 1:-1] - Phi[:-2, 1:-1]) / (2 * hy)
    return np.sqrt(dPhidx**2 + dPhidy**2)


def solve_V1prime_2d_picard(Lx, Ly, Nx, Ny, a_full, beta_b_full, c_full, p=2.0, damping=0.6, tol=1e-8, max_iter=4000):
    """Solve 2D V1' equation."""
    A, hx, hy = laplacian_2d_dirichlet(Nx, Ny, Lx, Ly)
    x = np.linspace(0, Lx, Nx + 2)
    y = np.linspace(0, Ly, Ny + 2)
    X, Y = np.meshgrid(x, y)
    Phi = 0.1 * np.sin(np.pi * X / Lx) * np.sin(np.pi * Y / Ly)

    for it in range(max_iter):
        gmag = gradmag_2d(Phi, hx, hy)
        Phi_int = Phi[1:-1, 1:-1]
        a_int = a_full[1:-1, 1:-1]
        bb_int = beta_b_full[1:-1, 1:-1]
        c_int = c_full[1:-1, 1:-1]
        rhs_int = a_int * gmag + bb_int * Phi_int - c_int * np.maximum(Phi_int, 0.0) ** p
        rhs = rhs_int.reshape(-1)
        Phi_new_int = spsolve(A, rhs).reshape(Ny, Nx)
        Phi_next = Phi.copy()
        Phi_next[1:-1, 1:-1] = (1 - damping) * Phi_int + damping * Phi_new_int
        Phi_next[1:-1, 1:-1] = np.maximum(Phi_next[1:-1, 1:-1], 0.0)
        err = np.linalg.norm(Phi_next - Phi, ord=np.inf)
        Phi = Phi_next
        if err < tol:
            break

    return X, Y, Phi, {"iters": it + 1, "inf_err": float(err), "maxPhi": float(Phi.max())}, (hx, hy)


# =============================================================================
# Figure 1: Eigenvalue threshold crossing (1D linear theory)
# =============================================================================

def fig1_eigenvalue_threshold():
    print("Generating Figure 1: Eigenvalue threshold crossing...")
    L = 1.0
    N = 600
    b_const = 0.8

    beta_values = np.linspace(0.0, 30.0, 61)
    lam_num = np.array([principal_eigenvalue_Lb_1d_const(N, L, beta * b_const) for beta in beta_values])
    lam_ana = (np.pi / L) ** 2 - beta_values * b_const
    beta_star = (np.pi / L) ** 2 / b_const

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(beta_values, lam_num, "o", markersize=4, label="Numerical (FD)", alpha=0.7)
    ax.plot(beta_values, lam_ana, "-", linewidth=2, label=r"Analytic: $\lambda_1 = (\pi/L)^2 - \beta b$")
    ax.axhline(0.0, color="k", linewidth=1)
    ax.axvline(beta_star, color="r", linestyle="--", linewidth=1.5, label=rf"$\beta^* = {beta_star:.2f}$")
    
    # Shade regions
    ax.fill_between(beta_values, lam_ana, 0, where=(lam_ana > 0), alpha=0.15, color="blue", label="Subcritical (no emergence)")
    ax.fill_between(beta_values, lam_ana, 0, where=(lam_ana < 0), alpha=0.15, color="green", label="Supercritical (emergence)")

    ax.set_xlabel(r"$\beta$ (viability gain)", fontsize=12)
    ax.set_ylabel(r"$\lambda_1(-\Delta - \beta b)$", fontsize=12)
    ax.set_title("Viability Threshold: When Support Exceeds Dissipation", fontsize=14)
    ax.legend(loc="upper right")
    ax.set_xlim(0, 30)
    ax.set_ylim(-15, 12)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "fig1_eigenvalue_threshold.png", dpi=300, bbox_inches="tight")
    plt.savefig(OUTPUT_DIR / "fig1_eigenvalue_threshold.pdf", bbox_inches="tight")
    plt.close()
    print(f"  Saved: fig1_eigenvalue_threshold.png/pdf")


# =============================================================================
# Figure 2: Below vs above threshold comparison (1D nonlinear)
# =============================================================================

def fig2_threshold_comparison():
    print("Generating Figure 2: Below/above threshold comparison...")
    L = 1.0
    p = 2.0
    c = 10.0
    a = 0.0
    b = 0.8

    beta_star = (np.pi / L) ** 2 / b
    beta_below = 0.8 * beta_star
    beta_above = 1.2 * beta_star

    x1, Phi1, _ = solve_V1prime_1d_picard(L, 800, a=a, beta_b=beta_below * b, c=c, p=p)
    x2, Phi2, _ = solve_V1prime_1d_picard(L, 800, a=a, beta_b=beta_above * b, c=c, p=p)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x1, Phi1, linewidth=2, color="steelblue", label=rf"Below threshold: $\beta = 0.8\beta^*$ (max = {Phi1.max():.2g})")
    ax.plot(x2, Phi2, linewidth=2, color="forestgreen", label=rf"Above threshold: $\beta = 1.2\beta^*$ (max = {Phi2.max():.3f})")
    
    ax.set_xlabel(r"$x$", fontsize=12)
    ax.set_ylabel(r"$\Phi(x)$ (presence field)", fontsize=12)
    ax.set_title("Presence Emergence: Nontrivial Equilibrium Above Viability Threshold", fontsize=14)
    ax.legend(loc="upper right")
    ax.set_xlim(0, 1)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "fig2_threshold_comparison.png", dpi=300, bbox_inches="tight")
    plt.savefig(OUTPUT_DIR / "fig2_threshold_comparison.pdf", bbox_inches="tight")
    plt.close()
    print(f"  Saved: fig2_threshold_comparison.png/pdf")


# =============================================================================
# Figure 3: Canonical closure sweep (presence collapse under contradiction)
# =============================================================================

def fig3_canonical_closure_sweep():
    print("Generating Figure 3: Canonical closure sweep...")
    L = 1.0
    N = 800
    x = np.linspace(0, L, N + 2)

    kappa = 0.9
    gamma = 0.9
    b0 = kappa * gamma

    mu = gaussian_bump_1d(x, center=0.5 * L, sigma=0.12 * L, amplitude=1.0)
    mu = np.clip(mu, 0.0, 1.0)
    a_x = b0 * mu

    p = 2.0
    c0 = 10.0
    c_x = c0 * np.ones_like(x)

    beta_star = (np.pi / L) ** 2 / b0
    beta = 1.2 * beta_star

    lam_values = np.linspace(0.0, 4.0, 21)
    maxPhi = []
    lam1_vals = []

    for lam in lam_values:
        b_x = b0 - lam * mu
        beta_b_x = beta * b_x
        x_sol, Phi_sol, info = solve_V1prime_1d_picard_spatial(L, N, a_x=a_x, beta_b_x=beta_b_x, c_x=c_x, p=p, damping=0.5)
        maxPhi.append(Phi_sol.max())
        lam1_vals.append(principal_eigenvalue_Lb_1d_spatial(N, L, beta_b_x))

    maxPhi = np.array(maxPhi)
    lam1_vals = np.array(lam1_vals)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Left: Presence vs contradiction cost
    ax1.plot(lam_values, maxPhi, "ko-", markersize=6, linewidth=2)
    ax1.set_xlabel(r"$\lambda$ (contradiction cost)", fontsize=12)
    ax1.set_ylabel(r"$\max_x \Phi(x)$", fontsize=12)
    ax1.set_title("Presence Collapse Under Contradiction", fontsize=14)
    ax1.axhline(0, color="gray", linestyle="--", linewidth=0.8)

    # Right: Eigenvalue indicator
    ax2.plot(lam_values, lam1_vals, "bo-", markersize=6, linewidth=2)
    ax2.axhline(0.0, color="k", linewidth=1)
    ax2.fill_between(lam_values, lam1_vals, 0, where=(np.array(lam1_vals) < 0), alpha=0.2, color="green", label="Viable")
    ax2.fill_between(lam_values, lam1_vals, 0, where=(np.array(lam1_vals) > 0), alpha=0.2, color="red", label="Non-viable")
    ax2.set_xlabel(r"$\lambda$ (contradiction cost)", fontsize=12)
    ax2.set_ylabel(r"$\lambda_1(-\Delta - \beta b(\cdot))$", fontsize=12)
    ax2.set_title("Eigenvalue Indicator Under Canonical Closure", fontsize=14)
    ax2.legend()

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "fig3_canonical_closure_sweep.png", dpi=300, bbox_inches="tight")
    plt.savefig(OUTPUT_DIR / "fig3_canonical_closure_sweep.pdf", bbox_inches="tight")
    plt.close()
    print(f"  Saved: fig3_canonical_closure_sweep.png/pdf")


# =============================================================================
# Figure 4: 2D presence field heatmap (hero figure)
# =============================================================================

def fig4_2d_presence_field():
    print("Generating Figure 4: 2D presence field (this may take a moment)...")
    Lx, Ly = 1.0, 1.0
    Nx, Ny = 100, 100  # Higher resolution for publication
    p = 2.0
    c0 = 10.0

    kappa = 0.9
    gamma = 0.9
    b0 = kappa * gamma  # = 0.81

    x = np.linspace(0, Lx, Nx + 2)
    y = np.linspace(0, Ly, Ny + 2)
    X, Y = np.meshgrid(x, y)

    # Use a gentler contradiction profile that doesn't kill viability
    sigma = 0.20
    mu = gaussian_bump_2d(X, Y, 0.5, 0.5, sigma, amplitude=0.6)
    mu = np.clip(mu, 0.0, 1.0)

    # Smaller contradiction cost to ensure positive viability in most of domain
    lam = 0.5
    b = b0 - lam * mu  # b ranges from ~0.81 down to ~0.51 (still positive everywhere)
    a = b0 * mu

    # Increase beta to ensure we're well above threshold
    beta_star_2d = ((np.pi / Lx) ** 2 + (np.pi / Ly) ** 2) / b0
    beta = 1.8 * beta_star_2d  # More aggressive to ensure emergence
    beta_b = beta * b

    c = c0 * np.ones_like(X)

    print(f"  Parameters: b0={b0:.3f}, lam={lam}, beta={beta:.2f}, b_min={b.min():.3f}, b_max={b.max():.3f}")

    Xg, Yg, Phi, info, _ = solve_V1prime_2d_picard(Lx, Ly, Nx, Ny, a, beta_b, c, p=p, damping=0.6, tol=1e-8)
    print(f"  2D solve completed: {info}")

    fig, axs = plt.subplots(1, 2, figsize=(12, 5))

    # Left: Viability field
    im0 = axs[0].imshow(b, origin="lower", extent=[0, Lx, 0, Ly], cmap="RdYlGn", vmin=0.0, vmax=1.0)
    axs[0].set_title(r"Viability Field $b(x,y) = \kappa\gamma - \lambda\mu(x,y)$", fontsize=13)
    axs[0].set_xlabel("$x$", fontsize=12)
    axs[0].set_ylabel("$y$", fontsize=12)
    cbar0 = plt.colorbar(im0, ax=axs[0], fraction=0.046, pad=0.04)
    cbar0.set_label("Viability", fontsize=10)

    # Right: Presence field with contours
    im1 = axs[1].imshow(Phi, origin="lower", extent=[0, Lx, 0, Ly], cmap="viridis")
    if Phi.max() > 1e-6:  # Only add contours if there's actual structure
        axs[1].contour(Xg, Yg, Phi, levels=10, colors="white", linewidths=0.8, alpha=0.7)
    axs[1].set_title(r"Presence Field $\Phi(x,y)$ — V1′ Equilibrium", fontsize=13)
    axs[1].set_xlabel("$x$", fontsize=12)
    axs[1].set_ylabel("$y$", fontsize=12)
    cbar1 = plt.colorbar(im1, ax=axs[1], fraction=0.046, pad=0.04)
    cbar1.set_label("Presence intensity", fontsize=10)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "fig4_2d_presence_field.png", dpi=300, bbox_inches="tight")
    plt.savefig(OUTPUT_DIR / "fig4_2d_presence_field.pdf", bbox_inches="tight")
    plt.close()
    print(f"  Saved: fig4_2d_presence_field.png/pdf")


# =============================================================================
# Figure 5: Grid refinement convergence (numerical rigor)
# =============================================================================

def fig5_grid_refinement():
    print("Generating Figure 5: Grid refinement convergence...")
    L = 1.0
    p = 2.0
    c = 10.0
    a = 0.0
    b = 0.8

    beta_star = (np.pi / L) ** 2 / b
    beta_above = 1.2 * beta_star

    Ns = [100, 200, 400, 800, 1600]
    max_vals = []
    residuals = []

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    for Nn in Ns:
        xN, PhiN, infoN = solve_V1prime_1d_picard(L, Nn, a=a, beta_b=beta_above * b, c=c, p=p)
        max_vals.append(PhiN.max())
        
        # Compute residual
        h = L / (Nn + 1)
        Phi_xx = (PhiN[2:] - 2 * PhiN[1:-1] + PhiN[:-2]) / h**2
        Phi_x = (PhiN[2:] - PhiN[:-2]) / (2 * h)
        res = -Phi_xx - (a * np.abs(Phi_x) + beta_above * b * PhiN[1:-1] - c * np.maximum(PhiN[1:-1], 0.0) ** p)
        rinf = float(np.linalg.norm(res, np.inf))
        residuals.append(rinf)
        
        ax1.plot(xN, PhiN, linewidth=1.5, label=rf"$N={Nn}$")

    ax1.set_xlabel(r"$x$", fontsize=12)
    ax1.set_ylabel(r"$\Phi(x)$", fontsize=12)
    ax1.set_title("Solution Convergence Under Grid Refinement", fontsize=14)
    ax1.legend()

    # Convergence plot
    ax2.loglog(Ns, residuals, "ko-", markersize=8, linewidth=2)
    ax2.set_xlabel("Grid points $N$", fontsize=12)
    ax2.set_ylabel(r"Residual $\|\mathcal{R}\|_\infty$", fontsize=12)
    ax2.set_title("Residual Decay (Second-Order Convergence)", fontsize=14)
    
    # Add reference line for O(h²)
    h_ref = np.array(Ns)
    ax2.loglog(h_ref, 0.5 * (h_ref[0] / h_ref) ** (-2) * residuals[0], "r--", linewidth=1.5, label=r"$O(h^2)$ reference")
    ax2.legend()

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "fig5_grid_refinement.png", dpi=300, bbox_inches="tight")
    plt.savefig(OUTPUT_DIR / "fig5_grid_refinement.pdf", bbox_inches="tight")
    plt.close()
    print(f"  Saved: fig5_grid_refinement.png/pdf")


# =============================================================================
# Figure 6: Contradiction field visualization (1D)
# =============================================================================

def fig6_field_decomposition():
    print("Generating Figure 6: Field decomposition visualization...")
    L = 1.0
    N = 800
    x = np.linspace(0, L, N + 2)

    kappa = 0.9
    gamma = 0.9
    b0 = kappa * gamma

    mu = gaussian_bump_1d(x, center=0.5 * L, sigma=0.12 * L, amplitude=1.0)
    mu = np.clip(mu, 0.0, 1.0)

    lam = 1.5
    b_x = b0 - lam * mu
    a_x = b0 * mu

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x, np.ones_like(x) * b0, "k--", linewidth=1.5, label=r"$\kappa\gamma$ (care × coherence)")
    ax.plot(x, mu, "r-", linewidth=2, label=r"$\mu(x)$ (contradiction field)")
    ax.plot(x, b_x, "g-", linewidth=2, label=r"$b(x) = \kappa\gamma - \lambda\mu(x)$ (viability)")
    ax.plot(x, a_x, "b-", linewidth=2, label=r"$a(x) = \kappa\gamma\mu(x)$ (creative drive)")

    ax.axhline(0, color="gray", linestyle=":", linewidth=0.8)
    ax.fill_between(x, 0, b_x, where=(b_x < 0), alpha=0.2, color="red", label="Negative viability region")

    ax.set_xlabel(r"$x$", fontsize=12)
    ax.set_ylabel("Field intensity", fontsize=12)
    ax.set_title("Canonical Closure: Field Decomposition", fontsize=14)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.6, 1.1)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "fig6_field_decomposition.png", dpi=300, bbox_inches="tight")
    plt.savefig(OUTPUT_DIR / "fig6_field_decomposition.pdf", bbox_inches="tight")
    plt.close()
    print(f"  Saved: fig6_field_decomposition.png/pdf")


# =============================================================================
# Figure 7: 2D Phase Transition (viable vs non-viable comparison)
# =============================================================================

def fig7_2d_phase_transition():
    print("Generating Figure 7: 2D phase transition comparison...")
    Lx, Ly = 1.0, 1.0
    Nx, Ny = 80, 80
    p = 2.0
    c0 = 10.0

    kappa = 0.9
    gamma = 0.9
    b0 = kappa * gamma

    x = np.linspace(0, Lx, Nx + 2)
    y = np.linspace(0, Ly, Ny + 2)
    X, Y = np.meshgrid(x, y)

    sigma = 0.18
    mu = gaussian_bump_2d(X, Y, 0.5, 0.5, sigma, amplitude=0.8)
    mu = np.clip(mu, 0.0, 1.0)

    # Common beta
    beta_star_2d = ((np.pi / Lx) ** 2 + (np.pi / Ly) ** 2) / b0
    beta = 1.5 * beta_star_2d
    c = c0 * np.ones_like(X)

    # Case 1: Low contradiction (viable)
    lam_low = 0.3
    b_low = b0 - lam_low * mu
    a_low = b0 * mu
    beta_b_low = beta * b_low

    # Case 2: High contradiction (collapse)
    lam_high = 1.8
    b_high = b0 - lam_high * mu
    a_high = b0 * mu
    beta_b_high = beta * b_high

    _, _, Phi_low, info_low, _ = solve_V1prime_2d_picard(Lx, Ly, Nx, Ny, a_low, beta_b_low, c, p=p, damping=0.6, tol=1e-8)
    _, _, Phi_high, info_high, _ = solve_V1prime_2d_picard(Lx, Ly, Nx, Ny, a_high, beta_b_high, c, p=p, damping=0.6, tol=1e-8)

    print(f"  Low λ={lam_low}: maxPhi={info_low['maxPhi']:.4f}")
    print(f"  High λ={lam_high}: maxPhi={info_high['maxPhi']:.4e}")

    fig, axs = plt.subplots(1, 2, figsize=(12, 5))

    im0 = axs[0].imshow(Phi_low, origin="lower", extent=[0, Lx, 0, Ly], cmap="viridis")
    if Phi_low.max() > 1e-6:
        axs[0].contour(X, Y, Phi_low, levels=8, colors="white", linewidths=0.7, alpha=0.7)
    axs[0].set_title(rf"Viable: $\lambda = {lam_low}$ (max $\Phi$ = {Phi_low.max():.3f})", fontsize=13)
    axs[0].set_xlabel("$x$", fontsize=12)
    axs[0].set_ylabel("$y$", fontsize=12)
    plt.colorbar(im0, ax=axs[0], fraction=0.046, pad=0.04)

    im1 = axs[1].imshow(Phi_high, origin="lower", extent=[0, Lx, 0, Ly], cmap="viridis")
    axs[1].set_title(rf"Collapsed: $\lambda = {lam_high}$ (max $\Phi$ = {Phi_high.max():.2e})", fontsize=13)
    axs[1].set_xlabel("$x$", fontsize=12)
    axs[1].set_ylabel("$y$", fontsize=12)
    plt.colorbar(im1, ax=axs[1], fraction=0.046, pad=0.04)

    plt.suptitle("2D Phase Transition: Presence Collapse Under Excess Contradiction", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "fig7_2d_phase_transition.png", dpi=300, bbox_inches="tight")
    plt.savefig(OUTPUT_DIR / "fig7_2d_phase_transition.pdf", bbox_inches="tight")
    plt.close()
    print(f"  Saved: fig7_2d_phase_transition.png/pdf")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Creative Determinant PDE Framework — Figure Generation")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    fig1_eigenvalue_threshold()
    fig2_threshold_comparison()
    fig3_canonical_closure_sweep()
    fig4_2d_presence_field()
    fig5_grid_refinement()
    fig6_field_decomposition()
    fig7_2d_phase_transition()

    print()
    print("=" * 60)
    print("All figures generated successfully!")
    print("=" * 60)
