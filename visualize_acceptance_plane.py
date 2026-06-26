import numpy as np
import matplotlib.pyplot as plt

def solve_for_epsilon(m, gamma, rt, target_p=0.84):
    """Rearranged Boltzmann equation to find Epsilon for a target P."""
    # Based on: P = 1 / (1 + exp((-2*gamma*m - eps)/rt))
    # log(1/P - 1) = (-2*gamma*m - eps) / rt
    # eps = -rt * log(1/P - 1) - 2*gamma*m
    return -rt * np.log(1/target_p - 1) - (2 * gamma * m)

def plot_equilibrium_manifold():
    # Grid for m and gamma
    m_vals = np.linspace(0.01, 1, 50)
    gamma_vals = np.linspace(1, 10, 50)
    M, G = np.meshgrid(m_vals, gamma_vals)
    
    # Calculate Epsilon for the target P=0.84 at RT=0.5
    RT = 0.75
    Eps = solve_for_epsilon(M, G, RT, target_p=0.84)
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot the isosurface
    surf = ax.plot_surface(M, G, Eps, cmap='magma', alpha=0.9, edgecolor='k', linewidth=0.1)
    
    ax.set_title("Equilibrium Manifold: Parameters for 84% Acceptance")
    ax.set_xlabel('Offer Fraction (m)')
    ax.set_ylabel('Sensitivity (Gamma)')
    ax.set_zlabel('Cooperative Bias (Epsilon)')
    
    fig.colorbar(surf, label='Required Epsilon', shrink=0.5)
    plt.show()

if __name__ == "__main__":
    plot_equilibrium_manifold()