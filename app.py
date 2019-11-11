from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import plotly.graph_objects as go
from plotly.offline import plot

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data/data.db"
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)


@app.route("/")
def main_page():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


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
    fig.add_trace(go.Scatter(x=random_x, y=random_y0, mode="lines", name="lines"))
    fig.add_trace(
        go.Scatter(x=random_x, y=random_y1, mode="lines+markers", name="lines+markers")
    )
    fig.add_trace(go.Scatter(x=random_x, y=random_y2, mode="markers", name="markers"))

    return plot(fig, show_link=False, output_type="div", include_plotlyjs=False)


@app.route("/upload", methods=["POST"])
def upload():
    file_ = request.files["file"]
    # TODO: Handle error
    data = np.loadtxt(file_)

    reference = np.random.randn(10000)
    fig = go.Figure(
        data=[
            go.Histogram(x=reference, histnorm="probability"),
            go.Histogram(x=data, histnorm="probability"),
        ]
    )

    return plot(fig, show_link=False, output_type="div")


if __name__ == "__main__":
    app.run()
