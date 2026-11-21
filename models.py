import os
from pathlib import Path
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, ForeignKey, event, select

# Change DB_BACKEND to "mysql" or "postgresql" to use a local server.
# Environment variables can override the course examples below.
from sqlalchemy.engine import URL

backend = os.environ.get("DB_BACKEND", "sqlite").lower()
if backend == "sqlite":
    url = URL.create("sqlite", database=str(Path(__file__).with_name("Test_DB.db")))
elif backend in ("mysql", "postgresql"):
    url = URL.create(
        "mysql+pymysql" if backend == "mysql" else "postgresql+psycopg2",
        username=os.environ.get("DB_USER", "root" if backend == "mysql" else "postgres"),
        password=os.environ.get("DB_PASSWORD", "" if backend == "mysql" else "Mft2026$$"),
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "3306" if backend == "mysql" else "5432")),
        database=os.environ.get("DB_NAME", "mft"),
    )
else:
    raise ValueError("DB_BACKEND must be sqlite, mysql or postgresql")
engine = create_engine(os.environ.get("DATABASE_URL", url))
if engine.dialect.name == "sqlite":
    @event.listens_for(engine, "connect")
    def sqlite_foreign_keys(connection, record):
        connection.execute("PRAGMA foreign_keys=ON")

metadata = MetaData()
doctors = Table("doctors", metadata, Column("id", Integer, primary_key=True), Column("name", String(255), nullable=False), Column("specialty", String(255), nullable=False))
patients = Table("patients", metadata, Column("id", Integer, primary_key=True), Column("name", String(255), nullable=False), Column("illness", String(255), nullable=False))
contract_pharma = Table("contract_pharma", metadata, Column("id", Integer, primary_key=True), Column("name", String(255), nullable=False), Column("location", String(255), nullable=False))
meds = Table("meds", metadata, Column("id", Integer, primary_key=True), Column("pharr_id", Integer, ForeignKey("contract_pharma.id", ondelete="CASCADE"), nullable=False), Column("name", String(255), nullable=False), Column("is_pill", Integer, nullable=False), Column("stock", Integer, nullable=False), Column("price", Float, nullable=False))
prescription = Table("prescription", metadata, Column("id", Integer, primary_key=True), Column("doc_id", Integer, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False), Column("pat_id", Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False), Column("phar_id", Integer, ForeignKey("contract_pharma.id", ondelete="CASCADE"), nullable=False), Column("date", String(255), nullable=False), Column("is_done", Integer, nullable=False))
prescription_items = Table("prescription_items", metadata, Column("id", Integer, primary_key=True), Column("prescr_id", Integer, ForeignKey("prescription.id", ondelete="CASCADE"), nullable=False), Column("med_id", Integer, ForeignKey("meds.id", ondelete="CASCADE"), nullable=False), Column("cons_instr", String(255), nullable=False))
MODEL_MAP = {t.name: t for t in metadata.sorted_tables}
metadata.create_all(engine)

def seed_data():
    with engine.begin() as conn:
        if conn.execute(select(doctors.c.id).limit(1)).first():
            return
        doc = conn.execute(doctors.insert().values(name="Dr. Smith", specialty="Cardiology")).inserted_primary_key[0]
        conn.execute(doctors.insert().values(name="Dr. Johnson", specialty="Neurology"))
        pat = conn.execute(patients.insert().values(name="Alex", illness="Hypertension")).inserted_primary_key[0]
        conn.execute(patients.insert().values(name="Rico", illness="Migraine"))
        pharma = conn.execute(contract_pharma.insert().values(name="PharmaPlus", location="3rd Street")).inserted_primary_key[0]
        med = conn.execute(meds.insert().values(pharr_id=pharma, name="Aspirin", is_pill=1, stock=100, price=5.99)).inserted_primary_key[0]
        conn.execute(meds.insert().values(pharr_id=pharma, name="Ibuprofen", is_pill=1, stock=50, price=8.50))
        presc = conn.execute(prescription.insert().values(doc_id=doc, pat_id=pat, phar_id=pharma, date="2026-10-07", is_done=0)).inserted_primary_key[0]
        conn.execute(prescription_items.insert().values(prescr_id=presc, med_id=med, cons_instr="Once daily with food"))

seed_data()
