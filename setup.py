import os
import sys

from cx_Freeze import Executable, setup

base = "Win32GUI" if sys.platform == "win32" else None

app_exe = Executable("app/app.py", base=base, icon="app/app.ico")
#app_exe = Executable("app/app.py", base=base)

includefiles = [ # (path in dev, path in prod)
    #(os.path.abspath("app.ico"), "app.ico"),
    (os.path.abspath("readme.md"), "readme.md"),
    (os.path.abspath("search_patterns.json"), "search_patterns.json"),
    (os.path.abspath("pdf"), "pdf")   # all contents of dir if it exists
]

build_exe_options = {
    "optimize" : 2,
    "include_files" : includefiles,
    "excludes" : [],  # modules
    "includes" : [], # modules
    "packages" : [], # packages to include
    "zip_includes" : [],      # files for zip directory - syntax same as include_files
    "zip_include_packages" :[],
    "zip_exclude_packages" : []
}

setup(
    name="PdfParser",
    version="1.0",
    description="Parse text data from pdf files into csv file",
    options={"build_exe": build_exe_options},
    executables= [app_exe]
)