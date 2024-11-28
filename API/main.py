import requests

def query_prometheus(prometheus_url, query):
    # Construct the Prometheus API URL for querying
    url = f"{prometheus_url}/api/v1/query"
    
    # Define the parameters for the query (PromQL query)
    params = {
        'query': query
    }
    
    # Send the request to Prometheus
    response = requests.get(url, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Return the JSON data
        return response.json()
    else:
        raise Exception(f"Failed to query Prometheus: {response.status_code}, {response.text}")

# Example usage:
prometheus_url = "http://<PROMETHEUS_SERVER>:9090"  # Replace with your Prometheus server address
query = 'node_cpu_seconds_total'  # Replace with your desired PromQL query
metrics_data = query_prometheus(prometheus_url, query)
print(metrics_data)
