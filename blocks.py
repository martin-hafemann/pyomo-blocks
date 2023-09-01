import pandas as pd
from pyomo.environ import *


# Get input parameters for the cgu
data = pd.read_csv(
    'data/assets/BHKWHilde.csv',
    index_col=0
)


def cgu_block_rule(block):
    """Rule for creating a cgu block with default components and constraints."""
    # Get index from model
    t = block.model().t

    # Define components
    block.bin = Var(t, within=Binary)
    block.gas = Var(t, domain=NonNegativeReals)
    block.power = Var(t, domain=NonNegativeReals)
    block.heat = Var(t, domain=NonNegativeReals)


    # Define construction rules for constraints
    def power_max_rule(_block, i):
        """Rule for the maximal power."""
        return _block.power[i] <= data.loc['Max', 'Power'] * _block.bin[i]
    

    def power_min_rule(_block, i):
        """Rule for the minimal power."""
        return data.loc['Min', 'Power'] * _block.bin[i] <= _block.power[i]
    

    def gas_depends_on_power_rule(_block, i):
        """Rule for the dependencies between gas demand and power output."""
        gas_max = data.loc['Max', 'Gas']
        gas_min = data.loc['Min', 'Gas']
        power_max = data.loc['Max', 'Power']
        power_min = data.loc['Min', 'Power']

        a = (gas_max - gas_min) / (power_max - power_min)
        b = gas_max - a * power_max

        return _block.gas[i] == a * _block.power[i] + b * _block.bin[i]
    

    def heat_depends_on_power_rule(_block, i):
        """Rule for the dependencies betwwen heat and power output."""
        heat_max = data.loc['Max', 'Heat']
        heat_min = data.loc['Min', 'Heat']
        power_max = data.loc['Max', 'Power']
        power_min = data.loc['Min', 'Power']

        a = (heat_max - heat_min) / (power_max - power_min)
        b = heat_max - a * power_max

        return _block.heat[i] == a * _block.power[i] + b * _block.bin[i]


    # Define constraints
    block.power_max_constraint = Constraint(
        t,
        rule=power_max_rule
        )
    block.power_min_constraint = Constraint(
        t,
        rule=power_min_rule
        )
    block.gas_depends_on_power_constraint = Constraint(
        t,
        rule=gas_depends_on_power_rule
        )
    block.heat_depends_on_power_constraint = Constraint(
        t,
        rule = heat_depends_on_power_rule
    )


