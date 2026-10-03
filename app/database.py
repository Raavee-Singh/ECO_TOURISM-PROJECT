from sqlmodel import Session, SQLModel, create_engine
from .config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, echo=False)


def init_db():
    from .models import Activity, Booking, BudgetPlan, Complaint, EnvironmentalObservation, Guide, Place, Review, SavedPlace, Stay, User
    SQLModel.metadata.create_all(engine)


def get_db():
    with Session(engine) as session:
        yield session
