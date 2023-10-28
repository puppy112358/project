import os
import time
import random
import sys
import subprocess
import re
import json
import tempfile

sys.path.append('../iMAP/ai_infra')
sys.path.append('../iMAP/build/cli')
from imap_engine import EngineIMAP

class GeneticOptimized:
    '''
    使用遗传算法进行组合逻辑优化
    '''
    def __init__(self, population_size=30, generations=5, mutation_rate=0.2, elite_rate=0.1, elite_mutation_rate=0.05):
        print("初始化 GeneticOptimized ...")
        # 使用固定路径初始化 IMAP 引擎
        self.input_file_path = './data/input/test.aig'
        self.engine = EngineIMAP(self.input_file_path, 'test.aig.seq')

        # 遗传算法参数初始化
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elite_mutation_rate = elite_mutation_rate  # 为精英染色体定义较低的变异率
        self.elite_rate = elite_rate

        # 初始化种群
        self.population = self.init_population()

        # 初始化全局最佳染色体和适应度
        self.global_best_chromosome = None
        self.global_best_fitness = float('-inf')  # 初始设置为负无穷大

        print("GeneticOptimized 初始化完成!")

    def init_population(self):
        '''
        初始化种群：随机生成优化序列以及对应的参数作为染色体
        '''
        print("初始化种群 ...")
        population = []
        for _ in range(self.population_size):
            chromosome = {
                "commands": [random.choice(['rewrite', 'refactor', 'balance']) for _ in range(5)],
                "rewrite": {
                    "priority_size": random.randint(6, 20),
                    "cut_size": random.randint(2, 4)
                },
                "refactor": {
                    "max_input_size": random.randint(6, 12),
                    "max_cone_size": random.randint(10, 20)
                }
            }
            population.append(chromosome)
        print("种群初始化完成!")
        return population

    def fitness(self, chromosome):
        """
        适应度函数，用于评估染色体的适应度。
        """
        # 初始化适应度值
        fitness = 0
        max_retries = 1  # 设置最大重试次数
        retries = 0
        
        while retries < max_retries:
            # 将染色体数据序列化为 JSON 并保存到临时文件中
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as tmp:
                json.dump(chromosome, tmp)
                tmp_path = tmp.name
            
            # 使用 subprocess.Popen 运行 optimize_aig.py，并传递临时文件的路径作为参数
            cmd = [sys.executable, 'src/optimize_aig.py', tmp_path]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
            
            # 等待子进程完成并捕获其输出
            output, _ = process.communicate()
            
            # 删除临时文件
            os.remove(tmp_path)
            
            pattern = r"Stats of .*?: pis=(\d+), pos=(\d+), area=(\d+), depth=(\d+)"
            match = re.search(pattern, output)

            if match:
                stats = {
                    'pis': int(match.group(1)),
                    'pos': int(match.group(2)),
                    'area': int(match.group(3)),
                    'depth': int(match.group(4))
                }
                
                # 根据提取的统计数据计算适应度值
                cost = 0.6 * stats['depth'] + 0.4 * stats['area']
                fitness = 1000 / cost
                print(fitness)
                break  # 成功提取信息，跳出循环
            else:
                #print("在适应度函数中出现错误: 无法从统计数据字符串中提取信息")
                #print("捕获到的输出:", output)  # 输出捕获到的语句
                #retries += 1  # 递增重试计数
                print("计算失败")
                return 0

        # 如果重试次数达到最大值，则输出失败的染色体组合
        #if retries == max_retries:
            #print("经过2次重试后，仍然无法从统计数据中提取信息。失败的染色体组合为：", chromosome)

        return fitness




    def select_parents(self, population, fitness_values):
        '''
        使用轮盘赌选择法选择两个父代
        '''
        total_fit = sum(fitness_values)
        pick = random.uniform(0, total_fit)
        current = 0
        for i, value in enumerate(fitness_values):
            current += value
            if current > pick:
                parent1 = population[i]
                break

        pick = random.uniform(0, total_fit)
        current = 0
        for i, value in enumerate(fitness_values):
            current += value
            if current > pick:
                parent2 = population[i]
                break

        return parent1, parent2

    def crossover(self, parent1, parent2):
        '''
        单点交叉
        '''
        print("开始交叉操作 ...")
        idx = random.randint(1, len(parent1["commands"]) - 2)
        child1_commands = parent1["commands"][:idx] + parent2["commands"][idx:]
        child2_commands = parent2["commands"][:idx] + parent1["commands"][idx:]
        child1 = {
            "commands": child1_commands,
            "rewrite": parent1["rewrite"] if random.random() < 0.5 else parent2["rewrite"],
            "refactor": parent1["refactor"] if random.random() < 0.5 else parent2["refactor"]
        }
        child2 = {
            "commands": child2_commands,
            "rewrite": parent2["rewrite"] if random.random() < 0.5 else parent1["rewrite"],
            "refactor": parent2["refactor"] if random.random() < 0.5 else parent1["refactor"]
        }
        print("交叉操作完成!")
        return child1, child2

    def mutate(self, chromosome, is_elite=False):
        '''
        变异
        '''
        mutation_rate = self.elite_mutation_rate if is_elite else self.mutation_rate
        print("开始变异操作 ...")
        if random.random() < mutation_rate:
            idx = random.randint(0, len(chromosome["commands"]) - 1)
            chromosome["commands"][idx] = random.choice(['rewrite', 'refactor', 'balance'])
        
        # 随机变异某些参数
        if random.random() < mutation_rate:
            chromosome["rewrite"]["priority_size"] = random.randint(6, 20)
        if random.random() < mutation_rate:
            chromosome["rewrite"]["cut_size"] = random.randint(2, 4)
        if random.random() < mutation_rate:
            chromosome["refactor"]["max_input_size"] = random.randint(6, 12)
        if random.random() < mutation_rate:
            chromosome["refactor"]["max_cone_size"] = random.randint(10, 20)
        print("变异操作完成!")
        return chromosome

    def run(self):
        '''
        运行遗传算法
        '''
        print("开始遗传算法 ...")
        try:
            for generation in range(self.generations):
                print(f"代数 {generation + 1}")
                fitness_values = [self.fitness(chromosome) for chromosome in self.population]

                # 检查是否有新的最佳染色体
                best_fitness_this_generation = max(fitness_values)
                best_chromosome_this_generation = self.population[fitness_values.index(best_fitness_this_generation)]
                
                if best_fitness_this_generation > self.global_best_fitness:
                    self.global_best_fitness = best_fitness_this_generation
                    self.global_best_chromosome = best_chromosome_this_generation

                # 添加精英策略: 保存适应度最高的染色体
                elite_count = int(self.elite_rate * self.population_size)
                elites = sorted(self.population, key=lambda x: self.fitness(x), reverse=True)[:elite_count]
                
                new_population = []
                # 先将精英染色体添加到新种群中，并进行较小程度的变异
                for elite in elites:
                    new_population.append(self.mutate(elite, is_elite=True))

                # 对其他染色体进行交叉和较大程度的变异
                for _ in range((self.population_size - elite_count) // 2):
                    parent1, parent2 = self.select_parents(self.population, fitness_values)
                    child1, child2 = self.crossover(parent1, parent2)
                    new_population.extend([self.mutate(child1), self.mutate(child2)])

                self.population = new_population
                self.population.sort(key=lambda x: self.fitness(x), reverse=True)

                # 输出全局最佳染色体和其适应度
                print(f"全局最佳染色体: {self.global_best_chromosome}")
                print(f"全局最佳适应度: {self.global_best_fitness}")

                # 技术映射阶段
                self.engine.map_fpga()
                self.engine.add_sequence('map_fpga')
                self.engine.write()  # 将优化序列写入文件
        except Exception as e:
            print(f"运行函数中出错: {e}")


print("开始主执行 ...")
if __name__ == '__main__':
    try:
        optimizer = GeneticOptimized()
        optimizer.run()
    except Exception as e:
            print(f"主函数中出错: {e}")