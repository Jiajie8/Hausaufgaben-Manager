import unittest

from task import Task
from task_manager import TaskManager


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.manager = TaskManager()

        self.task1 = Task(
            "Mathe lernen",
            "Kapitel 5 wiederholen",
            "Hoch",
            "Offen",
            "2026-04-10",
        )

        self.task2 = Task(
            "Praesentation vorbereiten",
            "Folien fuer das Schulprojekt erstellen",
            "Mittel",
            "In Bearbeitung",
            "2026-04-12",
        )

    def test_add_task(self):
        self.manager.add_task(self.task1)

        self.assertEqual(len(self.manager.get_all_tasks()), 1)
        self.assertEqual(
            self.manager.get_task_by_index(0),
            self.task1
        )

    def test_delete_task(self):
        self.manager.add_task(self.task1)
        self.manager.add_task(self.task2)

        self.manager.delete_task(0)

        self.assertEqual(len(self.manager.get_all_tasks()), 1)
        self.assertEqual(
            self.manager.get_task_by_index(0),
            self.task2
        )

    def test_change_status(self):
        self.manager.add_task(self.task1)

        self.manager.change_status(0, "Erledigt")

        self.assertEqual(
            self.manager.get_task_by_index(0).status,
            "Erledigt"
        )

    def test_filter_tasks_by_status(self):
        self.manager.add_task(self.task1)
        self.manager.add_task(self.task2)

        offene_tasks = self.manager.filter_tasks_by_status("Offen")

        self.assertEqual(len(offene_tasks), 1)
        self.assertEqual(offene_tasks[0], self.task1)

    def test_sort_tasks_by_due_date(self):
        self.manager.add_task(self.task2)
        self.manager.add_task(self.task1)

        sorted_tasks = self.manager.sort_tasks_by_due_date()

        self.assertEqual(sorted_tasks[0], self.task1)

    def test_mark_task_as_done(self):
        self.manager.add_task(self.task1)

        self.manager.mark_task_as_done(0)

        self.assertEqual(
            self.manager.get_task_by_index(0).status,
            "Erledigt"
        )


if __name__ == "__main__":
    unittest.main()