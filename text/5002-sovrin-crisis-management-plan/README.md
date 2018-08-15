- Name: Sovrin Crisis Management Plan
- Author: Darrell O'Donnell
- Start Date: 2018-08-15
- PR: -
- Jira Issue: --

# Summary
[summary]: #summary

This document describes how Sovrin will respond to urgent crises such as a downed network, a corrupted ledger, etc. For 
immediate action items, see Appendix A. For a step-by-step crisis checklist, see Appendix B.

# Rationale and Scope
[rationale]: #rationale

No matter how robust Sovrin is, it is possible that the network could become unavailable or untrustworthy due to attack 
or disaster. In a crisis, we need to take speedy action. This mechanism should meet the same high standards for diffuse 
trust and for transparency that normal Sovrin governance does; we don’t want attackers to create a fake crisis and then 
manipulate us through it, and we don’t want to become unsafe in our responses.

The scope of concern here is separate from our Vulnerability Management Protocol; that is about triaging and responding 
to reported security concerns before a crisis, whereas this deals with unanticipated crises that are recognized only as 
they unfold. More specifically, this document focuses on crises that develop quickly and without warning—and that 
therefore cannot be managed with scheduled meetings during regular work hours. The time scale for these crises might be 
minutes or hours, or maybe a day or two—but not weeks or months.


# Tutorial 
[tutorial]: #tutorial

#

# Reference
[reference]: #reference

Provide guidance for implementers, procedures to inform testing,
interface definitions, formal function prototypes, error codes,
diagrams, and other technical details that might be looked up.
Strive to guarantee that:

- Interactions with other features are clear.
- Implementation trajectory is well defined.
- Corner cases are dissected by example.

# Drawbacks
[drawbacks]: #drawbacks

Why should we *not* do this?

# Rationale and alternatives
[alternatives]: #alternatives

- Why is this design the best in the space of possible designs?
- What other designs have been considered and what is the rationale for not
choosing them?
- What is the impact of not doing this?

# Prior art
[prior-art]: #prior-art

Discuss prior art, both the good and the bad, in relation to this proposal.
A few examples of what this can include are:

- Does this feature exist in other SSI ecosystems and what experience have
their community had?
- For other teams: What lessons can we learn from other attempts?
- Papers: Are there any published papers or great posts that discuss this?
If you have some relevant papers to refer to, this can serve as a more detailed
theoretical background.

This section is intended to encourage you as an author to think about the
lessons from other implementers, provide readers of your proposal with a
fuller picture. If there is no prior art, that is fine - your ideas are
interesting to us whether they are brand new or if it is an adaptation
from other communities.

Note that while precedent set by other communities is some motivation, it
does not on its own motivate an enhancement proposal here. Please also take
into consideration that Indy sometimes intentionally diverges from common
identity features.

# Appendix B - Crisis Checklist #

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


