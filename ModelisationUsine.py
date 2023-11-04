# -*- coding: utf-8 -*-
"""
Created on Mon Oct  30 20:01:27 2023

@author: FATNI Khalid
"""

import numpy as np
import simpy


def simulation_usine(env, reparateurs, pieces_de_rechange):
    global cout

    cout = 0.0

    for i in range(30):
        env.process(fonctionnement_machine(env, reparateurs, pieces_de_rechange))
    while True:
        cout += 3.75 * 8 * reparateurs.capacity + 300 * pieces_de_rechange.capacity
        yield env.timeout(8.0)


def fonctionnement_machine(env, reparateurs, pieces_de_rechange):
    global cout

    while True:
        yield env.timeout(generer_temps_panne())
        t_panne = env.now
        print(' {:.2f} machine en panne'.format(t_panne))
        env.process(reparer_machine(env, reparateurs, pieces_de_rechange))
        yield pieces_de_rechange.get(1)
        t_reparation = env.now
        print(' {:.2f} machine réparée'.format(t_reparation))
        cout += 20 * (t_reparation - t_panne)


def reparer_machine(env, reparateurs, pieces_de_rechange):
    with reparateurs.request() as demande:
        yield demande
        yield env.timeout(generer_temps_reparation())
        yield pieces_de_rechange.put(1)
        print(' {:.2f} réparation terminée'.format(env.now))


def generer_temps_panne():
    return np.random.uniform(132, 182)


def generer_temps_reparation():
    return np.random.uniform(4, 30)


temps_observation = []
cout_observation = []
nombre_pieces_rechange = []


def observer(env, pieces_de_rechange):
    while True:
        temps_observation.append(env.now)
        cout_observation.append(cout)
        nombre_pieces_rechange.append(pieces_de_rechange.level)
        yield env.timeout(1.0)


np.random.seed(0)

env = simpy.Environment()

reparateurs = simpy.Resource(env, capacity=3)

pieces_de_rechange = simpy.Container(env, init=15, capacity=15)

env.process(simulation_usine(env, reparateurs, pieces_de_rechange))
env.process(observer(env, pieces_de_rechange))

env.run(until=8 * 5 * 52)

import matplotlib.pyplot as plt

plt.figure()
plt.step(temps_observation, cout_observation)
plt.xlabel('Temps (heures)')
plt.ylabel('Coût (DH')

plt.figure()
plt.step(temps_observation, nombre_pieces_rechange)
plt.xlabel('Temps (heures)')
plt.ylabel('Nombre de pièces de rechange')
