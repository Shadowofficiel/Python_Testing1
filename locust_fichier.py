from locust import HttpUser, TaskSet, task, between


class UserBehavior(TaskSet):

    @task(1)
    def load_home(self):
        self.client.get("/")

    @task(2)
    def show_summary(self):
        self.client.post("/showSummary", data={"email": "john@simplylift.co"})

    @task(3)
    def purchase_places(self):
        self.client.post("/purchasePlaces", data={
            'competition': 'Spring Festival',
            'club': 'Simply Lift',
            'places': 2
        })


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
