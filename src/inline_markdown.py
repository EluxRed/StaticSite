import re
from textnode import TextType, TextNode

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    supported_delimiters = ["**", "_", "`"]
    if not(delimiter in supported_delimiters):
        raise ValueError(f"invalid delimiter: {delimiter}")
    supported_text_types = [TextType.BOLD, TextType.ITALIC, TextType.CODE]
    if not(text_type in supported_text_types):
        raise ValueError(f"invalid text type: {text_type}")
    
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
        else:
            if node.text.count(delimiter)%2 != 0:
                raise SyntaxError(f"invalid markdown syntax: closing delimiter {delimiter} not found")
            new_nodes_strings = node.text.split(delimiter)
            counter = 0
            for new_node_text in new_nodes_strings:
                if new_nodes_strings[counter] == "":
                    counter += 1
                    continue
                if counter%2 == 0:
                    new_nodes.append(TextNode(new_node_text, TextType.TEXT))
                else:
                    new_nodes.append(TextNode(new_node_text, text_type))
                counter += 1
    return new_nodes

def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def split_nodes_image_or_link(old_nodes, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
        else:
            match text_type:
                case TextType.IMAGE:
                    tuples_list = extract_markdown_images(node.text)
                case TextType.LINK:
                    tuples_list = extract_markdown_links(node.text)
                case _:
                    raise ValueError(f"invalid text type: {text_type}")
            if len(tuples_list) == 0:
                new_nodes.append(node)
                continue
            text_to_split = node.text
            for tuple in tuples_list:
                text = tuple[0]
                url = tuple[1]
                if text_type == TextType.IMAGE:
                    separator = f"![{text}]({url})"
                else: # TextType.Link    
                    separator = f"[{text}]({url})"
                sections = text_to_split.split(separator, maxsplit=1)
                text_to_split = sections[1]
                if sections[0] != "":
                    new_nodes.append(TextNode(sections[0], TextType.TEXT))
                new_nodes.append(TextNode(text, text_type, url))
            if text_to_split != "":
                new_nodes.append(TextNode(text_to_split, TextType.TEXT))
    return new_nodes

def split_nodes_image(old_nodes):
    return split_nodes_image_or_link(old_nodes, TextType.IMAGE)

def split_nodes_link(old_nodes):
    return split_nodes_image_or_link(old_nodes, TextType.LINK)

def text_to_textnodes(text):
    nodes = split_nodes_delimiter([TextNode(text, TextType.TEXT)], "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes