import sys
import os
from pathlib import Path

# Adicionar o diretório raiz do projeto ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))