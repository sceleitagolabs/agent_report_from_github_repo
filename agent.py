from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Literal
from tools import clone_github_repo, extract_all_repos_to_txt, text_to_pdf
import os
from openai import OpenAI
import re
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import json
import markdown
from weasyprint import HTML, CSS

load_dotenv()
# === Define State ===
class State(BaseModel):
    repo_cloned: bool
    extracted: bool
    summary: str
    pdf_path: str

class UserInput(BaseModel):
    type_of_user: Literal["developer", "business_analyst", "product_manager", "technical_writer"]
    repo_url: str
    topic: str

base_path = "./repo_cloned/OUTPUT/"

user_input = """I'm a developer reviewing a GitHub repository, and I’d like your assistance in extracting and generating a clear report focused on the installation and setup process of the project.

The goal is to identify all relevant instructions, dependencies, environment setup steps, configuration details, and anything else necessary to get the project running locally or in production (as applicable). I’m particularly interested in any setup documentation from the README, installation scripts, Dockerfiles, or other setup-related file from the following repository: https://github.com/marianfoo/mcp-sap-docs"""

# === Node functions ===
def extract_json(text: str) -> dict:
    try:
        # Try parsing directly
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON from inside a Markdown code block
        match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        # Try to extract the first valid-looking JSON block
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        raise  # re-raise if nothing works

def user_info_input(state: State) -> State:

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system","content": """You are an information extraction specialist.
             Your task is to analyze the provided text and identify three key pieces of information: 
             the GitHub repository URL, the type of user, and the topic of the final report. 
             You will return this information in a JSON object with the following keys: 
             'repo_url', 'type_of_user', and 'topic'."""},
            {"role": "user", "content":user_input},
        ],
        temperature=0.3
    )
    outputs = response.choices[0].message.content
    outpusjson = extract_json(outputs)
    with open(base_path + "outputs.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(outpusjson, indent=2))
    return {"summary": json.dumps(outpusjson, indent=2)}

def node_clone_repo(state: State) -> State:
    files = ["outputs.json"]
    for f in files:
        path = os.path.join(base_path, f)
        if os.path.exists(path):
            with open(base_path + "outputs.json", "r", encoding="utf-8") as f:
                data = json.load(f) 
                repo_url = data["repo_url"]
    result = clone_github_repo(repo_url)
    return {"repo_cloned": result["success"]}
def node_extract_code(state: State) -> State:
    result = extract_all_repos_to_txt()
    return {"extracted": result["success"]}

def node_topic_files_identify(state: State) -> State:
    base_path = "./repo_cloned/OUTPUT/"
    files = ["readme.txt", "code.txt", "outputs.json"]
    content = ""
    for f in files:
        path = os.path.join(base_path, f)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                content += file.read()
            with open(base_path + "outputs.json", "r", encoding="utf-8") as f:
                outputs = json.load(f)
                topic = outputs["topic"]
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"""You are a content filtration expert. 
            Your task is to process the provided information and return only the content that is specifically about the following topic: {topic}. 
            Do not include any other information or commentary."""},
            {"role": "user", "content": content[:6000]},
        ],
        temperature=0.3
    )
    summary_code = response.choices[0].message.content
    with open(base_path + "summary_code.txt", "w", encoding="utf-8") as f:
        f.write(summary_code)
    return {"summary": summary_code}

def node_summarize_repo(state: State) -> State:
    base_path = "./repo_cloned/OUTPUT/"
    files = ["readme.txt", "summary_code.txt", "outputs.json"]
    content = ""
    for f in files:
        path = os.path.join(base_path, f)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                content += file.read()
            with open(base_path + "outputs.json", "r", encoding="utf-8") as f:
                outputs = json.load(f)
                type_of_user = outputs["type_of_user"]
                topic = outputs["topic"]
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"""You are a technical project summary writer. 
            Your task is to create a detailed, project-based summary of a GitHub repository. 
            This summary must be written for the {type_of_user} stakeholder audience. 
            The summary's main focus and title must be the following topic: {topic}. 
            You will present the final summary in clean markdown format."""},
            {"role": "user", "content": content[:6000]},
        ],
        temperature=0.3
    )
    summary = response.choices[0].message.content
    with open(base_path + "summary.md", "w", encoding="utf-8") as f:
        f.write(summary)
    return {"summary": summary}


def node_generate_pdf(state: State) -> State:
    base_path = "./repo_cloned/OUTPUT/"
    path = "repo_cloned/OUTPUT/summary.md"
    with open(path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(md_text, extensions=['extra', 'codehilite', 'tables'])

    # Wrap HTML in a basic structure
    full_html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: sans-serif; margin: 2em; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
    """

    # Load CSS if provided
    css = CSS(filename="style/style.css")  # adjust path if needed
    HTML(string=full_html).write_pdf(target=f"{base_path}/output.pdf", stylesheets=[css])

    # if not os.path.exists(path):
    #     return {"pdf_path": ""}
    # with open(path, "r", encoding="utf-8") as f:
    #     content = f.read()
    # result = text_to_pdf(content, filename="output.pdf")
    # return {"pdf_path": result["output_path"] if result["success"] else ""}
# === Build LangGraph ===
builder = StateGraph(State)
builder.add_node("user_info_input", user_info_input)
builder.add_node("clone", node_clone_repo)
builder.add_node("extract", node_extract_code)
builder.add_node("topic_files_identify", node_topic_files_identify)
builder.add_node("summarize", node_summarize_repo)
builder.add_node("pdf", node_generate_pdf)
builder.set_entry_point("user_info_input")
builder.add_edge("user_info_input", "clone")
builder.add_edge("clone", "extract")
builder.add_edge("extract", "topic_files_identify")
builder.add_edge("topic_files_identify", "summarize")
builder.add_edge("summarize", "pdf")
builder.add_edge("pdf", END)
app = builder.compile()
# === Run LangGraph ===
if __name__ == "__main__":
    result = app.invoke({"repo_cloned": False, "extracted": False, "summary": "", "pdf_path": ""})
    print(":white_check_mark: Final output:")
    print(result)