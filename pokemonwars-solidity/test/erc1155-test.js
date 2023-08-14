const { expect } = require("chai");
const { loadFixture } = require("@nomicfoundation/hardhat-network-helpers");
const { deployToken, zeroAddress } = require("./fixtures");

describe("ERC1155", function () {

  // проверка, что деплой контракта выполнен правильно
  // все переменные, которые инициализируются в контрукторе должны иметь правильные значения
  describe("Deployment", function () {
    // проверка значения переменной name
    it("Check that the token name is set correctly", async function () {
      const { token, realName } = await loadFixture(deployToken);
      const tokenName = await token.name();
      expect(tokenName).to.equal(realName);
    });
    // проверка значения переменной symbol
    it("Check that the token symbol is set correctly", async function () {
      const { token, realSymbol } = await loadFixture(deployToken);
      const tokenSymbol = await token.symbol();
      expect(tokenSymbol).to.equal(realSymbol);
    });
    // проверка interfaceID
    it("Check ERC 165 interface", async function () {
      const { token } = await loadFixture(deployToken);
      expect(await token.supportsInterface(0xd9b67a26)).to.be.equal(true);
    })
  });

  describe("Emission", function () {
    describe("MintApprove", function () {
      describe("Require", function () {
        // проверка, что разрешать делать эмиссию токена может только владелец токена
        it("Check that only the owner of the token can approve the emission of the token", async function () {
          const { token, owner, otherAccount } = await loadFixture(deployToken);
          await Promise.all([
            expect(token.setMintApproved(otherAccount.address, true)).not.to.be.reverted,
            expect(token.connect(otherAccount).setMintApproved(owner.address, true))
              .to.be.revertedWith("ERC1155: You are not owner"),
          ]);
        })
      });
    });

    // проверка, что функция mint работает правильно
    describe("Mint", function () {
      // проверка, корректной работы require
      describe("Require", function () {
        // проверка, что только владелец контракта может делать эмиссию токена
        it("Check that only the contract owner can do token emission", async function () {
          const { token, owner, otherAccount } = await loadFixture(deployToken);
          await Promise.all([
            expect(token.mint(otherAccount.address, 1, 1)).not.to.be.reverted,
            expect(token.connect(otherAccount).mint(owner.address, 2, 42)).to.be.revertedWith("ERC1155: You are not owner")
          ]);
        });

        // проверка, что можно делать эмиссию токена если есть approve на mint
        it("Check that you can do token emission if you have approval", async function () {
          const { token, owner, otherAccount } = await loadFixture(deployToken);
          await token.setMintApproved(otherAccount.address, true);
          await expect(token.connect(otherAccount).mint(owner.address, 2, 42)).not.to.be.reverted;
        })
      });
      // проверка, что после эмиссии токенов корректно изменяется баланс аккаунта,
      // на который токены минтятся
      it("Check that token emission correctly changes the balance of the account", async function () {
        const { token, otherAccount } = await loadFixture(deployToken);
        await token.mint(otherAccount.address, 2, 3);
        expect(await token.balanceOf(otherAccount.address, 2)).to.be.equal(3);
      });

      describe("Events", function () {
        // Проверка, что функция эмиссии вызывает событие трансфера. 
        it("Checking that the emission causes the TransferSingle event", async function () {
          const { token, owner, otherAccount } = await loadFixture(deployToken);
          await expect(token.mint(otherAccount.address, 2, 3)).to.be
            .emit(token, "TransferSingle")
            .withArgs(owner.address, zeroAddress, otherAccount.address, 2, 3);
        });
      });
    });
    // проверка, что функция mintBatch работает правильно
    describe("Mint a batch", function () {
      // проверка, корректной работы require
      describe("Require", function () {
        it("Check that only the contract owner can do token emission", async function () {
          const { token, owner, otherAccount } = await loadFixture(deployToken);
          await Promise.all([
            expect(token.mintBatch(otherAccount.address, [2, 3], [42, 1])).not.to.be.reverted,
            expect(token.connect(otherAccount).mintBatch(owner.address, [4, 5], [1, 1])).to.be.revertedWith("ERC1155: You are not owner")
          ]);
        });
        it("Check that only if the length of the token IDs is equal to the length of the number of tokens you can emit tokens", async function () {
          const { token, otherAccount } = await loadFixture(deployToken);
          await Promise.all([
            expect(token.mintBatch(otherAccount.address, [2, 3], [42, 1])).not.to.be.reverted,
            expect(token.mintBatch(otherAccount.address, [2, 3], [42, 1, 2, 3]))
              .to.be.revertedWith("ERC1155: The length of the tokenIds array is not equal to the length of the amounts array"),
            expect(token.mintBatch(otherAccount.address, [2, 3, 1, 2, 3], [42]))
              .to.be.revertedWith("ERC1155: The length of the tokenIds array is not equal to the length of the amounts array"),
          ]);
        });
        // проверка, что можно делать эмиссию токена если есть approve на mint
        it("Check that you can do token emission if you have approval", async function () {
          const { token, owner, otherAccount } = await loadFixture(deployToken);
          await token.setMintApproved(otherAccount.address, true);
          await expect(token.connect(otherAccount).mintBatch(owner.address, [2, 3], [42, 1])).not.to.be.reverted;
        })
      });

      // проверка, что после эмиссии токенов корректно изменяется баланс аккаунта,
      // на который токены минтятся
      it("Check that token emission correctly changes the balance of the account", async function () {
        const { token, otherAccount } = await loadFixture(deployToken);
        await token.mintBatch(otherAccount.address, [2, 3], [3, 1]);
        let [secondTokenBalance, thirdTokenBalance] = await Promise.all([
          token.balanceOf(otherAccount.address, 2),
          token.balanceOf(otherAccount.address, 3),
        ]);
        expect(secondTokenBalance).to.be.equal(3);
        expect(thirdTokenBalance).to.be.equal(1);
      });
      describe("Events", function () {
        // Проверка, что функция эмиссии вызывает событие трансфера. 
        it("Checking that the emission causes the TransferBatch event", async function () {
          const { token, owner, otherAccount } = await loadFixture(deployToken);
          await token.mintBatch(otherAccount.address, [2, 3], [3, 1]);
          await expect(token.mintBatch(otherAccount.address, [2, 3], [3, 1])).to.be
            .emit(token, "TransferBatch")
            .withArgs(owner.address, zeroAddress, otherAccount.address, [2, 3], [3, 1]);
        });
      });
    });
    describe("Balance", function () {
      describe("Require", function () {
        it("Check that you can not read the balance of tokens that are not emitted.", async function () {
          const { token, owner } = await loadFixture(deployToken);
          await expect(token.balanceOf(owner.address, 0)).to.be.revertedWith("ERC1155: There is no token with such an id");
        });
      });

      // Возвращаемый результат баланса проверяается выше.
    });
    describe("Batch Balance", function () {
      describe("Require", function () {
        it("Check that the length of the array with token IDs must be equal to the length of the array with accounts to view the balance", async function () {
          const { token, owner, otherAccount } = await loadFixture(deployToken);
          await Promise.all([token.mint(otherAccount.address, 3, 42), token.mint(owner.address, 2, 10)]);
          await Promise.all([
            expect(token.balanceOfBatch([owner.address, otherAccount.address], [2, 3])).not.to.be.reverted,
            expect(token.balanceOfBatch([otherAccount.address, owner.address], [2]))
              .to.be.revertedWith("ERC1155: The length of the tokenIds array is not equal to the length of the account array"),
            expect(token.balanceOfBatch([otherAccount.address], [2, 3, 3]))
              .to.be.revertedWith("ERC1155: The length of the tokenIds array is not equal to the length of the account array"),
          ]);
        });
      });
      it("Return value should be equal to balanceOf", async function () {
        const { token, owner, otherAccount } = await loadFixture(deployToken);
        await Promise.all([token.mint(otherAccount.address, 3, 42), token.mint(owner.address, 2, 10)]);
        let [balanceBatchOtherOwner, balanceBatchOther, balanceOther, balanceBatchOwner, balanceOwner] = await Promise.all([
          token.balanceOfBatch([otherAccount.address, owner.address], [3, 2]),
          token.balanceOfBatch([otherAccount.address], [3]),
          token.balanceOf(otherAccount.address, 3),
          token.balanceOfBatch([owner.address], [2]),
          token.balanceOf(owner.address, 2)
        ]);
        expect(balanceBatchOther[0]).to.be.equal(balanceOther);
        expect(balanceBatchOwner[0]).to.be.equal(balanceOwner);
        expect(balanceBatchOtherOwner[0]).to.be.equal(balanceOther);
        expect(balanceBatchOtherOwner[1]).to.be.equal(balanceOwner);
      })
    });
  });

  describe("Transfers", function () {
    describe("Safe transfer", function () {
      // проверка, корректной работы require
      describe("Require", function () {
        // проверка, что вызывается ошибка, если на балансе не достаточно токенов для отправки
        it("Check that there are enough tokens on the balance for the transfer", async function () {
          const { token, owner, otherAccount } = await loadFixture(deployToken);
          await token.mint(otherAccount.address, 1, 0);
          await expect(token.connect(otherAccount).safeTransferFrom(otherAccount.address, owner.address, 1, 1, [])).to.be.revertedWith("ERC1155: Not enough tokens");
        });
        // проверка, что вызывается ошибка, если нет такого токена что пытаются передать
        it("Check that you can't transfer non-existent tokens", async function () {
          const { token, owner, otherAccount } = await loadFixture(deployToken);
          await expect(token.connect(otherAccount)
            .safeTransferFrom(otherAccount.address, owner.address, 42, 1, [])).to.be
            .revertedWith("ERC1155: There is no token with such an id");
        });
        // проверка, что ты не можешь отправить токены с чужого аккаунта
        it("Check that you can't transfer from someone else's account", async function () {
          const { token, owner, otherAccount } = await loadFixture(deployToken);
          await token.mint(otherAccount.address, 1, 3);
          await expect(token.connect(otherAccount)
            .safeTransferFrom(owner.address, otherAccount.address, 1, 1, [])).to.be
            .revertedWith("ERC1155: You don't have enough rights");
        });
        // проверка, на ошибку если будет нулевой адрес
        it("Check that you can't transfer to address(0)", async function () {
          const { token, otherAccount } = await loadFixture(deployToken);
          await token.mint(otherAccount.address, 1, 3);
          await expect(token.connect(otherAccount)
            .safeTransferFrom(otherAccount.address, zeroAddress, 1, 1, [])).to.be
            .revertedWith("ERC1155: The recipient's address must be non-zero.");
        });
      });
      // проверка, что после трансфера корректно изменяется баланс аккаунта, на и из которого токены передаются.
      it("Check that token trabsfer correctly changes the balance of the account", async function () {
        const { token, owner, otherAccount } = await loadFixture(deployToken);
        await token.mint(otherAccount.address, 1, 3);
        await token.connect(otherAccount).safeTransferFrom(otherAccount.address, owner.address, 1, 2, []);
        let [ownerBalance, otherAccountBalance] = await Promise.all([
          token.balanceOf(owner.address, 1),
          token.balanceOf(otherAccount.address, 1),
        ]);
        expect(ownerBalance).to.be.equal(2);
        expect(otherAccountBalance).to.be.equal(1);
      });
    });
    describe("Safe batch transfer", function () {
      // проверка, корректной работы require
      describe("Require", function () {
        // проверка, что вызывается ошибка, если на балансе не достаточно токенов для отправки
        it("Check that there are enough tokens on the balance for the transfer", async function () {
          const { token, owner, otherAccount } = await loadFixture(deployToken);
          await token.mint(otherAccount.address, 1, 0);
          await expect(token.connect(otherAccount).safeBatchTransferFrom(otherAccount.address, owner.address, [1], [1], [])).to.be.revertedWith("ERC1155: Not enough tokens");
        });
        // проверка, что вызывается ошибка, если нет такого токена что пытаются передать
        it("Check that you can't transfer non-existent tokens", async function () {
          const { token, owner, otherAccount } = await loadFixture(deployToken);
          await expect(token.connect(otherAccount)
            .safeBatchTransferFrom(otherAccount.address, owner.address, [42], [1], [])).to.be
            .revertedWith("ERC1155: There is no token with such an id");
        });
        // проверка, что ты не можешь отправить токены с чужого аккаунта
        it("Check that you can't transfer from someone else's account", async function () {
          const { token, owner, otherAccount } = await loadFixture(deployToken);
          await token.mint(otherAccount.address, 1, 3);
          await expect(token.connect(otherAccount)
            .safeBatchTransferFrom(owner.address, otherAccount.address, [1, 1], [1, 2], [])).to.be
            .revertedWith("ERC1155: You don't have enough rights");
        });
        it("Check that you can't transfer to address(0)", async function () {
          const { token, otherAccount } = await loadFixture(deployToken);
          await token.mint(otherAccount.address, 1, 3);
          await expect(token.connect(otherAccount)
            .safeBatchTransferFrom(otherAccount.address, zeroAddress, [1], [1], [])).to.be
            .revertedWith("ERC1155: The recipient's address must be non-zero.");
        })
      });
      // проверка, что после трансфера корректно изменяется баланс аккаунта, на и из которого токены передаются.
      it("Check that token trabsfer correctly changes the balance of the account", async function () {
        const { token, owner, otherAccount } = await loadFixture(deployToken);
        await token.mint(otherAccount.address, 1, 3);
        await token.connect(otherAccount).safeBatchTransferFrom(otherAccount.address, owner.address, [1, 1], [1, 1], []);
        let [ownerBalance, otherAccountBalance] = await Promise.all([
          token.balanceOf(owner.address, 1),
          token.balanceOf(otherAccount.address, 1),
        ]);
        expect(ownerBalance).to.be.equal(2);
        expect(otherAccountBalance).to.be.equal(1);
      });
      it("Check that only if the length of the token IDs is equal to the length of the number of tokens you can transfer tokens", async function () {
        const { token, owner, otherAccount } = await loadFixture(deployToken);
        await Promise.all([
          token.mint(owner.address, 1, 10),
          token.mint(owner.address, 2, 10),
          token.mint(owner.address, 3, 10),
          token.mint(owner.address, 4, 10)
        ]);
        await Promise.all([
          expect(token.connect(owner).safeBatchTransferFrom(owner.address, otherAccount.address, [1, 2], [1, 1], [])).not.to.be.reverted,
          expect(token.connect(owner).safeBatchTransferFrom(owner.address, otherAccount.address, [1, 2], [5, 1, 2, 3], []))
            .to.be.revertedWith("ERC1155: The length of the tokenIds array is not equal to the length of the amounts array"),
          expect(token.connect(owner).safeBatchTransferFrom(owner.address, otherAccount.address, [1, 2, 3], [5], []))
            .to.be.revertedWith("ERC1155: The length of the tokenIds array is not equal to the length of the amounts array"),
        ]);
      });
    });
  });
  // Проверка uri
  describe("Uri", function () {
    describe("Require", function () {
      it("Check that you can not read the uri of tokens that are not emitted.", async function () {
        const { token } = await loadFixture(deployToken);
        await expect(token.uri(42)).to.be.revertedWith("ERC1155: There is no token with such an id")
      });
    });
    it("Check uri and tokenId", async function () {
      const { token, owner, realBaseUri } = await loadFixture(deployToken);
      await token.mintBatch(owner.address, [1, 2, 3], [0, 0, 0]);
      let [firstUri, secondUri, thirdUri] = await Promise.all([
        token.uri(1),
        token.uri(2),
        token.uri(3),
      ]);
      expect(firstUri).to.be.equal(realBaseUri + 1);
      expect(secondUri).to.be.equal(realBaseUri + 2);
      expect(thirdUri).to.be.equal(realBaseUri + 3);
    });
  });
  // Провека setApprovalForAll
  describe("Approve for all", function () {
    describe("Require", function () {
      it("Checking that the operator argument is always not equal to the sender", async function () {
        const { token, owner } = await loadFixture(deployToken);
        await expect(token.connect(owner).setApprovalForAll(owner.address, true)).to.be.revertedWith("ERC1155: Operator is you");
      });
      it("Check that you can only approve if you have not previously approved this address.", async function () {
        const { token, owner, otherAccount } = await loadFixture(deployToken);
        await token.connect(owner).setApprovalForAll(otherAccount.address, true);
        await expect(token.connect(owner).setApprovalForAll(otherAccount.address, true)).to.be.revertedWith("ERC1155: Approval is already there");
      });
    })
    it("Check that isApprovedForAll must be true after approval", async function () {
      const { token, owner, otherAccount } = await loadFixture(deployToken);
      await token.connect(owner).setApprovalForAll(otherAccount.address, true);
      expect(await token.isApprovedForAll(owner.address, otherAccount.address)).to.be.equal(true);
    });
  });
});
