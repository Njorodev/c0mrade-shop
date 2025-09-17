---

## User Accounts & Permissions

⚠️ Note to Developers:

The user accounts listed in this project are created for testing and demonstration purposes only.  
- **Admin / Superadmin**: Admin@c0mrade.com  
- **Moderator**: JohnDoe@c0mrade.com  
- **Customer**: TestUser@example.com  

**Important:** Do **not** use these credentials in a production environment.  
Passwords and accounts are meant to help you test the application functionality safely.  

Always create secure, unique accounts when deploying the project to production.


________________________________________________________________________
| User      | Email                    | Role       | Password         |
| --------- | ------------------------ | ---------- | ---------------- |
| Admin     | Admin@c0mrade.com        | superadmin | Adm1n!Secure2025 |
| John Doe  | JohnDoe@c0mrade.com      | moderator  | J0hnD03!2025     |
| Test User | TestUser@example.com     | customer   | T3stUser#123     |
------------------------------------------------------------------------

__________________________________________________________________________________________________
| Action / Permission   | Superadmin (Admin) | Moderator (John Doe)       | Customer (Test User) |
| --------------------- | ------------------ | -------------------------- | -------------------- |
| View all admins       | ✔                  | ✔                          | ✘                    |
| View superadmin       | ✔                  | ✘                          | ✘                    |
| View all moderators   | ✔                  | ✔                          | ✘                    |
| View all customers    | ✔                  | ✔                          | ✘                    |
| View carts            | ✔                  | ✔                          | ✔ (own only)         |
| View wishlists        | ✔                  | ✔                          | ✔ (own only)         |
| View orders           | ✔                  | ✔                          | ✔ (own only)         |
| Add products          | ✔                  | ✔                          | ✘                    |
| Delete products       | ✔                  | ✔                          | ✘                    |
| Delete customers      | ✔                  | ✘                          | ✘                    |
| Delete moderators     | ✔                  | ✘                          | ✘                    |
| Add items to cart     | ✘                  | ✘                          | ✔                    |
| Add items to wishlist | ✘                  | ✘                          | ✔                    |
| Place orders          | ✘                  | ✘                          | ✔                    |
| Full dashboard access | ✔                  | ✔ (except superadmin info) | ✘                    |
--------------------------------------------------------------------------------------------------