import os
import argparse
from huggingface_hub import HfApi, create_repo, login

def deploy_to_hf(repo_name: str, token: str):
    api = HfApi(token=token)
    
    # Create the repository if it doesn't exist
    try:
        create_repo(
            repo_id=repo_name,
            token=token,
            repo_type="space",
            space_sdk="docker",
            private=False,
            exist_ok=True
        )
        print(f"Space '{repo_name}' is ready.")
    except Exception as e:
        print(f"Error creating/finding space: {e}")
        return

    # Upload the entire directory
    print(f"Uploading files to https://huggingface.co/spaces/{repo_name} ...")
    api.upload_folder(
        folder_path=".",
        repo_id=repo_name,
        repo_type="space",
        path_in_repo=".",
        ignore_patterns=["__pycache__", ".git", ".env"]
    )
    print("Upload complete! The space will build and start automatically.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy OpenEnv to HF Spaces")
    parser.add_argument("--repo", type=str, help="HF repository name (e.g., 'username/openenv-support')")
    args = parser.parse_args()

    token = os.getenv("HF_TOKEN")
    if not token:
        print("HF_TOKEN environment variable not set. Cannot deploy.")
    elif not args.repo:
        print("Please provide a repository name with --repo 'username/repo-name'")
    else:
        deploy_to_hf(args.repo, token)
