"""
DISABLED - IMAP Email Import is disabled
"""

# Dummy class to prevent import errors
class CrmIMAP:
    def __init__(self, *args, **kwargs):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass
    
    def login(self, *args, **kwargs):
        pass
    
    def logout(self, *args, **kwargs):
        pass
    
    def fetch_emails(self, *args, **kwargs):
        return []
    
    def close(self, *args, **kwargs):
        pass


# Prevent any thread from starting
def start_imap(*args, **kwargs):
    """DISABLED"""
    pass


def stop_imap(*args, **kwargs):
    """DISABLED"""
    pass


class ImportEmails:
    """DISABLED - Dummy class"""
    def __init__(self, *args, **kwargs):
        pass
    
    def start(self):
        pass
    
    def run(self):
        pass
    
    def stop(self):
        pass