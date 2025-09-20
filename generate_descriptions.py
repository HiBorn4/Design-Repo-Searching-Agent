
import os
import json
from pathlib import Path
from openai import AzureOpenAI
from dotenv import load_dotenv

# --------- Load credentials ---------
load_dotenv()
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT")

client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-10-01-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# --------- CONFIG ---------
ROOT_DIR = Path("../")  # DESIGN-REPO
OUTPUT_DIR = Path("./auto_outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MASTER_FILE = Path("../__All_Errors.txt")

VALID_EXTS = [".png", ".jpg", ".jpeg", ".svg", ".gif", ".pdf", ".ppt", ".pptx"]

CATEGORIES = [
    "Icon repository",
    "Emailer & Newsletters",  # Fixed HTML entity
    "Internal Logos",
    "Mahindra Branding Guideline",
    "PPT Repository"
]

# --------- PROMPT TEMPLATE ---------
DESCRIPTION_PROMPT = """
I want you to generate a detailed, elaborated description of the given file.
Follow these rules:

1. Understand what the asset could represent (icon, logo, newsletter, PPT, branding file, etc.).
2. Explain its purpose and potential use in design/branding.
3. If the filename suggests a color gradient (e.g., red, white, blue), describe the color scheme.
4. If it’s an image, describe what it visually represents (symbol, shape, object).
5. If it’s a document (ppt, branding guideline, etc.), explain what kind of content might be inside.
6. Output in a human-friendly sentence or two, not just repeating the file name.

File to describe: {filename}
"""

def generate_description(file_path: Path) -> str:
    try:
        prompt = DESCRIPTION_PROMPT.format(filename=file_path.name)
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are an assistant that intelligently describes design and branding assets."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

def process_category(category: Path, output_file: Path):
    results = {}

    print(f"\n📂 Scanning category: {category}")
    if not category.exists():
        print(f"⚠️ Folder missing: {category}")
        category.mkdir(parents=True, exist_ok=True)
        print(f"📁 Created missing folder: {category}")

    for root, _, files in os.walk(category):
        for f in files:
            if Path(f).suffix.lower() in VALID_EXTS:
                file_path = Path(root) / f
                desc = generate_description(file_path)
                results[str(file_path)] = desc
                print(f"✅ {file_path} -> {desc}")

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"💾 JSON saved: {output_file.resolve()}")
    except Exception as e:
        print(f"❌ Failed to write JSON: {e}")

def main():
    master_log = []

    for cat in CATEGORIES:
        folder = ROOT_DIR / cat
        out_file = OUTPUT_DIR / f"{cat.replace(' ', '_').lower()}.json"
        process_category(folder, out_file)
        master_log.append(f"{folder} -> {out_file}")

    try:
        with open(MASTER_FILE, "a", encoding="utf-8") as mf:
            mf.write("\n".join(master_log) + "\n")
        print(f"\n📝 Master log updated: {MASTER_FILE.resolve()}")
    except Exception as e:
        print(f"❌ Failed to update master log: {e}")

    print("\n🎉 Finished scanning all categories. JSON files are in ./auto_outputs/")

if __name__ == "__main__":
    main()
