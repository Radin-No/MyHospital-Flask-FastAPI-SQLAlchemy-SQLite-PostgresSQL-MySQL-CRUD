from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, StatementError
from models import engine, MODEL_MAP

app = FastAPI(title="Hospital Management Test System")

class DoctorData(BaseModel):
    name: str
    specialty: str

class PatientData(BaseModel):
    name: str
    illness: str

class PharmaData(BaseModel):
    name: str
    location: str

class MedData(BaseModel):
    pharr_id: int
    name: str
    is_pill: int
    stock: int
    price: float

class PrescriptionData(BaseModel):
    doc_id: int
    pat_id: int
    phar_id: int
    date: str
    is_done: int

class ItemData(BaseModel):
    prescr_id: int
    med_id: int
    cons_instr: str

SCHEMAS = {"doctors": DoctorData, "patients": PatientData, "contract_pharma": PharmaData,
           "meds": MedData, "prescription": PrescriptionData, "prescription_items": ItemData}

def get_table(table):
    if table not in MODEL_MAP:
        raise HTTPException(status_code=404, detail="Table not found")
    return MODEL_MAP[table]

def values(table, data):
    try:
        return SCHEMAS[table](**data).model_dump()
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors(include_url=False, include_context=False))

def get_record(conn, model, id):
    record = conn.execute(select(model).where(model.c.id == id)).mappings().first()
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return dict(record)

@app.get("/")
def home():
    return {"tables": list(MODEL_MAP)}

@app.get("/{table}")
def index(table: str):
    model = get_table(table)
    with engine.connect() as conn:
        return [dict(r) for r in conn.execute(select(model).order_by(model.c.id.desc())).mappings()]

@app.get("/{table}/{id}")
def details(table: str, id: int):
    model = get_table(table)
    with engine.connect() as conn:
        return get_record(conn, model, id)

@app.post("/{table}", status_code=201)
def create(table: str, data: dict):
    model = get_table(table)
    try:
        with engine.begin() as conn:
            id = conn.execute(model.insert().values(**values(table, data))).inserted_primary_key[0]
            return get_record(conn, model, id)
    except (IntegrityError, StatementError):
        raise HTTPException(status_code=400, detail="Invalid record")

@app.put("/{table}/{id}")
def update(table: str, id: int, data: dict):
    model = get_table(table)
    try:
        with engine.begin() as conn:
            get_record(conn, model, id)
            conn.execute(model.update().where(model.c.id == id).values(**values(table, data)))
            return get_record(conn, model, id)
    except (IntegrityError, StatementError):
        raise HTTPException(status_code=400, detail="Invalid record")

@app.delete("/{table}/{id}")
def delete(table: str, id: int):
    model = get_table(table)
    with engine.begin() as conn:
        get_record(conn, model, id)
        conn.execute(model.delete().where(model.c.id == id))
    return {"deleted": id}
