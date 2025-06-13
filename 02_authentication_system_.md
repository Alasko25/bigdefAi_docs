# Chapter 2: Authentication System

Welcome back to the Big Defend IA tutorial! In the last chapter, [Backend API (Communication Hub)](01_backend_api__communication_hub__.md), we learned how the different parts of our system talk to each other using the API, like messengers sending requests and responses.

But imagine sending sensitive information, like transaction details, or accessing administration tools without knowing *who* is making the request. That wouldn't be safe, right? Just like our bank analogy from Chapter 1, we need a way to check people's IDs before they can enter the main office or access specific areas.

This is where the **Authentication System** comes in.

### What is the Authentication System?

The **Authentication System** is the part of Big Defend IA that handles:

1.  **Identification:** Knowing *who* you claim to be (e.g., "I am Admin BigDefend").
2.  **Authentication:** Verifying that you *are* indeed who you claim to be (e.g., "Okay, Admin BigDefend, prove it by showing your ID and password").

It's the security checkpoint at the entrance of our system. Before you can ask the [Backend API (Communication Hub)](01_backend_api__communication_hub__.md) to fetch transactions, manage alerts, or train the AI model, you first need to pass this check.

### Our Use Case: Logging In

The most common way you interact with the Authentication System is by **logging in**.

Imagine this simple task: **As a user, I want to log into the Big Defend IA application so I can access the dashboard and see relevant information.**

How does the system make this happen securely?

1.  You open the Big Defend IA application (the Frontend).
2.  You see a login page asking for your email and password.
3.  You enter your credentials and click "Login".
4.  The Frontend sends your email and password to the **Backend API**.
5.  The **Backend API** passes these credentials to the **Authentication System**.
6.  The **Authentication System** checks if a user with that email exists and if the provided password matches the one stored securely.
7.  If the check passes (authentication is successful), the **Authentication System** gives the Frontend a special temporary pass (called a **token**).
8.  The Frontend receives the token and remembers it.
9.  Now that you are authenticated, the Frontend can show you the dashboard and use the token to make requests to the [Backend API (Communication Hub)](01_backend_api__communication_hub__.md) for data (like getting transactions, as we saw in Chapter 1). Any future request will include this token to prove you're logged in.

### How the Frontend Handles Login

When you type your email and password and click login, the Frontend uses its [Backend API (Communication Hub)](01_backend_api__communication_hub__.md) service to send this information to a specific login "address" (an endpoint) on the Backend.

Let's look at a simplified version of the code in `apiService.ts` that handles this:

```typescript
// --- File: bdia - FrontEND/src/services/apiService.ts (Simplified) ---
import axios from 'axios';

const BASE_URL = 'http://localhost:8000/api/v1';
// ... api instance setup ...

// This function sends the login request to the Backend
export const login = async (
  email: string,
  password: string
): Promise<{ access_token: string }> => {
  const res = await axios.post(
    `${BASE_URL}/auth/jwt/login`, // The specific login address on the Backend
    new URLSearchParams({
      username: email, // The Backend expects 'username' and 'password'
      password: password,
    })
  );
  const { access_token } = res.data; // We get the token from the Backend's response
  localStorage.setItem('auth_token', access_token); // Store the token for later
  return res.data;
};

// ... other API functions ...
```

This function takes the email and password, creates a request to the `/auth/jwt/login` endpoint on our Backend, and uses `axios.post` to send it. If successful, it gets the `access_token` back from the Backend and stores it in the browser's `localStorage`. This token is our temporary pass!

After storing the token, the Frontend needs to remember that the user is now logged in. This is often managed using something like a "context" or "state" in the Frontend application. Our project uses `AuthContext.tsx`:

