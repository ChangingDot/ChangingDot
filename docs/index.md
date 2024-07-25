# Welcome to ChangingDot


ChangingDot uses static analysis and LLMs to create a graph of all changes that result from a intial seed change. 

This initial change can be anything, but we mostly focus our technology on refactorings and more specifically major dependency upgrades.

Using the graph, we can :

- Gain crucial insight the impact of the upgrade
- Have an idea of the nature of the resulting changes
- Rapidly uncover hard to find couplings that drag the project on and on
- A initial upgrade attempt

This information can be used before any major change to : 

- Estimate the effort and time required
- Figure out the best strategy to minimize the effort of the update (use codemodes, big bang, divide and conquer...)
- Prepare for the breaking changes that are induced
- Never be surprised by unexpected coupling
