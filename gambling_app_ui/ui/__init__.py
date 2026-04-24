"""
Console UI for the Gambling Simulation System.
Menu-driven interface for user interaction.
"""

import logging
from typing import Optional, List
from enum import Enum
import os

from gambling_app_services.services import (
    GamblerService, SessionService, BettingEngine, StakeService
)
from gambling_app_core.exceptions import GamblingAppException
from gambling_app_utils.utils import FormattingUtils, CalculationUtils
from gambling_app_services.strategies import BettingStrategyRegistry, OutcomeStrategyRegistry
from gambling_app_core.config import APP_CONFIG, GameType, GAME_ODDS_CONFIG
from gambling_app_db.repositories import StatisticsRepository


logger = logging.getLogger(__name__)


class MenuOption(Enum):
    """Main menu options."""
    START_SESSION = 1
    VIEW_STATUS = 2
    PLACE_BET = 3
    AUTO_PLAY = 4
    PAUSE_SESSION = 5
    RESUME_SESSION = 6
    END_SESSION = 7
    EXIT = 8


class GamblingUI:
    """Console User Interface for the Gambling Simulation System."""
    
    def __init__(self):
        """Initialize UI and services."""
        self.gambler_service = GamblerService()
        self.session_service = SessionService()
        self.stake_service = StakeService()
        self.betting_engine = BettingEngine()
        self.stats_repo = StatisticsRepository()
        
        self.current_gambler = None
        self.current_session = None
        self.current_game_type = GameType.ROULETTE
    
    def _recover_incomplete_session(self) -> None:
        """Recover from incomplete session if exists."""
        try:
            if self.current_gambler:
                active = self.session_service.get_active_session(self.current_gambler.gambler_id)
                if active and not self.current_session:
                    # Session exists in DB but not in memory - offer recovery options
                    print("\n⚠️  Found incomplete session from previous run")
                    print("1. Resume session")
                    print("2. End and start new session")
                    choice = input("Choose option (1-2): ").strip()
                    
                    if choice == "1":
                        self.current_session = active
                        print("Session resumed")
                    elif choice == "2":
                        try:
                            self.session_service.end_session(active.session_id)
                            self.current_session = None
                            print("Previous session ended. You can now start a new one.")
                        except:
                            self.current_session = None
                    input("Press Enter to continue...")
        except Exception as e:
            logger.warning(f"Session recovery error: {e}")
    
    def run(self) -> None:
        """Run the main application loop."""
        self.print_welcome()
        
        while True:
            try:
                # Ensure gambler is selected
                if not self.current_gambler:
                    self.select_or_create_gambler()
                    continue
                
                # Check for incomplete sessions
                self._recover_incomplete_session()
                
                # Show main menu
                self.show_main_menu()
            
            except KeyboardInterrupt:
                print("\n\nApplication interrupted by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                print(f"\nError: {e}")
                input("Press Enter to continue...")
    
    def print_welcome(self) -> None:
        """Print welcome screen."""
        self.clear_screen()
        print("=" * 70)
        print(" " * 15 + "GAMBLING SIMULATION SYSTEM")
        print(" " * 10 + "Strategic Gambler with Threshold Management")
        print("=" * 70)
        print()
    
    def select_or_create_gambler(self) -> None:
        """Select or create a gambler."""
        print("\n--- Gambler Selection ---")
        print("1. Select existing gambler")
        print("2. Create new gambler")
        print("3. View all gamblers")
        print("4. Exit")
        
        choice = input("\nYour choice (1-4): ").strip()
        
        if choice == "1":
            self.select_existing_gambler()
        elif choice == "2":
            self.create_new_gambler()
        elif choice == "3":
            self.view_all_gamblers()
        elif choice == "4":
            exit(0)
        else:
            print("Invalid choice")
    
    def select_existing_gambler(self) -> None:
        """Select an existing gambler."""
        try:
            gamblers = self.gambler_service.list_all_gamblers()
            
            if not gamblers:
                print("No gamblers found. Create one first.")
                return
            
            print("\n--- Available Gamblers ---")
            for i, gambler in enumerate(gamblers, 1):
                print(f"{i}. {gambler.name} - "
                      f"Stake: {FormattingUtils.format_currency(gambler.current_stake)}")
            
            choice = input("\nSelect gambler number: ").strip()
            index = int(choice) - 1
            
            if 0 <= index < len(gamblers):
                self.current_gambler = gamblers[index]
                self.current_session = None
                print(f"\nSelected gambler: {self.current_gambler.name}")
            else:
                print("Invalid selection")
        
        except Exception as e:
            print(f"Error: {e}")
    
    def create_new_gambler(self) -> None:
        """Create a new gambler."""
        try:
            print("\n--- Create New Gambler ---")
            
            name = input("Enter gambler name: ").strip()
            starting_stake = float(input(f"Starting stake (min $1): $"))
            win_threshold = float(input(f"Win threshold (must be > starting stake): $"))
            loss_threshold = float(input(f"Loss threshold (must be < starting stake): $"))
            
            gambler = self.gambler_service.create_gambler(
                name, starting_stake, win_threshold, loss_threshold
            )
            
            self.current_gambler = gambler
            self.current_session = None
            
            print(f"\nGambler '{name}' created successfully!")
        
        except GamblingAppException as e:
            print(f"Error: {e}")
        except ValueError:
            print("Invalid input. Please enter valid numbers.")
        except Exception as e:
            print(f"Unexpected error: {e}")
    
    def view_all_gamblers(self) -> None:
        """View all gamblers with statistics."""
        try:
            gamblers = self.gambler_service.list_all_gamblers()
            
            if not gamblers:
                print("No gamblers found.")
                return
            
            print("\n--- All Gamblers ---")
            print(f"{'Name':<20} {'Stake':<15} {'Win':<15} {'Loss':<15}")
            print("-" * 65)
            
            for gambler in gamblers:
                print(f"{gambler.name:<20} "
                      f"{FormattingUtils.format_currency(gambler.current_stake):<15} "
                      f"{FormattingUtils.format_currency(gambler.win_threshold):<15} "
                      f"{FormattingUtils.format_currency(gambler.loss_threshold):<15}")
            
            input("\nPress Enter to continue...")
        
        except Exception as e:
            print(f"Error: {e}")
    
    def show_main_menu(self) -> None:
        """Show main menu."""
        self.clear_screen()
        print(f"\n=== Current Gambler: {self.current_gambler.name} ===")
        print(f"Current Stake: {FormattingUtils.format_currency(self.current_gambler.current_stake)}")
        print(f"Win Threshold: {FormattingUtils.format_currency(self.current_gambler.win_threshold)}")
        print(f"Loss Threshold: {FormattingUtils.format_currency(self.current_gambler.loss_threshold)}")
        
        if self.current_session:
            print(f"\nActive Session ID: {self.current_session.session_id}")
            print(f"Bets Placed: {self.current_session.total_bets}")
        
        print("\n--- Main Menu ---")
        print("1. Start New Session")
        print("2. View Status")
        print("3. Place Bet")
        print("4. Auto Play")
        print("5. Pause Session")
        print("6. Resume Session")
        print("7. End Session")
        print("8. Exit")
        
        choice = input("\nYour choice (1-8): ").strip()
        
        try:
            option = MenuOption(int(choice))
            
            if option == MenuOption.START_SESSION:
                self.start_session()
            elif option == MenuOption.VIEW_STATUS:
                self.view_status()
            elif option == MenuOption.PLACE_BET:
                self.place_bet()
            elif option == MenuOption.AUTO_PLAY:
                self.auto_play()
            elif option == MenuOption.PAUSE_SESSION:
                self.pause_session()
            elif option == MenuOption.RESUME_SESSION:
                self.resume_session()
            elif option == MenuOption.END_SESSION:
                self.end_session()
            elif option == MenuOption.EXIT:
                print("\nThank you for using Gambling Simulation System!")
                exit(0)
        
        except (ValueError, KeyError):
            print("Invalid choice")
            input("Press Enter to continue...")
    
    def start_session(self) -> None:
        """Start a new session."""
        try:
            # Check for active session
            active = self.session_service.get_active_session(self.current_gambler.gambler_id)
            if active and self.current_session:
                print("\nYou already have an active session. End it first.")
                input("Press Enter to continue...")
                return
            elif active and not self.current_session:
                # Recover from incomplete session
                print("\n⚠️  Found incomplete session. Cleaning up...")
                try:
                    self.session_service.end_session(active.session_id)
                except:
                    pass  # Ignore cleanup errors
            
            # Select game type
            self.select_game_type()
            
            session = self.session_service.start_session(self.current_gambler.gambler_id)
            self.current_session = session
            
            print(f"\nSession started!")
            print(f"Game Type: {self.current_game_type.value.upper()}")
            print(f"Session ID: {session.session_id}")
            print(f"Starting Stake: {FormattingUtils.format_currency(session.starting_stake)}")
            
            input("\nPress Enter to continue...")
        
        except GamblingAppException as e:
            print(f"Error: {e}")
            input("Press Enter to continue...")
    
    def select_game_type(self) -> None:
        """Select game type for the session."""
        print("\n--- Select Game Type ---")
        games = list(GameType)
        for i, game in enumerate(games, 1):
            print(f"{i}. {game.value.upper()}")
        
        choice = input("Select game type (number): ").strip()
        try:
            self.current_game_type = games[int(choice) - 1]
            print(f"Selected: {self.current_game_type.value}")
        except (ValueError, IndexError):
            print("Invalid choice, using default")
            self.current_game_type = GameType.ROULETTE
    
    def view_status(self) -> None:
        """View current status."""
        print("\n--- Current Status ---")
        print(f"Gambler: {self.current_gambler.name}")
        print(f"Current Stake: {FormattingUtils.format_currency(self.current_gambler.current_stake)}")
        print(f"Starting Stake: {FormattingUtils.format_currency(self.current_gambler.starting_stake)}")
        print(f"Profit/Loss: {FormattingUtils.format_currency(self.current_gambler.current_stake - self.current_gambler.starting_stake)}")
        print(f"Win Threshold: {FormattingUtils.format_currency(self.current_gambler.win_threshold)}")
        print(f"Loss Threshold: {FormattingUtils.format_currency(self.current_gambler.loss_threshold)}")
        
        if self.current_session:
            print(f"\nSession Status: Active")
            print(f"Session ID: {self.current_session.session_id}")
            print(f"Total Bets: {self.current_session.total_bets}")
            print(f"Wins: {self.current_session.total_wins}")
            print(f"Losses: {self.current_session.total_losses}")
            
            if self.current_session.total_bets > 0:
                win_rate = CalculationUtils.calculate_win_rate(
                    self.current_session.total_wins,
                    self.current_session.total_bets
                )
                print(f"Win Rate: {FormattingUtils.format_percentage(win_rate)}")
        else:
            print("\nNo active session")
        
        # Display lifetime statistics
        self.display_statistics()
        
        input("\nPress Enter to continue...")
    
    def display_statistics(self) -> None:
        """Display current statistics for the gambler."""
        try:
            stats = self.stats_repo.get_gambler_stats(self.current_gambler.gambler_id)
            
            if stats:
                print("\n--- Lifetime Statistics ---")
                print(f"{'Total Bets':<20} {stats.get('total_bets', 0)}")
                print(f"{'Total Wins':<20} {stats.get('total_wins', 0)}")
                print(f"{'Total Losses':<20} {stats.get('total_losses', 0)}")
                win_rate = stats.get('win_rate', 0.0)
                print(f"{'Win Rate':<20} {win_rate:.2f}%")
                print(f"{'Total Profit/Loss':<20} {FormattingUtils.format_currency(stats.get('total_profit_loss', 0))}")
                print(f"{'Average Bet':<20} {FormattingUtils.format_currency(stats.get('average_bet', 0))}")
                print(f"{'Peak Stake':<20} {FormattingUtils.format_currency(stats.get('peak_stake', 0))}")
                print(f"{'Lowest Stake':<20} {FormattingUtils.format_currency(stats.get('lowest_stake', 0))}")
        except Exception as e:
            logger.warning(f"Error displaying statistics: {e}")
    
    def place_bet(self) -> None:
        """Place a single bet with predefined odds."""
        try:
            if not self.current_session:
                print("No active session. Start one first.")
                input("Press Enter to continue...")
                return
            
            print("\n--- Place Bet ---")
            print(f"Game: {self.current_game_type.value.upper()}")
            print(f"Current Stake: {FormattingUtils.format_currency(self.current_gambler.current_stake)}")
            print(f"Min Bet: {FormattingUtils.format_currency(APP_CONFIG.betting.min_bet)}")
            print(f"Max Bet: {FormattingUtils.format_currency(APP_CONFIG.betting.max_bet)}")
            
            # Get betting strategy
            print("\nAvailable Betting Strategies:")
            strategies = BettingStrategyRegistry.list_all()
            for i, strat in enumerate(strategies, 1):
                print(f"{i}. {strat}")
            
            strat_choice = input("Select strategy number: ").strip()
            betting_strategy = strategies[int(strat_choice) - 1]
            
            # Get bet amount
            bet_amount = float(input(f"\nBet amount: $"))
            
            # Show available odds for the game type
            print(f"\nAvailable odds for {self.current_game_type.value.upper()}:")
            game_odds = GAME_ODDS_CONFIG.get(self.current_game_type, [1.5, 1.8, 2.0])
            for i, odd in enumerate(game_odds, 1):
                print(f"{i}. {odd}")
            
            odds_choice = input("Select odds number: ").strip()
            odds = game_odds[int(odds_choice) - 1]
            
            # Get outcome strategy
            print("\nAvailable Outcome Strategies:")
            outcomes = OutcomeStrategyRegistry.list_all()
            for i, outcome in enumerate(outcomes, 1):
                print(f"{i}. {outcome}")
            
            outcome_choice = input("Select outcome strategy number: ").strip()
            outcome_strategy = outcomes[int(outcome_choice) - 1]
            
            # Place bet
            bet = self.betting_engine.place_bet(
                self.current_session.session_id,
                self.current_gambler.gambler_id,
                bet_amount,
                betting_strategy,
                odds
            )
            
            print(f"\nBet placed!")
            print(f"Bet ID: {bet.bet_id}")
            print(f"Amount: {FormattingUtils.format_currency(bet.bet_amount)}")
            print(f"Odds: {bet.odds}")
            
            # Resolve bet
            outcome, result_amount, net_change = self.betting_engine.resolve_bet(
                bet.bet_id, outcome_strategy
            )
            
            print(f"\nBet Result: {outcome.upper()}")
            if outcome == "win":
                print(f"Winnings: {FormattingUtils.format_currency(result_amount)}")
            current_stake = float(self.current_gambler.current_stake) if self.current_gambler.current_stake else 0.0
            print(f"New Stake: {FormattingUtils.format_currency(current_stake + net_change)}")
            
            # Update session
            self.current_session.total_bets += 1
            if outcome == "win":
                self.current_session.total_wins += 1
            else:
                self.current_session.total_losses += 1
            
            # Refresh gambler data
            self.current_gambler = self.gambler_service.get_gambler(
                self.current_gambler.gambler_id
            )
            
            # Display updated statistics
            print("\n--- Updated Statistics ---")
            self.display_statistics()
            
            # Check thresholds
            within_bounds, threshold = self.stake_service.check_thresholds(
                self.current_gambler.gambler_id
            )
            
            if not within_bounds:
                print(f"\n*** Threshold reached: {threshold.upper()} ***")
                print("Session auto-ending due to threshold.")
                self.end_session()
            
            input("\nPress Enter to continue...")
        
        except GamblingAppException as e:
            logger.error(f"Betting error: {e}")
            print(f"Error: {e}")
            input("Press Enter to continue...")
        except (ValueError, IndexError) as e:
            logger.error(f"Input error: {e}")
            print("Invalid input")
            input("Press Enter to continue...")
    
    def auto_play(self) -> None:
        """Auto play multiple bets with user-selected strategy."""
        try:
            if not self.current_session:
                print("No active session. Start one first.")
                input("Press Enter to continue...")
                return
            
            # Get available strategies
            strategies = BettingStrategyRegistry.list_all()
            outcomes = OutcomeStrategyRegistry.list_all()
            odds_list = GAME_ODDS_CONFIG.get(self.current_game_type, [1.8, 2.0])
            
            print(f"\n--- Auto Play Configuration ---")
            print(f"Game: {self.current_game_type.value.upper()}")
            print(f"Current Stake: {FormattingUtils.format_currency(self.current_gambler.current_stake)}\n")
            
            # Ask for betting strategy
            print("Available Betting Strategies:")
            for i, strat in enumerate(strategies, 1):
                print(f"{i}. {strat}")
            
            strat_choice = input("Select betting strategy number: ").strip()
            try:
                betting_strategy = strategies[int(strat_choice) - 1]
            except (ValueError, IndexError):
                print("Invalid choice, using first strategy")
                betting_strategy = strategies[0]
            
            # Ask for bet amount
            print(f"\nMin Bet: {FormattingUtils.format_currency(APP_CONFIG.betting.min_bet)}")
            print(f"Max Bet: {FormattingUtils.format_currency(APP_CONFIG.betting.max_bet)}")
            bet_amount = float(input(f"Bet amount per round: $"))
            bet_amount = min(bet_amount, self.current_gambler.current_stake)
            bet_amount = max(bet_amount, APP_CONFIG.betting.min_bet)
            
            # Ask for odds selection
            print(f"\nAvailable odds for {self.current_game_type.value.upper()}:")
            for i, odd in enumerate(odds_list, 1):
                print(f"{i}. {odd}")
            
            odds_choice = input("Select odds number: ").strip()
            try:
                odds = odds_list[int(odds_choice) - 1]
            except (ValueError, IndexError):
                print("Invalid choice, using first odds")
                odds = odds_list[0]
            
            # Ask for outcome strategy
            print("\nAvailable Outcome Strategies:")
            for i, outcome in enumerate(outcomes, 1):
                print(f"{i}. {outcome}")
            
            outcome_choice = input("Select outcome strategy number: ").strip()
            try:
                outcome_strategy = outcomes[int(outcome_choice) - 1]
            except (ValueError, IndexError):
                print("Invalid choice, using first outcome strategy")
                outcome_strategy = outcomes[0]
            
            # Ask for number of bets
            num_bets = APP_CONFIG.game.auto_play_count
            try:
                user_num = int(input(f"Number of bets to place (default: {num_bets}): ").strip())
                if user_num > 0:
                    num_bets = user_num
            except ValueError:
                pass  # Use default if invalid input
            
            print(f"\n--- Starting Auto Play ({num_bets} bets) ---")
            print(f"Strategy: {betting_strategy.upper()}")
            print(f"Bet Amount: {FormattingUtils.format_currency(bet_amount)}")
            print(f"Odds: {odds}")
            print(f"Outcome Strategy: {outcome_strategy.upper()}\n")
            
            for i in range(num_bets):
                try:
                    bet = self.betting_engine.place_bet(
                        self.current_session.session_id,
                        self.current_gambler.gambler_id,
                        bet_amount,
                        betting_strategy,
                        odds
                    )
                    
                    outcome, result, change = self.betting_engine.resolve_bet(bet.bet_id, outcome_strategy)
                    
                    self.current_session.total_bets += 1
                    if outcome == "win":
                        self.current_session.total_wins += 1
                        print(f"Bet {i+1}: WIN - +{FormattingUtils.format_currency(result)}")
                    else:
                        self.current_session.total_losses += 1
                        print(f"Bet {i+1}: LOSS - -{FormattingUtils.format_currency(bet_amount)}")
                    
                    # Refresh gambler to get updated stake
                    self.current_gambler = self.gambler_service.get_gambler(
                        self.current_gambler.gambler_id
                    )
                    print(f"      Current Stake: {FormattingUtils.format_currency(self.current_gambler.current_stake)}")
                    
                    # Check thresholds
                    within_bounds, threshold = self.stake_service.check_thresholds(
                        self.current_gambler.gambler_id
                    )
                    
                    if not within_bounds:
                        print(f"\n*** Threshold reached: {threshold.upper()} ***")
                        print("Auto-play stopped due to threshold.")
                        break
                
                except Exception as e:
                    logger.error(f"Bet {i+1} error: {e}")
                    self.current_session.total_losses += 1
                    continue
            
            # Refresh gambler for final summary
            self.current_gambler = self.gambler_service.get_gambler(
                self.current_gambler.gambler_id
            )
            
            print(f"\n--- Auto Play Summary ---")
            print(f"Total Bets Placed: {self.current_session.total_bets}")
            print(f"Wins: {self.current_session.total_wins}")
            print(f"Losses: {self.current_session.total_losses}")
            print(f"Final Stake: {FormattingUtils.format_currency(self.current_gambler.current_stake)}")
            
            # Display updated lifetime statistics
            print()
            self.display_statistics()
            
            input("\nPress Enter to continue...")
        
        except Exception as e:
            logger.error(f"Auto-play error: {e}")
            print(f"Error: {e}")
            input("Press Enter to continue...")
    
    def pause_session(self) -> None:
        """Pause current session."""
        try:
            if not self.current_session:
                print("No active session to pause")
                input("Press Enter to continue...")
                return
            
            self.session_service.pause_session(self.current_session.session_id)
            print("\nSession paused")
            
            input("Press Enter to continue...")
        
        except Exception as e:
            print(f"Error: {e}")
            input("Press Enter to continue...")
    
    def resume_session(self) -> None:
        """Resume paused session."""
        try:
            if not self.current_session:
                print("No active session to resume")
                input("Press Enter to continue...")
                return
            
            self.session_service.resume_session(self.current_session.session_id)
            print("\nSession resumed")
            
            input("Press Enter to continue...")
        
        except Exception as e:
            print(f"Error: {e}")
            input("Press Enter to continue...")
    
    def end_session(self) -> None:
        """End current session."""
        try:
            if not self.current_session:
                print("No active session to end")
                input("Press Enter to continue...")
                return
            
            session_id = self.current_session.session_id
            summary = self.session_service.end_session(session_id)
            self.current_session = None  # Clear session from memory
            
            self.print_session_summary(summary)
            
            input("\nPress Enter to continue...")
        
        except Exception as e:
            logger.error(f"End session error: {e}")
            # Force clear session even if there's an error
            self.current_session = None
            print(f"Error ending session: {e}")
            input("Press Enter to continue...")
    
    def print_session_summary(self, summary) -> None:
        """Print session summary report."""
        print("\n" + "=" * 70)
        print(" " * 25 + "SESSION SUMMARY")
        print("=" * 70)
        print(f"Session ID: {summary.session_id}")
        print(f"Duration: {FormattingUtils.format_duration(summary.duration_seconds)}")
        print()
        print(f"Starting Stake: {FormattingUtils.format_currency(summary.starting_stake)}")
        print(f"Ending Stake: {FormattingUtils.format_currency(summary.ending_stake)}")
        print(f"Profit/Loss: {FormattingUtils.format_currency(summary.profit_loss)}")
        print(f"ROI: {FormattingUtils.format_percentage(summary.roi)}")
        print()
        print(f"Total Bets: {summary.total_bets}")
        print(f"Wins: {summary.total_wins}")
        print(f"Losses: {summary.total_losses}")
        print(f"Win Rate: {FormattingUtils.format_percentage(summary.win_rate)}")
        print(f"Average Bet: {FormattingUtils.format_currency(summary.average_bet)}")
        print()
        print(f"Peak Stake: {FormattingUtils.format_currency(summary.peak_stake)}")
        print(f"Lowest Stake: {FormattingUtils.format_currency(summary.lowest_stake)}")
        print(f"Volatility: {summary.volatility:.4f}")
        print("=" * 70)
    
    @staticmethod
    def clear_screen() -> None:
        """Clear console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
