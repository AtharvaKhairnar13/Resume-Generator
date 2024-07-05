# Python program creating a
# small document using pylatex

import subprocess

# Define the name of the LaTeX document
latex_file = "main.tex"

# Compile the LaTeX document using pdfTeX
try:
    subprocess.run(["pdflatex", latex_file])
    print("LaTeX document compiled successfully.")
except subprocess.CalledProcessError as e:
    print("Error: LaTeX compilation failed.")
    print(e.stderr.decode())
