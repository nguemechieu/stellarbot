=======================
StellarBot - Trading Bot
=======================

StellarBot is a professional trading bot that interacts with the Stellar network, enabling automated and manual trades on the Stellar blockchain.

.. image:: https://img.shields.io/github/actions/workflow/status/nguemechieu/stellarbot/continuous-integration-workflow.yml?branch=master
    :alt: GitHub Workflow Status
    :target: https://github.com/nguemechieu/stellarbot/actions

.. image:: https://img.shields.io/pypi/v/stellarbot-sdk.svg
    :alt: PyPI
    :target: https://pypi.python.org/pypi/stellarbot-sdk

.. image:: https://static.pepy.tech/personalized-badge/stellarbot-sdk?period=total&units=abbreviation&left_color=grey&right_color=brightgreen&left_text=Downloads
    :alt: PyPI - Downloads
    :target: https://pypi.python.org/pypi/stellarbot-sdk

.. image:: https://img.shields.io/codeclimate/maintainability/stellarbot
    :alt: Code Climate maintainability
    :target: https://codeclimate.com/github/nguemechieu/stellarbot/maintainability

.. image:: https://img.shields.io/codecov/c/github/stellarbot/v2
    :alt: Codecov
    :target: https://codecov.io/gh/nguemechieu/stellarbot


Key Features
------------

- **Automated Trading:** Configure trading strategies and let the bot execute trades automatically.
- **Manual Trading:** Use the bot for manual trades on the Stellar blockchain with ease.
- **Stellar Network Integration:** Full integration with the Stellar network for real-time data and transactions.
- **Asynchronous & Synchronous Support:** Trade using both asynchronous and synchronous modes.

Documentation
-------------

The full documentation is available at:

* https://stellarbot-sdk.readthedocs.io

Installation
------------

Install the latest version of StellarBot via pip:

.. code-block:: bash

    pip install stellarbot

We follow `Semantic Versioning <https://semver.org/>`_ and recommend pinning the major version of this package in your requirements file to avoid any breaking changes.

Quick Start
-----------

Here's an example to get you started with using StellarBot for trading:

.. code-block:: python

    from stellar_sdk import Server, Keypair, TransactionBuilder, Network

    # Initialize keypair and server
    alice_keypair = Keypair.from_secret("YOUR_SECRET_KEY")
    server = Server("https://horizon-testnet.stellar.org")

    # Build a transaction
    alice_account = server.load_account(alice_keypair.public_key)
    transaction = (
        TransactionBuilder(
            source_account=alice_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=100
        )
        .append_payment_op(
            destination="GXXXXXXX",  # Bob's account ID
            amount="10.25",
            asset="XLM"
        )
        .set_timeout(30)
        .build()
    )
    transaction.sign(alice_keypair)

    # Submit the transaction
    response = server.submit_transaction(transaction)
    print(response)

Examples
--------

Explore more examples in the repository to understand how StellarBot can automate and simplify your trading strategies:

* https://github.com/nguemechieu/stellarbot/tree/master/examples

Development
-----------

To contribute to the development of StellarBot:

1. Fork the repository: https://github.com/nguemechieu/stellarbot
2. Create your feature branch: ``git checkout -b feature/YourFeature``
3. Commit your changes: ``git commit -am 'Add some feature'``
4. Push to the branch: ``git push origin feature/YourFeature``
5. Submit a pull request

License
-------

This project is licensed under the terms of the Apache License 2.0. See the LICENSE file for more information.

Useful Links
------------

- Documentation: https://stellarbot-sdk.readthedocs.io
- Source Code: https://github.com/nguemechieu/stellarbot
- Issue Tracker: https://github.com/nguemechieu/stellarbot/issues
- License: `Apache License 2.0 <https://github.com/nguemechieu/stellarbot/blob/master/LICENSE>`_

Thanks
------

A big thank you to all the contributors who have helped improve StellarBot!

