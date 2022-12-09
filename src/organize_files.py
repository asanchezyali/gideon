import os
import hashlib
from pathlib import Path
import json
import signal
import subprocess
from src.dir_walker import dir_walker
from src.filename_formats import invoice_validator, article_validator
from utils.bcolors import print_info


def organize_files(dir_input, dir_output):
    print_info("Starting organize files...")
    for file in dir_walker(Path(dir_input)):
        filename = os.path.basename(file)
        file_hash = hashlib.md5(open(file, "rb").read()).hexdigest()
        file_hash_path = Path(dir_output) / "file_hashes.json"
        if file_hash_path.exists():
            with open(file_hash_path, "r") as f:
                file_hashes = json.load(f)
        else:
            file_hashes = {}
        if file_hash in file_hashes:
            print_info(f"Duplicate file: {file}")
            print_info(f"Original file: {file_hashes[file_hash]}")
            process_one = subprocess.Popen(
                ["xdg-open", file], stdout=subprocess.PIPE, preexec_fn=os.setsid
            )
            process_two = subprocess.Popen(
                ["xdg-open", file_hashes[file_hash]],
                stdout=subprocess.PIPE,
                preexec_fn=os.setsid,
            )
            intent = str(input("Remove? [yes/no] ")).lower()
            while intent not in ["yes", "no"]:
                intent = input("Remove? [yes/no] ")
            if intent == "yes":
                os.killpg(os.getpgid(process_one.pid), signal.SIGTERM)
                os.killpg(os.getpgid(process_two.pid), signal.SIGTERM)
                os.remove(file)
            else:
                os.killpg(os.getpgid(process_one.pid), signal.SIGTERM)
                os.killpg(os.getpgid(process_two.pid), signal.SIGTERM)
        else:

            if invoice_validator(filename):
                _, company, invoice_or_report, _ = filename.split(".")
                new_dir = (
                    Path(dir_output) / invoice_or_report.capitalize() / company.upper()
                )
                print_info(f"Moving {file} to {new_dir}")
                new_dir.mkdir(parents=True, exist_ok=True)
                os.rename(file, os.path.join(new_dir, filename))
                file_hashes[file_hash] = os.path.join(new_dir, filename)
                with open(file_hash_path, "w") as f:
                    json.dump(file_hashes, f)
            if article_validator(filename):
                _, year, _, topic, doc_type, _ = filename.split(".")
                new_dir = (
                    Path(dir_output) / topic.capitalize() / doc_type.capitalize() / year
                )
                print_info(f"Moving {file} to {new_dir}")
                new_dir.mkdir(parents=True, exist_ok=True)
                os.rename(file, os.path.join(new_dir, filename))
                file_hashes[file_hash] = os.path.join(new_dir, filename)
                with open(file_hash_path, "w") as f:
                    json.dump(file_hashes, f)
    print_info("Finished organizing files.")
    for root, dirs, _ in os.walk(dir_input, topdown=False):
        for name in dirs:
            if not os.listdir(os.path.join(root, name)):
                print_info(f"Removing empty dir: {os.path.join(root, name)}")
                os.rmdir(os.path.join(root, name))

    if not os.listdir(dir_input):
        print_info(f"Removing empty dir: {dir_input}")
        os.rmdir(dir_input)
