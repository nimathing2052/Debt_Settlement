# algorithm_complexity.py
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def generate_complexity_plots():
    n = np.linspace(1, 100, 100)
    time_complexity = n**2  # O(n^2)
    space_complexity = n    # O(n)

    fig, ax = plt.subplots()
    ax.plot(n, time_complexity, label='Time Complexity O(n^2)')
    ax.plot(n, space_complexity, label='Space Complexity O(n)')
    ax.legend()
    plt.grid(True)

    # Save the 2D plot
    plt.savefig('app/static/complexity_plot_2d.png')
    plt.close(fig)

    # Create and save a 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(n, time_complexity, zs=0, zdir='z', label='Time Complexity O(n^2)', color='b')
    ax.plot(n, space_complexity, zs=0, zdir='z', label='Space Complexity O(n)', color='r')
    ax.set_xlabel('Number of Participants/Transactions (n)')
    ax.set_ylabel('Complexity')
    ax.set_zlabel('Magnitude')
    ax.legend()
    plt.savefig('app/static/complexity_plot_3d.png')
    plt.close(fig)

    return 'complexity_plot_2d.png', 'complexity_plot_3d.png'
