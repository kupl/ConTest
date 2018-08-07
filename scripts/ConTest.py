import os
import re
import sys
import operator
import time, datetime, argparse, glob
import json

start_time = datetime.datetime.now()
date = start_time.strftime('%m%d')
num_parallel = 10
time_budget = 0

configs = {
        'date': '0704',
        'script_path': os.path.abspath(os.getcwd()),
        'ex_dir': os.path.abspath('../experiments/'),
        'bench_dir': os.path.abspath('../benchmarks/'),
        'badinput_dir' : os.path.abspath('../../bad-input/')
}

def load_pgm_config(config_file):
    with open(config_file, 'r') as f:
        parsed = json.load(f)
    return parsed
    
def time_check():
    global time_budget
    now_time = datetime.datetime.now()
    total_time = (now_time-start_time).total_seconds()
    if time_budget < total_time:
        print "#############################################"
	print "################Time Out!!!!!################"
	print "#############################################"
        f = open("exit_time", 'w')
        f.write("exit_time: "+str(total_time))
        f.close()
        "time limit exceeded at ", total_time
        sys.exit()

def pure_concolic(load_config, pgm_config, stgy, trial):
    
    benchmark_dir = configs['bench_dir']+"/"+load_config['pgm_dir']+load_config['exec_dir']
    os.chdir(benchmark_dir)
    rm_cmd = " ".join(["rm -rf", "template*"])
    os.system(rm_cmd)
    time_check() 
    
    # run convetional concolic testing
    os.chdir(configs['script_path'])
    #####################################################################################################################
    run_concolic = " ".join(["python", "conventional_concolic.py", pgm_config, "100", str(num_parallel), stgy, trial])
    #####################################################################################################################
    os.system(run_concolic)
        
    # cp the branch_coverage_log of conventional concolic testing
    os.chdir(configs['ex_dir'])
    dir_name = "AllLogs__"+configs['date']+"__"+load_config['pgm_name']+"__"+stgy
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    cp_cmd = " ".join(["cp", configs['date']+"__"+stgy+trial+"/"+load_config['pgm_name']+"/logs/*.log", dir_name+"/"])
    os.system(cp_cmd)
        
    # collect test-cases which new branches are covered
    file_name = stgy+trial+"_test_cases"
    cat_cmd = " ".join(["cat", configs['date']+"__"+stgy+trial+"/"+load_config['pgm_name']+"/*/"+load_config['exec_dir']+"/Good.txt >", file_name])
    print cat_cmd
    os.system(cat_cmd)
        
    # post-processing
    sed_cmd = " ".join(["sed", "-i", "'/^$/d'", file_name])
    sed_cmd2 = " ".join(["sed", "-i", "'/^0/d'", file_name])
    print sed_cmd
    os.system(sed_cmd)
    os.system(sed_cmd2)

    f = open(file_name, 'r')
    lines = f.readlines()
    test_cases = "sorted"+file_name
    f2 = open(test_cases, 'a')
    
    split_seq = []
    for line in lines:
        line_list = line.split()
        if '0' in line_list:
            index = line_list.index('0')+1
            line = ' '.join(line_list[0:index])
            line = line + "\n"
            size = index
        else:
            size = len(line.split())
        if size >= 3:
            split_seq.append((size,line))

    split_seq = sorted(split_seq, key=lambda tup: tup[0])
    for element in split_seq:
        f2.write(element[1])

    f.close()
    f2.close()

    return test_cases

