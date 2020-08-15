"""
source: https://medium.com/@severinperez/making-the-most-of-polymorphism-with-the-liskov-substitution-principle-e22609866429

Liskov Substitution Principle (LSP) has 3 major canons:
1. A derived object cannot expect users to obey a stronger pre-condition than its parent object expects.
2. A derived object may not guarantee a weaker post-condition than its parent object guarantees.
3. Derived objects must accept anything that a base class could accept and have behaviors/outputs
   that do not violate the constraints of the base class.

The original code is written in Ruby
"""
from random import randint, choice


class Experiment:
    def __init__(self, title):
        self.title = title


class Scientist:
    def __init__(self, name):
        self.name = name

    def run_experiment(self, experiment):
        print(f'{self.name} is now running the {experiment.title} experiment.')


class MadScientist(Scientist):
    """ The original code has extra argument 'sabotage'. This violate LSP.
        original: run_experiment(self, experiment, sabotage)
        Updated:  run_experiment(self, experiment)
    """
    def run_experiment(self, experiment):
        if self.sabotage():
            print(f'{self.name} is now sabotaging the {experiment.title} experiment!')
        else:
            print(f'{self.name} is now running the {experiment.title} experiment.')

    def sabotage(self):
        """ This will generate random True and False value """
        return choice([True, False])


class Laboratory:
    def __init__(self, scientists: Scientist, experiments: Experiment):
        self.scientists = scientists
        self.experiments = experiments

    def run_all_experiments(self):
        for scientist in self.scientists:
            for experiment in self.experiments:
                scientist.run_experiment(experiment)


if __name__ == '__main__':
    chemistry_experiment = Experiment("chemistry")
    physics_experiment = Experiment("physics")
    biology_experiment = Experiment("biology")
    quantum_experiment = Experiment('Quantum Mechanics')
    experiments = [chemistry_experiment, physics_experiment, biology_experiment, quantum_experiment]

    marie_curie = Scientist("Marie Curie")
    niels_bohr = Scientist("Niels Bohr")
    hubert_farnsworth = MadScientist("Hubert Farnsworth")
    richard_feynman = MadScientist("Richard Feynman")
    scientists = [marie_curie, niels_bohr, hubert_farnsworth, richard_feynman]

    lab = Laboratory(scientists, experiments)
    lab.run_all_experiments()
