import os
import signal
import subprocess
from dir_walker import dir_walker
from bcolors import print_info, print_header, print_success


def get_intent(dir_path, file, extension):
    rename = str(input("Rename? [yes/no/delete/exit] ")).lower()
    while rename not in ["yes", "no", "delete", "exit"]:
        rename = str(input("Rename? [yes/no/delete/exit] ")).lower()
    if rename == "yes":
        new_name = input("New name?: ")
        if not new_name.endswith(extension):
            new_name += extension
        os.rename(file, os.path.join(dir_path, new_name))
    elif rename == "delete":
        sure = str(input("Are you sure? [yes/no] ")).lower()
        while sure not in ["yes", "no"]:
            sure = str(input("Are you sure? [yes/no] ")).lower()
        if sure == "yes":
            os.remove(file)
    elif rename == "exit":
        return False
    return True


def rename_files(dir_path):
    print_header("Starting rename files...")
    for file in dir_walker(dir_path):
        file_name = os.path.basename(file)
        extension = os.path.splitext(file_name)[1]
        print_info(f"Renaming file: {file_name}")
        process = subprocess.Popen(
            ["xdg-open", file], stdout=subprocess.PIPE, preexec_fn=os.setsid
        )
        intent = get_intent(dir_path, file, extension)
        if not intent:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            print_info("Exiting...")
            break
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        print_success("File renamed successfully!")
    print_success("Finished renaming files!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python rename_files.py <dir> <new_name>")
        sys.exit(1)
    rename_files(sys.argv[1])
