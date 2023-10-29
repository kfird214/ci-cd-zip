import zipfile, pathlib, argparse, fnmatch
from typing import List, Tuple, Iterable, Union

ROOT_FLAG = "--root_folder"
ADDITIONAL_FLAG = "--input"
OUTPUT_ZIP_FLAG = '--zip'
IGNORE_FLAG = '--ignore'

example_text = f'''
Example:
    zip-folder.py {ROOT_FLAG} "input" {OUTPUT_ZIP_FLAG} "out/out.zip" {IGNORE_FLAG} "*/folder_ignore/*" "*/ignore_file.txt"

    zip-folder.py {ADDITIONAL_FLAG} "input1" "input2" {OUTPUT_ZIP_FLAG} "out/out.zip" {IGNORE_FLAG} "*input1/folder_ignore/*" "*input2/ignore_file.txt"
'''

def str2bool(v: Union[str, bool]):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    if v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    raise argparse.ArgumentTypeError('Boolean value expected.')

parser = argparse.ArgumentParser(
    description='Zip a folder',
    epilog=example_text,
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
parser.add_argument(ROOT_FLAG, type=str, help="The root folder to zip", required=False)
parser.add_argument(ADDITIONAL_FLAG, type=str, nargs='+', help='Additional files to zip', default=[])
parser.add_argument(OUTPUT_ZIP_FLAG, type=str, help='The zip file to create', required=True)
parser.add_argument(IGNORE_FLAG, type=str, nargs='+', help='Patters to ignore from the root folder and additional dirs', default=[])
parser.add_argument('--dry', type=str2bool, help='Dry run, do not create the zip file', default=False)
args = parser.parse_args()

if (args.root_folder is None or args.root_folder == '') and len(args.input) == 0:
    raise argparse.ArgumentError(None, "No input files or root folder specified")

# Define the folder to zip
input_paths = [pathlib.Path(f) for f in args.input if f is not None and f !='']
resolved_input_paths = [rp.resolve() for rp in input_paths]

# DOWN_CHAR = '├'
# INDENT_CHAR = '─'
DOWN_CHAR = '|'
INDENT_CHAR = '-'
C = DOWN_CHAR + INDENT_CHAR

print('Inputs to zip')
for p in resolved_input_paths:
    print(f'{C} "{p}"')
print()

# Define the name of the zip file to create
zip_file_rel_path = args.zip
if args.zip is None or args.zip == '':
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
    print(f'{C} "{p}"')
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
    print(resolved_file_path)
    if resolved_file_path.is_dir():
        print(f"{C} ✖️ 📁 Skipping directory: " + str(file))
        return None

    for ignorePaths in ignore_paths_relative:
        # ignoreP = pathlib.Path(rootResolvedFolder / ignorePaths)
        ignoreP = pathlib.Path(ignorePaths)
        print(f'{C} Testing "{resolved_file_path}" against "{ignoreP}"')
        if str(ignoreP) in str(resolved_file_path) or fnmatch.fnmatch(str(resolved_file_path), str(ignoreP)):
            print(f'{C}─ ✖️ Skipping file because ignore path "{ignoreP}" is in "{resolved_file_path}"')
            return None

    print(f'{C} ✅ Adding file: "{file}" with entry name "{entry_name}"')
    
    return file

# Create the zip file
if args.dry != False:
    zip_file = zipfile.ZipFile(zip_file_path, "w")

for folder_glob_pair in files_to_zip:
    for file in folder_glob_pair[1]:
        rfile = file.resolve()
        root_path = folder_glob_pair[0].resolve()
        entryName = str(rfile).replace(str(root_path), "")
        fpath = add_file_to_zip(rfile, entryName)

        if args.dry != False and fpath is not None:
            zip_file.write(fpath, entryName)

if args.dry != False:
    zip_file.close()