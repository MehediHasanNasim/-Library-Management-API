# Library Management API

The Library Management API facilitates the management of a library system where users (members) can view, borrow, and return books, while administrators can manage the collection of books. The system implements JWT authentication and role-based access control to ensure secure access.

## Key Features & Implementation Design
 
### 1. Authentication and Authorization
- **JWT Authentication:** The system uses JWT for secure communication.
- **Role-Based Access Control**:
  - **Admin**:
    - Manage books (CRUD operations).
    - View all borrow records, returns, and fine submissions.
  - **Member**:
    - View available books.
    - Borrow, return books.
    - Pay fines.

---

### 2. Book Management (Admin)
- **CRUD Operations**:
  - Create, retrieve, update, or delete book entries.
  - Automatic synchronization of `total_copies` and `copies_available` to maintain consistency.
- Efficient querying for available books:
  - Retrieve only books with `copies_available > 0`.

---

### 3. Book Borrowing and Returning System (Member)
#### Borrowing:
- Members can borrow up to **5 books** at a time.
- Borrow records track the due date:
  - **Return Due Date**: 14 days from the borrow date.
- System checks availability before allowing borrowing:
  - Books must have `copies_available > 0`.

#### Returning:
- Borrowed books must be marked as returned.
- Returning a book triggers:
  - Updates to the book's availability in the system.
  - Automatic fine calculation for overdue returns:
    - Fine = **5 BDT per day** for late submissions.

---

### 4. Fine and Submission Handling
- **Fines**:
  - Automatically calculated for overdue books.
  - Linked to the corresponding borrow record.
- **Submissions**:
  - Tracks payments made against fines.
  - Fines are marked as paid upon successful payment.

---

### 5. Handling Concurrency
- Ensures consistency and integrity during borrowing:
  - **Database Transactions**:
    - Used `transaction.atomic()` to maintain database integrity.
  - **Row-Level Locking**:
    - Applied `select_for_update()` to lock the `Book` row during borrowing operations.
- Prevents race conditions:
  - Ensures that no multiple members can borrow the same book simultaneously.

---

### 6. Optimized Querying
- **Available Books**: 
  - Fetches only books with `copies_available > 0`.
- **User-Specific Records**:
  - Borrow records and fines are filtered for the authenticated user.

---

## How to Run the Project

### Clone the Repository:
```bash
git clone https://github.com/MehediHasanNasim/Library-Management-API.git
cd Library-Management-API
cd library_api
```
### Set Up Environment:

```bash
python3 -m venv venv
source venv/bin/activate  # For Windows: `venv\Scripts\activate`
```
### Install Dependencies
```bash
pip install -r requirements.txt
```
### Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```
### Run the Development Server
```bash
python manage.py runserver
```
### Note
Before running the project, you need to set up your environment variables, especially for production environments. 

1. **Create a `.env` file** in the root of your project (same level as `manage.py`).
   
2. **Add the following environment variables** to the `.env` file:
   
   ```env
   SECRET_KEY=<your_secret_key>
   DEBUG=True  # Set to False in production environments


### Testing the API
Use Postman or similar tools to test the endpoints listed below.
### Authentication Endpoints

| Method | Endpoint              | Description                  | Example JSON                                   |
|--------|-----------------------|------------------------------|------------------------------------------------|
| POST   | `/auth/users/`         | Register a user.             | `{ "username": "user", "password": "pass", "role": "member" }` |
| POST   | `/auth/jwt/create/`    | Obtain a JWT token.          | `{ "username": "user", "password": "pass" }`    |
| POST   | `/auth/jwt/refresh/`   | Refresh the JWT token.       | `{ "refresh": "<refresh_token>" }`              |
| POST   | `/auth/jwt/verify/`    | Verify a JWT token.          | `{ "token": "<jwt_token>" }`                    |

Superadmin: { "username": "admin", "password": "admin" }

### Books Endpoints

| Method | Endpoint            | Description                        | Example JSON                                |
|--------|---------------------|------------------------------------|---------------------------------------------|
| POST   | `/books/`            | Add a new book.                    | `{ "title": "Book", "author": "Author", "isbn": "1234", "total_copies": 5 }` |
| GET    | `/books/`            | List all books.                    | —                                           |
| GET    | `/books/{id}/`       | Retrieve a specific book.         | —                                           |
| PUT    | `/books/{id}/`       | Update a book's details.           | `{ "title": "Updated Title" }`               |
| DELETE | `/books/{id}/`       | Delete a book.                     | —                                           |


### Borrow Records Endpoints

| Method | Endpoint            | Description                          | Example JSON                     |
|--------|---------------------|--------------------------------------|----------------------------------|
| POST   | `/borrow-records/`   | Borrow a book.(only members)          | `{ "book": 8 }`                  |
| GET    | `/borrow-records/`   | List all borrow records (Member).    | —                                |


### Book Returns Endpoints

| Method | Endpoint            | Description                       | Example JSON                      |
|--------|---------------------|-----------------------------------|-----------------------------------|
| POST   | `/book-returns/`     | Mark a book as returned.          | `{ "borrow_record": 2}`           |
| GET    | `/book-returns/`     | List all book returns (Admin).    | —                                 |


### Fines Endpoints

| Method | Endpoint            | Description                       | Example JSON                      |
|--------|---------------------|-----------------------------------|-----------------------------------|
| GET    | `/fines/`            | View all fines for a user.        | —                                 |


### Submissions Endpoints

| Method | Endpoint            | Description                     | Example JSON                                  |
|--------|---------------------|---------------------------------|-----------------------------------------------|
| POST   | `/submissions/`      | Pay a fine.                    | `{ "borrow_record": 1, "amount_paid": 50.00 }` |
| GET    | `/submissions/`      | List all payment submissions.   | —                                            |



---