def sequential_pattern_mining(load_config, test_cases, stgy, trial):
    os.chdir(configs['ex_dir'])
    ip_file = "initpattern_"+stgy+trial
    pattern_file = "pattern_"+stgy+trial
        
    # run pattern mining algorithm(CloFast)
    #####################################################################################################################
    run_cmd = " ".join(["python", "vmsp.py", test_cases, "CloFast", "1", "3", ">", ip_file])
    #####################################################################################################################
    print run_cmd
    os.system(run_cmd)         
    time.sleep(2)
        
    init_f = open(ip_file, 'r')
    final_f = open(pattern_file, 'a')
    lines = init_f.readlines()[:50000]
    for line in lines:
        if "#SUP:" in line:
            pattern = line.split(" -2 #SUP: ")[0]
            final_f.write(pattern + "\n")
    init_f.close()
    final_f.close()

    # cp pattern_file
    dir_name = "AllLogs__"+configs['date']+"__"+load_config['pgm_name']+"__"+stgy
    cp_cmd = " ".join(["cp", pattern_file, dir_name+"/"])
    os.system(cp_cmd)

    return pattern_file


def pattern_templates(load_config, stgy, trial, test_cases, pattern_file, tem_num):
    os.chdir(configs['ex_dir'])
    dir_name = "AllLogs__"+configs['date']+"__"+load_config['pgm_name']+"__"+stgy+"/"
        
    # move temp_log
    mv_cmd = " ".join(["mv", "*"+test_cases+"*", "*pattern*", stgy+trial+"_test*", dir_name])
    os.system(mv_cmd)

    # transform pattern into template
    #####################################################################################################################
    pt_cmd = " ".join(["python", "make_template.py", dir_name+pattern_file, dir_name+test_cases, tem_num])
    #####################################################################################################################
    print pt_cmd
    os.system(pt_cmd)
        
    template_folder = "templates"+stgy+trial
    mv_cmd = " ".join(["mv", "templates", template_folder])
    os.system(mv_cmd)
    cp_cmd = " ".join(["cp -r", template_folder, configs['bench_dir']+"/"+load_config['pgm_name']+"/"+load_config['exec_dir']])
    os.system(cp_cmd)
    time.sleep(2)
        
    # move pattern_file
    mv2_cmd = " ".join(["mv", template_folder, dir_name+"/"])
    os.system(mv2_cmd)

    return template_folder

def template_concolic(template_folder, tem_num, load_config, pgm_config, stgy, trial):
    # run Template-Guided Concolic Testing.
    for i in range(1, int(tem_num)+1):
        os.chdir(configs['bench_dir']+"/"+load_config['pgm_name']+"/"+load_config['exec_dir'])

        time_check()
        cp_cmd = " ".join(["cp", "templates"+stgy+trial+"/template"+str(i)+".txt", "template.txt"])
        print cp_cmd
        os.system(cp_cmd)

        os.chdir(configs['script_path'])
        run_cmd = " ".join(["python", "template_concolic.py", pgm_config, "20", str(num_parallel), str(i+int(trial)*1000), "T-"+stgy])
        print run_cmd
        os.system(run_cmd)

    # cp template_concolic logs
    os.chdir(configs['ex_dir'])
    dir_name = "AllLogs__"+configs['date']+"__"+load_config['pgm_name']+"__"+stgy
    cp_cmd = " ".join(["cp", configs['date']+"__"+"T-"+stgy+trial+"*/"+load_config['pgm_name']+"/logs/*.log", dir_name+"/"])
    cp2_cmd = " ".join(["cp -r", configs['date']+"__"+"T-"+stgy+trial+"001/"+load_config['pgm_name']+"/1/"+load_config['exec_dir']+"/"+template_folder, dir_name+"/"])
    print cp_cmd
    os.system(cp_cmd)
    os.system(cp2_cmd)

    # remove T-Folder
    rm_cmd = " ".join(["rm -r", configs['date']+"__"+"T-"+stgy+"*/"])
    os.system(rm_cmd)

