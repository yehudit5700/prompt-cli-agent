import os
from pathlib import Path
import gradio as gr
from dotenv import load_dotenv
from google import genai
import httpx

# טעינת משתני סביבה
load_dotenv()

# טעינת מפתח ה-API
api_key = os.getenv("GEMINI_API_KEY")

# יצירת לקוח HTTP שאינו מודד את תקינות תעודת ה-SSL (פתרון עבור סביבת סינון)
http_client = httpx.Client(verify=False)

# התחברות ל-API של Gemini
client = genai.Client(
    api_key=api_key,
    http_options={'httpx_client': http_client}
)

def load_system_prompt(version="v3"):
    """טוען את הפרומפט מתוך הקובץ בתיקיית prompts"""
    prompt_path = Path("prompts") / f"prompt_{version}.txt"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return "You are a CLI command generator. Output only the command."

# רשימת המודלים לנסות לפי סדר עדיפויות
MODELS_TO_TRY = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash"
]

def generate_cli_command(user_instruction):
    if not user_instruction or not user_instruction.strip():
        return "# אנא הכניסי הוראה בשפה טבעית."
    
    system_prompt = load_system_prompt("v3")
    prompt_content = f"{system_prompt}\n\nUser request: {user_instruction}"
    
    # מעבר על רשימת המודלים
    for model_name in MODELS_TO_TRY:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_content
            )
            return response.text.strip()
        except Exception as e:
            # הדפסת השגיאה המדויקת לטרמינל לצורך זיהוי הבעיה
            print(f"[DEBUG] Error with model '{model_name}': {type(e).__name__} - {e}")
            continue
            
    return "# שגיאה: לא ניתן היה לקבל מענה מאף אחד מהמודלים ברשימה. ודאי שמפתח ה-API תקין ובידקי את פלט ה-DEBUG בטרמינל."

# עיצוב CSS מואר, נעים ובהיר
custom_css = """
body, .gradio-container {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%) !important;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    direction: rtl;
}

.main-header {
    text-align: center;
    padding: 28px;
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border: 1px solid #bae6fd;
    border-radius: 20px;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px -5px rgba(14, 165, 233, 0.15);
}

.main-header h1 {
    color: #0284c7 !important;
    font-size: 2.3rem !important;
    font-weight: 800;
    margin-bottom: 8px;
    letter-spacing: -0.5px;
}

.main-header p {
    color: #475569 !important;
    font-size: 1.1rem !important;
}

.action-btn {
    background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    transition: all 0.2s ease-in-out !important;
    box-shadow: 0 4px 14px 0 rgba(2, 132, 199, 0.3) !important;
}

.action-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px 0 rgba(2, 132, 199, 0.45) !important;
}

.gr-box, .gr-input, .gr-form {
    background-color: #ffffff !important;
    border-radius: 14px !important;
    border: 1px solid #cbd5e1 !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
}

.code-container {
    direction: ltr;
}
"""

# יצירת הממשק
with gr.Blocks(title="CLI Agent - Prompt Engineering Lab") as demo:
    
    with gr.Column(elem_classes=["main-header"]):
        gr.Markdown("# Natural Language ➔ CLI Agent")
        gr.Markdown("מערכת הממירה הוראות בשפה חופשית לפקודות טרמינל מדויקות | **Prompt Engineering Lab**")
    
    with gr.Row():
        with gr.Column(scale=1):
            input_text = gr.Textbox(
                label="הוראה בשפה טבעית (Input)", 
                placeholder="לדוגמה: תראה לי את כל הקבצים שנגמרים ב-txt",
                lines=4
            )
            submit_btn = gr.Button("תרגם לפקודה ⚡", variant="primary", elem_classes=["action-btn"])
            
            gr.Examples(
                examples=[
                    ["מה כתובת ה-IP של המחשב שלי?"],
                    ["תמחק את כל הקבצים הזמניים בתיקיית downloads"],
                    ["תסדר את הקבצים לפי גודל מהגדול לקטן"],
                    ["איזה תהליכים רצים כרגע במערכת?"],
                    ["תעתיק את כל קבצי ה-pdf מתיקיית מסמכים לתמונות"]
                ],
                inputs=input_text,
                label="דוגמאות לניסוי מהיר"
            )
        
        with gr.Column(scale=1):
            output_text = gr.Code(
                label="פקודת CLI שהתקבלה (Output)", 
                language="shell",
                lines=8,
                elem_classes=["code-container"]
            )

    submit_btn.click(
        fn=generate_cli_command,
        inputs=[input_text],
        outputs=[output_text]
    )

if __name__ == "__main__":
    custom_theme = gr.themes.Soft(
        primary_hue="sky",
        neutral_hue="slate",
    )
    demo.launch(theme=custom_theme, css=custom_css)