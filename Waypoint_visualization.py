import matplotlib.pyplot as plt
import numpy as np

class Waypoint_visualization():
    def __init__(self, x, y) -> None:

        if len(x) > len(y):
            x = x[:len(y)]

        if len(y) > len(x):
            y = y[:len(x)]

        self.x = x
        self.y = y

    def visualize(self, title, xlabel, ylabel):
        fig, ax = plt.subplots()
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        ax.scatter(self.x, self.y)
        plt.show()


    def multiDimensionalVisualize(self, title, xlabel, ylabel, colors=[], labels=[]):
        fig, ax = plt.subplots()
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        for i in range(len(self.x[0])):
            print([el[i] for el in self.x])
            #ax.scatter([el[i] for el in self.x], self.y, colors[i], labels[i])
            ax.scatter([el[i] for el in self.x], self.y)
        # Assume multi dimensional X value
        """for row in self.x:
            if len(colors) != len(row):
                raise Exception("Number of colors provided must match number of dimensions")

            if len(labels) != len(row):
                raise Exception("Number of labels provided must match number of dimensions")
            for index, col in enumerate(row):
                ax.scatter(col, self.y, label=labels[index], c=colors[index])
                """
        #plt.legend()
        plt.show()