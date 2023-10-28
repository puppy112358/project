import os
import time
import random
import sys
import subprocess
import ast
import re
from io import StringIO
from contextlib import redirect_stdout

sys.path.append('/home/ccy/project/iMAP/ai_infra')
sys.path.append('/home/ccy/project/iMAP/build/cli')
from imap_engine import EngineIMAP

class GeneticOptimized:
    '''
    使用遗传算法进行组合逻辑优化
    '''

    def __init__(self):
        print("初始化 GeneticOptimized ...")
        # 使用固定路径初始化 IMAP 引擎
        self.input_file_path = '/home/ccy/project/Intelligent-workflow/data/input/test.aig'
        self.engine = EngineIMAP(self.input_file_path, 'test.aig.seq')
        print("GeneticOptimized 初始化完成!")

    

    def run_fixed_sequence(self):
        # 读取输入文件
        self.engine.read()

        # Randomly select 10 operators from the list ['rewrite', 'refactor', 'balance']
        operators = random.choices(['rewrite', 'refactor', 'balance'], k=10)
        for op in operators:
            if op == 'rewrite':
                self.engine.rewrite(priority_size=13, cut_size=3)
            elif op == 'refactor':
                self.engine.refactor(max_input_size=9, max_cone_size=15)
            elif op == 'balance':
                self.engine.balance()
            
            # 使用 redirect_stdout 来捕获 print_stats 的输出
            captured_output = StringIO()
            with redirect_stdout(captured_output):
                self.engine.print_stats()
            stats_output = captured_output.getvalue()
            print("输出为",stats_output)  # 作为示例，这里简单地打印捕获的输出

        # 技术映射阶段
        self.engine.map_fpga()
        self.engine.add_sequence('map_fpga')
        self.engine.write()  # 将优化序列写入文件

print("开始主执行 ...")
if __name__ == '__main__':
    try:
        optimizer = GeneticOptimized()
        optimizer.run_fixed_sequence()
    except Exception as e:
        print(f"主函数中出错: {e}")

