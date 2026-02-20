
#!/usr/bin/env python3
"""
coolantHoseCalcs.py

Simple utility functions to estimate pressure drop, head loss, and required pump
conditions for coolant hoses and rigid tubing. Designed to help size hoses and
estimate how hose ID, length, fittings, and fluid properties affect system
pressure and flow.

Functions included:
- reynolds_number(rho, mu, v, d)
- friction_factor_haland(d, k, Re)
- darcy_weisbach_loss(f, L, d, v)
- minor_loss_coeffs(fittings)  # rough estimate for standard fittings
- pressure_drop_pipe(rho, mu, Q, d, L, k=1.5e-6, fittings=None)
- flow_from_pump_pressure(rho, mu, d, L, pump_deltaP, k=1.5e-6, fittings=None)
- convert_units helpers

Command-line usage:
    python coolantHoseCalcs.py --flow 20 --dia 0.01905 --length 10
    (Flow in L/min, diameter in m, length in m)

Notes:
- Default roughness k (m) is about 1.5e-6 for commercial-grade smooth steel or
  rigid tubing; for rubber hoses roughness can be higher (1e-5 to 1e-4).
- Uses Haaland approximation for friction factor.
- Fluid properties must be provided in SI units (rho kg/m^3, mu Pa.s).
"""

from math import log10, sqrt, pi
import argparse
import sys

# ---- Physical constants / helpers ----
def lpm_to_m3s(lpm):
    """Convert liters per minute to cubic meters per second."""
    return lpm / 1000.0 / 60.0

def m3s_to_lpm(m3s):
    return m3s * 1000.0 * 60.0

def pa_to_psi(pa):
    return pa / 6894.75729

def psi_to_pa(psi):
    return psi * 6894.75729

def m_to_mm(m):
    return m * 1000.0

# ---- Fluid mechanics ----
def reynolds_number(rho, mu, v, d):
    """
    Calculate Reynolds number.
    rho : density (kg/m^3)
    mu  : dynamic viscosity (Pa.s) (N.s/m^2)
    v   : velocity (m/s)
    d   : internal diameter (m)
    Returns Re (dimensionless)
    """
    if mu <= 0 or d <= 0:
        raise ValueError("Viscosity and diameter must be positive")
    Re = (rho * v * d) / mu
    return Re

def friction_factor_haland(d, k, Re):
    """
    Haaland approximation for turbulent flow friction factor f (Darcy).
    d : pipe diameter (m)
    k : absolute roughness (m)
    Re: Reynolds number
    Returns f (dimensionless)
    """
    if Re <= 0:
        raise ValueError("Reynolds number must be positive")
    # For laminar flow (Re < 2300) use f = 64/Re
    if Re < 2300:
        return 64.0 / Re
    # Haaland equation
    term = (k / (3.7 * d))**1.11 + 6.9 / Re
    f = ( -1.8 * log10(term) )**-2
    return f

def darcy_weisbach_loss(f, L, d, v):
    """
    Darcy-Weisbach frictional head loss (Pa).
    f : friction factor (dimensionless)
    L : pipe length (m)
    d : pipe diameter (m)
    v : mean flow velocity (m/s)
    Returns pressure drop in Pascals (Pa)
    """
    return f * (L / d) * 0.5 * v**2 * 1.0  # multiply by rho later if needed by caller

# ---- Minor (local) losses) ----
STANDARD_FITTING_K = {
    'straight_open_valve': 0.05,
    'globe_valve': 10.0,
    'gate_valve': 0.2,
    '90_elbow_smooth': 0.3,
    '90_elbow_sharp': 1.5,
    '45_elbow': 0.2,
    'tee_run': 0.6,
    'tee_branch': 1.8,
    'hose_barb': 2.0,
    'full_port_ball_valve': 0.05,
    'filter': 1.0,
    'quick_connect': 0.8,
}

def minor_loss_coeffs(fittings):
    """
    Sum K coefficients for a list of fittings. fittings is an iterable of keys
    from STANDARD_FITTING_K. Unknown fittings will raise a KeyError.
    """
    if not fittings:
        return 0.0
    K_total = 0.0
    for f in fittings:
        if f not in STANDARD_FITTING_K:
            raise KeyError(f"Unknown fitting key: {f}")
        K_total += STANDARD_FITTING_K[f]
    return K_total