```typescript
// --- File: bdia - FrontEND/src/contexts/AuthContext.tsx (Simplified) ---
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../types';
import { login as loginApi } from '../services/apiService';

interface AuthContextType {
  user: User | null; // Stores the logged-in user's info
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean; // True if a user is logged in
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null); // State to hold the user info

  const login = async (email: string, password: string) => {
    try {
      // Call the login function from apiService to talk to the Backend
      const { access_token } = await loginApi(email, password);

      // After getting the token, get the user's details from the Backend
      const res = await fetch('http://localhost:8000/api/v1/users/me', {
        headers: {
          Authorization: `Bearer ${access_token}`, // Use the new token to get user info
        },
      });

      if (!res.ok) throw new Error('Impossible de récupérer le profil');

      const userData = await res.json();
      setUser(userData); // Store the user data in our state
      // ... connect websocket etc ...
    } catch (err) {
      // Handle login failure (e.g., show error message)
      console.error("Login failed", err);
      throw err; // Re-throw to let UI handle it
    }
  };

  const logout = () => {
    // ... clear token, user state ...
  };

  return (
    <AuthContext.Provider value={{
      user,
      login,
      logout,
      isAuthenticated: !!user, // Check if user state is not null
      // ... loading ...
    }}>
      {children}
    </AuthContext.Provider>
  );
};

// ... useAuth hook ...
```

This `AuthContext` provides the `login` function that the login page components will call. Crucially, *after* successfully getting the token using `apiService.login`, it makes *another* request (`/users/me`) using that *newly obtained token* to fetch the user's profile details (like name and role). It then stores this user information in the `user` state variable. The `isAuthenticated` variable simply becomes `true` if `user` is not `null`.

### How the Backend Handles Login Requests

