# NO INTERNAL REFERENCE
from __future__ import print_function
import subprocess
import argparse
import os
from operator import itemgetter
import datetime
import sys

def read_lst(data):
    with open(data, 'r') as f:
        ret = f.readlines()
    return ret

def preprocess(l):
    ret = []

    for each in l:
        lst = each.split()
        string = " -1 ".join(lst)
        string += " -1 -2\n"
        ret.append(string)

    return ret

class SPM_Algo:
    def __init__(self, _input, _alg, _min):
        self._executable = "spmf.jar"
        self._input = _input
        self._alg = _alg

        if self._alg == "TKS":
            self._min = str(_min)
        else:
            self._min = str(float(_min)/100)

        self._output = self._input+".output."+self._alg+"_"+self._min

    def run(self):
        # java -jar spmf.jar run VMSP contextPrefixSpan.txt output.txt 50%

        subprocess.call(["java", "-jar", self._executable, "run", self._alg, self.encode_input(self._input), self._output, self._min])

    def encode_input(self, data):
        #print(data)
        in_ = read_lst(data)
        out_ = preprocess(in_)
        out_f = data+".preprocess."+self._alg+"_"+self._min
        with open(out_f,'w') as f:
            for each in out_:
                f.write(each)

        return out_f

    def decode_output(self):
        # read
        lines = []
        try:
            with open(self._output, "rU") as f:
                lines = f.readlines()
        except:
            print("read_output error")

        # decode
        patterns = []
        for line in lines:
            line = line.strip()
            patterns.append(line.split(" -1 "))

        return patterns

    def filter_output_by_len(self,lst,l):
        ret = []
        for i in lst:
            if len(i)>=l+1:
                ret.append(i)
        return ret

    def prettify_output(self, lst):
        for i in sorted(lst, key=lambda x: int(itemgetter(-1)(x).split("#SUP:")[-1]), reverse=False)[:]:
            print(" ".join(i))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='nonono')
    parser.add_argument('path', metavar='Path', type=str)
    parser.add_argument('alg')
    parser.add_argument('min_supp', type=int)
    parser.add_argument('min_len', type=int)
    args = parser.parse_args()

    path = os.path.abspath(args.path)
    alg = args.alg
    minimum = args.min_supp
    pattern_len = args.min_len

    start_time = datetime.datetime.now()

    vmsp = SPM_Algo(path, alg, minimum)
    vmsp.run()

    current_time = datetime.datetime.now()
    elapsed_time = str((current_time - start_time).total_seconds())
    print("pattern mining computation time", elapsed_time)

    decode_output =  vmsp.decode_output()
    #print(decode_output)
    post_output = vmsp.filter_output_by_len(decode_output, pattern_len)
    vmsp.prettify_output(post_output)

