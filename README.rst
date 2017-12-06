########
Use Case
########

Before launching pyogame, make sure you've installed all dependencies and that selenium is running.

If it's all good you can try to launch this command for basic rapatriation :

.. code-block:: console

    python ogame.py <account_key>

Where <account_key> is the name of the key under which you set your parameters in the configuration file.

Different options are available :

- rapatriate, shortcut r, will send your resources to the capital
- construct, shortcut c, will construct planed resources buildings
- probes, shortcut p, with argument <range> will send probes around your capital with a range of <range>
- build, shortcut b, with argument <n>/<building> will build a <building> building on number planet <n>
