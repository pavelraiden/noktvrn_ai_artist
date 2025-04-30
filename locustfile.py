from locust import HttpUser, task, between

class APIUser(HttpUser):
    # Wait time between tasks for each user
    wait_time = between(1, 3) # seconds

    # Define the host to test (will be overridden by --host flag)
    # host = "http://localhost:8000"

    @task
    def get_root(self):
        """Access the root endpoint."""
        self.client.get("/")

    @task
    def get_docs(self):
        """Access the API documentation (Swagger UI)."""
        self.client.get("/docs")

    # Add more tasks here to simulate user behavior
    # Example: POST request to create an artist (if endpoint exists)
    # @task(2) # Make this task twice as likely
    # def create_artist(self):
    #     self.client.post("/artists/", json={"name": "Test Artist", "genre": "Pop"})

# To run this test:
# 1. Ensure the API service is running (e.g., via `docker compose up api`)
# 2. Run Locust: locust -f locustfile.py --host http://localhost:8000
# 3. Open your browser to http://localhost:8089 (Locust Web UI)
# 4. Configure the number of users and spawn rate, then start swarming.

