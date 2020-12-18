from bokeh.plotting import figure, output_file, show, save, ColumnDataSource
from bokeh.models.tools import HoverTool
from bokeh.transform import factor_cmap
from bokeh.palettes import Blues8
from bokeh.embed import components
from bokeh.models import ColumnDataSource, Grid, Line, LinearAxis, Plot,FactorRange
import pandas as pd

fruits = ['Apples', 'Pears', 'Nectarines', 'Plums', 'Grapes', 'Strawberries']
years = ["2015", "2016", "2017"] #years represent sales
#colors will be given using pallet mentioned below
#fruits will represent years in our case

data = {'fruits' : fruits,
        '2015'   : [2, 1, 4, 3, 2, 4],
        '2016'   : [5, 3, 4, 2, 4, 6],
        '2017'   : [3, 2, 4, 4, 5, 3]}


x = [ (fruit, year) for fruit in fruits for year in years ]
counts = sum(zip(data['2015'], data['2016'], data['2017']), ()) # like an hstack

source = ColumnDataSource(data=dict(x=x, counts=counts))

p = figure(x_range=FactorRange(*x), plot_height=250, title="Fruit Counts by Year",
           toolbar_location=None, tools="")
       # use the palette to colormap based on the the x[1:2] values
p.vbar(x='x', top='counts', width=0.9, source=source, line_color="white",

       fill_color=factor_cmap('x', palette=Blues8, factors=years, start=1, end=2))

#for legend colors

# p = figure(x_range=fruits, y_range=(0, 10), plot_height=250, title="Fruit Counts by Year",
#            toolbar_location=None, tools="")

# p.vbar(x=dodge('fruits', -0.25, range=p.x_range), top='2015', width=0.2, source=source,
#        color="#c9d9d3", legend_label="2015")

# p.vbar(x=dodge('fruits',  0.0,  range=p.x_range), top='2016', width=0.2, source=source,
#        color="#718dbf", legend_label="2016")

# p.vbar(x=dodge('fruits',  0.25, range=p.x_range), top='2017', width=0.2, source=source,
#        color="#e84d60", legend_label="2017")

p.y_range.start = 0
p.x_range.range_padding = 0.1
p.xaxis.major_label_orientation = 1
p.xgrid.grid_line_color = None

show(p)