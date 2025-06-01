import os, time

def gitTask():
    print("[gitt.py] Starting git operations to save URL data...")
    all_output = ""
    
    print("[gitt.py] Changing directory to newspaper-bot-urls")
    os.chdir("newspaper-bot-urls")
    
    current_dir = os.getcwd()
    print(f"[gitt.py] Current working directory: {current_dir}")

    commands = [
        "pwd",
        f'git config --global user.name "{os.environ.get("NEWSPAPER_URLS_USERNAME")}"',
        f'git config --global user.email "{os.environ.get("NEWSPAPER_URLS_USEREMAIL")}"',
        "git add .",
        'git commit -m "Added urls"',
        f"git push https://{os.environ.get('NEWSPAPER_URLS_GIT_USERNAME')}:{os.environ.get('GIT_TOKEN')}@github.com/{os.environ.get('NEWSPAPER_URLS_GIT_USERNAME')}/{os.environ.get('NEWSPAPER_URLS_GIT_REPO')}.git --all"
    ]
    
    for i, cmd in enumerate(commands):
        # Hide sensitive command that contains tokens
        safe_cmd = cmd if "GIT_TOKEN" not in cmd else "[GIT PUSH COMMAND WITH AUTH TOKEN]"
        print(f"[gitt.py] Executing git command {i+1}/{len(commands)}: {safe_cmd}")
        
        time.sleep(1)
        output = os.popen(cmd).read()
        print(f"[gitt.py] Command output:\n{output}")
        all_output += output
    
    print("[gitt.py] Git operations completed successfully")
    return all_output