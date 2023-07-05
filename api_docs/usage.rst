Using ChainFury
===============

ChainFury is a Python library for creating and manipulating automated agents. It is built ground up to be used in backend
services with superior user experience. This is a simple example script on how you can use the `chainfury`.

.. code-block:: python

   import os
   from pprint import pprint
   from chainfury import Chain, ai_actions_registry, Edge, get_client, Node
   from chainfury.client import create_new_chain, get_chain_from_dict  # skip if not running chainfury server
   from chainfury.types import Dag


Master of all trades
--------------------

There are two different ways to create chains, one to create via the python package and other to create using the dashboard.
In this particular example we will show how you can use the `chainfury` package and server APIs to create, store, retrieve
and execute chains.

.. image:: https://d2e931syjhr5o9.cloudfront.net/nbox/cf000.png
   :align: center

It is so simple, you can create a chain from python use it from the dashboard or via an API on the `chainfury` server.

Creating chains in python
-------------------------

In this example we will create a dag that looks like this. :code:`man1, man2, tell_story` are the actions you want to take
and :code:`question` is what you send as the input from the chatbox and :code:`story` is the output that you get as an
output to the chatbox.


.. image:: https://d2e931syjhr5o9.cloudfront.net/nbox/cf001.png
   :align: center

You can start by copying the code below, to see in more details you can check out :py:mod:`chainfury.agent.ai_actions_registry`.

.. code-block:: python

   man1 = ai_actions_registry.to_action(
      action_name = "man1",
      model_id="openai-chat",
      model_params={
         "model": "gpt-3.5-turbo",
      },
      fn={
         "messages": [
               {
                  "role": "user",
                  "content": "You are a man who was running in the middle of desert. You see a mac donalds and the waiters you ask the questions: {{ question }}? You are pissed and you say",
               },
         ],
      },
      outputs={
         "answer": ("choices", 0, "message", "content"),
      },
   )

   man2 = ai_actions_registry.to_action(
      action_name = "man2",
      model_id="openai-chat",
      model_params={
         "model": "gpt-3.5-turbo",
      },
      fn={
         "messages": [
               {
                  "role": "user",
                  "content": "Someone comes upto you in a bar and screams '{{ x }}'? give a funny response to it.",
               },
         ],
      },
      outputs={
         "out": ("choices", 0, "message", "content"),
      },
   )

   tell_story = ai_actions_registry.to_action(
      action_name = "tell_story",
      model_id="openai-chat",
      model_params={
         "model": "gpt-3.5-turbo",
      },
      fn={
         "messages": [
               {
                  "role": "user",
                  "content": '''Two men were fighting in a bar.
   One yelled '{{ man1 }}'.

   Other responded by yelling '{{ man2 }}'.

   Continue this story for 3 more lines.
   ''',
               },
         ],
      },
      outputs={
         "story": ("choices", 0, "message", "content"),
      },
   )

Now try printing the three variables :code:`man1, man2, tell_story` and see what they contain. You should see something
like this:

.. code-block:: python

   (FuryNode{ ('b7305e89-cdfd-49a2-87a6-11052fd61da5', 'ai-powered') [
         Var(*'question', type=string, items=[], additionalProperties=[]),
         Var(*'model', type=string, items=[], additionalProperties=[]),
         Var(*'messages', type=array, items=[Var('', type=object, items=[], additionalProperties=Var('', type=string, items=[], additionalProperties=[]))], additionalProperties=[]),
   ] (15) => (1) [
         Var('answer', type=string, items=[], additionalProperties=[]),
   ] },
   FuryNode{ ('83165745-f948-4262-9592-fd8c3120fa11', 'ai-powered') [
         Var(*'x', type=string, items=[], additionalProperties=[]),
         Var(*'model', type=string, items=[], additionalProperties=[]),
         Var(*'messages', type=array, items=[Var('', type=object, items=[], additionalProperties=Var('', type=string, items=[], additionalProperties=[]))], additionalProperties=[]),
   ] (15) => (1) [
         Var('out', type=string, items=[], additionalProperties=[]),
   ] },
   FuryNode{ ('a0946f6f-2be6-41c9-9fac-389490436958', 'ai-powered') [
         Var(*'man1', type=string, items=[], additionalProperties=[]),
         Var(*'man2', type=string, items=[], additionalProperties=[]),
         Var(*'model', type=string, items=[], additionalProperties=[]),
         Var(*'messages', type=array, items=[Var('', type=object, items=[], additionalProperties=Var('', type=string, items=[], additionalProperties=[]))], additionalProperties=[]),
   ] (16) => (1) [
         Var('story', type=string, items=[], additionalProperties=[]),
   ] })

Now we can create a chain as simple as this:

.. code-block:: python

   story_bot = Chain(
      [man1, man2, tell_story],
      [
         Edge(man1.id, "answer", man2.id, "x"),
         Edge(man1.id, "answer", tell_story.id, "man1"),
         Edge(man2.id, "out", tell_story.id, "man2"),
      ],
      sample={"question": ""},
      main_in="question",
      main_out=f"{tell_story.id}/story",
   )

