from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Entry(Base):
    __tablename__ = "entry"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str]
    class_: Mapped[str] = mapped_column(name="class", nullable=True)
    pattern: Mapped[str] = mapped_column(nullable=True)
    etimology: Mapped[str] = mapped_column(nullable=True)

class Definition(Base):
    __tablename__ = "definition"

    id: Mapped[int] = mapped_column(primary_key=True)
    entry_id: Mapped[int]
    definition: Mapped[str]