import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from deep_translator import GoogleTranslator
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import os



def translate(text, source, target):
    translator = GoogleTranslator() # YOU MUST CREATE ONE FOR EACH REQUEST OR THE MULTI-THREADING WILL FAIL, SINCE EACH INSTANCE HANDLE ONE REQUEST AT a TIME.
    translator.source = source
    translator.target = target
    return translator.translate(text)

def translate_and_save(source_path, save_path, source_lang, target_lang, progress_var, num_workers):
    try:
        if not source_lang or not target_lang:
            raise ValueError("Please select both source and target languages")

        # Split the text lines into chunks of 5000 chars each
        chunks = []
        current_chunk = ""
        max_chunk_length = 5000 # This is fixed by google translate and by the library also
        with open(source_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                if len(current_chunk) + len(line) <= max_chunk_length:
                    current_chunk += line
                else:
                    chunks.append(current_chunk)
                    current_chunk = line

            # Append the remaining chunk if any
            if current_chunk:
                chunks.append(current_chunk)
        n_chunks = len(chunks)

        # Multi-Threading
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(
                    lambda text: translate(text, source_lang, target_lang),
                    chunk
                ) for chunk in chunks
            ]

            for i, future in enumerate(as_completed(futures)):
                # Update progress bar
                progress_var.set((i + 1) * 100 // n_chunks)
                root.update_idletasks()

        # Saving
        translated_text = "\n".join([future.result() for future in futures])
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(translated_text)

        status_label.config(text="Translation succeeded", fg="green")

    except Exception as e:
        status_label.config(text=f"Error: {str(e)}", fg="red")

def browse_source():
    source_file_path = filedialog.askopenfilename(title="Select Source File", filetypes=[("Text files", "*.txt")])
    source_entry.delete(0, tk.END)
    source_entry.insert(0, source_file_path)

def browse_save():
    save_file_path = filedialog.asksaveasfilename(title="Select Save File", defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    save_entry.delete(0, tk.END)
    save_entry.insert(0, save_file_path)

def start_translation():
    source_path = source_entry.get()
    save_path = save_entry.get()
    source_lang = source_lang_var.get()
    target_lang = target_lang_var.get()
    progress_bar = None
    
    try:
        num_workers = num_workers_var.get()
        if not source_path or not save_path:
            raise ValueError("Please provide source and save paths")

        if not source_lang or not target_lang:
            raise ValueError("Please select both source and target languages")

        status_label.config(text="Translation started", fg="black")

        # Set up progress bar
        progress_var = tk.IntVar()
        progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, mode="determinate")
        progress_bar.grid(row=7, column=1, pady=10, sticky="ew")

        # Disable Start Translation button during translation
        start_button.config(state=tk.DISABLED)

        translate_and_save(source_path, save_path, source_lang, target_lang, progress_var, num_workers)

    except Exception as ve:
        status_label.config(text=str(ve), fg="red")

    finally:
        # Enable Start Translation button after translation is complete
        start_button.config(state=tk.NORMAL)
        # Destroy progress bar if it exists
        if progress_bar:
            progress_bar.destroy()

def start_translation_thread():
    new_thread = threading.Thread(target=start_translation)
    new_thread.start()



# Create the main window
root = tk.Tk()
root.title("Fast Unlimited-Size Text Translation")
root.resizable(False, False)

# Create GUI elements
source_label = tk.Label(root, text="Source File:")
source_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

source_entry = tk.Entry(root, width=50)
source_entry.grid(row=0, column=1, padx=5, pady=5)

source_browse_button = tk.Button(root, text="Browse", command=browse_source)
source_browse_button.grid(row=0, column=2, padx=5, pady=5)

save_label = tk.Label(root, text="Save File:")
save_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")

save_entry = tk.Entry(root, width=50)
save_entry.grid(row=1, column=1, padx=5, pady=5)

save_browse_button = tk.Button(root, text="Browse", command=browse_save)
save_browse_button.grid(row=1, column=2, padx=5, pady=5)

source_lang_label = tk.Label(root, text="Source Language:")
source_lang_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")

source_lang_var = tk.StringVar(value="auto")
source_lang_dropdown = ttk.Combobox(root, textvariable=source_lang_var, values=["auto", "fr", "es", "de", "..."])
source_lang_dropdown.grid(row=2, column=1, padx=5, pady=5)

target_lang_label = tk.Label(root, text="Target Language:")
target_lang_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")

target_lang_var = tk.StringVar(value="en")
target_lang_dropdown = ttk.Combobox(root, textvariable=target_lang_var, values=["en", "fr", "es", "de", "..."])
target_lang_dropdown.grid(row=3, column=1, padx=5, pady=5)

num_workers_label = tk.Label(root, text="Number of Workers:")
num_workers_label.grid(row=5, column=0, padx=5, pady=5, sticky="e")

num_workers_var = tk.IntVar(value=os.cpu_count())
num_workers_entry = tk.Entry(root, textvariable=num_workers_var)
num_workers_entry.grid(row=5, column=1, padx=5, pady=5)

start_button = tk.Button(root, text="Start Translation", command=start_translation_thread)
start_button.grid(row=6, column=1, pady=10)

status_label = tk.Label(root, text="", fg="black")
status_label.grid(row=7, column=0, columnspan=3)

# Run the GUI
root.mainloop()
