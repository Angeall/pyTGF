import os
from os.path import join
from typing import List, Union


def to_file_name(name: str) -> str:
    lower_name = name.lower()
    return lower_name.replace(" ", "")


def to_camel_case(name: str, is_class: bool=False) -> str:
    name = name.lower()
    camel_case = ""
    name_lst = name.split()
    for i, word in enumerate(name_lst):
        if is_class or i != 0:
            word = word.title()
        camel_case += word
    return camel_case


def create_module(name: str):
    os.mkdir(name)
    f = open(join(name, "__init__.py"), "w")
    f.close()


def write_file(code: str, file_name: str):
    core_file = open(file_name, "w")
    core_file.write(code)
    core_file.close()


class CodeBlock:
    def __init__(self, head: str, blocks: List[Union['CodeBlock', str]], decorators: List[str] = None,
                 comment_lines: List[str] = None, class_level: bool = False):
        self.head = head
        self.block = blocks
        self.decorators = decorators
        self.commentLines = comment_lines
        self.classLevel = class_level

    def __str__(self, indent: str = "") -> str:
        result = ""
        if self.decorators is not None:
            for decorator in self.decorators:
                result += indent + decorator + "\n"
        result += indent + self.head + ":\n"
        indent += "    "
        if self.commentLines is not None:
            result += indent + '\"\"\"\n'
            for comment_line in self.commentLines:
                result += indent + comment_line + '\n'
            result += indent + '\"\"\"\n'
        for block in self.block:
            if isinstance(block, CodeBlock):
                result += block.__str__(indent)
            else:
                result += indent + block + "\n"
            if self.classLevel:
                result += '\n'
        return result