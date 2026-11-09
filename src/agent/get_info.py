"""
파일을 업로드하여 속성을 출력한다.

python get_info.py testData.pdf


"""

from pathlib import Path
import argparse
import json

from config import check_envs
from upload import upload
from exec_agent import USTAgent


def main():
    print("Starting the file upload and processing...")

    parser = argparse.ArgumentParser(
        description="Upload a file and get its properties."
    )
    parser.add_argument("file_path", type=str, help="Path to the file to be uploaded.")
    args = parser.parse_args()

    check_envs()

    file_path = args.file_path
    if not Path(file_path).exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    # 업로드 성공 사 파일 id 출력
    file_id = upload(file_path)
    print(f"File uploaded successfully\t(ID: {file_id})")

    # 에이전트 실행
    agent = USTAgent()
    result = agent.run(file_id)

    # JSON 형태 출력
    print("Result:")
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()
