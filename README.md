### Purpose
Turn your local or Github repository into a single text file including a tree, and the contents of all the files. Ignores certain formats, edit these in the blacklist. Outputs an estimated token length to judge suitability for prompting with language models such as Claude 3.5, GPT4o, or Gemini Ultra.  

### Usage
```
usage: python text_repo.py [-h] [-t TOKEN] path

Concatenate files from a local directory or GitHub repository and estimate token count. Claude 3.5 Sonnet has a 120k limit, so this is indicated as a threshold -- strip down your repo in order to get a viable length for prompting and receiving answers. 

Token refers to your Github auth token: navigate to "Settings > Developer settings > Personal access tokens > Tokens (classic)" to generate one and pass it as a command line argument likeso:

python text_repo.py -t eXaMpLeToKeN haelyons/text_repo


positional arguments:
  path                  Local directory path or GitHub repository full name (e.g., 'owner/repo')

options:
  -h, --help            show this help message and exit
  -t TOKEN, --token TOKEN
                        GitHub Personal Access Token (required for GitHub repositories)
```

### Dependencies
```
Run:
pip3 install requests github pygithub
``` 
