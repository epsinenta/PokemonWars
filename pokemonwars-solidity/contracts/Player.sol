// SPDX-License-Identifier: MIT

pragma solidity 0.8.15;
import "./Pokemon.sol";
import "./Game.sol";

contract Player {
    string public nickname;
    bool public isOnline;
    bool public inCombat;
    address public currentDroppedPokemon;
    IPokemon public attackerPokemon;
    uint256 healTimer;
    address public clientAddress;
    Game game;
    bool myTurn = false;

    event PokemonCatched(IPokemon selfPokemon);
    event PokemonRemoved(IPokemon selfPokemon);
    event PokemonHealed(IPokemon selfPokemon);
    event PlayerAttacked(IPokemon attackPokemon);
    event StartingBattle(IPokemon attackerPokemon, Player otherPlayer);
    event PokemonThrown(IPokemon selfPokemon);
    event PokemonReturned(IPokemon selfPokemon);

    constructor(
        string memory _nickname,
        address _clientAddress,
        address _gameAddress
    ) {
        clientAddress = _clientAddress;
        nickname = _nickname;
        game = Game(_gameAddress);
        require(game.token().isApprovedForAll(_clientAddress, _gameAddress), "You didn't set approval for game on token.");
        game.addPlayer();
    }

    function setOnline(bool newOnline) public {
        require(msg.sender == clientAddress, "It's not your player");
        isOnline = newOnline;
    }

    function donate() public payable {
        game.donate{value: msg.value}();
    }

    function buyPokeballs(uint256 amount) public {
        game.buyPokeballs(amount);
    }

    function changeNickname(string calldata newNickname) public {
        require(msg.sender == clientAddress, "It's not your player");
        nickname = newNickname;
    }

    function catchPokemon(address addressPokemon) public {
        require(msg.sender == clientAddress, "It's not your player");
        require(
            game.getPokemonPlayer(addressPokemon) == address(0),
            "This pokemon already have owner"
        );
        game.mintPokemon(address(this), addressPokemon);
        emit PokemonCatched(IPokemon(addressPokemon));
    }

    function dropPokemon(address enemy, address selfPokemon) public {
        require(
            msg.sender.codehash == address(this).codehash,
            "This function should be called only by other player contract."
        );
        require(
            selfPokemon.code.length != 0,
            "Address should be smart contract"
        );
        inCombat = false;
        myTurn = false;
        emit PokemonRemoved(IPokemon(selfPokemon));
        game.transferPokemon(address(this), enemy, selfPokemon, 1, "");
        currentDroppedPokemon = address(0);
    }

    function healPokemon(address selfPokemon) public {
        require(msg.sender == clientAddress, "It's not your player");
        require(
            selfPokemon.code.length != 0,
            "Address should be smart contract"
        );
        require(
            block.timestamp - healTimer > 5 minutes,
            "You need to wait to heal the pokemon again"
        );
        healTimer = block.timestamp;
        IPokemon pokemon = IPokemon(selfPokemon);
        emit PokemonHealed(pokemon);
        pokemon.heal();
    }

    function setTurn() external{
        myTurn = true;
    }

    function attack(address selfPokemon, address otherPlayer) public {
        require(msg.sender == clientAddress, "It's not your player");
        require(
            game.getPokemonPlayer(selfPokemon) == address(this),
            "It's not your pokemon"
        );
        require(
            otherPlayer.code.length != 0,
            "Other player should be smart contract"
        );
        require(
            selfPokemon.code.length != 0,
            "Pokemon address should be smart contract"
        );
        Player player = Player(otherPlayer);
        require(player.isOnline(), "Other player should be online");
        require(!player.inCombat(), "Other player already in combat");
        IPokemon pokemon = IPokemon(selfPokemon);
        emit StartingBattle(pokemon, player);
        player.onPlayerAttack(pokemon);
        inCombat = true;
        currentDroppedPokemon = selfPokemon;
    }

    // I choose you...
    function throwPokemon(address selfPokemon) public {
        require(msg.sender == clientAddress, "It's not your player");
        require(inCombat, "You are not in combat");
        require(
            game.getPokemonPlayer(selfPokemon) == address(this),
            "It's not your pokemon"
        );
        require(
            currentDroppedPokemon == address(0),
            "Your pokemon already in battle"
        );
        currentDroppedPokemon = selfPokemon;
        IPokemon selfPokemonInterface = IPokemon(selfPokemon);
        Player(game.getPokemonPlayer(address(attackerPokemon))).onPlayerAttack(selfPokemonInterface);
        emit PokemonThrown(selfPokemonInterface);
    }

    function returnPokemon() public {
        emit PokemonReturned(IPokemon(currentDroppedPokemon));
        currentDroppedPokemon = address(0);
    }

    function attack() public {
        require(myTurn, "It's not your turn now");
        require(
            currentDroppedPokemon != address(0),
            "You didn't throw pokemon"
        );
        myTurn = false;
        IPokemon selfPokemon = IPokemon(currentDroppedPokemon);
        selfPokemon.attack(attackerPokemon);
        Player attacker = Player(
            game.getPokemonPlayer(address(attackerPokemon))
        );
        attacker.onPlayerAttack(selfPokemon);
        if (!attackerPokemon.isAlive()) {
            address enemyAddress = game.getPokemonPlayer(
                address(attackerPokemon)
            );
            Player enemyPlayer = Player(enemyAddress);
            enemyPlayer.dropPokemon(
                address(address(this)),
                address(attackerPokemon)
            );
            inCombat = false;
        }
    }

    function onPlayerAttack(IPokemon _attackerPokemon) public {
        require(
            msg.sender.codehash == address(this).codehash,
            "Sender should be Player"
        );
        inCombat = true;
        myTurn = true;
        attackerPokemon = _attackerPokemon;
        emit PlayerAttacked(_attackerPokemon);
    }
}