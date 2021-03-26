# 5005: Preliminary Security Review
- Author: Daniel Hardman
- Status Date: 2017-01-15

>*Note, March 2021: At the time this document was written, no formal security audits of Sovrin had been performed; this was a first effort. Since its writing, several formal reviews have been completed, a [crisis management plan](../5002-sovrin-crisis-management-plan/README.md) has been drafted, a [vulnerability reporting mechanism](../5004-credential-vulnerability-disclosure-template/README.md) has been activated, and so forth. So some of the information is stale, but the general concepts remain relevant.*

## Introduction
Sovrin must be trustably secure and private to deliver the value it claims. This is even more true of Sovrin than it is of most enterprise and consumer software, because the very heart of its behavior and feature set is cryptographic, and because its raison d’etre centers on security and privacy.

This preliminary security review is a sanity check on whether Sovrin achieves its mission correctly. It describes Sovrin’s security landscape at a high level, identifies a few areas worthy of special focus, and makes recommendations for best practice and further study.

Note the hedge word preliminary. The author has legitimate training and work experience in the cybersecurity space, but is not a deep expert, and does not claim to be. The purpose of the review is to inform developers about broad issues on the platform, help friendly community members to ask better questions, and provide a starting point for deeper investigation by a true expert.

## Key Assumptions
* The reader has a general understanding of Sovrin architecture, including concepts like the validator pool, observers, agents, verifiable and anonymous claims, stewards, trust anchors, governance, and so forth. (For background reading on these topics, we recommend The Technical Foundations of Sovrin and the Sovrin Glossary.)
* We’re reviewing an architecture and processes, but not doing pen-testing against the live system. This report is a prerequisite for Sovrin going live, so we must base our analysis on a theoretical profile.
* We will use Sovrin in its expected form/maturity during Q1 and Q2 2017 timeframe as the defined scope.

## General Security Landscape
Sovrin provides a global, distributed, public source of truth about identity in the form of an identity ledger. This ledger lets a participant discover a minimal but vital set of characteristics about a particular identity (as referenced by a DID): the identity’s current public verification key plus metadata such as a URL at which the identity may be contacted. Note that this data does not in any way name or describe a person; it simply makes secure communication with that identity possible. This ledger then provides a foundation for trusted interactions between identity owners. Digital signatures, zero-knowledge proofs, verifiable and anonymous verifiable claims, and entire frameworks of trust and reputation derive.

Sovrin is (or intends to be) secure by design. It deliberately limits attack surfaces, decentralizes, minimizes trusts in each entity in the ecosystem, handles data with care, and goes out of its way to enforce best practices. This is a laudable mindset; however, cybersecurity is littered with systems built on good principles but executed imperfectly, so thoughtful analysis is warranted.

Sovrin also aims to be private by design. It embodies many of the principles embodied by ambitious privacy regulations such as GDPR and HIPAA. It defaults to zero disclosure, and uses some very sophisticated cryptographic primitives to achieve this goal. It facilitates anonymity and pseudonymity. It structures interactions in a way that frustrates second- and third-party correlation.

This is not to say that it guarantees privacy, however--identity owners can choose to disclose information to the general public or to any subset of entities that they like. Besides, many entities that use Sovrin will be wholly or mostly public--universities, government institutions, and nonprofits come to mind.

For parties that seek privacy, Sovrin disclosure generates an audit trail and takes place in the context of a link contract--an immutable record about the timing, terms, and parties to the data sharing.

Despite this powerful privacy infrastructure, it is possible for Sovrin identity owners to make ill-advised choices about disclosure. These choices are revocable, but may still have consequences that persist longer than an identity owner would prefer. For example, a person could choose to disclose their birthdate to the whole world, and later revoke that disclosure. The data could be deleted from Sovrin so it could not be found in the future. However, the audit trail of the disclosure and subsequent revocation of something persists, and anybody who has persisted the disclosed data could retain it (though it might violate terms of use from the data owner to do so). Such cases are understood not to be a deficiency of Sovrin’s privacy or security story, but rather a reflection of the core truth that no system is immune from foolish human choices. Nonetheless, Sovrin is largely resilient to mistakes, and provides good safeguards.

## Primitives
Key building blocks of Sovrin are worthy of individual description and analysis, because they permeate and inform higher-level constructs. Sovrin inherits their strengths and weaknesses with respect to security and privacy.

### Programming Platform
Sovrin and the core components it depends upon are written in python (specifically, python 3.5+). Python serializes and sanitizes data, including json messages and json-ld verifiable claims. This means Sovrin could be vulnerable to any issues in the python interpreter or its networking, crypto, serialization, and unicode libraries. I consider it likely that minor python CVEs will emerge from time to time, but unlikely that this will be a serious vector for exploits--python is so widely used and well supported that any problems in its ecosystems should be quickly found and fixed. However, Sovrin may serialize or (fail to) sanitize data in ways that are unique; this subtopic is worthy of greater attention. Another focus for more research might be python’s http support, which may play a limited role in the ecosystem.