Notice how we define the entire dag by defining the nodes and the edges. For sanity we also take in a sample input with
:code:`main_in` value, ie. :code:`question` and tell the :code:`main_out` ie. :code:`{tell_story.id}/story`. When you
print the :code:`story_bot` this is what you will get:

.. code-block:: python

   FuryDag(
      nodes: [
         b7305e89-cdfd-49a2-87a6-11052fd61da5,
         83165745-f948-4262-9592-fd8c3120fa11,
         a0946f6f-2be6-41c9-9fac-389490436958,
      ],
      edges: [
         FuryEdge('b7305e89-cdfd-49a2-87a6-11052fd61da5/answer' => '83165745-f948-4262-9592-fd8c3120fa11/x'),
         FuryEdge('b7305e89-cdfd-49a2-87a6-11052fd61da5/answer' => 'a0946f6f-2be6-41c9-9fac-389490436958/man1'),
         FuryEdge('83165745-f948-4262-9592-fd8c3120fa11/out' => 'a0946f6f-2be6-41c9-9fac-389490436958/man2'),
      ]
      main_in: question
      main_out: a0946f6f-2be6-41c9-9fac-389490436958/story
   )

Calling Chain
-------------

Calling the chain in a blocking fashion is super simple, you can just call the chain by passing the input string. Each call
will return the final output as well as all the intermediate steps. For example:

.. code-block:: python

   out, thoughts = story_bot("nice earrings!")
   pprint(thoughts)
   print("----")
   print(out)

In this you will get response like:

.. code-block::

   {'83165745-f948-4262-9592-fd8c3120fa11/out': {'timestamp': '2023-07-04T10:54:27.956500',
                                                   'value': '"Well, I may not have ...'},
   'a0946f6f-2be6-41c9-9fac-389490436958/story': {'timestamp': '2023-07-04T10:54:33.322340',
                                                   'value': 'As the two men ...'},
   'b7305e89-cdfd-49a2-87a6-11052fd61da5/answer': {'timestamp': '2023-07-04T10:54:25.724288',
                                                   'value': '"No, I don\'t have ...'}}
   ----
   As the two men continued to exchange loud words, the entire bar fell into an attentive silence. The onlookers couldn't
   help but be intrigued by the strange twist the conversation had taken. They leaned in closer, eagerly awaiting the next
   words to be hurled across the room. Suddenly, a wise old man sitting in a corner table interrupted the escalating
   argument. His weathered face held the weight of countless tales. With a calm yet commanding tone, he said, "Gentlemen,
   instead of engaging in a pointless brawl, let me share a true story that will quench your thirst for adventure and
   \teach you the value of compassion." With the bar now captivated by the storyteller's presence, the clashing egos were
   replaced by curiosity and anticipation. Little did anyone know, this chance encounter in the bar would lead to an
   extraordinary journey, bound to leave a lasting impact on the lives of everyone involved.


You can read more about it in :py:mod:`chainfury.base.Chain.__call__`.


Stream Chain
------------

Now you can also get the responses from the chain as each step is executed. In order to do that you will have to modify your code
to handle an iterator. You can read more in :py:mod:`chainfury.base.Chain.stream`

.. code-block:: python

   cf_stream_response = story_bot.stream("nice earrings!")

   out = None
   thoughts = {}
   for ir, done in cf_stream_response:
      if not done:
         thoughts.update(ir)
         pprint(ir)
      else:
         out = ir

   # use out and thoughts just like a normal call
   print("----")
   print(out)

Notice the dict by dict prints instead of a single large dictionary with all keys:

.. code-block::

   {'b7305e89-cdfd-49a2-87a6-11052fd61da5/answer': {'timestamp': '2023-07-04T10:54:35.857234',
                                                   'value': '"Nice earrings? Are ...'
                                                   }}
   {'83165745-f948-4262-9592-fd8c3120fa11/out': {'timestamp': '2023-07-04T10:54:39.355871',
                                                'value': 'Well, it seems like ...'
                                                }}
   {'a0946f6f-2be6-41c9-9fac-389490436958/story': {'timestamp': '2023-07-04T10:54:43.044220',
                                                   'value': 'The man in need of ...'
                                                   }}
   ----
   The man in need of water and food couldn't help but burst into laughter at the unexpected solution. He appreciated the
   cleverness and humor in his opponent's response. Their tense faces softened as they realized the absurdity of their
   argument in the midst of their shared predicament. They both agreed to set aside their differences and set off in search
   of the nearest oasis, sharing a newfound camaraderie along the way. And so, the bar altercation evolved into an unlikely
   bond forged by thirst, hunger, and a pair of watermelon earrings.

Superpowers with chainfury server
---------------------------------

This is only applicable when you are also using the `chainfury` server. If you are not then you can skip this section.

Put the chain in the DB
^^^^^^^^^^^^^^^^^^^^^^^

Once you are confident that chain you have built works and you want others to use this chain you can put it in the DB.

