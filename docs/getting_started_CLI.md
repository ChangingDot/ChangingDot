# Getting Started

## Installation

### Prerequisites

At the moment we only support C#, python support is planned for the near future.

You need to have .NET8.0 runtime installed on your machine. You can install it [here](https://dotnet.microsoft.com/download/dotnet/8.0)

### Install

You can install our CLI using the following command :

``` bash
pip install cdot
```

## Creating your first graph

To test out the tech, you can first download our simple test repo : 

```bash
git clone git@github.com:ChangingDot/ChangingLevels.git
```

Our CLI takes as input a path to a configuration file. In this readme we use a very simple change with config file stored in a CDN. 

Make sure you are in the ChangingLevels repo and run :

```bash
cdot run create https://rawcdn.githack.com/ChangingDot/ChangingBack/main/examples/example.yaml
```

## Visualizing your graph

You can then visualize the created graph by running this command : 

```bash
cdot run visualize https://rawcdn.githack.com/ChangingDot/ChangingBack/main/examples/example.yaml
```

## Committing the changes

A longer term goal of ChangingDot is to automate actual refactorings and therefore actually change the code. You can actually test this out using the following command.

```bash
cdot run commit https://rawcdn.githack.com/ChangingDot/ChangingBack/main/examples/example.yaml
```