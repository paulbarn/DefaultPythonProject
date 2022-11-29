import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path
from operator import itemgetter
from PyPDF2 import PdfReader
import re, sys, json

root = tk.Tk()
root.title('PDF Reader - v1.0')
#root.iconbitmap(Path(Path.cwd(), 'app.ico'))
root.geometry('1630x900+100+70')

# globals
DEFAULT_FONT = ('Verdana', 8)

#
# 3 posibilities exist
#   1. In Development Path.cwd() = PDdfParser, folder that is open in terminal when running the app.py file     - use PAth.cwd()
#   2. In Production as .exe one directory = build\exe.win-amd64-3.10, or where ever the .exe file is located   - use Path.cwd()
#   3. In Production as .exe one bundled file = will run from a temporary directory stored in sys.MEIPASS
#        This option not covered
cwd_path = Path.cwd()
pdf_path = Path(cwd_path) # path to pdf directory
ptn_path = Path(cwd_path) # path to json filename
csv_path = Path(cwd_path) # path to csv filename

pdf_filepaths = [] # list of pdf filename paths

pdf_box_width = 60
ptn_box_width = 160
csv_box_width = 160
list_box_rows = 34
text_box_rows = 27

def pdf_to_text(pdf_filepath):
    ''' Convert a pdf file to text '''
    # params: Path object from pathlib
    # return: raw text as string
    #
    reader = PdfReader(pdf_filepath)
    raw_text = ''
    for page in reader.pages:
        raw_text += page.extract_text(0)       # normal text orientation only
    raw_text = ' '.join(raw_text.splitlines()) # replace line breaks with spaces
    return raw_text

def extract_text(search_criteria, text_to_search):
    ''' Match patterns in search criteria '''
    # params: dict of dicts, string
    # return: dict with name, value pairs, note values are text
    #   { 'ts' : '2022/11/30 10:01:23', 'c1' : '0.88345345', ...}
    #   Formating and order of match groups are defined in search criteria json file
    #
    df = {}
    for key, value in search_criteria.items():
        pattern = value['pattern']
        fmt = value['format']
        order = value['order']
        matches = re.search(pattern, text_to_search)

        if matches:
            reorder = itemgetter(*[x-1 for x in order])(matches.groups())
            if type(reorder) != tuple:
                reorder = (reorder,)
            df[key] = fmt.format(*reorder)
        else:
            df[key] = ''
    return df

def write_to_textbox(data, textbox_name, search_criteria):
    if data:
        textbox_name.delete('1.0', tk.END)
        header_line = ','.join([k for k in search_criteria.keys()])
        textbox_name.insert('1.0', header_line + '\n')
        for d in data:
            data_line = ','.join([str(val) for val in d.values()])
            textbox_name.insert(tk.END, data_line + '\n')

def pdf_btn_browse():
    global pdf_path, pdf_filepaths, pdf_listbox_var, pdf_path_tkStr, pdf_file_count_tkStr

    dir_str = filedialog.askdirectory(initialdir=cwd_path)
    if dir_str:
        pdf_path_tkStr.set(dir_str)
        pdf_path = Path(dir_str)
        pdf_files = [f for f in pdf_path.iterdir() if f.suffix == '.pdf']
        pdf_filepaths = pdf_files
        pdf_listbox = []
        for f in pdf_files:
            pdf_listbox.append(f.name)
        pdf_listbox_var.set(value=pdf_listbox)
        pdf_file_count_tkStr.set(value=str(len(pdf_files)) + ' file(s)')

def ptn_btn_browse():
    global ptn_path

    fstr = filedialog.askopenfilename(title='Open file...', initialdir=cwd_path, filetypes=[('Pattern Files', '.json')])
    if fstr:
        ptn_path_tkStr.set(fstr)
        ptn_path = Path(fstr)
        with open(ptn_path, 'r') as f:
            lines = f.read()
            if lines:
                ptn_txtBox.delete('1.0', tk.END)
                ptn_txtBox.insert('1.0', lines)
            else:
                tk.messagebox.showwarning("Warning", 'No file contents.')

def csv_btn_browse():
    global csv_path

    fstr = filedialog.askopenfilename(title='Open file...', initialdir=cwd_path, filetypes=[('csv Files', '.csv')])
    if fstr:
        csv_path_tkStr.set(fstr)
        csv_path = Path(fstr)
        with open(csv_path, 'r') as f:
            lines = f.read()
            if lines:
                csv_txtBox.delete('1.0', tk.END)
                csv_txtBox.insert('1.0', lines)
            else:
                tk.messagebox.showwarning("Warning", 'No file contents.')

