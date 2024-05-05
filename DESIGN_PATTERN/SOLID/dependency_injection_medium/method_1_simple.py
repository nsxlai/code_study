from typing import List

from chat import AnswerGenerator, Chat, ConversationLogger, OutputWriter, UserMessageSource


class CliUserMessageSource(UserMessageSource):
    def get_user_message(self) -> str:
        return input("Human: ").strip().lower()


class CliOutputWriter(OutputWriter):
    def write_bot_messages(self, bot_messages: List[str]) -> None:
        for message in bot_messages:
            print(f"Bot: {message}")


if __name__ == "__main__":
    Chat(
        CliUserMessageSource(),
        CliOutputWriter(),
        AnswerGenerator(),
        ConversationLogger("logs.txt")
    ).run()
