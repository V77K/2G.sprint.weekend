
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

def load_data():
    return load_json(DATA_FILE, {})

def save_data(data):
    save_json(DATA_FILE, data)

def load_participants():
    return load_json(PARTICIPANT_FILE, [])

def save_participants(participants):
    save_json(PARTICIPANT_FILE, participants)

def load_group_map():
    return load_json(GROUP_MAP_FILE, {})

def save_group_map(mapping):
    save_json(GROUP_MAP_FILE, mapping)

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
    return render_template('index.html', data=data)

@app.route('/participants', methods=['GET', 'POST'])
def participants():
    if request.method == 'POST':
        raw = request.form['participants']
        participants = [p.strip() for p in raw.strip().split('\n') if p.strip()]
        save_participants(participants)
        return redirect('/')
    current = load_participants()
    return render_template('participants.html', participants=current)

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
    participants_list = load_participants()
    group_map = load_group_map()
    if request.method == 'POST':
        stage = request.form['stage']
        group_names_raw = request.form['group_names'].strip()
        group_count = 0
        if group_names_raw:
            group_names = [g.strip() for g in group_names_raw.split(',') if g.strip()]
            group_count = len(group_names)
        else:
            group_count = int(request.form['groups'])
            group_names = [f'Group {chr(65+i)}' for i in range(group_count)]

        if 'use_global' in request.form:
            names = participants_list
        else:
            names = request.form['names'].strip().split('\n')

        data = load_data()
        if stage not in data:
            data[stage] = {}

        assigned_groups = {name: group_map.get(name) for name in names}
        unassigned = [name for name, grp in assigned_groups.items() if not grp]
        random.shuffle(unassigned)

        for i, name in enumerate(unassigned):
            group = group_names[i % group_count]
            group_map[name] = group
            assigned_groups[name] = group

        save_group_map(group_map)

        # Преобразование в {group: [participants]}
        groupings = {g: [] for g in group_names}
        for name, group in assigned_groups.items():
            groupings[group].append(name)

        for group_name, participants in groupings.items():
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
    participants_list = load_participants()
    if request.method == 'POST':
        stage = request.form['stage']
        group = request.form['group']
        selected = request.form.getlist('participants')

        data = load_data()
        if stage not in data:
            data[stage] = {}
        if group not in data[stage]:
            data[stage][group] = {}

        for participant in selected:
            number = get_next_free_number(data, data[stage][group], participant)
            data[stage][group][participant] = number

        save_data(data)
        return redirect('/')
    data = load_data()
    return render_template('manual_assign.html', stages=data.keys(), participants=participants_list)
