from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource
from bokeh.transform import factor_cmap
from flask import Flask, render_template, request
from bokeh.io import show
from bokeh.util.string import encode_utf8

import requests


app = Flask(__name__)

def get_data_from_api(brand):
    response = requests.get('http://127.0.0.1:5000/' + brand)
    return response.json()

@app.route("/")
def index():
    total = 1
    positive = 0
    neutral = 0
    negative = 0
    sentiments = ["Positive", "Neutral", "Negative"]
    distribution = [positive, neutral, negative]
    source = ColumnDataSource(data=dict(sentiments=sentiments, distribution=distribution))

    p = figure(x_range=sentiments, plot_height=550, plot_width=1000, title="Sentiment distribution",
               x_axis_label='Sentiments')
    p.vbar(x='sentiments', top='distribution', width=0.7, source=source, legend_field="sentiments",
           line_color=None,
           fill_color=factor_cmap('sentiments', palette=['#39DA00', '#FDB229', '#FF0445'], factors=sentiments))

    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.legend.orientation = "horizontal"
    p.legend.location = "top_right"
    p.background_fill_color = "#0B0022"

    script, div = components(p)

    pos = round((float(positive) / float(total)) * 100, 1)
    neu = round((float(neutral) / float(total)) * 100, 1)
    neg = round((float(negative) / float(total)) * 100, 1)
    print(pos)
    print(neu)
    print(neg)

    html = render_template("chart.html",
                           the_div=div,
                           the_script=script,
                           positive=pos,
                           neutral=neu,
                           negative=neg)
    return encode_utf8(html)

@app.route("/", methods=['POST'])
def chart():
    brand = request.form['brand']
    response = get_data_from_api(brand=brand)
    # print(response)
    total = response['number_of_tweets']
    positive = response['positive']
    neutral = response['neutral']
    negative = response['negative']
    sentiments = ["Positive", "Neutral", "Negative"]
    distribution = [positive, neutral, negative]
    source = ColumnDataSource(data=dict(sentiments=sentiments, distribution=distribution))

    p = figure(x_range=sentiments, plot_height=550, plot_width= 1000, title="Sentiment distribution", x_axis_label = 'Sentiments')
    p.vbar(x='sentiments', top='distribution', width=0.9, source=source, legend_field="sentiments",
           line_color=None, fill_color=factor_cmap('sentiments', palette=['#39DA00', '#FDB229', '#FF0445'], factors=sentiments))

    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.legend.orientation = "horizontal"
    p.legend.location = "top_right"
    p.background_fill_color = "#0B0022"

    script, div = components(p)

    pos = round((float(positive)/float(total))*100, 1)
    neu = round((float(neutral)/float(total))*100, 1)
    neg = round((float(negative) / float(total)) * 100, 1)
    print(pos)
    print(neu)
    print(neg)

    html = render_template("chart.html",
                           the_div=div,
                           the_script=script,
                           positive=pos,
                           neutral=neu,
                           negative=neg)
    return encode_utf8(html)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
