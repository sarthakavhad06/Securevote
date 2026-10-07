// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @notice Educational single-election voting contract for a local Ganache network.
contract Voting {
    struct Candidate { string name; uint256 voteCount; }
    Candidate[] public candidates;
    mapping(address => bool) public hasVoted;
    event VoteCast(address indexed voter, uint256 indexed candidateId);

    constructor(string[] memory names) {
        require(names.length >= 2, "At least two candidates required");
        for (uint256 i = 0; i < names.length; i++) {
            require(bytes(names[i]).length > 0, "Candidate name is empty");
            candidates.push(Candidate({name: names[i], voteCount: 0}));
        }
    }

    function candidateCount() external view returns (uint256) { return candidates.length; }
    function getVotes(uint256 candidateId) external view returns (uint256) {
        require(candidateId < candidates.length, "Invalid candidate");
        return candidates[candidateId].voteCount;
    }
    function vote(uint256 candidateId) external {
        require(candidateId < candidates.length, "Invalid candidate");
        require(!hasVoted[msg.sender], "Account already voted");
        hasVoted[msg.sender] = true;
        candidates[candidateId].voteCount += 1;
        emit VoteCast(msg.sender, candidateId);
    }
}
