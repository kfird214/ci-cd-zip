import zipfile, pathlib, argparse, fnmatch
from typing import List, Tuple, Iterable

example_text = '''
Example:
    zip-folder.py "folder" "folder.zip" --ignore "*/folder_ignore/*" "*/ignore_file.txt"
'''

parser = argparse.ArgumentParser(description='Zip a folder', epilog=example_text)
parser.add_argument("--root_folder", type=str, help="The root folder to zip", required=False)
parser.add_argument('--input', type=str, nargs='+', help='The folders to zip', default=[])
parser.add_argument('--zip', type=str, help='The zip file to create')
parser.add_argument('--ignore', type=str, nargs='+', help='The paths to ignore', default=[])
args = parser.parse_args()


# Define the folder to zip
input_paths = [pathlib.Path(f) for f in args.input]
resolved_input_paths = [rp.resolve() for rp in input_paths]

print('Inputs to zip')
for p in resolved_input_paths:
    print(f'├─ "{p}"')
print()

# Define the name of the zip file to create
zip_file_rel_path = args.zip
if args.zip is None:
    zip_file_rel_path = 'out.zip'
    print(f'No zip file specified, using "{zip_file_rel_path}"')

zip_file_path = pathlib.Path(zip_file_rel_path)
zip_file_path.parent.mkdir(parents=True, exist_ok=True)

print(f'Zip file: "{zip_file_path.resolve()}"')

# Define the paths to ignore
ignore_paths_relative = args.ignore

print()
print('Ignore paths')
for p in ignore_paths_relative:
    print(f'├─ "{p}"')
print()

# Create a list of files to add to the zip file
files_to_zip: List[Tuple[pathlib.Path, Iterable[pathlib.Path]]] = []
if args.root_folder is not None:
    rootResolvedFolder = pathlib.Path(args.root_folder).resolve()
    print(f'Root folder: "{rootResolvedFolder}"')
    files_to_zip.append((rootResolvedFolder, rootResolvedFolder.rglob('*')))

for inputPath in input_paths:
    if inputPath.is_dir():
        files_to_zip.append((inputPath.parent, inputPath.rglob('*')))
    elif inputPath.is_file():
        files_to_zip.append((inputPath.parent, [inputPath]))

def add_file_to_zip(resolved_file_path: pathlib.Path, entry_name: str):
    rfile = resolved_file_path
    print(rfile)
    if rfile.is_dir():
        print("├─ ✖️ 📁 Skipping directory: " + str(file))
        return

    for ignorePaths in ignore_paths_relative:
        # ignoreP = pathlib.Path(rootResolvedFolder / ignorePaths)
        ignoreP = pathlib.Path(ignorePaths)
        print(f'├─ Testing "{rfile}" against "{ignoreP}"')
        if str(ignoreP) in str(rfile) or fnmatch.fnmatch(str(rfile), str(ignoreP)):
            print(f'├── ✖️ Skipping file because ignore path "{ignoreP}" is in "{rfile}"')
            return

    print(f'├─ ✅ Adding file: "{file}" with entry name "{entry_name}"')
    
    zip_file.write(file, entry_name)

# Create the zip file
with zipfile.ZipFile(zip_file_path, "w") as zip_file:
    for folder_glob_pair in files_to_zip:
        for file in folder_glob_pair[1]:
            rfile = file.resolve()
            root_path = folder_glob_pair[0].resolve()
            entryName = str(rfile).replace(str(root_path), "")
            add_file_to_zip(rfile, entryName)
