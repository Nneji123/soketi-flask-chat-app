# soketi-flask-chat-app
Simple Flask Chat App using Soketi backend

# Chat Application Setup Guide

This guide will help you set up and run the chat application using Soketi, Flask, and a simple HTTP server.

## Prerequisites

- Docker and Docker Compose
- Python 3.x
- ngrok account and authtoken

## Setup Steps

1. Clone the repository and navigate to the project directory.

2. Create a `.env` file in the root directory and add your ngrok authtoken:
   ```
   NGROK_AUTHTOKEN=your_ngrok_authtoken_here
   ```

3. Start Soketi and ngrok services:
   ```
   docker-compose up -d
   ```

4. Install Flask and required dependencies:
   ```
   pip install Flask Flask-SQLAlchemy pusher flask-cors
   ```

5. Run the Flask application:
   ```
   python app.py
   ```

6. In a new terminal, start the HTTP server for the frontend:
   ```
   python -m http.server 8000
   ```

7. Open your browser and navigate to `http://localhost:8000` to use the chat application.

Note: Make sure to update the Pusher configuration in both the Flask app and the HTML file with the correct Soketi details and ngrok URL.