def patterns_evaluation(load_config, stgy, trial, tem_num, pattern_file):
    # union the branch coverage for pure_concolic testing
    dir_name = "AllLogs__"+configs['date']+"__"+load_config['pgm_name']+"__"+stgy
    os.chdir(configs['ex_dir']+"/"+dir_name)
    pure_set = set([])
    b_set = []
    files = glob.glob("*" + "__"+stgy+"__" + "*")
    n =0
    for f in files:
        with open(f) as fp:
            lines = fp.readlines()
            if len(lines)==5:
                line = lines[-2]
                b_set = line.split(':')
                n = n+1
                pure_set = pure_set.union(set(b_set[1].split()))
    print "Conventional Concolic Testing: "+str(len(pure_set))

    # union the branch coverage for template-guided concolic testing
    good_set = []
    bad_set = []
    for j in range(1, 1+int(trial)):
        bad_temp_list = []
        good_temp_list = []
        for i in range(1, int(tem_num)+1):
            files = glob.glob(load_config['pgm_name'] + str(i+int(j)*1000) + "__T-"+stgy+"*")
            n =0
            cov_set = set([])
            for f in files:
                with open(f) as fp:
                    lines = fp.readlines()
                    if len(lines)==5:
                        line = lines[-2]
                        b_set = line.split(':')
                        n = n+1
                        cov_set = cov_set.union(set(b_set[1].split()))
            if len(cov_set - pure_set) <= 1: # Thresholds
                bad_temp_list.append(i)
            if len(cov_set - pure_set) >= 20:
                good_temp_list.append(i)
                
        if j ==1:
            pf = open("diversified_"+pattern_file+str(j), 'r')
        else:
            pf = open("ranked_"+pattern_file+str(j), 'r')
        lines = pf.readlines()  
        n = 1
        for l in lines:
            if n in bad_temp_list:
                bad_set.append(l)
            if n in good_temp_list:
                good_set.append(l)
            n = n+1
        pf.close()
        
    gf = open("good_file"+str(j), 'w')
    for e in good_set:
        gf.write(e)
    gf.close()                      
        
    bf = open("bad_file"+str(j), 'w')
    for e in bad_set:
        bf.write(e)
    bf.close()

    return bad_set, good_set

def pattern_ranking(bad_set, good_set, pattern_file):

    # Transform each pattern into ngram features
    good_ngram_set = set()
    for g in good_set:
        pat_list = g.split()
        pat_len = float(len(pat_list))
        n_size = int(round(pat_len/2))
        list_list = [pat_list[i:i+n_size] for i in xrange(len(pat_list)-n_size+1)]
        for e in list_list:
            gram = " ".join(e)
            good_ngram_set.add(gram)

    bad_ngram_set = set()
    for b in bad_set:
        pat_list = b.split()
        pat_len = float(len(pat_list))
        n_size = int(round(pat_len/2))
        list_list = [pat_list[i:i+n_size] for i in xrange(len(pat_list)-n_size+1)]
        for e in list_list:
            gram = " ".join(e)
            bad_ngram_set.add(gram)
        
    cand_pat = open(pattern_file, 'r')
    cand_lines = cand_pat.readlines()
        
    # Step1: Reflection
    pat_top = []
    pat_mid = []
    for c in cand_lines:
        good_bool = False
        bad_bool = False
        l_list = c.split()
        l_size = float(len(l_list))
        num = int(round(l_size/2))
        list_list = [l_list[i:i+num] for i in xrange(len(l_list)-num+1)]
        for l2 in list_list:
            gram = " ".join(l2)
            if gram in good_ngram_set:
                good_bool = True
            if gram in bad_ngram_set:
                bad_bool = True
                                        
        if good_bool and not(bad_bool):
            pat_top.append(c)       
        if not(good_bool) and not(bad_bool):
            pat_mid.append(c)       
        
    reflected_pat = pat_top + pat_mid               
    cand_pat.close()        
    ranked_file = "ranked_"+pattern_file    
    ranked_pat = open(ranked_file, 'w')
        
    # Step2: Diversification
    check_set = set()
    for l in reflected_pat:
        ngram_set = set()
        l_list = l.split()
        l_size = float(len(l_list))
        num = int(round(l_size/2))
        list_list = [l_list[i:i+num] for i in xrange(len(l_list)-num+1)]
        
        for l2 in list_list: #ngram(c)
            gram = " ".join(l2)
            ngram_set.add(gram)
        
        if not ngram_set.issubset(check_set): #ngram(c) is not subset of checkset
            check_set = ngram_set | check_set
            ranked_pat.write(l)
    ranked_pat.close()
        
    return ranked_file

