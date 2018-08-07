import os, sys, glob, argparse


def print_branches(stgy):
    
    conventional_set = stgy+"_set"
    template_set = "T-"+stgy+"_set"
    [conventional_set, template_set] = [set([]), set([])]

    files = glob.glob("*" + "_T-"+stgy+"_" + "*")
    b_set = []
    n =0 
    for f in files:
        with open(f) as fp:
	    lines = fp.readlines()
	    if len(lines)==5:
	        line = lines[-2]
		b_set = line.split(':')
		n = n+1	
		template_set = template_set.union(set(b_set[1].split()))
    print "T-"+stgy+": "  +str(len(template_set)) + " (" + str(n) + ")"

    files = glob.glob("*" + "_"+stgy+"_" + "*")
    b_set = []
    m =0 
    for f in files:
        with open(f) as fp:
	    lines = fp.readlines()
	    if len(lines)==5:
	        line = lines[-2]
		b_set = line.split(':')
		m = m+1	
		conventional_set = conventional_set.union(set(b_set[1].split()))
    print stgy+": "  +str(len(conventional_set)) + " (" + str(m) + ")"

    print "Total Branch Coverage: " + str(len(template_set | conventional_set)) + " (" + str(n+m) + ")"


def main():
    global time_budget
    parser = argparse.ArgumentParser()

    parser.add_argument("stgy")

    args = parser.parse_args()
    stgy = args.stgy

    print_branches(stgy)

if __name__ == '__main__':
    main()

