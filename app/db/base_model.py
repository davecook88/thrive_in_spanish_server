from sqlmodel import SQLModel, Session


class DBModel(SQLModel):
    __abstract__ = True

    async def save(self, db: Session) -> "DBModel":
        db.add(self)
        db.commit()
        return self

    async def delete(self, db: Session) -> None:
        db.delete(self)
        db.commit()
