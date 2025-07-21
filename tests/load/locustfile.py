from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)  # wait between 1-3s between tasks

    @task(2)
    def home(self):
        self.client.get("/")

    @task(1)
    def login(self):
        self.client.post("/login", data={
            "email": "test@example.com",
            "password": "testpass"
        })

    @task(1)
    def register(self):
        self.client.post("/register", data={
            "email": "newuser@example.com",
            "password": "newpass"
        })

    @task(1)
    def builds(self):
        self.client.get("/builds")

    @task(1)
    def logout(self):
        self.client.get("/logout")
