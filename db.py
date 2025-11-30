from sqlmodel import Field, SQLModel, create_engine, Session
from datetime import datetime
import os

DATABASE_URL = "sqlite:///covered_call.db"
engine = create_engine(DATABASE_URL, echo=False)

class Position(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    symbol: str
    type: str
    qty: int
    entry_price: float
    metadata: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

def init_db():
    if not os.path.exists("covered_call.db"):
        SQLModel.metadata.create_all(engine)

def SessionLocal():
    return Session(engine)
