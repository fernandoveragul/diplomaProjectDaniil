from dependencies.config import get_list_files, do_filer_file_list
from dependencies.exceptions import InvalidFolderType

print(do_filer_file_list(files=get_list_files(name_dir="examples")))
