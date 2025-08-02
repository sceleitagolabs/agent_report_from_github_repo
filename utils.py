import os
from typing import Optional


def get_openai_api_key() -> Optional[str]:
    """
    Get the OpenAI API key from environment variables.
    
    Returns:
        Optional[str]: The OpenAI API key if found, None otherwise.
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Warning: OPENAI_API_KEY environment variable not found.")
        return None
    return api_key


def get_serper_api_key() -> Optional[str]:
    """
    Get the Serper API key from environment variables.
    
    Returns:
        Optional[str]: The Serper API key if found, None otherwise.
    """
    api_key = os.getenv('SERPER_API_KEY')
    if not api_key:
        print("Warning: SERPER_API_KEY environment variable not found.")
        return None
    return api_key


def read_output_files() -> tuple[Optional[str], Optional[str]]:
    """
    Read the code.txt and readme.txt files from the output folder.
    
    Returns:
        tuple[Optional[str], Optional[str]]: A tuple containing (code_content, readme_content)
        If a file doesn't exist, its corresponding value will be None.
    """
    output_folder = "output"
    code_file_path = os.path.join(output_folder, "code.txt")
    readme_file_path = os.path.join(output_folder, "readme.txt")
    
    code_content = None
    readme_content = None
    
    # Read code.txt
    try:
        if os.path.exists(code_file_path):
            with open(code_file_path, 'r', encoding='utf-8') as file:
                code_content = file.read()
                print(f"Successfully read code.txt ({len(code_content)} characters)")
        else:
            print("Warning: code.txt not found in output folder")
    except Exception as e:
        print(f"Error reading code.txt: {e}")
    
    # Read readme.txt
    try:
        if os.path.exists(readme_file_path):
            with open(readme_file_path, 'r', encoding='utf-8') as file:
                readme_content = file.read()
                print(f"Successfully read readme.txt ({len(readme_content)} characters)")
        else:
            print("Warning: readme.txt not found in output folder")
    except Exception as e:
        print(f"Error reading readme.txt: {e}")
    
    return code_content, readme_content
