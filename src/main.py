from pathlib import os
import shutil
from block_to_html import markdown_to_html_node, extract_title

def main():
    copy_from_source_to_destination("static/", "public/")
    generate_pages_recursive("content/", "template.html", "public/")

def copy_from_source_to_destination(source, destination):
    if not(os.path.exists(source)):
        raise Exception("invalid source directory path")
    if os.path.exists(destination):
        shutil.rmtree(destination)
    os.mkdir(destination)
    copy_recursive(source, destination)
        
def copy_recursive(source, destination):
    for elem in os.listdir(source):
        elem_path = os.path.join(source, elem)
        dest_path = os.path.join(destination, elem)
        if os.path.isfile(elem_path):
            shutil.copy(elem_path, dest_path)
            print(f"Copied: {elem_path} to {dest_path}")
        else:
            os.mkdir(dest_path)
            copy_recursive(elem_path, dest_path)

def file_contents(path):
    file = open(path)
    contents = file.read()
    file.close()
    return contents

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    markdown = file_contents(from_path)
    template = file_contents(template_path)
    html_node = markdown_to_html_node(markdown)
    html_string = html_node.to_html()
    title = extract_title(markdown)
    new_file_content = template.replace("{{ Title }}", title).replace("{{ Content }}", html_string)
    dest_directory = os.path.dirname(dest_path)
    if not(os.path.exists(dest_directory)):
        os.makedirs(dest_directory, exist_ok=True)
    new_file = open(dest_path, "w")
    new_file.write(new_file_content)
    new_file.close()

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    for entry in os.listdir(dir_path_content):
        entry_path = os.path.join(dir_path_content, entry)
        if os.path.isfile(entry_path):
            if entry.endswith(".md"):
                file_name = entry[:-3] + ".html"
                dest_path = os.path.join(dest_dir_path, file_name)
                generate_page(entry_path, template_path, dest_path)
        else:
            dest_path = os.path.join(dest_dir_path, entry)
            generate_pages_recursive(entry_path, template_path, dest_path)


main()