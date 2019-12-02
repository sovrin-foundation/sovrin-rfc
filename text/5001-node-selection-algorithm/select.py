'''
Implementation of Steward Selection Algorithm.

Assumes CSV data in the format shown in sample-data.csv. This data was produced by exporting
the worksheet at http://bit.ly/2GoYXTG; any worksheet with the same general layout but with
different rows for stewards, and different numbers for N and M, should also be supported.
'''

import csv, os, sys, re, unittest, datetime
from itertools import combinations, islice, chain
#from concurrent.futures import ProcessPoolExecutor
#import numpy as np
import collections
from multiprocessing import Pool

max_f_for_steward_list = -1
f_from_data_file = 0
config_best = 10

def load_clean_csv(fname):
    # Read file and parse into rows and cells.
    with open(fname, "r") as f:
        rows = [r for r in csv.reader(f)]
    # Trim whitespace everywhere.
    for i in range(len(rows)):
        row = rows[i]
        for j in range(len(row)):
            row[j] = row[j].strip()
    if not [x for x in rows if not is_empty_row(x)]:
        raise Exception('No useful data.')
    return rows


# Define and compile some regexes that we're going to use to match cells.
f_pat = re.compile(r'.*(max ((number|#) (of )?)?faulted nodes(:|--) ?)?F$', re.I)
lik_pat = re.compile(r'.*likelihood( per y(ea)?r( \(from MT[BT]F\)?))?$', re.I)
fault_pat = re.compile(r'\s*fault\s*\?\s*$', re.I)

def parse_headers(rows, skip_f=False):
    # Define some rules to parse rows. The rules are tuples where the first item is the
    # name to assign to a variable if the rule matches, the second item is a function
    # for testing the row against the rule, and the third item is a function to extract
    # a value from the row.
    rules = [
        ('f', lambda row: f_pat.match(row[0]), lambda row: int(row[1])),
        ('scenarios', lambda row: bool((not row[0]) and (not row[1]) and row[2] and row[3] and row[4]), lambda row: row[2:]),
        ('liks', lambda row: lik_pat.match(row[0]), lambda row: [convert_float(cell) for cell in row[2:]]),
        ('_', lambda row: fault_pat.match(row[-1]), lambda row: None)
    ]
    # Parse headers.
    vars = {}
    row_idx = 0
    rule_idx = 0
    if skip_f:
        rule_idx = 1
        vars['f'] = 0
    while rule_idx < len(rules):
        rule = rules[rule_idx]
        row = rows[row_idx]
        row_idx += 1
        print('Testing rule %d against row %d (%s)' % (rule_idx, row_idx, ','.join(row)))
        if apply_rule(row, vars, rule[0], rule[1], rule[2]):
            rule_idx += 1
            continue
        if row_idx == len(rows):
            break
    # Make sure we found everything we expected.
    if row_idx == len(rows):
        if skip_f:
            not_found = [x for x in [r[0] for r in rules[1:-2]] if x not in locals()]
            raise Exception("Didn't find the following variable(s) in data: %s" % ', '.join(not_found))
        else:
            # Try reparsing the data without looking for the top portion where f is defined.
            return parse_headers(rows, True)
    return vars['f'], vars['scenarios'], vars['liks'], row_idx

def parse_stewards(rows, row_idx):
    # Now consume rows with steward names and their fault profiles
    stewards = []
    mttrs = []
    faults = []
    while row_idx < len(rows):
        row = rows[row_idx]
        print(row)
        if is_steward_row(row):
            stewards.append(row[0])
            mttrs.append(float(row[1]))
            faults.append([int(cell) for cell in row[2:]])
            row_idx += 1
        else:
            break
    return stewards, mttrs, faults

def is_steward_row(row):
    if has_string(row[0]) and has_num(row[1]):
        for x in row[2:]:
            x = str(x).strip()
            if x != '0' and x != '1':
                return False
        return True

def apply_rule(row, vars, var_name, test_func, assign_func):
    if test_func(row):
        vars[var_name] = assign_func(row)
        return True

def is_empty_row(r):
    if r:
        for cell in r:
            if cell and str(cell).strip():
                return False
    return True

def convert_float(txt):
    if type(txt) is str or type(txt) is unicode:
        txt = txt.strip()
        if txt.endswith('%'):
            return float(txt[:-1]) * 0.01
    return float(txt)

