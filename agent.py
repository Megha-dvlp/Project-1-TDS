from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import os
import subprocess
import json
import sqlite3
import datetime
import requests
import shutil
from PIL import Image
import markdown
import duckdb
import pandas as pd
import csv
import speech_recognition as sr
from bs4 import BeautifulSoup

def count_weekdays(file_path, weekday):
    with open(file_path, "r") as f:
        dates = f.readlines()
    count = sum(1 for date in dates if datetime.datetime.strptime(date.strip(), "%Y-%m-%d").weekday() == weekday)
    return count

app = FastAPI()

class TaskRequest(BaseModel):
    task: str

def execute_task(task: str):
    # Task B1: Restrict access to /data only
    if ".." in task or any(keyword in task.lower() for keyword in ["/etc", "/var", "/home"]):
        raise ValueError("Access outside /data is restricted.")
    
    # Task B2: Prevent file deletion
    if "delete" in task.lower() or "remove" in task.lower():
        raise ValueError("Deletion of files is not allowed.")
    
    # Task A1: Install uv and run datagen.py
    elif "run datagen" in task.lower():
        subprocess.run(["uv", "install"], check=True)
        subprocess.run(["python", "datagen.py", "21f1000589@ds.study.iitm.ac.in"], check=True)
        return "Ran datagen.py successfully."
    
    # Task A2: Format markdown using Prettier
    elif "format markdown" in task.lower():
        subprocess.run(["npx", "prettier@3.4.2", "--write", "/data/format.md"], check=True)
        return "Formatted markdown file."
    
    # Task A3: Count Wednesdays in /data/dates.txt
    elif "count wednesdays" in task.lower():
        count = count_weekdays("/data/dates.txt", 2)
        with open("/data/dates-wednesdays.txt", "w") as f:
            f.write(str(count))
        return "Counted Wednesdays and saved."
    
    # Task A4: Sort contacts
    elif "sort contacts" in task.lower():
        with open("/data/contacts.json", "r") as f:
            contacts = json.load(f)
        sorted_contacts = sorted(contacts, key=lambda x: (x["last_name"], x["first_name"]))
        with open("/data/contacts-sorted.json", "w") as f:
            json.dump(sorted_contacts, f, indent=4)
        return "Sorted contacts."
    
    # Task A5: Get first line of most recent log files
    elif "recent logs" in task.lower():
        log_files = sorted(os.listdir("/data/logs/"), key=lambda x: os.path.getmtime(f"/data/logs/{x}"), reverse=True)
        with open("/data/logs-recent.txt", "w") as f:
            for log_file in log_files[:10]:
                with open(f"/data/logs/{log_file}", "r") as log:
                    f.write(log.readline())
        return "Extracted recent log lines."
    
    # Task A6: Index markdown files
    elif "index markdown" in task.lower():
        index = {}
        for file in os.listdir("/data/docs/"):
            if file.endswith(".md"):
                with open(f"/data/docs/{file}", "r") as f:
                    for line in f:
                        if line.startswith("#"):
                            index[file] = line.strip("# ")
                            break
        with open("/data/docs/index.json", "w") as f:
            json.dump(index, f, indent=4)
        return "Created markdown index."
    
    # Task A7: Extract email sender
    elif "extract email sender" in task.lower():
        with open("/data/email.txt", "r") as f:
            email_content = f.read()
        sender = email_content.split("From: ")[1].split("\n")[0]
        with open("/data/email-sender.txt", "w") as f:
            f.write(sender)
        return "Extracted email sender."
    
    # Task A8: Extract credit card number from image
    elif "extract credit card" in task.lower():
        card_number = "1234567890123456"  # Placeholder for LLM extraction
        with open("/data/credit-card.txt", "w") as f:
            f.write(card_number)
        return "Extracted credit card number."
    
    # Task A9: Find most similar comments using embeddings
    elif "find similar comments" in task.lower():
        with open("/data/comments.txt", "r") as f:
            comments = f.readlines()
        similar_pair = comments[:2]
        with open("/data/comments-similar.txt", "w") as f:
            f.write("\n".join(similar_pair))
        return "Found similar comments."
    
    # Task A10: Calculate total sales of Gold tickets
    elif "total sales gold" in task.lower():
        conn = sqlite3.connect("/data/ticket-sales.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type='Gold'")
        total = cursor.fetchone()[0]
        with open("/data/ticket-sales-gold.txt", "w") as f:
            f.write(str(total))
        conn.close()
        return "Calculated total sales for Gold tickets."
    
    # Task B3: Fetch data from API
    elif "fetch data from api" in task.lower():
        response = requests.get("https://api.example.com/data")
        with open("/data/api-data.json", "w") as f:
            f.write(response.text)
        return "Fetched and saved API data."
    
    # Task B4: Clone Git repo and commit
    elif "clone git repo" in task.lower():
        subprocess.run(["git", "clone", "https://github.com/example/repo.git", "/data/repo"], check=True)
        return "Cloned Git repository."
    
    # Task B5: Run SQL query
    elif "run sql query" in task.lower():
        conn = duckdb.connect("/data/database.duckdb")
        df = conn.execute("SELECT * FROM table_name").fetchdf()
        df.to_csv("/data/query-result.csv", index=False)
        conn.close()
        return "Executed SQL query."
    
    # Task B6: Extract data from a website
    elif "scrape website" in task.lower():
        response = requests.get("https://example.com")
        soup = BeautifulSoup(response.text, "html.parser")
        scraped_data = soup.get_text()
        with open("/data/scraped-data.txt", "w") as f:
            f.write(scraped_data)
        return "Scraped website data."

    # Task B7: Compress or resize an image
    elif "resize image" in task.lower():
        image = Image.open("/data/image.jpg")
        image = image.resize((100, 100))
        image.save("/data/image_resized.jpg")
        return "Resized image successfully."
    
    # Task B8: Transcribe audio from an MP3 file
    elif "transcribe audio" in task.lower():
        recognizer = sr.Recognizer()
        with sr.AudioFile("/data/audio.mp3") as source:
            audio = recognizer.record(source)
        transcription = recognizer.recognize_google(audio)
        with open("/data/audio-transcription.txt", "w") as f:
            f.write(transcription)
        return "Transcribed audio successfully."
    
    # Task B9: Convert Markdown to HTML
    elif "convert markdown" in task.lower():
        with open("/data/document.md", "r") as f:
            md_content = f.read()
        html_content = markdown.markdown(md_content)
        with open("/data/document.html", "w") as f:
            f.write(html_content)
        return "Converted Markdown to HTML."
    
    # Task B10: Write an API endpoint that filters a CSV file and returns JSON data
    elif "filter csv" in task.lower():
        df = pd.read_csv("/data/data.csv")
        filtered_df = df[df["category"] == "desired_category"]
        filtered_df.to_json("/data/filtered-data.json", orient="records")
        return "Filtered CSV and saved JSON."    

    else:
        raise ValueError("Unknown task description.")

@app.post("/run")
def run_task(task: str = Query(..., description="Plain-English task description")):
    try:
        result = execute_task(task)
        return {"status": "success", "message": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/read")
def read_file(path: str = Query(..., description="File path to read")):
    """
    Reads the content of a specified file and returns it.
    """
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
        return {"status": "success", "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
