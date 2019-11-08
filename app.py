from flask import Flask, render_template
import numpy as np
import plotly.graph_objects as go
from plotly.offline import plot

app = Flask(__name__)


@app.route("/")
def main_page():
    return render_template("index.html")


@app.route("/graph")
def get_graph():
    np.random.seed(1)
    size = 100
    random_x = np.linspace(0, 1, size)
    random_y0 = np.random.randn(size) + 5
    random_y1 = np.random.randn(size)
    random_y2 = np.random.randn(size) - 5

    # Create traces
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=random_x, y=random_y0,
                             mode='lines',
                             name='lines'))
    fig.add_trace(go.Scatter(x=random_x, y=random_y1,
                             mode='lines+markers',
                             name='lines+markers'))
    fig.add_trace(go.Scatter(x=random_x, y=random_y2,
                             mode='markers', name='markers'))

    return plot(
        fig,
        show_link=False,
        output_type="div",
        include_plotlyjs=False
    )


if __name__ == '__main__':
    app.run()