def run_btn():
    global pdf_filepaths

    # get pdf filepaths to iterate over
    selected_indices = pdf_lstBox.curselection()
    selected_pdf_filepaths = [pdf_filepaths[i] for i in selected_indices]

    data = []
    search_criteria = None
    pdf_files_to_process = None

    # with open(ptn_path, 'r') as f:
    #     search_criteria = json.load(f)                             
    #search_criteria = json.loads(ptn_txtBox.get('1.0', tk.END))  # get from textbox

    # process all pdf files if none selected, only selected if 1 or more are selected
    num_selected = len(selected_pdf_filepaths)

    if num_selected == 0:
        # process all pdf files in pdf dir
        pdf_files_to_process = pdf_filepaths
    else:
        # selected only
        pdf_files_to_process = selected_pdf_filepaths

    # process pdf files
    search_criteria = json.loads(ptn_txtBox.get('1.0', tk.END))
    for pdf_filepath in pdf_files_to_process:
        text_to_search = pdf_to_text(pdf_filepath)
        data.append(extract_text(search_criteria, text_to_search))
    
    # write all file results to text box, one line per file
    write_to_textbox(data, csv_txtBox, search_criteria)
    
    # user must save csv by clicking button
    #write_to_csv(data, csv_path, search_criteria)

def ptn_btn_save():
    global ptn_path

    fstr = filedialog.asksaveasfilename(title='Save As...', initialdir=cwd_path,  filetypes=[('JSON', '.json')])
    if fstr:
        ptn_path_tkStr.set(fstr)
        ptn_path = Path(fstr)
        ptn_path = Path(ptn_path.parent, ptn_path.stem + '.json')
        with open(ptn_path, 'w') as f:
            f.write(ptn_txtBox.get('1.0', tk.END))
    else:
        ptn_path_tkStr.set('')

def csv_btn_save():
    global csv_path

    fstr = filedialog.asksaveasfilename(title='Save As...', initialdir=cwd_path, filetypes=[('CSV', '.csv')])
    if fstr:
        # user may type an extension, we don't want to add it twice
        if not fstr.endswith('.csv'):
            fstr += '.csv'
        csv_path = Path(fstr)
        csv_path_tkStr.set(str(csv_path.absolute()))
        with open(csv_path, 'w') as f:
            f.write(csv_txtBox.get('1.0', tk.END))
    else:
         csv_path_tkStr.set('')

def quit_btn():
    root.destroy()

#
# PDF Directory Selection Objects
#
pdf_frame = ttk.Frame(root, borderwidth=1, padding=5, relief='groove')
pdf_frame.grid(column=0, row=0, rowspan=2, padx=10, pady=10, sticky=tk.NW)

pdf_btn_browse = ttk.Button(pdf_frame, text='Browse pdf...', width=20, command=pdf_btn_browse)
pdf_btn_browse.grid(column=0, row=0, padx=1, pady=1, sticky=tk.NW)

pdf_path_tkStr = tk.StringVar()
pdf_lbl_dir = ttk.Label(pdf_frame, textvariable=pdf_path_tkStr)
pdf_lbl_dir.grid(column=0, row=1, padx=1, pady=2, sticky=tk.W)

lstbox_frame = ttk.Frame(pdf_frame)
scrollbar = ttk.Scrollbar(lstbox_frame, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
pdf_listbox_var = tk.Variable()
pdf_lstBox = tk.Listbox(lstbox_frame, listvariable=pdf_listbox_var, selectmode=tk.EXTENDED, height=list_box_rows, width=pdf_box_width, font=DEFAULT_FONT)
pdf_lstBox.pack()
pdf_lstBox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=pdf_lstBox.yview)
lstbox_frame.grid(column=0, row=2, padx=1, pady=4, sticky=tk.W)

pdf_file_count_tkStr = tk.StringVar(value='0 file(s)')
pdf_file_count = ttk.Label(pdf_frame, textvariable=pdf_file_count_tkStr)
pdf_file_count.grid(column=0, row=3, padx=1, pady=2, sticky=tk.E)

