
import subprocess
import os
from pathlib import Path
from fpdf import FPDF
# Initialize MCP app
# Define a tool
def clone_github_repo(repo_url: str, local_path: str = None) -> dict:
    """
    Clone a GitHub repository and return the result.
    """
    try:
        # If no local path is given, use repo name in a "repo_cloned" folder
        if not local_path:
            repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
            local_path = os.path.join(os.getcwd(), "repo_cloned", repo_name)
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        if local_path.exists():
            return {
                "success": False,
                "message": f"Directory already exists: {local_path}",
                "local_path": str(local_path)
            }
        # Clone the repository
        cmd = ["git", "clone", repo_url, str(local_path)]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {
            "success": True,
            "message": f":white_check_mark: Repo cloned to {local_path}",
            "local_path": str(local_path)
        }
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "message": f":x: Git clone failed: {e.stderr.strip() if e.stderr else str(e)}",
            "local_path": str(local_path)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f":x: Unexpected error: {str(e)}",
            "local_path": None
        }
def extract_all_repos_to_txt() -> dict:
    """
    Extracts code from all repos inside repo_cloned/ and writes to plain .txt files in repo_cloned/OUTPUT/.
    Also extracts README.md (if present) as readme.txt.
    """
    
    base_dir = Path("repo_cloned")
    output_dir = base_dir / "OUTPUT"
    output_dir.mkdir(parents=True, exist_ok=True)
    supported_extensions = [".py", ".java", ".js", ".ts", ".cpp", ".c", ".cs", ".rb", ".go", ".rs", ".php", ".md"]
    results = []
    for repo_dir in base_dir.iterdir():
        if repo_dir.is_dir() and repo_dir.name != "OUTPUT":
            repo_name = repo_dir.name
            code_file = output_dir / "code.txt"
            readme_file = output_dir / "readme.txt"
            code_lines = []
            readme_text = None
            for root, _, files in os.walk(repo_dir):
                for file in files:
                    full_path = Path(root) / file
                    # Extract code files
                    if full_path.suffix in supported_extensions:
                        try:
                            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                                content = f.read()
                                code_lines.append(f"\n# --- {full_path.relative_to(repo_dir)} ---\n{content}")
                        except Exception as e:
                            code_lines.append(f"\n# --- {full_path.relative_to(repo_dir)} ---\n[ERROR reading file: {e}]")
                    # Read README.md if found
                    if file.lower() == "readme.md" and readme_text is None:
                        try:
                            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                                readme_text = f.read()
                        except Exception as e:
                            readme_text = f"[ERROR reading README.md: {e}]"
            # Write code dump
            with open(code_file, "w", encoding="utf-8", errors="ignore") as f:
                f.write("\n".join(code_lines))
            # Write readme if exists
            if readme_text:
                with open(readme_file, "w", encoding="utf-8", errors="ignore") as f:
                    f.write(readme_text)
            results.append({
                "repo": repo_name,
                "code_file": str(code_file),
                "readme_file": str(readme_file) if readme_text else "README.md not found"
            })
    print(":white_check_mark: Finished writing readme.txt and code.txt")
    return {
        "success": True,
        "message": ":white_check_mark: Code and README extraction complete",
        "repos": results
    }
def text_to_pdf(text: str, filename: str = "output.pdf") -> dict:
    from fpdf import FPDF
    from pathlib import Path
    try:
        base_dir = Path.cwd() / "repo_cloned" / "OUTPUT"
        base_dir.mkdir(parents=True, exist_ok=True)
        output_path = base_dir / filename
        print(f":page_facing_up: Writing PDF to: {output_path}")
        print(f":memo: Text preview:\n{text[:500]}...\n")
        if not text.strip():
            return {
                "success": False,
                "message": ":x: No text provided for PDF generation.",
                "output_path": None
            }
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Helvetica", size=12)  # safer fallback
        for line in text.split('\n'):
            if line.strip():  # Only print non-empty lines
                pdf.multi_cell(0, 10, line)
        pdf.output(str(output_path))
        return {
            "success": True,
            "message": f":white_check_mark: PDF saved to {output_path}",
            "output_path": str(output_path)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f":x: Failed to generate PDF: {str(e)}",
            "output_path": None
        }
