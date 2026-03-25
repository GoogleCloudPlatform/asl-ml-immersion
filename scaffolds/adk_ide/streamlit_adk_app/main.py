import sys
import os
from streamlit.web import cli as stcli

def main():
    """
    Programmatic entry point for running the Streamlit app.
    This allows you to run or debug the app directly from your IDE.
    """
    # 1. Get the absolute path to the directory where main.py lives
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Build the absolute path to app.py
    app_path = os.path.join(current_dir, "app.py")
    
    # 3. Point sys.argv to the absolute path
    sys.argv = ["streamlit", "run", app_path]
    
    # Execute the Streamlit CLI within the current Python process
    sys.exit(stcli.main())

if __name__ == "__main__":
    main()