# ---- High-level calculations ----
def pressure_drop_pipe(rho, mu, Q, d, L, k=1.5e-6, fittings=None):
    """
    Calculate total pressure drop (Pa) for a length of pipe/hose with given flow.
    rho : fluid density (kg/m^3)
    mu  : dynamic viscosity (Pa.s)
    Q   : volumetric flow (m^3/s)
    d   : internal diameter (m)
    L   : length (m)
    k   : absolute roughness (m) (default 1.5e-6)
    fittings: iterable of fitting keys for minor losses
    Returns: total pressure drop in Pascals (Pa)
    """
    if Q < 0:
        raise ValueError("Flow must be non-negative")
    if d <= 0 or L < 0:
        raise ValueError("Diameter must be positive and length non-negative")
    A = pi * (d/2.0)**2
    if A <= 0:
        raise ValueError("Invalid diameter generating non-positive area")
    v = Q / A
    Re = reynolds_number(rho, mu, v, d) if v > 0 else 0.0
    f = friction_factor_haland(d, k, Re) if v > 0 else 0.0
    # Frictional loss (Pa) = f*(L/d)*0.5*rho*v^2
    friction_loss = f * (L / d) * 0.5 * rho * v**2
    # Minor losses (Pa) = K_total * 0.5*rho*v^2
    K_total = minor_loss_coeffs(fittings) if fittings else 0.0
    minor_loss = K_total * 0.5 * rho * v**2
    total_loss = friction_loss + minor_loss
    return {
        'Q_m3s': Q,
        'velocity_m_s': v,
        'Re': Re,
        'friction_factor': f,
        'friction_loss_Pa': friction_loss,
        'minor_loss_Pa': minor_loss,
        'total_loss_Pa': total_loss,
        'total_loss_psi': pa_to_psi(total_loss)
    }

def flow_from_pump_pressure(rho, mu, d, L, pump_deltaP_pa, k=1.5e-6, fittings=None, tol=1e-6, maxiter=100):
    """
    Given available pump pressure (Pa), estimate achievable flow (m^3/s) through
    the pipe/hose. Solves for Q iteratively because friction factor depends on Re.
    Returns Q (m^3/s).
    """
    if pump_deltaP_pa <= 0:
        return 0.0
    # Initial guess: assume friction factor ~0.02 and minor losses 0
    A = pi * (d/2.0)**2
    # Use energy equation: pump_deltaP = 0.5*rho*v^2*( f*(L/d) + K_total )
    K_total = minor_loss_coeffs(fittings) if fittings else 0.0
    f_guess = 0.02
    v = sqrt((2 * pump_deltaP_pa) / (rho * (f_guess * (L/d) + K_total)))
    Q = A * v
    for i in range(maxiter):
        Re = reynolds_number(rho, mu, v, d)
        f = friction_factor_haland(d, k, Re) if v > 0 else 0.0
        denom = rho * (f * (L/d) + K_total) / 2.0
        if denom <= 0:
            raise RuntimeError("Denominator non-positive during iteration")
        v_new = sqrt(pump_deltaP_pa / denom)
        if abs(v_new - v) < tol:
            v = v_new
            break
        v = v_new
        Q = A * v
    else:
        # did not converge
        pass
    return {
        'Q_m3s': Q,
        'Q_lpm': m3s_to_lpm(Q),
        'velocity_m_s': v,
        'Re': reynolds_number(rho, mu, v, d) if v>0 else 0.0,
        'friction_factor': friction_factor_haland(d, k, reynolds_number(rho, mu, v, d)) if v>0 else 0.0
    }

# ---- Example default coolant properties ----
# Typical ethylene glycol-based engine coolant ~ 20-50% mix has roughly:
COOLANT_DEFAULT = {
    'density_kg_m3': 1050.0,   # approximate
    'viscosity_Pa_s': 0.0020   # 2 cP = 0.002 Pa.s (varies with temp)
}

