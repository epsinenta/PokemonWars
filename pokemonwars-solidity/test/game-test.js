const { expect } = require("chai");
const { ethers } = require("hardhat");
const { loadFixture } = require("@nomicfoundation/hardhat-network-helpers");
const { deployGameAndPokemon, mintPokemon, pokeballPrice } = require("./fixtures");

describe("Game", function () {
  // проверка, что деплой контракта выполнен правильно
  // все переменные, которые инициализируются в контрукторе
  // должны иметь правильные значения
  describe("Deployment", function () {
    it("Check that the game owner is set correctly", async function () {
      const { game, owner } = await loadFixture(deployGameAndPokemon);
      expect(await game.owner()).to.be.equal(owner.address);
    });
    it("Check that the game.token name is set correctly", async function () {
      const { gameName, token } = await loadFixture(deployGameAndPokemon);
      expect(await token.name()).to.be.equal(gameName);
    });
    it("Check that the game.token symbol is set correctly", async function () {
      const { gameSymbol, token } = await loadFixture(deployGameAndPokemon);
      expect(await token.symbol()).to.be.equal(gameSymbol);
    });
  });

  // проверка доната и покупки pokeball-ов
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
    it("Check that you can buy pokeballs with a donation",
      async function () {
        const { game } = await loadFixture(deployGameAndPokemon);
        await game.donate({ value: pokeballPrice });
        await expect(game.buyPokeballs(1)).not.to.be.reverted;
      });
    it("Check that you can buy more than one pokeball for a large donation.",
      async function () {
        const { game } = await loadFixture(deployGameAndPokemon);
        await game.donate({ value: pokeballPrice*3 });
        await expect(game.buyPokeballs(3)).not.to.be.reverted;
      });
  });

  // проверка эмиссии
  describe("Emission", async function () {
    describe("Mint", function () {
      // проверка, корректной работы require
      describe("Require", function () {
        it("Check that you can mint pokemon if you have pokeball",
          async function () {
            const { game, pokemon, player } = await loadFixture(deployGameAndPokemon);
            await game.donate({ value: pokeballPrice });
            await game.buyPokeballs(1);
            await expect(game.mintPokemon(player.address, pokemon.address))
              .not.to.be.reverted;
          });
        it("Check that you can(not) mint pokemon if you do(not) have pokeballs",
          async function () {
            const { game, pokemon, player } = await loadFixture(deployGameAndPokemon);
            await expect(game.mintPokemon(player.address, pokemon.address)).to
              .be.revertedWith("You don't have enough pokeballs");
            await game.donate({ value: pokeballPrice });
            await game.buyPokeballs(1);
            await expect(game.mintPokemon(player.address, pokemon.address))
              .not.to.be.reverted;
          });
      });
      it("Check that getPokemonPlayer should be owner of pokemon",
        async function () {
          const { game, pokemon, player, owner } =
            await loadFixture(deployGameAndPokemon);
          await mintPokemon(game, player, owner, pokemon);
          expect(await game.getPokemonPlayer(pokemon.address)).to
            .be.equal(player.address);
        });
    });
    describe("Mint a batch", function () {
      // проверка, корректной работы require
      describe("Require", function () {
        it("Check that you can(not) mint pokemon if you do(not) have pokeballs",
          async function () {
            const { game, pokemon, pokemonCopy, player } =
              await loadFixture(deployGameAndPokemon);
            await expect(game.mintBatchPokemon(
              player.address, [pokemon.address, pokemonCopy.address], [1, 1]
            )).to.be.revertedWith("You don't have enough pokeballs");
            await game.donate(
              { value: pokeballPrice*2 }
            );
            await game.buyPokeballs(2);
            await expect(game.mintBatchPokemon(
              player.address, [pokemon.address, pokemonCopy.address], [1, 1]
            )).not.to.be.reverted;
          });

        it("Check that only if the length of the token IDs is equal to " +
          "the length of the number of tokens you can emit pokemons", async function () {
            const { game, pokemon, pokemonCopy, owner, player } =
              await loadFixture(deployGameAndPokemon);
            await game.connect(owner).donate(
              { value: pokeballPrice*2 }
            );
            await game.connect(owner).buyPokeballs(2);
            await Promise.all([
              expect(game.mintBatchPokemon(player.address,
                [pokemon.address, pokemonCopy.address], [1]))
                .to.be.revertedWith(
                  "The length of the tokenIds array is not equal to " +
                  "the length of the amounts array"
                ),
              expect(game.mintBatchPokemon(player.address,
                [pokemon.address], [1, 1]))
                .to.be.revertedWith(
                  "The length of the tokenIds array is not equal to " +
                  "the length of the amounts array"
                ),
              expect(game.mintBatchPokemon(player.address,
                [pokemon.address, pokemonCopy.address], [1, 1]))
                .not.to.be.reverted
            ]);
          });
      });
      it("Check that getPokemonPlayer should be owner of pokemon",
        async function () {
          const { game, pokemon, pokemonCopy, owner, player } =
            await loadFixture(deployGameAndPokemon);
          await game.connect(owner).donate(
            { value: pokeballPrice*2 }
          );
          await game.connect(owner).buyPokeballs(2);
          await game.mintBatchPokemon(
            player.address, [pokemon.address, pokemonCopy.address], [1, 1]
          );
          let [playerOne, playerCopy] = await Promise.all([
            game.getPokemonPlayer(pokemon.address),
            game.getPokemonPlayer(pokemonCopy.address),
          ]);
          expect(playerOne).to.be.equal(player.address);
          expect(playerCopy).to.be.equal(player.address);
        });
    });
  });

  // проверка трансфера покемонов
  describe("Transfer", function () {
    describe("transfer", function () {
      it("Check that the owners change their ownership when transferring",
        async function () {
          const { game, pokemon, owner, player, playerOther } =
            await loadFixture(deployGameAndPokemon);
          await mintPokemon(game, player, owner, pokemon);
          await game.connect(owner).transferPokemon(
            player.address, playerOther.address,
            pokemon.address, 1, []
          );
          expect(await game.getPokemonPlayer(pokemon.address)).to
            .be.equal(playerOther.address);
        });
    });
    describe("Transfer a batch", function () {
      describe("Require", function () {
        it("Check that only if the length of the token IDs is equal to " +
          "the length of the number of tokens you can transfer pokemons",
          async function () {
            const { game, pokemon, pokemonCopy, owner, player, playerOther } =
              await loadFixture(deployGameAndPokemon);
            await game.connect(owner).donate(
              { value: pokeballPrice*2 }
            );
            await game.connect(owner).buyPokeballs(2);
            await game.mintBatchPokemon(player.address,
              [pokemon.address, pokemonCopy.address], [1, 1]);
            await Promise.all([
              expect(game.transferBatchPokemon(player.address, playerOther.address,
                [pokemon.address, playerOther.address], [1], []))
                .to.be.revertedWith(
                  "The length of the addressesPokemon array is not equal to " +
                  "the length of the amounts array"
                ),
              expect(game.transferBatchPokemon(player.address, playerOther.address,
                [pokemon.address], [1, 1], []))
                .to.be.revertedWith(
                  "The length of the addressesPokemon array is not equal to " +
                  "the length of the amounts array"
                ),
              expect(game.transferBatchPokemon(player.address, playerOther.address,
                [pokemon.address, pokemonCopy.address], [1, 1], []))
                .not.to.be.reverted
            ]);
          });
      });

      it("Check that the owners change their ownership when transferring a batch",
        async function () {
          const { game, pokemon, pokemonCopy, owner, player, playerOther } =
            await loadFixture(deployGameAndPokemon);
          await game.connect(owner).donate(
            { value: pokeballPrice*2 }
          );
          await game.connect(owner).buyPokeballs(2);
          await game.mintBatchPokemon(
            player.address, [pokemon.address, pokemonCopy.address], [1, 1]
          );
          await game.connect(owner).transferBatchPokemon(
            player.address, playerOther.address,
            [pokemon.address, pokemonCopy.address], [1, 1], []
          );
          let [playerOne, playerCopy] = await Promise.all([
            game.getPokemonPlayer(pokemon.address),
            game.getPokemonPlayer(pokemonCopy.address),
          ]);
          expect(playerOne).to.be.equal(playerOther.address);
          expect(playerCopy).to.be.equal(playerOther.address);
        });
    });
  });
});
