import random
import torch
import torch.nn as nn

from collections import deque
from ai.networks.Networks import DQNNetwork

class DDQNWER:
    """
    Double Deep Q Network with Experience Replay
    """
    
    def __init__(self, lr, gamma, epsilon, input_size, actions):
        self.lr = lr
        self.gamma = gamma
        self.epsilon = epsilon
        self.actions = actions
        self.network = DQNNetwork(input_size, len(actions))
        self.target_network = DQNNetwork(input_size, len(actions))
        
        self.target_network.load_state_dict(self.network.state_dict())
        
        self.optimizer = torch.optim.Adam(self.network.parameters(), lr=self.lr)
        self.criterion = torch.nn.MSELoss()
        self.loss = 0
        
        self.bach_size = 32
        self.memory = deque(maxlen=1000)
    
    def add_in_memory(self, state, action, reward, next_state):
        self.memory.append((state, action, reward, next_state))
        
    def sample_memory(self):
        return random.sample(self.memory, self.bach_size)  

    def convert(self, state) -> None:
        state = [int(i) for i in state]
        return torch.tensor(state, dtype=torch.float32)
    
    def choose_action(self, state) -> int:
        state = self.convert(state)
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        else:
            with torch.no_grad():
                return self.network(state).argmax().item()
            
    def learn(self) -> None:
        if len(self.memory) < self.bach_size:
            return
        
        batch = self.sample_memory()
        
        for state, action, reward, next_state in batch:
            state = self.convert(state)
            next_state = self.convert(next_state)
            q_values = self.network(state)
            next_q_values = self.target_network(next_state)
            q_values[action] = reward + self.gamma * next_q_values.max().item()
            loss = self.criterion(self.network(state), q_values)
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            self.loss = loss.item()
       
    def update_target_network(self):
        self.target_network.load_state_dict(self.network.state_dict())
    