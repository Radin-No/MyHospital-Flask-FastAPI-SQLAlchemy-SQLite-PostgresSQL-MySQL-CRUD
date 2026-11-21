from flask import Flask, render_template, redirect, request, url_for, abort
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, StatementError
from models import engine, MODEL_MAP

app = Flask(__name__)

def get_table(table):
    if table not in MODEL_MAP:
        abort(404)
    return MODEL_MAP[table]

def get_record(conn, model, id):
    record = conn.execute(select(model).where(model.c.id == id)).mappings().first()
    if record is None:
        abort(404)
    return record

def form_data(model):
    data = {}
    for col in model.columns:
        if col.name != "id":
            try:
                data[col.name] = col.type.python_type(request.form[col.name])
            except (ValueError, KeyError):
                abort(400, "Invalid or missing field: " + col.name)
    return data

@app.route('/')
@app.route('/<string:table>')
def index(table='doctors'):
    model = get_table(table)
    with engine.connect() as conn:
        records = conn.execute(select(model).order_by(model.c.id.desc())).mappings().all()
    return render_template('index.html', records=records, table=table, tables=MODEL_MAP.keys())

@app.route('/details/<string:table>/<int:id>')
def details(table, id):
    model = get_table(table)
    with engine.connect() as conn:
        record = get_record(conn, model, id)
    return render_template('details.html', record=record, table=table, tables=MODEL_MAP.keys())

@app.route('/delete/<string:table>/<int:id>')
def delete(table, id):
    model = get_table(table)
    with engine.begin() as conn:
        get_record(conn, model, id)
        conn.execute(model.delete().where(model.c.id == id))
    return redirect(url_for('index', table=table))

@app.route('/create/<string:table>', methods=['GET', 'POST'])
def create(table):
    model = get_table(table)
    if request.method == 'POST':
        try:
            with engine.begin() as conn:
                conn.execute(model.insert().values(**form_data(model)))
        except (IntegrityError, StatementError):
            abort(400, 'Invalid record')
        return redirect(url_for('index', table=table))
    return render_template('create.html', table=table, tables=MODEL_MAP.keys())

@app.route('/update/<string:table>/<int:id>', methods=['GET', 'POST'])
def update(table, id):
    model = get_table(table)
    with engine.begin() as conn:
        record = get_record(conn, model, id)
        if request.method == 'POST':
            try:
                conn.execute(model.update().where(model.c.id == id).values(**form_data(model)))
            except (IntegrityError, StatementError):
                abort(400, 'Invalid record')
            return redirect(url_for('index', table=table))
    return render_template('update.html', record=record, table=table, tables=MODEL_MAP.keys())

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5005)
