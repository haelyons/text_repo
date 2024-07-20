### Purpose
Turn your local or Github repository into a single text file including a tree, and the contents of all the files. Ignores certain formats, and you can edit these in the blacklist. Your Github token (if used) will be stored in a local JSON. 

Program also outputs an estimated token length to judge suitability for prompting with language models such as Claude 3.5, GPT4o, or Gemini Ultra.  

### Usage
Concatenate files from a local directory or GitHub repository and estimate token count. Claude 3.5 Sonnet has a 120k limit, but on free mode you can enter messages up to 15-20k tokens. Strip down your repo in order to get a viable length for prompting and receiving answers, and set the limit to be added to the file.

Token refers to your Github auth token: navigate to "Settings > Developer settings > Personal access tokens > Tokens (classic)" to generate one and pass it as a command line argument `-t`.

General usage:
```
usage: text_repo.py [-h] [-t TOKEN] [-l LIMIT] path

Concatenate files from a local directory or GitHub repository.

positional arguments:
  path                  Local directory path or GitHub repository full name (e.g., 'owner/repo')

options:
  -h, --help            show this help message and exit
  -t TOKEN, --token TOKEN
                        GitHub Personal Access Token (required for GitHub repositories)
  -l LIMIT, --limit LIMIT
                        Token limit for partial concatenation (default: 15000)
```

Local example:
```
git clone https://github.com/haelyons/text_repo.git
cd ./text_repo
python text_repo.py ~/your_repo_path/
```

Github example:
```
git clone https://github.com/haelyons/text_repo.git
cd ./text_repo
# Example using a sample, randomly generated token - replace the repo with one of your own (or a public repo)
python text_repo.py -t ghp_Rx9fKmLpYjHqNvS3Zw7eBcAd5UoT1iW8nDgE haelyons/challenger_rp2040_wearable
# Future usage won't require your token again
python text_rep.py haelyons/challenger_rp2040_wearable  
```
## Dependencies
Run the following, depends on your Python installation. 
```
pip install python-docx 
pip install requests github pygithub
```

## Todo
- Exclude .git from tree 
