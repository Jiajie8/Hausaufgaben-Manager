from task import Task


class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self._validate_task(task)
        self.tasks.append(task)

    def delete_task(self, index):
        self._validate_index(index)
        self.tasks.pop(index)

    def edit_task(self, index, new_task):
        self._validate_index(index)
        self._validate_task(new_task)
        self.tasks[index] = new_task

    def change_status(self, index, new_status):
        self._validate_index(index)
        Task.validate_status(new_status)
        self.tasks[index].status = new_status

    def get_all_tasks(self):
        return self.tasks.copy()

    def get_task_by_index(self, index):
        self._validate_index(index)
        return self.tasks[index]

    def filter_tasks_by_status(self, status):
        Task.validate_status(status)
        return [task for task in self.tasks if task.status == status]

    def filter_tasks_by_priority(self, priority):
        Task.validate_priority(priority)
        return [task for task in self.tasks if task.priority == priority]

    def mark_task_as_done(self, index):
        self.change_status(index, "Erledigt")

    def sort_tasks_by_due_date(self):
        return sorted(self.tasks, key=lambda task: task.due_date)

    def get_overdue_tasks(self):
        return [task for task in self.tasks if task.is_overdue()]

    def get_tasks_due_today(self):
        return [task for task in self.tasks if task.is_due_today()]

    def _validate_index(self, index):
        if not isinstance(index, int):
            raise TypeError("Der Index muss eine ganze Zahl sein.")

        if index < 0 or index >= len(self.tasks):
            raise IndexError("Ungueltiger Index.")

    def _validate_task(self, task):
        if not isinstance(task, Task):
            raise TypeError(
                "Es koennen nur Task-Objekte hinzugefuegt werden."
            )
