
from flask import Flask, render_template, request, redirect
import json
import os
import random

app = Flask(__name__)
DATA_FILE = 'data.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
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

@app.route('/')
def index():
    data = load_data()
    return render_template('index.html', stages=data.keys())

@app.route('/create_stage', methods=['GET', 'POST'])
def create_stage():
    if request.method == 'POST':
        stage_name = request.form['stage']
        data = load_data()
        if stage_name not in data:
            data[stage_name] = {}
            save_data(data)
        return redirect('/')
    return render_template('create_stage.html')

@app.route('/auto_assign', methods=['GET', 'POST'])
def auto_assign():
    if request.method == 'POST':
        stage = request.form['stage']
        group_count = int(request.form['groups'])
        names = request.form['names'].strip().split('\n')
        random.shuffle(names)

        data = load_data()
        if stage not in data:
            data[stage] = {}

        groups = {f'Group {chr(65+i)}': [] for i in range(group_count)}
        for i, name in enumerate(names):
            group_name = f'Group {chr(65 + (i % group_count))}'
            groups[group_name].append(name)

        for group_name, participants in groups.items():
            if group_name not in data[stage]:
                data[stage][group_name] = {}
            for participant in participants:
                number = get_next_free_number(data, data[stage][group_name], participant)
                data[stage][group_name][participant] = number

        save_data(data)
        return redirect('/')
    data = load_data()
    return render_template('auto_assign.html', stages=data.keys())

@app.route('/manual_assign', methods=['GET', 'POST'])
def manual_assign():
    if request.method == 'POST':
        stage = request.form['stage']
        group = request.form['group']
        participant = request.form['participant']

        data = load_data()
        if stage not in data:
            data[stage] = {}
        if group not in data[stage]:
            data[stage][group] = {}

        number = get_next_free_number(data, data[stage][group], participant)
        data[stage][group][participant] = number

        save_data(data)
        return redirect('/')
    data = load_data()
    return render_template('manual_assign.html', stages=data.keys())

@app.route('/history')
def history():
    data = load_data()
    return render_template('history.html', data=data)
