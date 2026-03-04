import os
import time
import json
import requests
from dotenv import load_dotenv
from typing import Dict, Any, List

# -------------------------
# Load Environment
# -------------------------

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_KEY")

if not AZURE_ENDPOINT or not AZURE_KEY:
    raise ValueError("Missing AZURE credentials in .env file")

READ_API_URL = f"{AZURE_ENDPOINT}vision/v3.2/read/analyze"

HEADERS = {
    "Ocp-Apim-Subscription-Key": AZURE_KEY,
    "Content-Type": "application/pdf"
}

POLLING_HEADERS = {
    "Ocp-Apim-Subscription-Key": AZURE_KEY
}

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"

CONFIDENCE_THRESHOLD = 0.85


# -------------------------
# Submit Document
# -------------------------

def submit_document(file_path: str) -> str:
    with open(file_path, "rb") as f:
        response = requests.post(READ_API_URL, headers=HEADERS, data=f)

    if response.status_code != 202:
        raise RuntimeError(f"OCR submission failed: {response.text}")

    return response.headers["Operation-Location"]


# -------------------------
# Poll Result
# -------------------------

def poll_result(operation_url: str, timeout: int = 900) -> Dict[str, Any]:
    start = time.time()

    while True:
        response = requests.get(operation_url, headers=POLLING_HEADERS)

        if response.status_code != 200:
            raise RuntimeError("Polling failed")

        result = response.json()
        status = result.get("status")

        print("OCR Status:", status)

        if status == "succeeded":
            return result

        if status == "failed":
            raise RuntimeError("OCR failed")

        if time.time() - start > timeout:
            raise TimeoutError("OCR timed out")

        time.sleep(3)


# -------------------------
# Extract Text
# -------------------------

def extract_text_and_flags(result_json: Dict[str, Any]):
    full_text = []
    low_confidence_lines = []

    pages = result_json["analyzeResult"]["readResults"]

    for page in pages:
        for line in page["lines"]:
            line_text = line["text"]
            full_text.append(line_text)

            confidences = [word["confidence"] for word in line["words"]]
            avg_conf = sum(confidences) / len(confidences)

            if avg_conf < CONFIDENCE_THRESHOLD:
                low_confidence_lines.append({
                    "text": line_text,
                    "confidence": avg_conf
                })

        full_text.append("\n")

    return "\n".join(full_text), low_confidence_lines


# -------------------------
# Ollama Cleanup
# -------------------------

def clean_chunk_with_retry(chunk: str, retries: int = 3) -> str:
    prompt = (
        "You are fixing OCR recognition errors.\n"
        "Correct spelling mistakes caused by OCR.\n"
        "Do NOT paraphrase.\n"
        "Do NOT add explanations.\n"
        "Return corrected text only.\n\n"
        f"{chunk}"
    )

    for attempt in range(retries):
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )

            if response.status_code == 200:
                return response.json()["response"]

        except Exception as e:
            print(f"Retry {attempt+1} failed:", e)

        time.sleep(2)

    raise RuntimeError("Ollama failed after retries")


def clean_text_with_ollama(raw_text: str) -> str:
    print("Starting local LLM cleanup...")

    chunk_size = 3500
    chunks = [raw_text[i:i+chunk_size] for i in range(0, len(raw_text), chunk_size)]

    cleaned_chunks = []

    for i, chunk in enumerate(chunks):
        print(f"Cleaning chunk {i+1}/{len(chunks)}")
        cleaned = clean_chunk_with_retry(chunk)
        cleaned_chunks.append(cleaned)

    return "\n".join(cleaned_chunks)


# -------------------------
# Save Outputs
# -------------------------

def save_outputs(raw_json, raw_text, cleaned_text, flagged_lines):
    with open("raw_ocr_output.json", "w", encoding="utf-8") as f:
        json.dump(raw_json, f, indent=2, ensure_ascii=False)

    with open("raw_text.txt", "w", encoding="utf-8") as f:
        f.write(raw_text)

    with open("cleaned_text.txt", "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    with open("low_confidence_report.json", "w", encoding="utf-8") as f:
        json.dump(flagged_lines, f, indent=2, ensure_ascii=False)

    print("All outputs saved.")


# -------------------------
# Main
# -------------------------

def main():
    if not os.path.exists("input.pdf"):
        raise FileNotFoundError("Place input.pdf in project folder")

    print("Submitting PDF to Azure...")
    operation_url = submit_document("input.pdf")

    print("Waiting for OCR result...")
    result = poll_result(operation_url)

    print("Extracting text...")
    raw_text, flagged_lines = extract_text_and_flags(result)

    print("Low confidence lines:", len(flagged_lines))

    cleaned_text = clean_text_with_ollama(raw_text)

    print("Saving outputs...")
    save_outputs(result, raw_text, cleaned_text, flagged_lines)

    print("Pipeline complete.")


if __name__ == "__main__":
    main()
