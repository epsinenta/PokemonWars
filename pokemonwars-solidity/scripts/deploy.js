const hre = require("hardhat");

async function main() {
  const ERC = await hre.ethers.getContractFactory("ERC1155");
  const token = await ERC.deploy("Name", "LOL", "baseUri: ");

  await token.deployed();

  console.log(token.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
