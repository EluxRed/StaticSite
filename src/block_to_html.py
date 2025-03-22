from textnode import text_node_to_html_node, TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode
from inline_markdown import text_to_textnodes
from markdown_blocks import markdown_to_blocks, block_to_block_type, BlockType

def heading_block_to_header_number(block):
    if block[:2] == "# ":
        return 1
    if block[:3] == "## ":
        return 2
    if block[:4] == "### ":
        return 3
    if block[:5] == "#### ":
        return 4
    if block[:6] == "##### ":
        return 5
    if block[:7] == "###### ":
        return 6
    raise ValueError(f"invalid heading block, first 6 characters are: {block[:7]}")

def block_type_to_HTML_node(block_type, children, tag = None):
    match block_type:
        case BlockType.PARAGRAPH:
            return ParentNode("p", children)
        case BlockType.HEADING:
            return ParentNode(tag, children)
        case BlockType.CODE:
            return ParentNode("pre", children)
        case BlockType.QUOTE:
            return ParentNode("blockquote", children)
        case BlockType.OLIST:
            return ParentNode("ol", children)
        case BlockType.ULIST:
            return ParentNode("ul", children)
        case _:
           raise ValueError(f"invalid BlockType: {block_type}")

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for node in text_nodes:
        html_node = text_node_to_html_node(node)
        children.append(html_node)
    return children
    
def block_to_text(block):
    block_type = block_to_block_type(block)
    lines = block.split("\n")
    match block_type:
        case BlockType.PARAGRAPH:
            return " ".join(lines)
        case BlockType.HEADING:
            return " ".join(lines)[heading_block_to_header_number(block)+1:]
        case BlockType.CODE:
            start = 3
            end = len(block)-2
            if block[3] == "\n":
                start = 4
            if block[len(block)-4] == "\n":
                end = len(block)-3
            return block[start:end]
        case BlockType.QUOTE:
            return " ".join(list(map(lambda line: line[2:] if line.startswith("> ") else line, lines)))
        case _:
            raise ValueError(f"invalid BlockType: {block_type}")
        
def list_block_to_text_lines(block):
    block_type = block_to_block_type(block)
    lines = block.split("\n")
    match block_type:
        case BlockType.OLIST:
            text_lines = []
            for line in lines:
                text_lines.append(line[3:])
            return text_lines
        case BlockType.ULIST:
            text_lines = []
            for line in lines:
                text_lines.append(line[2:])
            return text_lines
        case _:
            raise ValueError(f"invalid BlockType: {block_type}")

def markdown_to_html_node(markdown):
    blocks_list = markdown_to_blocks(markdown)
    html_nodes = []
    for block in blocks_list:
        block_type = block_to_block_type(block)
        if block_type == BlockType.OLIST or block_type == BlockType.ULIST:
            text_lines = list_block_to_text_lines(block)
            list_children = []
            for text in text_lines:
                children = text_to_children(text)
                list_children.append(ParentNode("li", children))
            html_nodes.append(block_type_to_HTML_node(block_type, list_children))
        else: 
            text = block_to_text(block)
            if block_type == BlockType.CODE:
                text_node = TextNode(text, TextType.CODE)
                children = [text_node_to_html_node(text_node)]
                html_nodes.append(block_type_to_HTML_node(block_type, children))
            else:
                children = text_to_children(text)
                if block_type == BlockType.HEADING:
                    html_nodes.append(block_type_to_HTML_node(block_type, children, tag=f"h{heading_block_to_header_number(block)}"))
                else: #PARAGRAPH, QUOTE
                    html_nodes.append(block_type_to_HTML_node(block_type, children))
    return ParentNode("div", html_nodes)

def extract_title(markdown):
    blocks = markdown_to_blocks(markdown)
    h1_block = None
    for block in blocks:
        if block_to_block_type(block) == BlockType.HEADING:
            if heading_block_to_header_number(block) == 1:
                h1_block = block
    if h1_block == None:
        raise Exception("h1 header not found")
    return block_to_text(h1_block).strip()
