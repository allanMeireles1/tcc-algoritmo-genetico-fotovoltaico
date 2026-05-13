
import matplotlib.pyplot as plt


def plot_convergence(history, title):

    plt.figure(figsize=(8, 4))

    plt.plot(history)

    plt.title(title)
    plt.xlabel("Generation")
    plt.ylabel("Fitness")

    plt.grid(True)

    plt.tight_layout()

    plt.show()
