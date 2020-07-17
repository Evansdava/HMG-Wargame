import requests
import os
import sys
import pickle
import redis
# import json
from flask import Flask, render_template, request, redirect, url_for
sys.path.append('./static/scripts/python')
try:
    from map import Map
except ModuleNotFoundError:
    from static.scripts.python.map import Map

# Setting up redis/flask environments
redis = redis.Redis(host='srv-captain--redis', port=6379)

try:
    redis.set("test", 0)
    redis.delete("test")
except:
    redis_url = os.getenv('REDISTOGO_URL',
                          'redis://localhost:6379')
    redis = redis.from_url(redis_url)

app = Flask(__name__)
sys.setrecursionlimit(2000)

# Global variable to track the currently displayed map
# Bad practice perhaps, but a simple way to pass data between routes
current_map = None


@app.route('/')
def index():
    """Return home page for inputting settings"""
    return render_template('home.html')


@app.route('/map')
def show_map():
    """Create and display map based on user-input settings"""
    global current_map
    # Using the uzby api for random names
    r = requests.get("http://uzby.com/api.php", {'min': 3, 'max': 15})

    # The name is random, but the rest is from the main page's form
    name = str(r.content.decode("utf-8"))
    length = request.args.get('length')
    width = request.args.get('width')
    f_chance = request.args.get('f_chance')
    ri_chance = request.args.get('ri_chance')
    ro_chance = request.args.get('ro_chance')
    b_chance = request.args.get('b_chance')
    kingdoms = request.args.get('kingdoms')

    # Default values
    if length == "" or length is None:
        length = 15
    if width == "" or width is None:
        width = 15
    if f_chance == "" or f_chance is None:
        f_chance = 0.20
    if ri_chance == "" or ri_chance is None:
        ri_chance = 0.04
    if ro_chance == "" or ro_chance is None:
        ro_chance = 0.04
    if b_chance == "" or b_chance is None:
        b_chance = 0.30
    if kingdoms == "" or kingdoms is None:
        kingdoms = 4

    # Generating the map and assigning it to the global variable
    current_map = Map(name, length, width, f_chance,
                      ri_chance, ro_chance, b_chance, kingdoms)
    # hexes = pickle.dumps(current_map.hexes)
    hexes = current_map.hexes
    # map_pick = pickle.dumps(current_map)
    # Printing an ascii representation to ensure it generated properly
    print(current_map)
    return render_template('map.html', map=current_map, hexes=hexes)


@app.route('/map/save/<map_name>', methods=["POST"])
def save_map(map_name):
    """Save the current map as a bytestring to the redis database"""
    # The user can rename maps while saving them
    current_map.name = request.form.get("name")

    # Pickle converts the abstract object to bytes so redis can save it
    byte_map = pickle.dumps(current_map)
    redis.set(current_map.name, byte_map)
    return redirect(url_for('view_map', map_name=current_map.name))


@app.route('/map/<map_name>')
def view_map(map_name):
    """View the requested map"""
    global current_map
    # Pickle converts the bytestring back into a Map object for display
    current_map = pickle.loads(redis.get(map_name))
    print(current_map)
    return render_template('show_map.html', map=current_map)


@app.route('/map/delete/<map_name>')
def delete_map(map_name):
    """Delete a map"""
    # Will likely limit this to authenticated users in the future
    redis.delete(map_name)
    return redirect(url_for('index'))


@app.route('/list')
def list_maps():
    """View all saved maps"""
    # Redis docs recommend not returning the entire list of keys, instead
    # scanning small chunks at a time
    iterator = redis.scan_iter()
    name_list = [key.decode("utf-8") for key in iterator]

    # Avoiding duplicates may be necessary if the project scales up very far
    # name_set = set(name_list)

    # Turn each map into an object so that previews can be displayed
    map_list = []
    for name in name_list:
        map_list.append(pickle.loads(redis.get(name)))

    return render_template('map_list.html', maps=map_list)


@app.route('/map/edit/<map_name>', methods=["POST"])
def edit_map(map_name):
    """Edit the name of a map and save it"""
    global current_map
    current_map.name = request.form.get("name")

    # redis.rename() is supposed to implicitly do this, but wasn't working
    redis.set(current_map.name, pickle.dumps(current_map))
    redis.delete(map_name)

    print(current_map.name)
    return redirect(url_for('view_map', map_name=current_map.name))
