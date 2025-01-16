# 🐾 PetWell

A modern pet health management system with FastAPI backend and React frontend.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-green.svg)
![React](https://img.shields.io/badge/React-18.0+-61dafb.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🏗️ Project Structure

```
petwell/
├── api/              # Backend - FastAPI
│   ├── app/
│   │   ├── core/    # Core functionality
│   │   ├── models/  # Database models
│   │   ├── routes/  # API endpoints
│   │   └── utils/   # Utilities
│   └── tests/       # Backend tests
│
└── web/             # Frontend - React (Coming Soon)
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── hooks/
    │   └── utils/
    └── tests/
```

## 🚀 Quick Start

### Backend

1. Set up Python environment
```bash
cd api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the API server
```bash
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/api/docs` for API documentation.

### Frontend (Coming Soon)

The frontend will be built with:
- ⚛️ React 18
- 📝 TypeScript
- 🎨 Tailwind CSS
- 📊 Recharts for data visualization
- 🔄 React Query for API integration
- 🛣️ React Router for navigation

## 📚 Documentation

### Backend API
- Swagger UI: `/api/docs`
- ReDoc: `/api/redoc`

### Frontend (Planned)
- Component storybook
- API integration guide
- State management patterns

## 🛠️ Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT Authentication
- MinIO (File Storage)

### Frontend (Planned)
- React
- TypeScript
- Tailwind CSS
- React Query
- React Router
- Vite

## 🤝 Contributing

Contributions are welcome! Please check our contributing guidelines.

## 📝 License

This project is licensed under the MIT License.
