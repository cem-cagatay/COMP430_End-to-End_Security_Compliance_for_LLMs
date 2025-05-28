from llmsec.database     import MySQLDatabase
from llmsec.mitigation   import ChatGPTClient
from llmsec.chat_session import ChatSession

def main():
    # —————— connect & seed your single MySQL instance ——————
    db = MySQLDatabase(
        host="localhost",
        user="admin",
        password="Soydino1907.?02",
        database="db-430"
    )

    # —————— init OpenAI client ——————
    client = ChatGPTClient()  # reads OPENAI_API_KEY from env

    # —————— user login ——————
    raw = input("Enter your user ID (or 'exit' to quit): ").strip()
    if raw.lower() in ("exit", "quit"):
        print("Goodbye.")
        return

    try:
        user_id = int(raw)
    except ValueError:
        print("✘ Invalid user ID. Exiting.")
        return

    role = db.get_user_role(user_id)
    if not role:
        print(f"✘ No user found with ID={user_id}. Exiting.")
        return

    print(f"✔ Logged in as user {user_id} ({role}).")
    print("Type any prompt to send to ChatGPT. (Type 'exit' or 'quit' to end.)\n")

    # —————— start chat session ——————
    session = ChatSession(client, db, user_id)

    while True:
        prompt = input("You: ").strip()
        if prompt.lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        reply = session.send(prompt)
        print(f"Assistant: {reply}\n")

    db.close()

if __name__ == "__main__":
    main()