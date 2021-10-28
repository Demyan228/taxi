import sqlite3


class TasksDataBase:

    def __init__(self, database="tasks.sqlite"):
        self._db = database
        with sqlite3.connect(self._db) as connection:
            cursor = connection.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        address_from TEXT NOT NULL,
                        address_to TEXT NOT NULL,
                        phone INTEGER NOT NULL,
                        time INTEGER NOT NULL,
                        comment TEXT,
                        driver_id INTEGER,
                        is_active BOOLEAN NOT NULL
                        );
            """)
            connection.commit()

    def get_free_tasks(self):
        with sqlite3.connect(self._db) as connection:
            cursor = connection.cursor()
            result = cursor.execute("""
            SELECT id, address_from, address_to, phone, time, comment
            FROM tasks WHERE driver_id IS NULL;
            """).fetchall()
        return result

    def add_new_task(self, address_from, address_to, phone, time, comment):
        with sqlite3.connect(self._db) as connection:
            cursor = connection.cursor()
            cursor.execute("""
            INSERT INTO tasks 
            (address_from, address_to, phone, time, comment, driver_id, is_active)
            VALUES (?, ?, ?, ?, ?, NULL, FALSE)""",
                           (address_from, address_to, phone, time, comment))
            connection.commit()

    def take_task(self, task_id, driver_id):
        if self._task_is_free(task_id):
            self._set_driver_for_task(task_id, driver_id)
            return True
        return False

    def complete_task(self, task_id):
        with sqlite3.connect(self._db) as connection:
            cursor = connection.cursor()
            cursor.execute("""
            DELETE from tasks WHERE id=?""", (task_id,))
            connection.commit()

    def _task_is_free(self, task_id):
        with sqlite3.connect(self._db) as connection:
            cursor = connection.cursor()
            driver_id = cursor.execute("""
            SELECT driver_id FROM tasks WHERE id = ?""", (task_id,)).fetchone()[0]
        return driver_id is None

    def _set_driver_for_task(self, task_id, driver_id):
        with sqlite3.connect(self._db) as connection:
            cursor = connection.cursor()
            cursor.execute("""
            UPDATE tasks SET driver_id=? WHERE id=?""", (driver_id, task_id))
            connection.commit()

    def get_driver_tasks(self, driver_id):
        with sqlite3.connect(self._db) as connection:
            cursor = connection.cursor()
            result = cursor.execute("""
            SELECT id, address_from, address_to, phone, time, comment
            FROM tasks WHERE driver_id=?;""", (driver_id,)).fetchall()
        return result





















