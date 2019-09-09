# 5003: Sovrin Tokens
- Author: [Brent Zundel](brent.zundel@evernym.com)
- Start Date: 2019-03-26

## Summary
[summary]: #summary

This SIP introduces a Sovrin token, for use as a payment mechanism on the Sovrin
Ledger. It describes new transactions for creating and transferring tokens, as
well as the data structures and protocols around recording token transactions.

## Motivation
[motivation]: #motivation

### To protect the Sovrin Ledger
The Sovrin instantiation of Hyperledger Indy, or the Sovrin Ledger, is a
public-permissioned distributed ledger.
- It is public, in that anyone should be able to read from the ledger.
- It is permissioned, in that only a select set of validator nodes may write to
the ledger.

In order for a party to submit a request to the validators for a transaction
to be written to the ledger, the party must either hold a certain role known as
a Trust Anchor, or process the transaction request through a Trust Anchor. This
role is granted to validators and stewards of the Sovrin Ledger, and other
"trusted" entities. The purpose of the Trust Anchor role is to protect the
ledger from malicious transaction requests.

Changing this to allow anyone to submit transactions to the validators is
problematic. If anyone with a network connection may submit transaction requests
to validators, it is theoretically possible for anyone to overwhelm a validator
with too many transaction requests, and overwhelm the validator pool as they
work to consider the load of transaction requests. For this reason, transaction
requests pass through a Trust Anchor.

The drawback of this protection mechanism is that it makes the ledger
less accessible to anyone outside of the trusted circle. If the Sovrin Ledger is
truly to be a global public utility, the ability to request that a transaction
be written to the ledger should be available to anyone. This is the primary
motivation for introducing a token as a payment mechanism for transaction
requests.

If submitting a transaction request to a validator did not require a party to be
trusted, but instead required a small fee, this would provide an economic
disincentive to abuse the ledger while allowing anyone to submit transaction
requests.

### To support the maintenance and development of the Sovrin Ledger
As the token is used by parties to pay for transaction requests, they will
accumulate on the ledger as transaction fees. These tokens could be collected
and sold, with the proceeds going to support maintenance of the Sovrin Ledger
and the development of improvements to the ledger and the Sovrin ecosystem.

## Tutorial
[tutorial]: #tutorial

### Introduction
The Sovrin token is a bitcoin-style cybercoin that is native to the Sovrin
ledger. Consensus around valid token transactions occurs with the same pool of
validator nodes as every other transaction. Fees that accompany transactions are
processed atomically with those transactions, so they fail or succeed together.

The infrastructure for value transfer on the Sovrin ledger consists of a
payments sub-ledger (much like the domain and pool sub-ledgers) that records
payment transactions. Setting fees writes a fee schedule to the existing config
sub-ledger. There is also a cache of unspent transaction outputs, or
_UTXOs_.

### Denomination
- Each Sovrin token consists of 1 x 10<sup>9</sup> sovatoms.
- Sovatoms are the smallest unit and are not further divisible.
- All `amount` fields in payment APIs are denominated in sovatoms.
  - This allows transaction calculations to be performed on integers.
- 1 x 10<sup>10</sup> (10 billion) Sovrin tokens may be minted,
and all of the resulting 1 x 10<sup>19</sup> sovatoms may be stored
using a 64-bit integer.

### The Payment Ledger
The payment ledger makes use of Plenum to come to consensus about payment
transactions. The validation of these transactions includes:
- double-spend checking,
- verification of payment signatures,
- and enforcing the equality of input and output amounts.

After using Plenum to come to consensus, payment and fee transactions are
recorded on the payment ledger. The fee schedule is recorded on the config ledger.

The transaction types handled by the payment ledger are:
- **MINT_PUBLIC** - Creates Sovrin tokens as a transaction on the payment ledger.
The minting of tokens requires the signatures of multiple trustees.
- **XFER_PUBLIC** - Transfers Sovrin tokens from a set of input payment
addresses to a set of output payment addresses. This transaction is recorded on
the payment ledger.
- **GET_UTXO** - Queries the payment ledger for unspent transactions held
by a payment address.
- **SET_FEES** - Sets the fee schedule for ledger transactions, including
transactions recorded on other sub-ledgers. This transaction is recorded on the
config ledger. The setting of fees requires the signatures of multiple trustees.
- **GET_FEES** - Queries the config ledger to retrieve the current fee schedule.
- **FEES** - Attaches a fee payment, according to the fee schedule, to
transactions requests. The fee payment is recorded on the payment ledger. This
is never an independent transaction, but always attached to the primary
transaction request for which fees are being paid.