def has_string(cell):
    if type(cell) is str:
        cell = cell.strip()
    return cell and cell[0].isalpha()

def has_num(cell):
    if type(cell) is str:
        cell = cell.strip()
    if cell:
        try:
            convert_float(cell)
            return True
        except:
            pass
    return False

def max_f_for_steward_count(n):
    return max(int((n - 1) / 3), 0)

def load_data(fname, requested_f=max_f_for_steward_list):
    print("In 'Load Data'")
    rows = load_clean_csv(fname)
    print(rows)
    file_f, scenarios, liks, row_idx = parse_headers(rows)
    print(file_f, scenarios, liks, row_idx)
    stewards, mttrs, faults = parse_stewards(rows, row_idx)
    print(stewards, mttrs, faults)
    # Check validity of the f value we've been given.
    max_f = max_f_for_steward_count(len(stewards))
    if max_f > 8:
        max_f=8
    if file_f > 0 and (requested_f == f_from_data_file):
        requested_f = file_f
    elif requested_f == max_f_for_steward_list:
        requested_f = max_f
    if requested_f > max_f:
        raise Exception("%d stewards allow f=%d; can't satisfy requested f=%d." % (len(stewards), max_f, requested_f))
    return requested_f, scenarios, liks, stewards, mttrs, faults

def factorial(n):
    if n < 2:
        return 1
    return n * factorial(n - 1)

default_best_N = 10
worst_best_score = -10000000
invalid_worst_idx = -1

class BestN:
    '''
    Keep track of the best N combinations. We could do this with a simple sorted list,
    but when we have to insert tens of millions of time, there's really no point in
    keeping the list sorted constantly. It's far faster to just keep track of the
    worst item and keep replacing it with something better -- then sort once at the
    end.
    '''
    def __init__(self, max=default_best_N):
        '''
        Define a quantifier func that will be used to get numeric values for
        items in the list. By default, the quantifier should return numbers that
        are bigger if better; to sort ascending, make the quantifier return
        such a sequence times -1. Set max size of list.'''
        #assert quantifier
        assert type(max) is type(3)
        assert max > 0
        assert max <= 10000
        self._items = []
        #self.quantifier = lambda x: x.combined_score, config_best
        self._sorted = False
        self.max = max
        self.worst_idx = invalid_worst_idx
        self.worst_score = worst_best_score

    def _quantifier(self, x):
        return x.combined_score, config_best
    def _find_worst(self):
        self.worst_idx = invalid_worst_idx
        self.worst_score = worst_best_score
        for i in range(len(self._items)):
            n = self._quantifier(self._items[i])
            if (self.worst_idx == invalid_worst_idx) or (n < self.worst_score):
                self.worst_idx = i
                self.worst_score = n
    def __getattr__(self, item):
        if item == 'items':
            if not self._sorted:
                self._items.sort(reverse=True)
                self._find_worst()
                self._sorted = True
            return self._items
        raise AttributeError(item)
    def keep_if_better(self, candidate):
        if len(self._items) < self.max:
            self._items.append(candidate)
            self._sorted = False
        else:
            if self.worst_idx == invalid_worst_idx:
                self._find_worst()
            score = self._quantifier(candidate)
            if score > self.worst_score:
                self._items[self.worst_idx] = candidate
                self.worst_idx = invalid_worst_idx # Need to recalculate
                self._sorted = False
    def get_items(self):
        return self._items


class ComboAnalysis:
    '''Encapsulate info about a single combination of stewards.'''
    def __init__(self, faults, combo, stewards, mttrs):
        self.combo = sorted(combo)
        self.steward_indexes = {} # row index
        self.combo_faults = [0,0,0,0,0,0,0,0,0,0,0,0] 
        for i in combo: # needs to be optamized, maybe use panda....
            stewards_index = stewards.index(i) # row
            indexes = mttrs[stewards_index]
            self.steward_indexes[stewards_index] = indexes
            fault = faults[stewards_index]
            self.combo_faults = [x+y for x, y in zip(self.combo_faults, fault)]
        #print(self.combo_faults)
        self.results = []
        self._total = None
    def __getattr__(self, item):
        if item == 'combined_score':
            if not self._total:
                self._total = sum([r.score for r in self.results])
            return self._total
        raise AttributeError(item)
    def __lt__(self, other):
        return self.combined_score < other.combined_score
    def __str__(self):
        return '%s: %s' % ('+'.join(self.combo), self.combined_score)

