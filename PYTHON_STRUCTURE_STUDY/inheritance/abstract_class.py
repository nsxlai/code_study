from abc import ABCMeta, abstractmethod


class Book(object, metaclass=ABCMeta):
    def __init__(self, title, author):
        self.title  =title
        self.author = author

    @abstractmethod
    def display(): pass


#Write MyBook class
class MyBook(Book):
    def __init__(self, title, author, price):
        super().__init__(title, author)
        self.price = price

    def display(self):
        print(f'Title: {self.title}')
        print(f'Author: {self.author}')
        print(f'Price: {self.price}')


if __name__ == '__main__':
    # title=input()
    # author=input()
    # price=int(input())
    # new_novel=MyBook(title,author,price)
    # new_novel.display()

    novel1 = MyBook('The Alchemist', 'Paulo Coelho', 248)
    novel1.display()

    novel2 = MyBook('The Theory', 'John Smith', 100)
    novel2.display()