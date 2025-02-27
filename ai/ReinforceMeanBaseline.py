import numpy as np
import random
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical

from ai.networks.Networks import PNetwork

class ReinforceMeanBaseline:
    
    def __init__(self, lr, gamma, epsilon, input_size, actions):
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.actions = actions
        self.policy = PNetwork(input_size, len(actions)) 
        self.optimizer = optim.Adam(self.policy.parameters(), lr=self.lr)
        self.probs = []
        self.rewards = []
        self.loss = 0
        self.baseline = 0
        
    def convert(self, state) -> None:
        state = [int(i) for i in state]
        return torch.tensor(state, dtype=torch.float32)
    
    def choose_action(self, state) -> int:
        state = self.convert(state)
        if random.random() < self.epsilon:
            # Exploration: choisir une action au hasard avec probabilité epsilon
            return random.choice(range(len(self.actions)))
        else:
            # Exploitation: choisir l'action optimale selon la politique apprise
            probs = self.policy(state)
            m = Categorical(probs)
            action = m.sample()
            self.probs.append(m.log_prob(action))
            return action.item()
    
    def learn(self) -> None:
        discounts = []
        R = 0
        for r in self.rewards[::-1]:
            R = r + self.gamma * R
            discounts.insert(0, R - self.baseline)
            
        discounts = torch.tensor(discounts, dtype=torch.float32)
        
        policy_loss = []
        
        for log_prob, R in zip(self.probs, discounts):
            policy_loss.append(-log_prob * R)
        
        if policy_loss:
            self.optimizer.zero_grad()
            policy_loss = torch.stack(policy_loss).sum()
            
            policy_loss.backward()
            self.optimizer.step()
            
            self.loss = policy_loss.item()
            
            self.baseline = torch.mean(torch.tensor(self.rewards, dtype=torch.float32))
            
        self.probs = []
        self.rewards = []
