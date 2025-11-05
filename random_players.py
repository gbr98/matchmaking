import random
from typing import Optional

from matchmaking import MatchmakingSystem

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