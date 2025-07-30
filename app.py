from flask import Flask, render_template, request
import random
import math

app = Flask(__name__)

SESSIONS = ['Квалификация 1', 'Квалификация 2', 'Гонка 1', 'Гонка 2']

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    final_groups = []
    if request.method == 'POST':
        names = [n.strip() for n in request.form['names'].split('\n') if n.strip()]
        num_groups = int(request.form['num_groups'])
        random.shuffle(names)

        grouped = [[] for _ in range(num_groups)]
        for i, name in enumerate(names):
            grouped[i % num_groups].append(name)

        used_numbers = {name: set() for name in names}

        # Генерация для квалификаций и гонок
        for session in SESSIONS:
            session_result = []
            for group in grouped:
                available_numbers = list(range(1, len(group) + 1))
                random.shuffle(available_numbers)
                session_group = []
                for name in group:
                    possible_numbers = [n for n in range(1, 100) if n not in used_numbers[name]]
                    assigned = possible_numbers[0]
                    used_numbers[name].add(assigned)
                    session_group.append((name, assigned))
                session_result.append(session_group)
            results.append((session, session_result))

        # Формирование финалов (по алфавиту)
        sorted_names = sorted(names)
        final_size = int(math.ceil(len(sorted_names) / num_groups))
        final_groups_raw = [sorted_names[i:i + final_size] for i in range(0, len(sorted_names), final_size)]

        final_result = []
        for i, group in enumerate(final_groups_raw):
            session_group = []
            for name in group:
                possible_numbers = [n for n in range(1, 100) if n not in used_numbers[name]]
                assigned = possible_numbers[0]
                used_numbers[name].add(assigned)
                session_group.append((name, assigned))
            final_result.append(session_group)
        results.append((f'Финалы', final_result))

    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
