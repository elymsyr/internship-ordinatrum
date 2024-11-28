from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import requests
import json
from typing import Optional, List

# Configuration
PROMETHEUS_URL = "http://localhost:9090/api/v1/query"  # Adjust based on your Prometheus URL
QUERY_FILE = "queries.json"  # File to store user-defined queries

# FastAPI instance
app = FastAPI()

# OAuth2 password bearer for strong authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dummy user data for authentication
fake_users_db = {
    "user1": {
        "username": "user1",
        "password": "secretpassword",  # In a real app, use hashed passwords
    }
}

# Function to verify credentials (dummy in this case)
def verify_password(username: str, password: str):
    if username in fake_users_db and fake_users_db[username]["password"] == password:
        return True
    return False

# Dependency to get the current user
def get_current_user(token: str = Depends(oauth2_scheme)):
    # In a real app, verify the token, e.g., using JWT
    if token == "dummy_token_for_user1":
        return "user1"
    raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Models for API input/output
class QueryRequest(BaseModel):
    query: str
    name: str

class PrometheusQueryResponse(BaseModel):
    status: str
    data: dict

class SystemActivityResponse(BaseModel):
    active_time_percentage: float
    total_time: int

# Helper function to read and write to the queries file
def load_queries():
    try:
        with open(QUERY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_queries(queries: dict):
    with open(QUERY_FILE, "w") as f:
        json.dump(queries, f, indent=4)

# Endpoint for querying Prometheus
@app.get("/query/{query_name}", response_model=PrometheusQueryResponse)
async def query_prometheus(query_name: str, user: str = Depends(get_current_user)):
    # Load the stored queries
    queries = load_queries()

    if query_name in queries:
        query = queries[query_name]
    else:
        raise HTTPException(status_code=404, detail="Query not found")

    # Send the query to Prometheus
    response = requests.get(PROMETHEUS_URL, params={"query": query})
    data = response.json()

    if data["status"] == "error":
        raise HTTPException(status_code=500, detail="Error querying Prometheus")

    return PrometheusQueryResponse(status="success", data=data["data"])

# Endpoint for submitting a new query or updating an existing one
@app.post("/query", response_model=str)
async def submit_query(query_request: QueryRequest, user: str = Depends(get_current_user)):
    # Load existing queries
    queries = load_queries()

    # Update or add the new query
    queries[query_request.name] = query_request.query
    save_queries(queries)

    return f"Query '{query_request.name}' has been added/updated successfully."

# Custom endpoint to measure system activity
@app.get("/system/activity", response_model=SystemActivityResponse)
async def system_activity(user: str = Depends(get_current_user)):
    # For example purposes, let's assume the system has been active for 80% of the time.
    active_time_percentage = 80.0
    total_time = 3600  # In seconds, e.g., 1 hour

    return SystemActivityResponse(
        active_time_percentage=active_time_percentage,
        total_time=total_time
    )

# Endpoint for custom Prometheus queries (allow users to specify their own)
@app.post("/custom-query", response_model=PrometheusQueryResponse)
async def custom_query(query: str, user: str = Depends(get_current_user)):
    # Send custom query to Prometheus
    response = requests.get(PROMETHEUS_URL, params={"query": query})
    data = response.json()

    if data["status"] == "error":
        raise HTTPException(status_code=500, detail="Error querying Prometheus")

    return PrometheusQueryResponse(status="success", data=data["data"])
