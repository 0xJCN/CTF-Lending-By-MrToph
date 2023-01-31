# @version ^0.3.7

from vyper.interfaces import ERC20 as IERC20

interface IUniswapV2Pair:
    def place_holder(): nonpayable

interface ILending:
    def place_holder(): nonpayable

owner: immutable(address)

pair: IUniswapV2Pair
ctf: IERC20 
usd: IERC20
lending: ILending

@external
@payable
def __init__(_pair: IUniswapV2Pair, _ctf: IERC20, _usd: IERC20, _lending: ILending):
    owner = msg.sender
    self.pair = _pair
    self.ctf = _ctf
    self.usd = _usd 
    self.lending = _lending

@external
def attack():
    assert msg.sender == owner, "!owner"
    # exploit 
