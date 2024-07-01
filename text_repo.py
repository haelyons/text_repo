import os
import sys
import argparse
import requests
from github import Github
from io import StringIO

# Blacklist of file extensions
BLACKLIST_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp',
    '.mp3', '.wav', '.ogg', '.flac', '.aac',
    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv',
    '.zip', '.rar', '.7z', '.tar', '.gz',
    '.exe', '.dll', '.so', '.dylib',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.iso', '.bin', '.dat'
}

def is_text_file(filename):
    _, ext = os.path.splitext(filename.lower())
    return ext not in BLACKLIST_EXTENSIONS

def get_local_contents(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if is_text_file(file):
                yield os.path.join(root, file)

def get_local_tree(path, prefix=""):
    tree = ""
    contents = os.listdir(path)
    contents.sort()
    for item in contents:
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            tree += f"{prefix}├── {item}/\n"
            tree += get_local_tree(item_path, prefix + "│   ")
        else:
            tree += f"{prefix}├── {item}\n"
    return tree

def get_repo_contents(repo, path=""):
    contents = repo.get_contents(path)
    return [content for content in contents if content.type != "dir" and is_text_file(content.name)]

def get_repo_tree(repo, path="", prefix=""):
    tree = ""
    contents = repo.get_contents(path)
    for content in contents:
        if content.type == "dir":
            tree += f"{prefix}├── {content.name}/\n"
            tree += get_repo_tree(repo, content.path, prefix + "│   ")
        else:
            tree += f"{prefix}├── {content.name}\n"
    return tree

def main(path, github_token=None):
    try:
        is_local = os.path.exists(path)
        
        if is_local:
            repo_name = os.path.basename(os.path.abspath(path))
            output_filename = f"{repo_name}_concatenated.txt"
            with open(output_filename, "w", encoding="utf-8") as outfile:
                outfile.write("'''---\nRepository Structure:\n\n")
                outfile.write(get_local_tree(path))
                outfile.write("\n'''---\n")

                for file_path in get_local_contents(path):
                    rel_path = os.path.relpath(file_path, path)
                    outfile.write(f"\n'''---\n{rel_path}\n'''---\n")
                    try:
                        with open(file_path, "r", encoding="utf-8") as infile:
                            outfile.write(infile.read())
                        outfile.write("\n")
                    except UnicodeDecodeError:
                        outfile.write(f"[Unable to decode file: {rel_path}]\n")
        else:
            if not github_token:
                raise ValueError("GitHub token is required for remote repositories")
            
            g = Github(github_token)
            repo = g.get_repo(path)
            output_filename = f"{repo.name}_concatenated.txt"
            
            with open(output_filename, "w", encoding="utf-8") as outfile:
                outfile.write("'''---\nRepository Structure:\n\n")
                outfile.write(get_repo_tree(repo))
                outfile.write("\n'''---\n")

                files = get_repo_contents(repo)
                for file in files:
                    if file.type == "file":
                        outfile.write(f"\n'''---\n{file.path}\n'''---\n")
                        try:
                            content = file.decoded_content.decode("utf-8")
                            outfile.write(content)
                            outfile.write("\n")
                        except UnicodeDecodeError:
                            outfile.write(f"[Unable to decode file: {file.path}]\n")

        print(f"Concatenation complete. Output saved to '{output_filename}'")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concatenate files from a local directory or GitHub repository.")
    parser.add_argument("path", help="Local directory path or GitHub repository full name (e.g., 'owner/repo')")
    parser.add_argument("-t", "--token", help="GitHub Personal Access Token (required for GitHub repositories)")
    args = parser.parse_args()

    main(args.path, args.token)
