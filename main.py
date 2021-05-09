import pandas as pd

from os.path import dirname, join   # Used to get description.html

from bokeh.io import curdoc # Updating document
from bokeh.layouts import column, row   # Used for layout
from bokeh.transform import linear_cmap # Used for color mapping
from bokeh.plotting import figure
from bokeh.palettes import Spectral6
from bokeh.models import ColumnDataSource, Select, Div, Slider, TextInput
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn

# Description of our visualization
description = Div(text=open(join(dirname(__file__), "description.html")).read(), sizing_mode="stretch_width")

# Import dataset into pandas dataframe
movies = pd.read_csv('imdb_movie_metadata.csv', encoding="utf8")    # Read data into dataframe
movies.dropna(inplace=True)  # Drop rows with missing attributes
movies.drop_duplicates(inplace=True) # Remove duplicates
movies.reset_index(drop=True ,inplace=True)  # Reset index
movies.sort_index(axis=1, inplace=True)  #Sort by name

# Create ColumnDataSource to be used for plotting
source = ColumnDataSource(data=dict(x=[], y=[], title=[], year=[]))

# Create axis map dictionary
axis_map = {
    "IMDb score": "imdb_score",
    "Year": "title_year",
    "Duration (minutes)": "duration",
    "Budget (USD)": "budget",
    "Gross earning (USD)": "gross"
}

# Returns list of unique values and adds "All"
def get_unique_list(dataframe_column):
    unique_list = sorted(list(dataframe_column.unique()))
    unique_list.insert(0, "All")
    return unique_list

# Returns list of unique genres after splitting and adds "All"
def get_unique_genres(dataframe_column):
    df_list = list(dataframe_column)
    return_list = list()
    for element in df_list:
        return_list.append(element.split("|"))  # Split each element
    return_list = [values for sublist in return_list for values in sublist] # Flatten list
    return_list = sorted(list(set(return_list)))    # Create unique sorted list
    return_list.insert(0, "All")
    return return_list

# Create input controls
language = Select(title='Languages', value='All', options=get_unique_list(movies['language']))
country = Select(title='Countries', value='All', options=get_unique_list(movies['country']))
genre = Select(title='Genre', value='All', options=get_unique_genres(movies['genres']))
color = Select(title='Color', value='All', options=get_unique_list(movies['color']))
contentRating = Select(title='Content rating', value='All', options=get_unique_list(movies['content_rating']))

# Create axis controls
x_axis = Select(title="X-Axis", options=list(axis_map.keys()), value="Year")
y_axis = Select(title="Y-Axis", options=list(axis_map.keys()), value="IMDb score")

# TODO: update when selecting new y
# Tooltips shown when hover over point 
TOOLTIPS = [
    ("Title", "@title"),
    ("Year", "@year")
]

# Color mapper
mapper = linear_cmap(field_name='y', palette=Spectral6, low=min(movies['imdb_score'].tolist()), high=max(movies['imdb_score'].tolist()))

# Creating plot figure
plot_figure = figure(height=500, width=600, title="", toolbar_location=None, tooltips=TOOLTIPS, sizing_mode="scale_both")
plot_figure.circle(x="x", y="y", source=source, size=6, color=mapper, line_color=mapper)

# Selects movies based on inputs
def select_movies():
    language_value = language.value
    country_value = country.value
    color_value = color.value
    genre_value = genre.value
    contentRating_value = contentRating.value
    
    # Selected movies
    selected = movies

    # Filter based on select widget
    if (language_value != "All"):
        selected = selected[selected['language'].str.contains(language_value)==True]
    if (country_value != "All"):
        selected = selected[selected['country'].str.contains(country_value)==True]
    if (color_value != "All"):
        selected = selected[selected['color'].str.contains(color_value)==True]
    if (genre_value != "All"):
        selected = selected[selected['genres'].str.contains(genre_value)==True]
    if (contentRating_value != "All"):
        selected = selected[selected['content_rating'].str.contains(contentRating_value)==True]

    return selected

# Updates plot based on new selectiong
def update():
    selected_movies = select_movies()
    x_name = axis_map[x_axis.value]
    y_name = axis_map[y_axis.value]

    plot_figure.xaxis.axis_label = x_axis.value
    plot_figure.yaxis.axis_label = y_axis.value
    plot_figure.title.text = "%d movies selected" % len(selected_movies)

    source.data = dict(
        x = selected_movies[x_name],
        y = selected_movies[y_name],
        title = selected_movies['movie_title'],
        year = selected_movies['title_year']
    )

# When any control input changes, update plot
controls = [language, country, genre, color, contentRating, x_axis, y_axis]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

# Create input layout
inputs = column(*controls, width=320)

# Create layout
layout = column(description, row(inputs, plot_figure), sizing_mode="scale_both")

# Initial load of data
update()

curdoc().add_root(layout)
curdoc().title = "Movies"