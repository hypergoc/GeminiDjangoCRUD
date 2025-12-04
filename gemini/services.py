# gemini/services.py

import os
import re
import logging
from django.conf import settings
import google.generativeai as genai
from .models import GeminiQuery
from dotenv import load_dotenv

# --- KONFIGURACIJA ---
load_dotenv()
logger = logging.getLogger(__name__)

try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    raise Exception("GOOGLE_API_KEY nije pronađen u .env fajlu.")


# --- FUNKCIJA #1: POZIVANJE AI-ja ---
def get_ai_response(prompt: str, history: int):
    """
    Vraća tuple: (tekst_odgovora, sirovi_response, tokeni, poslani_request)
    """
    try:
        model_name = os.environ.get("GEMINI_MODEL", "gemini-pro")
        model = genai.GenerativeModel(model_name=model_name)

        history_from_db = GeminiQuery.objects.all().order_by('-timestamp')[:history]

        api_history = []

        prompt_rule = os.environ["GEMINI_CONFIG"]

        if prompt_rule:
            prompt = f"{prompt}, ({prompt_rule})"

        for entry in reversed(history_from_db):
            api_history.append({"role": "user", "parts": [entry.question]})
            api_history.append({"role": "model", "parts": [entry.response]})


        full_request_payload = {
            "model_used": model_name,
            "prompt": prompt
        }

        if api_history and len(api_history) > 0:
            full_request_payload["history_len"] = len(api_history)
            full_request_payload["history"] = api_history

        chat = model.start_chat(history=api_history)
        response = chat.send_message(prompt)
        ai_response_text = response.text

        try:
            from google.protobuf.json_format import MessageToDict
            raw_response_dict = MessageToDict(response._result)
        except Exception:
            raw_response_dict = {'error': 'Could not serialize response object', 'text': ai_response_text}

        total_tokens = response.usage_metadata.total_token_count
        return ai_response_text, raw_response_dict, total_tokens, full_request_payload
    except Exception as e:
        logger.error(f"Greška prilikom poziva Gemini API-ja: {e}")
        error_text = f"Došlo je do greške u komunikaciji s Gemini API-jem: {str(e)}"
        error_payload = {"error": str(e), "prompt": prompt}
        return error_text, {'error': str(e)}, None, error_payload


# --- FUNKCIJA #2: ČITANJE SADRŽAJA FOLDERA ---
def read_folder_contents(folder_name: str) -> str:
    """ Čita sve .py fajlove iz odabranog foldera. """
    folder_path = os.path.join(settings.BASE_DIR, folder_name)
    full_content = ""
    if not os.path.isdir(folder_path):
        return f"GREŠKA: Folder '{folder_name}' nije pronađen."
    try:
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith('.py'):
                file_path = os.path.join(folder_path, filename)
                full_content += f"\n\n--- Sadržaj fajla: {filename} ---\n\n"
                with open(file_path, 'r', encoding='utf-8') as f:
                    full_content += f.read()
    except Exception as e:
        return f"GREŠKA pri čitanju fajlova iz '{folder_name}': {e}"
    return full_content


# --- FUNKCIJA #3: ČITANJE FAJLOVA IZ AI ODGOVORA (za 'Dohvati') ---
def read_files_from_response(response_text: str) -> str:
    """ Čita fajlove spomenute u AI odgovoru i vraća njihov sadržaj. """
    logger.info("--- Pokrenuto čitanje postojećih fajlova ---")
    filepaths = re.findall(r"###\s*([\w\-\./]+)", response_text)
    if not filepaths:
        return "Nije pronađena nijedna putanja do fajla u formatu '### putanja/do/fajla.py'."

    content = ""
    for path in set(filepaths):  # set() da izbjegnemo duplikate
        content += read_folder_contents(os.path.dirname(path)) if path.endswith('/') else open(
            os.path.join(settings.BASE_DIR, path.strip()), 'r', encoding='utf-8').read()
    return content


# --- FUNKCIJA #4: PRIMJENA PROMJENA (za 'Primijeni') ---
def apply_code_to_files(response_text: str) -> str:
    """ Parsira AI odgovor i zapisuje kod u stvarne fajlove. """
    logger.info("--- Pokrenuta primjena promjena na fajlove ---")
    code_blocks = re.findall(r"###\s*(?P<filepath>[\w\-\./]+)\s*\n```(?P<language>\w+)?\n(?P<code>.*?)\n```",
                             response_text, re.DOTALL)
    if not code_blocks:
        return "Nije pronađen nijedan ispravno formatiran blok koda za primjenu."

    report_lines = []
    for filepath, _, code in code_blocks:
        target_path = os.path.join(settings.BASE_DIR, filepath.strip())
        logger.info(f"Pokušavam zapisati u fajl: {target_path}")
        try:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(code.strip())
            report_lines.append(f"USPJEH: Fajl '{filepath}' je uspješno zapisan.")
        except Exception as e:
            report_lines.append(f"GREŠKA: Nije moguće zapisati fajl '{filepath}'. Razlog: {e}")
            logger.error(f"Greška pri zapisu u '{filepath}': {e}")
    return "\n".join(report_lines)