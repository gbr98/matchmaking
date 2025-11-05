# FPS Matchmaking System Simulator

A Python-based simulation of a competitive FPS (First-Person Shooter) game matchmaking system that creates balanced 5v5 matches based on player skill (ELO rating) and recent performance (win/loss streaks).

## 📋 Overview

This simulator models a real-time matchmaking queue where players arrive at random intervals and are matched into balanced teams when sufficient compatible players are available. The system prioritizes both skill-based matching and team balance to ensure fair and competitive matches.

## 🎮 Game Format

- **Match Size**: 10 players (5 vs 5)
- **Time-Based Simulation**: Players join the queue at random times
- **Dynamic Matching**: Matches are evaluated each time a new player joins

## 🎯 Matchmaking Rules and Assumptions

### Player Attributes

Each player has three key attributes:

1. **ELO Rating** (`elo`): 
   - Skill-based ranking score
   - Range: 1000 - 3000 (simulated)
   - Higher ELO indicates more skilled players

2. **Net Wins Score** (`net_wins`):
   - Recent performance indicator
   - Calculation: (Wins - Losses) from last 10 matches
   - Range: -10 to +10
   - Positive values indicate winning streaks
   - Negative values indicate losing streaks

3. **Join Time**: Timestamp when the player entered the queue

### Matching Criteria

A match can only be created when **ALL** of the following conditions are met:

#### 1. **Minimum Players Requirement**
- At least **10 players** must be in the queue

#### 2. **ELO Compatibility**
- All 10 players in a match must be within a maximum ELO distance
- Default: `max_elo_distance = 200`
- Calculation: `max(player_elo) - min(player_elo) ≤ max_elo_distance`
- **Purpose**: Ensures all players are of similar skill level

#### 3. **Team Balance (Net Wins)**
- Teams are balanced to minimize the difference in average net wins
- Players with high win streaks are paired with players who have losing streaks
- **Goal**: Each team's average net wins should be as close to 0 as possible
- **Purpose**: Prevents one-sided matches and promotes competitive balance

### Matchmaking Algorithm

The system uses a sophisticated multi-step approach:

1. **ELO-Based Candidate Selection**
   - Queue is sorted by ELO rating
   - Sliding window technique finds groups of 10 players within ELO range
   - Multiple candidate groups are evaluated

2. **Team Balancing (Greedy Algorithm)**
   - Players are sorted by net wins (descending)
   - Players are alternately assigned to teams to balance total net wins
   - High net win players are distributed across both teams

3. **Optimization**
   - System finds the combination with the best team balance
   - Balance score: `|avg_net_wins_team1 - avg_net_wins_team2|`
   - Lower balance score = more fair match

4. **Match Creation**
   - Best balanced match is selected and created
   - Matched players are removed from queue
   - Remaining players wait for the next match opportunity

## 🔧 System Behavior

### Player Addition (Simulation)

In the simulation, players are generated with:
- **Random arrival times**: Uniformly distributed over the simulation period
- **Random ELO ratings**: Between 1000 and 3000
- **Random net wins**: Between -10 and +10
- **Configurable player join rate**: Adjustable via parameters

### Match Evaluation Trigger

- The system checks for match creation **after each player joins** the queue
- No time-based polling or waiting periods
- Immediate matching when criteria are satisfied

### Queue Management

- **FIFO with Skill Priority**: Within ELO ranges, players are matched opportunistically
- Players remain in queue until matched
- No timeout or queue abandonment (in simulation)

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/fps-matchmaking-simulator.git
cd fps-matchmaking-simulator

# No external dependencies required (uses only Python standard library)
python matchmaking.py
```

## 🚀 Usage

### Basic Simulation

```python
from matchmaking import simulate_matchmaking

# Run simulation with default parameters
system = simulate_matchmaking(
    num_players=50,           # Total players to simulate
    max_time=300.0,           # Simulation time window (seconds)
    max_elo_distance=200,     # Maximum ELO spread in a match
    seed=42                   # Random seed for reproducibility
)
```

### Custom Configuration

```python
# Example: High player activity scenario
player_join_rate = 50  # players per minute
max_simulation_time = 240.0  # 4 minutes

