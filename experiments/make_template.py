from __future__ import print_function
from __future__ import division
from collections import Counter
from operator import itemgetter

import argparse
import glob
import os
import sys

grep_fcnt = 0
temp_fcnt = 0
cnt = 0

def make_dir(tempdir):
  try:
    os.makedirs(tempdir)
  except OSError as e:
    pass

def _regex(lst):
  '''
  change pattern to regex
  ex) <old>47 92 47 -> 47.*92.*47
      <new>47 92 47 -> .*47.* 92.* 47\>
 '''
  #s = ".*".join(lst)
  s = ".* ".join(lst)
  s = '".*'+s+'\>"'
  return s

def filter_grep(lst, p):
  '''
  input
  lst := pattern
  p   := file path

  output:
  filtered input file name
  '''
  global grep_fcnt
  grep_fcnt += 1

  f_ = "grep"+str(grep_fcnt)+".txt"
  #create input file matching with pattern

  make_dir('./filter_grep/')
  path = os.path.join('filter_grep', f_)
  cmd_lst = ['grep', _regex(lst), p, ">", path]
  cmd = " ".join(cmd_lst)
  print("grep cmd:", cmd)
  os.system(cmd)
  return path

def avg_idx_dict(dic):
  def sum_idx(lst):
    sum_lst = [0 for each in lst[0]]
    for each in lst:
      sum_lst = [sum(x) for x in zip(sum_lst, each)]
    sum_lst = [float(x)/len(lst) for x in sum_lst]
    return sum_lst

  avg_dict = {}
  for i in dic:
    avg_dict[i] = sum_idx(dic[i])
  return avg_dict

def calculate(pattern, f_):
  chset = Counter(pattern)
  with open(f_, 'r') as f:
    data = f.readlines()

  def filter_rec():
    def find_idx(pattern, lst):
      add_idx = lambda x, y: x+y
      if len(pattern) == 0:
        return []
      else:
        try:
          a = lst.index(pattern[0])
          add_a = lambda x: add_idx(a+1,x)
          return [a]+map(add_a, find_idx(pattern[1:], lst[a+1:]))
        except ValueError:
          return [-1]

    def average(lst):
      sum_lst = [sum(i) for i in zip(*lst)]
      sum_lst = [float(i)/len(lst) for i in sum_lst]
      return sum_lst

    filter_rec_cnt = 0
    all_lst = []

    for idx, i in enumerate(data):
      s = i.split()
      idx_lst = find_idx(pattern, s)

      if -1 in idx_lst:
        filter_rec_cnt +=1
      elif len(idx_lst)!=len(pattern):
        filter_rec_cnt +=1
      else:
        all_lst.append(idx_lst)
    print ('grep:', len(data), ', filtered:', filter_rec_cnt, 'percent', round(filter_rec_cnt/len(data), 2))
    return average(all_lst)

  return filter_rec()

def make_tempfile_new(avg, pat):
  global temp_fcnt
  temp_fcnt += 1
  f_ = './templates/template' + str(temp_fcnt) + '.txt'

  lst = []
  with open(f_, 'w') as f:
    for each in zip(avg, pat):
      lst.append(each)

    for each in lst:
      float_to_int = str(int(round(each[0])))
      f.write(float_to_int+':'+each[1]+'\n')

def iterate(pattern_file, data_file, tem_num):
  def pattern_to_template(pat, data_file):
    '''
    input := list of strings
    '''
    f = filter_grep(pat, data_file)
    avg = calculate(pat, f)
    make_dir('./templates/')
    make_tempfile_new(avg, pat)

  with open(pattern_file, 'r') as f:
    lst = f.readlines()[:int(tem_num)]

  for each in lst:
    in_ = each.split()
    pattern_to_template(in_, data_file)

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('pattern')
  parser.add_argument('data')
  parser.add_argument('tem_num')
  args = parser.parse_args()
  pattern = args.pattern
  data = args.data
  tem_num = args.tem_num
  #print(pattern, data)

  iterate(pattern, data, tem_num)

if __name__ == '__main__':
  main()

