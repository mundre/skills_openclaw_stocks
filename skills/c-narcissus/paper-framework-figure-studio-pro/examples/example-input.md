# Example Input

Design a main framework figure for this paper.

Problem:
Existing semi-supervised decentralized federated learning methods mainly strengthen consensus, but in personalized settings not all local differences are noise.

Method:
Each client has a shared branch and a personal branch. Unlabeled samples receive both a shared pseudo-label from neighbor-aware consensus and a personal pseudo-label from the local model. A sample-wise gate combines them. Shared structure is updated through fast decentralized collaboration, while personal structure is updated through slow local adaptation. Only shared branches are selectively aggregated, using weights based on quality, similarity, and personalization risk.

Goal of the figure:
Help reviewers understand why this method goes beyond consensus and preserves personalization while retaining collaborative gains.
