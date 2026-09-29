"""
Finite-graph Creative Determinant problem: the exact model checked in ``cd_formalization``.

This module implements, without normalization or reinterpretation, the definitions of
``CdFormal/Graph/Basic.lean``, the Jacobi splitting of ``CdFormal/Graph/FixedPoint.lean``, the
constants of ``SemioticGraph.exists_pos_graph`` (``CdFormal/Graph/Existence.lean``) and the
concrete example of ``CdFormal/Graph/Example.lean`` at the pinned submodule revision.

Model
-----
For finite vertices ``V``, symmetric nonnegative weights ``w``, boundary ``B`` and interior
``I = V \\ B``::

    L_G u(x) = Σ_y w(x,y) (u(x) - u(y))
    g_G u(x) = sqrt(Σ_y w(x,y) (u(y) - u(x))²)
    L_G u = a g_G u + b u - c max(u, 0)^p   on I,      u = 0 on B.

Both sums run over *all* vertices, so boundary edges contribute through the zero boundary
values. There is no vertex measure and no degree normalization. Self weights contribute
nothing to ``L_G``, ``g_G`` or the energy; they do enter the Jacobi numerator and denominator,
where they cancel at a fixed point.

The principal eigenvalue is the minimum of the Rayleigh quotient of ``L_G - diag(b)`` over
functions vanishing on ``B`` with unit Euclidean norm, i.e. the smallest eigenvalue of the
interior block of the *full-degree* Laplacian minus ``diag(b)``.

Status of the statements used here
----------------------------------
* Theorem 3.26 (Lean, ``SemioticGraph.exists_pos_graph``): if the interior graph is connected,
  the principal eigenvalue is negative, and ``a(x) <= sqrt(w(x,y))`` at both ends of every
  positive-weight edge between distinct interior vertices, then a solution positive at every
  interior vertex exists. The edge condition is sufficient for that proof, not necessary.
* Example 3.29 (Lean, ``triangle_isSolution``, ``triangle_gradNorm``): ``u = (0, 2, 2)`` solves
  the triangle example with gradient norm 2 at both interior vertices.
* Proposition 3.30 (classical proof in the paper; not a Lean declaration): a nonnegative
  solution satisfies ``max u <= max_x ((b(x) + a(x)²/4)_+ / c(x))^{1/(p-1)}``
  (``linfty_bound_graph``); the bound is attained and differs from the continuum cap
  ``(b/c)^{1/(p-1)}`` (Remark 3.31).
* Proposition 3.32: ``λ₁ < 0`` is not necessary on graphs (the triangle with ``b = 1/2`` has a
  positive solution and ``λ₁ = +1/2``).
* Observation (numerical; Remark 3.28): iterating the Jacobi map from the sub- or
  supersolution barrier converges monotonically in the runs recorded by the tests.
  Convergence of the iteration is a classical consequence of monotonicity in finite
  dimensions; it is not part of the Lean development, which proves existence only, and no
  rate is claimed.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any

import numpy as np

from ._validation import (
    check_exponent,
    check_finite_array,
    check_nonnegative_scalar,
    check_positive_int,
    check_positive_scalar,
    require_positive_coefficient,
)
from .analysis import _monotone_label

__all__ = [
    "SemioticGraph",
    "edge_condition",
    "edge_condition_holds",
    "energy",
    "existence_theorem_applies",
    "grad_norm",
    "spectral_report",
    "interior_connected",
    "jacobi_map",
    "laplacian",
    "linfty_bound_graph",
    "plateau",
    "principal_eigenpair",
    "proof_constants",
    "residual",
    "solve_graph",
    "triangle",
]


def _unit_interval_field(name: str, value: object, n: int) -> np.ndarray:
    arr = check_finite_array(name, value, shape=(n,))
    if np.any(arr < 0.0) or np.any(arr > 1.0):
        raise ValueError(f"{name} must take values in [0, 1]")
    return arr


@dataclass(frozen=True)
class SemioticGraph:
    """A finite weighted graph with a Dirichlet boundary and the CD coefficients.

    Attributes
    ----------
    w : ndarray, shape (n, n)
        Symmetric nonnegative edge weights. Diagonal entries are allowed and irrelevant to the
        operators (they cancel in the Jacobi map).
    boundary : ndarray of bool, shape (n,)
        ``True`` at boundary vertices, where solutions vanish.
    a : ndarray, shape (n,)
        Creative drive ``a = κγμ`` with values in ``[0, 1]``.
    b : ndarray, shape (n,)
        Viability potential (any finite values).
    c : ndarray, shape (n,)
        Carrying capacity, strictly positive.
    p : float
        Saturation exponent, ``p > 1``.
    """

    w: np.ndarray
    boundary: np.ndarray
    a: np.ndarray
    b: np.ndarray
    c: np.ndarray
    p: float

    def __post_init__(self) -> None:
        w = check_finite_array("w", self.w)
        if w.ndim != 2 or w.shape[0] != w.shape[1]:
            raise ValueError(f"w must be a square matrix, got shape {w.shape}")
        n = w.shape[0]
        if n < 1:
            raise ValueError("the graph needs at least one vertex")
        if np.any(w < 0.0):
            raise ValueError("weights must be nonnegative")
        if not np.array_equal(w, w.T):
            raise ValueError(
                "weights must be exactly symmetric (the Lean model has w x y = w y x); "
                "symmetrize explicitly with 0.5 * (w + w.T) if that is the intended model"
            )
        boundary = np.asarray(self.boundary)
        if boundary.shape != (n,):
            raise ValueError(f"boundary must have shape ({n},), got {boundary.shape}")
        boundary = boundary.astype(bool)
        a = _unit_interval_field("a", self.a, n)
        b = check_finite_array("b", self.b, shape=(n,))
        c = check_finite_array("c", self.c, shape=(n,))
        require_positive_coefficient("c", c)
        p = check_exponent("p", self.p)
        for name, value in (
            ("w", w),
            ("boundary", boundary),
            ("a", a),
            ("b", b),
            ("c", c),
            ("p", p),
        ):
            object.__setattr__(self, name, value)

    @classmethod
    def from_fields(
        cls,
        w: np.ndarray,
        boundary: np.ndarray,
        kappa: np.ndarray,
        gamma: np.ndarray,
        mu: np.ndarray,
        b: np.ndarray,
        c: np.ndarray,
        p: float,
    ) -> SemioticGraph:
        """Build the graph from care, coherence and contradiction fields in ``[0, 1]``,
        with ``a = κγμ`` (``SemioticGraph.a`` in Lean). ``b`` is a free admissible
        coefficient here, not the canonical closure."""
        n = int(np.asarray(w).shape[0]) if np.ndim(w) == 2 else -1
        kappa_arr = _unit_interval_field("kappa", kappa, n)
        gamma_arr = _unit_interval_field("gamma", gamma, n)
        mu_arr = _unit_interval_field("mu", mu, n)
        return cls(w=w, boundary=boundary, a=kappa_arr * gamma_arr * mu_arr, b=b, c=c, p=p)

    @property
    def n(self) -> int:
        """Number of vertices."""
        return int(self.w.shape[0])

    @property
    def interior(self) -> np.ndarray:
        """Boolean mask of interior vertices."""
        return ~self.boundary

    @property
    def degree(self) -> np.ndarray:
        """``d(x) = Σ_y w(x,y)`` over all vertices, self weight included."""
        return self.w.sum(axis=1)


def _field(G: SemioticGraph, u: object) -> np.ndarray:
    return check_finite_array("u", u, shape=(G.n,))


def laplacian(G: SemioticGraph, u: np.ndarray) -> np.ndarray:
    """``(L_G u)(x) = Σ_y w(x,y) (u(x) - u(y))`` at every vertex (Lean ``SemioticGraph.laplacian``)."""
    u = _field(G, u)
    return (G.w * (u[:, None] - u[None, :])).sum(axis=1)


def grad_norm(G: SemioticGraph, u: np.ndarray) -> np.ndarray:
    """``|∇u|(x) = sqrt(Σ_y w(x,y) (u(y) - u(x))²)`` (Lean ``SemioticGraph.gradNorm``)."""
    u = _field(G, u)
    return np.sqrt((G.w * (u[None, :] - u[:, None]) ** 2).sum(axis=1))


def _reaction(G: SemioticGraph, u: np.ndarray) -> np.ndarray:
    return G.a * grad_norm(G, u) + G.b * u - G.c * np.maximum(u, 0.0) ** G.p


def residual(G: SemioticGraph, u: np.ndarray) -> np.ndarray:
    """Equation residual ``L_G u - (a|∇u| + b u - c u₊^p)`` at interior vertices and the
    boundary violation ``u(x) - 0`` at boundary vertices. ``u`` solves the problem
    (Lean ``SemioticGraph.IsSolution``) iff this vanishes identically."""
    u = _field(G, u)
    r = laplacian(G, u) - _reaction(G, u)
    r[G.boundary] = u[G.boundary]
    return r


def energy(G: SemioticGraph, u: np.ndarray) -> float:
    """Quadratic form of ``L_G - diag(b)``:
    ``½ Σ_x Σ_y w(x,y)(u(x)-u(y))² - Σ_x b(x) u(x)²`` (Lean ``SemioticGraph.energy``)."""
    u = _field(G, u)
    return float(0.5 * (G.w * (u[:, None] - u[None, :]) ** 2).sum() - (G.b * u**2).sum())


def interior_connected(G: SemioticGraph) -> bool:
    """Whether the interior graph (interior vertices joined by positive-weight edges) is
    connected and nonempty (Lean ``SemioticGraph.interiorGraph.Connected``)."""
    interior = [int(i) for i in np.flatnonzero(G.interior)]
    if not interior:
        return False
    seen = {interior[0]}
    queue = deque([interior[0]])
    while queue:
        x = queue.popleft()
        for y in interior:
            if y not in seen and y != x and G.w[x, y] > 0.0:
                seen.add(y)
                queue.append(y)
    return len(seen) == len(interior)


def _off_diagonal(w: np.ndarray) -> np.ndarray:
    """Copy of the weight matrix with the diagonal (self weights) set to zero."""
    off = w.copy()
    np.fill_diagonal(off, 0.0)
    return off


def _dirichlet_block(G: SemioticGraph) -> tuple[np.ndarray, np.ndarray]:
    """Interior block of ``diag(d') - w' - diag(b)`` where ``w'`` is ``w`` with the diagonal
    removed and ``d'`` its row sums (boundary edges included).

    Self weights contribute nothing to ``L_G`` (the pair difference vanishes), so they are
    removed *before* summation. Forming ``diag(d) - w`` with the diagonal included would
    cancel ``w(x,x)`` against itself only in exact arithmetic; a large self weight would
    swamp the off-diagonal contributions in floating point and corrupt the operator.
    """
    interior = np.flatnonzero(G.interior)
    off = _off_diagonal(G.w)
    full = np.diag(off.sum(axis=1)) - off - np.diag(G.b)
    return interior, full[np.ix_(interior, interior)]


def principal_eigenpair(G: SemioticGraph) -> tuple[float, np.ndarray]:
    """Principal Dirichlet eigenvalue of ``L_G - diag(b)`` and a unit eigenvector.

    The eigenvalue is the smallest eigenvalue of the interior block of the full-degree
    Laplacian ``diag(d') - w' - diag(b)`` (degrees include boundary edges; self weights are
    removed before summation because they do not enter ``L_G``; nothing is recomputed after
    removing boundary vertices). The returned vector vanishes on the boundary, has unit
    Euclidean norm and is nonnegative; Theorem (Lean ``SemioticGraph.exists_pos_eigenvector``,
    used in the proof of Theorem 3.26): it is positive at every interior vertex when the
    interior graph is connected.

    Use ``spectral_report`` for the independent verification of the pair against the direct
    operator and the Rayleigh quotient.

    Raises
    ------
    ValueError
        If the interior is empty (the infimum over the empty unit sphere is not defined).
    """
    interior, block = _dirichlet_block(G)
    if interior.size == 0:
        raise ValueError("the principal eigenvalue requires a nonempty interior")
    vals, vecs = np.linalg.eigh(block)
    v = np.abs(vecs[:, 0])
    v /= np.linalg.norm(v)
    phi = np.zeros(G.n)
    phi[interior] = v
    return float(vals[0]), phi


def spectral_report(G: SemioticGraph) -> dict[str, Any]:
    """Principal eigendata checked against independently evaluated quantities.

    Returns ``lam1`` (from the assembled block), ``phi``, ``rayleigh`` (the energy of ``phi``
    evaluated directly from pair differences divided by ``sum phi^2``; Theorem (Rayleigh
    quotient, the infimum in Definition 3.25): an upper bound for the exact ``lambda_1``),
    ``defect`` (``max |L_G phi - b phi - lam1 phi|`` on the interior, with
    ``L_G`` evaluated from pair differences), ``margin`` (a floating-point margin, see below)
    and ``status``:

    * ``"negative"``: both ``lam1`` and the Rayleigh quotient lie below ``-margin`` and the
      defect is small; the hypothesis ``lambda_1 < 0`` of the Lean theorem holds up to
      floating-point rounding of the reported quantities.
    * ``"nonnegative"``: ``lam1 > margin``.
    * ``"indeterminate"``: ``|lam1| <= margin`` or the defect is not small; no sign claim.

    The margin ``1e3 * n * eps * (max degree + max |b|)`` is a rounding allowance, not a
    proof. An exact certificate is a function ``u`` with rational entries and ``E(u) < 0``
    evaluated exactly (Lean ``principalEigenvalue_neg``).
    """
    lam1, phi = principal_eigenpair(G)
    interior = G.interior
    off = _off_diagonal(G.w)
    scale = float(off.sum(axis=1).max() + np.abs(G.b).max())
    margin = 1e3 * G.n * np.finfo(float).eps * max(1.0, scale)
    rayleigh = energy(G, phi) / float(np.sum(phi**2))
    defect = float(np.max(np.abs((laplacian(G, phi) - G.b * phi - lam1 * phi)[interior])))
    small_defect = defect <= 1e3 * margin * max(1.0, abs(lam1))
    if lam1 < -margin and rayleigh < -margin and small_defect:
        status = "negative"
    elif lam1 > margin and small_defect:
        status = "nonnegative"
    else:
        status = "indeterminate"
    return {
        "lam1": lam1,
        "phi": phi,
        "rayleigh": float(rayleigh),
        "defect": defect,
        "margin": float(margin),
        "status": status,
    }


def edge_condition(G: SemioticGraph) -> np.ndarray:
    """Boolean matrix of violations of the edge-dominance hypothesis of the Lean theorem:
    entry ``(x, y)`` is ``True`` when ``x ≠ y`` are interior, ``w(x,y) > 0`` and
    ``a(x) > sqrt(w(x,y))``. The hypothesis quantifies over ordered pairs, so both ends of
    every edge are checked."""
    interior = G.interior
    positive = G.w > 0.0
    distinct = ~np.eye(G.n, dtype=bool)
    relevant = positive & distinct & interior[:, None] & interior[None, :]
    # The exact hypothesis, evaluated in floating point with no slack: a numerical tolerance
    # would silently weaken the theorem's assumption.
    violated = G.a[:, None] > np.sqrt(G.w)
    return relevant & violated


def edge_condition_holds(G: SemioticGraph) -> bool:
    """``a(x) <= sqrt(w(x,y))`` for every ordered pair of distinct interior vertices with
    ``w(x,y) > 0``. Corollary 3.27 (Lean ``exists_pos_graph_of_unweighted``): for weights in
    ``{0, 1}`` this follows from ``0 <= a <= 1``."""
    return not bool(edge_condition(G).any())


def existence_theorem_applies(G: SemioticGraph) -> dict[str, Any]:
    """Check the hypotheses of ``SemioticGraph.exists_pos_graph`` and report each one.

    ``applies`` is ``True`` iff the interior is nonempty and connected, the edge condition
    holds exactly, and the spectral status is ``"negative"`` (see ``spectral_report``: the
    assembled eigenvalue and the directly evaluated Rayleigh quotient both lie below a stated
    floating-point margin). An eigenvalue within the margin of zero is ``"indeterminate"`` and
    does not certify the theorem. When ``applies`` is ``False`` the theorem does not apply;
    that is not evidence that no positive solution exists.
    """
    report: dict[str, Any] = {
        "interior_nonempty": bool(G.interior.any()),
        "interior_connected": interior_connected(G),
        "edge_condition": edge_condition_holds(G),
        "principal_eigenvalue": None,
        "rayleigh_upper_bound": None,
        "spectral_margin": None,
        "spectral_status": "undefined",
        "negative_eigenvalue": False,
    }
    if report["interior_nonempty"]:
        spec = spectral_report(G)
        report["principal_eigenvalue"] = spec["lam1"]
        report["rayleigh_upper_bound"] = spec["rayleigh"]
        report["spectral_margin"] = spec["margin"]
        report["spectral_status"] = spec["status"]
        report["negative_eigenvalue"] = spec["status"] == "negative"
    keys = ("interior_nonempty", "interior_connected", "edge_condition", "negative_eigenvalue")
    report["failed"] = [k for k in keys if not report[k]]
    report["applies"] = not report["failed"]
    return report


def plateau(G: SemioticGraph, M: float) -> np.ndarray:
    """``M`` at interior vertices and ``0`` on the boundary (Lean ``SemioticGraph.plateau``)."""
    return np.where(G.boundary, 0.0, float(M))


def jacobi_map(G: SemioticGraph, u: np.ndarray, K: float) -> np.ndarray:
    """The shifted Jacobi fixed-point map (Lean ``SemioticGraph.fixedPointMap``)::

        F_K(u)(x) = [Σ_y w(x,y) u(y) + a(x)|∇u|(x) + (b(x)+K) u(x) - c(x) max(u(x),0)^p]
                    / [Σ_y w(x,y) + K]      on the interior,  0 on the boundary.

    Theorem (Lean ``fixedPointMap_eq_iff_isSolution``): for ``K > 0`` its fixed points are
    exactly the solutions. Lemma (Lean ``mul_sub_numer``): ``(d(x) + K)(u(x) - F_K(u)(x))``
    equals the equation residual.
    """
    K = check_positive_scalar("K", K)
    u = _field(G, u)
    numer = G.w @ u + G.a * grad_norm(G, u) + (G.b + K) * u - G.c * np.maximum(u, 0.0) ** G.p
    denom = G.degree + K
    return np.where(G.boundary, 0.0, numer / denom)


def proof_constants(G: SemioticGraph) -> dict[str, Any]:
    """The constants constructed inside the proof of ``exists_pos_graph`` for this graph.

    Theorem 3.26 (Lean ``SemioticGraph.exists_pos_graph``, proof constants): with ``λ₁ < 0``
    and the positive unit eigenvector ``φ``::

        t   = -λ₁ / (-λ₁ + Σ_x c(x)),         ε = t^{1/(p-1)}      (so c ε^{p-1} <= -λ₁)
        M   = (1 + Σ_y (|b(y)| + a(y)²/4) / c(y))^{1/(p-1)}        (so a²/4 + b <= c M^{p-1})
        K   = 1 + Σ_x (a(x) Σ_y sqrt(w(x,y)) + c(x) p M^{p-1} + |b(x)|)

    ``sub = ε φ`` is a subsolution (Lean ``smul_subsolution``) and ``sup = plateau(M)`` a
    supersolution (Lean ``plateau_supersolution``).

    Raises
    ------
    ValueError
        If the interior is empty or the principal eigenvalue is not negative.
    """
    lam1, phi = principal_eigenpair(G)
    if not lam1 < 0.0:
        raise ValueError(f"the barriers require a negative principal eigenvalue, got {lam1}")
    p = G.p
    t = -lam1 / (-lam1 + float(G.c.sum()))
    eps = t ** (1.0 / (p - 1.0))
    M = (1.0 + float(((np.abs(G.b) + G.a**2 / 4.0) / G.c).sum())) ** (1.0 / (p - 1.0))
    K = 1.0 + float((G.a * np.sqrt(G.w).sum(axis=1) + G.c * p * M ** (p - 1.0) + np.abs(G.b)).sum())
    return {
        "lam1": lam1,
        "phi": phi,
        "eps": float(eps),
        "M": float(M),
        "K": float(K),
        "sub": eps * phi,
        "sup": plateau(G, M),
    }


def linfty_bound_graph(G: SemioticGraph) -> float:
    """Upper bound for nonnegative solutions on the graph:
    ``max_{x interior} ((b(x) + a(x)²/4)_+ / c(x))^{1/(p-1)}``.

    Proposition 3.30 (classical proof in the paper's finite-graph section). At a positive
    maximum ``M`` of a nonnegative solution, attained at an interior vertex ``x``,
    ``S = L_G u(x) >= 0`` and ``|∇u|(x)² <= M S``; the completed square
    ``a sqrt(M S) <= S + (a²/4) M`` (Lean ``mul_sqrt_mul_le``) then gives
    ``c(x) M^{p-1} <= b(x) + a(x)²/4``. The bound is not itself a Lean declaration at the
    pinned revision. Remark 3.31: it differs materially from the continuum cap
    ``(b/c)^{1/(p-1)}`` (Lemma 3.10), which uses ``∇u = 0`` at an interior maximum.
    """
    interior = G.interior
    if not interior.any():
        return 0.0
    ratio = np.maximum(G.b + G.a**2 / 4.0, 0.0) / G.c
    return float(np.max(ratio[interior]) ** (1.0 / (G.p - 1.0)))


def solve_graph(
    G: SemioticGraph,
    start: str | np.ndarray = "subsolution",
    K: float | None = None,
    max_iter: int = 10000,
    atol: float = 1e-12,
    rtol: float = 1e-12,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Iterate the shifted Jacobi map and validate the result through its residual.

    Parameters
    ----------
    G : SemioticGraph
    start : {"subsolution", "plateau"} or ndarray
        Initial function. The named barriers are those of ``proof_constants`` (they require
        ``λ₁ < 0``); an explicit array must be finite with zero boundary values.
    K : float, optional
        Shift of the Jacobi splitting (``K > 0``). Defaults to the proof's constant.
    max_iter : int
        Iteration budget (``>= 1``).
    atol, rtol : float
        Convergence: ``||residual||_∞ <= atol + rtol * scale`` on the interior, where
        ``scale = max(||L_G u||_∞, ||reaction||_∞)``.

    Returns
    -------
    u : ndarray
        Final iterate.
    info : dict
        ``converged``, ``termination`` (``"converged"``, ``"max_iter"``, ``"nonfinite"``,
        ``"stagnation"``), ``iters``, ``residual_inf``, ``residual_scale``, ``update_inf``,
        ``boundary_err``, ``monotone`` (``"nondecreasing"``, ``"nonincreasing"``,
        ``"constant"`` or ``"non-monotone"``), ``K``, ``min_interior``, ``max``.

    Notes
    -----
    Existence of a fixed point between the barriers is the Lean theorem; the convergence
    observed here is reported, not assumed. An exhausted budget or a nonfinite iterate is a
    failure, never an accepted solution.
    """
    max_iter = check_positive_int("max_iter", max_iter)
    atol = check_nonnegative_scalar("atol", atol)
    rtol = check_nonnegative_scalar("rtol", rtol)
    consts: dict[str, Any] | None = None
    if isinstance(start, str):
        if start not in ("subsolution", "plateau"):
            raise ValueError("start must be 'subsolution', 'plateau', or an array")
        consts = proof_constants(G)
        u = np.array(consts["sub"] if start == "subsolution" else consts["sup"], dtype=float)
    else:
        u = _field(G, start).copy()
        if np.any(u[G.boundary] != 0.0):
            raise ValueError("the initial function must vanish on the boundary")
    if K is None:
        if consts is None:
            try:
                consts = proof_constants(G)
            except ValueError as exc:
                raise ValueError("K must be given explicitly when λ₁ >= 0") from exc
        K = consts["K"]
    K = check_positive_scalar("K", K)

    interior = G.interior
    converged = False
    termination = "max_iter"
    iters = 0
    update_inf = float("nan")
    min_step = float("inf")
    max_step = float("-inf")

    def _residual_state(v: np.ndarray) -> tuple[float, float]:
        lap = laplacian(G, v)
        reac = _reaction(G, v)
        r = (lap - reac)[interior]
        s = max(float(np.max(np.abs(lap[interior]))), float(np.max(np.abs(reac[interior]))))
        return float(np.max(np.abs(r))), s

    res_inf, scale = _residual_state(u)
    if not np.isfinite(res_inf):
        termination = "nonfinite"
    elif res_inf <= atol + rtol * scale:
        # The initial function already solves the problem: zero iterations, zero update.
        converged = True
        termination = "converged"
        update_inf = 0.0
    else:
        for iters in range(1, max_iter + 1):
            v = jacobi_map(G, u, K)
            if not np.all(np.isfinite(v)):
                termination = "nonfinite"
                u = v
                res_inf, scale = float("nan"), float("nan")
                break
            step = v - u
            update_inf = float(np.max(np.abs(step)))
            min_step = min(min_step, float(step.min()))
            max_step = max(max_step, float(step.max()))
            u = v
            res_inf, scale = _residual_state(u)
            if not np.isfinite(res_inf):
                termination = "nonfinite"
                break
            if res_inf <= atol + rtol * scale:
                converged = True
                termination = "converged"
                break
            if update_inf == 0.0:
                termination = "stagnation"
                break

    step_tol = 1e-12 * max(1.0, float(np.max(np.abs(u))) if np.all(np.isfinite(u)) else 1.0)
    info: dict[str, Any] = {
        "converged": converged,
        "termination": termination,
        "iters": iters,
        "residual_inf": res_inf,
        "residual_scale": scale,
        "update_inf": update_inf,
        "boundary_err": float(np.max(np.abs(u[G.boundary]))) if G.boundary.any() else 0.0,
        "monotone": _monotone_label(min_step, max_step, step_tol) if iters > 0 else "constant",
        "K": K,
        "min_interior": float(np.min(u[interior])) if interior.any() else float("nan"),
        "max": float(np.max(u)) if np.all(np.isfinite(u)) else float("nan"),
        "atol": atol,
        "rtol": rtol,
    }
    return u, info


def triangle() -> SemioticGraph:
    """Example 3.29, the verified Lean example ``SemioticGraph.triangle``: complete graph on
    three vertices with all weights equal to 1 (diagonal included), boundary ``{0}``,
    ``κ = γ = μ = 1`` (so ``a = 1``), ``b = 2``, ``c = 1``, ``p = 2``. Theorem (Lean
    ``triangle_isSolution``, ``triangle_gradNorm``, ``triangle_energy``): ``u = (0, 2, 2)``
    solves it with gradient norm 2 at both interior vertices, ``(0, 1, 1)`` has energy ``-2``,
    and its principal eigenvalue is ``-1``. The independent ``b = 2`` here is a free admissible
    coefficient; it is not the canonical closure ``κγ - λμ`` with ``λ > 0``."""
    return SemioticGraph(
        w=np.ones((3, 3)),
        boundary=np.array([True, False, False]),
        a=np.ones(3),
        b=np.full(3, 2.0),
        c=np.ones(3),
        p=2.0,
    )
