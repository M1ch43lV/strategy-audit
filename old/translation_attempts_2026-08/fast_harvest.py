import json, os, subprocess

import concurrent.futures



def main():

    root = os.path.dirname(os.path.abspath(__file__))

    repos_dir = os.path.join(root, "repos")

    os.makedirs(repos_dir, exist_ok=True)

    

    with open(os.path.join(root, "corpus_sources.json"), "r", encoding="utf-8") as f:

        data = json.load(f)

    

    repos = [item["repo"] for item in data["repos"]]

    

    def clone_repo(repo):

        dirname = repo.replace("/", "_", 1)

        target = os.path.join(repos_dir, dirname)

        if os.path.exists(target):

            return f"Exists: {dirname}"

        

        cmd = ["git", "clone", "--depth", "1", f"https://github.com/{repo}.git", target]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:

            return f"Success: {repo}"

        else:

            return f"Failed: {repo} - {result.stderr.strip()}"



    print(f"Cloning {len(repos)} repos concurrently...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:

        for result in executor.map(clone_repo, repos):

            print(result)

            

if __name__ == "__main__":

    main()

