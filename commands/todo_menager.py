import json
from typing import Dict, List

class TODO:
    def __init__(self, filename='todo.json'):
        self.filename = filename

    def read(self) -> Dict:
        try:
            with open(self.filename, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"tasks": []}

    def save(self, data: Dict):
        with open(self.filename, 'w') as file:
            json.dump(data, file, indent=2)

    def render(self) -> str:
        data = self.read()
        tasks = data.get('tasks', [])
        text = "\n\33[33m\33[1mTODO LIST\033[0m\n\n"
        for i, task in enumerate(tasks, 1):
            color = '\033[32m' if task['complete'] else '\033[31m'
            status = "[✓]" if task['complete'] else "[✗]"
            text += f"{i}. {color}{status} {task['title']} (by {task['author']})\033[0m\n"
        return text

    def add_task(self, title: str, author: str):
        data = self.read()
        data['tasks'].append({
            "title": title,
            "author": author,
            "complete": False
        })
        self.save(data)
        return f"Added task: {title}"

    def set_completion(self, task_num: int, complete: bool) -> str:
        data = self.read()
        try:
            task = data['tasks'][task_num - 1]
            task['complete'] = complete
            self.save(data)
            status = "completed" if complete else "marked as incomplete"
            return f"Task '{task['title']}' {status}"
        except IndexError:
            return "Invalid task number"