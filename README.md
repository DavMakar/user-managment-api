# User Management API

A simple RESTful API built with Flask for managing users, packaged in a lightweight Docker container.

[![Docker Image](https://img.shields.io/badge/docker-davmakar/user--management--api-blue?logo=docker)](https://hub.docker.com/r/davmakar/user-management-api)

---

## 🚀 Quick Start

### 1. Run the API with Docker

```bash
docker run -d -p 5000:5000 --name user-api davmakar/user-management-api
```

### 2. Open in your browser

Visit:  
👉 [http://localhost:5000](http://localhost:5000)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/users` | Get all users |
| GET | `/api/users/:id` | Get user by ID |
| POST | `/api/users` | Create new user |
| DELETE | `/api/users/:id` | Delete user |