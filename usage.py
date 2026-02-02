import requests
import sys
import os
import mimetypes

API_BASE = "http://localhost:8000"
UPLOAD_URL = f"{API_BASE}/api/v1/upload"
ASK_URL = f"{API_BASE}/api/v1/ask"
HEALTH_URL = f"{API_BASE}/health"

def check_health():
    try:
        response = requests.get(HEALTH_URL)
        if response.status_code == 200:
            print("API is healthy.")
            return True
        else:
            print(f"API returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("Could not connect to API. Is the server running?")
        return False

def upload_image(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        return None

    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = "application/octet-stream"

    print(f"Uploading '{os.path.basename(file_path)}'...")
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, mime_type)}
            response = requests.post(UPLOAD_URL, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(" Upload successful!")
            return data['id']
        
        elif response.status_code == 400:
             print(f" Upload failed: {response.json().get('detail')}")
             return None
        else:
            print(f"Server Error: {response.text}")
            return None
        
    except Exception as e:
        print(f"Error during upload: {e}")
        return None

def ask_loop(document_id):

    while True:
        try:
            question = input(" Question: ").strip()
        except KeyboardInterrupt:
            print("\n Exiting.")
            break
        
        if question.lower() in ["exit", "quit"]:
            print(" Exiting.")
            break
        
        if not question:
            continue

        payload = {
            "document_id": document_id,
            "question": question
        }

        try:
            response = requests.post(ASK_URL, json=payload)

            if response.status_code == 200:
                answer = response.json().get("answer", "No answer provided.")
                print(f" Answer: {answer}\n")
            else:
                print(f" Error ({response.status_code}): {response.text}\n")
        except Exception as e:
            print(f" Request failed: {e}\n")

if __name__ == "__main__":
    
    if not check_health():
        sys.exit(1)

    raw_path = input("\n Enter path to image file: ").strip()
    image_path = raw_path.strip('"').strip("'") 
    
    doc_id = upload_image(image_path)
    
    if doc_id:
        ask_loop(doc_id)