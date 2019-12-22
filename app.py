import uuid
from dataclasses import dataclass

from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    login_user,
    UserMixin,
    LoginManager,
    login_required,
    current_user,
)
from werkzeug.security import check_password_hash
import numpy as np
from scipy.stats import ks_2samp
import plotly.graph_objects as go
from plotly.offline import plot

app = Flask(__name__)
app.config.from_pyfile("settings")
if app.env == "production":
    app.config.from_envvar("PRODUCTION_SETTINGS")

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)


class Homework(db.Model):
    __tablename__ = "homeworks"

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String)
    reference = db.Column(db.String)


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    homework_id = db.Column(db.Integer, db.ForeignKey("homeworks.id"), nullable=False)
    homework = db.relationship("Homework", lazy=True)

    path = db.Column(db.String)


@dataclass
class KSResult:
    level: float
    dist: float
    p_val: float
    rejected: bool


@app.route("/")
def main_page():
    hws = Homework.query.order_by(Homework.id.desc()).all()
    return render_template("index.html", hws=hws)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(email=username).first()
        # Check if `check_password_hash` and this code are secure
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))

        # Handle login failure


@app.route("/dashboard")
@login_required
def dashboard():
    hws = Homework.query.order_by(Homework.id.desc()).all()
    return render_template("dashboard.html", hws=hws)


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
@login_required
def upload():
    hw_id = request.form["homework"]
    hw = Homework.query.get(hw_id)
    if hw.status != "OPEN":
        abort(500)

    file_ = request.files["file"]
    # TODO: Handle error
    data = np.loadtxt(file_)

    path = f"data/{uuid.uuid4().hex}"
    np.save(path, data)

    submission = (
        Submission.query.filter_by(user_id=current_user.id, homework_id=hw_id)
        .order_by(Submission.id.desc())
        .first()
    )
    if submission:
        # TODO: Delete old submission
        pass

    submission = Submission(user_id=current_user.id, homework_id=hw_id, path=path)
    db.session.add(submission)
    db.session.commit()

    return redirect(url_for("show_result", id_=submission.id))


@app.route("/result/<int:id_>")
@login_required
def show_result(id_):
    submission = Submission.query.filter_by(user_id=current_user.id, id=id_).first()
    if not submission:
        abort(404)

    data = np.load(submission.path + ".npy")

    hw = submission.homework.reference
    reference = np.loadtxt(hw)

    # FIXME: This seems to release the data to the HTML
    trace_reference = go.Histogram(
        x=reference, histnorm="probability", name="Reference"
    )
    trace_result = go.Histogram(x=data, histnorm="probability", name="Your Result")
    fig = go.Figure(data=[trace_reference, trace_result])
    fig.update_layout(barmode="overlay")
    fig.update_traces(opacity=0.3)
    fig_div = plot(fig, show_link=False, output_type="div")

    level = 0.05
    dist, p_val = ks_2samp(data, reference)
    ks_result = KSResult(level=level, dist=dist, p_val=p_val, rejected=p_val < level)

    return render_template("result.html", fig_div=fig_div, ks_result=ks_result)


if __name__ == "__main__":
    app.run()
