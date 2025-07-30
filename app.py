
from flask import Flask, render_template, request, redirect, jsonify
import os
import json
import random

app = Flask(__name__)
DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_used_numbers_for_participant(data, participant):
    used = set()
    for stage in data.values():
        for group in stage.values():
            if participant in group:
                used.add(group[participant])
    return used

def get_next_free_number(data, group_participants, participant):
    used_numbers = set(group_participants.values())
    used_by_person = get_used_numbers_for_participant(data, participant)
    number = 1
    while number in used_numbers or number in used_by_person:
        number += 1
    return number

@app.route("/")
def index():
    data = load_data()
    return render_template("main.html", data=data)

@app.route("/submit", methods=["POST"])
def submit():
    stage = request.form["stage"]
    raw_input = request.form["input"].strip()
    lines = [line.strip() for line in raw_input.split("\n") if line.strip()]

    data = load_data()
    if stage not in data:
        data[stage] = {}

    result = {}
    for line in lines:
        if ":" in line:
            group_name, names_str = line.split(":", 1)
            group_name = group_name.strip()
            names = [n.strip() for n in names_str.split(",") if n.strip()]
        else:
            continue

        if group_name not in data[stage]:
            data[stage][group_name] = {}

        result[group_name] = []
        for name in names:
            number = get_next_free_number(data, data[stage][group_name], name)
            data[stage][group_name][name] = number
            result[group_name].append((name, number))

    save_data(data)
    return render_template("result.html", result=result, stage=stage)

@app.route("/history")
def history():
    data = load_data()
    return render_template("history_full.html", data=data)
