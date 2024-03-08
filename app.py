from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import sqlite3
from random import randint

app = Flask(__name__)
app.secret_key = 'your_secret_key' # Required for session management

DATABASE = 'highscores.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db_connection()
    db.execute('''
        CREATE TABLE IF NOT EXISTS high_scores (
            id INTEGER PRIMARY KEY, 
            name TEXT, 
            score INTEGER
        )
    ''')
    db.commit()
    db.close()

# Manually pushing the application context
with app.app_context():
    init_db()

def add_score(name, score):
    conn = get_db_connection()
    conn.execute('INSERT INTO high_scores (name, score) VALUES (?, ?)', (name, score))
    conn.commit()
    conn.close()

def get_high_scores(limit=10):
    conn = get_db_connection()
    scores = conn.execute('SELECT name, score FROM high_scores ORDER BY score DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    return scores

@app.route('/add_score', methods=['POST'])
def add_score_route():
    score_data = request.json
    add_score(score_data['name'], score_data['score'])
    return jsonify({'message': 'Score added successfully!'}), 201

@app.route('/high_scores', methods=['GET'])
def get_high_scores_route():
    scores = get_high_scores()
    return jsonify([{'name': row['name'], 'score': row['score']} for row in scores])


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/snake')
def snake():
    return render_template('snake.html')

@app.route('/hilo')
def hilo():
    # Initialize points to 100 if it's not already in the session
    if 'hilo_points' not in session:
        session['hilo_points'] = 100

    # Retrieve points from session
    points = session['hilo_points']

    if 'hilo_errors' not in session:
        session['hilo_errors'] = 3

    errors = session['hilo_errors']
    if errors == 0:
        final_points = session['hilo_points']
        session['hilo_points'] = 100 # reset game points
        session['hilo_errors'] = 3 # reset errors
        top_scores = get_high_scores()
        return render_template('hilo_gameover.html',
                               points = final_points,
                               top_scores = top_scores)

    while True:
        number_first = randint(1,10)
        number_second = randint(1,10)
        if number_first != number_second:
            break

    return render_template('hilo.html',
                           points=points,
                           errors = errors,
                           number_first = number_first,
                           number_second = number_second)


@app.route('/hilo_guess', methods=['POST'])
def hilo_guess():
    number_first = int(request.form.get('number_first'))
    number_second = int(request.form.get('number_second'))
    guess = request.form.get('guess')
    points = int(request.form.get('points'))

    # Update points and determine result based on the guess
    if guess == 'Higher' and number_second > number_first:
        result = 'correct'
        session['hilo_points'] += 50
    elif guess == 'Lower' and number_second < number_first:
        result = 'correct'
        session['hilo_points'] += 50
    else:
        result = 'incorrect'
        session['hilo_points'] -= 50
        session['hilo_errors'] -= 1

    return render_template('hilo_result.html',
                           number_first = number_first,
                           number_second = number_second,
                           result = result)


@app.route("/guppies")
def guppies():
    # Initialize points to 100 if it's not already in the session
    if 'vbucks' not in session:
        session['vbucks'] = 100

    # Retrieve points from session
    cur = session['vbucks']

    #if 'vbucks' not in session:
    #   session['vbucks'] = 3

    #errors = session['hilo_errors']
    if cur <= 1:
        final_cur = session['vbucks']
        session['vbucks'] = 100  # reset game points
        #top_scores = get_high_scores()
        return render_template('guppies_over.html',
                               cur=final_cur)

    while True:
        first_num = randint(1, 10)
        second_num = randint(1, 10)
        if first_num != second_num:
            break

    return render_template('guppies.html',
                           cur=cur,
                           first_num=first_num,
                           second_num=second_num)
                           #top_scores=top_scores)


@app.route('/guppies_guess', methods=['POST'])
def guppies_guess():

    number_first = int(request.form.get('first_num'))
    number_second = int(request.form.get('second_num'))
    #num_guess = int(request.form.get('num_guess'))
    bet = int(request.form.get('bet'))
    cur = int(request.form.get('cur'))

    # Update points and determine result based on the guess
    if bet <= cur:
        if number_second > number_first:
            result = 'correct'
            session['vbucks'] += bet
        elif number_second < number_first:
            result = 'incorrect'
            session['vbucks'] -= bet
        else:
            result = 'incorrect'
            session['vbucks'] -= bet
    else:
        return render_template('not_possible.html')

    return render_template('guppies_result.html',
                           number_first=number_first,
                           number_second=number_second,
                           result=result,
                           bet=bet,
                           cur=cur)


if __name__ == '__main__':
    app.run(debug=True)
