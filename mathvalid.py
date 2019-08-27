import matplotlib.pyplot as plt
import numpy as np

def hyperbolicDistanceMaping(array):
    y = np.cosh(array / 0.4)
    return np.sqrt(0.2 - 0.2 / (y * y))

if __name__ == '__main__':
    x = np.arange(1000)
    x = x / 500.0
    y = hyperbolicDistanceMaping(x)
    plt.scatter(x, y)
    plt.show()