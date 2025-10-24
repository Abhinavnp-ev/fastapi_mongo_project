# FastAPI MongoDB with GCP Storage

## Overview
This project is a FastAPI backend application connected to MongoDB for database operations and Google Cloud Storage (GCS) for file uploads. The application is fully containerized using Docker and ready to deploy to cloud providers such as Google Cloud Platform (GCP).

---

## Features
- MongoDB CRUD APIs for managing data
- File upload endpoint that stores files to Google Cloud Storage
- Metadata of uploaded files stored in MongoDB
- Interactive API documentation with Swagger UI
- Dockerized for consistent deployment

---

## Setup

### Prerequisites
- Python 3.11 installed locally
- Docker installed locally
- Google Cloud Platform account with a Storage bucket created
- MongoDB Atlas or local MongoDB instance up and running
- `credentials.json` Google Cloud service account key file with proper Storage permissions

---

### Environment Configuration

1. Copy `.env.example` to `.env`


2. Fill the `.env` with your configuration values:


3. Place your Google Cloud service account key JSON file as `credentials.json` in the project root.

---

### Running Locally (without Docker)

1. Create and activate a virtual environment

python -m venv venv
source venv/bin/activate # On Windows PowerShell use venv\Scripts\Activate.ps1

2. Install dependencies

pip install -r requirements.txt

3. Run FastAPI app

uvicorn app.main:app --reload

Access Swagger UI at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Docker Container Setup

Build the Docker image(make sure docker desktop is running):

docker build -t myfastapiapp .


Run the container:

docker run -p 8000:8000 myfastapiapp

Your app will be accessible at [http://localhost:8000](http://localhost:8000)

---

## Deployment to Google Cloud Run

1. Make sure you have the [Google Cloud SDK](https://cloud.google.com/sdk) installed and logged in.

2. Set your GCP project:

gcloud config set project your-project-id

3. Build the container image and push it to Google Container Registry:

gcloud builds submit --tag gcr.io/your-project-id/myfastapiapp

4. Deploy to Cloud Run:

gcloud run deploy myfastapiapp
--image gcr.io/your-project-id/myfastapiapp
--platform managed
--region your-region
--allow-unauthenticated


5. After deployment, Cloud Run will provide a public URL to access your FastAPI app.

---
Large File Upload Support
This project supports uploading large files efficiently to Google Cloud Storage (GCS) via two methods:

Chunked Upload (Server Upload):
The API reads the uploaded file in 1MB chunks and streams them to GCS, avoiding loading entire files into memory.

Signed URL Upload (Client Upload):
For files larger than 32MB (Cloud Run request size limit), the API generates a temporary signed URL.
Clients can upload files directly to GCS via this URL, bypassing the API backend.

How to use Signed URL Upload
Request a signed upload URL from:

GET /upload-url/?filename=yourfile.ext

Receive JSON with upload_url and unique_filename.

Upload your file directly to Google Cloud Storage using this URL via tools like curl, Postman, or frontend code.
