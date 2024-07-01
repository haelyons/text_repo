import os
import sys
import argparse
import requests
from github import Github
from io import StringIO
import re
import tokenize
from io import BytesIO

BLACKLIST_EXTENSIONS = {
    # Images
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp',
    # Audio
    '.mp3', '.wav', '.ogg', '.flac', '.aac',
    # Video
    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv',
    # Archives
    '.zip', '.rar', '.7z', '.tar', '.gz',
    # Executables
    '.exe', '.dll', '.so', '.dylib',
    # Other binary formats
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.iso', '.bin', '.dat'
}

def estimate_tokens(text):
    def is_likely_code(text):
        code_patterns = [
            r'\bdef\b', r'\bclass\b', r'\bif\b.*:', r'\bfor\b.*:', r'\bwhile\b.*:',
            r'\bimport\b', r'\bfrom\b.*\bimport\b', r'^\s*@', r'^\s*#',
            r'\b(var|let|const)\b', r'\bfunction\b', r'\breturn\b',
            r'\bpublic\b', r'\bprivate\b', r'\bprotected\b', r'\bstatic\b',
            r'\b(int|float|double|string|bool|void)\b'
        ]
        return any(re.search(pattern, text, re.MULTILINE) for pattern in code_patterns)

    if is_likely_code(text):
        try:
            token_count = 0
            # Use generate_tokens instead of tokenize for more robustness
            for tok in tokenize.generate_tokens(StringIO(text).readline):
                if tok.type not in {tokenize.COMMENT, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING}:
                    token_count += 1
            return token_count
        except tokenize.TokenError:
            # If tokenizing as Python code fails, fall back to the generic method
            pass
        except IndentationError:
            # If there's an indentation error, fall back to the generic method
            pass

    # Generic tokenization for non-code or if code tokenization fails
    words = re.findall(r'\w+|[^\w\s]', text)
    return len(words)

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
        total_tokens = 0
        
        if is_local:
            repo_name = os.path.basename(os.path.abspath(path))
            output_filename = f"{repo_name}_concatenated.txt"
            with open(output_filename, "w", encoding="utf-8") as outfile:
                outfile.write("'''---\nRepository Structure:\n\n")
                tree = get_local_tree(path)
                outfile.write(tree)
                total_tokens += estimate_tokens(tree)
                outfile.write("\n'''---\n")

                for file_path in get_local_contents(path):
                    rel_path = os.path.relpath(file_path, path)
                    outfile.write(f"\n'''---\n{rel_path}\n'''---\n")
                    try:
                        with open(file_path, "r", encoding="utf-8") as infile:
                            content = infile.read()
                            outfile.write(content)
                            total_tokens += estimate_tokens(content)
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
                tree = get_repo_tree(repo)
                outfile.write(tree)
                total_tokens += estimate_tokens(tree)
                outfile.write("\n'''---\n")

                files = get_repo_contents(repo)
                for file in files:
                    if file.type == "file":
                        outfile.write(f"\n'''---\n{file.path}\n'''---\n")
                        try:
                            content = file.decoded_content.decode("utf-8")
                            outfile.write(content)
                            total_tokens += estimate_tokens(content)
                            outfile.write("\n")
                        except UnicodeDecodeError:
                            outfile.write(f"[Unable to decode file: {file.path}]\n")

        # Add token estimation to the end of the file
        with open(output_filename, "a", encoding="utf-8") as outfile:
            outfile.write(f"\n'''---\nEstimated total tokens: {total_tokens}\n'''---\n")

        print(f"Concatenation complete. Output saved to '{output_filename}'")
        print(f"Estimated total tokens: {total_tokens}")
        
        if total_tokens > 120000:
            print(f"\nTotal tokens is above current limit for Claude 3.5 Opus, consider filtering your repository")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concatenate files from a local directory or GitHub repository.")
    parser.add_argument("path", help="Local directory path or GitHub repository full name (e.g., 'owner/repo')")
    parser.add_argument("-t", "--token", help="GitHub Personal Access Token (required for GitHub repositories)")
    args = parser.parse_args()

    main(args.path, args.token)
