import json
import os
from datetime import datetime

import boto3
import dateparser
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
app.config.update(SECRET_KEY=os.environ.get("FLASK_SECRET_KEY"))

TEE_TIME_FORMAT = "%a, %b %d @ %I:%M%p"

AWS_LAMBDA = boto3.client("lambda")
GET_COURSES_LAMBDA_NAME = os.environ["GET_COURSES_LAMBDA_NAME"]
GET_TEE_TIMES_LAMBDA_NAME = os.environ["GET_TEE_TIMES_LAMBDA_NAME"]


class LambdaError(Exception):
    pass


def invoke_lambda(lambda_name, payload={}):
    resp = AWS_LAMBDA.invoke(FunctionName=lambda_name, Payload=json.dumps(payload))
    if resp["StatusCode"] != 200:
        raise LambdaError(lambda_name)
    return json.loads(resp["Payload"].read().decode("utf8"))


def get_courses():
    return invoke_lambda(GET_COURSES_LAMBDA_NAME)


def get_tee_times(earliest_time, latest_time, days_ahead, courses):
    return json.loads(
        invoke_lambda(
            GET_TEE_TIMES_LAMBDA_NAME,
            {
                "earliestTime": earliest_time,
                "latestTime": latest_time,
                "daysAhead": days_ahead,
                "courses": courses,
            },
        )["body"]
    )


def format_response(resp):
    return {
        course: list(
            map(
                lambda dt: datetime.strftime(dt, TEE_TIME_FORMAT),
                sorted(map(dateparser.parse, time_list)),
            )
        )
        for course, time_list in resp.items()
    }


@app.route("/tee_times", methods=["POST"])
def tee_times():
    earliest_time = request.form.get("earliest_time")
    latest_time = request.form.get("latest_time")
    days_ahead = request.form.get("days_ahead")
    courses = request.form.getlist("courses[]")
    return jsonify(format_response(get_tee_times(earliest_time, latest_time, days_ahead, courses)))


@app.route("/", methods=["GET"])
def index():
    data = {"courses": get_courses()}
    return render_template("index.html", data=data)
