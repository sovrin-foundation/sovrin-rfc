# 5002 Sovrin Crisis Management Plan
- Author: Daniel Hardman, Chair TGB (.md by Darrell O'Donnell)
- Start Date: 2018-08-15

## Summary

This document describes how Sovrin will respond to urgent crises such as a downed network, a corrupted ledger, etc. For 
immediate action items, see [Appendix A](#appendix-a---recommendations-for-immediate-action). For a step-by-step crisis checklist, see [Appendix B](#appendix-b---crisis-checklist).

## Rationale and Scope

No matter how robust Sovrin is, it is possible that the network could become unavailable or untrustworthy due to attack 
or disaster. In a crisis, we need to take speedy action. This mechanism should meet the same high standards for diffuse 
trust and for transparency that [normal Sovrin governance does](https://docs.google.com/document/d/18V1c0rOQYxNMleuV_2z7yQny0KdBnuDkWlN8DNUrioM/edit); we don’t want attackers to create a fake crisis and then 
manipulate us through it, and we don’t want to become unsafe in our responses.

The scope of concern here is separate from our Vulnerability Management Protocol; that is about triaging and responding 
to reported security concerns before a crisis, whereas this deals with unanticipated crises that are recognized only as 
they unfold. More specifically, this document focuses on crises that develop quickly and without warning—and that 
therefore cannot be managed with scheduled meetings during regular work hours. The time scale for these crises might be 
minutes or hours, or maybe a day or two—but not weeks or months.

## Human Stakeholders

Many people have a stake in a Sovrin network crisis. Our plan needs to think about how these people learn what’s happening, and how they contribute to a solution:

* Sovrin’s Board of Trustees
* Sovrin’s Technical Governance Board
* Sovrin’s stewards and the sysadmins who run their nodes
* The general Sovrin community (users, those who run observers, those who run agencies)
* The Hyperledger community, who will be running the same or similar code
* Journalists and other informed, external observers

## Sample Crisis Scenarios

The following scenarios are representative, not exhaustive; they should suggest commonalities (or uniquenesses) in circumstance, discovery, timing, and problem-solving. How long would each of these scenarios take to be detected and handled? What research and troubleshooting might they entail? What decisions would need to be proposed and approved, and by whom? Likelihood is assessed over the next 6-month period, considers only variants of a scenario that rise to the level of a Sovrin crisis, and is entirely subjective. As the Sovrin ecosystem matures, likelihoods will change.

| Description  | Likelihood  |
|---|---|
| War/conflict disrupts free flow of data due to legalities or chaos  | xx  |
| Earthquake/tsunami/typhoon impacts a broad geo, disrupting pool  | xx  |
| Huge DDoS attack makes pool unusable  | xxxx  |
| Failed network upgrade  | xxxxx  |
| Schism in Sovrin community breaks pool  | x  |
| Stealthy hack or latent exploit is discovered  | xxxx  |
| Sudden legal roadblock takes many nodes offline  | x  |
| Rogue node admin misbehaves, ruining network reputation  | xx  |

## General Remediations

Most potential responses to disaster scenarios will draw from a common playbook. We expect the following actions to figure in many responses:

* Research the extent of damage or intrusion
* Change which nodes are validators
* Apply a hotfix to nodes
* Reconfigure nodes (e.g., to change firewalls, to purge logs, etc)
* Revoke privileges (for sysadmins on a node, for orgs acting as trust anchors, etc)
* Issue a press release

## Prioritized Goals

We’d like our crisis management plan to prioritize some goals above others. Circumstances may require minor tweaks, but generally, the sequence (driven by relative urgency and importance) and the emphasis should look like this:

1. Understand the nature of the crisis, its ramifications, and its potential solutions well enough to act intelligently, neither jumping too fast nor waiting too long (see [Colin Powell’s 40-70 rule](http://theamericanceo.com/2013/07/02/5-responsibilities-of-a-ceo-make-good-decisions/) ).
1. Marshall a response that is coordinated, unambiguous, and trackable.
1. Limit the scope of the crisis (in time, in people, in systems) as much as possible.
1. Communicate with accurate and appropriate content, and with wise timing, to all stakeholders.
1. Do longer-term remediation after the crisis.
1. Guarantee an intelligent postmortem.


## Suggested Approach
The plan is built from the following ingredients:

1. Appoint a permanent owner of this plan.
1. dentify crisis detectors: Who should receive which signals that will help us detect the crisis? Prove that these signals work.
1. Define escalation and triage procedures.
1. Clarify decision-making protocols and ownership.
1. Practice.

### Permanent Owner of Plan

We recommend that the owner be the Technical Governance Board collectively. Here, ownership is about who evolves, maintains, monitors, reports on, and practices the details of the plan. The ultimate approver of the plan is the Board of Trustees and the larger Sovrin community.

### Crisis Detectors
Concerns about a developing network problem are reported to a Triage Committee consisting of TGB members, engineers, node sysadmins, paid support professionals that answer a phone day or night, etc. The design of this committee is an independent and evolving question not specified here, but in general it should have variety in expertise, access, geo, and legal jurisdiction. The full membership of the committee need not be available constantly, but at least one member of this committee should be. All members of this committee should have contact information for all other members. The Triage Committee should be accessible over various channels that have been publicized (email to [network-health@sovrin.org](mailto:network-health@sovrin.org) , Twitter, chat/IRC, phone?).

**The sysadmins** who operate nodes are responsible for their own machine’s health. The `[Provisional Trust Framework LINK TK]()` requires them to agree in principle to the goal of 99.9% uptime, though it does not enforce this standard. We assume that each sysadmin will run monitoring tools that detect anomalies in network, memory, disk, and CPU usage, and that troubling signals will be noticed quickly by humans. All sysadmins have a duty to report to the Triage Committee, quickly, concerns that might be broader than a single machine.

Any **member of the Sovrin community** can also raise a concern to the Triage Committee.

**Quality Assurance professionals** at companies that contribute to Sovrin’s codebases should run periodic probes of the live network; failure of these tests should also trigger an immediate report to the Triage Committee.

**The network itself** generates metrics of its performance. These metrics (or a subset thereof) are published to the world (giving the community an opportunity to note anomalies and ask questions); the metrics should also be monitored by automated processes capable of notifying the Triage Committee about concerns.

### Escalation and Triage Procedures

The Triage Committee reviews all incoming reports. The first step in triage is to record a ticket in Sovrin’s JIRA instance. A submitted report should be assigned to at least one Committee member for review. How this assignment takes place should be decided by the Committee. `[TK Recommendation?]` A report that is reviewed may either be escalated for full Committee discussion, or ignored.

If a report is escalated to the full Committee, the Committee convenes a real-time discussion (e.g., using teleconference software). `[TK Again, need specifics]` The Committee either de-escalates (if the issue is analyzed as a non-crisis), plans and acts (if no fact-finding is necessary), or chooses a Lead Investigator on the issue and decides how to work the problem. In the latter case, it plans a follow-up conversation at which decisions will be made, once the Lead Investigator reports.

Any time the Triage Committee meets, the full meeting is recorded. These meetings are later published, but publication can wait until the crisis is over. Also, the Triage Committee reports all decisions (ignore, escalate + \[de-escalate | act | investigate + \[act | de-escalate\]\]) to Sovrin’s TGB no later than immediately upon concluding their decision. Any escalated issues are also reported to Sovrin’s Board of Trustees within 24 hours--immediately if the action plan requires legal, PR, or other administrative support.

The Triage Committee is primarily an “analyze and recommend” group. Actions such as issuing a press release, changing the status of a validator node, applying an urgent hotfix, and so forth often require others to approve and/or implement. Therefore, the Triage Committee will often reach out to stakeholders to coordinate.

The sysadmins of validator nodes, the Sovrin TGB, and the Sovrin Board of Trustees agree to be notified in real time (e.g., by phone call in the middle of the night) if the Triage Committee reaches consensus that such escalation is required.

### Ownership

In general, the Board of Trustees must approve any action related to technical management of the Sovrin network, although day-to-day decisions have been delegated to the Technical Governance Board. The Board of Trustees also controls budget and Sovrin’s public relations strategy. Thus, the Board is the ultimate owner of collective governance choices.

The stewards own their nodes. Any individual node owner may do whatever they like with their node, although acting out of harmony with a quorum of their peers may cause them to lose validator/steward status.

### Practice
We should identify a crisis scenario and practice its entire lifecycle. For example, we could postulate that a DDoS attack targets the Sovrin network and is able to flood it with spurious identity creation requests. The network has no bandwidth for other users; it is fully consumed with processing these useless transactions.

The rehearsal should begin with someone reporting the problem over one of the channels that the Triage Committee operates. Preferably, this should happen at a time that the Committee does not know in advance. If things go well, the Committee will then assign the issue, review it, triage it, and create and execute a plan to solve the problem.

One rehearsal will undoubtedly teach us a lot--but rehearsing periodically will be even more beneficial.

## Appendix A - Recommendations for Immediate Action
[appendixa]: #appendixa

1. ***Staff the Triage Committee.***
1. Implement a “**last known good version**” of software as part of the upgrade protocol, such that a fallback version of the software is known and available to (e.g., predownloaded by) all parties before an upgrade proceeds.
1. Develop and practice a (non-automated) **methodology for hotfixing nodes**.
1. Engage a cybersecurity Incident Response team to be on call for the network.
1. Create a discretionary budget that the Triage Committee can spend without further approval (e.g., $5k). This would allow certain solutions to be triggered far more quickly.
1. ***Create a decision-maker/approval matrix*** that shows who needs to be contacted about certain types of decisions. Who can speak to the press? Who can call a lawyer in the US or Europe or Asia? Who can approve expenditures > $5k? Who can approve suspending the entire network for 30 secs? For 30 min? Who can approve forking the code?
1. Create a “ledger explorer” tool that facilitates low-level dumping of ledger records, for forensic purposes.
1. Implement mechanisms that allow validator nodes to whitelist one another, such that all consensus-related traffic occurs between IP addresses and ports that are explicitly allowed, where all other traffic is dropped. Importantly, this mechanism needs to adjust firewall config in realtime as machines are added to or removed from the consensus pool on the ledger.
1. **Re-analyze the auto-blacklist feature** (where nodes get negative reputation if they cease to respond) for safety. In scenarios where a service interruption happens for innocent reasons (a typhoon, earthquake, legal takedown order, or DDoS against a single node), we do not want the rest of the network to blacklist too quickly. (Or perhaps we are willing to tolerate a quick blacklist, as long as recovery of reputation is straightforward.)
1. ***Cultivate a PR contact that can help manage press releases***. (Possibly this could be done by the marketing folks for Sovrin or Evernym?)
1. ***Practice at least one crisis scenario.***
1. Schedule a refresh of this plan at least quarterly.


## Appendix B - Crisis Checklist

1. Understand the nature of the crisis, its ramifications, and its potential solutions well enough to act intelligently,
 neither jumping too fast nor waiting too long (see Colin Powell’s 40-70 rule).
Record the meeting so we are transparent.
   1. Do we understand both the root cause(s) and the proximate cause(s) of the crisis? What is our confidence in this 
   assessment?
   1. Is there any contradictory evidence?
   1. What other key questions need to be answered?
   1. Do we need additional contingency plans? If so, for which scenarios? How will we know when such a plan should be 
   triggered, and who will work such plans?
   1. To what extent could/should research be parallelized with initial response?
   1. Who knows about it? Who should know, and what should they be told? Do we need to manage how news spreads?
   1. Can we change the severity of the problem or the urgency or expense of the solution, such that the problem is 
   less of a crisis?
   1. How do different choices change our risk profile, now and in the future?
   1. Who will pay for research and/or remediation work? Do we have budget?
   1. Who outside the Triage Committee has decision-making authority that we need?
   1. What is the disposition of the Triage Committee itself during this crisis? Who’s unreachable, who’s wide awake, 
   who’s supposed to be asleep? What additional resources in the TGB, the BoT, or other friends can we call upon? How 
   about professionals we can hire to help?
1. Marshall a response that is coordinated, unambiguous, and trackable.
   1. Are we going to de-escalate (no longer a crisis), investigate further, or act now?
   1. Communicate immediately to the TGB. If we don’t de-escalate, communicate to the BoT as well. (These 
   communications don’t need to be wake-someone-up-in-the-middle-of-the-night notifications, unless people 
   from these groups are required to work the problem in real time.)
   1. Who from the Triage Committee is going to be the Lead Investigator of this particular issue? When and how will 
   s/he report back, and what will others be doing in the meantime? Make sure that the answer to this question is 
   known to the TGB and the BoT.
1. Work the problem.
   1. Transition out of crisis mode if the immediate urgency decreases.
   1. Record progress in the JIRA ticket.
   1. Schedule an Executive Briefing for the BoT and/or the TGB as the crisis winds down.
   1. Issue public status reports under the direction of marketing professionals.
1. After the immediate crisis, address long-term needs.
   1. Hold a formal post-mortem.
   1. Schedule appropriate fixes that may be better (superseding kludges) or too expensive for the short term.
   1. Plan ways to monitor progress over this longer horizon.


