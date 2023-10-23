Fury Agents Manifesto
=====================

**Starting date: 21st October, 2023**


ChainFury's `first commit`_ was on 7th April, 2023. It has been about 6 months since then and it has undergone lot of
production usage. With multiple API changes and engines, we are now at a stable place. This is also a good time to check
up on the things that have released in the wild till now.

tl;dr
-----

Predictable automated chains as agents, that use tree searching algorithms to find solution to a problem with given set
of actions. Has ability to create new actions and learn from feedback. 

Agents
------

There have been several "agent like" systems that have been released. Some can create code, others can perform advanced
searching. Ultimately all of them can be modelled as a Chain and use different algorithms. ``chainfury`` can support
all algorithms and has a type-based robust chaining engine. This means building agents is the next logical step. There
is a lot of theory and academic research done on the topic of agents. All of them have different tradeoffs. But first
let's start with the requirements of an agent.

* Agent should be able to execute task without human intervention
* Agent should stop when it can't proceed
* Agent should be interruptible to take in feedback
* Agent should take inputs from it's environment
* Agent should be able to remember things over time
* Agent should be predictable in its behaviour, debuggable

Von-Neumann machine
~~~~~~~~~~~~~~~~~~~

We are followers of the agent as a `Von-Neumann machine`_, which means each chain has a complete I/O mechanism where
each input and output can be accessed independently. ``chainfury`` can use different memory systems like VectorDB, etc.
meaning that it can persist data over time. For the CPU analogy we have :py:mod:`chainfury.base.Chain` which models the
execution as a DAG of :py:class:`chainfury.base.Node` objects. Each node contains the unit step of the chain. We can
parallellise and speed up executions by using :py:mod:`chainfury.utils.threaded_map`.

``chainfury`` is already being used in production and thus with the infrastructure layer sorted we can then think about
what to build on top of it.

Automated
~~~~~~~~~

One of the most important things is that these agents be automated and run without human in the loop.

Edits
-----

.. all the links here

.. _first commit: https://github.com/NimbleBoxAI/ChainFury/commit/64a5f7b0fcf3d8bcce0cde6ee974b659ebe01b68
.. _Von-Neumann machine: https://blog.nimblebox.ai/new-flow-engine-from-scratch
