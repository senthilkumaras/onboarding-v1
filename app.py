from master_agent import (
    init_state,
    welcome,
    start_topic,
    handle_user_message,
    continue_to_next_topic,
)

def main():
    state = init_state()

    # Welcome
    state = welcome(state)
    print("\nAGENT:", state["assistant_message"])

    # Start first topic (Company Basics)
    state = start_topic(state)
    print("\nAGENT:", state["assistant_message"])

    while not state.get("is_done"):
        user = input("\nYOU: ").strip()

        # Simple commands
        if user.lower() in ("exit", "quit"):
            print("AGENT: Bye!")
            break

        if user.lower() in ("continue", "next", "yes"):
            state = continue_to_next_topic(state)
            print("\nAGENT:", state["assistant_message"])
            continue

        # Normal message
        state["user_message"] = user
        state = handle_user_message(state)
        print("\nAGENT:", state["assistant_message"])

        if state.get("pause_requested"):
            print("AGENT: We paused. Come back when ready.")
            break


if __name__ == "__main__":
    main()
