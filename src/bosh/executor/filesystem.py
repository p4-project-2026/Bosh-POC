import os
import shutil
from pathlib import Path
from datetime import datetime

class FileSystem:
    def __init__(self, initial_path: str = None):
        self.wd = Path(initial_path).resolve() if initial_path else Path.cwd()
    
    def make_absolute(self, target_path: str):
        path = Path(target_path)
        if not path.is_absolute():
            path = (self.wd / path).resolve()
        return path
    
    def go_to(self, target_path: str):
        new_wd = self.make_absolute(target_path)
        if not new_wd.is_dir():
            raise Exception(f"Cannot go to '{target_path}': Not a directory")
        
        self.wd = new_wd

    def go_up(self):
        self.wd = self.wd.parent

    def make(self, target_path, name, is_folder = False):
        path = self.make_absolute(target_path / name) if target_path else self.wd / name
        
        if is_folder:
            path.mkdir(parents=True, exist_ok=True) # parents=True to create any missing parent directories, exist_ok=True to avoid error if it already exists
        else:
            path.parent.mkdir(parents=True, exist_ok=True) # Ensure parent directories exist
            path.touch(exist_ok=True)
    
    def delete(self, target_path):
        path = self.make_absolute(target_path)
        if path.is_dir():
            shutil.rmtree(path) # Recursively delete directory and its contents
        elif path.is_file():
            path.unlink()
        else:
            raise Exception(f"Cannot delete '{target_path}': Not a file or directory")
    
    def rename(self, target_path, new_name):
        path = self.make_absolute(target_path)
        if not path.exists():
            raise Exception(f"Cannot rename '{target_path}': Path does not exist")
        
        path.rename(path.parent / new_name)

    def copy(self, source_path, target_path):
        src = self.make_absolute(source_path)
        dst = self.make_absolute(target_path)

        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True) # dirs_exist_ok=True to allow copying into existing directories
        elif src.is_file():
            shutil.copy2(src, dst) # copy2 to preserve metadata

    def move(self, source_path, target_path):
        src = self.make_absolute(source_path)
        dst = self.make_absolute(target_path)

        shutil.move(src, dst)

    def read(self, target_path):
        path = self.make_absolute(target_path)
        if not path.is_file():
            raise Exception(f"Cannot read '{target_path}': Not a file")
        
        return path.read_text()
    
    def write(self, target_path, data, append=False):
        path = self.make_absolute(target_path)
        if path.is_dir():
            raise Exception(f"Cannot write to '{target_path}': Is a directory")
        
        mode = 'a' if append else 'w' # add to end of file (append) or overwrite (write)
        with path.open(mode) as f:
            f.write(data)
    
    def list_dir(self, target_path=None):
        path = self.make_absolute(target_path) if target_path else self.wd
        if not path.is_dir():
           return []
        return [entry.name for entry in path.iterdir()] # Return just the names of the entries in the directory
    
    def get_metadata(self, target_path):
        path = self.make_absolute(target_path)
        if not path.exists():
            raise Exception(f"Cannot get metadata for '{target_path}': Path does not exist")
        
        meta = path.stat()
        return {
            "name": path.name,
            "size": meta.st_size,
            "location": str(path.resolve()),
            "creation_date": datetime.fromtimestamp(meta.st_birthtime).isoformat(), 
            "modification_date": datetime.fromtimestamp(meta.st_mtime).isoformat(),
            "is_folder": path.is_dir(),
            "is_file": path.is_file(),
            "age": (datetime.now() - datetime.fromtimestamp(meta.st_mtime)).total_seconds()
        }