### Payment Address
A *payment address* is a string with the structure: <code>pay:sov:\<Ed25519
Verification Key>\<Checksum></code>. An address is the identifier for some
number of UTXOs. Each UTXO contains some number of tokens.

A *payment key* is the Ed25519 signing key that corresponds to the verification
key in the payment address. In order for a value transfer to be authorized,
it must be signed by the payment key for for each payment address used as
an input in the transaction.

#### UTXOs

A payment address is associated on the ledger with a number of unspent
transaction outputs (UTXOs). A UTXO is identified by the payment address it is
associated with and the sequence number of the transaction in which it was
created. For example, a UTXO for address pay:sov:12345 that was created during
transaction number 293, would be identified as pay:sov:12345:293

Whenever a token transaction is recorded on the payment ledger, the result is
the spending or creation of some number of UTXOs. When a UTXO is used as input
in a payment transaction, the UTXO is spent along with all of the tokens
contained there. The output of a payment transaction is a set of new UTXOs.

Note: If a sender has a UTXO that contains 100 tokens and wishes to send 60
tokens to a recipient, the sender must specify a payment address at which they
wish to receive the remaining balance of tokens from the spent UTXO.

For example:
1. A **MINT** transaction creates 100 tokens for address pay:sov:12345. The
**MINT** transaction is recorded on the ledger at sequence number 52.
   1. These tokens exist on the ledger as a single UTXO that is associated with
   address pay:sov:12345 and sequence number 52.
1. A **XFER_PUBLIC** transaction transfers 60 tokens from address pay:sov:12345
to address pay:sov:98765. The **XFER_PUBLIC** transaction is recorded on the
ledger at sequence number 69.
   1. This transaction spends the UTXO pay:sov:12345:52 and creates two new
   UTXOs, one for the recipient, and one for the remaining tokens.
      1. UTXO pay:sov:98765:69 that contains 60 tokens for the recipient.
      1. UTXO pay:sov:12345:69 that contains 40 tokens as change for the sender.

      Note: The change UTXO does not need to use the same payment address as an
      input UTXO.
   1. The **XFER_PUBLIC** transaction is valid because:
      1. pay:sov:12345:52 had not previously been spent.
      1. The transaction was signed by the payment key for pay:sov:12345.
      1. The transaction input from pay:sov:12345:52 (100 tokens) was equal to
      the output in pay:sov:98765:69 and pay:sov:12345:69 (60 + 40 tokens).

### UTXO Cache
The UTXO cache is used to facilitate the efficient answering of payment ledger
queries. This cache is used to answer the following questions:
1. Given a UTXO, has the UTXO been spent and what is its associated value?
   - Each UTXO is prepended with a "0" and is encoded to create a key. This key
    is added to the cache. The value associated with this key is the number of
    tokens held by that address at that sequence number.
    - For example: if the UTXO for payment address pay:sov:24601 at sequence
    number 557 has 10 tokens, the key would be 0:pay:sov:24601:557 and the value
    would be 10.
1. Given an address, what are all the UTXOs?
   - An address is prepended with "1" and then encoded to create a key which is
   added to the cache. The value associated with this key is a
   delimiter-separated list of the sequence numbers of the transactions for
   which the address has unspent amounts.
   - For example: if the address pay:sov:8675309 was sent tokens in transactions
   with sequence numbers 129, 455, and 1090, and none of the tokens has been
   spent, then the key would be 1:pay:sov:8675309 and the value would be
   129:455:1090.

The UTXO cache is updated whenever a payment transaction is written to the
ledger.

### Transaction Fees
The primary purpose of transaction fees is to reduce spam and to introduce a
financial disincentive for DDoS and similar attacks. Sovrin can offer open
access by setting the fees for ledger transactions high enough to discourage
abuse of the network while at the same time keeping fees as low as possible.

