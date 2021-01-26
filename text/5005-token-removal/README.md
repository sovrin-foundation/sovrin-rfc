# 5005: Removal of Sovrin Token Plugin
- Author: [Alexandr Kolesov](alexander.kolesov@evernym.com), [Richard Esplin](mailto:richard.esplin@evernym.com), and [Renata Toktar](renata.toktar@evernym.com)
- Start Date: 2020-12-01

## Summary
[summary]: #summary

This proposal supersedes [SIP 5003: Sovrin Tokens](https://github.com/sovrin-foundation/sovrin-sip/tree/master/text/5003-sovrin-tokens) and details how to safely remove the experimental token from the Sovrin networks.

## Motivation
[motivation]: #motivation

In January of 2018, [Sovrin published a whitepaper explaining how a token could be used to allow unmediated public write access](https://sovrin.org/library/sovrin-protocol-and-token-white-paper/) to the ledger. In August of 2018, an experimental token was launched on the testing networks, and in November of 2019, the token code was added to Sovrin MainNet. [Large scale testing of the token occurred on the test networks](https://sovrin.org/sovrin-foundation-launches-test-token-for-decentralized-identity-network/) over this period. Due to regulatory hurdles, no token was ever minted on Sovrin MainNet. In June of 2020, Sovrin leadership formally adopted a resolution to not mint a token on Sovrin MainNet.

As explained in [SIP 5003](https://github.com/sovrin-foundation/sovrin-sip/tree/master/text/5003-sovrin-tokens), the Sovrin Token consists of a [plugin to an Indy ledger](https://github.com/sovrin-foundation/token-plugin), and a [plugin to the libindy client library](https://github.com/sovrin-foundation/libsovtoken). Neither code base has been maintained since March of 2020. The unmaintained ledger plugin which is currently installed is a risk to the health of the Sovrin Networks in some key ways:

* It has only been tested on Ubuntu 16.04, which is soon to be end-of-lifed. The plugin could break while upgrading the Sovrin Networks to newer versions of Ubuntu.
* It depends on the deprecated [Indy Crypto](https://github.com/hyperledger/indy-node), the predecessor to [Hyperledger Ursa](https://github.com/hyperledger/ursa). Indy Crypto has not received security updates or other improvements since October 2019. Because the rest of Indy uses Ursa, there is an additional risk of a dependency conflict.
* It’s build process depends on the Sovrin deployment of Jenkins for CI / CD, which has not been maintained since early 2020. It is likely that the unit tests and system tests won’t run.
* As development of [Hyperledger Indy](https://github.com/hyperledger/indy-node) continues, the Sovrin Token is not being updated to remain compatible.

Given that there are no plans to use this token code, there is no incentive to maintain it. This proposal explains how to safely remove the token from the Sovrin networks to avoid the risks presented by this unmaintained code.

## Tutorial
[tutorial]: #tutorial

Removing functionality from a distributed ledger has to be done carefully so as not to interrupt consensus, corrupt the ledger, or prevent history from being audited.

A standard deployment of Indy runs four ledgers:
* The pool ledger contains a list of all nodes in consensus.
* The domain ledger contains the identity objects.
* The config ledger contains ledger settings such as the authorization rules (auth_rules) that determine permissions.
* The audit ledger contains a root hash of each of the other ledgers for every transaction, thus making it possible to check the exact state of the other ledgers at any point in time to verify that the correct authorization rule was applied for each transaction on the domain ledger for any point in history.

The token plugin adds a fifth ledger which contains the token transactions. There are two common types of transactions on the token ledger: transfers of value, and the payment of fees. Fee payment is associated with write transaction on the domain ledger and depends on the state of the auth_rules on the config ledger.

Each Sovrin network should be separately considered:
* Sovrin MainNet is a permanent ledger for production use, and its history should never be lost or changed. It has an initialized token ledger with a hash in the audit table, but no token transactions.
* Sovrin StagingNet is a stable ledger for demonstration and testing purposes. It is widely used even though no guarantees are made about the history of StagingNet. It is intended to be reset regularly but has never been reset in practice. It has an initialized token ledger with a history of token transactions including two SET_FEE transactions. Tokens are available through the Sovrin Self Serve website.
* Sovrin BuilderNet is used to test new Indy releases for stability before the other Sovrin networks. It is useful for developers building solutions, but makes no guarantees about preserving history. BuilderNet was reset in June of 2020. It has an initialized token ledger and a history of only a few token transactions that include two SET_FEE transactions. Tokens are available through the Sovrin Self Serve website.

There are three facets to removing the token plugin:
1. Each network that has the token plugin installed will need to drop the token ledger while keeping the audit ledger consistent.
2. Networks that have recorded token transactions need to ensure the history of fees paid when writing to the domain ledger fulfills the auth_rules recorded on the config ledger at the time of the write.
3. The history of transfers of value will be unrecoverably lost when the token ledger is dropped during the plugin removal.


## Reference
[reference]: #reference

We have [introduced into Indy features to aid in the removal of the token plugin](https://github.com/hyperledger/indy-hipe/tree/master/text/0162-plugin-removal-helpers):
* frozen ledgers
* default fee handlers

With these new features, we can safely remove the token plugin from all Sovrin Networks. The process to remove the token will be very similar for each network.

Some work is required prior to removing the token from the networks:
* Remove the token functionality from [the Self Serve website](https://selfserve.sovrin.org).
* Build versions of the Sovrin.deb that
  * does not include the ledger plugin,
  * and has a migration script that drops the token ledger.


### Sovrin BuilderNet
Sovrin MainNet has the token plugin installed and a token ledger initialized, but has no token transactions. The removal process would proceed as follows:
1. Update the auth_rules to not reference fees as a method of ledger write authorization. (This is an optional step, as any fees mentioned in auth_rules will be ignored once the plugin is removed, but removing references to unused functionality will avoid confusion in the future.)
2. Upgrade the network to a version of Indy that supports frozen ledgers and default fee handlers. (This can probably be a rolling upgrade with no downtime.)
3. Send the LEDGERS_FREEZE transaction to freeze the token ledger.
4. Upgrade the network to a version of the Sovrin package that removes the token plugin.
5. Upgrade the network to a version of the Sovrin package that executes a migration script to drop the token ledger.

The last two steps could be combined, but are probably safer to perform independently.

### Sovrin StagingNet
Sovrin StagingNet is configured the same as Sovrin BuilderNet, but has a more extensive token history. The steps to remove the token plugin would be the same.

### Sovrin MainNet
Upgrading the Sovrin MainNet is easier because even though it has the token plugin installed and a token ledger initialized, it has no token transactions. The removal process follows the same instructions as for BuilderNet, but it only requires a version of Indy that supports frozen ledgers because there are no auth_rules that mention fees. The migration script should still be run to remove unused ledger files.


## Drawbacks
[drawbacks]: #drawbacks

There is a concern that removing the token code is dangerous and it is better to leave it in place. We consider the risks of leaving it in place to be greater than the effort required in testing that the removal is safe.

There is a possibility that Sovrin will reverse its previous decision and want to put at token back onto the networks. The dropped token ledgers can be recreated with different ledger IDs, but the hashes from the frozen ledgers will remain on the audit ledger for those networks.


## Rationale and alternatives
[alternatives]: #alternatives

We evaluated a number of alternatives before deciding to enhance Indy with frozen ledgers and default fee handlers.

### Maintaining a stub plugin

The most obvious approach to dealing with historical token transactions would be to simplify the token plugin. A minimal plugin could be a stub that simply returned the necessary ledger hashes; an unused token ledger would only need to return a constant hash, but the stub plugin could be enhanced to return a history of hashes if desired. A more complete solution would include the deprecated token transactions in the plugin. All of these approaches would require long term maintenance of the stub plugin.

### Move the token transactions to Indy

We can eliminate a token plugin by moving the token transactions to Indy as deprecated historical transactions. This would allow the history to be validated, and reduce the maintenance burden. But we don't want Indy to become a graveyard for every transaction type a plugin author defines, and we don't want to tie Indy to as specific payment mechanism.

### Truncate the transaction log that includes token transactions

We could roll the history of the ledger into a new genesis transaction that represents the current state without any token transactions. Though this is possible, it would require significant development and testing to ensure that we captured the state completely. It would also require a complicated roll out for everyone to adopt the new genesis transaction.

### Resetting StagingNet and BuilderNet

Removing the token from StagingNet and BuilderNet is complicated because there is a history of token transactions on those networks. Dropping the token ledger will remove the previous token transactions, but transactions that reference fees will still exist in the history of the domain ledger. The cleanest way to deal with that history would be to reset the networks to an empty state. BuilderNet was reset in June of 2020. StagingNet is considered a non-production network and it is expected that it would be regularly reset. But StagingNet is widely used and a reset would cause a significant disruption as developers would have to redeploy their demo credentials. For this reason, we concluded that we had to find a way to address historical token transactions without a network reset.

### Rewriting history on StagingNet and BuilderNet

Another way to remove the historical token transactions on StagingNet and BuilderNet would be to rewrite the history of those networks. This is something we have done before in our development environments, and it can be done safely without too much work. But there is a concern that tampering with history could erode confidence in the reliability of Sovrin if changing the history on the test networks is seen as setting a precedence for how we would deal with MainNet. Introducing the concept of a default fee handler seems a more appropriate solution.


## Prior art
[prior-art]: #prior-art

This work builds on the experience we had implementing the auth_rules and the audit ledgers.

During testing and development of Indy, we have experience rewriting history. Though it is not advised, we know it can be done safely.


## Unresolved questions
[unresolved]: #unresolved-questions

This proposal resolves all questions that have been raised in previous discussions about this topic.

Implementing the plan to remove the Sovrin token code from the Sovrin networks will require approval from the Sovrin TGB and Board of Trustees. Questions raised during that process will be incorporated into revisions of this proposal.
