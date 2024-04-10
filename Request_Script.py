import requests

def send_data_to_api(input_data):
    """
    Sends structured data to a specified API endpoint via POST request and returns the request payload on successful completion.
    
    The input_data dictionary must include:
    - "url": The URL of the API endpoint.
    - "table": The table data as a Python object (list or dict).
    - "headers": A list of table headers.
    - "total_bids_traversed": The total number of bids traversed.
    - "total_bids_matched": The total number of bids matched.
    
    Parameters:
    - input_data (dict): A dictionary containing the URL, table (as a Python object),
                         headers, total_bids_traversed, and total_bids_matched.
    
    Returns:
    - tuple: A tuple containing a message indicating the success or failure of the data transmission and the data payload sent.
    """
    try:
        # Prepare the data payload to send
        data_payload = {
            "headers": input_data['headers'],
            "table": input_data['table'],
            "total_bids_traversed": input_data['total_bids_traversed'],
            "total_bids_matched": input_data['total_bids_matched']
        }
        
        # Send a POST request with the prepared data
        response = requests.post(input_data['url'], json=data_payload)
        
        if response.status_code == 200:
            return ("Data sent successfully.", data_payload)
        else:
            return (f"Failed to send data. Status code: {response.status_code}", data_payload)
    except Exception as e:
        return (f"An error occurred: {e}", data_payload)