# Re-export everything from views_main.py
from accounting.views_main import *

# Explicitly list the ViewSets needed by urls.py
from accounting.views_main import (
    VoIPCallViewSet,
    VoIPCallLogViewSet,
)
