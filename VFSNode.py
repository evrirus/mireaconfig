class VFSNode:
    def __init__(self, name: str, owner: str = "root"):
        self.name = name
        self.owner = owner

    def is_dir(self):
        return False

    def is_file(self):
        return False
