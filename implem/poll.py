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
import time
import sys

def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

def poll_alternatives(commands,refresh_rate,display):
    procs = []
    # spawn some processes
    for proc_id,command in enumerate(commands):
        #print("launching as id {} command {}".format(proc_id,command))
        proc = subprocess.Popen(command, stdout=subprocess.PIPE)
        procs.append( proc )

    # loop that polls until completion
    spinner = spinning_cursor()
    id_of_quickest = None
    outwrap = None
    polling = True
    while polling:
        #
        for proc_id,proc in enumerate(procs):
            if proc.poll() != None:
                #print("proc {} finished".format( proc_id ))
                id_of_quickest = proc_id
                outwrap = io.TextIOWrapper(proc.stdout, encoding="utf-8")
                polling = False
                break
        #
        if display:
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            time.sleep( refresh_rate )
            sys.stdout.write('\b')
        else:
            time.sleep( refresh_rate )
    #
    for proc_id,proc in enumerate(procs):
        #print("proc {} to be killed".format(proc_id))
        proc.kill()
    #
    return (outwrap,id_of_quickest)


