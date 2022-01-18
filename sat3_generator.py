#
# Copyright 2022 Erwan Mahe (github.com/erwanM974)
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import random

from sat3_to_membership import Clause3SAT,Problem3SAT
from sat3_commons import *




class Generator3SAT:

    def __init__(self, name, num_var, num_clause):
        assert( num_clause > 1 )
        self.name = name
        self.num_var = num_var
        self.num_clause = num_clause

    def generate_SAT(self,parent_path):
        variables = [idx for idx in range(1,self.num_var+1)]
        literals = variables + [-idx for idx in variables]
        clauses = [ Clause3SAT(*random.sample(literals, 3)) ]
        #
        max_iteration = 100
        while max_iteration > 0:
            max_iteration -= 1
            clauses.append( Clause3SAT(*random.sample(literals,3)) )
            problem = Problem3SAT("temp",self.num_var,len(clauses),clauses)
            (is_sat,solution) = problem.is_SAT()
            if is_sat:
                if len(clauses) == self.num_clause:
                    problem = Problem3SAT(self.name, self.num_var, len(clauses), clauses)
                    return problem
                else:
                    continue
            else:
                clauses.pop()
        return None

    def generate_UNSAT(self, parent_path):
        variables = [idx for idx in range(1,self.num_var+1)]
        literals = variables + [-idx for idx in variables]
        clauses = [ Clause3SAT(*random.sample(literals, 3)) ]
        #
        max_iteration = 200
        while max_iteration > 0:
            max_iteration -= 1
            problem = Problem3SAT("temp",self.num_var,len(clauses),clauses)
            (is_sat, solution) = problem.is_SAT()
            if is_sat:
                clauses.append( Clause3SAT(*[-idx for idx in random.sample(solution, 3)]) )
                if len(clauses) > self.num_clause:
                    break
            else:
                if len(clauses) == self.num_clause:
                    problem = Problem3SAT(self.name, self.num_var, len(clauses), clauses)
                    return problem
                else:
                    clauses.append( Clause3SAT(*random.sample(literals, 3)) )
        return None



# Here we generate some 3-SAT problems to be later used in experiments
# We generate problems given a number of variables, a number of clauses and given whether we want a Satisfiable or an Unsatisfiable problem*
def generate_custom_problems(gen_problem_path):
    random.seed(42)
    empty_directory(gen_problem_path)
    for var_num in range(3,9):
        for clause_num in range(3,40):
            generator = Generator3SAT("mahe_v{}_c{}_SAT".format(var_num,clause_num),var_num,clause_num)
            problem = generator.generate_SAT(temp_dir_path)
            if problem != None:
                problem.to_dimacs(gen_problem_path,"Satisfiable SAT")
            #
            generator = Generator3SAT("mahe_v{}_c{}_UNSAT".format(var_num,clause_num),var_num,clause_num)
            problem = generator.generate_UNSAT(temp_dir_path)
            if problem != None:
                problem.to_dimacs(gen_problem_path,"Unsatisfiable UNSAT")