def diverse_pattern(load_config, stgy, pattern_file):
    dir_name = "AllLogs__"+configs['date']+"__"+load_config['pgm_name']+"__"+stgy
    os.chdir(configs['ex_dir']+"/"+dir_name)
        
    diverse_file = "diversified_"+pattern_file
    diverse_pat = open(diverse_file, 'a')
        
    pf = open(pattern_file, 'r')
    pf_list = pf.readlines()
        
    # Diversification
    check_set = set()
    for l in pf_list:
        ngram_set = set()
        l_list = l.split()
        l_size = float(len(l_list))
        num = int(round(l_size/2))
        list_list = [l_list[i:i+num] for i in xrange(len(l_list)-num+1)]
        
        for l2 in list_list: #ngram(c)
            gram = " ".join(l2)
            ngram_set.add(gram)
        
        if not ngram_set.issubset(check_set): #ngram(c) is not subset of checkset
            check_set = ngram_set | check_set
            diverse_pat.write(l)

    pf.close()
    diverse_pat.close()

    return diverse_file


def remove_emptydir(load_config, stgy, tem_num):
    os.chdir(configs['badinput_dir'])
    real_name = load_config['pgm_name'].split("-")[0]
    for j in range(1, 15):
        for i in range(1, int(tem_num)+1):
            baddir = configs['date']+"_"+real_name+"T-"+stgy+str(i+int(j)*1000)+"/"
            if os.path.exists(baddir) and os.listdir(baddir) == []:
                rm_cmd = " ".join(["rm -r", baddir])
                os.system(rm_cmd)

    
def main():
    global time_budget
    parser = argparse.ArgumentParser()

    parser.add_argument("pgm_config")
    parser.add_argument("stgy")
    parser.add_argument("time_limit")

    args = parser.parse_args()
    pgm_config = args.pgm_config
    load_config = load_pgm_config(args.pgm_config)
    stgy = args.stgy
    time_budget = int(args.time_limit)
        
    tem_num = "20" # Hyper-Parameter (H2)

    for i in range(1,100):
        # Step 1: Conventional Concolic Testing.
        test_cases = pure_concolic(load_config, pgm_config, stgy, str(i))
        print test_cases
                
        # Step 2: Sequential Pattern Mining.
        pattern = sequential_pattern_mining(load_config, test_cases, stgy, str(i))
        print pattern
                
        # Step 3: Pattern Ranking
        if i != 1:
            bad_set, good_set = patterns_evaluation(load_config, stgy, str(i-1), tem_num, "pattern_"+stgy)
            l_pattern = pattern_ranking(bad_set, good_set, pattern)
            time.sleep(2)
        else:
            l_pattern = diverse_pattern(load_config, stgy, pattern)

        # Step 4: Patten to Template
        template_folder =  pattern_templates(load_config, stgy, str(i), test_cases, l_pattern, tem_num)
        print template_folder
                
        # Step 5: Template-Guided Concolic Testing
        template_concolic(template_folder, tem_num, load_config, pgm_config, stgy, str(i))

    remove_emptydir(load_config, stgy, tem_num)

    dir_name = "AllLogs__"+configs['date']+"__"+load_config['pgm_name']+"__"+stgy
    os.chdir(configs['ex_dir']+"/"+dir_name)
    end_time =  datetime.datetime.now()
    exec_time = 'Duration: {}'.format(end_time-start_time)
    with open('execution time','w') as f:
        f.write('Duration: {}'.format(end_time-start_time))

if __name__ == '__main__':
    main()
