from enum import Enum

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    OLIST = "ordered_list"
    ULIST = "unordered_list"

def markdown_to_blocks(markdown):
    blocks_list = map(lambda block: block.strip(), markdown.split("\n\n"))
    non_empty_blocks = []
    for block in blocks_list:
        if block == "":
            continue
        non_empty_blocks.append(block)
    return non_empty_blocks

def block_to_block_type(block):
    lines = block.split("\n")
    if block[:2] == "# " or block[:3] == "## " or block[:4] == "### " or block[:5] == "#### " or block[:6] == "##### " or block[:7] == "###### ":
        return BlockType.HEADING
    if block[:3] == "```" and block[len(block)-3:] == "```":
        return BlockType.CODE
    if block[0] == ">":
        return BlockType.QUOTE
    if block[:2] == "- ":
        for line in lines:
            if line[:2] != "- ":
                return BlockType.PARAGRAPH
        return BlockType.ULIST
    if block[:3] == "1. ":
        i = 1
        for line in lines:
            if line[:3] != f"{i}. ":
                return BlockType.PARAGRAPH
            i += 1
        return BlockType.OLIST
    return BlockType.PARAGRAPH

