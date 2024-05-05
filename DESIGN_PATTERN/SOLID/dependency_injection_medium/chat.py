"""
source: https://medium.com/illuin/dependency-injection-made-easy-in-python-45ece11efeca
use opyoid Python package to manage the dependency injection
"""
from typing import List, Optional


class UserMessageSource:
    def get_user_message(self) -> str:
        raise NotImplementedError


class OutputWriter:
    def write_bot_messages(self, bot_messages: List[str]) -> None:
        raise NotImplementedError


class AnswerGenerator:
    def __init__(self):
        self.end_conversation = False

    def get_answers(self, user_message: str) -> List[str]:
        bot_messages = []
        if user_message in ["hello", "hi"]:
            bot_messages.append("Hello there!")
        elif user_message in ["bye", "good bye"]:
            bot_messages.append("See you!")
            self.end_conversation = True
        else:
            bot_messages.append("I'm sorry, I didn't understand that :(")
        return bot_messages


class ConversationLogger:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def append_to_conversation(self, user_message: str, bot_messages: List[str]) -> None:
        with open(self.file_path, "a") as conversation_file:
            conversation_file.write(f"Human: {user_message}\n")
            for message in bot_messages:
                conversation_file.write(f"Bot: {message}\n")


class Chat:
    def __init__(self,
                 user_message_source: UserMessageSource,
                 output_writer: OutputWriter,
                 answer_generator: AnswerGenerator,
                 conversation_logger: Optional[ConversationLogger] = None):
        self.user_message_source = user_message_source
        self.output_writer = output_writer
        self.answer_generator = answer_generator
        self.conversation_logger = conversation_logger

    def run(self):
        while not self.answer_generator.end_conversation:
            user_message = self.user_message_source.get_user_message()
            bot_messages = self.answer_generator.get_answers(user_message)
            self.output_writer.write_bot_messages(bot_messages)
            if self.conversation_logger:
                self.conversation_logger.append_to_conversation(user_message, bot_messages)
