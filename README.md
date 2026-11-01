# BuildSight AI — Construction Intelligence Capstone

An educational Streamlit capstone application aligned to a multimodal construction intelligence concept.

## Modules
1. **Site Safety & PPE:** Upload a site photo for an optional Gemini-powered interpretation or a labelled demo checklist.
2. **Crack & Defect Review:** Photo interpretation with limitations and professional escalation guidance.
3. **Cost Planning:** Editable construction budget, progress-based spend, contingency, indicative market value, and rough material planning.
4. **Weather-Aware Assistant:** Safety checklist for normal weather, high winds, heavy rain, and extreme heat, plus optional AI Q&A.
5. **Exports:** Download image review reports as TXT and estimates as JSON.

## Run locally
Requires Python 3.10 or newer.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Optional Gemini AI
1. Create an API key in Google AI Studio.
2. Start the app and enter the key in the sidebar.
3. Uploaded images and prompts are sent to the Gemini API for interpretation.
4. Never put API keys in source code or commit them to GitHub.

Without a key, the app runs in demo mode. **Demo image-review outputs are examples and do not analyze image pixels.**

## Deploy for a live demo
1. Create a public repository at https://github.com/new named `BuildSight-AI-Capstone`.
2. Upload `app.py`, `requirements.txt`, `README.md`, `.gitignore`, `.streamlit/config.toml`, and `tests/`.
3. Visit https://share.streamlit.io/ and sign in with GitHub.
4. Select **Create app**, choose your repository, select branch `main`, and set main file to `app.py`.
5. Deploy. Streamlit will show the actual public app URL after a successful build.

Expected URL formats (examples only):
- Repository: `https://github.com/YOUR-USERNAME/BuildSight-AI-Capstone`
- Demo: `https://YOUR-APP-NAME.streamlit.app`

These are templates, not published links. This project archive has not been uploaded or deployed automatically.

## Tests
```bash
python -m unittest discover -s tests -v
```

## Safety and accuracy limitations
This app is not a certified safety inspection, structural diagnosis, engineering design, bill of quantities, or professional property valuation. Photo analysis can be wrong and must be verified. Cost rates and material coefficients are editable illustrative assumptions; validate them against a project-specific BOQ, local prices and qualified professionals.
