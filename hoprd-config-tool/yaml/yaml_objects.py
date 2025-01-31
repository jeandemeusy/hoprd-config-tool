from .parser import YAMLParser

class IPv4(YAMLParser):
    scalar = True
    ipv4: str

class Token(YAMLParser):
    scalar = True
    token: str

class Aggregating(YAMLParser):
    aggregation_threshold: int
    unrealized_balance_ratio: float
    aggregate_on_channel_close: bool

class AutoFunding(YAMLParser):
    funding_amount: str
    min_stake_threshold: str

class AutoRedeeming(YAMLParser):
    redeem_only_aggregated: bool
    minimum_redeem_ticket_value: str

class ClosureFinalizer(YAMLParser):
    max_closure_overdue: int