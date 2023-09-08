StellarBot Python SDK
==================

.. image:: https://img.shields.io/github/actions/workflow/status/nguemechieu/stellarbot/continuous-integration-workflow.yml?branch=master
    :alt: GitHub Workflow Status
    :target: https://github.com/nguemechieu/stellarbot/actions

.. image:: https://img.shields.io/readthedocs/stellarbot-sdk.svg
    :alt: Read the Docs
    :target: https://stellar-sdk.readthedocs.io/en/latest/

.. image:: https://static.pepy.tech/personalized-badge/stellarbot-sdk?period=total&units=abbreviation&left_color=grey&right_color=brightgreen&left_text=Downloads
    :alt: PyPI - Downloads
    :target: https://pypi.python.org/pypi/stellarbot-sdk

.. image:: https://img.shields.io/codeclimate/maintainability/stellarbot
    :alt: Code Climate maintainability
    :target: https://codeclimate.com/github/nguemechieu/stellarbot/maintainability

.. image:: https://img.shields.io/codecov/c/github/stellarbot/v2
    :alt: Codecov
    :target: https://codecov.io/gh/nguemechieu/stellarbot

.. image:: https://img.shields.io/pypi/v/stellarbot-sdk.svg
    :alt: PyPI
    :target: https://pypi.python.org/pypi/stellarbot-sdk

.. image:: https://img.shields.io/badge/python-%3E%3D3.7-blue
    :alt: Python - Version
    :target: https://pypi.python.org/pypi/stellarbot-sdk

.. image:: https://img.shields.io/badge/implementation-cpython%20%7C%20pypy-blue
    :alt: PyPI - Implementation
    :target: https://pypi.python.org/pypi/stellarbot-sdk

.. image:: https://img.shields.io/badge/stellarbot%20Protocol-19-blue
    :alt: Stellar Protocol
    :target: https://developers.stellarbot.org/docs/glossary/scp/

Documentation
-------------
py-stellar-base's documentation can be found at https://stellarbot-sdk.readthedocs.io.

Installing
----------

.. code-block:: text

    pip install -U stellar-sdk

We follow `Semantic Versioning 2.0.0 <https://semver.org/>`_, and I strongly
recommend that you specify its major version number in the dependency
file to avoid the unknown effects of breaking changes.

A Simple Example
----------------
You can find more examples `here <https://github.com/nguemechieu/stellarbot/tree/master/examples>`__.

Building transaction with synchronous server

.. code-block:: python

    # Alice pay 10.25 XLM to Bob
    from stellar_sdk import Asset, Server, Keypair, TransactionBuilder, Network

    alice_keypair = Keypair.from_secret("SBFZCHU5645DOKRWYBXVOXY2ELGJKFRX6VGGPRYUWHQ7PMXXJNDZFMKD")
    bob_address = "GA7YNBW5CBTJZ3ZZOWX3ZNBKD6OE7A7IHUQVWMY62W2ZBG2SGZVOOPVH"

    server = Server("https://horizon-testnet.stellar.org")
    alice_account = server.load_account(alice_keypair.public_key)
    base_fee = 100
    transaction = (
        TransactionBuilder(
            source_account=alice_account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=base_fee,
        )
        .add_text_memo("Hello, Stellar!")
        .append_payment_op(bob_address, Asset.native(), "10.25")
        .set_timeout(30)
        .build()
    )
    transaction.sign(alice_keypair)
    response = server.submit_transaction(transaction)
    print(response)


* Building transaction with asynchronous server

.. code-block:: python

    # Alice pay 10.25 XLM to Bob
    import asyncio

    from stellar_sdk import Asset, ServerAsync, Keypair, TransactionBuilder, Network
    from stellar_sdk.client.aiohttp_client import AiohttpClient

    alice_keypair = Keypair.from_secret("SBFZCHU5645DOKRWYBXVOXY2ELGJKFRX6VGGPRYUWHQ7PMXXJNDZFMKD")
    bob_address = "GA7YNBW5CBTJZ3ZZOWX3ZNBKD6OE7A7IHUQVWMY62W2ZBG2SGZVOOPVH"



    if __name__ == "__main__":
        StellarBot()


StellarBot
-------------
stellarbot -model allows you to trade
Links
-----
* Document: https://stellarbot-sdk.readthedocs.io
* Code: https://github.com/nguemechieu/stellarbot
* Examples: https://github.com/nguemechieu/stellarbot/tree/master/examples
* Issue tracker: https://github.com/nguemechieu/stellarbot/issues
* License: `Apache License 2.0 <https://github.com/stellarbot/blob/master/LICENSE>`_
* Releases: https://pypi.org/project/stellarbot/

Thank you to all the people who have already contributed to stellarbot!

.. _Stellar Horizon server: https://github.com/nguemechieu/stellar/go/tree/master/services/horizon