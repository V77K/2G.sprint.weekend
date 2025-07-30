
from flask import Flask, render_template, request, redirect, jsonify
import json
import os
import random

app = Flask(__name__)

DATA_FILE = 'data.json'
PARTICIPANT_FILE = 'participants.json'
GROUP_MAP_FILE = 'group_map.json'

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_data(): return load_json(DATA_FILE, {})
def save_data(data): save_json(DATA_FILE, data)
def load_participants(): return load_json(PARTICIPANT_FILE, [])
def save_participants(p): save_json(PARTICIPANT_FILE, p)
def load_group_map(): return load_json(GROUP_MAP_FILE, {})
def save_group_map(m): save_json(GROUP_MAP_FILE, m)

@app.route('/')
def index():
    data = load_data()
    return render_template("index.html", data=data)

@app.route('/print/<stage>')
def print_stage(stage):
    data = load_data()
    stage_data = data.get(stage, {})
    return render_template("print_stage.html", stage=stage, stage_data=stage_data)

@app.route('/participants', methods=['GET', 'POST'])
def participants():
    if request.method == 'POST':
        raw = request.form['participants']
        people = [p.strip() for p in raw.strip().split('\n') if p.strip()]
        save_participants(people)
        return redirect('/participants')
    return render_template("participants.html", participants=load_participants())
