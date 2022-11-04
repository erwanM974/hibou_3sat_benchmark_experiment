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

import os
from distutils.dir_util import copy_tree

from implem.commons import empty_directory
from implem.sat3_generator import generate_custom_problems
from implem.sat3_to_membership import make_membership_for_problems
from implem.calls import experiment

prob_uf20_path = "./uf20/"
gen_u20_path = "./gen_uf20/"


def try_mkdir(dir_path):
    try:
        os.mkdir(dir_path)
    except FileExistsError:
        pass

def generate_translate_verify(custom_name,max_iteration_genrate,num_tries_generate,variables,clauses,num_tries_analyze):
    gen_custom_path = "./gen_{}/".format(custom_name)
    try_mkdir(gen_custom_path)
    generate_custom_problems(custom_name,max_iteration_genrate,num_tries_generate,variables,clauses)
    make_membership_for_problems(gen_custom_path, gen_custom_path)
    experiment(gen_custom_path, "exp_3sat_{}".format(custom_name), num_tries_analyze)

def translate_verify_uf20(num_tries_analyze):
    try_mkdir(gen_u20_path)
    empty_directory(gen_u20_path)
    copy_tree(prob_uf20_path, gen_u20_path)
    make_membership_for_problems(gen_u20_path, gen_u20_path)
    experiment(gen_u20_path, "exp_3sat_uf20", num_tries_analyze)


def benchmarks_3sat():
    num_tries = 5
    generate_translate_verify("custom_small",300,4,[3,10],[4,50],num_tries)
    generate_translate_verify("custom_big",300,4,[20,27],[40,100],num_tries)
    translate_verify_uf20(num_tries)


if __name__ == '__main__':
    try_mkdir("./temp/")
    #benchmarks_3sat()
    experiment(gen_u20_path, "exp_3sat_uf20", 5)
