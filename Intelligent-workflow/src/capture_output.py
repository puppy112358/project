import sys
import subprocess
import re
from multiprocessing import Process, Manager

def capture_output(output_queue):
    # 定义要捕获的输出的正则表达式
    pattern = r"Stats of AIG: pis=\d+, pos=\d+, area=\d+, depth=\d+"

    # 运行 main.py 并实时捕获其输出
    with subprocess.Popen(["python3", "/home/ccy/project/Intelligent-workflow/src/main.py"], stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as proc:
        for line in proc.stdout:
            sys.stdout.write(line)  # 打印到控制台
            sys.stdout.flush()
            # 检查输出是否匹配指定的格式
            if re.match(pattern, line.strip()):
                output_queue.put(line.strip())  # 将匹配的输出发送到 main.py

    # 当 main.py 结束时，结束 capture_output.py
    sys.exit()

if __name__ == "__main__":
    with Manager() as manager:
        # 创建一个 Queue 对象来接收子进程的输出
        output_queue = manager.Queue()

        # 使用 Process 运行 capture_output 函数
        p = Process(target=capture_output, args=(output_queue,))
        p.start()
        p.join()


