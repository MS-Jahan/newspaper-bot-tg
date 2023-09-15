import os, time

def gitTask():
    all_output = ""
    os.chdir("newspaper-bot-urls")

    print(str(os.getcwd()))

    commands = [
        "pwd",
        f'git config --global user.name "{os.environ.get("NEWSPAPER_URLS_USERNAME")}"',
        f'git config --global user.email "{os.environ.get("NEWSPAPER_URLS_USEREMAIL")}"',
        "git add .",
        'git commit -m "Added urls"',
        f"git push https://{os.environ.get('NEWSPAPER_URLS_GIT_USERNAME')}:{os.environ.get('GIT_TOKEN')}@github.com/{os.environ.get('NEWSPAPER_URLS_GIT_USERNAME')}/{os.environ.get('NEWSPAPER_URLS_GIT_REPO')}.git --all"
    ]

    for cmd in commands:
        time.sleep(1)
        output = os.popen(cmd).read()
        print(output)
        all_output += output
    
    return all_output