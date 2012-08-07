def get_model():
    from foundry.models import FoundryComment
    return FoundryComment


def get_form():
    from foundry.forms import CommentForm
    return CommentForm

"""Most monkey patches are loaded when models.py is loaded. However, some 
management commands never load models.py (eg. collectstatic). Applicable 
patches must be appliied here."""

"""FileSystemStorage must be able to handle missing directories. If a foundry 
based product has a layer 'foo' then collectstatic must not break."""
import os

from django.core.files.storage import FileSystemStorage

def FileSystemStorage_listdir(self, path):
        if not self.exists(path):
            return [], []
        path = self.path(path)
        directories, files = [], []
        for entry in os.listdir(path):
            if os.path.isdir(os.path.join(path, entry)):
                directories.append(entry)
            else:
                files.append(entry)
        return directories, files

FileSystemStorage.listdir = FileSystemStorage_listdir

