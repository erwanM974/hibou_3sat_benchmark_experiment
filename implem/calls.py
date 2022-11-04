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

from implem.poll import poll_alternatives


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
                return (False, [], tries, t_total)
        elif "s SATISFIABLE" in line:
            is_sat = True
        elif line.startswith("v"):
            if not is_sat:
                raise Exception("cannot have solution if UNSAT")
            solution = [int(sol) for sol in line[2:].split(" ")[:-1]]
            return (True, solution, tries, t_total)

def parse_hibou_output(outwrap):
    #
    verdict = None
    length = None
    node_count = None
    elapsed_time = None
    result = None
    #
    for line in outwrap:
        if "verdict" in line:
            if "WeakPass" in line:
                verdict = "WeakPass"
                result = True
            elif "Pass" in line:
                verdict = "Pass"
                result = True
            elif "WeakFail" in line:
                verdict = "WeakFail"
                result = False
            elif "Fail" in line:
                verdict = "Fail"
                result = False
            elif "Inconc" in line:
                verdict = "Inconc"
            else:
                print(line)
                raise Exception("some other verdict ?")
        # ***
        if "of length" in line:
            length = int(line.split(" ")[-1].strip()[1:-1])
        # ***
        if "node count" in line:
            node_count = int(line.split(" ")[-1].strip())
        # ***
        if "elapsed" in line:
            elapsed_time = float(line.split(" ")[-1].strip())
        # ***
    #
    mydict = {
        'node_count': node_count,
        'length': length,
        'verdict': verdict,
        'elapsed_time': elapsed_time
    }
    return (result,mydict)

def is_sat_via_membership(parent_path,name,num_tries):
    hsf_file = "{}{}.hsf".format(parent_path, name)
    hif_file = "{}{}.hif".format(parent_path, name)
    htf_file = "{}{}.htf".format(parent_path, name)
    #
    hcf_file_wtloc = "conf_wtloc.hcf"
    hcf_file_noloc = "conf_noloc.hcf"
    #
    commands = [ ["./hibou_label.exe", "analyze", hsf_file, hif_file, htf_file, hcf_file_wtloc],
                 ["./hibou_label.exe", "analyze", hsf_file, hif_file, htf_file, hcf_file_noloc] ]
    #
    hibou_result = None
    final_dict = {}
    final_dict['tries_time'] = []
    final_dict['tries_quickest'] = []
    for i in range(0,num_tries):
        (outwrap,id_of_quickest) = poll_alternatives(commands,0.1,False)
        (hibou_result,try_dict) = parse_hibou_output(outwrap)
        #
        keys = ['node_count','length','verdict']
        for key in keys:
            if key in final_dict:
                assert( final_dict[key] == try_dict[key] )
            else:
                final_dict[key] = try_dict[key]
        #
        final_dict['tries_time'].append(try_dict['elapsed_time'])
        if id_of_quickest == 0:
            final_dict['tries_quickest'].append('WT_LOC')
        elif id_of_quickest == 1:
            final_dict['tries_quickest'].append('NO_LOC')
        else:
            raise Exception
        #
    t_total = statistics.median(final_dict['tries_time'])
    final_dict['median_time'] = t_total
    #
    return (hibou_result,final_dict)

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
    columns = ["name",
               "varisat_result",
               "varisat_time_tries",
               "varisat_time_median",
               "hibou_verdict",
               "hibou_nodes",
               "trace_length",
               "hibou_time_tries",
               "hibou_tries_quickest",
               "hibou_time_median"]
    f.write(";".join(columns) + "\n")
    f.flush()
    #
    for filename in os.listdir(saved_path):
        if filename.endswith(".cnf"):
            name = filename[:-4]
            (varisat_result,varisat_solution,varisat_t_tries,varisat_t_median) = is_sat_varisat(saved_path,name,num_tries)
            (hibou_result,mydict) = is_sat_via_membership(saved_path,name,num_tries)
            if varisat_result != hibou_result:
                raise Exception("not same result for satisfiability for name:{} :: varisat:{} - hibou:{}".format(name,varisat_result,hibou_result))
            f.write("{};{};{};{};{};{};{};{};{};{}\n".format(name,
                                                    varisat_result,
                                                             varisat_t_tries,
                                                    varisat_t_median,
                                                    mydict['verdict'],
                                                    mydict['node_count'],
                                                    mydict['length'],
                                                    mydict['tries_time'],
                                                    mydict['tries_quickest'],
                                                    mydict['median_time']))
            f.flush()