The fees are set by a quorum of Sovrin trustees, and should be adjusted to react
to changes in the value of the Sovrin token. The transactions for which fees are
collected are the transactions that require the most work from validator nodes,
namely requests to write to the Sovrin ledger.

These transactions are:
- NYM
- ATTRIB
- SCHEMA
- CRED_DEF
- REVOC_REG_DEF
- REVOC_REG_ENTRY
- XFER_PUBLIC

More write transactions may be added in the future.

### Incorporation with Hyperledger Indy
Hyperledger Indy provides the code base for the Sovrin Ledger. This code base
may be extended with plugins. Ledger plugins add new transactions and
sub-ledgers to the transactions and sub-ledgers already defined by Hyperledger
Indy.

#### Ledger Plugins
This process for adding plugins to Hyperledger Indy is explained in
[Hyperledger's indy-plenum repository](https://github.com/hyperledger/indy-plenum/blob/master/docs/source/plugins.md)

Plugins allow for new transactions to be added to an instantiation of Indy,
without requiring changes to the core codebase. New sub-ledgers may also be
defined using these plugins. A sub-ledger is where the new transactions may be
stored.

Two ledger plugins are proposed in this document:
- A Token plugin, which adds a payments sub-ledger and the transactions:
   - **MINT_PUBLIC**
   - **XFER_PUBLIC**
   - **GET_UTXO**
- A Fees plugin, which adds these transactions to the payments sub-ledger
mentioned above:
   - **GET_FEES**
   - **SET_FEES**
   - **FEES**

Note: While the Token plugin and the accompanying payment sub-ledger may be
used without the Fees plugin, the Fees plugin depends on the Token plugin.

#### Indy-SDK Payments API Plugin
The Indy-SDK payments API comes with a default payment handler plugin called
[LibNullPay](https://github.com/hyperledger/indy-sdk/blob/master/libnullpay/README.md).
LibNullPay allows for a "null" token to be used with the payments API. the
"null" token transactions are dummy transactions. They are not stored on a
ledger and do not initiate consensus.

The payments API allows for other payment handler plugins to be initialized.
An Indy-SDK payments API compatible payments handler is proposed in this
document:
- LibSovToken, which handles Sovrin token payment functionality through the
Indy-SDK payments API for the Token and Fees ledger plugins and produces properly
formatted and signed transaction requests for each of the new transactions
listed above. LibSovToken also parses the transaction responses from the new
ledger plugins through the Indy-SDK payments API.


#### NOTE
With the recent introduction of
[AUTH_RULE](https://github.com/hyperledger/indy-node/blob/master/docs/source/transactions.md#auth_rule)
transactions in Hyperledger Indy, and the capability of creating an
authorization table on the config ledger, the way that the Fees plugin will
create and query a fee schedule may change. This SIP reflects the way the Fees
plugin and the associated payments API are currently built. Any proposed
changes to this process will be recorded in a supplemental SIP.

## Reference
[reference]: #reference

Work on the Token and Fees ledger plugins that are proposed to be added to
Sovrin's instantiation of Hyperledger Indy may be found in the
[Sovrin token-plugin repo](https://github.com/sovrin-foundation/token-plugin).

Documentation for the proper format of transaction requests and transaction
responses for the Token plugin, specifically for the **MINT_PUBLIC**,
**XFER_PUBLIC**, and **GET_UTXO** transactions can be found here:
[Ledger Token Transactions.](https://github.com/sovrin-foundation/token-plugin/tree/master/sovtoken/doc/Interface)

Documentation for the proper format of transaction requests and transaction
responses for the Fees plugin, specifically for the **SET_FEES**, **GET_FEES**,
and **FEES** transactions can be found here:
[Ledger Fee Transactions.](https://github.com/sovrin-foundation/token-plugin/tree/master/sovtokenfees/doc/Interface)

Documentation for the Indy-SDK payments API and how to use it may be found here:
[Indy SDK Payments API.](https://github.com/hyperledger/indy-sdk/tree/master/docs/design/004-payment-interface)

The structure of the inputs and outputs of the LibSovToken payment handler
plugin for the Indy-SDK payments API are documented here:
[Sovrin Token specific data structures.](https://github.com/sovrin-foundation/libsovtoken/blob/master/doc/data_structures.md)

## Drawbacks
[drawbacks]: #drawbacks

### Undesired Speculation
The intention of the Sovrin token is to enable a more public way to submit
transaction requests without compromising the security and performance of the
Sovrin ledger validator nodes. However, the introduction of the Sovrin token
may be incorrectly viewed as an invitation for speculators to purchase Sovrin
tokens, even though they have no intention of making use of the utility provided
by Sovrin tokens, i.e. writing to the Sovrin ledger.

This speculative action may cause the value of the Sovrin token to fluctuate,
requiring a quick response from the Sovrin stewards in adjusting the fee
schedule for ledger transactions so that fees remain reasonable.

### Additional Costs
Moving from a Trust Anchor model, where trusted entities may submit write
transaction to the ledger, to a Token model, where submitting a write
transaction requires the payment of fees denominated in Sovrin tokens, will
introduce new costs to those who are currently trusted entities.

### Load on the Ledger
Adding new transactions potentially increases load on the validator nodes and
the size of the ledger. Each request for a write transaction now also requires
a **FEE** transaction, effectively doubling the computational load on each
validator for write transactions.

A **FEE** transaction always accompanies some other primary transaction. The two
transactions must be atomic:
- the primary transaction should not be processed if the **FEE** transaction
fails,
- the **FEE** transaction should not be written if the primary transaction
fails.

Recording the **FEE** transaction on the payment sub-ledger and the primary
transaction on another sub-ledger may require that the two sub-ledgers be
synchronized in some way. This may also cause difficulties during catchup (when
a validator node updates its state to be current with the rest of the validator
pool).

If the Sovrin token begins to be commonly used for other payments besides fees,
there will be additional load on the validator nodes as they come to consensus
on the **XFER_PUBLIC** transactions.

## Rationale and alternatives
[alternatives]: #alternatives

This design for a Sovrin token described here is simple. It is based on the UTXO
model for transactions found in [bitcoin](https://bitcoin.org/en/bitcoin-paper),
which simplifies validity checking for payment transactions.

Other designs that were considered were [zerocoin](http://zerocoin.org/) and
[zcash](https://z.cash/). These were not chosen due to the complexity of
modifying them for Hyperledger Indy and out of an abundance of caution around
possible regulatory issues surrounding private transactions, Sovrin stewards,
and validators.

If the Sovrin token is not introduced, the existing system of Trust Anchor-based
write requests will continue and the Sovrin ledger will be less of a public
utility than it otherwise could be.

## Prior art
[prior-art]: #prior-art

There are many examples of tokens and other cybercoins in production today, a
few of these were linked to above. In some of these systems, such as bitcoin
and zcash, the tokens are used as a medium of exchange or a store of value.
In other systems the tokens are used to access some resource. In
[ethereum](https://www.ethereum.org/), the cybercoins are used to pay for
distributed computation. In [filecoin](https://filecoin.io/), the tokens are
used to pay for distributed storage.

The Sovrin token follows the bitcoin model of addresses and UTXOs, but is more
similar to ethereum or filecoin, in that the token is used to pay for access to
a resource. The resource in the case of the Sovrin token, is the Sovrin ledger,
which serves as a verifiable data registry for decentralized identifiers,
verifiable credential schemas, and the public keys and other objects needed for
verifying those credentials.

The author is not aware of any other token that is used for this purpose.

## Unresolved questions
[unresolved]: #unresolved-questions

There are a number of questions that remain unanswered, some of which may be
outside of the scope of this effort:
- How will the Sovrin token and the payment ledger affect the catchup process
for validator nodes?
- What impact will the introduction of fees have on the time it takes to process
transactions, and how can this impact be mitigated?
- Should the token and fees plugins be merged into a single plugin?
- Is Plenum too "heavy" for token transactions?
   - Would it even be possible to use a different consensus algorithm for the payment
   sub-ledger?
- Are there GDPR and privacy issues that need to be addressed?
- How could the adjustment of the fee schedule in response to changes in the
value of the token be automated?
- Should the payment of fees be the only way to submit transaction requests?
   - Would a hybrid model work that combines tokens and trust anchors?
