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

from implem.sat3_to_membership import Clause3SAT,Problem3SAT
from implem.commons import *




class Generator3SAT:

    def __init__(self, name, num_var, num_clause):
        assert( num_clause > 1 )
        self.name = name
        self.num_var = num_var
        self.num_clause = num_clause

    def generate_SAT(self, max_iteration):
        variables = [idx for idx in range(1,self.num_var+1)]
        literals = variables + [-idx for idx in variables]
        clauses = [ Clause3SAT(*random.sample(literals, 3)) ]
        #
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

    def generate_UNSAT(self, max_iteration):
        variables = [idx for idx in range(1,self.num_var+1)]
        literals = variables + [-idx for idx in variables]
        clauses = [ Clause3SAT(*random.sample(literals, 3)) ]
        #
        while max_iteration > 0:
            max_iteration -= 1
            problem = Problem3SAT("temp",self.num_var,len(clauses),clauses)
            (is_sat, solution) = problem.is_SAT()
            if is_sat:
                if len(clauses) == self.num_clause:
                    clauses.pop(random.randint(0, self.num_clause - 1))
                #
                if bool(random.getrandbits(1)):
                    clauses.append( Clause3SAT(*[-idx for idx in random.sample(solution, 3)]) )
                else:
                    clauses.append( Clause3SAT(*random.sample(literals, 3)) )
            else:
                if len(clauses) == self.num_clause:
                    problem = Problem3SAT(self.name, self.num_var, len(clauses), clauses)
                    return problem
                else:
                    clauses.append( Clause3SAT(*random.sample(literals, 3)) )
        return None


def try_generate(sat_kind,var_num,clause_num,max_iteration,num_tries):
    remaining_tries = num_tries
    while remaining_tries > 0:
        print("trying to generate {} with {} variables and {} clauses".format(sat_kind,var_num,clause_num))
        generator = Generator3SAT("mahe_v{}_c{}_{}".format(var_num,clause_num,sat_kind), var_num, clause_num)
        #
        if sat_kind == "SAT":
            problem = generator.generate_SAT(max_iteration)
        elif sat_kind == "UNSAT":
            problem = generator.generate_UNSAT(max_iteration)
        else:
            raise Exception("should be SAT or UNSAT")
        #
        if problem != None:
            return problem
        else:
            remaining_tries = remaining_tries - 1
            print("failed, remains {} tries".format(remaining_tries))

# Here we generate some 3-SAT problems to be later used in experiments
# We generate problems given a number of variables, a number of clauses and given whether we want a Satisfiable or an Unsatisfiable problem*
def generate_custom_problems(custom_name,max_iteration,num_tries,variables,clauses):
    gen_custom_path = "./gen_{}/".format(custom_name)
    random.seed(42)
    empty_directory(gen_custom_path)
    for var_num in range(variables[0],variables[1]+1):
        for clause_num in range(clauses[0],clauses[1]+1):
            problem = try_generate("SAT",var_num,clause_num,max_iteration,num_tries)
            #
            if problem != None:
                problem.to_dimacs(gen_custom_path,"Satisfiable SAT")
            #
            problem = try_generate("UNSAT",var_num,clause_num,max_iteration,num_tries)
            #
            if problem != None:
                problem.to_dimacs(gen_custom_path,"Unsatisfiable UNSAT")


