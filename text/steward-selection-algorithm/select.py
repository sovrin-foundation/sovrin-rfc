'''
Implementation of Steward Selection Algorithm.

Assumes CSV data in the format shown in sample-data.csv. This data was produced by exporting
the worksheet at http://bit.ly/2GoYXTG; any worksheet with the same general layout but with
different rows for stewards, and different numbers for N and M, should also be supported.
'''

import csv, os, sys, re, unittest

max_f_for_steward_list = -1
f_from_data_file = 0


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
        #print('Testing rule %d against row %d (%s)' % (rule_idx, row_idx, ','.join(row)))
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
    rows = load_clean_csv(fname)
    file_f, scenarios, liks, row_idx = parse_headers(rows)
    stewards, mttrs, faults = parse_stewards(rows, row_idx)
    # Check validity of the f value we've been given.
    max_f = max_f_for_steward_count(len(stewards))
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
    def __init__(self, quantifier, max=default_best_N):
        '''
        Define a quantifier func that will be used to get numeric values for
        items in the list. By default, the quantifier should return numbers that
        are bigger if better; to sort ascending, make the quantifier return
        such a sequence times -1. Set max size of list.'''
        assert quantifier
        assert type(max) is type(3)
        assert max > 0
        assert max <= 10000
        self._items = []
        self.quantifier = quantifier
        self._sorted = False
        self.max = max
        self.worst_idx = invalid_worst_idx
        self.worst_score = worst_best_score
    def _find_worst(self):
        self.worst_idx = invalid_worst_idx
        self.worst_score = worst_best_score
        for i in range(len(self._items)):
            n = self.quantifier(self._items[i])
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
            score = self.quantifier(candidate)
            if score > self.worst_score:
                self._items[self.worst_idx] = candidate
                self.worst_idx = invalid_worst_idx # Need to recalculate
                self._sorted = False

class ComboAnalysis:
    '''Encapsulate info about a single combination of stewards.'''
    def __init__(self, combo, stewards):
        self.combo = combo
        self.steward_indexes = [stewards.index(s) for s in combo]
        self.results = []
        self._total = None
    def __getattr__(self, item):
        if item == 'combined_score':
            if self._total is None:
                self._total = sum([r.score for r in self.results])
            return self._total
        raise AttributeError(item)
    def __cmp__(self, other):
        return self.combined_score - other.combined_score
    def __str__(self):
        return '%s: %s' % ('+'.join(self.combo), self.combined_score)

class ScenarioResult:
    '''Encapsulate info about one combination of stewards in one scenario.'''
    def __init__(self, scenario, scenarios, liks, faults, combo_indexes, f, mttrs):
        self.name = scenario
        self.idx = scenarios.index(scenario)
        self.likelihood = liks[self.idx]
        self.combo_indexes = combo_indexes
        self.f = f
        self.fault_count = 0
        relevant_mttrs = []
        profile = []
        for ci in combo_indexes:
            relevant_mttrs.append(mttrs[ci])
            faults_for_member = faults[ci]
            n = faults_for_member[self.idx]
            profile.append(n)
            if n:
                self.fault_count += 1
        self.profile = profile
        self.failure_distance = self.f - self.fault_count
        if self.failure_distance < 0:
            relevant_mttrs.sort()
            # The MTTR of the scenario is the time it will take for the i-th node to
            # repair its fault, where i is the number of the node that finally
            # gets the whole network back into consensus.
            self.mttr = relevant_mttrs[-(self.failure_distance + 1)]
            self.importance = self.likelihood * self.mttr
        else:
            # We don't have any repair time if we never lost consensus.
            self.mttr = 0
            # The importance of an uptime is its likelihood * the average downtime of all
            # the nodes in the scenario.
            self.importance = self.likelihood * sum(relevant_mttrs) / len(relevant_mttrs)
        # The score of a scenario is its importance * its failure_distance
        self.score = (self.importance * self.failure_distance)
    def __cmp__(self, other):
        return self.score - other.score

def analyze(f, scenarios, liks, stewards, mttrs, faults, bestN):
    m = (3 * f) + 1
    n = len(stewards)
    total_combinations = factorial(n) / (factorial(m) * factorial(n - m))
    print('Analyzing %d total %d-steward combinations (n=%d, f=%d).' % (total_combinations, m, n, f))
    best = BestN(lambda x: x.combined_score, bestN)
    for combo in unique_combinations(stewards, m):
        analyze_combo(combo, best, scenarios, liks, stewards, mttrs, faults, f)
    return best

def analyze_combo(combo, best, scenarios, liks, stewards, mttrs, faults, f):
    '''
    Given a single combination, evaluate its downtime across all scenarios. If it has less
    downtime than one of the current "top N" combinations, put this one into the "top N"
    list.
    '''
    ca = ComboAnalysis(combo, stewards)
    for scenario in scenarios:
        sr = ScenarioResult(scenario, scenarios, liks, faults, ca.steward_indexes, f, mttrs)
        ca.results.append(sr)
    best.keep_if_better(ca)

def unique_combinations(items, n):
    if n == 0:
        yield []
    else:
        for i in range(len(items)):
            for cc in unique_combinations(items[i + 1:], n - 1):
                yield [items[i]] + cc

def report(best, f):
    m = (3 * f) + 1
    title = '%d Best %d-Steward Combinations, Ranked' % (len(best.items), m)
    print('\n' + title)
    print('-' * len(title))
    for i in range(len(best.items)):
        combo = best.items[i]
        print('%d: %s' % (i + 1, combo))

