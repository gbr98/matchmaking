import random
import heapq
from typing import List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import time

@dataclass
class Player:
    """Represents a player in the matchmaking system"""
    id: int
    elo: int
    net_wins: int  # wins - losses from last 10 matches (-10 to +10)
    join_time: float
    
    def __repr__(self):
        return f"Player(id={self.id}, elo={self.elo}, net={self.net_wins:+d})"
    
    def __hash__(self):
        """Make Player hashable based on ID"""
        return hash(self.id)
    
    def __eq__(self, other):
        """Players are equal if they have the same ID"""
        if not isinstance(other, Player):
            return False
        return self.id == other.id


class MatchmakingSystem:
    """FPS Game Matchmaking System"""
    
    def __init__(self, max_elo_distance: int = 200):
        self.queue: List[Player] = []
        self.max_elo_distance = max_elo_distance
        self.current_time = 0.0
        self.match_count = 0
        self.player_id_counter = 0
        
    def add_player(self, elo: int, net_wins: int, arrival_time: float) -> Player:
        """Add a player to the queue"""
        player = Player(
            id=self.player_id_counter,
            elo=elo,
            net_wins=net_wins,
            join_time=arrival_time
        )
        self.player_id_counter += 1
        self.queue.append(player)
        self.current_time = arrival_time
        
        print(f"\n[Time {self.current_time:.2f}s] {player} joined queue")
        print(f"Queue size: {len(self.queue)}")
        
        return player
    
    def check_elo_compatibility(self, players: List[Player]) -> bool:
        """Check if all players are within max ELO distance"""
        if len(players) < 10:
            return False
        
        elos = [p.elo for p in players]
        elo_range = max(elos) - min(elos)
        
        return elo_range <= self.max_elo_distance
    
    def balance_teams(self, players: List[Player]) -> Tuple[List[Player], List[Player]]:
        """
        Balance teams to minimize the difference in average net_wins between teams.
        Uses a greedy approach with sorting.
        """
        # Sort players by net_wins (descending)
        sorted_players = sorted(players, key=lambda p: p.net_wins, reverse=True)
        
        team1 = []
        team2 = []
        sum1 = 0
        sum2 = 0
        
        # Greedy assignment: assign each player to the team with lower sum
        for player in sorted_players:
            if len(team1) < 5 and (len(team2) == 5 or sum1 <= sum2):
                team1.append(player)
                sum1 += player.net_wins
            else:
                team2.append(player)
                sum2 += player.net_wins
        
        return team1, team2
    
    def find_best_match(self) -> Optional[Tuple[List[Player], List[Player]]]:
        """
        Find the best 10 players for a match that satisfy all criteria.
        Returns two balanced teams or None if no match is possible.
        """
        if len(self.queue) < 10:
            return None
        
        # Sort queue by ELO for easier searching
        sorted_queue = sorted(self.queue, key=lambda p: p.elo)
        
        # Try different combinations of 10 players within ELO range
        best_match = None
        best_balance = float('inf')
        
        # Use sliding window approach to find players within ELO range
        for i in range(len(sorted_queue) - 9):
            candidate_players = []
            
            for j in range(i, len(sorted_queue)):
                if len(candidate_players) == 10:
                    break
                    
                if not candidate_players or \
                   (sorted_queue[j].elo - candidate_players[0].elo <= self.max_elo_distance):
                    candidate_players.append(sorted_queue[j])
            
            # Check if we have exactly 10 players within ELO range
            if len(candidate_players) == 10 and self.check_elo_compatibility(candidate_players):
                team1, team2 = self.balance_teams(candidate_players)
                
                # Calculate balance score
                avg1 = sum(p.net_wins for p in team1) / 5
                avg2 = sum(p.net_wins for p in team2) / 5
                balance_score = abs(avg1 - avg2)
                
                if balance_score < best_balance:
                    best_balance = balance_score
                    best_match = (team1, team2)
        
        return best_match
    
    def create_match(self) -> bool:
        """
        Attempt to create a match from the current queue.
        Returns True if a match was created, False otherwise.
        """
        match = self.find_best_match()
        
        if match is None:
            print(f"[Time {self.current_time:.2f}s] Cannot create match - criteria not met")
            return False
        
        team1, team2 = match
        self.match_count += 1
        
        # Remove matched players from queue
        matched_players = set(team1 + team2)
        self.queue = [p for p in self.queue if p not in matched_players]
        
        # Display match info
        print(f"\n{'='*70}")
        print(f"[Time {self.current_time:.2f}s] MATCH #{self.match_count} CREATED!")
        print(f"{'='*70}")
        
        self._display_team("TEAM 1", team1)
        self._display_team("TEAM 2", team2)
        
        print(f"\nRemaining in queue: {len(self.queue)}")
        print(f"{'='*70}\n")
        
        return True
    
    def _display_team(self, team_name: str, team: List[Player]):
        """Display team information"""
        print(f"\n{team_name}:")
        total_elo = 0
        total_net = 0
        
        for player in sorted(team, key=lambda p: p.elo, reverse=True):
            wait_time = self.current_time - player.join_time
            print(f"  {player} | Wait: {wait_time:.2f}s")
            total_elo += player.elo
            total_net += player.net_wins
        
        avg_elo = total_elo / len(team)
        avg_net = total_net / len(team)
        
        print(f"  Average ELO: {avg_elo:.1f}")
        print(f"  Average Net Wins: {avg_net:.2f}")
        print(f"  ELO Range: {min(p.elo for p in team)} - {max(p.elo for p in team)}")


