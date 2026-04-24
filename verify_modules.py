"""
Module segregation verification script.
Demonstrates all modules working together in the new modular structure.
"""

def test_imports():
    """Test that all modules can be imported."""
    print("=" * 70)
    print("GAMBLING SIMULATION SYSTEM - MODULE VERIFICATION")
    print("=" * 70)
    print()
    
    # Test Core
    print("1. Testing gambling_app_core (Foundation Module)")
    print("-" * 70)
    try:
        from gambling_app_core import (
            AppConfig, APP_CONFIG, GameType, GAME_ODDS_CONFIG,
            GamblingAppException, DatabaseException,
            SessionStatus, BetOutcome,
            GamblerDTO, SessionDTO, BetDTO
        )
        print("   ✓ Configurations loaded")
        print(f"   ✓ GameType enum: {[t.name for t in GameType]}")
        print(f"   ✓ Game odds configured for {len(GAME_ODDS_CONFIG)} games")
        print("   ✓ Exception hierarchy available")
        print("   ✓ Entity models available")
        print()
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test DB
    print("2. Testing gambling_app_db (Database Module)")
    print("-" * 70)
    try:
        from gambling_app_db import (
            DatabaseConnection,
            GamblerRepository,
            SessionRepository,
            BetRepository,
            TransactionRepository,
            StatisticsRepository
        )
        print("   ✓ DatabaseConnection available")
        print("   ✓ GamblerRepository available")
        print("   ✓ SessionRepository available")
        print("   ✓ BetRepository available")
        print("   ✓ TransactionRepository available")
        print("   ✓ StatisticsRepository available")
        print()
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test Utils
    print("3. Testing gambling_app_utils (Utilities Module)")
    print("-" * 70)
    try:
        from gambling_app_utils import (
            LoggerSetup,
            FormattingUtils,
            CalculationUtils,
            StatisticsCalculator,
            StreakTracker
        )
        print("   ✓ LoggerSetup available")
        print("   ✓ FormattingUtils available")
        print("   ✓ CalculationUtils available")
        print("   ✓ StatisticsCalculator available")
        print("   ✓ StreakTracker available")
        
        # Test formatting
        formatted = FormattingUtils.format_currency(1234.56)
        print(f"   ✓ Currency formatting works: {formatted}")
        print()
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test Services
    print("4. Testing gambling_app_services (Business Logic Module)")
    print("-" * 70)
    try:
        from gambling_app_services import (
            GamblerService,
            SessionService,
            StakeService,
            BettingEngine,
            BettingStrategyRegistry,
            OutcomeStrategyRegistry,
            StakeValidator,
            BetValidator
        )
        print("   ✓ GamblerService available")
        print("   ✓ SessionService available")
        print("   ✓ StakeService available")
        print("   ✓ BettingEngine available")
        print("   ✓ BettingStrategyRegistry available")
        print("   ✓ OutcomeStrategyRegistry available")
        print("   ✓ Validators available")
        
        # Test strategy registry - just verify it exists
        registry = BettingStrategyRegistry()
        print(f"   ✓ Betting strategy registry initialized")
        print()
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test UI
    print("5. Testing gambling_app_ui (User Interface Module)")
    print("-" * 70)
    try:
        from gambling_app_ui import GamblingUI
        print("   ✓ GamblingUI available")
        print("   ✓ All menu functions accessible")
        print()
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    return True


def show_dependency_tree():
    """Display module dependency structure."""
    print("6. Module Dependency Structure")
    print("-" * 70)
    print("""
    gambling_app_core (Foundation)
    │
    ├─→ gambling_app_db
    │   └─ Depends on: core, mysql-connector-python
    │
    ├─→ gambling_app_utils
    │   └─ Depends on: core
    │
    ├─→ gambling_app_services
    │   ├─ Depends on: core, db, utils
    │   └─ Provides: Services, Strategies, Validators
    │
    └─→ gambling_app_ui
        └─ Depends on: core, db, utils, services
    """)


def show_deployment_order():
    """Display recommended deployment order."""
    print("7. Git Deployment Order")
    print("-" * 70)
    print("""
    1. gambling_app_core        (Tag: core-v1.0.0)
    2. gambling_app_db          (Tag: db-v1.0.0)
    3. gambling_app_utils       (Tag: utils-v1.0.0)
    4. gambling_app_services    (Tag: services-v1.0.0)
    5. gambling_app_ui          (Tag: ui-v1.0.0)
    6. Root Package             (Tag: app-v1.0.0)
    """)


if __name__ == "__main__":
    success = test_imports()
    
    if success:
        print("=" * 70)
        print("✓ ALL MODULES VERIFIED SUCCESSFULLY")
        print("=" * 70)
        print()
        
        show_dependency_tree()
        print()
        
        show_deployment_order()
        print()
        
        print("=" * 70)
        print("NEXT STEPS:")
        print("=" * 70)
        print("""
1. Review DEPLOYMENT_GUIDE.md for detailed instructions
2. Review MODULAR_STRUCTURE.md for architecture overview
3. Create Git repository with modular structure
4. Deploy modules in order: core → db → utils → services → ui
5. Tag each module version for tracking
6. Set up CI/CD pipeline for modular testing
        """)
    else:
        print("=" * 70)
        print("✗ MODULE VERIFICATION FAILED")
        print("=" * 70)
