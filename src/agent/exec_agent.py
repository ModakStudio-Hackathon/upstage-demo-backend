import json
import time
from openai import OpenAI
from config import UST_API_KEY, UST_HEADER, UST_AGNT_ID, UST_CNFG_ID


class USTAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=UST_API_KEY,
            base_url=f"https://api.upstage.ai/v2",
            default_headers=UST_HEADER
        )

    def create_job(self, file_id: str) -> str:
        response = self.client.responses.create(
            model=UST_AGNT_ID,
            input=[{"role": "user", "content": [{"type": "input_file", "file_id": file_id}]}],
            extra_body={"config_id": UST_CNFG_ID}
        )
        return response.id

    def wait(self, job_id):
        response = self.client.responses.retrieve(job_id)
        while response.status in {"queued", "in_progress"}:
            time.sleep(1)
            response = self.client.responses.retrieve(job_id)

        if response.status != "completed":
            raise RuntimeError(
                f"Job {job_id} ended with status {response.status}: "
                f"{response.error or 'No error details'}"
            )
        #print(f"Job {job_id} completed.")

        return response

    def get_result(self, response):
        if not response.output:
            raise RuntimeError("No output available.")
        try:
            result = json.loads(response.output_text)
            if isinstance(result, str):
                result = json.loads(result)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse output as JSON: {e}")

        return result

    def run(self, file_id: str):
        job_id = self.create_job(file_id)
        response = self.wait(job_id)
        result = self.get_result(response)
        return result