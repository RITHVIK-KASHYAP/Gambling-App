"""
Repository implementations for all entities.
Provides CRUD operations for Gamblers, Sessions, Bets, Transactions, and Statistics.
"""

from typing import List, Optional, Dict, Any
from gambling_app_db.repositories.base_repository import BaseRepository
import logging


logger = logging.getLogger(__name__)


class GamblerRepository(BaseRepository):
    """Repository for Gambler entity."""
    
    def table_name(self) -> str:
        return "gamblers"
    
    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find gambler by name."""
        query = "SELECT * FROM gamblers WHERE name = %s"
        results = self.db.execute_query(query, (name,))
        
        if results:
            return results[0]
        return None
    
    def get_all_gamblers(self) -> List[Dict[str, Any]]:
        """Get all gamblers."""
        query = "SELECT * FROM gamblers ORDER BY created_at DESC"
        return self.db.execute_query(query)


class SessionRepository(BaseRepository):
    """Repository for Session entity."""
    
    def table_name(self) -> str:
        return "sessions"
    
    def find_active_session(self, gambler_id: int) -> Optional[Dict[str, Any]]:
        """Find active session for a gambler."""
        query = """
            SELECT * FROM sessions 
            WHERE gambler_id = %s AND session_status = 'active'
            ORDER BY start_time DESC LIMIT 1
        """
        results = self.db.execute_query(query, (gambler_id,))
        
        if results:
            return results[0]
        return None
    
    def find_session_by_id(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Find session by ID."""
        query = "SELECT * FROM sessions WHERE session_id = %s"
        results = self.db.execute_query(query, (session_id,))
        
        if results:
            return results[0]
        return None
    
    def get_gambler_sessions(self, gambler_id: int) -> List[Dict[str, Any]]:
        """Get all sessions for a gambler."""
        query = "SELECT * FROM sessions WHERE gambler_id = %s ORDER BY start_time DESC"
        return self.db.execute_query(query, (gambler_id,))
    
    def update_session_status(self, session_id: int, status: str) -> int:
        """Update session status."""
        return self.update(session_id, {"session_status": status}, "session_id")
    
    @staticmethod
    def _map_session(row) -> Dict[str, Any]:
        """Map database row to session dictionary."""
        if isinstance(row, dict):
            return row
        return {
            "session_id": row[0],
            "gambler_id": row[1],
            "start_time": row[2],
            "end_time": row[3],
            "starting_stake": float(row[4]) if row[4] else None,
            "ending_stake": float(row[5]) if row[5] else None,
            "total_bets": row[6],
            "total_wins": row[7],
            "total_losses": row[8],
            "session_status": row[9],
            "pause_count": row[10]
        }


class BetRepository(BaseRepository):
    """Repository for Bet entity."""
    
    def table_name(self) -> str:
        return "bets"
    
    def get_session_bets(self, session_id: int) -> List[Dict[str, Any]]:
        """Get all bets for a session."""
        query = "SELECT * FROM bets WHERE session_id = %s ORDER BY placed_at ASC"
        return self.db.execute_query(query, (session_id,))
    
    def get_pending_bets(self, session_id: int) -> List[Dict[str, Any]]:
        """Get pending bets for a session."""
        query = """
            SELECT * FROM bets 
            WHERE session_id = %s AND outcome = 'pending'
            ORDER BY placed_at ASC
        """
        return self.db.execute_query(query, (session_id,))
    
    def get_bet_by_id(self, bet_id: int) -> Optional[Dict[str, Any]]:
        """Find bet by ID."""
        query = "SELECT * FROM bets WHERE bet_id = %s"
        results = self.db.execute_query(query, (bet_id,))
        
        if results:
            return results[0]
        return None
    
    def update_bet_outcome(self, bet_id: int, outcome: str, result_amount: float) -> int:
        """Update bet outcome."""
        return self.update(
            bet_id,
            {"outcome": outcome, "result_amount": result_amount},
            "bet_id"
        )
    
    def get_session_stats(self, session_id: int) -> Dict[str, Any]:
        """Get betting statistics for a session."""
        query = """
            SELECT 
                COUNT(*) as total_bets,
                SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as total_wins,
                SUM(CASE WHEN outcome = 'loss' THEN 1 ELSE 0 END) as total_losses,
                SUM(bet_amount) as total_wagered,
                SUM(CASE WHEN outcome = 'win' THEN result_amount ELSE 0 END) as total_winnings
            FROM bets WHERE session_id = %s
        """
        results = self.db.execute_query(query, (session_id,))
        
        if results:
            row = results[0]
            return {
                "total_bets": row["total_bets"] or 0,
                "total_wins": row["total_wins"] or 0,
                "total_losses": row["total_losses"] or 0,
                "total_wagered": float(row["total_wagered"]) if row["total_wagered"] else 0.0,
                "total_winnings": float(row["total_winnings"]) if row["total_winnings"] else 0.0
            }
        return {
            "total_bets": 0,
            "total_wins": 0,
            "total_losses": 0,
            "total_wagered": 0.0,
            "total_winnings": 0.0
        }
    
    @staticmethod
    def _map_bet(row) -> Dict[str, Any]:
        """Map database row to bet dictionary."""
        if isinstance(row, dict):
            return row
        return {
            "bet_id": row[0],
            "session_id": row[1],
            "gambler_id": row[2],
            "bet_amount": float(row[3]),
            "betting_strategy": row[4],
            "odds": float(row[5]),
            "odd_type": row[6],
            "placed_at": row[7],
            "outcome": row[8],
            "result_amount": float(row[9]) if row[9] else None
        }


