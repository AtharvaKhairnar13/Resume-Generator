import numpy as np
import os
import pickle
import streamlit as st
import sys
import urllib
import subprocess
import re
import tensorflow as tf
from transformers import GPT2Tokenizer, TFGPT2LMHeadModel

latex_file = "main.tex"
pdf_file = "main.pdf"  # Name of the compiled PDF file

# Function to compile LaTeX document
def update_name_in_latex(latex_file, new_name):
    try:
        # Read the existing LaTeX content
        with open(latex_file, "r") as f:
            content = f.read()
        
        # Find the start and end positions of the name section
        start_pos = content.find("%ADD NAME")
        if start_pos == -1:
            st.error("Error: Technical Skills section not found in LaTeX file.")
            return False
        end_pos = content.find("\\end{center}", start_pos)
        if end_pos == -1:
            st.error("Error: End of center environment not found after Technical Skills section.")
            return False
        
        # Extract the existing skills section
        skills_section = content[start_pos:end_pos+1]
        
        # Replace existing skills with new_skills
        updated_skills_section = skills_section.replace(skills_section, new_name)
        print(updated_skills_section)
        # Replace existing skills section with updated_skills_section in the content
        updated_content = content[:start_pos] + updated_skills_section + "\n" + content[end_pos+13:]
        # Write the updated content back to the LaTeX file
        with open(latex_file, "w") as f:
            f.write(updated_content)
        
    except Exception as e:
        st.error("Error: Failed to update LaTeX file with new name.")
        st.error(str(e))
        return False


def compile_and_get_pdf_bytes(latex_file,skills,name):
    try:
        # Compile LaTeX document
        update_name_in_latex(latex_file, name)
        with open(latex_file, "r") as f:
            content = f.read()

        
        
        start_pos = content.find("\\section*{\\faIcon{cogs} Technical Skills}")
        if start_pos == -1:
            st.error("Error: Technical Skills section not found in LaTeX file.")
            return False
        end_pos = content.find("\\end{center}", start_pos)
        if end_pos == -1:
            st.error("Error: End of center environment not found after Technical Skills section.")
            return False
        
        # Extract the existing skills section
        skills_section = content[start_pos:end_pos+1]
        
        # Replace existing skills with new_skills
        updated_skills_section = skills_section.replace(skills_section, skills)
        
        # Replace existing skills section with updated_skills_section in the content
        updated_content = content[:start_pos] + updated_skills_section + "\n" + content[end_pos+13:]
        

        # Write the updated content back to the LaTeX file
        with open(latex_file, "w") as f:
            f.write(updated_content)

        subprocess.run(["pdflatex", latex_file])

        # Read the compiled PDF bytes
        with open("main.pdf", "rb") as f:
            pdf_bytes = f.read()
        return pdf_bytes
    except subprocess.CalledProcessError as e:
        st.error("Error: LaTeX compilation failed.")
        st.error(e.stderr.decode())
        return None
def onclick():
    pass
def get_skills(text,tokenizer,model):
    prompt=f'<startoftext>Prompt: Mention Required Skills for the following Job Description: {text}\nAnswer:'
    generated=tokenizer(f"{prompt}",return_tensors="pt").input_ids
    sample_outputs=model.generate(generated,do_sample=False,top_k=50,max_length=128,top_p=0.90,temperature=0,num_beams=5,early_stopping=True,num_return_sequences=3)
    pred_text=tokenizer.decode(sample_outputs[0],skip_special_tokens=True)
    
    return pred_text

def split_answer(text):
    parts = text.split("\n")
    first_answer = parts[1]
    
    # Find the position of the phrase "Answer: The skills required for the above job description is"
    phrase = "Answer: The skills required for the above job description is"
    start_index = first_answer.find(phrase)
    if start_index == -1:
        return None
    
    # Extract the part after the phrase
    skills_text = first_answer[start_index + len(phrase):].strip()
    
    # Split the text into individual skills
    skills = skills_text.split(", ")[:5]  # Extract the first 5 skills
    
    return skills
    
def generate_skills_list(skills):
    # Define the LaTeX template
    latex_template = """
    \\section*{\\faIcon{cogs} Technical Skills}
        \\begin{center}
            \\begin{itemize}[label=\\tiny\\faCircle, itemsep=1pt]
                %s
            \\end{itemize}
        \\end{center}
    """

    # Generate LaTeX code for each skill in the list
    item_template = "\\item \\textbf{%s}"
    items = "\n".join([item_template % skill for skill in skills])

    # Insert the items into the template
    latex_code = latex_template % items

    return latex_code

def main():
    tokenizer=GPT2Tokenizer.from_pretrained("gpt2",bos_token='<startoftext>',eos_token='<endoftext>',pad_token='<pad>')
    model=TFGPT2LMHeadModel.from_pretrained("/Users/atharvakhairnar13/Desktop/AAi_Competition/gpt2-finetuned-jd-to-skills")
    st.title("Resume Generator")
    progress=0
    mybar = st.progress(progress)
    download_Disable=True
    name = st.text_input("Enter Your name", key="name_input")
    if name:
        progress=25
        mybar.progress(progress)
    JD = st.text_input("Enter the Job Description")
    if JD:
        progress=100
        mybar.progress(progress)
        download_disabled = False
        st.success('Resume Created Successfully', icon="✅")

    sktx=get_skills(JD,tokenizer,model)
    final_skill=split_answer(sktx)

    new_skills = generate_skills_list(final_skill)

    new_name = f"""
    %ADD NAME
    \\begin{{center}}
        \\textbf{{\\Huge {name}}} \\\\
        \\vspace{{2mm}}
    \\end{{center}}
"""

    

    st.write("")
    st.write("")
    st.write("")
    st.write("")
    col1, col2,col3 = st.columns([1,1,1])
    
    with col2:
        download_disabled = progress != 100
        st.download_button("Download Resume", compile_and_get_pdf_bytes(latex_file,new_skills,new_name), file_name=f"{name}_Resume.pdf", mime="application/pdf", disabled=download_disabled)    
    
    

if __name__ == "__main__":
    
    main()
    
