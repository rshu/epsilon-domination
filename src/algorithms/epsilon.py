#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2019, Jianfeng Chen <jchen37@ncsu.edu>
# vim: set ts=4 sts=4 sw=4 expandtab smartindent:
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, _distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

import os
import sys
import collections
import random
import numpy as np

cwd = os.getcwd()
root = cwd[:os.getcwd().rfind('e-dom/') + len('e-dom/') - 1]
sys.path.append(f'{root}/src')
from model import ML


# Assumping all objectives are to maximize
def epsilon(dataset, HP_obj, eval_func, N1, epsilon_lst):
    weights = dict()
    epsilon_lst = np.array(epsilon_lst)
    for name in HP_obj.pres + HP_obj.learns:
        weights[name] = 0

    # Step1: find the best preprocessor and best learner
    best_values = np.array([np.NINF for _ in range(len(epsilon_lst))])

    for _ in range(N1):
        rnd_hp, pre, learner = HP_obj.get_rnd_hp_without_range()
        # print(rnd_hp)
        values = eval_func(dataset, rnd_hp)

        diff_weight = 0
        diff_weight += collections.Counter(
            (values - best_values) > epsilon_lst)[True] / len(epsilon_lst)
        # pdb.set_trace()
        diff_weight -= collections.Counter(
            (values - best_values) < -1 * epsilon_lst)[True] / len(epsilon_lst)

        weights[pre] += diff_weight
        weights[learner] += diff_weight

        best_values = np.maximum(best_values, values)

    best_pre, best_learner = HP_obj.pres[0], HP_obj.learns[0]
    for i in HP_obj.pres:
        if weights[i] > weights[best_pre]:
            best_pre = i
    for j in HP_obj.learns:
        if weights[j] > weights[best_learner]:
            best_learner = j

    print('best_pre', best_pre)
    print('best_learner', best_learner)


    # Step2, start from best pre and best learner
    N2 = 100
    best_weights = dict()

    for i in range(N2):
        rnd_hp = HP_obj.get_rnd_hp_from_best(best_pre, best_learner)
        # print(rnd_hp)
        best_weights[str(rnd_hp)] = 0

    best_values_n2 = np.array([np.NINF for _ in range(len(epsilon_lst))])
    print(best_weights)

    for key in best_weights:
        rnd_hp = eval(key)
        print(rnd_hp)
        values_n2 = eval_func(dataset, rnd_hp)
        print(values_n2)

        diff_weight = 0
        diff_weight += collections.Counter(
            (values_n2 - best_values_n2) > epsilon_lst)[True] / len(epsilon_lst)

        # pdb.set_trace()
        diff_weight -= collections.Counter(
            (values_n2 - best_values_n2) < -1 * epsilon_lst)[True] / len(epsilon_lst)

        best_weights[key] += diff_weight

        best_values_n2 = np.maximum(best_values, values)

    print(best_weights)

    # find best and worst in N2
    best_candidate = list(best_weights.keys())[0]
    worst_candidate = list(best_weights.keys())[0]

    for key in best_weights.keys():
        if best_weights[key] > best_weights[best_candidate]:
            best_candidate = key

        if best_weights[key] < best_weights[worst_candidate]:
            worst_candidate = key

    print(type(eval(best_candidate)))
    print(best_candidate)
    print(type(eval(worst_candidate)))
    print(worst_candidate)

    # update range in N3 stage
    

if __name__ == '__main__':
    random.seed(2019)
    FARSEC_HP = ML.get_HP_obj()
    epsilon('derby', FARSEC_HP, ML.evaluation, 100, [0.2, 0.2, 0.2])
