from app.db import query_db

class UserService:
    @staticmethod
    def get_all_users():
        try:
            users = query_db("SELECT * FROM users")
            return {"users": users if users else [], "count": len(users) if users else 0}
        except Exception as e:
            print(f"Error: {e}")
            return {"users": [], "count": 0}

    @staticmethod
    def get_user_by_id(user_id):
        try:
            return query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
        except Exception as e:
            print(f"Error: {e}")
            return None

    @staticmethod
    def create_user(data):
        try:
            return query_db(
                'INSERT INTO users (name, email, role) VALUES (%s, %s, %s) RETURNING *',
                (data.get('name'), data.get('email'), data.get('role')),
                one=True,
                commit=True
            )
        except Exception as e:
            raise Exception(f"Error creating user: {str(e)}")

    @staticmethod
    def delete_user(user_id):
        try:
            user = UserService.get_user_by_id(user_id)
            if user:
                query_db("DELETE FROM users WHERE id = %s", (user_id,), commit=True)
            return user
        except Exception as e:
            raise Exception(f"Error deleting user: {str(e)}")