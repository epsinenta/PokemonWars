// SPDX-License-Identifier: MIT
pragma solidity 0.8.15;
import "./Game.sol";

enum SpecialPokemonType {
    Normal,
    Fire,
    Water,
    Grass,
    Flying,
    Fighting,
    Poison,
    Electric,
    Ground,
    Rock,
    Psychic,
    Ice,
    Bug,
    Ghost,
    Steel,
    Dragon,
    Dark,
    Fairy
}

interface IPokemon {
    function attack(IPokemon otherPokemon) external;

    function defend(uint8, SpecialPokemonType) external;

    function isAlive() external view returns (bool);

    function heal() external;

    function pokemonId() external returns(uint256);
}

contract Pokemon is IPokemon {
    uint256 public pokemonId;
    string public name;
    uint8 public damage;
    uint8 public health;
    uint8 public defense;
    bool alive = true;
    IGame game;

    SpecialPokemonType public typePokemon;
    SpecialPokemonType typeAdvantages;
    SpecialPokemonType typeWeaknesses;

    constructor(
        uint256 _pokemonId,
        string memory _name,
        uint8 _damage,
        uint8 _defense,
        SpecialPokemonType _pokemontype,
        SpecialPokemonType _advantages,
        SpecialPokemonType _weaknesses,
        address _game
    ) {
        pokemonId = _pokemonId;
        name = _name;
        damage = _damage;
        health = 100;
        defense = _defense;
        typePokemon = _pokemontype;
        typeAdvantages = _advantages;
        typeWeaknesses = _weaknesses;
        game = IGame(_game);
    }

    function attack(IPokemon otherPokemon) external {
        require(
            otherPokemon.isAlive(),
            "The pokemon you want to attack is dead"
        );
        require(isAlive(), "Your pokemon is dead");
        require(
            game.getPokemonPlayer(address(this)) == msg.sender,
            "msg.sender != player of pokemon"
        );
        otherPokemon.defend(damage, typePokemon);
    }

    function defend(uint8 _damage, SpecialPokemonType typeOtherPokemon) public {
        if (typeOtherPokemon == typeAdvantages) {
            _damage = (_damage * 3) / 4;
        }

        if (typeOtherPokemon == typeWeaknesses) {
            _damage = (_damage * 5) / 4;
        }
        if (_damage > defense) {
            _damage -= defense;
        } else {
            _damage = 0;
        }
        if (health > _damage) {
            health -= _damage;
        } else {
            health = 0;
            alive = false;
        }
    }

    function isAlive() public view returns (bool) {
        return alive;
    }

    function heal() public {
        require(
            game.getPokemonPlayer(address(this)) == msg.sender,
            "Call heal() in Player, not in pokemon"
        );
        uint8 newHealth = health + 30;
        health = newHealth > 100 ? 100 : newHealth;
        alive = true;
    }
}