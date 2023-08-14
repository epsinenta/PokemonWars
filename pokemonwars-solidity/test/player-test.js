const { expect } = require("chai");
const { loadFixture } = require("@nomicfoundation/hardhat-network-helpers");
const { deployGameAndPokemon, mintPlayerPokemon,
  pokeballPrice, deployEverythingWithMintedPokemons } = require("./fixtures");
const { time } = require("@nomicfoundation/hardhat-network-helpers");

describe("Player", function () {
  // проверка, что деплой контракта выполнен правильно
  // все переменные, которые инициализируются в контрукторе должны иметь правильные значения
  describe("Deployment", function () {
    it("Check that the player nickname is set correctly", async function () {
      const { player, playerNickname } = await loadFixture(deployGameAndPokemon);
      expect(await player.nickname()).to.be.equal(playerNickname);
    });
    it("Check that the player clientAddress is set correctly", async function () {
      const { player, playerOther, owner, otherAccount } = await loadFixture(deployGameAndPokemon);
      const [playerAddress, otherAddress] = await Promise.all([
        player.clientAddress(),
        playerOther.clientAddress()
      ]);
      expect(playerAddress).to.be.equal(owner.address);
      expect(otherAddress).to.be.equal(otherAccount.address);
    });
    it("Check that the game players is set correctly", async function () {
      const { player, playerOther, game } = await loadFixture(deployGameAndPokemon);
      const [playerOne, playerTwo] = await Promise.all([
        await game.players(0),
        await game.players(1)
      ]);
      expect(playerOne).to.be.equal(player.address);
      expect(playerTwo).to.be.equal(playerOther.address);
    });
  });
  describe("setOnline", function () {
    describe("Require", function () {
      it("Check that only the player can set online", async function () {
        const { player, owner, otherAccount } = await loadFixture(deployGameAndPokemon);
        await Promise.all([
          expect(player.connect(owner).setOnline(true)).not.to.be.reverted,
          expect(player.connect(otherAccount).setOnline(false)).to.be.revertedWith("It's not your player")
        ]);
      });
    });
    it("Check that isOnline changes", async function () {
      const { player } = await loadFixture(deployGameAndPokemon);
      await player.setOnline(true);
      expect(await player.isOnline()).to.be.equal(true);
      await player.setOnline(false);
      expect(await player.isOnline()).to.be.equal(false);
    });
  });
  describe("Donation", function () {
    it("Check that you can't buy pokeballs without a donation", async function () {
      const { game } = await loadFixture(deployGameAndPokemon);
      await Promise.all([
        expect(game.buyPokeballs(1)).to.be
          .revertedWith("You don't have enough funds on the balance"),
        expect(game.buyPokeballs(3)).to.be
          .revertedWith("You don't have enough funds on the balance")
      ]);
    });
    it("Check that you can buy pokeballs after donation", async function () {
      const { game } = await loadFixture(deployGameAndPokemon);
      await game.donate({ value: pokeballPrice })
      await expect(game.buyPokeballs(1)).not.to.be.reverted;
    });
  });
  describe("changeNickname", function () {
    describe("Require", function () {
      it("Check that only the owner can change the nickname", async function () {
        const { player, otherAccount } = await loadFixture(deployGameAndPokemon);
        await Promise.all([
          expect(player.changeNickname("Жаба")).not.to.be.reverted,
          expect(player.connect(otherAccount).changeNickname("Баба"))
            .to.be.revertedWith("It's not your player")
        ]);
      });
    });
    it("Check that nickname changes", async function () {
      const { player } = await loadFixture(deployGameAndPokemon);
      await player.changeNickname("new nickname");
      expect(await player.nickname()).to.be.equal("new nickname");
    });
  });
  describe("catchPokemon", function () {
    describe("Require", function () {
      it("Check that only the owner can catch a pokemon", async function () {
        const { pokemon, player, otherAccount } =
          await loadFixture(deployGameAndPokemon);
        await expect(player.connect(otherAccount).catchPokemon(pokemon.address))
          .to.be.revertedWith("It's not your player");
      });
      it("Check that you can only catch pokemon that do not have an owner.", async function () {
        const { player, playerOther, otherAccount, pokemon } =
          await loadFixture(deployGameAndPokemon);
        await mintPlayerPokemon(playerOther, otherAccount, pokemon);
        await expect(player.catchPokemon(pokemon.address)).to.be.revertedWith("This pokemon already have owner");
      });
    });
    it("Check that the call emits an event", async function () {
      const { player, pokemon } =
        await loadFixture(deployGameAndPokemon);
      await player.donate({ value: pokeballPrice });
      await player.buyPokeballs(1);
      await expect(player.catchPokemon(pokemon.address)).to.be
        .emit(player, "PokemonCatched").withArgs(pokemon.address)
    });
  });
  describe("attack(address,address)", function () {
    describe("Require", function () {
      it("Check that only the owner can attack other player", async function () {
        const { player, playerOther, otherAccount, pokemon } =
          await loadFixture(deployEverythingWithMintedPokemons);
        await Promise.all([
          expect(player.connect(otherAccount)['attack(address,address)'](pokemon.address, playerOther.address)).
            to.be.revertedWith("It's not your player"),
          expect(playerOther['attack(address,address)'](pokemon.address, playerOther.address)).
            to.be.revertedWith("It's not your player")
        ]);
      });
      it("Check that only you can attack with your pokemon", async function () {
        const { player, playerOther, otherAccount, pokemon, pokemonCopy } =
          await loadFixture(deployEverythingWithMintedPokemons);
        await Promise.all([
          expect(player['attack(address,address)'](pokemonCopy.address, playerOther.address)).
            to.be.revertedWith("It's not your pokemon"),
          expect(playerOther.connect(otherAccount)['attack(address,address)'](pokemon.address, playerOther.address)).
            to.be.revertedWith("It's not your pokemon")
        ]);
      });
      it("Check that the other player must be a smart contract", async function () {
        const { player, playerOther, owner, otherAccount, pokemon, pokemonCopy } =
          await loadFixture(deployEverythingWithMintedPokemons);
        await Promise.all([
          expect(player['attack(address,address)'](pokemon.address, otherAccount.address)).
            to.be.revertedWith("Other player should be smart contract"),
          expect(playerOther.connect(otherAccount)['attack(address,address)'](pokemonCopy.address, owner.address)).
            to.be.revertedWith("Other player should be smart contract")
        ]);
      });
      it("Check that onPlayerAttack cannot call the account", async function () {
        const { playerOther, player, otherAccount, pokemon } =
          await loadFixture(deployGameAndPokemon);
        await Promise.all([
          expect(player.onPlayerAttack(pokemon.address)).
            to.be.revertedWith("Sender should be Player"),
          expect(playerOther.onPlayerAttack(pokemon.address)).
            to.be.revertedWith("Sender should be Player"),
          expect(player.connect(otherAccount).onPlayerAttack(pokemon.address)).
            to.be.revertedWith("Sender should be Player"),
          expect(playerOther.connect(otherAccount).onPlayerAttack(pokemon.address)).
            to.be.revertedWith("Sender should be Player"),
        ]);
      });
      it("Check that the other player must be online", async function () {
        const { player, playerOther, owner, otherAccount, pokemon, pokemonCopy } =
          await loadFixture(deployGameAndPokemon);
        await Promise.all([
          mintPlayerPokemon(player, owner, pokemon),
          mintPlayerPokemon(playerOther, otherAccount, pokemonCopy),
          player.setOnline(true)
        ]);
        await expect(player['attack(address,address)'](pokemon.address, playerOther.address)).
          to.be.revertedWith("Other player should be online")
      });
    });
    it("Check that the call emits an event", async function () {
      const { player, playerOther, pokemon } =
        await loadFixture(deployEverythingWithMintedPokemons);
      await expect(player['attack(address,address)'](pokemon.address, playerOther.address)).
        to.be.emit(player, "StartingBattle").withArgs(pokemon.address, playerOther.address);
    });
    it("Check that inCombat and currentDroppedPokemon is set correctly", async function () {
      const { player, playerOther, pokemon } =
        await loadFixture(deployEverythingWithMintedPokemons);
      await player['attack(address,address)'](pokemon.address, playerOther.address);
      const [playerInCombat, playerCurrentDrop, otherInCombat, otherAttacker] = await Promise.all([
        player.inCombat(),
        player.currentDroppedPokemon(),
        playerOther.inCombat(),
        playerOther.attackerPokemon(),
      ]);
      expect(playerInCombat).to.be.equal(true);
      expect(playerCurrentDrop).to.be.equal(pokemon.address);
      expect(otherInCombat).to.be.equal(true);
      expect(otherAttacker).to.be.equal(pokemon.address);
    });
  });
  describe("attack()", function () {
    describe("Require", function () {
      it("Check that you should throw pokemon before attack", async function () {
        const { player, playerOther, pokemon } =
          await loadFixture(deployEverythingWithMintedPokemons);
        await player["attack(address,address)"](pokemon.address, playerOther.address);
        await expect(playerOther["attack()"]()).to.be.revertedWith("You didn't throw pokemon");
      });
    });
    it("Check that the attack reduces health", async function () {
      const { player, playerOther, pokemon, pokemonCopy, otherAccount } =
        await loadFixture(deployEverythingWithMintedPokemons);
      await player["attack(address,address)"](pokemon.address, playerOther.address);
      const [pokemonCopyHealth1] = await Promise.all([
        pokemonCopy.health(),
        playerOther.connect(otherAccount).throwPokemon(pokemonCopy.address)
      ]);
      await player["attack()"]();
      const pokemonCopyHealth2 = await pokemonCopy.health();
      expect(pokemonCopyHealth2 - pokemonCopyHealth1).to.be.below(0);
    });
    it("Check that after killing a pokemon it is transferred to the killer", async function () {
      const { player, playerOther, otherAccount, pokemon, pokemonCopy,
        pokemonDamage, pokemonDefense, game } =
        await loadFixture(deployEverythingWithMintedPokemons);
      await player["attack(address,address)"](pokemon.address, playerOther.address);
      await playerOther.connect(otherAccount).throwPokemon(pokemonCopy.address);
      for (let pokemonCopyHealth = 100; pokemonCopyHealth > 0;) {
        await player["attack()"]();
        pokemonCopyHealth = Math.max(0,
          pokemonCopyHealth - (pokemonDamage - pokemonDefense));
        if (pokemonCopyHealth != 0) {
          await playerOther["attack()"]();
        }
      }
      expect(await pokemonCopy.isAlive()).to.be.false;
      expect(await game.getPokemonPlayer(pokemonCopy.address)).to.be.equal(player.address);
    });
  });
  describe("throwPokemon", function () {
    describe("Require", function () {
      it("Check that only the owner can throw a pokemon", async function () {
        const { player, playerOther, pokemon, pokemonCopy } =
          await loadFixture(deployEverythingWithMintedPokemons);
        await player["attack(address,address)"](pokemon.address, playerOther.address);
        await expect(playerOther.throwPokemon(pokemonCopy.address))
          .to.be.revertedWith("It's not your player");
      });
      it("Check that you can throw pokemon only when in combat", async function () {
        const { player, pokemon } =
          await loadFixture(deployGameAndPokemon);
        await player.setOnline(true);
        await expect(player.throwPokemon(pokemon.address))
          .to.be.revertedWith("You are not in combat");
      });
      it("Check that you can throw only your pokemon", async function () {
        const { player, playerOther, otherAccount, pokemon } =
          await loadFixture(deployEverythingWithMintedPokemons);
        await player["attack(address,address)"](pokemon.address, playerOther.address);
        await expect(playerOther.connect(otherAccount).throwPokemon(pokemon.address))
          .to.be.revertedWith("It's not your pokemon");
      });
      it("Check that there can only be one pokemon in the combat", async function () {
        const { player, playerOther, otherAccount, pokemon, pokemonCopy } =
          await loadFixture(deployEverythingWithMintedPokemons);
        await player["attack(address,address)"](pokemon.address, playerOther.address);
        await playerOther.connect(otherAccount).throwPokemon(pokemonCopy.address);
        await expect(playerOther.connect(otherAccount).throwPokemon(pokemonCopy.address)).
          to.be.revertedWith("Your pokemon already in battle");
      });
    });
    it("Check that the call emits an event", async function () {
      const { player, playerOther, otherAccount, pokemon, pokemonCopy } =
        await loadFixture(deployEverythingWithMintedPokemons);
      await player["attack(address,address)"](pokemon.address, playerOther.address);
      await expect(playerOther.connect(otherAccount).throwPokemon(pokemonCopy.address))
        .to.be.emit(playerOther, "PokemonThrown").withArgs(pokemonCopy.address);
    });
  });
  describe("returnPokemon", function () {
    it("Check that you can throw after return", async function () {
      const { player, playerOther, otherAccount, pokemon, pokemonCopy } =
        await loadFixture(deployEverythingWithMintedPokemons);
      await player["attack(address,address)"](pokemon.address, playerOther.address);
      await playerOther.connect(otherAccount).throwPokemon(pokemonCopy.address);
      await playerOther.connect(otherAccount).returnPokemon();
      await expect(playerOther.connect(otherAccount).throwPokemon(pokemonCopy.address)).
        not.to.be.reverted;
    });
    it("Check that the return emits an event", async function () {
      const { player, playerOther, otherAccount, pokemon, pokemonCopy } =
        await loadFixture(deployEverythingWithMintedPokemons);
      await player["attack(address,address)"](pokemon.address, playerOther.address);
      await playerOther.connect(otherAccount).throwPokemon(pokemonCopy.address);
      await expect(playerOther.connect(otherAccount).returnPokemon())
        .to.be.emit(playerOther, "PokemonReturned").withArgs(pokemonCopy.address);
    });
  });
  describe("healPokemon", function () {
    describe("Require", function () {
      it("Check that only the owner can heal a pokemon", async function () {
        const { player, playerOther, otherAccount, pokemon, pokemonCopy } =
          await loadFixture(deployEverythingWithMintedPokemons);
        await player["attack(address,address)"](pokemon.address, playerOther.address);
        await playerOther.connect(otherAccount).throwPokemon(pokemonCopy.address);
        await player["attack()"]();
        await expect(playerOther.healPokemon(pokemonCopy.address))
          .to.be.revertedWith("It's not your player")
      });
      it("Check that you can't treat your pokemon too often", async function () {
        const { player, playerOther, otherAccount, pokemon, pokemonCopy } =
          await loadFixture(deployEverythingWithMintedPokemons);
        await player["attack(address,address)"](pokemon.address, playerOther.address);
        await playerOther.connect(otherAccount).throwPokemon(pokemonCopy.address);
        await player["attack()"]();
        await Promise.all([
          playerOther["attack()"](),
          expect(playerOther.connect(otherAccount).healPokemon(pokemonCopy.address))
            .not.to.be.reverted
        ]);
        await player["attack()"]();
        await expect(playerOther.connect(otherAccount).healPokemon(pokemonCopy.address))
          .to.be.revertedWith("You need to wait to heal the pokemon again");
        await time.increase(5 * 60); // 5 minutes
        await expect(playerOther.connect(otherAccount).healPokemon(pokemonCopy.address))
          .not.to.be.reverted;
      });
    });
    it("Check that the call emits an event", async function () {
      const { player, playerOther, otherAccount, pokemon, pokemonCopy } =
        await loadFixture(deployEverythingWithMintedPokemons);
      await player["attack(address,address)"](pokemon.address, playerOther.address);
      await playerOther.connect(otherAccount).throwPokemon(pokemonCopy.address);
      await player["attack()"]();
      await expect(playerOther.connect(otherAccount).healPokemon(pokemonCopy.address))
        .to.be.emit(playerOther, "PokemonHealed").withArgs(pokemonCopy.address);
    });
    it("Check that the call heals a pokemon", async function () {
      const { player, playerOther, otherAccount, pokemon, pokemonCopy } =
        await loadFixture(deployEverythingWithMintedPokemons);
      await player["attack(address,address)"](pokemon.address, playerOther.address);
      await playerOther.connect(otherAccount).throwPokemon(pokemonCopy.address);
      await player["attack()"]();
      await playerOther.connect(otherAccount).healPokemon(pokemonCopy.address);
      expect(await pokemonCopy.health()).to.be.equal(100)
    });
  });
});
