import requests


class ServerConnector:

    def __init__(self, address, port):
        self.url = f"{address}:{port}"
        self.user_id = None
        self.views = set()

    def set_user(self, user_id):
        self.user_id = user_id

    def add_view(self, view):
        self.views.add(view)

    def update_data(self):
        for view in self.views:
            view.update_data()

    def get_free_tasks(self):
        content = requests.get(f"{self.url}/tasks").json()
        return content

    def get_task_for_driver(self):
        url = f"{self.url}/driver/{self.user_id}/tasks"
        content = requests.get(url).json()
        return content

    def add_task(self, address_from, address_to, phone, time, comment):
        url = f"{self.url}/tasks"
        params = {
            "address_from": address_from,
            "address_to": address_to,
            "phone": phone,
            "time": time,
            "comment": comment
        }
        result = requests.post(url, json=params).json()
        self.update_data()
        return result["status"] == "ok"

    def take_task(self, task_id):
        url = f"{self.url}/tasks/{task_id}/take"
        params = {"driver_id": self.user_id}
        result = requests.post(url, json=params).json()
        self.update_data()
        return result["status"] == "ok"

    def complete_task(self, task_id):
        url = f"{self.url}/tasks/{task_id}/complete"
        requests.post(url)
        self.update_data()
        return True