.. code-block:: python

   chain_db = create_new_chain("funny_story", story_bot)
   print(chain_db)

   {
      'name': 'funny_story',
      'description': None,
      'dag': {
         'nodes': [
            {'id': 'b7305e89-cdfd-49a2-87a6-11052fd61da5', ...},
            ...
         ],
         'edges': [
            {'id': 'b7305e89-cdfd-49a2-87a6-11052fd61da5/answer-83165745-f948-4262-9592-fd8c3120fa11x', ...},
            ...
         ],
         'sample': {'question': ''},
         'main_in': 'question',
         'main_out': 'a0946f6f-2be6-41c9-9fac-389490436958/story'
      },
      'engine': 'fury',
      'deleted_at': None,
      'id': 'efs5w2mz',
      'created_by': 'ng54wyxa',
      'meta': None,
      'created_at': '2023-07-04T10:54:43.071866'
   }

Loading Chain from DB
^^^^^^^^^^^^^^^^^^^^^

You need to know the chatbot ID from the database that you can then use to load up the chain and use it as if you build it
using python. This flexibililty allows `chainfury` to be used in several different system architectures. To load a chain
from DB it is as simple as:

.. code-block:: python

   chain = Chain.from_id(chain_db["id"])

   cf_stream_response = chain.stream("why do you have a dry throat?")
   print("cf_stream_response:", cf_stream_response)

   out = None
   thoughts = {}
   for ir, done in cf_stream_response:
      if not done:
         thoughts.update(ir)
         pprint(ir)
      else:
         out = ir

   # use out and thoughts just like a normal call
   print("----")
   print(out)

Then you can stream the response just like above:

.. code-block::

   {'b7305e89-cdfd-49a2-87a6-11052fd61da5/answer': {'timestamp': '2023-07-04T10:54:45.501326',
                                                   'value': '"Excuse me, but why ...'
                                                   }}
   {'83165745-f948-4262-9592-fd8c3120fa11/out': {'timestamp': '2023-07-04T10:54:47.984287',
                                                'value': 'Well, it sounds like ...'
                                                }}
   {'a0946f6f-2be6-41c9-9fac-389490436958/story': {'timestamp': '2023-07-04T10:54:53.386416',
                                                   'value': "The first man's ..."
                                                   }}
   ----
   The first man's frustration subsided for a moment as he couldn't help but crack a smile at the clever response. "You've
   got a point there," he replied, wiping the sweat off his brow. "Guess I'll have to settle for a cold glass of water
   when I finally make it out of here."

   As the two men continued their banter, their voices softened, and the tension in the bar began to ease. They realized
   that their shared experience had brought about a strange camaraderie amidst the chaos. It was as if the scorching desert
   had forged an unlikely bond between them.

   With a newfound solidarity, they made a pact to conquer the relentless desert together. They raised their glasses,
   empty though they were, and toasted to their unexpected friendship. In that moment, they knew that no matter the
   challenges ahead, they were no longer alone in the vast expanse of the Mojave Desert.

The optimal way to use this setup is in the backend where you don't want to hardcode the chains in your codebase but
still be able to execute it by pulling from the DB.

Inference via API
^^^^^^^^^^^^^^^^^

If you know the chatbot ID which you have from the previous step then you can also all the API in which case the chain
will be executed on the server itself.

.. code-block:: python

   stub = get_client()
   prompt_fn = stub.chatbot.u(chain_db["id"]).prompt

   out, err = prompt_fn("post", json = {"session_id": "random-uuid", "new_message": "GET"})
   if err:
      print("ERROR:", err)
      print("OUTPUT:", out)
      raise
   out

You will get a response that looks something like:

.. code-block::

   {
   'result': 'The men\'s argument intensified, filled with anger and frustration. As they shouted insults back and forth '
             'the entire bar fell into an uneasy silence, everyone\'s eyes fixated on the escalating confrontation. A '
             'sense of impending chaos hung in the air, threatening to shatter the peace within the establishment.\n\nBut '
             'then, unexpectedly, a wise old man seated at the corner of the bar interjected, his voice calm yet commanding. '
             '"Gentlemen, perhaps it is not the desert or its dry humor to blame," he said softly. "Maybe, deep down, both '
             'of you are searching for something more than just water in this arid landscape."\n\nHis words lingered in the '
             'air, slowly diffusing the tension within the bar. The two fighters exchanged puzzled glances, their anger '
             'momentarily subsiding as they contemplated the old man\'s wisdom. Suddenly, a realization dawned upon them, '
             'reminding them of their shared humanity.',
   'thought': [{'engine': 'fury',
      'ir_steps': 3,
      'thoughts': ['be616dbe-ee7f-4b28-87a7-c60a185b6406/answer',
      'cb5d15e7-4e53-4efa-bf31-9c316acf7840/out',
      '9d4e1328-a18a-4e10-8396-8c349d2d818c/story']}],
   'num_tokens': 1,
   'prompt_id': 17823285}


Conclusion
----------

Now you are ready to use `chainfury`. This system is capable of building complex chains either from:
* dashboard
* python package

Then you can then use this chain from either from:
* python: by directly calling the chain
* python: loading the chain from the DB and executing it
* API: the server can also execute the chain and return the results

