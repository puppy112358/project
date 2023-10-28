# imap_runner.py

import sys
sys.path.append('/home/ccy/project/iMAP/ai_infra')
from imap_engine import EngineIMAP

def main():
    input_file_path = '/home/ccy/project/Intelligent-workflow/data/input/test.aig'
    engine = EngineIMAP(input_file_path, 'test.aig.seq')
    engine.read()
    engine.print_stats()

if __name__ == "__main__":
    main()

