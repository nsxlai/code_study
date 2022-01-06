from dataclasses import dataclass
from random import random
from time import sleep
from typing import List

from chat import AnswerGenerator, Chat, OutputWriter, UserMessageSource


@dataclass
class MqConfig:
    host: str
    port: int
    username: str
    password: str


class MqUserMessageSource(UserMessageSource):
    def __init__(self, config: MqConfig):
        self.config = config

    def get_user_message(self) -> str:
        return self.poll_messages()

    def poll_messages(self) -> str:
        # Fake method, real implementation would use the MqConfig
        sleep(1)
        return "hi" if random() > 0.2 else "bye"


class MqOutputWriter(OutputWriter):
    def __init__(self, config: MqConfig):
        self.config = config

    def write_bot_messages(self, bot_messages: List[str]) -> None:
        for message in bot_messages:
            self.produce_message(message)

    def produce_message(self, message: str) -> None:
        # Fake method, real implementation would use the MqConfig
        pass


if __name__ == "__main__":
    mq_config = MqConfig(
        "localhost",
        1234,
        "mq_user",
        "my_password",
    )
    Chat(
        MqUserMessageSource(mq_config),
        MqOutputWriter(mq_config),
        AnswerGenerator(),
    ).run()