# ---- CLI interface ----
def parse_args(argv):
    p = argparse.ArgumentParser(description="Estimate hose pressure drop / flow for coolant systems.")
    p.add_argument('--flow', '-f', type=float, help="Flow rate in L/min (if provided, script computes pressure drop).", default=None)
    p.add_argument('--dia', '-d', type=float, help="Inner diameter in inches or meters (see --units). Default 3/4\" = 0.01905 m", default=0.01905)
    p.add_argument('--length', '-L', type=float, help="Length in meters", default=10.0)
    p.add_argument('--units', choices=['m','in'], default='m', help="Units for diameter: 'm' or 'in' (default m)")
    p.add_argument('--pump_psi', type=float, help="Pump available delta pressure in psi (if provided, script computes achievable flow).", default=None)
    p.add_argument('--rho', type=float, help="Fluid density kg/m^3", default=COOLANT_DEFAULT['density_kg_m3'])
    p.add_argument('--mu', type=float, help="Fluid dynamic viscosity Pa.s (N.s/m^2). 0.001 Pa.s = 1 cP", default=COOLANT_DEFAULT['viscosity_Pa_s'])
    p.add_argument('--roughness', type=float, help="Absolute roughness k in meters (default 1.5e-6)", default=1.5e-6)
    p.add_argument('--fittings', type=str, help="Comma-separated list of fittings keys (e.g. 90_elbow_smooth,full_port_ball_valve)", default="")
    return p.parse_args(argv)

def main(argv):
    args = parse_args(argv)
    # Diameter conversion if inches specified
    d = args.dia
    if args.units == 'in':
        d = args.dia * 0.0254
    fittings = [x.strip() for x in args.fittings.split(',')] if args.fittings else []
    # Remove empty strings
    fittings = [f for f in fittings if f]

    rho = args.rho
    mu = args.mu
    k = args.roughness

    if args.flow is not None and args.pump_psi is not None:
        print("Provide either --flow (to compute pressure drop) OR --pump_psi (to compute achievable flow), not both.")
        sys.exit(1)

    if args.flow is not None:
        Q_m3s = lpm_to_m3s(args.flow)
        result = pressure_drop_pipe(rho, mu, Q_m3s, d, args.length, k=k, fittings=fittings)
        print(f"Input: flow = {args.flow:.2f} L/min, dia = {m_to_mm(d):.2f} mm, length = {args.length:.2f} m")
        print(f"Velocity = {result['velocity_m_s']:.3f} m/s")
        print(f"Re = {result['Re']:.0f}")
        print(f"Friction factor f = {result['friction_factor']:.5f}")
        print(f"Frictional loss = {result['friction_loss_Pa']:.1f} Pa ({pa_to_psi(result['friction_loss_Pa']):.3f} psi)")
        print(f"Minor loss = {result['minor_loss_Pa']:.1f} Pa ({pa_to_psi(result['minor_loss_Pa']):.3f} psi)")
        print(f"Total pressure drop = {result['total_loss_Pa']:.1f} Pa ({result['total_loss_psi']:.3f} psi)")
    elif args.pump_psi is not None:
        pump_pa = psi_to_pa(args.pump_psi)
        res = flow_from_pump_pressure(rho, mu, d, args.length, pump_pa, k=k, fittings=fittings)
        print(f"Input: pump deltaP = {args.pump_psi:.3f} psi, dia = {m_to_mm(d):.2f} mm, length = {args.length:.2f} m")
        print(f"Estimated flow = {res['Q_lpm']:.2f} L/min")
        print(f"Velocity = {res['velocity_m_s']:.3f} m/s")
        print(f"Re = {res['Re']:.0f}")
        print(f"Friction factor f = {res['friction_factor']:.5f}")
    else:
        # Print help summary example
        print("No --flow or --pump_psi supplied. Example usages:")
        print("  Compute pressure drop for 20 L/min in 3/4\" (0.01905 m) line, 10 m long:")
        print("    python coolantHoseCalcs.py --flow 20 --dia 0.01905 --length 10")
        print("  Compute achievable flow with 50 psi pump pressure:")
        print("    python coolantHoseCalcs.py --pump_psi 50 --dia 0.01905 --length 10")
        print("\nAvailable standard fitting keys:", ', '.join(sorted(STANDARD_FITTING_K.keys())))

if __name__ == '__main__':
    main(sys.argv[1:])
