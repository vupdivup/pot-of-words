from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey
from typing import List

class Base(DeclarativeBase):
    pass

class Entry(Base):
    __tablename__ = "entry"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str]
    class_: Mapped[str] = mapped_column(name="class", nullable=True)
    pattern: Mapped[str] = mapped_column(nullable=True)
    etimology: Mapped[str] = mapped_column(nullable=True)
    definitions: Mapped[List["Definition"]] = relationship(lazy="selectin")

    def to_dict(self):
        return {
            "id": self.id,
            "key": self.key,
            "class": self.class_,
            "pattern": self.pattern,
            "etimology": self.etimology,
            "definitions": [d.definition for d in self.definitions]
        }

class Definition(Base):
    __tablename__ = "definition"

    id: Mapped[int] = mapped_column(primary_key=True)
    entry_id: Mapped[int] = mapped_column(ForeignKey(Entry.id))
    definition: Mapped[str]

    def to_dict(self):
        return self.definition