### Operating Systems and Infrastructure
The heart of Sovrin is its validator nodes, which run as daemons and maintain the integrity of the global, distributed ledger. Nodes may run either Linux (in various flavors) or Windows Server. The nodes are permissioned, meaning the community agrees to let a server function in that capacity using rules drafted and enacted by the Sovrin Foundation. This governance includes an agreement from the steward to conform to a list of industry-recognized best practices such as running a firewall with an aggressive security posture, disabling unnecessary services, and so forth. Stewards can choose not to conform, but in doing so they lose their standing as sanctioned validators. Stewards also agree to submit an OpenSCAP audit report of their node’s security posture, which is made available to the public. Only the sysadmin(s) in the sponsoring org for a validator node have root access on the node, not members of the Sovrin community.

Because each node is different in ownership, admin strategy, configuration, and patch level, it is  unlikely that attackers could make headway hacking at the general infrastructure level; there is too much variety. However, individual nodes may be vulnerable to a more targeted attack. See the section on malicious nodes below.

### Cryptography
Sovrin uses a protocol called CurveZMQ for transport-level, secure internal communication. CurveZMQ is an authentication and encryption protocol for ZeroMQ. Based on CurveCP and NaCl - fast, secure elliptic-curve crypto. The foundation of signatures and public/private key usage in Sovrin is elliptical curve cryptography built by experts and hardened by public inspection (libsodium, based on NaCl, by Daniel Bernstein et al.; see this report on the security profile of that technology). The specific elliptic curve that the system favors, Ed25519, provides 128 bits of security (equivalent to ~3000-bit RSA keys), which is very strong. Even stronger curves, such as Goldilocks, are compatible with the design and may be plugged in at some point in the future.

Some in the tech community have worried about standard cryptographic techniques being vulnerable to quantum computers. Today, this is a theoretical risk--no quantum computers have been built that can crack even modest encryption. Remediation for this risk--encryption algorithms resistant to quantum number crunching--is receiving attention in the academic, cryptographic community, but is not yet mature. Thus, Sovrin is neither less nor more vulnerable to quantum computing than other secure systems. However, its architectural friendliness to new curves may position it well to react as technology evolves.

In addition to core crypto, Sovrin provides privacy through a category of technologies called “anonymous credentials” or “anonymous claims.” These technologies let someone prove attributes about their identity (e.g., “I possess a valid driver’s license” or “I am over age 21”) as attested by an issuing authority, without identification (“here is my driver’s license number” or “here is my birthdate”). It is possible to prove such things without the issuer and verifying parties being able to collude and correlate, and it is also possible for issuers to revoke such credentials without eroding privacy. These technologies were not invented by the builders of Sovrin; they derive from the U-Prove mechanisms owned by Microsoft researchers, and the idemix (Identity Mixer) mechanisms developed by IBM research in Zurich. Specifically, Sovrin favors the Camenisch/Lyskyanskya digital signature scheme for anonymous credentials.

My opinion is that the cryptographic foundation of Sovrin is fundamentally sound; as with most systems, how it is invoked, and how keys are managed and communicated, is far more likely to be a gap in the armor than the algorithms. Sovrin’s behavior in these looser dimensions has been reviewed by genuine experts, and its open source makes all decisions transparent for public vetting as well--but this is certainly an area for further study.

### Devices and Agents
In the narrowest sense, Sovrin is a distributed ledger and the servers that expose it. However, the ecosystem will certainly include devices as well--mobile phones, tablets, desktops, and IoT things--that need to interact in secure ways. In addition, it is likely that over time the ecosystem will come to be permeated by agents--semi-autonomous chunks of software that improve usability by automating common and technical tasks.

These entities will not be policed by the Sovrin Foundation or the community--the “wild west” of today’s internet, where anything can be plugged in at any time, and the security posture of each participant is suspect, is the likely pattern. Each such entity represents an attack surface; many probably have access to at least some sensitive data and workflows.

Faced with such a landscape, Sovrin takes the sensible approach of enabling delegation with limited trust, providing redundancy and failsafes, and making it easy to do things right. Specific scenarios (e.g., a malicious agent) are discussed below. 

### Human Governance
Sovrin is more than just a technology; it is backed by the non-profit Sovrin Foundation, and there are processes and people tasked with helping it succeed. These people may be able to plug gaps in a security posture, and troubleshoot problems that arise. However, it may also be important to consider whether they constitute an attack surface for social engineering.

