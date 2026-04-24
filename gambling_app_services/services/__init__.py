"""
Service layer for the Gambling Simulation System.
Contains core business logic for gamblers, sessions, bets, and transactions.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from datetime import timedelta
import collections

from gambling_app_core.entities import (
    Gambler, Session, Bet, Transaction, SessionSummaryDTO,
    SessionStatus, TransactionType, BetOutcome, OddType
)
from gambling_app_db.repositories import (
    GamblerRepository, SessionRepository, BetRepository,
    TransactionRepository, StatisticsRepository
)
from gambling_app_services.validators import (
    StakeValidator, BetValidator, GamblerValidator
)
from gambling_app_services.strategies import BettingStrategyRegistry, OutcomeStrategyRegistry
from gambling_app_utils.utils import CalculationUtils, StreakTracker, StatisticsCalculator, FormattingUtils
from gambling_app_core.exceptions import (
    GamblerException, SessionException, BetValidationException,
    StakeValidationException, BettingEngineException
)
from gambling_app_core.config import APP_CONFIG


logger = logging.getLogger(__name__)


# ============= GAMBLER SERVICE =============

class GamblerService:
    """Service for managing gambler profiles."""
    
    def __init__(self):
        """Initialize gambler service."""
        self.gambler_repo = GamblerRepository()
        self.stats_repo = StatisticsRepository()
    
    def create_gambler(self, name: str, starting_stake: float,
                      win_threshold: float, loss_threshold: float) -> Gambler:
        """
        Create a new gambler.
        
        Args:
            name: Gambler name
            starting_stake: Initial stake amount
            win_threshold: Upper threshold
            loss_threshold: Lower threshold
        
        Returns:
            Created gambler object
        
        Raises:
            GamblerException: If creation fails
        """
        try:
            # Validate inputs
            GamblerValidator.validate_gambler_name(name)
            StakeValidator.validate_initial_stake(starting_stake)
            StakeValidator.validate_threshold(win_threshold, loss_threshold, starting_stake)
            
            # Check if gambler already exists
            if self.gambler_repo.find_by_name(name):
                raise GamblerException(f"Gambler '{name}' already exists")
            
            # Create gambler
            gambler = Gambler(
                name=name,
                starting_stake=starting_stake,
                current_stake=starting_stake,
                win_threshold=win_threshold,
                loss_threshold=loss_threshold
            )
            
            # Save to database
            gambler_id = self.gambler_repo.create({
                "name": name,
                "starting_stake": starting_stake,
                "current_stake": starting_stake,
                "win_threshold": win_threshold,
                "loss_threshold": loss_threshold
            })
            
            gambler.gambler_id = gambler_id
            
            # Create statistics record
            self.stats_repo.create({
                "gambler_id": gambler_id,
                "total_sessions": 0,
                "total_bets": 0,
                "total_wins": 0,
                "total_losses": 0,
                "total_profit_loss": 0.0,
                "win_rate": 0.0,
                "peak_stake": starting_stake,
                "lowest_stake": starting_stake,
                "average_bet": 0.0
            })
            
            logger.info(f"Created gambler: {name}")
            return gambler
        
        except (GamblerException, StakeValidationException) as e:
            raise
        except Exception as e:
            logger.error(f"Error creating gambler: {e}")
            raise GamblerException(f"Failed to create gambler: {str(e)}")
    
    def get_gambler(self, gambler_id: int) -> Gambler:
        """Get gambler by ID."""
        data = self.gambler_repo.read(gambler_id)
        if not data:
            raise GamblerException(f"Gambler {gambler_id} not found")
        
        # Handle both dict and tuple formats
        if isinstance(data, dict):
            gambler_data = data
        else:
            # Convert tuple to dict if needed (shouldn't happen with dictionary cursor)
            gambler_data = {
                "gambler_id": data[0],
                "name": data[1],
                "starting_stake": float(data[2]),
                "current_stake": float(data[3]),
                "win_threshold": float(data[4]),
                "loss_threshold": float(data[5]),
                "created_at": data[6],
                "updated_at": data[7]
            }
        
        return self._map_to_gambler(gambler_data)
    
    def get_gambler_by_name(self, name: str) -> Optional[Gambler]:
        """Get gambler by name."""
        data = self.gambler_repo.find_by_name(name)
        if data:
            return self._map_to_gambler(data)
        return None
    
    def reset_gambler(self, gambler_id: int, confirm: bool = False) -> None:
        """
        Reset gambler to initial state.
        
        Args:
            gambler_id: Gambler ID
            confirm: Confirmation flag
        
        Raises:
            GamblerException: If reset fails
        """
        try:
            GamblerValidator.validate_reset_request(confirm)
            
            gambler = self.get_gambler(gambler_id)
            
            self.gambler_repo.update(gambler_id, {
                "current_stake": gambler.starting_stake
            })
            
            logger.info(f"Reset gambler {gambler_id}")
        
        except Exception as e:
            logger.error(f"Error resetting gambler: {e}")
            raise GamblerException(f"Failed to reset gambler: {str(e)}")
    
    def list_all_gamblers(self) -> List[Gambler]:
        """Get all gamblers."""
        data = self.gambler_repo.get_all_gamblers()
        return [self._map_to_gambler(d) for d in data]
    
    @staticmethod
    def _map_to_gambler(data: Dict[str, Any]) -> Gambler:
        """Map repository data to Gambler object."""
        return Gambler(
            gambler_id=data["gambler_id"],
            name=data["name"],
            starting_stake=data["starting_stake"],
            current_stake=data["current_stake"],
            win_threshold=data["win_threshold"],
            loss_threshold=data["loss_threshold"],
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )


# ============= SESSION SERVICE =============

class SessionService:
    """Service for managing game sessions."""
    
    def __init__(self):
        """Initialize session service."""
        self.session_repo = SessionRepository()
        self.transaction_repo = TransactionRepository()
        self.bet_repo = BetRepository()
        self.gambler_repo = GamblerRepository()
    
    def start_session(self, gambler_id: int) -> Session:
        """
        Start a new session.
        
        Args:
            gambler_id: Gambler ID
        
        Returns:
            Started session
        
        Raises:
            SessionException: If session cannot be started
        """
        try:
            # Check for active session
            active = self.session_repo.find_active_session(gambler_id)
            if active:
                raise SessionException("Gambler already has an active session")
            
            # Get gambler data
            gambler_data = self.gambler_repo.read(gambler_id)
            if not gambler_data:
                raise SessionException(f"Gambler {gambler_id} not found")
            
            current_stake = gambler_data.get("current_stake", gambler_data[3] if isinstance(gambler_data, (list, tuple)) else 0)
            
            # Create session
            session = Session(
                gambler_id=gambler_id,
                starting_stake=current_stake,
                start_time=datetime.now()
            )
            
            # Save to database
            session_id = self.session_repo.create({
                "gambler_id": gambler_id,
                "starting_stake": current_stake,
                "session_status": SessionStatus.ACTIVE.value
            })
            
            session.session_id = session_id
            
            # Record initial transaction
            self.transaction_repo.create({
                "gambler_id": gambler_id,
                "session_id": session_id,
                "transaction_type": TransactionType.INITIAL_STAKE.value,
                "amount": current_stake,
                "previous_balance": current_stake,
                "new_balance": current_stake,
                "description": "Session started"
            })
            
            logger.info(f"Started session {session_id} for gambler {gambler_id}")
            return session
        
        except SessionException:
            raise
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            raise SessionException(f"Failed to start session: {str(e)}")
    
    def get_active_session(self, gambler_id: int) -> Optional[Session]:
        """Get active session for gambler."""
        data = self.session_repo.find_active_session(gambler_id)
        if data:
            return self._map_to_session(data)
        return None
    
    def get_session(self, session_id: int) -> Session:
        """Get session by ID."""
        data = self.session_repo.find_session_by_id(session_id)
        if not data:
            raise SessionException(f"Session {session_id} not found")
        return self._map_to_session(data)
    
    def pause_session(self, session_id: int) -> None:
        """Pause a session."""
        session_data = self.session_repo.find_session_by_id(session_id)
        if not session_data:
            raise SessionException(f"Session {session_id} not found")
        
        self.session_repo.update_session_status(session_id, SessionStatus.PAUSED.value)
        self.session_repo.update(session_id, {
            "pause_count": session_data["pause_count"] + 1
        }, "session_id")
        
        logger.info(f"Paused session {session_id}")
    
    def resume_session(self, session_id: int) -> None:
        """Resume a paused session."""
        self.session_repo.update_session_status(session_id, SessionStatus.ACTIVE.value)
        logger.info(f"Resumed session {session_id}")
    
    def end_session(self, session_id: int) -> SessionSummaryDTO:
        """
        End a session and return summary.
        
        Args:
            session_id: Session ID
        
        Returns:
            Session summary
        
        Raises:
            SessionException: If session cannot be ended
        """
        try:
            session_data = self.session_repo.find_session_by_id(session_id)
            if not session_data:
                raise SessionException(f"Session {session_id} not found")
            
            gambler_id = session_data["gambler_id"]
            gambler_data = self.gambler_repo.read(gambler_id)
            current_stake = gambler_data.get("current_stake", gambler_data[3] if isinstance(gambler_data, (list, tuple)) else 0)
            
            # Update session
            self.session_repo.update(session_id, {
                "end_time": datetime.now(),
                "ending_stake": current_stake,
                "session_status": SessionStatus.ENDED.value
            }, "session_id")
            
            # Calculate summary
            bets_data = self.bet_repo.get_session_stats(session_id)
            transactions = self.transaction_repo.get_session_transactions(session_id)
            
            profit_loss = current_stake - session_data["starting_stake"]
            win_rate = CalculationUtils.calculate_win_rate(
                bets_data["total_wins"],
                bets_data["total_bets"]
            )
            
            summary = SessionSummaryDTO(
                session_id=session_id,
                gambler_id=gambler_id,
                duration_seconds=session_data.get("duration_seconds", 0),
                starting_stake=session_data["starting_stake"],
                ending_stake=current_stake,
                profit_loss=profit_loss,
                total_bets=bets_data["total_bets"],
                total_wins=bets_data["total_wins"],
                total_losses=bets_data["total_losses"],
                win_rate=win_rate,
                average_bet=CalculationUtils.calculate_average_bet(
                    bets_data["total_wagered"],
                    bets_data["total_bets"]
                ),
                volatility=StatisticsCalculator.calculate_volatility_from_stakes(
                    [t["new_balance"] for t in transactions]
                ),
                peak_stake=max([t["new_balance"] for t in transactions] or [session_data["starting_stake"]]),
                lowest_stake=min([t["new_balance"] for t in transactions] or [session_data["starting_stake"]]),
                session_status=SessionStatus.ENDED.value
            )
            
            logger.info(f"Ended session {session_id} with profit/loss: {profit_loss}")
            return summary
        
        except SessionException:
            raise
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            raise SessionException(f"Failed to end session: {str(e)}")
    
    @staticmethod
    def _map_to_session(data: Dict[str, Any]) -> Session:
        """Map repository data to Session object."""
        return Session(
            session_id=data["session_id"],
            gambler_id=data["gambler_id"],
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            starting_stake=data["starting_stake"],
            ending_stake=data.get("ending_stake"),
            total_bets=data.get("total_bets", 0),
            total_wins=data.get("total_wins", 0),
            total_losses=data.get("total_losses", 0),
            session_status=data.get("session_status", SessionStatus.ACTIVE.value),
            pause_count=data.get("pause_count", 0)
        )


# ============= STAKE SERVICE =============

class StakeService:
    """Service for managing stake operations."""
    
    def __init__(self):
        """Initialize stake service."""
        self.gambler_repo = GamblerRepository()
        self.transaction_repo = TransactionRepository()
    
    def update_stake(self, gambler_id: int, session_id: int,
                    amount: float, operation: str = "update",
                    description: str = None) -> float:
        """
        Update gambler stake.
        
        Args:
            gambler_id: Gambler ID
            session_id: Session ID
            amount: Amount to add/subtract
            operation: 'add' or 'subtract'
            description: Transaction description
        
        Returns:
            New stake amount
        
        Raises:
            StakeValidationException: If update is invalid
        """
        try:
            # Get current stake
            gambler_data = self.gambler_repo.read(gambler_id)
            current_stake = gambler_data.get("current_stake", gambler_data[3] if isinstance(gambler_data, (list, tuple)) else 0)
            
            # Convert everything to float for safety
            current_stake = float(current_stake) if current_stake else 0.0
            amount = float(amount) if amount else 0.0
            
            # Calculate new stake
            if operation == "add":
                StakeValidator.validate_stake_update(current_stake, amount, "add")
                new_stake = current_stake + amount
            elif operation == "subtract":
                StakeValidator.validate_stake_update(current_stake, amount, "subtract")
                new_stake = current_stake - amount
            else:
                raise StakeValidationException(f"Unknown operation: {operation}")
            
            # Update gambler
            self.gambler_repo.update(gambler_id, {"current_stake": new_stake})
            
            # Record transaction
            self.transaction_repo.create({
                "gambler_id": gambler_id,
                "session_id": session_id,
                "transaction_type": "stake_update",
                "amount": amount,
                "previous_balance": current_stake,
                "new_balance": new_stake,
                "description": description or f"Stake {operation}: {amount}"
            })
            
            logger.info(f"Updated stake for gambler {gambler_id}: {current_stake} -> {new_stake}")
            return new_stake
        
        except StakeValidationException:
            raise
        except Exception as e:
            logger.error(f"Error updating stake: {e}")
            raise StakeValidationException(f"Failed to update stake: {str(e)}")
    
    def check_thresholds(self, gambler_id: int) -> tuple:
        """
        Check if stake has crossed thresholds.
        
        Returns:
            (within_bounds: bool, threshold_type: str or None)
            threshold_type: 'win', 'loss', or None
        """
        gambler_data = self.gambler_repo.read(gambler_id)
        current_stake = gambler_data.get("current_stake", gambler_data[3] if isinstance(gambler_data, (list, tuple)) else 0)
        win_threshold = gambler_data.get("win_threshold", gambler_data[4] if isinstance(gambler_data, (list, tuple)) else 0)
        loss_threshold = gambler_data.get("loss_threshold", gambler_data[5] if isinstance(gambler_data, (list, tuple)) else 0)
        
        if current_stake >= win_threshold:
            return False, "win"
        elif current_stake <= loss_threshold:
            return False, "loss"
        
        return True, None


# ============= BETTING ENGINE =============

class BettingEngine:
    """Service for managing bets and outcomes."""
    
    def __init__(self):
        """Initialize betting engine."""
        self.bet_repo = BetRepository()
        self.stake_service = StakeService()
        self.gambler_repo = GamblerRepository()
        self.streak_tracker = StreakTracker()
        from gambling_app_db.repositories import StatisticsRepository
        self.stats_repo = StatisticsRepository()
    
    def place_bet(self, session_id: int, gambler_id: int,
                 bet_amount: float, betting_strategy: str,
                 odds: float, odd_type: str = OddType.DECIMAL.value) -> Bet:
        """
        Place a bet.
        
        Args:
            session_id: Session ID
            gambler_id: Gambler ID
            bet_amount: Bet amount
            betting_strategy: Strategy name
            odds: Odds value
            odd_type: Type of odds
        
        Returns:
            Placed bet
        
        Raises:
            BetValidationException: If bet is invalid
        """
        try:
            # Get gambler
            gambler_data = self.gambler_repo.read(gambler_id)
            current_stake = gambler_data.get("current_stake", gambler_data[3] if isinstance(gambler_data, (list, tuple)) else 0)
            
            # Convert to float for consistency
            current_stake = float(current_stake) if not isinstance(current_stake, float) else current_stake
            bet_amount = float(bet_amount) if not isinstance(bet_amount, float) else bet_amount
            
            # Validate
            BetValidator.validate_bet_amount(bet_amount, current_stake)
            BetValidator.validate_odds(odds, odd_type)
            
            # Check strategy exists
            strategy = BettingStrategyRegistry.get(betting_strategy)
            
            # Create bet
            bet = Bet(
                session_id=session_id,
                gambler_id=gambler_id,
                bet_amount=bet_amount,
                betting_strategy=betting_strategy,
                odds=odds,
                odd_type=odd_type,
                placed_at=datetime.now()
            )
            
            # Save to database
            bet_id = self.bet_repo.create({
                "session_id": session_id,
                "gambler_id": gambler_id,
                "bet_amount": bet_amount,
                "betting_strategy": betting_strategy,
                "odds": odds,
                "odd_type": odd_type
            })
            
            bet.bet_id = bet_id
            
            # Deduct from stake
            self.stake_service.update_stake(
                gambler_id, session_id,
                bet_amount, "subtract",
                f"Bet placed: {betting_strategy}"
            )
            
            logger.info(f"Placed bet {bet_id}: {bet_amount} at {odds} odds")
            return bet
        
        except BetValidationException:
            raise
        except Exception as e:
            logger.error(f"Error placing bet: {e}")
            raise BetValidationException(f"Failed to place bet: {str(e)}")
    
    def resolve_bet(self, bet_id: int, outcome_strategy: str = "weighted") -> tuple:
        """
        Resolve a pending bet.
        
        Args:
            bet_id: Bet ID
            outcome_strategy: Strategy for determining outcome
        
        Returns:
            (outcome: str, result_amount: float, net_change: float)
        
        Raises:
            BettingEngineException: If resolution fails
        """
        try:
            bet_data = self.bet_repo.get_bet_by_id(bet_id)
            if not bet_data:
                raise BettingEngineException(f"Bet {bet_id} not found")
            
            # Convert all numeric values to float early
            bet_amount = float(bet_data["bet_amount"]) if bet_data["bet_amount"] else 0.0
            odds = float(bet_data["odds"]) if bet_data["odds"] else 1.0
            
            # Get outcome strategy
            outcome_strat = OutcomeStrategyRegistry.get(outcome_strategy)
            
            # Determine outcome
            is_win = outcome_strat.determine_outcome(odds)
            outcome = BetOutcome.WIN.value if is_win else BetOutcome.LOSS.value
            
            # Calculate payout
            if is_win:
                if bet_data["odd_type"] == "decimal":
                    result_amount = bet_amount * odds
                elif bet_data["odd_type"] == "fixed":
                    result_amount = bet_amount * (1 + odds)
                else:  # probability
                    result_amount = bet_amount * 2  # Simple double for probability
                
                net_change = result_amount - bet_amount
            else:
                result_amount = 0.0
                net_change = -bet_amount
            
            # Update bet
            self.bet_repo.update_bet_outcome(bet_id, outcome, result_amount if is_win else 0)
            
            # Update stake
            gambler_id = bet_data["gambler_id"]
            session_id = bet_data["session_id"]
            
            if is_win:
                self.stake_service.update_stake(
                    gambler_id, session_id,
                    result_amount, "add",
                    f"Bet won: {bet_amount} @ {odds}"
                )
            
            # Record transaction
            from gambling_app_db.repositories import TransactionRepository
            trans_repo = TransactionRepository()
            
            gambler_data = self.gambler_repo.read(gambler_id)
            current_stake = gambler_data.get("current_stake", gambler_data[3] if isinstance(gambler_data, (list, tuple)) else 0)
            current_stake = float(current_stake) if current_stake else 0.0
            
            trans_repo.create({
                "gambler_id": gambler_id,
                "session_id": session_id,
                "transaction_type": outcome,
                "amount": bet_amount,
                "previous_balance": current_stake - net_change,
                "new_balance": current_stake,
                "description": f"Bet {outcome}: {bet_amount} @ {odds}"
            })
            
            # Track streak
            self.streak_tracker.record_outcome(outcome)
            
            # Update statistics
            self._update_statistics(gambler_id, outcome, bet_amount, result_amount, current_stake)
            
            logger.info(f"Resolved bet {bet_id}: {outcome} for {result_amount}")
            return outcome, result_amount, net_change
        
        except BettingEngineException:
            raise
        except Exception as e:
            logger.error(f"Error resolving bet: {e}")
            raise BettingEngineException(f"Failed to resolve bet: {str(e)}")
    
    def _update_statistics(self, gambler_id: int, outcome: str, bet_amount: float, 
                          result_amount: float, current_stake: float) -> None:
        """
        Update gambler statistics after a bet is resolved.
        
        Args:
            gambler_id: Gambler ID
            outcome: Bet outcome ('win' or 'loss')
            bet_amount: Amount wagered
            result_amount: Amount won (0 if loss)
            current_stake: Current stake after bet
        """
        try:
            # Get current statistics
            stats = self.stats_repo.get_gambler_stats(gambler_id)
            
            if not stats:
                logger.warning(f"Statistics not found for gambler {gambler_id}")
                return
            
            # Update statistics
            total_bets = stats.get("total_bets", 0) + 1
            total_wins = stats.get("total_wins", 0) + (1 if outcome == "win" else 0)
            total_losses = stats.get("total_losses", 0) + (1 if outcome == "loss" else 0)
            
            # Calculate profit/loss
            profit_change = result_amount - bet_amount if outcome == "win" else -bet_amount
            total_profit_loss = float(stats.get("total_profit_loss", 0)) + profit_change
            
            # Calculate win rate
            win_rate = (total_wins / total_bets * 100) if total_bets > 0 else 0.0
            
            # Update peak and lowest stakes
            peak_stake = max(float(stats.get("peak_stake", current_stake)), current_stake)
            lowest_stake = min(float(stats.get("lowest_stake", current_stake)), current_stake)
            
            # Calculate average bet
            total_wagered = float(stats.get("average_bet", 0)) * (total_bets - 1) + bet_amount if total_bets > 1 else bet_amount
            average_bet = total_wagered / total_bets if total_bets > 0 else 0.0
            
            # Update statistics in database
            self.stats_repo.update_statistics(gambler_id, {
                "total_bets": total_bets,
                "total_wins": total_wins,
                "total_losses": total_losses,
                "total_profit_loss": total_profit_loss,
                "win_rate": round(win_rate, 2),
                "peak_stake": peak_stake,
                "lowest_stake": lowest_stake,
                "average_bet": round(average_bet, 2)
            })
            
            logger.info(f"Updated statistics for gambler {gambler_id}: "
                       f"Total Bets={total_bets}, Wins={total_wins}, Losses={total_losses}, "
                       f"Win Rate={win_rate:.2f}%")
        
        except Exception as e:
            logger.error(f"Error updating statistics for gambler {gambler_id}: {e}")
