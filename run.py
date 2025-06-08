import os
from llmsec.database     import MySQLDatabase
from llmsec.mitigation   import ChatGPTClient
from llmsec.chat_session import ChatSession
from llmsec.policy import load_policy

def main():
    # —————— connect & seed your single MySQL instance ——————
    db = MySQLDatabase(
        host="db-430.c52weece2t3h.eu-north-1.rds.amazonaws.com",
        user="admin",
        password="Soydino1907.?02",
        database="db-430"
    )

    # —————— init OpenAI client ——————
    client = ChatGPTClient(api_key=os.getenv("OPENAI_API_KEY"))

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
    POLICY = load_policy("permissions.json")
    session = ChatSession(client, db, user_id, policy=POLICY)

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