It is important to understand the scope of this human governance. Sovrin is truly free and truly open source; anybody can take the code and do what they like with it at any time. The Sovrin Foundation doesn’t own the ledger, or veto access to it. Rather, it provides an explicit “face” for the community behind the ledger, and guarantees that choices about the ecosystem take place in an open, collaborative, coherent, and auditable fashion. Working with the community, the foundation develops and codifies rules, explains their rationale, and encourages the community to play by them. Those who play by the rules get to call their ecosystem “Sovrin” and get to use the ledger and brand that relies on those rules; those who play by different rules can do so under whatever name and conventions they like. We say that Sovrin is “permissioned”--but it is the rules, not the Sovrin Foundation as benevolent arbiter, that give this permission.

A critique has been made that this governance militates against the freedom that ought to obtain. “Look at Ethereum and Bitcoin,” this reasoning urges; “they don’t have any governance.”

In fact, they do; it’s just less obvious. Bitcoin Core is studying how to react in case a hard fork is needed, and Ethereum has been through the process multiple times. The people who debate and then enact such changes are doing governance, and they are susceptible to social engineering just as Sovrin’s org is. If anything, Sovrin’s approach is safer because of its increased transparency.

### Data
As a distributed ledger, Sovrin has deep involvement in data--data with important security and privacy implications. Other data orbits around the ledger (e.g., on the devices and agents mentioned above.) Understanding the types of data involved, and how this data flows, is important to any security analysis.

Data “on the ledger” falls into four general categories:

1. Sequence numbers, timestamps, and transactional metadata.
2. Public keys and related public metadata about a DID.
3. Hashes plus links to canonical data values, documenting intentionally public data.
4. Hashes that provide proof-of-existence and tamper evidence for private data.

Category 1 is uninteresting from a security perspective; it is pure ledger recordkeeping.

Category 2 is the basis for deciding that an identity is authentic (not spoofed), for understanding whether and how an identity is self-sovereign, and for knowing how to talk to an identity’s authorized agent(s). It never contains secrets or PII, and need not be encrypted.

Category 3 is likewise cleartext. It might be used to record the mailing address of a government office, or standard json schemas for verifiable claims--anything of a public reference nature.

Category 4 is interesting. Suppose Alice contracts with Bob to sell a car, and seals the deal with handwritten paperwork that both parties sign. She then scans the contract and places a hash of it on the ledger. This ledger record could say something opaque, like “at timestamp X, identity XYZ records attribute FOO with a value that hashes to ABCDEF”. The ledger never holds the actual contract, never associates it with Alice’s or Bob’s name or other PII, and need not specify that the attribute is a contract. Later, if Alice wants to prove that the contract existed and was in force at a given time, she uses whatever out-of-band mechanism she likes to present the scan--but she can point to the ledger to prove that what she shares matches her id and the timestamp she asserts. No doctoring of the scanned image will have been possible, due to the hash.

Category 4 data can also encompass consent receipts or very complex hierarchies of data that need to be anchored to the ledger--and it can be used with any PII. Alice can record a hash of her PII on the ledger, if she likes--but she never records the PII itself there; the ledger can’t look up the value of a piece of info--it only proves existence and lack of tampering. The only entity who ever knows Alice’s PII is Alice, until she discloses it in whatever non-Sovrin manner she chooses.

Data “off the ledger” in the Sovrin ecosystem includes pairwise keys (the public key of another party, and the public and private key that the identity is known by, to that party); claims (assertions about attributes belonging to one’s own identity or the identity of others); audit trails; reputation; and much more. This data needs to be stored somewhere. Sovrin’s advice is to store true secrets (private keys) on the edge, under the direct control of their owners (e.g., on a mobile device). All workflows in Sovrin are friendly to this behavior; in particular, Sovrin agents and nodes are not considered “trusted third parties” in the cybersecurity sense. However, Sovrin itself cannot force people not to share passwords. Carelessness is always possible.

### Consensus
Ledger writes are performed by byzantine fault tolerant consensus (see plenum). This explicitly handles the possibility that multiple validators may be damaged, malicious, or colluding. Consensus controls ordering, the reputation of nodes and thus their promotion and demotion, and many other housekeeping items.

## Attack Surfaces
The following section outlines some scenarios where exploitation might be interesting. The outline is not ordered or prioritized, and it is not intended to be exhaustive. However, I believe that it captures a meaningful subset of the issues that need further analysis. A future security audit should review and expand this list, giving each item its own CVSS score.