# # Initialize MCP app
# mcp = FastMCP(name="REPO_CLONER", version="1.0.0")
# # Define a tool
# @mcp.tool()
# def clone_github_repo(repo_url: str, local_path: str = None) -> dict:
#     """
#     Clone a GitHub repository and return the result.
#     """
#     try:
#         # If no local path is given, use repo name in a "repo_cloned" folder
#         if not local_path:
#             repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
#             local_path = os.path.join(os.getcwd(), "repo_cloned", repo_name)
#         local_path = Path(local_path)
#         local_path.parent.mkdir(parents=True, exist_ok=True)
#         if local_path.exists():
#             return {
#                 "success": False,
#                 "message": f"Directory already exists: {local_path}",
#                 "local_path": str(local_path)
#             }
#         # Clone the repository
#         cmd = ["git", "clone", repo_url, str(local_path)]
#         subprocess.run(cmd, capture_output=True, text=True, check=True)
#         return {
#             "success": True,
#             "message": f":white_check_mark: Repo cloned to {local_path}",
#             "local_path": str(local_path)
#         }
#     except subprocess.CalledProcessError as e:
#         return {
#             "success": False,
#             "message": f":x: Git clone failed: {e.stderr.strip() if e.stderr else str(e)}",
#             "local_path": str(local_path)
#         }
#     except Exception as e:
#         return {
#             "success": False,
#             "message": f":x: Unexpected error: {str(e)}",
#             "local_path": None
#         }
# @mcp.tool()
# def extract_all_repos_to_txt() -> dict:
#     """
#     Extracts code from all repos inside repo_cloned/ and writes to plain .txt files in repo_cloned/OUTPUT/.
#     Also extracts README.md (if present) as readme.txt.
#     """
#     base_dir = Path("repo_cloned")
#     output_dir = base_dir / "OUTPUT"
#     output_dir.mkdir(parents=True, exist_ok=True)
#     supported_extensions = [".py", ".java", ".js", ".ts", ".cpp", ".c", ".cs", ".rb", ".go", ".rs", ".php"]
#     results = []
#     for repo_dir in base_dir.iterdir():
#         if repo_dir.is_dir() and repo_dir.name != "OUTPUT":
#             repo_name = repo_dir.name
#             code_file = output_dir / "code.txt"
#             readme_file = output_dir / "readme.txt"
#             code_lines = []
#             readme_text = None
#             for root, _, files in os.walk(repo_dir):
#                 for file in files:
#                     full_path = Path(root) / file
#                     # Extract code files
#                     if full_path.suffix in supported_extensions:
#                         try:
#                             with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
#                                 content = f.read()
#                                 code_lines.append(f"\n# --- {full_path.relative_to(repo_dir)} ---\n{content}")
#                         except Exception as e:
#                             code_lines.append(f"\n# --- {full_path.relative_to(repo_dir)} ---\n[ERROR reading file: {e}]")
#                     # Read README.md if found
#                     if file.lower() == "readme.md" and readme_text is None:
#                         try:
#                             with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
#                                 readme_text = f.read()
#                         except Exception as e:
#                             readme_text = f"[ERROR reading README.md: {e}]"
#             # Write code dump
#             with open(code_file, "w", encoding="utf-8") as f:
#                 f.write("\n".join(code_lines))
#             # Write readme if exists
#             if readme_text:
#                 with open(readme_file, "w", encoding="utf-8") as f:
#                     f.write(readme_text)
#             results.append({
#                 "repo": repo_name,
#                 "code_file": str(code_file),
#                 "readme_file": str(readme_file) if readme_text else "README.md not found"
#             })
#     return {
#         "success": True,
#         "message": ":white_check_mark: Code and README extraction complete",
#         "repos": results
#     }
# @mcp.tool()
# def text_to_pdf(text: str, filename: str = "output.pdf") -> dict:
#     """
#     Convert raw text into a PDF file and save it inside repo_cloned/documents/.
#     """
#     try:
#         # Force output to always go to repo_cloned/documents/
#         base_dir = Path.cwd() / "repo_cloned" / "documents"
#         base_dir.mkdir(parents=True, exist_ok=True)
#         output_path = base_dir / filename
#         # Create and format PDF
#         pdf = FPDF()
#         pdf.add_page()
#         pdf.set_auto_page_break(auto=True, margin=15)
#         pdf.set_font("Arial", size=12)
#         for line in text.split('\n'):
#             pdf.multi_cell(0, 10, line)
#         # Save the PDF
#         pdf.output(str(output_path))
#         return {
#             "success": True,
#             "message": f":white_check_mark: PDF saved to {output_path}",
#             "output_path": str(output_path)
#         }
#     except Exception as e:
#         return {
#             "success": False,
#             "message": f":x: Failed to generate PDF: {str(e)}",
#             "output_path": None
#         }
# # Run the MCP server
# if __name__ == "__main__":
#     print(":ear: Server ready to register tools...")
#     mcp.run()