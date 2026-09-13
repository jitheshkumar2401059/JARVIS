from brain.gemini import GeminiBrain


def main():

    jarvis = GeminiBrain()

    print("JARVIS: Online. How may I assist you?")

    while True:

        user_input = input("\nYou: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("JARVIS: Goodbye.")
            break

        if not user_input:
            continue

        try:

            response = jarvis.ask(user_input)

            print("JARVIS: ", end="")

            for chunk in response:

                if chunk.text:
                    print(
                        chunk.text,
                        end="",
                        flush=True
                    )

            print()

        except Exception as error:

            print(
                "\nJARVIS: "
                "I'm unable to complete that request right now."
            )

            print(
                "Developer information:",
                error
            )


if __name__ == "__main__":
    main()