system = simulate_matchmaking(
    num_players=int(player_join_rate * max_simulation_time / 60),
    max_time=max_simulation_time,
    max_elo_distance=200,
    seed=42
)
```

### Adjustable Parameters

| Parameter | Description | Default | Effect |
|-----------|-------------|---------|--------|
| `num_players` | Total players to generate | 50 | Higher = more matches |
| `max_time` | Simulation duration (seconds) | 300.0 | Spread of player arrivals |
| `max_elo_distance` | Max ELO spread allowed | 200 | Lower = stricter matching |
| `seed` | Random seed | None | Set for reproducible results |

## 📊 Output Example

```
======================================================================
FPS MATCHMAKING SIMULATION
======================================================================
Players to simulate: 200
Max ELO distance: 200
Max simulation time: 240.0s
======================================================================

[Time 1.23s] Player(id=0, elo=1523, net=+3) joined queue
Queue size: 1
[Time 1.23s] Cannot create match - criteria not met

[Time 2.45s] Player(id=1, elo=1678, net=-2) joined queue
Queue size: 2
[Time 2.45s] Cannot create match - criteria not met

... [more players join] ...

======================================================================
[Time 15.67s] MATCH #1 CREATED!
======================================================================

TEAM 1:
  Player(id=8, elo=1890, net=+7) | Wait: 2.34s
  Player(id=3, elo=1850, net=+4) | Wait: 8.12s
  Player(id=5, elo=1820, net=+1) | Wait: 5.67s
  Player(id=7, elo=1780, net=-2) | Wait: 3.45s
  Player(id=2, elo=1750, net=-5) | Wait: 9.23s
  Average ELO: 1818.0
  Average Net Wins: 1.00
  ELO Range: 1750 - 1890

TEAM 2:
  Player(id=9, elo=1880, net=+6) | Wait: 1.98s
  Player(id=4, elo=1840, net=+3) | Wait: 6.78s
  Player(id=6, elo=1810, net=0) | Wait: 4.56s
  Player(id=1, elo=1770, net=-3) | Wait: 11.45s
  Player(id=0, elo=1740, net=-6) | Wait: 14.44s
  Average ELO: 1808.0
  Average Net Wins: 0.00
  ELO Range: 1740 - 1880

Remaining in queue: 12
======================================================================

... [simulation continues] ...

======================================================================
SIMULATION SUMMARY
======================================================================
Total players: 200
Matches created: 18
Players matched: 180
Players still in queue: 20
Final simulation time: 240.00s
======================================================================
```

## 🏗️ Architecture

### Class Structure

```
Player (dataclass)
├── id: int
├── elo: int
├── net_wins: int
└── join_time: float

MatchmakingSystem
├── queue: List[Player]
├── max_elo_distance: int
├── current_time: float
├── match_count: int
└── Methods:
    ├── add_player()
    ├── check_elo_compatibility()
    ├── balance_teams()
    ├── find_best_match()
    └── create_match()
```

### Key Algorithms

- **ELO Matching**: Sliding window on sorted list - O(n²)
- **Team Balancing**: Greedy algorithm - O(n log n)
- **Queue Management**: List operations - O(n)

## 🎲 Simulation Assumptions

1. **Player Arrival**: Follows uniform random distribution over time window
2. **ELO Distribution**: Uniform between 1000-3000 (can be adjusted to normal distribution)
3. **Net Wins Distribution**: Uniform between -10 to +10
4. **No Player Abandonment**: Players stay in queue indefinitely
5. **Instant Matching**: No deliberate delays for finding "better" matches
6. **Deterministic Balancing**: Given the same players, always produces same team split

## 🔍 Technical Details

### Time Complexity
- **Adding Player**: O(1)
- **Finding Match**: O(n² × 10 log 10) where n = queue size
- **Creating Match**: O(n)

### Space Complexity
- O(n) where n = number of players in queue

## 📈 Possible Extensions

- [ ] Dynamic ELO distance based on wait time
- [ ] Priority for long-waiting players
- [ ] Role-based matchmaking (e.g., tank, support, DPS)
- [ ] Party/group matchmaking
- [ ] Regional/latency-based matching
- [ ] Time-of-day player distribution
- [ ] Match history and post-match ELO updates
- [ ] Visualization of match quality metrics

## 📝 License

MIT License - feel free to use and modify for your projects.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

---

**Note**: This is a simulation for educational and demonstration purposes. Real-world matchmaking systems may use more sophisticated algorithms, machine learning models, and infrastructure for handling concurrent requests.
