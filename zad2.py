# @author = Krystian Krakowski

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sys
import matplotlib.transforms as tran


# Main class of all figures
class Figure:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def x(self):
        return self.x

    def y(self):
        return self.y

    def color(self):
        return self.color


# Class of point
class Point(Figure):
    def __init__(self, x, y, color):
        Figure.__init__(self, x, y, color)


# Class of polygon
class Polygon(Figure):
    def __init__(self, color, points):
        Figure.__init__(self, None, None, color)
        self.points = points

    def points(self):
        return self.points


# Class of rectangle.
class Rectangle(Figure):
    def __init__(self, x, y, color, width, height):
        Figure.__init__(self, x, y, color)
        self.width = width
        self.height = height

    def width(self):
        return self.width

    def height(self):
        return self.height


# Class of square
class Square(Figure):
    def __init__(self, x, y, color, size):
        Figure.__init__(self, x, y, color)
        self.size = size

    def size(self):
        return self.size


# Class of circle
class Circle(Figure):
    def __init__(self, x, y, color, radius):
        Figure.__init__(self, x, y, color)
        self.radius = radius

    def radius(self):
        return self.radius


# Function to load file with data. Return screen, palette and arrays of figures
def load(name):
    options = json.loads(open(name, "r+").read())  # Read data with json parser

    figures = options["Figures"]
    screen = options["Screen"]
    palette = options["Palette"]

    points = []
    squares = []
    rectangles = []
    polygons = []
    circles = []

    for i in figures:
        if (i["type"] == "point"):
            points.append(i)
        elif (i["type"] == "square"):
            squares.append(i)
        elif (i["type"] == "rectangle"):
            rectangles.append(i)
        elif (i["type"] == "polygon"):
            polygons.append(i)
        elif (i["type"] == "circle"):
            circles.append(i)

    return screen, palette, points, squares, rectangles, polygons, circles


# Class of screen
class Screen:
    def __init__(self, width, height, bg_color, fg_color):
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.fg_color = fg_color

    def width(self):
        return self.width

    def height(self):
        return self.height

    def bg_color(self):
        return self.bg_color

    def fg_color(self):
        return self.fg_color


# Function to edit color into one format, in this case to hex form (string)
def colorEditor(color, palette):
    if color[0] != "#":  # If color is not hex form
        if (color[0] == "("):  # If color is (?,?,?) form
            colors = list(map(hex, map(int, color[1:-1].split(","))))
            return "#" + colors[0][2:] + colors[1][2:] + colors[2][2:]
        else:  # If color is from palette
            return colorEditor(palette[color], palette)
    else:  # If color is hex form
        return color


# Function to initialize all data. Return class screen and also array of figures
def initialize(screen, palette, points, squares, rectangles, polygons, circles):
    myscreen = Screen(int(screen["width"]), int(screen["height"]), colorEditor(screen["bg_color"], palette),
                      colorEditor(screen["fg_color"], palette))
    myfigures = []

    for i in points:
        a = Point(int(i["x"]), int(i["y"]), colorEditor(screen["fg_color"], palette))
        myfigures.append(a)

    for i in squares:
        a = Square(int(i["x"]), int(i["y"]),
                   colorEditor(i.get("color", colorEditor(screen["fg_color"], palette)), palette), int(i["size"]))
        myfigures.append(a)

    for i in rectangles:
        a = Rectangle(int(i["x"]), int(i["y"]),
                      colorEditor(i.get("color", colorEditor(screen["fg_color"], palette)), palette), int(i["width"]),
                      int(i["height"]))
        myfigures.append(a)

    for i in polygons:
        a = Polygon(colorEditor(i.get("color", colorEditor(screen["fg_color"], palette)), palette), list(i["points"]))
        myfigures.append(a)

    for i in circles:
        a = Circle(int(i["x"]), int(i["y"]),
                   colorEditor(i.get("color", colorEditor(screen["fg_color"], palette)), palette), int(i["radius"]))
        myfigures.append(a)

    return myscreen, myfigures


# Function to draw all figures, screen and save to file
def draw(screen, figures, path, mydpi):
    fig, ax = plt.subplots()

    ax.set_xlim((0, screen.width))  # Set width of screen
    ax.set_ylim((0, screen.height))  # Set height of screen

    ax.axes.get_xaxis().set_visible(False)  # Set xaxis invisible
    ax.axes.get_yaxis().set_visible(False)  # Set yaxis invisible

    ax.spines['top'].set_visible(False)  # Set top invisible
    ax.spines['right'].set_visible(False)  # Set right invisible
    ax.spines['bottom'].set_visible(False)  # Set bottom invisible
    ax.spines['left'].set_visible(False)  # Set left invisible

    ax.set_facecolor(screen.bg_color)  # Set background color

    for i in figures:
        if isinstance(i, Polygon):
            ax.add_artist(plt.Polygon(i.points, True, color=i.color))
        elif isinstance(i, Rectangle):
            ax.add_artist(plt.Rectangle([i.x, i.y], i.width, i.height, color=i.color))
        elif isinstance(i, Square):
            ax.add_artist(plt.Rectangle([i.x, i.y], i.size, i.size, color=i.color))
        elif isinstance(i, Circle):
            ax.add_artist(plt.Circle([i.x, i.y], i.radius, color=i.color))
        else:
            ax.add_artist(plt.Rectangle([i.x, i.y], 1, 1, color=i.color))

    if path is not None:  # Save to file if path exist
        fig.set_size_inches(screen.width / float(fig.get_dpi()),
                            screen.height / float(fig.get_dpi()))  # Set size of fig to original size
        fig.subplots_adjust(
            bottom=0)  # In fig erase "white-spaces", "white board" (Problem with saving image with white frame)
        fig.subplots_adjust(top=1)
        fig.subplots_adjust(right=1)
        fig.subplots_adjust(left=0)
        fig.savefig(path, dpi=fig.get_dpi() * mydpi)  # Save file

    plt.show()  # Show figures on the background


# Main function which parse argument from the command line
# (first argument is path to data, next with "-o" is path to save image)
# mydpi is optional and can be increased to better quality of image
def main(mydpi=1):
    if (len(sys.argv) == 1):
        print("Blad argumentow")
        return

    args = sys.argv
    name = args[1]
    screen, palette, points, squares, rectangles, polygons, circles = load(name)
    screen, figures = initialize(screen, palette, points, squares, rectangles, polygons, circles)

    index = 0
    newpath = None
    for i in args:
        if i == "-o":
            newpath = args[index+1]
        elif i== "-d":
            mydpi = int(args[index+1])
        index += 1

    draw(screen, figures, newpath, mydpi)


if __name__ == "__main__":
    main()
