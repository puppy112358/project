import sys
import json
import os

sys.path.append('../iMAP/ai_infra')
sys.path.append('../iMAP/build/cli')
from imap_engine import EngineIMAP

def optimize_aig(chromosome):
    # 初始化执行标志为 False
    executed_stats = False
    try:
        # 初始化 IMAP 引擎
        input_file_path = './data/input/test.aig'
        engine = EngineIMAP(input_file_path, 'test.aig.seq')
        
        # 读取输入文件
        engine.read()

        # 仅遍历染色体的 commands 键
        for gene_name in chromosome["commands"]:
            if gene_name == "rewrite":
                engine.rewrite(priority_size=chromosome["rewrite"]["priority_size"], cut_size=chromosome["rewrite"]["cut_size"])
            elif gene_name == "refactor":
                engine.refactor(max_input_size=chromosome["refactor"]["max_input_size"], max_cone_size=chromosome["refactor"]["max_cone_size"])
            elif gene_name == "balance":
                engine.balance()

        # 输出统计信息
        engine.print_stats()
        
        # 设置执行标志为 True
        executed_stats = True
    except Exception as e:
        print(f"Error in optimize_aig: {e}")

    # 检查执行标志
    if not executed_stats:
        print("Error: Code did not reach engine.print_stats()")

if __name__ == '__main__':
    temp_file_path = sys.argv[1]
    
    if not os.path.exists(temp_file_path):
        print(f"Error: Temporary file '{temp_file_path}' not found!")
        sys.exit(1)  # Exit with an error code

    # 从临时文件中加载染色体数据
    with open(temp_file_path, 'r') as file:
        chromosome = json.load(file)
    optimize_aig(chromosome)


