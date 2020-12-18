from bokeh.plotting import figure, output_file, show, save, ColumnDataSource
from bokeh.models.tools import HoverTool
from bokeh.transform import factor_cmap
from bokeh.palettes import Blues8
from bokeh.embed import components
from bokeh.models import ColumnDataSource, Grid, Line, LinearAxis, Plot
import pandas as pd


#import data frames here
x = [1,2,3,4,5,6] #vlaues for x and y axis

y = [2,5,8,9,6,4]

source = ColumnDataSource(dict(x=x, y=y))

plot = figure(
    title = 'line plot', #title for line chart
    x_axis_label  = 'X label', 
    y_axis_label = 'Y label',
    plot_width=500, plot_height=400,
)
glyph = Line(x="x", y="y", line_color="#f46d43", line_width=6, line_alpha=0.6)

# plot.multi_line([[1, 3, 2], [3, 4, 6, 6]], [[2, 1, 4], [4, 7, 8, 5]],
#              color=["firebrick", "navy"], alpha=[0.8, 0.3], line_width=4)
# plot.line(x,y, legend= 'Test',line_width = 2,line_color="#f46d43") can plot with this too

plot.add_glyph(source, glyph)

show(plot)


