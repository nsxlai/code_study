from opyoid import ClassBinding, Injector, InstanceBinding

from chat import AnswerGenerator, Chat, ConversationLogger, OutputWriter, UserMessageSource
from method_1_simple import CliOutputWriter, CliUserMessageSource


if __name__ == "__main__":
    injector = Injector(bindings=[
        ClassBinding(Chat),
        ClassBinding(AnswerGenerator),
        InstanceBinding(ConversationLogger, ConversationLogger("file.txt")),
        ClassBinding(CliUserMessageSource),
        ClassBinding(CliOutputWriter),
    ])
    chat = injector.inject(Chat)
    chat.run()
