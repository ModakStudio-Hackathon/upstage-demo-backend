import mimetypes
from pathlib import Path
from typing import BinaryIO

from openai import OpenAI
from .config import UST_API_KEY, UST_HEADER


def upload(
    source: str | Path | BinaryIO,
    filename: str | None = None,
    content_type: str | None = None,
) -> str:
    """
    Upload a local path or binary stream to Upstage and return its file ID.

    Args:
        source: Local file path or an open binary file stream.
        filename: Name used for a binary stream upload.
        content_type: MIME type used for a binary stream upload.
    """
    if isinstance(source, (str, Path)):
        file_path = Path(source)
        if not file_path.is_file():
            raise FileNotFoundError(f"The file {file_path} does not exist.")

        with file_path.open("rb") as file_stream:
            return _upload_stream(
                file_stream,
                filename=filename or file_path.name,
                content_type=content_type,
            )

    return _upload_stream(
        source,
        filename=filename or "receipt-image",
        content_type=content_type,
    )


def _upload_stream(
    file_stream: BinaryIO,
    *,
    filename: str,
    content_type: str | None,
) -> str:
    try:
        media_type = (
            content_type
            or mimetypes.guess_type(filename)[0]
            or "application/octet-stream"
        )
        client = OpenAI(
            api_key=UST_API_KEY,
            base_url="https://api.upstage.ai/v2",
            default_headers=UST_HEADER,
        )
        response = client.files.create(
            file=(filename, file_stream, media_type),
            purpose="user_data",
        )
        return response.id
    except Exception as e:
        raise RuntimeError(f"Failed to upload file: {e}") from e
