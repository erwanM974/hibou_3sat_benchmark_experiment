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

import subprocess
import io
import os
import time
import statistics

def is_sat_varisat(parent_path,name,num_tries):
    outwrap = None
    tries = []
    while len(tries) < num_tries:
        t_start = time.time()
        varisat_proc = subprocess.Popen(["./varisat.exe", "{}{}.cnf".format(parent_path, name)],
                                        stdout=subprocess.PIPE)
        varisat_proc.wait()
        tries.append( time.time() - t_start )
        outwrap = io.TextIOWrapper(varisat_proc.stdout, encoding="utf-8")
    t_total = statistics.median(tries)
    is_sat = False
    for line in outwrap:
        if "ERROR" in line:
            raise Exception(line)
        elif "s UNSATISFIABLE" in line:
            if is_sat:
                raise Exception("cannot be both SAT and UNSAT")
            else:
                return (False, [], t_total)
        elif "s SATISFIABLE" in line:
            is_sat = True
        elif line.startswith("v"):
            if not is_sat:
                raise Exception("cannot have solution if UNSAT")
            solution = [int(sol) for sol in line[2:].split(" ")[:-1]]
            return (True, solution, t_total)



def is_sat_via_membership(parent_path, name,num_tries):
    hsf_file = "{}{}.hsf".format(parent_path, name)
    htf_file = "{}{}.htf".format(parent_path, name)
    #
    outwrap = None
    tries = []
    while len(tries) < num_tries:
        t_start = time.time()
        hibou_proc = subprocess.Popen(["./hibou_label.exe", "analyze", hsf_file, htf_file],
                                      stdout=subprocess.PIPE)
        hibou_proc.wait()
        tries.append(time.time() - t_start)
        outwrap = io.TextIOWrapper(hibou_proc.stdout, encoding="utf-8")
    t_total = statistics.median(tries)
    #
    for line in outwrap:
        if "WeakPass" in line:
            return (True,t_total)
        elif "Fail" in line:
            return (False,t_total)
        elif "Inconc" in line:
            raise Exception("Inconc ?")

# This experiment consists in solving 3-SAT problems using two methods, to ascertain that results using both methods are equal and to compare the time that is required
# Those two methods are:
# 1 - using the varisat SAT solver
# 2 - solving a multi-trace membership problem issued from a polynomial reduction of the initial 3-SAT problem
#
# In order to launch the experiment use the "experiment" method on:
# 1 - the path towards the directory which contains the problems to treat in .cnf, .hsf and .htf formats
#     for each problem of name "prob", the directory must contains three files:
#       + "prob.cnf" in DIMACS format
#       + "prob.hsf", specifying an interaction model, it comes from the conversion performed by the script "sat3_to_membership.py"
#       + "prob.htf", specifying a multi-trace, it comes from the conversion performed by the script "sat3_to_membership.py"
# 2 - the name of the ".csv" file that is to be generated from running the experiment
# 3 - the number of times/tries to perform each computation; then the time that will be displayed will be a mean value of those tries
#     so as to have more consistent results
def experiment(saved_path,csv_name,num_tries):
    f = open("{}.csv".format(csv_name), "w")
    f.truncate(0) # empty file
    f.write("name,varisat_res,varisat_time,hibou_res,hibou_time\n")
    f.flush()
    #
    for filename in os.listdir(saved_path):
        if filename.endswith(".cnf"):
            name = filename[:-4]
            (varisat_result,varisat_solution,varisat_t_total) = is_sat_varisat(saved_path,name,num_tries)
            (hibou_result,hibou_t_total) = is_sat_via_membership(saved_path,name,num_tries)
            if varisat_result != hibou_result:
                raise Exception("not same result for satisfiability for name:{} :: varisat:{} - hibou:{}".format(name,varisat_result,hibou_result))
            f.write("{},{},{},{},{}\n".format(name,varisat_result,varisat_t_total,hibou_result,hibou_t_total))
            f.flush()


