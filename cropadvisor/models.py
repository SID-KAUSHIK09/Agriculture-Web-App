from .extensions import db


class Info(db.Model):
    __tablename__ = "info"

    Sno = db.Column(db.Integer, primary_key=True)
    Crop_name = db.Column(db.String(100), nullable=False)
    Info_type = db.Column(db.String(100), nullable=False)
    Ans = db.Column(db.String(1000), nullable=True)


class Discussion(db.Model):
    __bind_key__ = "discussions"
    __tablename__ = "discussions"

    Sno = db.Column(db.Integer, primary_key=True)
    Farmer_name = db.Column(db.String(100), nullable=False)
    Query = db.Column(db.String(1000), nullable=False)
    # Answers are stored as one text field, one answer per line:
    # "<answer> - answer by <name>". Legacy rows used commas; see `answers`.
    Ans = db.Column(db.String(1000), nullable=True)

    ANSWER_SEPARATOR = "\n"

    @property
    def answers(self) -> list[str]:
        if not self.Ans:
            return []
        sep = self.ANSWER_SEPARATOR if self.ANSWER_SEPARATOR in self.Ans else ","
        return [a.strip() for a in self.Ans.split(sep) if a.strip()]

    def add_answer(self, text: str, author: str) -> None:
        entry = f"{text.strip()} - answer by {author.strip()}"
        existing = self.answers
        self.Ans = self.ANSWER_SEPARATOR.join([*existing, entry])
