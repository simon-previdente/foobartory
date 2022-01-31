Foobartory
==========

A kata with parallelism issues.

Setup
-----

Requirements: Python 3.6+ (with ``asyncio``, f-strings, ``typing``)

No additional package is required.

To run the program : ``python3 foobartory.py``

To run the tests: ``python3 foobartory_test.py``

Architecture
------------

Implementation inspired by the actor pattern :

- There is no shared state, immutable data is passed through the message queues.

- The manager manages the inventory and emits request messages

- The bots are the actors that process the messages (in ``requests`` queue) and transmit their results (in ``results`` queue)


The advantage of this architecture is that it avoids shared resource problems such as deadlocks.