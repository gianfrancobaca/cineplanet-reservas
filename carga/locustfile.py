from locust import HttpUser, task, between, tag

class Visitante(HttpUser):
    wait_time = between(1, 2)

    @tag("salud")
    @task(1)
    def salud(self):
        self.client.get("/salud")

    @tag("db")
    @task(3)
    def salud_db(self):
        self.client.get("/salud/db")