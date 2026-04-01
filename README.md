# Cyber Threat Intelligence (CTI) Tools

This repository contains tools for automating Cyber Threat Intelligence (CTI) tasks, including vulnerability scanning and PDF decryption for analysis.

## Project Structure

- `cti-daily-update/`: AWS Serverless application for daily CTI updates.
  - `functions/`: Lambda source code (`nvd.py`, `news.py`, `utils.py`).
  - `keyword_list.txt`: CVE scanning keywords (Product/Vendor).
  - `news_keyword.txt`: News scanning keywords (Attack types/Topics).
- `pdf-decryptor/`: Azure Function for decrypting protected PDF files.

---

## 1. CTI Daily Update (AWS)

Automated scanning from the National Vulnerability Database (NVD) and security news feeds, with reporting via email, Microsoft Teams, or Excel webhooks.

### Prerequisites (AWS)
- [uv](https://github.com/astral-sh/uv) (v0.1.0+)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- Python 3.12+ (managed by `uv` via `.python-version`)

### Local Setup & Configuration
1.  **Initialize Environment:**
    ```bash
    cd cti-daily-update
    uv venv --python 3.12 --seed
    uv sync
    source .venv/bin/activate
    ```
2.  **Configure Environment Variables:**
    Copy `.env.example` to `.env` and fill in your keys. **Note:** The `make deploy` command will automatically sync these values to AWS SSM Parameter Store.
    - `NVD_API_KEY`: Required for higher rate limits on NVD.
    - `GPT_KEY_B64`: Base64 encoded OpenAI key for news summarization.
    - `OPENAI_URL`: API Endpoint (e.g., `https://api.openai.com/v1`).
    - `*_WEBHOOK_URL`: Logic App webhooks for Excel/Email reports.

### Development & Operations
The `Makefile` automates several workflows:

| Command | Description |
| :--- | :--- |
| `make build` | Generates `requirements.txt` and runs `sam build`. |
| `make test-nvd` | **Dry Run:** Runs `functions/nvd.py` locally using `uv run`. |
| `make test-news` | **Dry Run:** Runs `functions/news.py` locally using `uv run`. |
| `make invoke-nvd` | Simulates a full NVD Lambda invocation locally via `sam local invoke`. |
| `make invoke-news` | Simulates a full News Lambda invocation locally via `sam local invoke`. |
| `make deploy` | Builds, **updates AWS SSM parameters from `.env`**, and deploys via SAM. |

### Refining Search Keywords
- **CVE Scan:** Edit `keyword_list.txt`. Add products or vendors (e.g., `Cisco`, `Fortinet`).
- **News Scan:** Edit `news_keyword.txt`. Add attack types or groups (e.g., `Ransomware`, `APT`).

---

## 2. PDF Decryptor (Azure)

An Azure Function that decrypts password-protected PDFs and extracts text for CTI analysis.

### Prerequisites (Azure)
- [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)

### API Usage
- **Endpoint:** `POST /api/decrypt_pdf`
- **Request Body:**
  ```json
  {
    "file_content": "<base64_encoded_pdf>",
    "password": "<pdf_password>"
  }
  ```
- **Response:** `{"text": "..."}` (Extracted text content).

### Deployment & Local Dev
1.  **Local Development:**
    ```bash
    cd pdf-decryptor
    # Create venv and install dependencies
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    # Start the function locally
    func start
    ```
2.  **Cloud Deployment:**
    Ensure you are logged in to Azure (`az login`), then run:
    ```bash
    func azure functionapp publish EventCall --python
    ```

---

## Security Note
- Never commit your `.env` file.
- Sensitive credentials for AWS are managed via **SSM Parameter Store** (automatically updated during `make deploy`).
