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

from sat3_commons import empty_directory
from sat3_generator import generate_custom_problems
from sat3_to_membership import make_membership_for_problems
from sat3_calls import experiment

prob_uf20_path = "./uf20/"
gen_custom_path = "./gen_custom/"
gen_u20_path = "./gen_uf20/"


def try_mkdir(dir_path):
    try:
        os.mkdir(dir_path)
    except FileExistsError:
        pass

def benchmarks_3sat():
    generate_custom_problems(gen_custom_path)
    make_membership_for_problems(gen_custom_path, gen_custom_path)
    experiment(gen_custom_path, "exp_3sat_mahe", 5)

    empty_directory(gen_u20_path)
    copy_tree(prob_uf20_path, gen_u20_path)
    make_membership_for_problems(gen_u20_path, gen_u20_path)
    experiment(gen_u20_path, "exp_3sat_uf20", 5)

if __name__ == '__main__':
    try_mkdir("./temp/")
    try_mkdir(gen_custom_path)
    try_mkdir(gen_u20_path)

    benchmarks_3sat()

