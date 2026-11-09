from pathlib import Path
from openai import OpenAI
from config import UST_API_KEY, UST_HEADER, UST_AGNT_ID


def upload(file_path: str) -> str:
    """
    Uploads a file to the Upstage API and returns the file ID.

    Args:
        file_path (str): The path to the file to be uploaded.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    with open(file_path, "rb") as f:
        try:
            client = OpenAI(
                api_key=UST_API_KEY,
                base_url=f"https://api.upstage.ai/v2",
                default_headers=UST_HEADER,
            )

            response = client.files.create(file=f, purpose="user_data")

            return response.id
        except Exception as e:
            raise RuntimeError(f"Failed to upload file: {e}")
