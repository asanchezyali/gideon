import os
import json
import shutil
from hashlib import md5
from pathlib import Path
from src.constants import EXCLUDE_PROJECT_DIR
from src.dir_walker import dir_walker
from src.constants import DocType, TOPICS, EXCLUDE_PROJECT_DIR, FORMAT_RESEARCH_PROJECT, FORMAT_COMMERCIAL_PROJECT
from src.rename_files import rename_all_files
from utils.bcolors import print_error, print_info, print_success
from utils.managers import open_file, close_file
from utils.strings import camel_case


def calculate_file_hash(file):
    return md5(open(file, "rb").read()).hexdigest()


def load_file_hashes(dir_output):
    file_hash_path = Path(dir_output) / "file_hashes.json"
    if file_hash_path.exists():
        with open(file_hash_path, "r") as f:
            file_hashes = json.load(f)
            return file_hashes, file_hash_path
    else:
        return {}, file_hash_path


def open_duplicate_files(file, duplicate_file):
    print_info(f"Duplicate file: {file}")
    print_info(f"Original file: {duplicate_file}")
    process_one = open_file(file)
    process_two = open_file(duplicate_file)
    return process_one, process_two


def remove_duplicate_file(intent, file, process_one, process_two):
    if intent == "yes":
        close_file(process_one)
        close_file(process_two)
        os.remove(file)
        print_success(f"Removed {file}")
    else:
        close_file(process_one)
        close_file(process_two)
        print_info(f"Kept {file}")


def save_normal_doc(file, filename, dir_output):
    try:
        print_info(f"Saving {file}...")
        _, year, _, topic, doc_type, _ = filename.split(".")
        topic = TOPICS[topic]
        doc_type = DocType.get_type_docs()[doc_type]
        new_dir = (
            Path(dir_output)
            / camel_case(topic).replace(" ", "_")
            / doc_type.capitalize().replace(" ", "_")
            / year
        )
        print_info(f"Moving {file} to {new_dir}...")
        new_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(file, os.path.join(new_dir, filename))
        os.remove(file)
        return os.path.join(new_dir, filename)
    except Exception as error:
        print_error(f'Error in the file "{filename}"')
        print_error(error)
        return None


def save_article(file, filename, dir_output):
    return save_normal_doc(file, filename, dir_output)


def save_book(file, filename, dir_output):
    return save_normal_doc(file, filename, dir_output)


def save_thesis(file, filename, dir_output):
    return save_normal_doc(file, filename, dir_output)


def save_commercial_doc(file, filename, dir_output):
    try:
        print_info(f"Saving {file}...")
        date, company, _, doc_type, _ = filename.split(".")
        doc_type = DocType.get_type_docs()[doc_type]
        new_dir = (
            Path(dir_output)
            / camel_case(doc_type).replace(" ", "_")
            / company.upper().replace(" ", "_")
            / date
        )
        print_info(f"Moving {file} to {new_dir}...")
        new_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(file, os.path.join(new_dir, filename))
        os.remove(file)
        return os.path.join(new_dir, filename)
    except Exception as error:
        print_error(f'Error in the file "{filename}"')
        print_error(error)
        return None


def save_commercial_document(file, filename, dir_output):
    return save_commercial_doc(file, filename, dir_output)


def save_legal_document(file, filename, dir_output):
    return save_commercial_doc(file, filename, dir_output)


def save_nda(file, filename, dir_output):
    return save_commercial_doc(file, filename, dir_output)


save_file_actions = {
    DocType.ARTICLE: save_article,
    DocType.BOOK: save_book,
    DocType.THESIS: save_thesis,
    DocType.COMMERCIAL_DOCUMENT: save_commercial_document,
    DocType.LEGAL_DOCUMENT: save_legal_document,
    DocType.NON_DISCLOSURE_AGREEMENT: save_nda,
}


def get_doc_type(filename):
    chunks = filename.split(".")
    return chunks[-2]


def _delete_empty_dirs(dir_input):
    for root, dirs, _ in os.walk(dir_input, topdown=False):
        for name in dirs:
            if not os.listdir(os.path.join(root, name)):
                print_info(f"Removing empty dir: {os.path.join(root, name)}")
                os.rmdir(os.path.join(root, name))

    if not os.listdir(dir_input):
        print_info(f"Removing empty dir: {dir_input}")
        os.rmdir(dir_input)


def move_project_dir(dir_input, dir_output):
    print_info("Starting move project dir...")
    for root, dirs, _ in os.walk(dir_input):
        for dirname in dirs:
            chunks = dirname.split(".")
            if len(chunks) != 3:
                print_error(f"{dirname} is not a valid project name")
                print_info(f"Expected format: {FORMAT_RESEARCH_PROJECT}")
                continue
            _, topic, project_type = dirname.split(".")
            if project_type == "Owner":
                print_info(f"Moving {dirname} to {dir_output}...")
                topic = TOPICS[topic]
                new_dir = (
                    Path(dir_output)
                    / topic.capitalize().replace(" ", "_")
                    / "Projects"
                    / dirname.replace(" ", "_")
                )
                print_info(f"Moving {dirname} to {new_dir}...")
                shutil.move(os.path.join(root, dirname), new_dir)
            elif project_type == "Job":
                print_info(f"Moving {dirname} to {dir_output}...")
                new_dir = (
                    Path(dir_output)
                    / "Jobs"
                    / topic.upper().replace(" ", "_")
                    / "Projects"
                    / dirname.replace(" ", "_")
                )
                print_info(f"Moving {dirname} to {new_dir}...")
                shutil.move(os.path.join(root, dirname), new_dir)
            else:
                print_error(f"Unknown project type: {project_type}")
                print_error(f"Project type must be 'owner' or 'job'")
                print_error(f"Project type found: {project_type}")
                print_error(f"Project dir: {dirname}")
                print_error(f"Project dir path: {os.path.join(root, dirname)}")
                print_error("Aborting...")
    print_info("Finished move project dir.")


def organize_all_files(dir_input, dir_output):
    print_info("Starting rename files...")
    rename_all_files(dir_input)
    print_info("Starting organize files...")

    for file in dir_walker(dir_input, dir_excludes=EXCLUDE_PROJECT_DIR):
        print_info(f"Processing {file}...")
        filename = os.path.basename(file)
        file_hash = calculate_file_hash(file)
        file_hashes, file_hash_path = load_file_hashes(dir_output)

        if file_hash in file_hashes:
            process_one, process_two = open_duplicate_files(
                file, file_hashes[file_hash]
            )
            intent = str(input("Remove? [yes/no] ")).lower()
            while intent not in ["yes", "no"]:
                intent = input("Remove? [yes/no] ")
            remove_duplicate_file(intent, file, process_one, process_two)
        else:
            doc_type = get_doc_type(filename)
            new_file_path = save_file_actions[doc_type](file, filename, dir_output)
            if new_file_path:
                file_hashes[file_hash] = new_file_path
                with open(file_hash_path, "w") as f:
                    json.dump(file_hashes, f)

    _delete_empty_dirs(dir_input)
    print_info("Finished organizing files.")
