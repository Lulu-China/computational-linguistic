# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np

class HMM():
    def __init__(self, HMM_params):
        self.A = np.array(HMM_params.get('A'))
        self.B = np.array(HMM_params.get('B'))
        self.S = np.array(HMM_params.get('S',['q'+str(i) for i in range(len(self.A))]))
        self.V = np.array(HMM_params.get('V',['v'+str(i) for i in range(len(self.B))]))
        self.pi = np.array(HMM_params.get('pi',np.ones(len(self.S))/len(self.S)))
        
    def viterbi(self,obs_seq):
        # 初始化
        delta = self.pi * self.B[np.where(self.V==obs_seq[0])]
        psi = np.zeros((1,len(self.S))).astype(int)
        # 迭代计算
        for t in range(1,len(obs_seq)):
            i_to_j = np.multiply(delta[-1,:], self.A.T)
            delta_t = np.max(i_to_j, axis=1) * self.B[np.where(self.V==obs_seq[t])]
            psi_t = np.argmax(i_to_j, axis=1)
            delta = np.r_[delta, delta_t]
            psi = np.r_[psi, [psi_t]]
        # 终止
        P_star = np.max(delta[-1,:])
        Q = [np.argmax(delta[-1,:])]
        # 最佳路径
        for t in range(1,len(obs_seq)):
            Q.append(psi[t,Q[-1]])
        Q.reverse()
        # 保存变量
        self.delta = delta
        self.path = self.S[Q]
        self.P_star = P_star
        return
    
    def forward_algorithm(self, obs_seq):
        # 初始化
        alpha = self.pi * self.B[np.where(self.V==obs_seq[0])]
        # 迭代计算
        for t in range(1,len(obs_seq)):
            alpha_t = np.dot(alpha[-1,:], self.A) * self.B[np.where(self.V==obs_seq[t])]
            alpha = np.r_[alpha, alpha_t]
        # 终止
        self.alpha = alpha
        self.probability = np.sum(alpha[-1,:])
        return


def viterbi(HMM_params, obs_seq):
    A = np.array(HMM_params.get('A'))
    B = np.array(HMM_params.get('B'))
    S = np.array(HMM_params.get('S',['q'+str(i) for i in range(len(A))]))
    V = np.array(HMM_params.get('V',['v'+str(i) for i in range(len(B))]))
    pi = np.array(HMM_params.get('pi',np.ones(len(S))/len(S)))
    # 初始化
    delta = pi * B[np.where(V==obs_seq[0])]
    psi = np.zeros((1,len(S))).astype(int)
    # 迭代计算
    for t in range(1,len(obs_seq)):
        i_to_j = np.multiply(delta[-1,:], A.T)
        delta_t = np.max(i_to_j, axis=1) * B[np.where(V==obs_seq[t])]
        psi_t = np.argmax(i_to_j, axis=1)
        delta = np.r_[delta, delta_t]
        psi = np.r_[psi, [psi_t]]
    # 终止
    P_star = np.max(delta[-1,:])
    Q = [np.argmax(delta[-1,:])]
    # 最佳路径
    for t in range(1,len(obs_seq)):
        Q.append(psi[t,Q[-1]])
    Q.reverse()
    return S[Q], P_star, delta

def forward_algorithm(HMM_params, obs_seq):
    A = np.array(HMM_params.get('A'))
    B = np.array(HMM_params.get('B'))
    S = np.array(HMM_params.get('S',['q'+str(i) for i in range(len(A))]))
    V = np.array(HMM_params.get('V',['v'+str(i) for i in range(len(B))]))
    pi = np.array(HMM_params.get('pi',np.ones(len(S))/len(S)))
    # 初始化
    alpha = pi * B[np.where(V==obs_seq[0])]
    # 迭代计算
    for t in range(1,len(obs_seq)):
        alpha_t = np.dot(alpha[-1,:], A) * B[np.where(V==obs_seq[t])]
        alpha = np.r_[alpha, alpha_t]
    # 终止
    probability = np.sum(alpha[-1,:])
    return probability, alpha

if __name__ == "__main__":
    HMM_params = {'S':[1,2,3],
                  'V':['H','T'],
                  'A':[[0.9,0.05,0.05],[0.45,0.1,0.45],[0.45,0.45,0.1]],
                  'B':[[0.5,0.75,0.25],[0.5,0.25,0.75]],
                  'pi':[1/3,1/3,1/3]
                  }
    obs_seq = ['T','H','H']
    path, P_star, delta = viterbi(HMM_params,obs_seq)
    p, alpha = forward_algorithm(HMM_params, obs_seq)
    hmm = HMM(HMM_params)
    hmm.viterbi(obs_seq)
    hmm.forward_algorithm(obs_seq)
