from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import TodoForm
from .models import Todo


def index(request):
    todos = Todo.objects.order_by("is_resolved", "due_date", "-created_at")
    form = TodoForm()
    return render(request, "todo_list/home.html", {"todos": todos, "form": form})


def create(request):
    if request.method != "POST":
        return redirect("todo_list_index")
    form = TodoForm(request.POST)
    if form.is_valid():
        form.save()
    return redirect("todo_list_index")


def edit(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id)
    if request.method == "POST":
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            return redirect("todo_list_index")
    else:
        form = TodoForm(instance=todo)
    return render(request, "todo_list/edit.html", {"form": form, "todo": todo})


@require_POST
def toggle_resolved(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id)
    todo.is_resolved = not todo.is_resolved
    todo.save(update_fields=["is_resolved", "updated_at"])
    return redirect("todo_list_index")


@require_POST
def delete(request, todo_id):
    todo = get_object_or_404(Todo, pk=todo_id)
    todo.delete()
    return redirect("todo_list_index")
