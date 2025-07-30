
from flask import Flask, render_template, request, redirect
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

@app.route('/participants', methods=['GET', 'POST'])
def participants():
    if request.method == 'POST':
        raw = request.form['participants']
        people = [p.strip() for p in raw.strip().split('\n') if p.strip()]
        save_participants(people)
        return redirect('/participants')
    return render_template("participants.html", participants=load_participants())

@app.route('/create_stage', methods=['GET', 'POST'])
def create_stage():
    if request.method == 'POST':
        stage = request.form['stage']
        data = load_data()
        if stage not in data:
            data[stage] = {}
            save_data(data)
        return redirect('/')
    return render_template('create_stage.html')

@app.route('/auto_assign', methods=['GET', 'POST'])
def auto_assign():
    participants = load_participants()
    group_map = load_group_map()
    if request.method == 'POST':
        stage = request.form['stage']
        group_letters = request.form.getlist('group_letters')
        num_groups = len(group_letters)

        names = participants
        data = load_data()
        if stage not in data:
            data[stage] = {}

        assigned = {name: group_map.get(name) for name in names}
        unassigned = [n for n in names if not assigned[n]]
        random.shuffle(unassigned)

        for i, name in enumerate(unassigned):
            group = f'Group {group_letters[i % num_groups]}'
            group_map[name] = group
            assigned[name] = group

        save_group_map(group_map)

        groups = {f'Group {letter}': [] for letter in group_letters}
        for name, group in assigned.items():
            groups[group].append(name)

        for gname, members in groups.items():
            if gname not in data[stage]:
                data[stage][gname] = {}
            numbers = list(range(1, len(members) + 1))
            random.shuffle(numbers)
            for m, num in zip(members, numbers):
                data[stage][gname][m] = num

        save_data(data)
        return redirect('/')
    return render_template("auto_assign.html", stages=load_data().keys())

@app.route('/manual_assign', methods=['GET', 'POST'])
def manual_assign():
    participants = load_participants()
    if request.method == 'POST':
        stage = request.form['stage']
        group = request.form['group']
        selected = request.form.getlist('participants')

        data = load_data()
        if stage not in data:
            data[stage] = {}
        if group not in data[stage]:
            data[stage][group] = {}

        numbers = list(range(1, len(selected) + 1))
        random.shuffle(numbers)

        for p, num in zip(selected, numbers):
            data[stage][group][p] = num

        save_data(data)
        return render_template("manual_result.html", results=zip(selected, numbers), stage=stage, group=group, participants=participants, stages=load_data().keys())
    return render_template("manual_assign.html", participants=participants, stages=load_data().keys())

@app.route('/print/<stage>')
def print_stage(stage):
    data = load_data()
    stage_data = data.get(stage, {})
    return render_template("print_stage.html", stage=stage, stage_data=stage_data)