class TransactionRepository(BaseRepository):
    """Repository for Transaction entity."""
    
    def table_name(self) -> str:
        return "transactions"
    
    def get_gambler_transactions(self, gambler_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get transactions for a gambler."""
        query = """
            SELECT * FROM transactions 
            WHERE gambler_id = %s 
            ORDER BY created_at DESC LIMIT %s
        """
        return self.db.execute_query(query, (gambler_id, limit))
    
    def get_session_transactions(self, session_id: int) -> List[Dict[str, Any]]:
        """Get transactions for a session."""
        query = """
            SELECT * FROM transactions 
            WHERE session_id = %s 
            ORDER BY created_at ASC
        """
        return self.db.execute_query(query, (session_id,))
    
    def get_balance_at_time(self, gambler_id: int, session_id: int) -> float:
        """Get current balance from most recent transaction."""
        query = """
            SELECT new_balance FROM transactions 
            WHERE gambler_id = %s AND session_id = %s
            ORDER BY created_at DESC LIMIT 1
        """
        results = self.db.execute_query(query, (gambler_id, session_id))
        
        if results:
            row = results[0]
            if isinstance(row, dict):
                return float(row["new_balance"])
            return float(row[0])
        return 0.0
    
    @staticmethod
    def _map_transaction(row) -> Dict[str, Any]:
        """Map database row to transaction dictionary."""
        if isinstance(row, dict):
            return row
        return {
            "transaction_id": row[0],
            "gambler_id": row[1],
            "session_id": row[2],
            "transaction_type": row[3],
            "amount": float(row[4]),
            "previous_balance": float(row[5]),
            "new_balance": float(row[6]),
            "created_at": row[7],
            "description": row[8]
        }


class StatisticsRepository(BaseRepository):
    """Repository for Statistics entity."""
    
    def table_name(self) -> str:
        return "statistics"
    
    def get_gambler_stats(self, gambler_id: int) -> Optional[Dict[str, Any]]:
        """Get statistics for a gambler."""
        query = "SELECT * FROM statistics WHERE gambler_id = %s"
        results = self.db.execute_query(query, (gambler_id,))
        
        if results:
            return results[0]
        return None
    
    def update_statistics(self, gambler_id: int, stats: Dict[str, Any]) -> int:
        """Update gambler statistics."""
        return self.update(gambler_id, stats, "gambler_id")
    
    def get_all_statistics(self) -> List[Dict[str, Any]]:
        """Get statistics for all gamblers."""
        query = "SELECT * FROM statistics ORDER BY total_profit_loss DESC"
        return self.db.execute_query(query)
    
    @staticmethod
    def _map_statistics(row) -> Dict[str, Any]:
        """Map database row to statistics dictionary."""
        if isinstance(row, dict):
            return row
        return {
            "statistic_id": row[0],
            "gambler_id": row[1],
            "total_sessions": row[2],
            "total_bets": row[3],
            "total_wins": row[4],
            "total_losses": row[5],
            "total_profit_loss": float(row[6]),
            "win_rate": float(row[7]),
            "peak_stake": float(row[8]),
            "lowest_stake": float(row[9]),
            "average_bet": float(row[10]),
            "longest_win_streak": row[11],
            "longest_loss_streak": row[12],
            "volatility": float(row[13]),
            "updated_at": row[14]
        }
