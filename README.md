# FastAPI Authentication Server

A simple authentication server built with FastAPI that supports user signup, signin, and JWT-based authentication.

## Features

- User registration with validation
- User authentication with JWT tokens
- Password hashing using SHA-256
- JSON file-based data storage
- Comprehensive input validation

## Requirements

- Python 3.8+
- Newman (for testing)

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Newman (for testing)

```bash
npm install -g newman
```

On Linux/Mac, you may need to use `sudo`:

```bash
sudo npm install -g newman
```

### 3. Run the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

## Testing

### Automated Testing

Make the test script executable (Linux/Mac/WSL):

```bash
chmod +x test.sh
./test.sh
```

For Windows:

```bash
test.bat
```

### Manual Testing with Postman

1. Download the [Postman collection](https://raw.githubusercontent.com/UXGorilla/hiring-backend/main/collection.json)
2. Import it into Postman
3. Set the following environment variables:
   - `baseUrl`: Your server URL (e.g., `http://localhost:8000`)
   - `username`: A test username
   - `password`: A test password
   - `fname`: First name
   - `lname`: Last name
4. Run the collection

## API Endpoints

### POST /signup

Register a new user.

**Request Body:**
```json
{
  "username": "john",
  "password": "Pass123",
  "fname": "John",
  "lname": "Doe"
}
```

**Success Response (201):**
```json
{
  "result": true,
  "message": "SignUp success. Please proceed to Signin"
}
```

### POST /signin

Sign in an existing user.

**Request Body:**
```json
{
  "username": "john",
  "password": "Pass123"
}
```

**Success Response (200):**
```json
{
  "result": true,
  "jwt": "<jwt_token>",
  "message": "Signin success"
}
```

### GET /user/me

Get current user information (requires JWT token).

**Headers:**
```
Authorization: <jwt_token>
```

**Success Response (200):**
```json
{
  "result": true,
  "data": {
    "fname": "John",
    "lname": "Doe",
    "password": "<hashed_password>"
  }
}
```

## Validation Rules

### Username
- Only lowercase English alphabets (a-z)
- At least 4 characters
- No numbers or special characters

### Password
- At least 5 characters
- Must contain at least 1 uppercase letter
- Must contain at least 1 lowercase letter
- Must contain at least 1 number
- No special characters allowed

### First Name & Last Name
- Only English alphabets (A-Z, a-z)

## Deployment

The application can be deployed on various platforms:

### Railway

1. Create a new project on [Railway](https://railway.app)
2. Connect your GitHub repository
3. Railway will auto-detect the Python app
4. Set the start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Render

1. Create a new Web Service on [Render](https://render.com)
2. Connect your GitHub repository
3. Set the build command: `pip install -r requirements.txt`
4. Set the start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Create a `vercel.json` file:
```json
{
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```
3. Deploy: `vercel --prod`

## File Structure

```
.
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── test.sh             # Test script for Linux/Mac/WSL
├── test.bat            # Test script for Windows
├── users.json          # User data storage (auto-generated)
└── README.md           # This file
```

## Security Notes

- **For Production**: Change the `JWT_SECRET` in `main.py` to a secure random string
- Passwords are hashed using SHA-256
- JWT tokens expire after 24 hours
- The `users.json` file stores user data locally

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:

**Linux/Mac:**
```bash
lsof -ti:8000 | xargs kill -9
```

**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Newman Not Found

Ensure Node.js and npm are installed, then:
```bash
npm install -g newman
```

## License

This is a technical assessment project for iGnosis Tech.