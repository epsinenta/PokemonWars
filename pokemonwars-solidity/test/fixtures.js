// We define a fixtures to reuse the same setup in every test.
// We use loadFixture to run this setups once, snapshot state,
// and reset Hardhat Network to that snapshot in every test.
const { ethers } = require("hardhat");
const { loadFixture } = require("@nomicfoundation/hardhat-network-helpers");
const hre = require("hardhat");
const zeroAddress = "0x0000000000000000000000000000000000000000";
const pokeballPrice = ethers.utils.formatUnits(1000, "wei");

async function deployToken() {
  const realName = "Test Game Name";
  const realSymbol = "IDK";
  const realBaseUri = "https://example.com/";

  // Contracts are deployed using the first signer/account by default
  const [owner, otherAccount] = await ethers.getSigners();

  const ERC = await hre.ethers.getContractFactory("ERC1155");
  const token = await ERC.deploy(realName, realSymbol, realBaseUri);
  await token.deployed();

  return { token, owner, otherAccount, realName, realSymbol, realBaseUri };
}

async function deployGameAndPokemon() {
  const pokemonId = 0;
  const pokemonName = "Test Pikachu Name";
  const pokemonDamage = 40;
  const pokemonDefense = 25;
  const pokemonType = ethers.BigNumber.from("7"); // Electric
  const pokemonAdvantage = ethers.BigNumber.from("2"); // Water
  const pokemonWeaknesses = ethers.BigNumber.from("3"); // Grass
  const playerNickname = "Player nickname";

  const [[owner, otherAccount], gameFactory, pokemonFactory, playerFactory,
    { token, realName: gameName, realSymbol: gameSymbol, realBaseUri: gameUri }] =
    await Promise.all([
      ethers.getSigners(),
      hre.ethers.getContractFactory("Game"),
      hre.ethers.getContractFactory("Pokemon"),
      hre.ethers.getContractFactory("Player"),
      deployToken()
    ]);
  const game = await gameFactory.deploy(token.address);
  const [pokemon, pokemonCopy] = await Promise.all([
    pokemonFactory.deploy(
      pokemonId, pokemonName, pokemonDamage, pokemonDefense,
      pokemonType, pokemonAdvantage, pokemonWeaknesses,
      game.address
    ),
    pokemonFactory.deploy(
      pokemonId + 1, pokemonName, pokemonDamage, pokemonDefense,
      pokemonType, pokemonAdvantage, pokemonWeaknesses,
      game.address
    )
  ]);
  await Promise.all([
    token.connect(owner).setMintApproved(game.address, true),
    token.connect(owner).setApprovalForAll(game.address, true),
    token.connect(otherAccount).setApprovalForAll(game.address, true)
  ]);
  const [player, playerOther] = await Promise.all([
    playerFactory.deploy(playerNickname, owner.address, game.address),
    playerFactory.deploy(playerNickname, otherAccount.address, game.address),
  ]);

  return {
    game, owner, otherAccount,
    gameName, gameSymbol, gameUri, token,
    pokemonId, pokemonName, pokemonDamage, pokemonDefense,
    pokemonType, pokemonAdvantage, pokemonWeaknesses,
    pokemon, pokemonCopy,
    playerNickname, player, playerOther
  };
};

async function mintPokemon(game, player, account, pokemon) {
  let connected = game.connect(account);
  await connected.donate({ value: pokeballPrice });
  await connected.buyPokeballs(1);
  await connected.mintPokemon(player.address, pokemon.address);
  return connected;
};

async function deployEverythingWithMintedPokemons() {
  const {
    game, owner, otherAccount,
    gameName, gameSymbol, gameUri, token,
    pokemonId, pokemonName, pokemonDamage, pokemonDefense,
    pokemonType, pokemonAdvantage, pokemonWeaknesses,
    pokemon, pokemonCopy,
    playerNickname, player, playerOther
  } = await loadFixture(deployGameAndPokemon);
  await Promise.all([
    mintPlayerPokemon(player, owner, pokemon),
    mintPlayerPokemon(playerOther, otherAccount, pokemonCopy),
    player.setOnline(true),
    playerOther.connect(otherAccount).setOnline(true)
  ]);
  return {
    game, owner, otherAccount,
    gameName, gameSymbol, gameUri, token,
    pokemonId, pokemonName, pokemonDamage, pokemonDefense,
    pokemonType, pokemonAdvantage, pokemonWeaknesses,
    pokemon, pokemonCopy,
    playerNickname, player, playerOther
  };
};

async function mintPlayerPokemon(player, account, pokemon) {
  let connected = player.connect(account);
  await connected.donate({ value: pokeballPrice });
  await connected.buyPokeballs(1);
  await connected.catchPokemon(pokemon.address);
  return connected;
};

module.exports = {
  deployToken,
  deployGameAndPokemon,
  mintPokemon,
  deployEverythingWithMintedPokemons,
  mintPlayerPokemon,
  zeroAddress,
  pokeballPrice
};
