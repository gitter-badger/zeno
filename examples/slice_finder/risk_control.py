"""
    Statistical significance testing & false discovery control

    Author: Yeounoh Chung (yeounohster@gmail.com)
"""
from scipy import stats
import numpy as np
import math


def t_testing(sample_a, reference, alpha=0.05):
    ''' Unpaired two-sample (Welch's) t-test '''
    mu, s, n = reference[0], reference[1], reference[2]
    sample_b_mean = (mu*n - np.sum(sample_a))/(n-len(sample_a))
    sample_b_var = (s**2*(n-1) - np.std(sample_a)**2*(len(sample_a)-1))/(n-len(sample_a)-1)

    t = np.mean(sample_a) - sample_b_mean
    t /= math.sqrt( np.var(sample_a)/len(sample_a) + sample_b_var/(n-len(sample_a)) )

    prob = stats.norm.cdf(t)
    return prob
    

def effect_size(slice_reference, reference, size_min=0):
    mu, s, n = reference[0], reference[1], reference[2]
    slice_mu, slice_s, slice_n = slice_reference[0], slice_reference[1], slice_reference[2]
    if n-slice_n == 0:
        return 0
    if slice_n < size_min:
        return 0
    sample_b_mean = (mu*n - slice_mu*slice_n)/(n-slice_n)
    sample_b_var = (s**2*(n-1) - slice_s**2*(slice_n-1))/(n-slice_n-1)
    if sample_b_var < 0:
        sample_b_var = 0.

    diff = slice_mu - sample_b_mean
    diff /= math.sqrt( (slice_s + math.sqrt(sample_b_var))/2. )

    # mu, s, n = reference[0], reference[1], reference[2]
    # if n-len(sample_a) == 0:
    #     return 0
    # sample_b_mean = (mu*n - np.sum(sample_a))/(n-len(sample_a))
    # sample_b_var = (s**2*(n-1) - np.std(sample_a)**2*(len(sample_a)-1))/(n-len(sample_a)-1)
    # if sample_b_var < 0:
    #     sample_b_var = 0.

    # diff = np.mean(sample_a) - sample_b_mean
    # diff /= math.sqrt( (np.std(sample_a) + math.sqrt(sample_b_var))/2. )
    # return diff

    # comparing slice S and its counterpart S' (D-S)
    # counterpart: the rest of examples
    # H_o: slice S <= slice S'
    # H_a: slice S > slice S'
    # Welch's t-test: test if two populations have the same mean
    # Cohen’s d for Welch test
    # if t-statistic greater than threshold value, 
    # reject null (accept H_a slice S > slice S'), meaning S problematic
    # According to Cohen’s rule of thumb [18], 
    # an effect size of 0.2 is considered small, 
    # 0.5 is medium, 0.8 is large, and 1.3 is very large.

    return diff
