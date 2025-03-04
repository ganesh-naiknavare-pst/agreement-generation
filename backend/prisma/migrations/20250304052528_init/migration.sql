/*
  Warnings:

  - You are about to drop the column `endDate` on the `Agreement` table. All the data in the column will be lost.
  - You are about to drop the column `ownerId` on the `Agreement` table. All the data in the column will be lost.
  - You are about to drop the column `tenantId` on the `Agreement` table. All the data in the column will be lost.
  - You are about to drop the column `phone` on the `Owner` table. All the data in the column will be lost.
  - You are about to drop the column `phone` on the `Tenant` table. All the data in the column will be lost.
  - Added the required column `address` to the `Agreement` table without a default value. This is not possible if the table is not empty.
  - Added the required column `city` to the `Agreement` table without a default value. This is not possible if the table is not empty.
  - Added the required column `agreementId` to the `Owner` table without a default value. This is not possible if the table is not empty.
  - Added the required column `agreementId` to the `Tenant` table without a default value. This is not possible if the table is not empty.

*/
-- CreateEnum
CREATE TYPE "AgreementStatus" AS ENUM ('APPROVED', 'PROCESSING', 'REJECTED');

-- DropForeignKey
ALTER TABLE "Agreement" DROP CONSTRAINT "Agreement_ownerId_fkey";

-- DropForeignKey
ALTER TABLE "Agreement" DROP CONSTRAINT "Agreement_tenantId_fkey";

-- DropIndex
DROP INDEX "Owner_email_key";

-- DropIndex
DROP INDEX "Tenant_email_key";

-- AlterTable
ALTER TABLE "Agreement" DROP COLUMN "endDate",
DROP COLUMN "ownerId",
DROP COLUMN "tenantId",
ADD COLUMN     "address" TEXT NOT NULL,
ADD COLUMN     "city" TEXT NOT NULL,
ADD COLUMN     "pdf" BYTEA,
ADD COLUMN     "status" "AgreementStatus" NOT NULL DEFAULT 'PROCESSING';

-- AlterTable
ALTER TABLE "Owner" DROP COLUMN "phone",
ADD COLUMN     "agreementId" INTEGER NOT NULL;

-- AlterTable
ALTER TABLE "Tenant" DROP COLUMN "phone",
ADD COLUMN     "agreementId" INTEGER NOT NULL;

-- AddForeignKey
ALTER TABLE "Owner" ADD CONSTRAINT "Owner_agreementId_fkey" FOREIGN KEY ("agreementId") REFERENCES "Agreement"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Tenant" ADD CONSTRAINT "Tenant_agreementId_fkey" FOREIGN KEY ("agreementId") REFERENCES "Agreement"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
