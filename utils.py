user_query = None

def set_user_query(query: str) -> str:
    global user_query
    user_query = query

def get_user_query() -> str:
    global user_query
    return user_query