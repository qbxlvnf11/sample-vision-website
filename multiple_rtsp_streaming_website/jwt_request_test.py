from datetime import datetime, timedelta
import jwt
import requests
import json
from datetime import datetime

def generate_jwt(company_id: str, secret_key: str) -> str:

    print("--- Start to generate JWT ---")
    
    ## JWT Payload
    payload = {
        'companyId': company_id,
        'iat': datetime.utcnow(),  # iat: Issued At
        'exp': datetime.utcnow() + timedelta(hours=1)  # exp: Expiration Time
    }
    
    print(f"Payload Info: {payload}")
    
    ## JWT Encryption (HS256 Algorithm)
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    
    print(f"JWT: {token}")
    return token

def send_event_to_server(jwt, base_url, endpoint, test_data: str):

    full_url = f"{base_url}{endpoint}"
    
    ## Header
    headers = {
        "Authorization": f"Bearer {jwt}"
    }
    
    ## Body
    payload = {
        "test_data": test_data,
        "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    print("--- Sending Request ---")
    print(f"URL: {full_url}")
    print(f"Headers: {headers}")
    print(f"Body: {json.dumps(payload, indent=2)}")
    
    try:
        ## Request
        response = requests.post(full_url, headers=headers, json=payload)
        
        #3 Response
        print("\n--- Received Response ---")
        print(f"Status Code: {response.status_code}")
         
        if response.ok:
            print("Response JSON:", response.json())
        else:
            print("Error Response:", response.text)

    except requests.exceptions.RequestException as e:
        print(f"\nAn error occurred: {e}")


# --- 함수 실행 예시 ---
if __name__ == "__main__":

    company_id = "test_company_id"
    secret_key = "test_secret_key"

    jwt = generate_jwt(company_id, secret_key)

    test_data = "test_data"

    send_event_to_server(
        jwt=jwt,
        base_url=base_url,
        endpoint=endpoint,
        test_data=test_data,
    )