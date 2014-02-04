############
Installation
############

First, you have to make sure that your configuration file is set.
If it's not, copy the example and edit it to your liking.

.. code-block:: console

    cp conf.json.example conf.json
    vim conf.json
    [...]

Then you have to install the few dependencies needed :

.. code-block:: console

    apt-get install python-lxml python-selenium python-dateutil

And finally download selenium and launch selenium :

.. code-block:: console

    wget http://selenium.googlecode.com/files/selenium-server-standalone-2.39.0.jar
    java -jar selenium-server-standalone-2.39.0.jar

You're then all set to launch pyogame !
