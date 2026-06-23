from datetime import datetime


class Task:
    VALID_PRIORITIES = ["Niedrig", "Mittel", "Hoch"]
    VALID_STATUS = ["Offen", "In Bearbeitung", "Erledigt"]

    def __init__(self, title, description, priority, status, due_date):
        if not title or not title.strip():
            raise ValueError("Der Titel darf nicht leer sein.")

        self.validate_priority(priority)
        self.validate_status(status)

        self.title = title.strip()
        self.description = description
        self.priority = priority
        self.status = status

        # Datum validieren
        self.due_date = self.validate_due_date(due_date)

    @staticmethod
    def validate_due_date(due_date):
        try:
            return datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Datum muss im Format YYYY-MM-DD sein.")

    @classmethod
    def validate_priority(cls, priority):
        if priority not in cls.VALID_PRIORITIES:
            raise ValueError("Prioritaet muss Niedrig, Mittel oder Hoch sein.")

    @classmethod
    def validate_status(cls, status):
        if status not in cls.VALID_STATUS:
            raise ValueError(
                "Status muss Offen, In Bearbeitung oder Erledigt sein."
            )

    def days_left(self):
        return (self.due_date.date() - datetime.now().date()).days

    def is_overdue(self):
        return self.days_left() < 0 and self.status != "Erledigt"

    def is_due_today(self):
        return self.days_left() == 0

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "due_date": self.due_date.strftime("%Y-%m-%d"),
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["title"],
            data["description"],
            data["priority"],
            data["status"],
            data["due_date"],
        )

    def __str__(self):
        status_info = ""

        if self.is_overdue():
            status_info = " | UEBERFAELLIG"
        elif self.is_due_today():
            status_info = " | HEUTE FAELLIG"
        else:
            status_info = f" | Noch {self.days_left()} Tage"

        return (
            f"Titel: {self.title} | "
            f"Beschreibung: {self.description} | "
            f"Prioritaet: {self.priority} | "
            f"Status: {self.status} | "
            f"Faellig am: {self.due_date.strftime('%Y-%m-%d')}"
            f"{status_info}"
        )