def select(fname, suggested_f, bestN):
    f, scenarios, liks, stewards, mttrs, faults = load_data(fname, suggested_f)
    results = analyze(f, scenarios, liks, stewards, mttrs, faults, bestN)
    report(results, f)

class Tests(unittest.TestCase):

    def test_ScenarioResult(self):
        stewards = 'A,B,C,D,E,F'.split(',')
        scenarios = 'a,b,c'.split(',')
        liks = [.5, .4, .3]
        mttrs = [6,7,8,9,10,11]
        combo_indexes = [0,2,3,4]
        faults = [[0,1,1],[1,0,0],[0,0,0],[1,1,1],[0,1,0],[1,0,1]]
        sr = ScenarioResult('b', scenarios, liks, faults, combo_indexes, 1, mttrs)
        self.assertEquals(sr.name, 'b')
        self.assertEquals(sr.idx, 1)
        self.assertAlmostEquals(sr.likelihood, .4)
        self.assertEquals(sr.mttr, 8)
        self.assertAlmostEquals(sr.score, -6.4)

    def test_unique_combinations(self):
        fruit = 'apple,banana,orange,pear'.split(',')
        combos = '\n'.join(sorted(['+'.join(x) for x in unique_combinations(fruit, 2)]))
        self.assertEquals(combos, 'apple+banana\napple+orange\napple+pear\nbanana+orange\nbanana+pear\norange+pear')

    def test_is_empty_row(self):
        self.assertTrue(is_empty_row((None,None,None)))
        self.assertTrue(is_empty_row(('','','')))
        self.assertFalse(is_empty_row((1,'',None)))

    def test_convert_float(self):
        self.assertAlmostEquals(convert_float('1'), 1.0)
        self.assertAlmostEquals(convert_float(1), 1.0)
        self.assertAlmostEquals(convert_float('0.01'), 0.01)
        self.assertAlmostEquals(convert_float('10%'), 0.1)

    def test_factorial(self):
        self.assertEquals(factorial(1), 1)
        self.assertEquals(factorial(2), 2)
        self.assertEquals(factorial(3), 6)
        self.assertEquals(factorial(4), 24)

    def test_has_string(self):
        self.assertTrue(has_string(' abc '))
        self.assertTrue(has_string('X'))
        self.assertFalse(has_string(' 123'))

    def test_has_num(self):
        self.assertFalse(has_num(' abc '))
        self.assertFalse(has_num('X'))
        self.assertTrue(has_num(' 123'))
        self.assertTrue(has_num('-2'))
        self.assertTrue(has_num('1%'))

    def test_is_steward_row(self):
        self.assertTrue(is_steward_row(('x', '25', 1, '0', '0', '1')))
        self.assertFalse(is_steward_row(('x', '25', 5, '0', '0', '1')))
        self.assertFalse(is_steward_row(('x', '25', '1', '0', '0.1', '1')))

    def test_max_f_for_steward_count(self):
        self.assertEquals(max_f_for_steward_count(0), 0)
        self.assertEquals(max_f_for_steward_count(3), 0)
        self.assertEquals(max_f_for_steward_count(4), 1)
        self.assertEquals(max_f_for_steward_count(5), 1)
        self.assertEquals(max_f_for_steward_count(7), 2)

    def test_parse_headers(self):
        rows = [x.split(',') for x in ''',,scheduled maintenance coincidence,botched upgrade,foo
likelihood per year (from MTBF),,1%,85%,17%
Steward,MTTR,fault?,fault?,fault?
Bank A,5,1,1,0
Tech Firm B,13,1,0,1'''.replace('\r', '').split('\n')]
        f, scenarios, liks, row_idx = parse_headers(rows)
        self.assertEquals(row_idx, 3)
        self.assertEquals(liks, [0.01,0.85,0.17])
        self.assertEquals(f, 0)

    def test_load_data_good(self):
        fname = os.path.join(os.path.dirname(__file__), 'sample-data.csv')
        f, scenarios, liks, stewards, mttrs, faults = load_data(fname, f_from_data_file)
        self.assertEquals(f, 1)
        self.assertEquals(scenarios[0], 'scheduled maintenance coincidence')
        self.assertEquals(scenarios[11], 'major natural disaster, US East Coast')
        self.assertEquals(liks, [0.01, 0.85, 0.0001, 0.05, 0.01, 0.8, 0.03, 0.5, 0.02, 0.03, 0.1, 0.0001])
        self.assertEquals(stewards, ['Bank A', 'Tech Firm B', 'University C', 'Law Firm D', 'NGO E', 'Government F', 'Consortium G', 'Tech Firm H', 'Biotech Firm J'])
        self.assertEquals(mttrs, [5.0, 13.0, 11.0, 6.0, 6.0, 9.0, 12.0, 8.0, 7.0])
        self.assertEquals(faults[0], [1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0])
        self.assertEquals(faults[8], [1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0])

    def test_not_enough_stewards(self):
        fname = os.path.join(os.path.dirname(__file__), 'sample-data.csv')
        self.assertRaises(Exception, load_data, fname, 5)

    def test_BestN(self):
        # Keep a list of the 3 best integers. Always give it back in sorted form.
        b = BestN(lambda x: x, 3)
        def try_this(*args):
            b = BestN(lambda x: x, 3)
            for arg in args:
                b.keep_if_better(arg)
            return b
        b = try_this(3,10,4,11,9)
        self.assertEquals(b.items, [11,10,9])
        self.assertEquals(b.worst_idx, 2)
        self.assertEquals(b.worst_score, 9)
        b = try_this(-10,-9,-3.14,4.0,-1)
        self.assertEquals(b.items, [4,-1,-3.14])

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
        select(args.fname, args.f, args.best)