class ScenarioResult:
    '''Encapsulate info about one combination of stewards in one scenario.'''
    def __init__(self, index, liks, combo_indexes, combo_summed_faults, f, mttrs):
        #self.name = scenario
        #self.idx = scenarios.index(scenario)
        self.likelihood = liks[index]
        self.combo_indexes = combo_indexes
        self.f = f
        #self.fault_count = 0
        #relevant_mttrs = []
        #profile = []
        """ for ci in combo_indexes.keys():
            #relevant_mttrs.append(mttrs[ci])
            n = faults[ci][index]
            #profile.append(n)
            if n:
                self.fault_count += 1 """
        #self.profile = profile
        combo_values = combo_indexes.values()
        relevant_mttrs = list( combo_values )
        self.failure_distance = self.f - combo_summed_faults
        if self.failure_distance < 0:
            relevant_mttrs.sort()
            # The MTTR of the scenario is the time it will take for the i-th node to
            # repair its fault, where i is the number of the node that finally
            # gets the whole network back into consensus.
            index = self.failure_distance + 1
            index = -index
            self.mttr = relevant_mttrs[index]
            self.importance = self.likelihood * self.mttr
        else:
            # We don't have any repair time if we never lost consensus.
            self.mttr = 0
            # The importance of an uptime is its likelihood * the average downtime of all
            # the nodes in the scenario. This is just a rough approximation.
            self.importance = self.likelihood * sum(relevant_mttrs) / len(relevant_mttrs)
        # The score of a scenario is its importance * its failure_distance
        self.score = (self.importance * self.failure_distance)
    def __lt__(self, other):
        return self.score < other.score


def analyze_combo(combo, scenarios, liks, stewards, mttrs, faults, f):
    '''
    Given a single combination, evaluate its downtime across all scenarios. If it has less
    downtime than one of the current "top N" combinations, put this one into the "top N"
    list.
    '''
    ca = ComboAnalysis(faults, combo, stewards, mttrs)
    for index in range(len(scenarios)):
        #print(ca.combo_summed_faults)
        summed_faults = ca.combo_faults[index]
        sr = ScenarioResult(index, liks, ca.steward_indexes, summed_faults, f, mttrs)
        ca.results.append(sr)
    return ca

def report(best, f):
    m = (3 * f) + 1
    title = '%d Best %d-Steward Combinations, Ranked' % (len(best.items), m)
    print('\n' + title)
    print('-' * len(title))
    for i in range(len(best.items)):
        combo = best.items[i]
        print('%d: %s' % (i + 1, combo))

def batch(iterable, n=1): # https://stackoverflow.com/questions/8290397/how-to-split-an-iterable-in-constant-size-chunks
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

""" def grouper(n, iterable):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args) """

def grouper_it(n, iterable): # https://pastebin.com/YkKFvm8b
    it = iter(iterable)
    while True:
        chunk_it = islice(it, n)
        try:
            first_el = next(chunk_it)
        except StopIteration:
            return
        yield chain((first_el,), chunk_it)

if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == 'test':
        del sys.argv[1]  # remove --test from args, so unittest won't complain about unknown switch
        unittest.main()
    else:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('fname', help='CSV data file in format matching http://bit.ly/2GoYXTG. Lines before scenarios are optional.')
        parser.add_argument('--f', '-f', help='Number of faulted nodes to allow before consensus is lost. -1=max allowed by steward list (default); 0=as in data file', type=int, default=max_f_for_steward_list)
        parser.add_argument('--best', help='Specify how many of the best steward combinations to show.', type=int, default=10)
        args = parser.parse_args()

        f, scenarios, liks, stewards, mttrs, faults = load_data(args.fname,  args.f)
        # analyze
        m = (3 * f) + 1
        print ("m= %s",m)
        n = len(stewards)
        print ("n= %s",n)
        total_combinations = factorial(n) / (factorial(m) * factorial(n - m))
        print('Analyzing %d total %d-steward combinations (n=%d, f=%d).' % (total_combinations, m, n, f))

        def calculate_combination(combo):
            return analyze_combo(combo, scenarios, liks, stewards, mttrs, faults, f)

        with Pool() as pool:
            best = BestN()
            combos = grouper_it(800, combinations(stewards, m))
            for cs in combos:
                combos_with_score = pool.map_async( calculate_combination, cs)
                [best.keep_if_better(combo) for combo in combos_with_score.get() ]
            report(best, f)            
