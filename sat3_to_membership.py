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


from sat3_commons import *
from sat3_calls import is_sat_varisat

# DIMACS CNF format parser
# - Comment lines start with "c" -> to ignore
# - The first line is of the form
#   "p FORMAT VARIABLES CLAUSES"
#   e.g.  "p cnf 20 91"
# - All following lines each correspond to a clause and are of the form
#   "l1 l2 l3 0" where l1 l2 l3 are literals and each clause is terminated by the value 0 (to ignore)
#   e.g. "4 -18 19 0" means "v4 \/ neg(v18) \/ v19"

def literal_to_string(l):
    if l > 0:
        return "x{}".format(l)
    elif l == 0:
        raise ValueError('literals cannot be 0')
    else:
        return "¬x{}".format(-l)


class Clause3SAT:
    def __init__(self, l1, l2, l3):
        self.l1 = l1
        self.l2 = l2
        self.l3 = l3

    def __str__(self):
        return "{}∨{}∨{}".format(*map(literal_to_string, [self.l1,self.l2,self.l3]))

    def to_dimacs(self):
        return "{} {} {} 0".format(self.l1, self.l2, self.l3)

    @staticmethod
    def from_dimacs(dimacs_str):
        literals = list(filter(None,dimacs_str.split(" ")))[:3]
        return Clause3SAT(*map(int,literals))

    def has_literal(self,l):
        if l == self.l1 or l == self.l2 or l == self.l3:
            return True
        else:
            return False

class Problem3SAT:

    def __init__(self, name, num_var, num_clause, clauses):
        self.name = name
        self.num_var = num_var
        self.num_clause = num_clause
        self.clauses = clauses

    def __str__(self):
        return "∧".join(map(lambda x: "({})".format(x),self.clauses))

    def make_multi_trace(self,membership_to_gen_path):
        f = open("{}{}.htf".format(membership_to_gen_path,self.name), "w")
        multitrace_str = "{\n"
        all_traces = ["  [l{0}] l{0}!m".format(x) for x in range(1,self.num_clause+1)]
        multitrace_str += ";\n".join(all_traces)
        multitrace_str += "\n}"
        f.write(multitrace_str)

    def get_occurences(self, literal):
        occs = []
        for clause_id in range(1,self.num_clause+1):
            if self.clauses[clause_id-1].has_literal(literal):
                occs.append(clause_id)
        return occs

    def stringify_occurence_sequence(self,occurences):
        if len(occurences) == 0:
            return "        o"
        elif len(occurences) == 1:
            occ = occurences[0]
            return "        l{} -- m ->|".format(occ)
        else:
            emissions = map(lambda x:"            l{} -- m ->|".format(x),occurences)
            term= "        strict(\n"
            term += ",\n".join(emissions)
            term+= "\n        )"
            return term

    def stringify_interaction(self):
        interaction_str = "strict(\n"
        for var_id in range(1,self.num_var+1):
            interaction_str += "    alt(\n"
            positive_occurences = self.get_occurences(var_id)
            interaction_str += self.stringify_occurence_sequence(positive_occurences)
            interaction_str += ",\n"
            negative_occurences = self.get_occurences(-var_id)
            interaction_str += self.stringify_occurence_sequence(negative_occurences)
            interaction_str += "\n"
            interaction_str += "    )"
            if var_id < self.num_var:
                interaction_str += ",\n"
            else:
                interaction_str += "\n"
        interaction_str += ")\n"
        return interaction_str

    def stringify_signature(self):
        signature_str = "@message{m}\n"
        all_lfs = ";".join(  ["l{}".format(x) for x in range(1,self.num_clause+1)] )
        signature_str += "@lifeline{"
        signature_str += "{}".format(all_lfs)
        signature_str += "}\n"
        return signature_str

    def get_analysis_options(self):
        return """@analyze_option{
    strategy = DepthFS;
    analysis_kind = hide;
    local_analysis = true;
    goal = WeakPass
}
"""

    def make_interaction(self,membership_to_gen_path):
        f = open("{}{}.hsf".format(membership_to_gen_path,self.name), "w")
        content = self.get_analysis_options()
        content += self.stringify_signature()
        content += self.stringify_interaction()
        f.write(content)

    def to_dimacs(self,parent_path,remark):
        f = open("{}{}.cnf".format(parent_path, self.name), "w")
        content = cnf_template.format(self.name, remark, self.num_var, self.num_clause)
        for clause in self.clauses:
            content += clause.to_dimacs() + "\n"
        f.write(content)

    @staticmethod
    def from_dimacs(name,dimacs_lines):
        got_p_line = False
        num_var = None
        num_clause = None
        clauses = []
        for dimacs_str in dimacs_lines:
            dimacs_str = dimacs_str.strip()
            if dimacs_str.startswith("c"):
                continue
            elif dimacs_str.startswith("p") and not got_p_line:
                content = list(filter(None,dimacs_str.split(" ")))
                num_var = int( content[2] )
                num_clause = int( content[3] )
                got_p_line = True
            elif dimacs_str.startswith("%"):
                break
            elif dimacs_str != "":
                clauses.append(Clause3SAT.from_dimacs(dimacs_str))
        return Problem3SAT(name,num_var,num_clause,clauses)

    def is_SAT(self):
        self.to_dimacs(temp_dir_path,"temporary")
        (result,solution,_) = is_sat_varisat(temp_dir_path,self.name,1)
        return (result,solution)


# Here we parse 3-SAT problems written into the DIMACS format into dedicated Python objects
# We then generate corresponding multi-trace membership problems using a polynomial reduction of the problem
def make_membership_for_problems(problem_dir_path,membership_to_gen_path):
    for filename in os.listdir(problem_dir_path):
        if filename.endswith(".cnf"):
            filename = filename[:-4]
            f = open("{}{}.cnf".format(problem_dir_path, filename), "r")
            prob = Problem3SAT.from_dimacs(filename, f.readlines())
            prob.make_multi_trace(membership_to_gen_path)
            prob.make_interaction(membership_to_gen_path)


