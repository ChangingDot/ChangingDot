<div align="center">
  <img src="./docs/assets/logo_white_background.png" alt="ChangingDot Logo" width=300></img>
</div>
<br>
<div align="center">
  <b>Prepare your major dependency updates with graph-guided refactoring analysis</b>
</div>
<br>
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


## Test us out using our CLI

``` bash
pip install changing-dot
```

### Installation

At the moment we only support C#, python support is planned for the near future.

You need to have .NET8.0 runtime installed on your machine. You can install it [here](https://dotnet.microsoft.com/download/dotnet/8.0)

### Creating your first graph

To test out the tech, you can first download our simple test repo : 

```bash
git clone git@github.com:ChangingDot/ChangingLevels.git
```

Our CLI takes as input a path to a configuration file. In this readme we use a very simple change with config file stored in a CDN. If you want to try out the technology on one of your own repo, check out the [documentation](https://changingdot.github.io/ChangingDot/).

Make sure you are in the ChangingLevels repo and run :

```bash
cdot create -c https://rawcdn.githack.com/ChangingDot/ChangingDot/main/examples/example.yaml
```

### Visualizing your graph

You can then visualize the created graph by running this command : 

```bash
cdot visualize -c https://rawcdn.githack.com/ChangingDot/ChangingDot/main/examples/example.yaml
```

### Running analyses on the graph

This graph can be used as a base for different analyses and even code changes. It gives crucial inforamtion on the impact of a seed change.
We don't currently support any analyses but plan to implement the following : 

- [ ] Breaking change analysis
- [ ] Spread analysis
- [ ] Complexity/ type of changes

If you have any ideas for other analyses or uses for the graph, to not hesitate to open an issue, or send us a message.

### Committing the changes

A longer term goal of ChangingDot is to automate actual refactorings and therefore actually change the code. You can actually test this out using the following command.

```bash
cdot commit -c https://rawcdn.githack.com/ChangingDot/ChangingDot/main/examples/example.yaml
```

If you do not want to automatically commit the changes, you can apply them to your local git repo to review and changes them later on

```bash
cdot apply-changes -c https://rawcdn.githack.com/ChangingDot/ChangingDot/main/examples/example.yaml
```
