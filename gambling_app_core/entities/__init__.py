"""
Entity models for the Gambling Simulation System.
Data Transfer Objects (DTOs) and domain models.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


# ============= ENUMS =============

class SessionStatus(Enum):
    """Session status enumeration."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ENDED = "ended"


class TransactionType(Enum):
    """Transaction type enumeration."""
    INITIAL_STAKE = "initial_stake"
    BET_PLACED = "bet_placed"
    BET_WON = "bet_won"
    BET_LOST = "bet_lost"
    SESSION_SUMMARY = "session_summary"


class BetOutcome(Enum):
    """Bet outcome enumeration."""
    PENDING = "pending"
    WIN = "win"
    LOSS = "loss"


class OddType(Enum):
    """Odd type enumeration."""
    DECIMAL = "decimal"
    FIXED = "fixed"
    PROBABILITY = "probability"


# ============= DTOs =============

@dataclass
class GamblerDTO:
    """Data Transfer Object for Gambler."""
    gambler_id: int
    name: str
    starting_stake: float
    current_stake: float
    win_threshold: float
    loss_threshold: float
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SessionDTO:
    """Data Transfer Object for Session."""
    session_id: int
    gambler_id: int
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    starting_stake: float = 0.0
    ending_stake: Optional[float] = None
    total_bets: int = 0
    total_wins: int = 0
    total_losses: int = 0
    session_status: str = SessionStatus.ACTIVE.value
    pause_count: int = 0


@dataclass
class BetDTO:
    """Data Transfer Object for Bet."""
    bet_id: int
    session_id: int
    gambler_id: int
    bet_amount: float
    betting_strategy: str
    odds: float
    odd_type: str
    placed_at: datetime = field(default_factory=datetime.now)
    outcome: str = BetOutcome.PENDING.value
    result_amount: Optional[float] = None


@dataclass
class TransactionDTO:
    """Data Transfer Object for Transaction."""
    transaction_id: int
    gambler_id: int
    session_id: int
    transaction_type: str
    amount: float
    previous_balance: float
    new_balance: float
    created_at: datetime = field(default_factory=datetime.now)
    description: Optional[str] = None


@dataclass
class StatisticsDTO:
    """Data Transfer Object for Statistics."""
    statistic_id: int
    gambler_id: int
    total_sessions: int = 0
    total_bets: int = 0
    total_wins: int = 0
    total_losses: int = 0
    total_profit_loss: float = 0.0
    win_rate: float = 0.0
    peak_stake: float = 0.0
    lowest_stake: float = 0.0
    average_bet: float = 0.0
    longest_win_streak: int = 0
    longest_loss_streak: int = 0
    volatility: float = 0.0
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SessionSummaryDTO:
    """DTO for session summary statistics."""
    session_id: int
    gambler_id: int
    duration_seconds: float
    starting_stake: float
    ending_stake: float
    profit_loss: float
    total_bets: int
    total_wins: int
    total_losses: int
    win_rate: float
    average_bet: float
    volatility: float
    peak_stake: float
    lowest_stake: float
    session_status: str
    
    @property
    def roi(self) -> float:
        """Calculate Return on Investment."""
        if self.starting_stake == 0:
            return 0.0
        return (self.profit_loss / self.starting_stake) * 100


# ============= DOMAIN MODELS =============

@dataclass
class Gambler:
    """Domain model for Gambler."""
    name: str
    starting_stake: float
    current_stake: float
    win_threshold: float
    loss_threshold: float
    gambler_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dto(self) -> GamblerDTO:
        """Convert to DTO."""
        return GamblerDTO(
            gambler_id=self.gambler_id or 0,
            name=self.name,
            starting_stake=self.starting_stake,
            current_stake=self.current_stake,
            win_threshold=self.win_threshold,
            loss_threshold=self.loss_threshold,
            created_at=self.created_at or datetime.now(),
            updated_at=self.updated_at or datetime.now()
        )


@dataclass
class Session:
    """Domain model for Session."""
    gambler_id: int
    starting_stake: float
    session_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    ending_stake: Optional[float] = None
    total_bets: int = 0
    total_wins: int = 0
    total_losses: int = 0
    session_status: str = SessionStatus.ACTIVE.value
    pause_count: int = 0
    
    @property
    def duration_seconds(self) -> float:
        """Calculate session duration in seconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    def to_dto(self) -> SessionDTO:
        """Convert to DTO."""
        return SessionDTO(
            session_id=self.session_id or 0,
            gambler_id=self.gambler_id,
            start_time=self.start_time or datetime.now(),
            end_time=self.end_time,
            starting_stake=self.starting_stake,
            ending_stake=self.ending_stake,
            total_bets=self.total_bets,
            total_wins=self.total_wins,
            total_losses=self.total_losses,
            session_status=self.session_status,
            pause_count=self.pause_count
        )


@dataclass
class Bet:
    """Domain model for Bet."""
    session_id: int
    gambler_id: int
    bet_amount: float
    betting_strategy: str
    odds: float
    odd_type: str
    bet_id: Optional[int] = None
    placed_at: Optional[datetime] = None
    outcome: str = BetOutcome.PENDING.value
    result_amount: Optional[float] = None
    
    def to_dto(self) -> BetDTO:
        """Convert to DTO."""
        return BetDTO(
            bet_id=self.bet_id or 0,
            session_id=self.session_id,
            gambler_id=self.gambler_id,
            bet_amount=self.bet_amount,
            betting_strategy=self.betting_strategy,
            odds=self.odds,
            odd_type=self.odd_type,
            placed_at=self.placed_at or datetime.now(),
            outcome=self.outcome,
            result_amount=self.result_amount
        )


@dataclass
class Transaction:
    """Domain model for Transaction."""
    gambler_id: int
    session_id: int
    transaction_type: str
    amount: float
    previous_balance: float
    new_balance: float
    transaction_id: Optional[int] = None
    created_at: Optional[datetime] = None
    description: Optional[str] = None
    
    def to_dto(self) -> TransactionDTO:
        """Convert to DTO."""
        return TransactionDTO(
            transaction_id=self.transaction_id or 0,
            gambler_id=self.gambler_id,
            session_id=self.session_id,
            transaction_type=self.transaction_type,
            amount=self.amount,
            previous_balance=self.previous_balance,
            new_balance=self.new_balance,
            created_at=self.created_at or datetime.now(),
            description=self.description
        )