def simulate_matchmaking(
    num_players: int = 50,
    max_time: float = 300.0,
    max_elo_distance: int = 200,
    seed: Optional[int] = None
):
    """
    Simulate a matchmaking system with players arriving at random times.
    
    Args:
        num_players: Number of players to simulate
        max_time: Maximum simulation time in seconds
        max_elo_distance: Maximum ELO difference allowed in a match
        seed: Random seed for reproducibility
    """
    if seed is not None:
        random.seed(seed)
    
    # Initialize matchmaking system
    mm_system = MatchmakingSystem(max_elo_distance=max_elo_distance)
    
    print("="*70)
    print("FPS MATCHMAKING SIMULATION")
    print("="*70)
    print(f"Players to simulate: {num_players}")
    print(f"Max ELO distance: {max_elo_distance}")
    print(f"Max simulation time: {max_time}s")
    print("="*70)
    
    # Generate player arrival events
    events = []
    for i in range(num_players):
        arrival_time = random.uniform(0, max_time)
        elo = random.randint(1000, 3000)
        net_wins = random.randint(-10, 10)
        events.append((arrival_time, elo, net_wins))
    
    # Sort events by arrival time
    events.sort(key=lambda x: x[0])
    
    # Process events
    for arrival_time, elo, net_wins in events:
        # Add player to queue
        mm_system.add_player(elo, net_wins, arrival_time)
        
        # Try to create a match
        mm_system.create_match()
    
    # Summary
    print("\n" + "="*70)
    print("SIMULATION SUMMARY")
    print("="*70)
    print(f"Total players: {num_players}")
    print(f"Matches created: {mm_system.match_count}")
    print(f"Players matched: {mm_system.match_count * 10}")
    print(f"Players still in queue: {len(mm_system.queue)}")
    print(f"Final simulation time: {mm_system.current_time:.2f}s")
    print("="*70)
    
    return mm_system


if __name__ == "__main__":
    
    player_join_rate = 50 # players per minute
    max_simulation_time = 240.0 # 3 minutes

    system = simulate_matchmaking(
        num_players=int(player_join_rate*max_simulation_time/60),
        max_time=max_simulation_time,
        max_elo_distance=200,
        seed=42
    )