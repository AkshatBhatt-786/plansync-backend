import os
from pyfiglet import print_figlet
from rich import print
from dotenv import load_dotenv
from app import create_app
from rich.traceback import install
from pathlib import Path


install()
print_figlet("DUHACKS 5.0")
app = create_app()
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