#
# Pattern Selection Objects
#
ptn_frame = ttk.Frame(root, borderwidth=1, padding=5, relief='groove')
ptn_frame.grid(column=1, row=0, padx=10, pady=10, sticky=tk.NW)

ptn_path_tkStr = tk.StringVar()
ptn_lbl_dir = ttk.Label(ptn_frame, textvariable=ptn_path_tkStr)
ptn_lbl_dir.grid(column=0, row=1, padx=1, pady=2, sticky=tk.W)

ctrl_frame = ttk.Frame(ptn_frame, borderwidth=1, padding=0, relief='')
ptn_btn_browse = ttk.Button(ctrl_frame, text='Browse Patten', width=20, command=ptn_btn_browse)
ptn_btn_save = ttk.Button(ctrl_frame, text='Save Pattern', width=20, command=ptn_btn_save)
# match_type = tk.StringVar(None,FIND_ALL)
# radio1 = ttk.Radiobutton(ctrl_frame, text="Find All",  value=FIND_ALL, variable=match_type)
# radio2 = ttk.Radiobutton(ctrl_frame, text="Find Each",  value=FIND_EACH, variable=match_type)
ptn_btn_browse.pack(side=tk.LEFT, padx=10, pady=0)
ptn_btn_save.pack(side=tk.LEFT, padx=10, pady=0)
#radio1.pack(side=tk.LEFT, padx=10, pady=0)
#radio2.pack(side=tk.LEFT, padx=10, pady=0)
ctrl_frame.grid(column=0, row=0, padx=1, pady=0, sticky=tk.W)

ptn_txtBox = tk.Text(ptn_frame, width=ptn_box_width, height=text_box_rows, font=DEFAULT_FONT)
ptn_txtBox.grid(column=0, row=2, padx=1, pady=4, sticky=tk.W)

#
# CSV Extract Objects - csv file contents
#
csv_frame = ttk.Frame(root, borderwidth=1, padding=5, relief='groove')
csv_frame.grid(column=1, row=1, padx=10, pady=10, sticky=tk.NW)

csv_path_tkStr = tk.StringVar()
csv_lbl_dir = ttk.Label(csv_frame, textvariable=csv_path_tkStr)
csv_lbl_dir.grid(column=0, row=1, padx=1, pady=2, sticky=tk.W)

csv_btn_browse = ttk.Button(csv_frame, text='Browse CSV', width=20, command=csv_btn_browse)
csv_btn_browse.grid(column=0, row=0, padx=1, pady=1, sticky=tk.NW)

csv_btn_save = ttk.Button(csv_frame, text='Save CSV', width=20, command=csv_btn_save)
csv_btn_save.grid(column=0, row=0, padx=150, pady=1, sticky=tk.W)

csv_txtBox = tk.Text(csv_frame, width=csv_box_width, height=text_box_rows, font=DEFAULT_FONT)
csv_txtBox.grid(column=0, row=2, padx=1, pady=4, sticky=tk.W)

#
# Run, SaveCSV, Quit buttons
#
run_frame = ttk.Frame(root, borderwidth=1, padding=20, relief='groove')
run_frame.grid(column=0, row=1, padx=10, pady=155, sticky=tk.EW)

run_btn = ttk.Button(run_frame, text='Run', width=15, command=run_btn)
run_btn.pack(pady=15)

quit_btn = ttk.Button(run_frame, text='Quit', width=15, command=quit_btn)
quit_btn.pack(pady=5)

instr_label = ttk.Label(run_frame, text='Instructions:\n1. Select PDF Directory\n2. Select Pattern file\n3. Edit Pattern file if necessary\n4. Save Pattern file\n5. Click Run button\n6. Save csv file')
instr_label.pack(pady=20, anchor=tk.S)

#
# Working directory is where the file is run from
#
# if getattr( sys, 'frozen', False ):
#     # running in a bundle
#     tk.messagebox.showwarning("Warning", f'Runing Frozen.\nCWD: {Path.cwd()}\nARGV: {sys.argv[0]}')
#     # if sys.MEIPASS:
#     #     print(f'sys.MEIPASS: {sys.MEIPASS}')
# else :
#     # running live
#     tk.messagebox.showwarning("Warning", f'Running Normal..\nCWD: {Path.cwd()}\nARGV: {sys.argv[0]}')
#     pass

#
# Run application
#
root.mainloop()