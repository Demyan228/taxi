import json

from flask import Flask, request, jsonify

from database import TasksDataBase

app = Flask(__name__)
db = TasksDataBase()


@app.route("/tasks", methods=["GET"])
def get_free_tasks():
    result = [{
        "id": _id,
        "address_from": address_from,
        "address_to": address_to,
        "phone": phone,
        "time": time,
        "comment": comment
    } for _id, address_from, address_to, phone, time, comment in db.get_free_tasks()]
    return jsonify(result)


@app.route("/driver/<int:driver_id>/tasks", methods=["GET"])
def get_tasks_for_driver(driver_id):
    result = [{
        "id": _id,
        "address_from": address_from,
        "address_to": address_to,
        "phone": phone,
        "time": time,
        "comment": comment
    } for _id, address_from, address_to, phone, time, comment in db.get_driver_tasks(driver_id)]
    return jsonify(result)


@app.route("/tasks", methods=["POST"])
def add_new_task():
    if not request.is_json:
        print("NOT JSON")
        return {"status": "error", "message": "no json sent"}
    data = json.loads(request.data)
    db.add_new_task(data["address_from"], data["address_to"],
                    data["phone"], data["time"], data["comment"])
    return {"status": "ok"}


@app.route("/tasks/<int:task_id>/take", methods=["POST"])
def take_task(task_id):
    if not request.is_json:
        print("NOT JSON")
        return {"status": "error", "message": "no json sent"}
    data = json.loads(request.data)
    result = db.take_task(task_id, data["driver_id"])
    return {"status": "ok" if result else "failed"}


@app.route("/tasks/<int:task_id>/complete", methods=["POST"])
def complete_task(task_id):
    db.complete_task(task_id)
    return {"status": "ok"}


if __name__ == "__main__":
    app.run()
