
from flask import Flask, render_template, request, redirect
import json
import os
import random

app = Flask(__name__)
DATA_FILE = 'data.json'
PARTICIPANT_FILE = 'participants.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_participants():
    if not os.path.exists(PARTICIPANT_FILE):
        return []
    with open(PARTICIPANT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_participants(participants):
    with open(PARTICIPANT_FILE, 'w', encoding='utf-8') as f:
        json.dump(participants, f, ensure_ascii=False, indent=2)

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

@app.route('/clear_data')
def clear_data():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    return redirect('/')

@app.route('/clear_participants')
def clear_participants():
    if os.path.exists(PARTICIPANT_FILE):
        os.remove(PARTICIPANT_FILE)
    return redirect('/participants')
