# Step 1: Use the official Python 3.10 base image
FROM python:3.10

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the requirements file and install dependencies
RUN pip install markdown
RUN pip install duckdb
RUN pip install speechrecognition
RUN pip install bs4
RUN pip install FastAPI
RUN pip install uvicorn
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Step 4: Copy the rest of the application code into the container
COPY . .

# Step 5: Expose port 8000 for FastAPI
EXPOSE 8000

# Step 6: Define the command to start the FastAPI app
CMD ["uvicorn", "agent:app", "--host", "0.0.0.0", "--port", "8000"]