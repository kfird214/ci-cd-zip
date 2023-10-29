import zipfile, os, pathlib

# Define the folder to zip
folder_to_zip = "input"
rootPath = pathlib.Path(folder_to_zip)
rootResolvedFolder = rootPath.resolve()

# Define the name of the zip file to create
zip_file_rel_path = "out/out.zip"
zip_file_path = pathlib.Path(zip_file_rel_path)
zip_file_path.parent.mkdir(parents=True, exist_ok=True)


# Define the paths to ignore
ignore_paths_relative = [
    "ignore_dir",
    "ignore.txt",
    "dir/ignore.txt",
]

ignore_paths = [os.path.realpath(os.path.join(rootResolvedFolder, p)) for p in ignore_paths_relative]

# Create a list of files to add to the zip file

files_to_zip = rootPath.rglob('*')

# Create the zip file
with zipfile.ZipFile(zip_file_path, "w") as zip_file:
    for file in files_to_zip:
        rfile = file.resolve()
        print(rfile)
        if rfile.is_dir():
            print("├─ ✖️ 📁 Skipping directory: " + str(file))
            continue

        shouldIgnore = False
        for ignorePaths in ignore_paths:
            ignoreP = pathlib.Path(rootResolvedFolder / ignorePaths)
            print(f'├─ Testing "{rfile}" against "{ignoreP}"')
            if rfile.is_relative_to(ignoreP):
                print(f'├── ✖️ Skipping file because ignore path "{ignoreP}"')
                shouldIgnore = True
                break

        if shouldIgnore:
            continue

        print(f'├─ ✅ Adding file: "{file}"')
        entryName = str(rfile).replace(str(rootResolvedFolder), "")
        zip_file.write(file, entryName)

# Move the zip file to the folder to zip
# shutil.move(zip_file_name, folder_to_zip)