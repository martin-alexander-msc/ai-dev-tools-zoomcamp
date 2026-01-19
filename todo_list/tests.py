from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from .models import Todo


class TodoModelTests(TestCase):
    def test_defaults(self):
        todo = Todo.objects.create(title="Sample")
        self.assertFalse(todo.is_resolved)
        self.assertIsNone(todo.due_date)

    def test_str(self):
        todo = Todo.objects.create(title="Sample")
        self.assertEqual(str(todo), "Sample")


class TodoViewsTests(TestCase):
    def create_todo(self, **overrides):
        data = {
            "title": "Task",
            "description": "Details",
            "due_date": date.today(),
            "is_resolved": False,
        }
        data.update(overrides)
        return Todo.objects.create(**data)

    def test_home_empty(self):
        response = self.client.get(reverse("todo_list_index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todo_list/home.html")
        self.assertContains(response, "No todos yet.")

    def test_home_lists_todos(self):
        todo = self.create_todo(title="First")
        response = self.client.get(reverse("todo_list_index"))
        self.assertContains(response, "First")
        self.assertIn(todo, response.context["todos"])

    def test_home_ordering(self):
        today = date.today()
        first = self.create_todo(title="First", due_date=today)
        second = self.create_todo(title="Second", due_date=today + timedelta(days=1))
        resolved = self.create_todo(title="Resolved", due_date=today, is_resolved=True)
        response = self.client.get(reverse("todo_list_index"))
        todos = list(response.context["todos"])
        self.assertEqual(todos, [first, second, resolved])

    def test_create_todo(self):
        response = self.client.post(
            reverse("todo_list_create"),
            {
                "title": "New todo",
                "description": "",
                "due_date": "2025-01-01",
                "is_resolved": False,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Todo.objects.filter(title="New todo").exists())

    def test_create_invalid(self):
        response = self.client.post(reverse("todo_list_create"), {"title": ""})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Todo.objects.count(), 0)

    def test_create_get_redirects(self):
        response = self.client.get(reverse("todo_list_create"))
        self.assertEqual(response.status_code, 302)

    def test_edit_get(self):
        todo = self.create_todo()
        response = self.client.get(reverse("todo_list_edit", args=[todo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, todo.title)

    def test_edit_post(self):
        todo = self.create_todo()
        response = self.client.post(
            reverse("todo_list_edit", args=[todo.id]),
            {
                "title": "Updated",
                "description": "Updated",
                "due_date": "2025-02-01",
                "is_resolved": True,
            },
        )
        self.assertEqual(response.status_code, 302)
        todo.refresh_from_db()
        self.assertEqual(todo.title, "Updated")
        self.assertTrue(todo.is_resolved)

    def test_edit_invalid(self):
        todo = self.create_todo()
        response = self.client.post(
            reverse("todo_list_edit", args=[todo.id]),
            {"title": "", "description": "", "due_date": "", "is_resolved": False},
        )
        self.assertEqual(response.status_code, 200)
        todo.refresh_from_db()
        self.assertEqual(todo.title, "Task")

    def test_edit_missing_returns_404(self):
        response = self.client.get(reverse("todo_list_edit", args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_toggle_resolved(self):
        todo = self.create_todo(is_resolved=False)
        response = self.client.post(reverse("todo_list_toggle", args=[todo.id]))
        self.assertEqual(response.status_code, 302)
        todo.refresh_from_db()
        self.assertTrue(todo.is_resolved)

    def test_toggle_requires_post(self):
        todo = self.create_todo()
        response = self.client.get(reverse("todo_list_toggle", args=[todo.id]))
        self.assertEqual(response.status_code, 405)

    def test_toggle_missing_returns_404(self):
        response = self.client.post(reverse("todo_list_toggle", args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_delete(self):
        todo = self.create_todo()
        response = self.client.post(reverse("todo_list_delete", args=[todo.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Todo.objects.filter(id=todo.id).exists())

    def test_delete_requires_post(self):
        todo = self.create_todo()
        response = self.client.get(reverse("todo_list_delete", args=[todo.id]))
        self.assertEqual(response.status_code, 405)

    def test_delete_missing_returns_404(self):
        response = self.client.post(reverse("todo_list_delete", args=[999]))
        self.assertEqual(response.status_code, 404)
