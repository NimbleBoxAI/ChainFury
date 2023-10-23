(RAG) Q/A with ChainFury
========================

One of the first use cases of LLM powered apps is question answering. This is how you should think about this problem:

* LLMs are "general purpose string-to-string computers", so they can take in a text information (data) and instruction
  on how to process that data
* If you have a question, you first need to find this data so you can add it to the input of the LLM
* This data can be found in a variety of places, such as blogs, PDFs, etc.

In order to achieve this outcome you need to figure out how to index this information and how to query it, then prompt
the LLM. There are two building blocks:

* **Vector Databse**: You first need to store the data in a way that is easy to query. The first thing you might think is a
  database like Postgres or MongoDB. However, these databases are for structured querying. They are not suited to the
  task of searching for a similar piece of text. For this you need vector databases like `Qdrant <https://qdrant.tech/>`_.
  To get the embeddings you will need to vectorize your dataset, for this we will use :code:`text-embedding-ada-002` model
  from OpenAI.
* **Prompt Engineering**: Once you have the data, you need to figure out the right way to ask the LLM and get response
  from it. This is where **ChainFury** comes into the picture. 

For code go to Github `@yashbonde/cf_demo <https://github.com/yashbonde/cf_demo>`_

Want to play with example in the `demo app`_.

Objective
---------

We are going to build a simple question answering system for slides of `Blitzscaling PDF`_. You can download the PDF
and keep it for your reference.

.. image:: https://www.thepowermba.com/en/wp-content/uploads/2021/07/BLITZSCALING-5-1024x629.png

Take a note of this, we will test our agent to answer this question! The outcome will be a Streamlit app where you can
query and get nicely summarized answers.

Step 0: Installing dependencies
-------------------------------

We install the following dependencies for this demo:

.. code-block:: bash

  echo '''fire==0.5.0
  PyMuPDF==1.22.5
  fitz==0.0.1.dev2
  chainfury>=1.4.3
  qdrant-client==1.1.1
  streamlit==1.26.0''' >> requirements.txt
  pip install -r requirements.txt

  # load the environment variables
  export QDRANT_API_URL="https://xxx" # qdrant.tech
  export QDRANT_API_KEY="hbl-xxxxxx"
  export OPENAI_TOKEN="sk-xxx"        # platform.openai.com
  export CHATNBX_TOKEN="tune-xxxxx"   # chat.nbox.ai

Step 1: Loading the PDF
-----------------------

We first load the PDF and extract the text from it, you can read the full code for `load_data.py`_. I'll only highlight
the few important parts here.


Step 1.1: Chunking of PDF
~~~~~~~~~~~~~~~~~~~~~~~~~

The first step is to break apart the document into "chunks". You can use several methods
for this, we will use the simplest. **One chunk = One page**.

  You can get into far more complex strategies based on tokens using :code:`tiktoken`, but for now we will keep it simple.

However a page can also contain a lot of text or no text so we come up with simple rules like:

* page contains atleast 10 words
* if page contains :code:`> 700 tokens ~ 2500 chars` we break it into parts of 2500 chars each

.. code-block:: python

  payloads = []
  for i,p in enumerate(page_text):
    if len(p.strip().split()) < 10:
      continue

    chunk_size = 2500
    if len(p) > 2500:
      for j,k in enumerate(range(0, len(p), int(chunk_size * 0.8))):
        payloads.append({"doc": pdf, "page_no": i, "chunk": j, "text": p[k:k+chunk_size]})

Step 1.2: Embeddings
~~~~~~~~~~~~~~~~~~~~

Next step is to get embeddings for each of these chunks. More important than getting chunks is to keep the system high
performance. For this we will use :mod:`chainfury.utils.threaded_map` to parallelize the process. We create buckets of
payloads and extract the text to get embeddings (batching):

.. code-block:: python

    # (batching + parallel) gives ~2 orders of magnitude speedup
    for b in buckets:
      full_out = threaded_map(
        fn = get_embedding,
        inputs = [(x, pbar) for x in b],
        max_threads = 16
      )
      all_items.extend(full_out)

Step 1.3: Loading in Qdrant
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally we load the embeddings into Qdrant. Note that there are two ways to load this data, read more about `Qdrant loading`_.

* **Fresh Load**: You can load the data from scratch, this will usually be the fastest since you are only going to upload
  to the disk directly. However, this is not good if you want to keep previous information in the database. For this we
  write:

  .. code-block:: python

    from chainfury.components.qdrant import recreate_collection, disable_indexing, enable_indexing

    recreate_collection(collection_name, 1536) # OpenAI embedding dim
    disable_indexing(collection_name)

    success = client.upload_collection(
      collection_name = collection_name,
      vectors = embedding,
      payload = payloads,
      ids = None, # Vector ids will be assigned automatically
      batch_size = 256 # How many vectors will be uploaded in a single request?
    )

    enable_indexing(collection_name)

* **Incremental Load**: You can load the data incrementally, this will be slower since you are going to be indexing as you
  are uploading, compute becomes a bottleneck in this case. For this you can temporarily disable indexing and then enable
  later. You can use inbuilt :mod:`chainfury.components.qdrant.qdrant_write` function to do this.

  .. code-block:: python

    from chainfury.components.qdrant import disable_indexing, enable_indexing, qdrant_write

    disable_indexing(collection_name)

    # **NOTE:** This part is not in the file and is just a representation of what the code will look like
    for emb_bucket, payload_bucket in zip(embedding_buckets, payloads_buckets):
      success, status, err = qdrant_write(
        embeddings = emb_bucket,
        collection_name = collection_name,
        extra_payload = payload_bucket,
      )

    enable_indexing(collection_name)

Step 2: Prompt Engineering
--------------------------


Next step is to retrieve the information at runtime and query the LLM, you can read the full code for `streamlit_app.py`_.
Again I am only highlighting the important parts here.

.. code-block:: python

  from chainfury.components.qdrant import qdrant_read

  out, err = qdrant_read(
    embeddings = embedding,
    collection_name = collection_name,
    top = 3, # How many results to return?
  )

From this we create prompt like this:

.. code-block:: python

  messages=[
    {
      "role" : "system", 
      "content" : '''
  You are a helpful assistant that is helping user summarize the information with citations.

  Tag all the citations with tags around it like:

  ```
  this is some text [<id>2</id>, <id>14</id>]
  ```'''},
    {
      "role": "user",
      "content": f'''
  Data points collection:

  {dp_text}

  ---

  User has asked the following question:

  {question}
  '''}
  ]

This is then passed to either `ChatNBX <chat.nbox.ai>`_ or OpenAI ChatGPT API. The response is then parsed and returned
to the user.


Step 3: Putting it all together
-------------------------------

Finally we put it all together in a Streamlit app. You can read the full code for `streamlit_app.py`_. The above code
can be put inside a single function and called with each query. You can use the `demo app`_ for your self now.

.. image:: https://d2e931syjhr5o9.cloudfront.net/chainfury/blitzscaling_qa_rag.png


We asked it a question and it gave the correct answer (see in the image in Objective section)!

.. all the links are here

.. _Blitzscaling PDF: https://drive.google.com/file/d/1QeWwfxEcYyAXkLexCgUX4AWr6nnO3Aqk/view?usp=sharing
.. _load_data.py: https://github.com/yashbonde/cf_demo/blob/master/load_data.py
.. _streamlit_app.py: https://github.com/yashbonde/cf_demo/blob/master/streamlit_app.py
.. _Qdrant loading: https://qdrant.tech/documentation/tutorials/bulk-upload/#upload-directly-to-disk
.. _demo app: https://blitzscaling.streamlit.app/