On the Backend side, the `main.py` file (our Backend's reception desk from Chapter 1) is configured to direct incoming login requests to the part of the code that handles authentication.

```python
# --- File: bdia-BackEND/app/main.py (Simplified) ---
from fastapi import FastAPI
from fastapi_users import FastAPIUsers
# ... other imports ...

from app.auth.user_manager import get_user_manager # Manages user data/checks
from app.schemas.user import UserRead, UserCreate
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

app = FastAPI()

# ... Include other routers (transactions, alerts, etc.) ...

# Configure how authentication works (using JWT tokens)
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login") # Tells FastAPI where the login endpoint is

def get_jwt_strategy() -> JWTStrategy:
    # Defines how tokens are created and validated
    return JWTStrategy(
        secret="votre_secret_key", # Secret key for signing tokens (use settings.SECRET_KEY in prod!)
        lifetime_seconds=3600 # How long the token is valid (1 hour)
    )

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# This object combines user management and authentication logic
fastapi_users = FastAPIUsers[User, int](
    get_user_manager, # How to find and manage users
    [auth_backend], # How to authenticate (using our JWT setup)
)

# ... startup event ...

# Include the authentication routes provided by fastapi_users
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt", # Requests to /auth/jwt/... go here
    tags=["auth"],
)

# Include a route to get the current authenticated user's info (used by Frontend after login)
# This route requires authentication to access!
app.include_router(
    fastapi_users.get_users_router(UserRead, UserCreate),
    prefix="/users", # Requests to /users/... go here
    tags=["users"],
)
# NOTE: In our specific code, the main.py includes a default users router,
# which includes the /users/me endpoint needed by the frontend.
# However, there's also a separate app/routers/user.py which is NOT included by default in main.py.
# We'll focus on the routes included in main.py via fastapi_users.

```

The `fastapi_users` library does a lot of heavy lifting here. When a `POST` request hits `/auth/jwt/login`, `fastapi_users` takes over. It uses the configured `auth_backend` and `get_user_manager` to:

1.  Receive the `username` (email) and `password` from the request.
2.  Use the `user_manager` to find the user in the database based on the email.
3.  Use the `user_manager` to verify if the provided password matches the stored password for that user.
4.  If the password is correct, it uses the `JWTStrategy` to create a new JWT (JSON Web Token) containing information about the authenticated user.
5.  It sends this JWT back to the Frontend as the `access_token`.

The `main.py` also includes the `fastapi_users.get_users_router`, which provides useful endpoints like `/users/me`. This endpoint is *protected*, meaning you *must* be authenticated (send a valid token) to access it. This is what the Frontend uses *after* a successful login to fetch the user's details (`id`, `name`, `email`, `role`) to display in the application and store in the `AuthContext`.

### The Temporary Pass: JSON Web Tokens (JWT)

Instead of sending your email and password with *every single request* after logging in (which would be insecure and inefficient), the system uses a **JSON Web Token (JWT)**.

Think of a JWT as a sealed envelope containing a temporary ID card. When you log in successfully, the Backend creates this card for you, seals it with a special signature (the `secret` key in `get_jwt_strategy`), and gives it to the Frontend.

```mermaid
graph LR
    A[Frontend (Browser)] -- Send email/password --> B(Backend API /auth/jwt/login);
    B -- Checks credentials & creates JWT --> C(Authentication System);
    C -- Sends JWT (Token) to --> A;
    A -- Stores Token in localStorage --> D(localStorage);
    subgraph Subsequent Requests
        A -- Include Token in header --> E(Backend API /protected/endpoint);
        E -- Validate Token --> C;
        C -- Token Valid? Tell Backend --> E;
        E -- Proceed with request (e.g., get data) --> F(Other Routers/Database);
        F -- Send data --> E;
        E -- Send response --> A;
    end
```

For subsequent requests (like getting transactions, alerts, etc.), the Frontend adds this token to the request headers (a standard place to put extra information, like showing your ID card as you enter a building). The Backend API is set up (via `api.interceptors.request.use` in `apiService.ts` on the Frontend, and by using FastAPI dependency injection like `Depends(fastapi_users.current_user())` on the Backend) to automatically check for this token, verify its signature (to make sure it hasn't been tampered with), and confirm that it's still valid (not expired).

If the token is valid, the Backend knows who the user is without needing their password again and allows the request to proceed. If the token is missing, invalid, or expired, the Backend refuses the request (often returning a 401 Unauthorized error), prompting the Frontend to maybe redirect you back to the login page (handled by `api.interceptors.response.use` in `apiService.ts`).

```typescript
// --- File: bdia - FrontEND/src/services/apiService.ts (Interceptor) ---
// ... api instance setup ...

// This runs BEFORE every request sent by the 'api' instance
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token'); // Get the stored token
    if (token) {
      // If a token exists, add it to the 'Authorization' header
      config.headers.Authorization = `Bearer ${token}`; // Format is 'Bearer TOKEN_STRING'
    }
    return config; // Proceed with the request
  },
  (error) => Promise.reject(error)
);

// This runs AFTER every response received by the 'api' instance
api.interceptors.response.use(
  (response) => response, // If response is okay, just return it
  (error) => {
    // If the response status is 401 (Unauthorized)...
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token'); // Remove the invalid token
      window.location.href = '/login'; // Redirect user to login page
    }
    return Promise.reject(error); // Propagate other errors
  }
);

// ... login function and other API functions ...
```
This interceptor pattern is a clean way for the Frontend to automatically add the token to almost all outgoing requests and handle expired tokens centrally.

### Authentication and Authorization

It's important to distinguish between **Authentication** and **Authorization**:

| Concept        | Analogy                                 | What it answers             | Handled (Partially) In This Chapter? | Where it's fully handled     |
| :------------- | :-------------------------------------- | :-------------------------- | :----------------------------------- | :--------------------------- |
| **Authentication** | Checking your ID at the entrance      | *Who are you?* (Prove it!)  | Yes                                  | Backend Auth System          |
| **Authorization**  | What areas you are allowed to access    | *What can you do?*          | Briefly mentioned                    | [User and Role Management](03_user_and_role_management_.md) |

This chapter focuses on Authentication – proving your identity. Once the system knows *who* you are through authentication, the next step, Authorization, determines *what* you're allowed to see or do based on your assigned [User and Role Management](03_user_and_role_management_.md).

### Conclusion

The **Authentication System** is the critical first layer of security in Big Defend IA. It ensures that only legitimate users can access the application and its data by verifying their identity, primarily through a login process that results in a secure, temporary token (JWT). This token is then used for all subsequent communication with the [Backend API (Communication Hub)](01_backend_api__communication_hub__.md), preventing the need to send sensitive credentials repeatedly.

With authentication in place, the Backend knows *who* is making requests. The next logical step is to understand *what* different users are allowed to do. This depends on their roles and permissions.

Let's dive into the next chapter to explore how the system manages different types of users and assigns them specific roles and permissions.

[User and Role Management](03_user_and_role_management_.md)