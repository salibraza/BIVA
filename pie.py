from math import pi
import pandas as pd
from bokeh.palettes import Category20c
from bokeh.transform import cumsum
from bokeh.plotting import figure,show

x = { 'United States': 157, 'United Kingdom': 93, 'Japan': 89, 'China': 63,
      'Germany': 44, 'India': 42, 'Italy': 40, 'Australia': 35, 'Brazil': 32,
      'France': 31, 'Taiwan': 31, 'Spain': 29 }

data = pd.Series(x).reset_index(name='value').rename(columns={'index':'country'})
data['color'] = Category20c[len(x)]



# represent each value as an angle = value / total * 2pi
data['angle'] = data['value']/data['value'].sum() * 2*pi

total=data['value'].sum()

percentage=[]

for val in data['value']:
    per=val/total*100
    val=round(per)
    percentage.append(val)

data['percentage']=percentage



p = figure(plot_height=350, title="Pie Chart", toolbar_location=None,
           tools="hover", tooltips="@country: @value: @percentage%")

p.wedge(x=0, y=1, radius=0.4, 
        
        # use cumsum to cumulatively sum the values for start and end angles
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend_field='country', source=data)

p.axis.axis_label=None
p.axis.visible=False
p.grid.grid_line_color = None


show(p)