* Checks and balances in Sovrin’s human governance
    * Paralyze SF through FUD (legal, market, hype) in the community
    * Paralyze SF by creating deadlocks in voting
    * Fake a vote from one or more stakeholders
    * Tamper with the record of a vote to change its outcome
    * Prevent stakeholders from voting to skew results
    * Skew data on which a vote is based
        * Governance says no more than X validators from a single country, but puppet institutions in another country undermine true pattern of control
        * Are human members vetted so all conflicts of interest are known?
    * Spear-phish Sovrin movers and shakers
    * Malicious or disgruntled insiders
        * Sysadmins on validators
        * Trust anchors
        * Members of Sovrin Foundation Board of Trustees
* Timing
    * Manipulate clock or timestamps
        * Trigger timeouts
        * Alter the order of transactions
        * Cause certain transactions to fail
        * Alter when a revocation takes effect
        * Influence reputation of nodes or agents
        * Reset system clock to game a scheduled task
    * Where do we not have timeouts, but should?
* Install, Deploy, and Upgrade
    * Package managers (docker, pypi, .deb, .rpm) that have known vulnerabilities
    * Packages that launch install scripts with hooks (e.g., postinst) that are susceptible to manipulation while running as root
    * CM tools that have known vulnerabilities (puppet, chef, ansible, salt)
    * Sovrin binaries that don’t match their hash/checksum
    * Escalation of privilege during deploy--running arbitrary code
    * Does Sovrin enforce enough security constraints on validator nodes? See draft tech governance rules.
* General tech stack
    * CVEs in python, libsodium, CurveZMQ, and so forth: does Sovrin have a mechanism to track and evaluate?
    * Does Sovrin have a plan to manage its own vulnerabilities? See this proposal.
* Governments
    * Demands for data are unlikely to apply to the ledger--but what about to agents?
    * Is Sovrin set up in such a way that locality-of-data regulations can be satisfied?
    * Do any export restrictions apply to Sovrin?
    * Governments can require less than perfect self-sovereignty of their citizens (e.g., access to citizen private keys); is this constraint hidable, or public? And can it cause transitive privacy erosion for people living outside that legal jurisdiction (e.g., by being able to inspect data from elsewhere, shared privately with the citizen?)
* DDoS
    * What mechanism does Sovrin use to prevent “spam identities”?
    * How does Sovrin prevent itself from being overwhelmed by simple read requests?
* Error handling and logging
    * Error handling paths that trigger undefined behavior
    * Leaked info via error messages or logs
    * Disk space exhaustion or system slowdown through excessive logging
* Data sanitization
    * Malformed verifiable claims
    * Malformed CurveZMQ messages
    * Malformed ledger transactions
    * Malformed DDOs
    * Malformed keys
* Gamed reputation
    * Sybil attacks with fake identities that bolster or destroy reputation for another identity in artificial ways
    * Transactions with artificial frequency
    * Transactions at artificial times
* Malicious or hacked validator
    * Correlation by IP address (GeoIP) of requester + time + identity of interest -- possibly strengthened by collusion with other malicious validators -- possibly defeated by observer fabric and/or mix networks?
    * DDoS on other validators (will be detected and punished fairly soon)
* Malicious issuer or relying party
    * Attempt to track use of its credentials by embedding a cookie in them (defeated by anon creds)
    * Subvert privacy by sharding revocation tails poorly
* Malicious or hacked Agent
    * Collude to correlate owner
    * Record activities too much
    * Run malicious plugins
    * Ruin owner reputation by obnoxious behavior
    * Holds secure backup from device, but shouldn’t be able to unlock; any leakage?
    * Pretend a device has been lost, locking out user
    * Pretend user adds another device
    * Steal data about a third party that is communicated as claims to the agent
    * Steal user config for/from external services (e.g., API keys for Facebook)
* Malicious, hacked, or lost mobile device
    * Leak sensitive data on secure vault (mitigate with biometrics, continuous reauth?)
* Key recovery
    * Social recovery via Shamir secret sharing: coopt N friends to take over an ID?
* Agencies
    * Correlate behaviors across many agents
    * Correlate requests for revocation tails
    * Hosting infrastructure as a vector to attack agents
    * Https MitM

## Recommendations
* Immediately implement the vulnerability management protocol that’s been proposed, including a bug bounty program to make Sovrin vulnerability reporting more community-friendly.
* Grow Sovrin’s security and privacy chops by inviting one or more cybersecurity experts and privacy hawks to participate in Sovrin leadership.
* Commission a formal legal audit of Sovrin to identify regulatory and accountability issues that Sovrin needs to understand. 
* Commission a formal security audit by a true subject matter expert. First deliverable: a vulnerability list like the list of attack surfaces above, where each item has a CVSS score so areas for deeper exploration can be prioritized.
* Develop a simple security training for various Sovrin audiences: developers, end users, IT sysadmins, and board members.
* Create a crisis management plan, in the event that a DDoS or other hack happens to the production system. This will significantly speed Sovrin’s response to the sorts of events that led to hard forks in Ethereum.
