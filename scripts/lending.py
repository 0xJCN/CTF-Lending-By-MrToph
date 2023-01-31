from ape import accounts, project
from .utils.helper import w3


def main():
    # --- BEFORE EXPLOIT --- #
    print("\n--- Setting up scenario ---\n")

    # get accounts
    deployer = accounts.test_accounts[0]
    attacker = accounts.test_accounts[1]
    victim = accounts.test_accounts[2]

    # deploy token contracts
    print("\n--- Deploying Token Contracts ---\n")
    usd = project.ERC20.deploy("USD Token", "USD", 18, sender=deployer)
    ctf = project.ERC20.deploy("CTF Token", "CTF", 18, sender=deployer)

    # deploy uniswap contracts
    print("\n--- Deploying Uniswap Contracts ---\n")
    factory = project.UniswapV2Factory.deploy(deployer.address, sender=deployer)
    pair = project.IUniswapV2Pair.at(
        factory.createPair(ctf.address, usd.address, sender=deployer).return_value
    )

    # create lending protocol
    lending = project.LendingProtocol.deploy(
        ctf.address, usd.address, pair.address, sender=deployer
    )

    # add initial liquidity at a CTF price (denoted in USD) of 1_000
    usd.mint(pair.address, w3.to_wei(1_000, "ether"), sender=deployer)
    ctf.mint(pair.address, w3.to_wei(1, "ether"), sender=deployer)
    pair.mint(deployer.address, sender=deployer)

    # victim deposits 50k USD
    victim_amount = w3.to_wei(50_000, "ether")
    usd.mint(victim.address, victim_amount, sender=deployer)
    usd.approve(lending.address, victim_amount, sender=victim)
    lending.deposit(victim.address, usd.address, victim_amount, sender=victim)

    # send attacker 10k of USD and CTF tokens each
    usd.mint(attacker.address, w3.to_wei(10_000, "ether"), sender=deployer)
    ctf.mint(attacker.address, w3.to_wei(10, "ether"), sender=deployer)

    # define initial balance for attacker and lending contract
    attacker_initial_bal = usd.balanceOf(attacker.address) / 10**18
    lending_initial_bal = usd.balanceOf(lending.address) / 10**18

    print(
        f"\n--- \nInitial Balances:\n⇒ Attacker: {attacker_initial_bal}\n⇒ Lending Contract: {lending_initial_bal}\n---\n"
    )

    # --- EXPLOIT GOES HERE --- #
    print("\n--- Initiating exploit... ---\n")

    # exploit

    # --- AFTER EXPLOIT --- #
    print("\n--- After exploit: Attacker drained all USD from Lending Contract ---\n")

    # define initial balance for attacker and lending contract
    attacker_final_bal = usd.balanceOf(attacker.address) / 10**18
    lending_final_bal = usd.balanceOf(lending.address) / 10**18

    print(
        f"\n--- \nFinal Balances:\n⇒ Attacker: {attacker_final_bal}\n⇒ Lending Contract: {lending_final_bal}\n---\n"
    )

    # contract with victim's USD deposit should be empty after attack
    assert usd.balanaceOf(lending.address) == 0
    assert usd.balanceOf(attacker.address) == w3.to_wei(60_000, "ether")

    print("\n--- 🥂 Challenge Completed! 🥂---\n")


if __name__ == "__main__":
    main()
