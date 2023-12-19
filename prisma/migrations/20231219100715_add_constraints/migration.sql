/*
  Warnings:

  - Made the column `total_spins` on table `aggregated` required. This step will fail if there are existing NULL values in that column.
  - Made the column `total_revenue` on table `aggregated` required. This step will fail if there are existing NULL values in that column.
  - Made the column `total_purchases` on table `aggregated` required. This step will fail if there are existing NULL values in that column.
  - Made the column `avg_revenue_per_purchase` on table `aggregated` required. This step will fail if there are existing NULL values in that column.
  - Made the column `total_daily_revenue` on table `aggregated` required. This step will fail if there are existing NULL values in that column.

*/
-- AlterTable
ALTER TABLE "aggregated" ALTER COLUMN "total_spins" SET NOT NULL,
ALTER COLUMN "total_revenue" SET NOT NULL,
ALTER COLUMN "total_purchases" SET NOT NULL,
ALTER COLUMN "avg_revenue_per_purchase" SET NOT NULL,
ALTER COLUMN "total_daily_revenue" SET NOT NULL;
