#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyomo.environ import *
from pyomo.dae import *
from pyomo.opt import SolverFactory
import matplotlib.pyplot as plt

ipm = SolverFactory('ipopt')



m = ConcreteModel()
m.t = ContinuousSet(bounds=(0,1))
m.x = Var(m.t, initialize=-1)
m.dxdt = DerivativeVar(m.x)
m.c = Constraint(m.t, rule=lambda n, i: n.dxdt[i] == n.x[i] ** 2 - 2 * n.x[i] + 1 if i > 0 else Constraint.Skip)
m.x[0].set_value(-3.0)
m.x[0].fix()

dae = TransformationFactory('dae.collocation')
dae.apply_to(m, nfe=2, ncp=2)
# m.pprint()

ipm.solve(m, tee=True)

# x = []
# t = []
# for i in m.t:
#     x.append(value(m.x[i]))
#     t.append(i)
#
# plt.plot(t, x)
# plt.show()

n_jump = 1
t_jump = m.t.get_lower_element_boundary(n_jump)  #: Starts at zero
t_jump = 0.666667
m.add_component('dummy_x', Var())
m.add_component('dummy_con', Constraint())
dummy_var = getattr(m, 'dummy_x')
dummy_con = getattr(m, 'dummy_con')
deq = getattr(m, 'dxdt_disc_eq')
print(deq[t_jump].expr._args[0])
print(hex(id(deq[t_jump].expr)))
# con_expr = deq[t_jump].expr
# print(hex(id(con_expr)))
# new_rhs = con_expr._args[0]
# new_rhs._args[1] = dummy_var
# print(deq[t_jump].expr)
# print(hex(id(deq[t_jump].expr)))
# print(con_expr)
# print(hex(id(con_expr)))
# deq[t_jump].set_value(con_expr)
def p_memhex(object):
    print(hex(id(object)))


con_expr = deq[t_jump].expr.clone()
new_rhs = con_expr._args[0]

old_var = new_rhs._args[1]
p_memhex(old_var)

new_rhs._args[1] = dummy_var

p_memhex(new_rhs._args[1])
deq[t_jump].set_value(con_expr)
dummy_exp = old_var - dummy_var == 0
dummy_con.set_value(dummy_exp)

ipm.solve(m, tee=True)
print(value(dummy_var))
m.pprint()
x = []
t = []
for i in m.t:
    x.append(value(m.x[i]))
    t.append(i)
    if i == t_jump:
        x.append(value(dummy_var))
        t.append(i)

plt.plot(t, x, '-o')
plt.show()