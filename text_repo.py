import os
import sys
import argparse
import requests
from github import Github
from io import StringIO

def get_repo_contents(repo, path=""):
    contents = repo.get_contents(path)
    return [content for content in contents if content.type != "dir"]

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

def main(github_token, repo_full_name):
    try:
        # GitHub authentication
        g = Github(github_token)

        # Get the repository
        repo = g.get_repo(repo_full_name)

        # Create output file
        output_filename = f"{repo.name}_concatenated.txt"
        with open(output_filename, "w", encoding="utf-8") as outfile:
            # Write the repo tree structure
            outfile.write("'''---\nRepository Structure:\n\n")
            outfile.write(get_repo_tree(repo))
            outfile.write("\n'''---\n")

            # Get all files in the repository
            files = get_repo_contents(repo)

            # Concatenate files
            for file in files:
                if file.type == "file":
                    outfile.write(f"\n'''---\n{file.path}\n'''---\n")
                    content = file.decoded_content.decode("utf-8")
                    outfile.write(content)
                    outfile.write("\n")

        print(f"Concatenation complete. Output saved to '{output_filename}'")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Concatenate files from a GitHub repository.")
    parser.add_argument("token", help="GitHub Personal Access Token")
    parser.add_argument("repo", help="Full name of the repository (e.g., 'owner/repo')")
    args = parser.parse_args()

    main(args.token, args.repo)

